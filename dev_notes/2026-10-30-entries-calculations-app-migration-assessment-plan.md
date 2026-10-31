# Entries/Calculations App Generalization and Migration Plan

**Date:** 2026-10-30
**Status:** Prototype implemented and tested on feature branches; integration remains under review
**Repositories in scope:** `nomad-FAIR`, `nomad-app-plugins-simulation`
(`nomad-simulation-apps` package), and this distro-dev repository

## Executive assessment

The requested change is feasible and smaller than the word “app” initially suggests.
The Entries and Calculations apps are not separate React applications. They are
declarative NOMAD `AppEntryPoint` configurations rendered by the same generic search
UI. Today both definitions live in `nomad-FAIR`'s `nomad/config/defaults.yaml`.

The work should establish the following ownership boundary:

| Concern | Intended owner |
| --- | --- |
| Generic search-app model, API, routing, and renderer | `nomad-FAIR` |
| Domain-neutral Entries app | `nomad-FAIR` |
| Calculation/simulation-specific app configuration | `nomad-simulation-apps` |
| Installation of both source packages for local development | distro-dev |

The recommended interpretation of “generalize Entries” is to make its **curated
surface** domain-neutral: generic entry metadata, visibility/origin/dataset filters,
schema definitions, and custom quantities. It should still permit advanced
cross-domain searches; it simply should not promote simulation, ELN, solar-cell, or
catalysis fields as its default columns and menus. Those fields remain indexed and
searchable, and specialized apps can provide the domain-specific curated experience.

Domain-neutral must not mean context-free. Entries should provide a high-level
dashboard that moves users into installed, curated apps without ranking data spaces by
their number of entries. Phase 3 therefore starts with a dedicated data/UX exploration
of an app registry-driven overview (for example Calculations, ELN, Alexandria, and
other installed apps), its navigation behavior, and its empty/missing-app states.

The Calculations app can be moved without a custom frontend or a new backend endpoint.
Its configuration should become a modern Python `AppEntryPoint` in
`nomad-simulation-apps`, preserving the public path `calculations` and the current
query semantics. The core YAML definition must be removed in the same integrated
change that installs the plugin, because duplicate app paths are currently silently
overwritten.

## Environment and branch refresh performed

I followed the top-level distro-dev `README.md`: packages under `packages/` are Git
submodules and uv workspace members. All seven existing subpackage remotes were
fetched with pruning before this assessment. Read-only analysis was performed against
the fresh remote default-branch refs, not against the older checked-out feature
branches.

| Package | Development base | Fresh remote ref inspected |
| --- | --- | --- |
| `nomad-FAIR` | `develop` | `eb7bcb69b` |
| `nomad-gui` | `develop` | `bc27355e` |
| `nomad-results-normalizer` | `main` (no `develop`) | `5f7fe46` |
| `nomad-schema-plugin-nmr` | `main` (no `develop`) | `eb23bdc` |
| `nomad-schema-plugin-run` | `develop` | `0f10001` |
| `nomad-simulations` | `develop` | `83eb2c1` |
| `simulation-parsers` | `develop` | `8314785` |
| target `nomad-app-plugins-simulation` | `develop` | `f2ff53a` (`v0.1.3`) |

No existing package checkout was switched because this phase only creates a plan.
Several local development branches are behind their fresh remote refs, so they must be
fast-forwarded before implementation.

The distro root already contains user changes, including staged `.gitmodules` changes
and unstaged `pyproject.toml` workspace changes. These directly overlap the future
distro integration. They must be preserved and reconciled rather than replaced.

## Current architecture and evidence

### App definitions and rendering

At `nomad-FAIR origin/develop@eb7bcb69b`:

- Entries is `nomad/config/defaults.yaml:507-635`.
- Calculations is `nomad/config/defaults.yaml:636-794`.
- `AppEntryPoint` is defined in `nomad/config/models/plugins.py:114-127`.
- The app configuration model is in `nomad/config/models/ui.py:1368-1420`.
- Plugin discovery and configuration overrides are handled in
  `nomad/config/models/config.py:2659-2777`.
