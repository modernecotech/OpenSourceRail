# Historical railway designs and city catalogues

Use the dated editions below to follow the routes, equipment records and city introductions that accompanied each review. Their relative links open the files that existed together at that revision.

| Historical edition | What to open |
|---|---|
| Former maglev city studies | [City-by-city index at the recorded revision](https://github.com/modernecotech/OpenSourceRail/blob/578ee3950b872bf30fbf9e4207b2bda85951bdd7/engineering/ferrite_maglev/city-index.md) and [documentation coverage at the same revision](https://github.com/modernecotech/OpenSourceRail/blob/578ee3950b872bf30fbf9e4207b2bda85951bdd7/docs/design-engine/ferrite-maglev/research-closure/readme-coverage.md). The [publication manifest](pre-comfort-default/manifest.json) records the historical commit. |
| Wheel-supported railway design closure | [Original closure review and linked vehicle coverage](https://github.com/modernecotech/OpenSourceRail/blob/ebeb3b769a9b416180c64124debc1f23317ca277/docs/design-engine/v06-design-closure/README.md). The [all-city audit manifest](../design-engine/v06-design-closure/all-city-baseline-audit/manifest.json) identifies the working copy retained with the audit. |
| Subsequent maglev archive | The [v0.5 archive manifest](v0.5-maglev/manifest.json) names the later frozen development selection and its source and payload hashes. |
| Digital twin exports | The [retired export register](retired-twin-exports/README.md) identifies earlier candidate archives by their original Git blobs. Downloads used by the twin manifest, validation pages and sourcing workflow remain available in the checkout. |
| Intermediate sourcing packets | The [retired packet index](retired-sourcing-packets/README.md) preserves exact Git tree IDs for nine superseded domestic-source frame and federated purchasing evaluations. Current validation and test inputs remain in place. |
| v0.5.2 execution evidence | The [retired execution-tree register](../../engineering/assurance/retired-v052-execution-trees.json) pins five former assurance trees, including city affordability, closure, drives, integrated and stopped-recovery trials, to their original commit and Git tree IDs. |
| City PM-maglev studies | The [retired city study inventory](retired-city-maglev/README.md) pins 265 former four-file city maglev packets to their exact Git trees and gives single-city and all-city recovery instructions. Maintained city maps and outlines remain in each city folder. |

For the railway now presented to operators, open the [operator guide](../operator-review/README.md) or [current engineering guide](../design-engine/current/README.md).

## Finding files from an earlier study

The [research input guide](../../engineering/maglev_research/README.md) locates the original specification, illustrations, study parameters and infrastructure policy that previously occupied the project root and `lib/templates`. Their contents and historical source identifiers are preserved.

To inspect an old edition without disturbing a working design, use the commit and path in its archive record. For example, the following command lists the files from the retired drive study, including its original README:

```sh
git ls-tree -r --name-only 001ae0807cf070716bcc57d8746b0765eeb672fc -- engineering/assurance/v052-drives-development
```

The working tree still includes the [digital twin validation downloads](../design-engine/digital-twin/validation.md), the [wheel-supported closure record](../design-engine/v06-design-closure/README.md) and the [civil comparison portfolio](../design-engine/civil-topology-revisions/README.md). Sourcing, release replay and civil comparison tools still read files from these families.

A shallow checkout may need to fetch the recorded commit first. Active city geography, publishable drawings, offline Workbench inputs, release fixtures and source-bound comparisons can have users long after their original study. Check the consumer, generator and receipt before moving them. Local solver runs under `build/`, recovery records under `var/` and Git history have their own storage lifecycles.
