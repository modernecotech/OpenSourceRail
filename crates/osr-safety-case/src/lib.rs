//! OpenSourceRail — GSN (Goal Structuring Notation) compiler.
//!
//! Input: a directory of TOML files describing goals, strategies, and
//! solutions (RFC 0005 §4.9). Output: a validated, closure-checked,
//! text-rendered safety case.
//!
//! The goal of this crate is the smallest thing that can credibly be
//! called a GSN compiler — three node kinds, one closure rule, one
//! rendered output. Everything else (assumptions, contexts,
//! away-goals, cross-module references, graphviz, HTML) is deferred
//! until a concrete safety-case claim needs it.
//!
//! # GSN model (v1)
//!
//! | Node kind | Role |
//! |---|---|
//! | **Goal** | A claim. Leaves supported directly by a solution; internal nodes decomposed by a strategy. |
//! | **Strategy** | Argumentation — how a parent goal decomposes into subgoals. |
//! | **Solution** | Evidence pointer — a Kani harness, a proptest, a TLA+ run, a sim demonstration, or an external citation. |
//!
//! # Closure
//!
//! A case *closes* iff every root goal (one with no parent strategy)
//! traces — through strategies and subgoals — to at least one
//! solution. Formally, the set of closed goals is the least fixed
//! point of:
//!
//! > `closed(G) ⇐ ∃ solution s. s.parent == G.id`
//! > `closed(G) ⇐ ∃ strategy s. s.parent == G.id ∧ ∀ c ∈ s.children. closed(c)`
//!
//! A case closes iff every root goal is in this set.

#![forbid(unsafe_code)]

use serde::Deserialize;
use std::collections::{BTreeMap, BTreeSet};
use std::fmt;
use std::fs;
use std::path::{Path, PathBuf};

// ---------------------------------------------------------------------------
// Model
// ---------------------------------------------------------------------------

/// One TOML file — combined tables of goals, strategies, and
/// solutions. A case is the union of every file in the directory.
#[derive(Debug, Default, Deserialize)]
pub struct CaseFile {
    #[serde(default, rename = "goal")]
    pub goals: Vec<Goal>,
    #[serde(default, rename = "strategy")]
    pub strategies: Vec<Strategy>,
    #[serde(default, rename = "solution")]
    pub solutions: Vec<Solution>,
}

#[derive(Clone, Debug, Deserialize)]
pub struct Goal {
    pub id: String,
    pub description: String,
    /// Id of the strategy this goal is a subgoal of, if any. Root
    /// goals omit this field.
    #[serde(default)]
    pub parent: Option<String>,
}

#[derive(Clone, Debug, Deserialize)]
pub struct Strategy {
    pub id: String,
    pub description: String,
    /// Id of the goal this strategy argues for.
    pub parent: String,
    /// Ids of the subgoals the strategy decomposes into.
    pub children: Vec<String>,
}

#[derive(Clone, Debug, Deserialize)]
pub struct Solution {
    pub id: String,
    pub description: String,
    /// Id of the goal this solution directly supports.
    pub parent: String,
    pub evidence: Evidence,
}

#[derive(Clone, Debug, Deserialize)]
pub struct Evidence {
    /// "kani", "proptest", "tla", "differential", "sim-run", "cite".
    pub kind: String,
    /// Repository-relative path to the artefact.
    pub path: String,
    /// Optional anchor within the file — a function name for Kani /
    /// proptest, a section heading for a spec.
    #[serde(default)]
    pub anchor: Option<String>,
    /// Optional free-form note rendered alongside the evidence.
    #[serde(default)]
    pub note: Option<String>,
}

// ---------------------------------------------------------------------------
// Validation + closure
// ---------------------------------------------------------------------------

/// Fully assembled, validated safety case. Build one via [`Case::load_dir`].
#[derive(Debug, Default)]
pub struct Case {
    pub goals: BTreeMap<String, Goal>,
    pub strategies: BTreeMap<String, Strategy>,
    pub solutions: BTreeMap<String, Solution>,
}