- The app API caches entry points by `app.path` in
  `nomad/app/v1/routers/apps.py:452-480` and serves them at lines 484-634.
- The legacy GUI collects all app entry points in `gui/src/config.js:101-108`, creates
  their routes in `gui/src/components/nav/Routes.js:171-204`, and renders them with the
  generic search context/page.

Consequently, this task is about configuration ownership and compatibility, not a
calculation-specific React component.

### Entries is described as general but curated as multi-domain

The Entries app currently says it searches across all domains, but its default columns
and menus include:

- simulation program, DFT, and precision fields;
- material structure and crystallographic fields;
- ELN fields;
- simulation workflows and electronic/vibrational/mechanical properties;
- EELS, solar-cell, and heterogeneous-catalysis fields.

This has two costs. The general entry search is visually dominated by particular
domains, and the core package owns an expanding catalog of domain-specific presets.
The app also uses deprecated `filters` and `filter_menus`; these are translated through
a large backwards-compatibility map in `nomad/config/models/ui.py:1453-2212`.

The migration should not delete that compatibility map in this project. Third-party
apps may still refer to its old keys. New and migrated first-party definitions should
stop depending on it and use `search_quantities` plus an explicit modern `Menu`.

### A second, stale Entries configuration exists in the GUI

`gui/src/defaultApp.js` is a roughly 2,000-line static copy of the Entries
configuration. It is consumed by user-data search, dataset search, query editing,
sample history, and section selection. It has drifted from the server definition and
still contains old menu items, deprecated fields, and outdated result paths.

Changing only `defaults.yaml` would therefore not fully generalize Entries. The static
copy should be replaced by the runtime Entries app already available in `apps` from
`gui/src/config.js`, with a small domain-neutral fallback for isolated frontend tests.
The existing consumers clone the object before customizing it, so a narrow
`defaultApp` compatibility export can remain while its source becomes dynamic.

### Calculations is a pure search-app configuration

The current app:

- preserves `path: calculations`, label `Calculations`, and category `Theory`;
- selects calculation/material/method columns;
- locks the query to entries containing
  `results.method.simulation.program_name`;
- exposes simulation method, precision, workflow, and property menus;
- supplies five dashboard widgets.

It searches standard `results.*` quantities in the core Elasticsearch schema. It does
not own a parser, schema, normalizer, custom API, or frontend component. The new package
will therefore depend on a compatible NOMAD Results/App API, but not on
`nomad-simulations` merely to render the app.

### The target repository is ready for another app entry point

The linked repository is named `FAIRmat-NFDI/nomad-app-plugins-simulation`, while its
installable project and Python package are:

- distribution: `nomad-simulation-apps`;
- import package: `nomad_simulation_apps`;
- current app: Alexandria;
- current registration:
  `alexandria_app = "nomad_simulation_apps.apps:alexandria_entry_point"`.

The target already uses Python `App`/`AppEntryPoint` objects and an explicit menu, so
Calculations fits its existing structure. There is minor repository metadata drift:
the README and `project.urls.Repository` refer to the old/non-canonical
`nomad-simulation-apps` GitHub URL. That should be corrected while touching packaging
metadata, without broadening this into an Alexandria refactor.

## Proposed functional contract

### General Entries app

Recommended curated defaults:

- selected columns: entry name, entry type, upload time, and authors;
- optional columns: upload name/ID, mainfile, comment, references, datasets, and
  publication/access state;
- generic menus:
  - author, upload time, external database, dataset name, and DOI;
  - visibility, entry/upload/dataset identifiers, and upload name;
  - schema/definition selection and custom quantities;
- broad search-quantity availability so expert users can still construct
  cross-domain queries.

Recommended dashboard intent, with the final composition deliberately deferred to the
Phase 3 exploration:

- an at-a-glance overview of the major kinds of data available in the current search
  scope;
