# How to run the new GUI with local apps and staging data

Status: development-only workflow, browser-smoke-tested on 2026-10-31.

## Purpose

Use the locally developed new GUI and local NOMAD app definitions while
displaying real, public data from the NOMAD staging deployment. This is useful
for visually reviewing app and dashboard changes without importing a large
dataset into the local development environment.

Remain signed out throughout this workflow. It is intended for unauthenticated,
read-only visual testing.

## Why a hybrid setup is necessary

The legacy GUI keeps its app configuration in the frontend, so changing its
`apiBase` can redirect data requests without replacing the local app
configuration.

The new GUI obtains both of the following through API requests:

- app definitions from `/api/v1/apps/entry-points`;
- search results and aggregations from endpoints such as
  `/api/v1/entries/query`.

Pointing the entire new GUI API at staging therefore also replaces locally
modified app definitions with the staging versions. The hybrid setup splits
the requests as follows:

```text
New GUI at 127.0.0.1:3002
├── /apps API requests ───────────────> local backend at localhost:8000
└── entry/search/data API requests ──> staging backend at nomad-lab.eu
```

Staging also supplies the new GUI runtime configuration and metainfo.

## Prerequisites

From the distribution repository root:

1. Complete the normal distro-dev setup (`uv run poe setup`).
2. Ensure the required infrastructure containers are running.
3. Ensure `packages/nomad-gui` dependencies are installed.
4. Ensure the local backend configuration includes the app/plugin changes to
   be reviewed.

## 1. Add the temporary split-API routing hook

In `packages/nomad-gui/src/api/utils.ts`, change `getUrl` so an optional
`VITE_APPS_API_URL` handles only `apps` routes:

```ts
export function getUrl(path: string) {
  if (/^https?:\/\//i.test(path)) {
    return path
  }
  const rel = path.replace(/^\/+/, '')
  // Local-only visual testing can keep app definitions on the development
  // backend while loading entry data from a remote deployment.
  const appsApiUrl = import.meta.env.VITE_APPS_API_URL?.replace(/\/+$/, '')
  const base =
    appsApiUrl && /^apps(?:\/|$)/.test(rel)
      ? appsApiUrl
      : ENV.API_URL?.replace(/\/+$/, '') || ''
  return `${base}/${rel}`
}
```

This is a temporary local testing hook. Unless the project explicitly decides
to support it as a permanent development feature, do not commit this hunk.

## 2. Create the local Vite environment file

Create `packages/nomad-gui/.env.local` with:

```dotenv
VITE_USE_MOCKED_API=false
VITE_CONFIG_FILE_URL=https://nomad-lab.eu/staging/config.js
VITE_METAINFO_FILE_URL=https://nomad-lab.eu/staging/metainfo.js
VITE_APPS_API_URL=http://localhost:8000/nomad-oasis/api/v1
```

`.env.local` is ignored by the `nomad-gui` repository and must remain
uncommitted.

Use the final `/staging/config.js` and `/staging/metainfo.js` URLs exactly as
shown. The nominal URLs below redirect to those files, but the redirect
responses do not contain the CORS headers required for cross-origin scripts:

```text
https://nomad-lab.eu/prod/v1/staging/gui/v2/config.js
https://nomad-lab.eu/prod/v1/staging/gui/v2/metainfo.js
```

A browser can therefore reject the nominal URLs even though opening either URL
directly appears to work.

## 3. Start the local backend

From the distribution repository root, run:

```bash
uv run poe start
```

Wait until the output reports that Uvicorn is running on port 8000. The local
backend supplies the locally modified app registry and validates app
configuration.

## 4. Start the new GUI

In a second terminal, run:

```bash
cd packages/nomad-gui
CHOKIDAR_USEPOLLING=true npm run start -- --host 127.0.0.1 --port 3002
```

Polling avoids `EMFILE: too many open files, watch` failures seen on macOS in
this workspace.

Do not use `uv run poe gui start`; that starts the legacy GUI. For this setup,
also avoid the current root `uv run poe gui-v2` task because its explicit
`VITE_CONFIG_FILE_URL` and `VITE_METAINFO_FILE_URL` process variables override
the values in `.env.local`.

## 5. Open and verify the Entries app

Open this URL directly rather than using the legacy GUI's "open in new GUI"
button:

```text
http://127.0.0.1:3002/apps/entries
```

Confirm the following:

- the header shows `SIGN IN`, confirming an unauthenticated session;
- locally configured dashboard widgets and other app changes are present;
- entry rows and aggregation counts contain staging data;
- the browser Network panel shows app-definition requests such as
  `http://localhost:8000/nomad-oasis/api/v1/apps/entry-points/entries`;
- the Network panel shows data requests such as
  `https://nomad-lab.eu/staging/backend/api/v1/entries/query`.

The important check is that both origins appear. If every API request goes to
staging, the GUI is displaying staging app definitions rather than the local
changes.

## Troubleshooting

### Blank page and CORS errors for `config.js` or `metainfo.js`

Check that `.env.local` uses the direct `/staging/config.js` and
`/staging/metainfo.js` URLs, then restart Vite. Do not use the redirecting
`/prod/v1/staging/gui/v2/` URLs.

### `Network Error` for `/apps/entry-points`

The local backend is not running, is still starting, or is not reachable on
port 8000. Restart `uv run poe start` and wait for application startup to
complete.

### `EMFILE: too many open files, watch`

Start Vite with `CHOKIDAR_USEPOLLING=true` as shown above.

### The page opens the old GUI

Use `http://127.0.0.1:3002/apps/entries` directly. Port 3002 is the local Vite
server for the new GUI in this development setup.

### The local app changes load but no entry data appears

Remain signed out, inspect the browser Network panel, and verify that
`entries/query` targets `https://nomad-lab.eu/staging/backend/api/v1`. Also
check for a staging outage or a CORS response error.

## Cleanup

Before committing `nomad-gui` changes:

1. Stop the Vite and local backend processes.
2. Delete `packages/nomad-gui/.env.local`.
3. Remove only the temporary `VITE_APPS_API_URL` routing hunk from
   `packages/nomad-gui/src/api/utils.ts`, preserving any unrelated work in that
   file.
4. Verify that `git -C packages/nomad-gui status --short` no longer lists
   `src/api/utils.ts` because of this setup.

No change to `packages/nomad-FAIR/gui/src/config.js` is needed for the new GUI.
If that legacy file was modified during an earlier experiment, restore its
normal expression before committing:

```js
export const apiBase = `${appBase}/api`
```
