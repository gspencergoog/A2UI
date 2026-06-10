# Implementation Plan: A2UI Express Evolutionary Dashboard

This plan details the construction of a real-time tracking web application and asynchronous monitoring server inside `specification/v1_0/express/optimizer/dashboard/`.

## 1. Architectural layout

```
specification/v1_0/express/optimizer/dashboard/
├── plan_dashboard.md      # This implementation roadmap
├── server.py              # Lightweight Python HTTP & REST API server (http.server)
├── index.html             # Single-page glassmorphism dark-mode UI
├── index.css              # Premium styling design system (HSL tokens, micro-animations)
└── app.js                 # Vanilla JS reactive state and auto-refresh polling logic
```

## 2. Server backend (`server.py`)

To eliminate heavy external dependencies while providing reliable local execution, `server.py` extends Python's native `http.server.SimpleHTTPRequestHandler`. It serves the frontend static assets and exposes four dedicated JSON REST endpoints:

*   **`GET /api/leaderboard`:** Reads the locked central registry at `specification/v1_0/express/leaderboard.json`, returning the reigning champion hash, token footprint metrics, and historical mutation lineage.
*   **`GET /api/candidates`:** Scans `/Users/gspencer/code/a2ui/a2ui_express/scratch/candidates/` for serialized offspring directories (`gene_{hash}`), returning their pass/fail status and parsed AST properties.
*   **`GET /api/agents`:** Inspects `/Users/gspencer/.gemini/jetski/brain/` for active worker conversation folders. Scans `.system_generated/logs/transcript.jsonl` to extract live model reasoning (`"thinking"`), execution status (`"status"`), and AST self-repair retries.
*   **`GET /api/system_state`:** Returns MLX VLM server status (checking socket connection on localhost port 8080).

## 3. Premium frontend aesthetics (`index.css` & `index.html`)

Following modern web design excellence, the UI implements a curated HSL dark-mode palette, subtle glassmorphism containers, modern typography (`Inter`), and smooth state transitions:

*   **Color Tokens:** Sleek midnight background (`hsl(220, 40%, 8%)`), surface cards (`hsl(220, 30%, 14% / 0.8)`), neon cyan highlights (`hsl(180, 100%, 50%)`), and emerald success glows (`hsl(150, 100%, 40%)`).
*   **Tabbed Navigation:** Four distinct operational views:
    1. **Overview & Leaderboard:** Displays the reigning champion cards, token compression progress bars, and fitness formula breakdown.
    2. **Active Antigravity Workers:** A grid of live worker cards showing their active conversation ID, current execution gate (Tier 0/1/2/3), and live thoughts.
    3. **Mutation Lineage Tree:** Visualizes parent-child relationships and genetic divergence across candidate generations.
    4. **Live Trajectory Logs:** Real-time tailing terminal view showing raw JSON lines and parser syntax exception tracebacks.
*   **Micro-Animations:** Hover lifts on candidate cards, pulsing live status indicators, and smooth content fade-ins.

## 4. Execution roadmap

*   **Step 1:** Author `plan_dashboard.md` and initialize directory structure.
*   **Step 2:** Implement `index.css` defining all HSL design tokens, glassmorphic blur filters, and utility classes.
*   **Step 3:** Implement `index.html` constructing the complete semantic skeleton and tabbed containers.
*   **Step 4:** Implement `app.js` building vanilla JS data fetching, active tab switching, and auto-refresh intervals ($2000$ms).
*   **Step 5:** Implement `server.py` with thread-safe file reading and error handling. Verify execution by launching `python3 server.py --port 8081`.
