use std::path::{Path, PathBuf};

use anyhow::{bail, Result};
use clap::{Parser, Subcommand};
use osr_city_studio::CityProject;

#[derive(Debug, Parser)]
#[command(
    name = "osr-city-studio",
    version,
    about = "Deterministic, Git-backed OSR city design and service planning"
)]
struct Cli {
    #[arg(long, default_value = "projects/samawah", global = true)]
    project: PathBuf,
    #[command(subcommand)]
    command: Command,
}

#[derive(Debug, Subcommand)]
enum Command {
    /// Serve the browser design and service-planning interface.
    Serve {
        #[arg(long, default_value = "127.0.0.1")]
        host: String,
        #[arg(long, default_value_t = 8090)]
        port: u16,
    },
    /// Validate source locks, network intent, and weekly service plans.
    Validate,
    /// Compile the current draft into build/city-studio/<slug>/snapshot.json.
    Compile,
    /// Materialize an immutable revision JSON file ready for Git review.
    Revision,
    /// List materialized revisions and identify the current candidate.
    Revisions,
    /// Compare a materialized revision with the current candidate.
    Compare {
        /// Content-addressed revision id, for example osr-0123456789abcdef.
        revision_id: String,
    },
    /// Print the Git branch, parent commit, and working-tree state as JSON.
    GitStatus,
}

#[tokio::main]
async fn main() -> Result<()> {
    let cli = Cli::parse();
    match cli.command {
        Command::Serve { host, port } => {
            osr_city_studio::server::serve(&cli.project, &host, port).await
        }
        Command::Validate => {
            let snapshot = CityProject::load(&cli.project)?.compile()?;
            println!("{}", serde_json::to_string_pretty(&snapshot)?);
            if snapshot.summary.validation_errors > 0 {
                bail!("{} validation error(s)", snapshot.summary.validation_errors);
            }
            Ok(())
        }
        Command::Compile => {
            let project = CityProject::load(&cli.project)?;
            let repository_root = repository_root(&project);
            let output = project.write_build_snapshot(&repository_root)?;
            println!("{}", output.display());
            Ok(())
        }
        Command::Revision => {
            let project = CityProject::load(&cli.project)?;
            println!(
                "{}",
                serde_json::to_string_pretty(&project.materialize_revision()?)?
            );
            Ok(())
        }
        Command::Revisions => {
            let project = CityProject::load(&cli.project)?;
            println!("{}", serde_json::to_string_pretty(&project.revisions()?)?);
            Ok(())
        }
        Command::Compare { revision_id } => {
            let project = CityProject::load(&cli.project)?;
            println!(
                "{}",
                serde_json::to_string_pretty(&project.compare_revision(&revision_id)?)?
            );
            Ok(())
        }
        Command::GitStatus => {
            let project = CityProject::load(&cli.project)?;
            println!("{}", serde_json::to_string_pretty(&project.git_state())?);
            Ok(())
        }
    }
}

fn repository_root(project: &CityProject) -> PathBuf {
    project
        .git_state()
        .repository_root
        .map(PathBuf::from)
        .unwrap_or_else(|| Path::new(".").to_path_buf())
}