- recognizable representation of installed specialized apps/domains, such as
  Calculations, Solar Cells, MOFs/porous materials, and ELN/experimental data;
- dataset discovery, initially considering top datasets by entry count and a path to a
  fuller dataset list;
- source/origin context, such as external databases and recent data growth, when this
  is useful and sufficiently complete;
- navigation or filtering actions that take the user from an overview item to the
  matching Entries results or specialized app.

This overview is different from restoring every domain's detailed filter menus to
Entries. A compact “Solar Cells” or “Calculations” overview/count can be general and
cross-domain; detailed efficiency, DFT, or MOF-property controls remain owned by the
specialized app.

The following should leave the Entries curated surface:

- all `results.method.simulation.*` fields;
- DFT/TB/GW/BSE/DMFT, simulation precision, MD, geometry optimization, and
  simulation-property menus;
- `results.eln.*` columns and ELN menu (the existing ELN app remains their curated
  home);
- material/symmetry, EELS, solar-cell, and catalysis presets.

Removing the last group is a deliberate generalization, not a claim that it belongs in
Calculations. Until each domain has a dedicated app, those quantities remain available
through definitions/custom-quantity search. Keeping formula as a default would be a
reasonable product decision, but the cleanest cross-domain baseline is metadata-only;
this plan recommends that baseline.

To limit unrelated behavioral change, retain the current Entries path, pagination,
rows, and search-syntax policy during this migration.

### Plugin-owned Calculations app

Preserve the current user contract:

- public route `/search/calculations` and `path='calculations'`;
- label/category/readme intent;
- locked simulation-program existence criterion;
- column choices and selected state;
- explicit equivalents of every current calculation menu;
- the five current dashboard widgets and their layouts.

Use modern models (`search_quantity`, `SearchQuantities`, explicit `Menu`) rather than
copying deprecated `filters`, `filter_menus`, or `quantity` aliases. The serialized app
response before and after the move should be compared semantically, allowing only the
known model modernization and entry-point ID change.

## Implementation plan

### Phase 0 — Branch hygiene and reproducible baselines

1. Before touching a package, confirm it has no uncommitted package-local changes,
   fetch/prune again, switch to its development base, fast-forward only, and create a
   feature branch from that updated base.
2. Use separate branches/PRs:
   - `nomad-FAIR`: `feature/generalize-entries-app` from `develop`;
   - target app repository: `feature/calculations-app` from `develop`;
   - distro-dev: `feature/simulation-apps-integration` from `main`.
3. Snapshot the current serialized Entries and Calculations configurations and, in an
   integrated environment, the responses from:
   - `/api/v1/apps/entry-points`;
   - `/api/v1/apps/entry-points/entries`;
   - `/api/v1/apps/entry-points/calculations`.
4. Save a list of the current paths, columns, locked filters, menu quantities, and
   dashboard widgets as migration test fixtures. Do not use formatting equality as the
   only parity check because deprecated aliases normalize into modern fields.

### Phase 1 — Add and branch the target package in distro-dev

1. Reconcile, do not overwrite, the current staged `.gitmodules` and modified
   `pyproject.toml` work.
2. Add the linked repository as a submodule. Use the local directory
   `packages/nomad-simulation-apps` to match the Python distribution and the user's
   terminology, while `.gitmodules` records the canonical repository URL:
   `https://github.com/FAIRmat-NFDI/nomad-app-plugins-simulation.git`.
3. Inside the new submodule, fetch `origin`, switch/fast-forward `develop`, and create
   `feature/calculations-app` before editing, in accordance with the requested package
   workflow.
4. Extend root `pyproject.toml`:
   - add `nomad-simulation-apps` to project dependencies;
   - add `packages/nomad-simulation-apps` to uv workspace members;
   - add `nomad-simulation-apps = { workspace = true }` under `tool.uv.sources`.
5. Defer the final lockfile/sync until the new entry point exists, but keep the
   submodule and distro edits together on the distro integration branch.