#[derive(Debug)]
pub enum CaseError {
    Io(std::io::Error),
    Parse { path: PathBuf, source: toml::de::Error },
    DuplicateId { kind: &'static str, id: String },
    DanglingParent { kind: &'static str, id: String, parent: String },
    DanglingChild { strategy_id: String, missing_child: String },
    MissingEvidence { solution_id: String, path: String },
    Unclosed { goals: Vec<String> },
}

impl fmt::Display for CaseError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            CaseError::Io(e) => write!(f, "io error: {e}"),
            CaseError::Parse { path, source } => {
                write!(f, "parse error in {}: {source}", path.display())
            }
            CaseError::DuplicateId { kind, id } => {
                write!(f, "duplicate {kind} id {id:?}")
            }
            CaseError::DanglingParent { kind, id, parent } => {
                write!(
                    f,
                    "{kind} {id:?} references unknown parent {parent:?}"
                )
            }
            CaseError::DanglingChild { strategy_id, missing_child } => {
                write!(
                    f,
                    "strategy {strategy_id:?} lists unknown child goal {missing_child:?}"
                )
            }
            CaseError::MissingEvidence { solution_id, path } => {
                write!(
                    f,
                    "solution {solution_id:?} points at missing evidence file {path:?}"
                )
            }
            CaseError::Unclosed { goals } => {
                write!(
                    f,
                    "{} goal(s) do not close against evidence: {}",
                    goals.len(),
                    goals.join(", ")
                )
            }
        }
    }
}

impl std::error::Error for CaseError {}

impl From<std::io::Error> for CaseError {
    fn from(e: std::io::Error) -> Self {
        CaseError::Io(e)
    }
}

impl Case {
    /// Load every `*.toml` file under `dir` (non-recursive) and
    /// merge them into a single validated case. Evidence paths are
    /// resolved relative to `evidence_root` (repo root by default).
    pub fn load_dir(dir: &Path, evidence_root: &Path) -> Result<Self, CaseError> {
        let mut case = Case::default();
        let mut entries: Vec<_> = fs::read_dir(dir)?
            .filter_map(|r| r.ok())
            .filter(|e| {
                e.path().extension().and_then(|s| s.to_str()) == Some("toml")
            })
            .collect();
        entries.sort_by_key(|e| e.path());
        for entry in entries {
            let path = entry.path();
            let text = fs::read_to_string(&path)?;
            let file: CaseFile =
                toml::from_str(&text).map_err(|source| CaseError::Parse {
                    path: path.clone(),
                    source,
                })?;
            case.absorb(file)?;
        }
        case.validate_links()?;
        case.validate_evidence_paths(evidence_root)?;
        case.validate_closure()?;
        Ok(case)
    }

    fn absorb(&mut self, file: CaseFile) -> Result<(), CaseError> {
        for g in file.goals {
            if self.goals.insert(g.id.clone(), g.clone()).is_some() {
                return Err(CaseError::DuplicateId {
                    kind: "goal",
                    id: g.id,
                });
            }
        }
        for s in file.strategies {
            if self.strategies.insert(s.id.clone(), s.clone()).is_some() {
                return Err(CaseError::DuplicateId {
                    kind: "strategy",
                    id: s.id,
                });
            }
        }
        for s in file.solutions {
            if self.solutions.insert(s.id.clone(), s.clone()).is_some() {
                return Err(CaseError::DuplicateId {
                    kind: "solution",
                    id: s.id,
                });
            }
        }
        Ok(())
    }

    fn validate_links(&self) -> Result<(), CaseError> {
        for g in self.goals.values() {
            if let Some(p) = &g.parent {
                if !self.strategies.contains_key(p) {
                    return Err(CaseError::DanglingParent {
                        kind: "goal",
                        id: g.id.clone(),
                        parent: p.clone(),
                    });
                }
            }
        }
        for s in self.strategies.values() {
            if !self.goals.contains_key(&s.parent) {
                return Err(CaseError::DanglingParent {
                    kind: "strategy",
                    id: s.id.clone(),
                    parent: s.parent.clone(),
                });
            }
            for child in &s.children {
                if !self.goals.contains_key(child) {
                    return Err(CaseError::DanglingChild {
                        strategy_id: s.id.clone(),
                        missing_child: child.clone(),
                    });
                }
            }
        }
        for s in self.solutions.values() {
            if !self.goals.contains_key(&s.parent) {
                return Err(CaseError::DanglingParent {
                    kind: "solution",
                    id: s.id.clone(),
                    parent: s.parent.clone(),
                });
            }
        }
        Ok(())
    }

    fn validate_evidence_paths(&self, root: &Path) -> Result<(), CaseError> {
        for s in self.solutions.values() {
            // Let "cite" solutions point at external identifiers
            // (standards, papers) without requiring a local file.
            if s.evidence.kind == "cite" {
                continue;
            }
            let full = root.join(&s.evidence.path);
            if !full.exists() {
                return Err(CaseError::MissingEvidence {
                    solution_id: s.id.clone(),
                    path: s.evidence.path.clone(),
                });
            }
        }
        Ok(())
    }

