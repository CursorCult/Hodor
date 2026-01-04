---
description: "Enforce golden-thread traceability from requirements through design, implementation, and tests"
alwaysApply: true
---

# Hodor Rule (Golden Thread Traceability)

Hodor enforces a single, continuous thread of traceability across the entire software lifecycle. Every requirement must be implemented and verified, and every design choice, code change, and test must trace back to a requirement.

## Core requirements

- **Bidirectional traceability:** Requirements map forward to design, code, and tests; every artifact maps back to a requirement.
- **No orphans:** Untraced requirements, design elements, code, or tests are not allowed.
- **Single source of truth:** The traceability record is the authoritative audit trail for decisions and verification evidence.
- **Predictability over cleverness:** Prefer simple, verifiable designs that are easy to trace and test.
- **Risk-based rigor:** Apply stricter traceability and verification to higher-criticality components.

## Required artifacts

- **Requirements live in specs:** Requirements remain in `docs/specifications/` with stable IDs.
- **Trace items are explicit:** Requirements use Doorstop-style YAML items (uid/text/links).
- **Tests show satisfaction:** Tests embed HODOR metadata comments that link to requirement IDs and (optionally) test references.
- **Audit report is required:** CI regenerates the audit report using `scripts/build_traceability_audit.py` and publishes it under `docs/traceability/`.
- **No stock site:** The custom audit report is the authoritative traceability view.

Hodor is language-agnostic and applies to all non-test source code and its associated verification evidence.
