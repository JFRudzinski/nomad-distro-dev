# Python Workflow Definition demo

This branch is a reproducible NOMAD development distribution for demonstrating
the Python Workflow Definition (PWD) parser in the NOMAD GUI. It pins NOMAD,
the GUI, the PWD parser, the electronic and atomistic parsers, and the run
schema as Git submodules.

## Clone the demo

Prerequisites:

- Git
- Docker with `docker compose`
- [uv](https://docs.astral.sh/uv/)

Clone the demo branch together with all pinned submodules:

```bash
git clone \
  --branch demo/python-workflow-definition \
  --recurse-submodules \
  https://github.com/JFRudzinski/nomad-distro-dev.git \
  nomad-distro-dev-pwd-demo
cd nomad-distro-dev-pwd-demo
```

For an existing clone:

```bash
git fetch origin
git switch demo/python-workflow-definition
git pull --ff-only
git submodule sync --recursive
git submodule update --init --recursive
```

Do not use `git submodule update --remote` for the demo. The distro commit pins
the tested submodule revisions; `--remote` would move them to newer branch tips.

## Pinned source revisions

The Git links in the distro commit are authoritative. The branches below record
where each tested commit came from.

| Package | Source branch | Pinned commit |
| --- | --- | --- |
| `nomad-FAIR` | `develop` | `9b101b103951` |
| `nomad-gui` | `fix-coarse-grained-particle-visualization` | `8e3688eaa2a5` |
| `nomad-parser-python-workflow-definition` | `feature/pwd-utility-grouping-function-sources` | `5f0054a0b338` |
| `electronic-parsers` | `develop` | `95207c87b75b` |
| `atomistic-parsers` | `fix-publishing-python` | `c782e592159e` |
| `nomad-schema-plugin-run` | `fix-publishing-python` | `4bc2282fdd59` |

You can verify the checkout with:

```bash
git submodule status
```

A leading space on every line means that each submodule matches the revision
pinned by this branch. A `+` means that a checkout has moved away from the pin.

## Start NOMAD and the GUI

From the distro root:

```bash
uv sync
uv run poe setup
uv run poe start
```

`poe setup` starts Elasticsearch, MongoDB, Temporal, and the local Keycloak
test server and creates `nomad.yaml` when it is absent. Keep `poe start`
running while using the demo.

Open:

<http://localhost:8000/nomad-oasis/gui/v2/>

Use the local test account when an upload requires login:

- username: `test`
- password: `password`

## Upload the examples

Create a new upload in the GUI and upload one archive at a time from this
directory:

- `data/quantum_espresso.zip` — recipe-only QE workflow. The calculation tasks
  stay at the top level and connected Python helper stages become separate
  utility subworkflows.
- `data/data_export.zip` — exported QE workflow with calculation data. Use this
  for the full demo: calculation tasks link to parsed QE entries and utility
  functions are grouped by connected component.
- `data/arithmetic.zip` — pure Python workflow. With no external execution
  tasks, all function calls remain at the top level instead of being placed in
  a synthetic utility subworkflow.

After processing finishes, open the entry whose main file is `workflow.json`,
then inspect its **Workflow** card.

For `data_export.zip`, verify that:

1. the workflow layout renders without a `data is undefined` error;
2. QE calculation nodes are visible at the top level;
3. each connected helper stage is represented by its own expandable utility
   subworkflow; and
4. calculation nodes with a uniquely parser-matched file link to their NOMAD
   entries.

The parser deliberately does not treat arbitrary `.out` files as references.
The PWD graph identifies execution directories, and NOMAD's parser registry
must identify exactly one entry-producing file in a directory before the task
is converted to a reference.

## Stop or restart

Stop the foreground NOMAD process with `Ctrl-C`, then stop the infrastructure:

```bash
docker compose down
```

The compose file uses fixed `nomad_*` container names. If startup reports that
a name such as `nomad_temporal` is already in use, first run `docker compose
down` in the other NOMAD distro checkout that owns those containers, then
start this demo again.

After parser or configuration changes, restart `uv run poe start` and reprocess
or re-upload the example. Refreshing the browser alone does not rebuild an
already processed archive.

## Parser verification

The parser tests can be run from the distro root with:

```bash
uv run --directory packages/nomad-parser-python-workflow-definition pytest -q
```
