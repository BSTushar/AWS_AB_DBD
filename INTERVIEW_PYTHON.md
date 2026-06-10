# Python Interview Guide — Basics (Simple & Practical)

**For your 30-min interview.** Short answers you can say out loud. Examples are plain Python 3.

---

## 1. Why Python? (If they ask)

> *"Readable, fast to build with, huge ecosystem (boto3 for AWS, pytest/unittest for tests). Good for scripts, APIs, and automation — which is exactly what our discovery Lambdas use."*

---

## 2. Data Types — Know These Cold

| Type | What it is | Example |
|------|------------|---------|
| **int** | Whole number | `42` |
| **float** | Decimal | `3.14` |
| **str** | Text | `"hello"` |
| **bool** | True / False | `True`, `False` |
| **list** | Ordered, changeable | `[1, 2, 3]` |
| **tuple** | Ordered, **cannot change** | `(1, 2)` |
| **dict** | Key → value | `{"name": "Tom", "age": 25}` |
| **set** | Unique items, no order | `{1, 2, 3}` |
| **None** | "Nothing" / empty | `x = None` |

### List vs tuple vs set (very common question)

```python
# List — you can append, change
nums = [1, 2, 3]
nums.append(4)

# Tuple — fixed (good for pairs you won't change)
point = (10, 20)

# Set — removes duplicates
ids = list({1, 2, 2, 3})   # [1, 2, 3] (order may vary)
```

**Say:** *"List when I need to grow or edit. Tuple when the group is fixed. Set when I only care about unique values."*

---

## 3. Variables & Naming

```python
account_id = "123456789012"   # snake_case is Python style
MAX_TIMEOUT = 60              # ALL_CAPS for constants
```

- Python is **dynamically typed** — you don't write `int x = 5`; the type follows the value.
- **`is` vs `==`**
  - `==` → same **value**
  - `is` → same **object in memory** (use for `None`: `if x is None`)

```python
a = [1, 2]
b = [1, 2]
a == b    # True  (same contents)
a is b    # False (different list objects)
```

---

## 4. Strings

```python
name = "mysql"
msg = f"Engine is {name}"           # f-string (preferred)
msg = "Engine is {}".format(name)   # older style

s = "  hello  "
s.strip()          # "hello"
s.lower()          # "  hello  "
s.split(",")       # split by comma
",".join(["a","b"]) # "a,b"

"linux" in platform.lower()   # True — substring check
```

**Your project uses:** `.strip()`, `.lower()`, f-strings for ARNs like `f"arn:aws:iam::{account_id}:role/{role_name}"`.

---

## 5. If / Elif / Else

```python
status = "Success"

if status == "Success":
    print("OK")
elif status == "Failed":
    print("Bad")
else:
    print("Unknown")
```

**Truthy / falsy** (common trick question):

| Falsy | Everything else is truthy |
|-------|----------------------------|
| `False`, `None`, `0`, `""`, `[]`, `{}`, `()` | e.g. `"hello"`, `[0]`, `{"a": 1}` |

```python
if accounts:        # empty list = False
    scan(accounts)
```

---

## 6. Loops

### for loop

```python
for account in ["111", "222", "333"]:
    print(account)

for i, item in enumerate(["a", "b"]):
    print(i, item)   # 0 a, 1 b
```

### while loop

```python
while time.time() < end_time:
    time.sleep(5)
    # check status, break when done
```

**Your project:** Discovery Lambda polls SSM in a `while` loop until Success/Failed/timeout.

### break vs continue

- **`break`** — leave the loop completely
- **`continue`** — skip rest of this round, go to next item

```python
for record in records:
    if record.get("region") != "eu-west-1":
        continue      # skip this record
    results.append(record)
```

---

## 7. List / Dict / Set Comprehensions

**Shorthand to build a new list:**

```python
# Long way
out = []
for a in accounts:
    if a.strip():
        out.append(a.strip())

# Comprehension
out = [a.strip() for a in accounts if a.strip()]
```

**Dict comprehension:**

```python
tags = {t["Key"]: t["Value"] for t in tag_list if "Key" in t}
```

**Set comprehension:**

```python
exclude = {x.strip() for x in env.split(",") if x.strip()}
```

**Interview line:** *"Comprehensions are the same logic as a for-loop, just shorter and often clearer for simple filters/maps."*

---

## 8. Functions

```python
def greet(name, greeting="Hello"):
    """Docstring — optional description."""
    return f"{greeting}, {name}"

greet("Tom")              # Hello, Tom
greet("Tom", "Hi")        # Hi, Tom
```

### *args and **kwargs

```python
def log(*args, **kwargs):
    print(args)    # tuple of extra positional args
    print(kwargs)  # dict of keyword args
```

**When asked:** *"` *args` collects extra positional arguments; `**kwargs` collects keyword arguments. Useful for wrappers and flexible APIs."*

### Mutable default argument trap (classic question)

```python
# BAD — same list reused every call!
def add_item(x, items=[]):
    items.append(x)
    return items

# GOOD
def add_item(x, items=None):
    if items is None:
        items = []
    items.append(x)
    return items
```

---

## 9. Modules & Imports

