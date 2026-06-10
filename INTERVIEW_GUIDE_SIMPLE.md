# AWS Database Discovery — Simple Guide (Layman's Terms)

**For your interview:** Use this to explain *what* the project does and *how* the code works — without heavy jargon.

---

## 1. What Is This Project? (One Simple Story)

Imagine Airbus has **many AWS accounts** (like many separate offices). Inside each account there are **computers (EC2 servers)**. Some of those computers run **databases** (MySQL, PostgreSQL, MongoDB).

**The problem:** Nobody has one place to see *"Which server has which database, in which account, in which region?"*

**Our solution:** A **robot in the main (hub) account** that:
1. Visits each spoke account (safely, with permission)
2. Asks each Linux server: *"Do you have a database? Which one?"*
3. Collects all answers into **one file in S3**
4. Shows the results on a **web page** (API + UI)

**Important:** We never SSH into servers. We use **AWS SSM** (a built-in agent on the server) — like sending a message instead of breaking in with a key.

---

## 2. Big Picture (Like a Factory Line)

```
Schedule or button click
        ↓
   Discovery Lambda  ("the collector")
        ↓
   For each account & region:
        → Get temporary access (STS)
        → List Linux servers that are online (SSM)
        → Run a small Python script on each server
        → Read the JSON answer
        ↓
   Save everything in ONE file: S3 inventory.json
        ↓
   API Lambda reads that file when you open the UI
        ↓
   Browser shows tables and charts
```

**Think of it like:** A nightly stock check. The shop closes, someone counts everything once, writes it on a sheet. During the day, people read the sheet — they don't count live every second.

---

## 3. Main Files — What Each One Does (Simple)

| File | Simple job |
|------|------------|
| `discovery_handler.py` | **Boss script in the cloud.** Loops accounts, runs SSM, saves results to S3. |
| `api_handler.py` | **Waiter.** Reads S3 and serves JSON when the UI asks. |
| `discovery_python.py` | **Detective on the server.** Looks for MySQL/Postgres/Mongo and prints JSON. |
| `inventory_ui.html` | **Dashboard in the browser.** Dropdowns, table, pretty colors. |
| `ssm-document.json` | **Recipe for SSM.** Says: download script from S3, run with Python. |

---

## 4. Algorithms Explained in Plain English

An **algorithm** here just means: *the step-by-step recipe the code follows.*

---

### Algorithm 1: "Which accounts should we scan?"

**Where:** `discovery_handler.py` → `resolve_accounts_to_scan()`

**In simple words:**
1. Read a list of account IDs from settings (`SPOKE_ACCOUNTS`).
2. If "scan whole organization" is turned on, ask AWS Organizations for all active accounts.
3. Remove any accounts on the "exclude" list.
4. Merge manual list + org list, but **don't duplicate** the same account twice.

**Like:** Making a guest list for a party — invite people from two lists, but if someone is on both lists, only write their name once.

**Tiny code idea:**
```python
merged = list(dict.fromkeys(org_ids + manual))
```
Translation: `dict.fromkeys` = "keep order, drop duplicates."

---

### Algorithm 2: "How do we enter a spoke account safely?"

**Where:** `get_spoke_client()`

**In simple words:**
1. Hub Lambda says to AWS STS: *"I want to become the spoke role for 5 minutes."*
2. AWS gives **temporary keys** (not permanent passwords).
3. Lambda uses those keys to talk to SSM/EC2 in that account.

**Like:** A visitor badge at reception — works for a short time, then expires.

---

### Algorithm 3: "Which servers can we talk to?"

**Where:** `get_managed_instances()`

**In simple words:**
1. Ask SSM: *"Which machines do you manage?"*
2. Keep only ones that are **Online**.
3. Keep only **Linux** (not Windows).

**Why:** SSM can only run our script on managed, online Linux boxes.

---

### Algorithm 4: "What about stopped servers?"

**Where:** `get_linux_ec2_instance_ids()` + `build_stub_records_offline_ec2()`

**In simple words:**
1. EC2 API lists Linux servers even if they are **stopped**.
2. If a server is stopped, SSM usually **cannot** run the script.
3. We still add a **placeholder row** saying: *"This server exists but we skipped it — offline."*

**Like:** You note *"freezer broken, couldn't check inside"* instead of pretending it doesn't exist.

