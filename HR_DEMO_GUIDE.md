# HR Demo Guide — Offline Dashboard (5 minutes)

**One file. No AWS. No login. No API.**

---

## Before the meeting (30 seconds)

1. Copy **`inventory_ui.html`** to your laptop (USB, email, Teams — whatever HR allows).
2. Double-click the file — it opens in **Chrome** or **Edge**.
3. Wait ~2 seconds. You should see:
   - Green **HR demo** badge at the top
   - Green banner: *"HR demo mode — this file runs fully offline…"*
   - Region **ap-south-1** and account **987213268214 — DEMOR1** already loaded
   - KPI numbers filled in
   - **Global inventory brain** table already loaded at the bottom

**If the page looks empty:** press **↻ Reload sample** once.

---

## What to say (simple story)

### 1. Problem (30 sec)

> *"Airbus has databases on Linux servers (EC2) spread across many AWS accounts. We need one place to see **what runs where** — MySQL, PostgreSQL, MongoDB — **without logging into each server with SSH**."*

### 2. Solution (45 sec)

> *"A scheduled scan runs from a central hub account. It uses **AWS SSM** — a secure agent already on the server — to run a **read-only script**. Results are saved as one inventory file. This dashboard reads that inventory."*

### 3. Show the screen (3 min)

Walk through in this order:

| Step | What to click / show | What to say |
|------|----------------------|-------------|
| **A** | KPI strip (3 boxes) | *"For this region and account: how many EC2 hosts, how many DB detections, which engines."* |
| **B** | Region dropdown → switch to **eu-west-1** | *"Multi-region — same tool, different AWS region."* |
| **C** | Account dropdown → **DEMOR2** | *"Multi-account — each spoke account appears here after discovery."* |
| **D** | Instance table — click **demo-app-db-01** row | *"One server can host **multiple databases**. Click a row to focus the topology diagram."* |
| **E** | Topology panel (right side) | *"Visual map: EC2 instance → detected databases. Green = running, red = stopped."* |
| **F** | Engine cards / chart | *"Quick breakdown by engine type."* |
| **G** | Scroll to **Global inventory brain** | *"Executive view — all regions and accounts in one table. Filters are client-side, no extra API calls."* |
| **H** | Filter **Engine: mysql** | *"Filter down to only MySQL rows instantly."* |
| **I** | **Download CSV** button | *"Export for reporting or sharing."* |

### 4. Close (30 sec)

> *"This demo uses **sample data** so we can present without live AWS. In production, the same UI connects to our API after a real discovery scan. Data is a **snapshot** — we run discovery on a schedule or on demand, then reload the dashboard."*

---

## Sample data in the demo

| Account label | Region | Instance | Story |
|---------------|--------|----------|--------|
| **DEMOR1** | ap-south-1 | demo-app-db-01 | Running — **MySQL + PostgreSQL** on same host |
| **DEMOR1** | ap-south-1 | demo-legacy-02 | **Stopped** — offline, scan skipped |
| **DEMOR2** | eu-west-1 | demo-mongo-01 | Running — **MongoDB** |
| **DEMOR2** | ap-south-1 | demo-pg-analytics | Running — **PostgreSQL** |
| **DEMOR3** | ap-south-1 | demo-empty-01 | Stopped — scanned, **no database** found |

---

## If HR asks common questions

| Question | Short answer |
|----------|--------------|
| Is this live AWS? | *"This file is an **offline demo** with sample data. The real system uses the same UI against our API."* |
| Do we SSH into servers? | *"No. We use **SSM Run Command** — IAM-controlled, auditable, no open SSH ports."* |
| Is it safe? | *"**Read-only** — we only check processes and paths, never connect to the database with credentials."* |
| New account onboarded? | *"StackSet deploys IAM + SSM setup; discovery picks up new accounts when configured for org-wide scan."* |
| Cost? | *"Serverless — Lambda + S3 + API Gateway. No always-on servers for the hub."* |

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Page blank / no data | Click **↻ Reload sample** |
| Styles look broken | Need internet once for Tailwind CDN — open file while online, or use Chrome with network |
| Wrong browser | Use **Chrome** or **Edge** (not old IE) |
| Want live AWS again | Edit `BASE_URL` at top of HTML to your API URL and host on https (not file://) |

---

## File to share with HR

**Only share:** `inventory_ui.html`

They do **not** need the rest of the repo for this demo.
