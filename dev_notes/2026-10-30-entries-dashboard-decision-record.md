# Superseded: Entries app-overview dashboard decision record

**Date:** 2026-10-30
**Status:** Rejected after visual review on 2026-10-31
**Scope:** Generalize the core `Entries` app by making installed, curated apps
the primary way to explore heterogeneous data.

## Supersession note

The app-overview widget was removed after visual inspection because it duplicated
the Apps page without adding a data-oriented or project-management view. The
implementation and configuration described below are retained only as a historical
record of the prototype. They are no longer the intended Entries design.

The replacement assessment is
[`2026-10-31-entries-dashboard-project-management-widget-assessment.md`](2026-10-31-entries-dashboard-project-management-widget-assessment.md).

## Decision

> **Review update:** The app-only proposal removed too much entry context. The
> implemented prototype therefore starts with app cards and also includes entry
> type, dataset, external-database, and upload-time widgets. This deliberately
> presents more possibilities for visual review; individual supplemental widgets
> can be removed after inspection.

Add a generic `app_overview` dashboard widget and use it as the Entries
dashboard. The widget presents installed apps as navigation cards using their
registered label, category, description, and path. Apps are the curated search
spaces (or "subdatabases") that already define which data and controls belong
together.

The first version omits per-app entry counts, method distributions, and property
distributions. It retains generic entry-type, dataset, origin, and recency views
as reviewable context underneath the app cards. Entry type is included as a
prototype candidate, not yet accepted as the primary organization of the page.

The React component must not contain domain names or a fixed app list. Its
configuration supports an optional ordered `app_paths` list:

- when `app_paths` is set, render installed matching apps in that order;
- when it is omitted, render all installed apps in category/label order;
- omit the Entries app itself and any configured path that is not installed;
- render a clear empty state if no matching app is available.

For the first reference-distro demo, configure the Entries widget with the
known paths `calculations`, `eln`, and `alexandria`. This demonstrates a small,
intentional set while keeping the widget reusable. Missing optional apps are
simply absent. A deployment can remove `app_paths` to show its full installed
app registry.

## Why the earlier entry-focused prototype was rejected

The first proposal used `entry_type`, datasets, external databases, and upload
time. That approach is technically inexpensive, but it does not satisfy the
product goal:

- entry distributions are commonly very imbalanced and let the dominant type
  or method define the page;
- an entry type is an implementation/schema label, not a stable research-data
  category;
- method and property distributions reintroduce simulation-specific bias;
- sparse dataset/origin metadata can make important curated data spaces appear
  absent;
- the intended organization already exists in app definitions, including their
  locked queries, columns, filters, and dashboards.

The local 13-entry sample confirmed the risk: `domain` had one value (`dft`),
method coverage was 5/13, program coverage was 7/13, and only two entry types
covered 9/13 entries. These figures are not production measurements, but the
design remains biased even with a larger sample because visual prominence is
driven by entry volume.

## Prototype

```text
Explore data by app
Apps provide curated search spaces for particular data and workflows.

┌──────────────────────┬──────────────────────┬──────────────────────┐
│ Calculations         │ ELN                  │ Alexandria           │
│ Theory               │ Experiment           │ Theory               │
│ Search calculations  │ Search electronic    │ Search the curated   │
│                      │ lab notebooks        │ Alexandria data      │
│ Open app →           │ Open app →           │ Open app →           │
└──────────────────────┴──────────────────────┴──────────────────────┘
```

Cards wrap responsively into fewer columns. Selecting a card opens the app's
normal route: `/apps/{path}` in the new GUI and `/search/{path}` in the legacy
GUI. The card does not carry the current Entries query because each target app
has its own locked query and filter vocabulary.

The ordinary Entries results table remains below the dashboard. Its curated
columns and menus become domain-neutral, while advanced quantity search remains
available for cross-domain work.

## Generic configuration contract

The backend UI model gains this reusable widget shape:

```yaml
type: app_overview
title: Explore data by app
description: Apps provide curated search spaces for particular data and workflows.
app_paths:
  - calculations
  - eln
  - alexandria
layout: ...
```

`app_paths` is optional and contains unique app paths. It selects presentation,
not app installation. App metadata continues to come from the existing
`GET /api/v1/apps/entry-points` endpoint, so labels and descriptions cannot
drift from the target apps.

No search/count endpoint is added. This keeps dashboard initialization to the
already cached app-registry request and avoids per-card aggregation cost or
access-scope ambiguity.

## Required implementation surfaces

1. Add `WidgetAppOverview` to the discriminated widget union in the backend UI
   model, including validation that configured paths are unique.
2. Add the widget to the new GUI dashboard renderer and generated config types.
   Reuse the existing app metadata query and card visual language.
3. Add a compatible legacy GUI renderer while legacy search apps are supported.
4. Preserve the new widget fields during dashboard export/import. The initial
   widget is configuration-driven and need not expose an interactive editor.
5. Configure Entries with the demo paths and replace its domain-specific columns
   and filter menus with generic metadata controls.
6. Keep app-path uniqueness validation in the server registry so two installed
   apps cannot silently claim the same route.

## Future extension: counts

Counts can be added later, but only as an explicit enhancement. Correct counts
must combine each app's locked query with the user's access scope, explain that
memberships overlap, handle apps without a locked query, and batch requests.
Count failure must never remove navigation. None of this is required for the
metadata-card demo.

## Acceptance criteria

1. Entries leads with app cards and does not use method or property
   distributions; supplemental generic entry widgets remain individually
   removable after visual review.
2. The demo shows each installed configured app and quietly skips uninstalled
   optional paths.
3. Card metadata is read from the installed app registry; it is not duplicated
   in the widget configuration or component.
4. Cards navigate to the correct app in both supported GUIs.
5. The card layout wraps without overlap at all dashboard breakpoints and has
   loading, error, and empty states.
6. The app overview creates no entry-search aggregation requests; each
   supplemental search widget uses the existing bounded aggregation behavior.
7. Dashboard configuration round-trips through validation and export/import.
8. The generalized Entries columns and menus contain no curated controls rooted
   at `results.material`, `results.method`, `results.properties`, or
   `results.eln`.
9. Duplicate configured `app_paths` and duplicate installed app routes produce
   clear validation/configuration errors.
10. Exactly one installed app owns `calculations` after the core copy is removed.

## Review gate

The rich Phase 3B prototype is ready for visual review in the running new GUI.
Approval should identify which of Entry types, Datasets, External databases,
and Entries over time should remain alongside the generic app overview.
Per-app counts remain deferred because app memberships overlap.