---

### Algorithm 5: "Run the script and wait for answer"

**Where:** `run_ssm_command()`

**In simple words:**
1. Send command to all target instance IDs at once.
2. Wait in a loop (check every 5 seconds).
3. Stop when status is Success / Failed / Timeout.
4. For each server, read **stdout** (normal output) and **stderr** (errors).

**Like:** Sending homework to 10 students and refreshing the portal until all submissions are in or time is up.

---

### Algorithm 6: "Turn script output into table rows"

**Where:** `parse_discovery_output()`

**In simple words:**
1. Script prints JSON like: `{ "databases": [ {...}, {...} ] }`.
2. Sometimes extra text appears before JSON — find the first `{` and parse from there.
3. For **each database** found, create **one flat row** (account, instance, engine, version, port, size…).
4. If script says success but **zero databases**, still add one row: `engine: none` (so the server shows up).

**Like:** One student can have 0 or 3 databases — we make 0 or 3 lines in the spreadsheet.

---

### Algorithm 7: "Save everything in one snapshot"

**Where:** `store_results_s3()`

**In simple words:**
1. Wrap all rows in a JSON object: `{ schema_version, updated_at, record_count, records: [...] }`.
2. Upload to S3 as **one file** (`discovery/inventory.json`).

**Why one file:** Cheap and simple for a POC. Easy for API to read whole inventory at once.

---

### Algorithm 8: "On the server — how do we detect a database?"

**Where:** `ssm/discovery_python.py`

**In simple words — for each engine (MySQL, Postgres, Mongo):**

| Step | What we do | Why |
|------|------------|-----|
| 1 | Check if process is running (`pgrep`) | Running = live database |
| 2 | If not running, check if program exists (`command -v`) | Maybe installed but stopped |
| 3 | Read version (`mysql --version`, etc.) | Know which version |
| 4 | Measure data folder size (`du -sm /var/lib/mysql`) | Rough size in MB |
| 5 | Check open port (`ss -tlnp`) | Which port it listens on |
| 6 | Read RAM (`/proc/meminfo`) and CPU cores (`/proc/cpuinfo`) | Machine size hints |

Then print **one JSON** to the screen. SSM sends that back to the hub.

**We do NOT:** log into the database, read tables, or change anything. **Read-only.**

---

### Algorithm 9: "API — filter and group data for the UI"

**Where:** `api_handler.py`

**Two main tricks:**

#### A) Filtering (`apply_record_filters`)
- User picks region, engine, etc. in the URL query.
- Loop every record; **skip** rows that don't match.
- Return what’s left.

**Like:** Filtering a spreadsheet by column.

#### B) Grouping (`group_by_instance`)
- Flat rows might have 3 lines for the same server (3 databases).
- Build a dictionary keyed by `instance_id`.
- Each instance gets a `databases: []` list inside.

**Like:** Instead of 3 separate rows for one PC, one row with 3 databases nested inside.

#### C) Live red/green for running/stopped (`enrich_instances_ec2_state`)
- Snapshot might be old.
- API can **ask EC2 right now**: *"Is this instance running or stopped?"*
- UI turns green (running) or red (stopped).

**Like:** The inventory sheet says what was true yesterday; a quick phone call confirms if the machine is on *right now*.

---

### Algorithm 10: "UI load flow"

**Where:** `inventory_ui.html`

**In simple words:**
1. User sets `BASE_URL` to the API.
2. Click **Reload** → fetch `/regions`, then `/accounts?region=...`, then `/accounts/{id}/instances?region=...`.
3. Draw table, KPI numbers, engine chart, topology for selected row.
4. Color theme changes if selected instance is running (green) or stopped (red).

**No backend in the HTML file** — it’s just JavaScript calling the API.

---

## 5. Walk Through the Code Like a Story

### Part A — Discovery Lambda starts

```python
def lambda_handler(event, context):
    accounts_to_scan = resolve_accounts_to_scan()
```

**Say in interview:** *"First we build the list of accounts — manual list or whole org."*

---

### Part B — Loop account × region

```python
for account_id in accounts_to_scan:
    for region in regions:
        ssm = get_spoke_client(account_id, "ssm", region=region)
        ec2 = get_spoke_client(account_id, "ec2", region=region)
```