```python
import json
import os
from datetime import datetime

import boto3   # third-party (AWS SDK)
```

- **`import x`** — whole module
- **`from x import y`** — one name from module
- **`if __name__ == "__main__":`** — code runs only when file is executed directly, not when imported

```python
# discovery_python.py pattern
def main():
    ...

if __name__ == "__main__":
    main()
```

**Say:** *"So the same file can be imported as a module or run as a script."*

---

## 10. Files & `with`

```python
with open("/proc/meminfo") as f:
    for line in f:
        if line.startswith("MemTotal:"):
            mem_kb = int(line.split()[1])
```

**`with`** = context manager → file **always closed**, even if error.

---

## 11. Exceptions (try / except)

```python
try:
    data = json.loads(text)
except json.JSONDecodeError as e:
    logger.warning("Bad JSON: %s", e)
    data = {}
except Exception as e:
    logger.error("Unexpected: %s", e)
    raise          # re-raise if you can't handle it
finally:
    pass           # always runs (cleanup)
```

**Your project pattern:** Don't crash the whole Lambda — log, return empty list or skip that account.

**They may ask:** *"When to catch vs raise?"*
- **Catch** when you can recover (bad JSON on one instance → skip it)
- **Raise** when caller must know (S3 bucket missing → fail the run)

---

## 12. JSON in Python

```python
import json

obj = {"status": "ok", "count": 3}
text = json.dumps(obj)              # Python → string
text = json.dumps(obj, default=str) # datetime etc. → str

back = json.loads(text)             # string → Python
```

---

## 13. Dictionaries — Deep Dive

```python
d = {"engine": "mysql", "port": 3306}

d.get("engine")           # "mysql"
d.get("missing", 0)       # 0 — default if key missing
d["engine"]               # KeyError if missing

"engine" in d               # True
d.keys() / d.values() / d.items()

# Safe nested access
tags = inst.get("Tags") or []
```

**Grouping pattern (like your API):**

```python
by_instance = {}
for row in records:
    iid = row["instance_id"]
    if iid not in by_instance:
        by_instance[iid] = {"databases": []}
    by_instance[iid]["databases"].append(row)
```

---

## 14. OOP — Classes (Basics)

```python
class DatabaseRecord:
    def __init__(self, engine, port):
        self.engine = engine
        self.port = port

    def label(self):
        return f"{self.engine}:{self.port}"

r = DatabaseRecord("mysql", 3306)
print(r.label())
```

| Term | Meaning |
|------|---------|
| **Class** | Blueprint |
| **Object / instance** | One thing built from the class |
| **`__init__`** | Constructor — runs when you create object |
| **`self`** | The current instance |
| **Method** | Function on a class |
| **Inheritance** | Child class gets parent methods |

```python
class Animal:
    def speak(self):
        return "..."

class Dog(Animal):
    def speak(self):
        return "woof"
```

**Your Lambdas mostly use functions**, not classes — that's normal for small AWS handlers.

---

## 15. Common Built-ins (Know Names)

| Function | Does |
|----------|------|
| `len(x)` | Length |
| `range(5)` | 0,1,2,3,4 |
| `sorted(list)` | New sorted list |
| `min` / `max` / `sum` | Math on iterables |
| `any([False, True])` | True if any truthy |
| `all([True, True])` | True if all truthy |
| `isinstance(x, dict)` | Type check |
| `type(x)` | What type is x |

```python
accounts = sorted(set(account_ids))
if all(a.isdigit() for a in accounts):
    ...
```

---

## 16. `lambda` (Small Anonymous Function)

```python
square = lambda x: x * x
sorted(items, key=lambda i: i["port"])
```

**Not related to AWS Lambda** — same word, different thing. AWS Lambda = serverless function; Python `lambda` = one-line function.

---

## 17. Generators & `yield` (Light)

```python
def read_lines(path):
    with open(path) as f:
        for line in f:
            yield line.strip()   # produces one at a time, saves memory
```

**Say:** *"Generator yields items lazily instead of building a huge list in memory."*

---

## 18. Decorators (One Sentence)

```python
@patch("module.function")
def test_something(self):
    ...
```

**Say:** *"A decorator wraps a function — runs something before/after. In tests, `@patch` replaces a dependency with a fake."*

---

## 19. Virtual Env & pip (If They Ask Dev Setup)

```bash
python -m venv .venv
.venv\Scripts\activate    # Windows
pip install -r requirements.txt
```

**Your repo:** `requirements.txt` has `boto3>=1.26.0`.

---

## 20. Testing (unittest — You Have This in Repo)

```python
import unittest
from unittest.mock import patch

class MyTests(unittest.TestCase):
    @patch("api_handler.load_all_records", return_value=[])
    def test_health(self, mock_load):
        resp = api_handler.lambda_handler(event, None)
        self.assertEqual(resp["statusCode"], 200)

if __name__ == "__main__":
    unittest.main()
```

| Piece | Purpose |
|-------|---------|
| `unittest.TestCase` | Test class |
| `assertEqual(a, b)` | a must equal b |
| `@patch` | Mock external call (no real AWS) |
| `setUp` / `tearDown` | Run before/after each test (optional) |

