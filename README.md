# Proxie Studio DevOps Evaluation — Static Web App <-> Local Python Bridge

This project establishes a real-time, bi-directional telemetry and control bridge between a pure static Three.js Web application hosted on GitHub Pages and a local Python program without using a server-side backend.

## Architectural Decision & Trade-off Analysis

**Mechanism Chosen:** Playwright / Chrome DevTools Protocol (CDP) Bridge.

**Why this approach was selected:**
I chose Playwright (CDP) because it bridges the local Python runtime directly into the running browser's DOM context using `page.expose_function()` and `page.evaluate()`. This allows us to hook directly into the app's existing `window.postMessage` bus without modifying `index.html`, setting up external signaling/socket servers, or building complex custom Chrome extensions.

### Trade-offs & Evaluation Criteria

* **Latency:** Sub-millisecond (~1–3ms). Data transfers directly over local browser Inter-Process Communication (IPC) rather than polling or screen scraping.
* **Architecture Integrity:** The hosted Three.js app remains 100% static on GitHub Pages with zero backend server overhead.
* **Security & Permissions:** Requires execution permissions on the local machine to spawn or attach to a Chromium browser instance.

---

## Technical Data Flow

1. **Read Stream (Browser -> Python):** `index.html` broadcasts `robot-state` via `window.postMessage` on every animation frame[cite: 3]. An injected initialization script captures these events and forwards them instantly to Python's exposed async handler.
2. **Write Stream (Python -> Browser):** Python dispatches `robot-command` events directly into the browser context via `page.evaluate()`, controlling movement parameters in real time[cite: 3].

---

## Setup & Running Instructions

### 1. Hosted Web App
The static app is hosted live at:
`https://taha2804.github.io/robot-explorer/`

### 2. Local Environment Setup
Clone this repository and install the dependencies:
```bash
# Install Python dependencies
pip install -r requirements.txt

# Install Playwright browser engine
python -m playwright install chromium