    /// Compute the least fixed point of the closure rule and return
    /// the set of closed goal ids.
    pub fn closed_goals(&self) -> BTreeSet<String> {
        let mut closed: BTreeSet<String> = BTreeSet::new();
        let by_parent_solution: BTreeMap<String, Vec<&Solution>> = {
            let mut m: BTreeMap<String, Vec<&Solution>> = BTreeMap::new();
            for s in self.solutions.values() {
                m.entry(s.parent.clone()).or_default().push(s);
            }
            m
        };
        let by_parent_strategy: BTreeMap<String, Vec<&Strategy>> = {
            let mut m: BTreeMap<String, Vec<&Strategy>> = BTreeMap::new();
            for s in self.strategies.values() {
                m.entry(s.parent.clone()).or_default().push(s);
            }
            m
        };

        loop {
            let mut progress = false;
            for g in self.goals.values() {
                if closed.contains(&g.id) {
                    continue;
                }
                let has_direct_solution = by_parent_solution.contains_key(&g.id);
                let has_closed_strategy = by_parent_strategy
                    .get(&g.id)
                    .map(|strats| {
                        strats
                            .iter()
                            .any(|s| s.children.iter().all(|c| closed.contains(c)))
                    })
                    .unwrap_or(false);
                if has_direct_solution || has_closed_strategy {
                    closed.insert(g.id.clone());
                    progress = true;
                }
            }
            if !progress {
                break;
            }
        }

        closed
    }

    fn validate_closure(&self) -> Result<(), CaseError> {
        let closed = self.closed_goals();
        let mut unclosed: Vec<String> = self
            .goals
            .values()
            .filter(|g| !closed.contains(&g.id))
            .map(|g| g.id.clone())
            .collect();
        unclosed.sort();
        if !unclosed.is_empty() {
            return Err(CaseError::Unclosed { goals: unclosed });
        }
        Ok(())
    }

    /// Goals with no parent strategy — the case's top-level claims.
    pub fn root_goals(&self) -> Vec<&Goal> {
        let mut roots: Vec<&Goal> =
            self.goals.values().filter(|g| g.parent.is_none()).collect();
        roots.sort_by(|a, b| a.id.cmp(&b.id));
        roots
    }

    pub fn goal_count(&self) -> usize {
        self.goals.len()
    }
    pub fn strategy_count(&self) -> usize {
        self.strategies.len()
    }
    pub fn solution_count(&self) -> usize {
        self.solutions.len()
    }
}

// ---------------------------------------------------------------------------
// Text rendering
// ---------------------------------------------------------------------------

/// Render the case as an indented ASCII tree rooted at every root
/// goal. Intended for human inspection and for diffing across
/// commits; the CI gate is closure, not the rendered form.
pub fn render_text(case: &Case) -> String {
    let mut out = String::new();
    out.push_str(&format!(
        "OpenSourceRail safety case — {} goal(s), {} strategy(ies), {} solution(s)\n",
        case.goal_count(),
        case.strategy_count(),
        case.solution_count(),
    ));
    out.push_str(&"=".repeat(72));
    out.push('\n');

    let by_parent_solution: BTreeMap<String, Vec<&Solution>> = {
        let mut m: BTreeMap<String, Vec<&Solution>> = BTreeMap::new();
        for s in case.solutions.values() {
            m.entry(s.parent.clone()).or_default().push(s);
        }
        for v in m.values_mut() {
            v.sort_by(|a, b| a.id.cmp(&b.id));
        }
        m
    };
    let by_parent_strategy: BTreeMap<String, Vec<&Strategy>> = {
        let mut m: BTreeMap<String, Vec<&Strategy>> = BTreeMap::new();
        for s in case.strategies.values() {
            m.entry(s.parent.clone()).or_default().push(s);
        }
        for v in m.values_mut() {
            v.sort_by(|a, b| a.id.cmp(&b.id));
        }
        m
    };

    for root in case.root_goals() {
        render_goal(
            &mut out,
            case,
            root,
            0,
            &by_parent_solution,
            &by_parent_strategy,
        );
    }
    out
}