### Phase 2 — Add Calculations to `nomad-simulation-apps`

1. Add `src/nomad_simulation_apps/apps/calculations_app.py` containing the modern
   `App` definition.
2. Export `calculations_entry_point` from
   `src/nomad_simulation_apps/apps/__init__.py`.
3. Register a second `nomad.plugin` entry in `pyproject.toml`, using a stable name such
   as:

   ```toml
   calculations_app = "nomad_simulation_apps.apps:calculations_entry_point"
   ```

4. Prefer ordinary Python configuration for columns, filters, and menus. A companion
   YAML file for the dashboard is acceptable and matches the Alexandria pattern, but
   should be loaded through package resources rather than assuming a real filesystem
   path if wheel/zip compatibility is required.
5. Correct canonical repository links in `README.md` and `project.urls.Repository`.
6. Verify the minimum supported `nomad-lab` version against the modern fields used by
   the app. Do not leave the current broad `>=1.3.0` promise if the new app only works
   with NOMAD 2.x; either raise the floor or add a small compatibility matrix.
7. Add tests that assert:
   - entry-point import and metadata;
   - stable path/label/category;
   - locked query;
   - exact column and menu quantity sets;
   - dashboard widget count/types;
   - successful validation against the intended NOMAD version.
8. Run target-package pytest and Ruff checks, build a wheel/sdist, install the built
   artifact in a clean environment, and verify plugin discovery from package metadata.

### Phase 3 — Generalize Entries in `nomad-FAIR`

#### Phase 3A — Explore and decide the Entries overview dashboard

This is a decision gate before implementing the final Entries configuration.
The exploration initially favored entry metadata distributions, but review
identified that type/method distributions would let the dominant data class bias the
overview. The revised decision is recorded in
`dev_notes/2026-10-30-entries-dashboard-decision-record.md`: use installed apps as
the organizing units and omit counts/distributions from the first version.

1. Inventory the specialized apps that are expected in the reference distro and, for
   each app, record:
   - label, path, category, and intended audience;
   - its `filters_locked`/membership criterion;
   - whether membership can be counted reliably and efficiently;
   - whether entries may belong to multiple apps and how overlap should be explained;
   - the target navigation behavior from Entries.
2. Inventory candidate indexed quantities and measure them against representative
   production-like data. At minimum evaluate:
   - `domain` (currently aggregatable but limited to `dft`, `ems`, and `nexus`);
   - `entry_type` (descriptive but currently configured as non-aggregatable and often
     too granular/plugin-specific);
   - `results.properties.available_properties` (useful for properties such as
     `solar_cell`, but not a complete app/domain classifier);
   - `results.method.method_name` and
     `results.method.simulation.program_name` for calculations;
   - `results.eln.sections` for ELN/experimental data;
   - MOF/porous-material section or property presence from the installed porous
     materials plugin;
   - `datasets.dataset_name`, `datasets.doi`, `external_db`, and
     `upload_create_time` for dataset/origin/recency overviews.
3. Quantify candidate quality rather than choosing by field name alone:
   - percentage of visible entries classified;
   - size and meaning of the unclassified bucket;
   - overlap between categories/apps;
   - cardinality and label stability;
   - consistency across central NOMAD and smaller Oases;
   - aggregation latency and response size under realistic access scopes.
4. Prototype at least two dashboard approaches:
   - **configuration-only prototype:** compose existing `terms`/`histogram` widgets
     for datasets, origins, methods/properties, and time;
   - **app-aware overview prototype:** cards/tiles using installed app metadata and
     links into the corresponding app. Treat per-app counts as an optional later
     extension rather than a prerequisite.
5. Explicitly assess the platform gap. Existing dashboards only support terms,
   histogram, periodic-table, scatter, and box-plot widgets over the current search
   context. They do not provide per-widget locked queries, app links, or a true dataset
   list. Decide whether the goal can be met with existing widgets or requires one or
   more narrowly scoped additions, for example:
   - an `app_overview` widget driven by registered app metadata, with counts deferred;
   - a reusable query/count tile widget with label, icon, description, query, and link;
   - a dataset-list widget that can show name, entry count, DOI, and navigation rather
     than only a terms aggregation.
