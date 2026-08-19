# Chrome Extension UI

## Load the extension

1. Open `chrome://extensions`
2. Enable **Developer mode**
3. **Load unpacked** → select the `extension/` folder in this repo

## Configure API access

Open extension options and set:

| Field | Example |
|-------|---------|
| API URL | `http://127.0.0.1:8080` (local) or `https://your-app.up.railway.app` |
| API Token | Value of `SUPER_BROWSER_API_TOKEN` on the server |

## Scrape a paginated list

1. Log into the target site in Chrome (ListKit, Skool, Facebook group, directory).
2. Navigate to the list or members page.
3. Open the Super Browser side panel.
4. **Sync profile** — sends domain cookies to the API for cloud browser handoff.
5. Choose preset (`auto` recommended) and max pages.
6. **Scrape this list** — queues a background job; progress updates in the panel.
7. **Download CSV** when status is `complete`.

## Presets

| Preset | Sites |
|--------|-------|
| `listkit` | next.listkit.io, app.listkit.io |
| `skool` | skool.com community members |
| `facebook_group` | facebook.com/groups/* (infinite scroll) |
| `directory` | search/results/directory list pages |
| `generic` | any paginated table or card list |
| `auto` | detects preset from URL |

## API endpoints used by the extension

- `GET /health`
- `GET /list/presets`
- `POST /list/plan`
- `POST /list/run`
- `GET /list/{job_id}`
- `GET /list/{job_id}/export`
- `POST /profiles/sync`
