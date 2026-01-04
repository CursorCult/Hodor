# Part of the [CursorCult](https://github.com/CursorCult)

# Hodor

Golden-thread traceability from requirements through design, implementation, and tests.

**Install**

```sh
pipx install cursorcult
cursorcult link Hodor
```

Rule file format reference: https://cursor.com/docs/context/rules#rulemd-file-format

**When to use**

- You need audit-ready traceability across requirements, design, code, and tests.
- You operate in safety-critical or high-reliability environments.
- You want a single, trustworthy record of what was required and how it was verified.

**What it enforces**

- Bidirectional traceability between requirements and all downstream artifacts.
- No orphan requirements, designs, code, or tests.
- A single source of truth for verification evidence and decisions.
- Predictable, verifiable designs over cleverness.
- Risk-based rigor: stricter traceability for higher-criticality components.

**Project layout (recommended)**

```
docs/specifications/           # requirement source of truth (with stable IDs)
docs/specifications/requirements/<domain>/  # requirement items (MON-001, etc.)
tests/                         # tests with Requirements blocks in docstrings
docs/traceability/traceability_audit.html
```

**Traceability items**

Hodor expects:
- Doorstop-style YAML items for **requirements** (`uid`, `text`, `links`).
- Requirement IDs listed in **test docstrings** for tests (scanner-derived test items).

Test docstrings include a `Requirements:` block:

```
def test_cmd_status_success():
    """Status succeeds with default config and no issues.

    Requirements:
    - MON-002
    """
```

Test IDs are derived from the test file path (no manual IDs).

**Background**

Hodor is inspired by NASA's "golden thread" principle in Safety and Mission Assurance and software requirements such as NPR 7150.2 (SWE-052). Related guidance includes the NASA Software Engineering Handbook and NASA-STD-8739.8 (Software Assurance).

**Tooling**

Hodor ships a generator for an audit-ready HTML report:

```
python3 .cursor/rules/Hodor/scripts/build_traceability_audit.py \
  --root . \
  --req-dir docs/specifications/requirements/mon \
  --test-scan-dir tests \
  --out docs/traceability/traceability_audit.html
```

Requires: Python + PyYAML (`pip install pyyaml`).

**CI integration**

Run the generator in CI and commit the updated HTML report, similar to how coverage stats are injected into README.md.

**Credits**

- Developed by Will Wieselquist. Anyone can use it.