---

## 21. Top 20 Interview Questions + Short Answers

### 1. List vs tuple?
**List** mutable; **tuple** immutable. Tuple uses less memory, can be dict keys if all items hashable.

### 2. Shallow vs deep copy?
**Shallow** — new container, same inner objects. **Deep** — copies nested objects too (`copy.deepcopy`).

### 3. What is GIL?
Global Interpreter Lock — one thread runs Python bytecode at a time in CPython. Fine for I/O (network, files); threads don't speed CPU-heavy math much. Use **multiprocessing** for CPU parallel work.

### 4. `==` vs `is`?
Value equality vs identity. Use `is None`, not `== None`.

### 5. How do you handle errors?
`try/except`, log, return safe default or re-raise. Don't swallow errors silently.

### 6. Mutable vs immutable?
**Immutable:** int, str, tuple, frozenset — can't change in place. **Mutable:** list, dict, set.

### 7. What is `*args` / `**kwargs`?
Extra positional / keyword arguments as tuple / dict.

### 8. List comprehension vs map/filter?
All valid; comprehensions are more Pythonic and readable for simple cases.

### 9. What is PEP 8?
Python style guide — snake_case, 4 spaces, line length, imports order.

### 10. How does `import` work?
Python searches `sys.path`, loads module once (cached in `sys.modules`).

### 11. `def` vs `lambda`?
`def` for named, multi-line functions; `lambda` for tiny one-liners.

### 12. What is `None`?
Singleton meaning "no value". Type is `NoneType`.

### 13. Dictionary get vs `[]`?
`.get(key, default)` avoids KeyError.

### 14. How to reverse a list?
`lst.reverse()` in place, or `lst[::-1]` / `reversed(lst)` new view.

### 15. Remove duplicates keeping order?
`list(dict.fromkeys(items))` — same trick as in your discovery handler.

### 16. Read a file line by line?
`with open(...) as f: for line in f:` — memory efficient.

### 17. What is docstring?
String right after `def` — documents the function (`help(func)`).

### 18. `pass` vs `continue` vs `break`?
`pass` = do nothing placeholder; `continue` = next loop iteration; `break` = exit loop.

### 19. Type hints (optional modern Python)?
```python
def add(a: int, b: int) -> int:
    return a + b
```
Documentation + tooling; not required at runtime.

### 20. How do you debug?
`print` / `logging`, debugger (`pdb`), read stack trace bottom-up, reproduce with small input.

---

## 22. Small Coding Patterns They Might Ask You to Explain

### Swap two values
```python
a, b = b, a
```

### Count things
```python
from collections import Counter
Counter(["mysql", "mysql", "postgres"])
```

### Default dict for grouping
```python
from collections import defaultdict
groups = defaultdict(list)
groups["i-123"].append(record)
```

### Enumerate with index
```python
for idx, account in enumerate(accounts, start=1):
    print(idx, account)
```

### Zip two lists
```python
for id, name in zip(ids, names):
    ...
```

---

## 23. Python + AWS (Tie to Your Project)

```python
import os
import boto3

# Config from Lambda environment
bucket = os.environ.get("S3_BUCKET", "")

# Client
s3 = boto3.client("s3")
s3.get_object(Bucket=bucket, Key="discovery/inventory.json")

# Pagination
paginator = s3.get_paginator("list_objects_v2")
for page in paginator.paginate(Bucket=bucket):
    ...
```

**Say:** *"boto3 is the AWS SDK. Lambdas use env vars for config and boto3 clients for S3, STS, SSM, EC2."*

---

## 24. Logging (Production Style)

```python
import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

logger.info("Scanning account %s", account_id)
logger.warning("Parse failed: %s", err)
logger.error("AssumeRole failed", exc_info=True)
```

**Prefer `%s` formatting in logging** — string only built if level is enabled.

---

## 25. One-Page Revision (Memorize Tonight)

```
TYPES:     list[], dict{}, set{}, tuple(), str, int, float, bool, None
LOOP:      for x in items: ...  |  while cond: ...
COMP:      [x for x in items if cond]
FUNC:      def name(a, b=default): return ...
ERROR:     try / except / finally / raise
JSON:      json.loads, json.dumps
FILE:      with open(path) as f:
TRUTH:     empty list/dict/""/0/None = False
is vs ==:  is for None; == for values
TEST:      unittest + mock.patch
AWS:       boto3 + os.environ
STYLE:     snake_case, readable > clever
```

---

## 26. If They Give a Live Python Question

Stay calm. Talk through steps:

1. **Read input** — what type? list of dicts?
2. **Edge cases** — empty list? None? missing key?
3. **Use `.get()`** on dicts
4. **Write loop or comprehension**
5. **Return** the result

**Example:** *"Return all account IDs that have MySQL"*

```python
def mysql_accounts(records):
    ids = set()
    for r in records:
        if not isinstance(r, dict):
            continue
        if str(r.get("engine", "")).lower() == "mysql":
            ids.add(r.get("account_id"))
    return sorted(ids)
```

---

*Good luck — keep answers short, give one example, connect to your project when you can.*