6. For the first app-aware version, do not show counts. Discover metadata from the app
   registry, allow an optional ordered path selection, omit unavailable apps, and show
   an empty state when no configured app is installed. If counts are added later,
   define behavior for overlapping apps, access scope, zero results, and failures
   before exposing them.
7. Produce a short dashboard decision record under `dev_notes/` containing:
   - evaluated quantities and measured coverage;
   - wireframes or screenshots of the prototypes;
   - the chosen widget set and responsive layout;
   - navigation/filter interactions;
   - any new index/model/API/widget work required;
   - rejected alternatives and why;
   - an explicit performance budget and acceptance criteria.
8. Review that decision with the relevant domain/app owners before freezing the
   Entries app implementation. This review is the exit criterion for Phase 3A.

#### Phase 3B — Implement the approved Entries configuration and dashboard

**Review update (2026-10-31):** The app overview was removed after visual inspection
because it duplicates the Apps page. The approved configuration-only replacement is
Simulation workflows, Experimental methods/activities, Data added to NOMAD, and
Datasets/collections. It is the first step of a combined prototype-then-model approach.
The subsequent sidebar prototype restores selected high-level Material, Method,
Workflow, Properties, Instrument, and NeXus-class filters while keeping generic entry
metadata and avoiding the complete Calculations/NeXus domain menus.
See
[`2026-10-31-entries-dashboard-project-management-widget-assessment.md`](2026-10-31-entries-dashboard-project-management-widget-assessment.md).

1. Rewrite the Entries default entry point in `nomad/config/defaults.yaml` with the
   agreed domain-neutral columns and an explicit modern menu.
2. Replace deprecated `filters` with `search_quantities`; keep broad advanced search
   rather than restricting results to one domain.
3. Add only the dashboard widgets approved in Phase 3A. If a new widget type is
   required, keep its configuration model, API behavior, rendering, and tests generic
   enough for other apps to reuse; do not hard-code the reference distro's app list in
   the React component.
4. Replace the large static `gui/src/defaultApp.js` payload with a small export derived
   from `apps.find(app => app.path === 'entries')`, plus a minimal domain-neutral
   fallback for isolated tests. Preserve cloning/customization in its five consumers.
5. Add a test that the default columns and detailed filter menus contain no
   simulation/ELN or other domain-specific controls, while generic search and embedded
   search pages still initialize. Domain-classification quantities explicitly approved
   for high-level dashboard summaries are permitted and tested as such.
6. Add dashboard tests for registry-driven metadata, configured ordering, links,
   missing-app and empty states, responsive layout, and the requirement that the
   widget issues no entry-search aggregation requests.
7. Add app-path uniqueness validation when initializing the app cache. A duplicate
   path should raise a clear configuration error naming both entry points instead of
   silently allowing the later one to win.
8. Remove `apps/2_theory/1_calculations` from core defaults only on the integration
   branch where the target package is installed and discoverable.
9. Keep the old filter-menu compatibility map for third-party configuration. Its
   removal is a separate deprecation project.
10. Update release/migration notes to state:
   - Calculations now requires `nomad-simulation-apps`;
   - `/search/calculations` is unchanged;
   - the configuration entry-point ID changes from
     `apps/2_theory/1_calculations` to the Python entry-point ID, so deployment
     include/exclude/override keys must be updated.

### Phase 4 — Integrated verification

Before the gates below, regenerate `uv.lock` through uv (never by hand), run `uv
sync`, and verify `importlib.metadata.entry_points(group='nomad.plugin')` exposes both
Alexandria and Calculations from the editable target package. Record the coordinated
`nomad-FAIR` and `nomad-simulation-apps` commits in the distro integration branch.

Backend/configuration gates:

