# Retired v0.5.2 drive development execution

The original 55-file execution package is preserved by the pinned Git revision
`001ae0807cf070716bcc57d8746b0765eeb672fc` and tree
`36e40dbaddc0f95b07e71b2d36d148bcd5f3e073`. This working-tree pointer
keeps older document links usable. The [retirement record](../retired-v052-execution-trees.json)
identifies the other archived v0.5.2 campaign packages.

To inspect the original package from a full Git checkout without changing the
current source tree, run:

```sh
mkdir -p build/historical-v052
git archive 001ae0807cf070716bcc57d8746b0765eeb672fc engineering/assurance/v052-drives-development | tar -xf - -C build/historical-v052
```

The [pinned Git tree](https://github.com/modernecotech/OpenSourceRail/tree/001ae0807cf070716bcc57d8746b0765eeb672fc/engineering/assurance/v052-drives-development)
provides direct access when the local checkout lacks that revision.
