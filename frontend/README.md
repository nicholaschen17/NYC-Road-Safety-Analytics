# NYC Road Safety Analytics — frontend

React (Vite) implementation of the screens described in [`wireframes/README.md`](wireframes/README.md) and the HTML mocks in [`wireframes/mock_design_html/`](wireframes/mock_design_html/).

## Routes

| Path | Screen |
|------|--------|
| `/` | NYC crash hotspot dashboard |
| `/incidents` | Incident explorer (timeline + table + detail) |
| `/zones/:gridId` | Zone grid drill-down (example: `/zones/4812`) |
| `/reporting` | Reporting & export center |

## Run locally

```bash
cd frontend
npm install
npm run dev
```

Then open the URL Vite prints (default `http://localhost:5173`).

## Build

```bash
npm run build
```

Static output is written to `dist/`.