- exactly one app has `path='entries'` and exactly one has `path='calculations'`;
- both app endpoints return 200 and all referenced search quantities validate;
- Entries has the agreed generic curated fields;
- Calculations matches the pre-migration semantic fixture;
- the locked calculations query excludes non-simulation entries;
- package include/exclude and override configuration works with the new entry-point ID;
- uninstalling/excluding `nomad-simulation-apps` removes Calculations cleanly without
  affecting Entries.

Frontend gates:

- `/search/entries` and `/search/calculations` load without console/API errors;
- menus, columns, row details, and dashboard widgets render;
- the Entries dashboard gives a comprehensible overview of the configured installed
  apps and handles missing-app and empty states;
- overview cards lead to the correct specialized app without issuing entry-search
  aggregation requests;
- User Data, Dataset, Query editor, Sample History, and Section Select embedded
  searches use the generalized runtime Entries context;
- direct bookmarks to `/search/calculations` still work;
- the Theory category ordering remains acceptable after plugin discovery changes.

Suggested focused suites before broader CI:

- `nomad-FAIR`: app-router tests, UI-model tests, and affected legacy-GUI specs;
- `nomad-simulation-apps`: all package tests and Ruff checks;
- distro: `uv sync`, focused cross-package pytest, legacy GUI test/build, and an API/UI
  smoke test with services running.

## Merge and release sequencing

Cross-repository sequencing matters:

1. Merge and release the target package with the new Calculations entry point first,
   but do not install it alongside an unmodified core default in production.
2. Merge the `nomad-FAIR` change that generalizes Entries and removes its Calculations
   block with explicit release notes about the new package dependency.
3. In distro-dev, update the two submodule commits and add/install the target package
   in one integration commit/PR.
4. Validate the integrated distro before promoting the coordinated versions.

This avoids both failure modes: a period with no Calculations app and a period with two
apps claiming the same path. The proposed uniqueness guard turns the latter into a
visible startup/configuration error if coordination regresses.

## Risks and mitigations

| Risk | Mitigation |
| --- | --- |
| Duplicate `calculations` paths silently shadow each other | Add uniqueness validation and make removal/installation atomic. |
| Calculations disappears when the plugin is absent | Add distro dependency, release note, and explicit exclusion/uninstall test. |
| Existing NOMAD config overrides stop applying | Document and test the entry-point ID migration. |
| Plugin app references Results fields unavailable in an older NOMAD | Validate every quantity and set/test a truthful NOMAD dependency floor. |
| Entries appears generic but embedded searches retain stale config | Replace `defaultApp.js`'s static copy with the runtime Entries definition. |
| Configured app paths are absent in a smaller deployment | Omit missing apps and render a clear empty state when none remain. |
| Per-app counts are mistaken for a partition | Do not show counts in the first version; apps are navigation choices and may overlap. |
| Domain-specific filters become less discoverable | Keep them searchable via definitions/custom quantities and let specialized apps own curated menus. |
| App/category order changes after plugin discovery | Perform a GUI smoke test; treat a general ordering mechanism as separate scope. |
| Existing distro edits are lost | Preserve and reconcile the current `.gitmodules`/`pyproject.toml` diffs before applying integration changes. |

## Explicit non-goals

- Moving Results schema quantities, Elasticsearch mappings, parsers, normalizers, or
  calculation data out of `nomad-FAIR`.
- Creating a calculation-specific React application or API.
- Refactoring the Alexandria app beyond compatibility required by the shared package.
- Removing deprecated filter-menu support from core.
- Changing the new `nomad-gui` submodule; the affected frontend is the legacy GUI
  located inside `nomad-FAIR`.

## Completion criteria

The migration is complete when the integrated distro contains one generic Entries app
owned by `nomad-FAIR`, one behaviorally equivalent Calculations app owned by
`nomad-simulation-apps`, an approved and tested cross-domain Entries overview
dashboard, no duplicate static Entries configuration, stable public routes, passing
focused and package-level tests, and documented installation/override migration
steps.