**Say:** *"For each account and region we get temporary credentials and open SSM and EC2 clients."*

---

### Part C — Find targets

```python
online_instances = get_managed_instances(ssm)
result = run_ssm_command(ssm, online_ids, account_id)
```

**Say:** *"We only command instances SSM says are online. Then we run our document which executes discovery_python.py."*

---

### Part D — Parse and save

```python
records = parse_discovery_output(output, iid, account_id, region, instance_details)
all_records.extend(records)
...
store_results_s3(all_records)
```

**Say:** *"We flatten JSON into rows, merge all accounts, write one snapshot to S3."*

---

### Part E — API serves the UI

```python
items = load_all_records()          # read S3
items = apply_record_filters(...)   # filter
grouped = group_by_instance(items)  # group for table
```

**Say:** *"API is read-only on the snapshot — filter, group, optional live EC2 state — return JSON with CORS so the browser works."*

---

## 6. Key Words — Simple Definitions

| Word | Plain meaning |
|------|----------------|
| **Hub** | Main AWS account that runs discovery |
| **Spoke** | Other AWS accounts with EC2 |
| **STS / AssumeRole** | Temporary permission to act inside another account |
| **SSM** | AWS tool to run commands on servers without SSH |
| **Lambda** | Small Python function that runs in the cloud on demand |
| **S3** | File storage in AWS (our inventory JSON lives here) |
| **Snapshot** | One point-in-time copy — not live streaming |
| **CORS** | Lets a web page in the browser call our API safely |
| **StackSet** | Deploy same CloudFormation stack to many accounts at once |

---

## 7. Good Sentences for the Interview

Copy these and say them in your own voice:

1. *"We solve inventory visibility — which databases sit on which EC2, across accounts — without SSH."*

2. *"Discovery is write: scan and save. API is read: serve the last snapshot. That keeps the UI fast and cheap."*

3. *"On each server, a small Python script only checks processes, paths, and ports — it never connects to the database with a password."*

4. *"If a server is stopped, we still list it but mark discovery as skipped offline."*

5. *"New accounts can appear automatically if org-wide discovery and StackSet on the OU are configured."*

6. *"It's not real-time forever — you run discovery again or wait for the schedule, then reload the UI."*

---

## 8. Python Basics Tied to This Project

If they ask Python basics, link to your code:

| Topic | Simple explanation | Where in project |
|-------|-------------------|------------------|
| **List** | Ordered collection `[1, 2, 3]` | `all_records = []`, append rows |
| **Dict** | Key → value map | Each inventory record, `by_instance` grouping |
| **for loop** | Repeat for each item | Every account, every instance, every DB |
| **if / continue** | Skip what you don't want | Filters in `apply_record_filters` |
| **try / except** | Don't crash on errors | JSON parse, assume role failures |
| **functions** | Reusable steps | `get_spoke_client`, `parse_discovery_output` |
| **import boto3** | AWS SDK for Python | All Lambda AWS calls |
| **os.environ** | Settings from Lambda config | `SPOKE_ACCOUNTS`, regions, bucket name |
| **json.loads / dumps** | Text ↔ Python object | SSM output, S3 file |
| **logging** | Print for CloudWatch | `logger.info(...)` everywhere |

---

## 9. What We Did NOT Build (Be Honest)

- Not a live database connection monitor 24/7
- Not automatic EC2 creation (StackSet only sets IAM + SSM doc)
- Not RDS discovery (this is **EC2 self-managed DBs**)
- Not full enterprise Tier 3 (Control Tower, Config, SCPs) — that's roadmap

---

## 10. One-Page Cheat Sheet (Print This)

```
PROBLEM:  DBs on EC2 across many AWS accounts — no central list
METHOD:   SSM Run Command (no SSH), read-only Python script
FLOW:     Hub Lambda → assume role → SSM → JSON → S3 → API → UI
STORE:    One file: discovery/inventory.json
ENGINES:  MySQL, PostgreSQL, MongoDB
OFFLINE:  Stub row, discovery_status = skipped_offline
REFRESH:  Run discovery again + Reload UI
SECURITY: Temporary STS creds, read-only script, IAM least privilege
```

---

*Good luck — explain it like you're telling a colleague how the system works, not like reading AWS docs.*