fn render_goal(
    out: &mut String,
    case: &Case,
    goal: &Goal,
    depth: usize,
    by_parent_solution: &BTreeMap<String, Vec<&Solution>>,
    by_parent_strategy: &BTreeMap<String, Vec<&Strategy>>,
) {
    let indent = "  ".repeat(depth);
    out.push_str(&format!("{indent}G {}: {}\n", goal.id, goal.description));

    if let Some(sols) = by_parent_solution.get(&goal.id) {
        for s in sols {
            let anchor = s
                .evidence
                .anchor
                .as_deref()
                .map(|a| format!("  [{a}]"))
                .unwrap_or_default();
            out.push_str(&format!(
                "{indent}  E {}: {} ({}){anchor} — {}\n",
                s.id, s.description, s.evidence.kind, s.evidence.path
            ));
            if let Some(note) = &s.evidence.note {
                out.push_str(&format!("{indent}      note: {note}\n"));
            }
        }
    }

    if let Some(strats) = by_parent_strategy.get(&goal.id) {
        for strat in strats {
            out.push_str(&format!(
                "{indent}  S {}: {}\n",
                strat.id, strat.description
            ));
            for child_id in &strat.children {
                if let Some(child) = case.goals.get(child_id) {
                    render_goal(
                        out,
                        case,
                        child,
                        depth + 2,
                        by_parent_solution,
                        by_parent_strategy,
                    );
                }
            }
        }
    }
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

#[cfg(test)]
mod tests {
    use super::*;
    use std::io::Write;

    fn tmp() -> tempfile::TempDir {
        tempfile::tempdir().expect("tmp")
    }

    fn write_toml(dir: &Path, name: &str, content: &str) {
        let path = dir.join(name);
        let mut f = fs::File::create(path).unwrap();
        f.write_all(content.as_bytes()).unwrap();
    }

    #[test]
    fn minimal_case_closes() {
        let g = tmp();
        let evidence = g.path().join("README.md");
        fs::write(&evidence, "dummy").unwrap();
        write_toml(
            g.path(),
            "root.toml",
            r#"
[[goal]]
id = "G1"
description = "root claim"

[[solution]]
id = "E1"
description = "direct evidence"
parent = "G1"
evidence = { kind = "proptest", path = "README.md" }
"#,
        );
        let case = Case::load_dir(g.path(), g.path()).expect("closes");
        assert_eq!(case.goal_count(), 1);
        assert_eq!(case.solution_count(), 1);
        assert!(case.closed_goals().contains("G1"));
    }

    #[test]
    fn unclosed_goal_is_rejected() {
        let g = tmp();
        write_toml(
            g.path(),
            "root.toml",
            r#"
[[goal]]
id = "G1"
description = "root claim with no evidence"
"#,
        );
        let err = Case::load_dir(g.path(), g.path()).unwrap_err();
        assert!(matches!(err, CaseError::Unclosed { .. }));
    }

    #[test]
    fn decomposition_closes_when_children_close() {
        let g = tmp();
        let evidence = g.path().join("x.md");
        fs::write(&evidence, "dummy").unwrap();
        write_toml(
            g.path(),
            "root.toml",
            r#"
[[goal]]
id = "G1"
description = "root"

[[strategy]]
id = "S1"
description = "decompose"
parent = "G1"
children = ["G1.1"]

[[goal]]
id = "G1.1"
description = "sub"
parent = "S1"

[[solution]]
id = "E1"
description = "ev"
parent = "G1.1"
evidence = { kind = "kani", path = "x.md" }
"#,
        );
        let case = Case::load_dir(g.path(), g.path()).expect("closes");
        assert!(case.closed_goals().contains("G1"));
        assert!(case.closed_goals().contains("G1.1"));
    }

    #[test]
    fn cite_evidence_skips_path_check() {
        let g = tmp();
        write_toml(
            g.path(),
            "root.toml",
            r#"
[[goal]]
id = "G1"
description = "root"

[[solution]]
id = "E1"
description = "standard"
parent = "G1"
evidence = { kind = "cite", path = "IEC 62279:2015 §6.5" }
"#,
        );
        // No real file at that path; "cite" should still pass.
        let _ = Case::load_dir(g.path(), g.path()).expect("closes");
    }

    #[test]
    fn duplicate_id_rejected() {
        let g = tmp();
        write_toml(
            g.path(),
            "root.toml",
            r#"
[[goal]]
id = "G1"
description = "first"

[[goal]]
id = "G1"
description = "duplicate"
"#,
        );
        let err = Case::load_dir(g.path(), g.path()).unwrap_err();
        assert!(matches!(err, CaseError::DuplicateId { kind: "goal", .. }));
    }
}
