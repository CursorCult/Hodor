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

**Background**

Hodor is inspired by NASA's "golden thread" principle in Safety and Mission Assurance and software requirements such as NPR 7150.2 (SWE-052). Related guidance includes the NASA Software Engineering Handbook and NASA-STD-8739.8 (Software Assurance).

**Tooling**

Hodor expects a traceability system (e.g., Doorstop or an RTM) to maintain links. A simple config-driven verification script is planned but not included in this draft.

**Credits**

- Developed by Will Wieselquist. Anyone can use it.
