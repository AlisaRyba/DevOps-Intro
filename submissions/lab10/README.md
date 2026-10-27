# Lab 10 evidence

## Scope

This directory contains measured evidence, not example values. The owner pushed both release tags. The v0.1.1 workflow's test, publish and Render deploy jobs succeeded, and the public application was independently checked after readiness. All three independent idle/wake cycles are complete: **12.805613 / 14.896333 / 13.723240 seconds**. Each returned HTTP 200 QuickNotes JSON and lost its distinctive synthetic note.

The full narrative and design answers are in [the submission](../lab10.md).

## Evidence groups

| Files | Meaning |
|---|---|
| `release-bootstrap.json`, `release-ci-deploy.json` | Remote run IDs, outcomes, job links, published digests and CI-triggered deployment identity |
| `anonymous-pull-v0.1.*.txt`, `manifest-v0.1.*.json` | Public pull without registry credentials; AMD64/ARM64 manifests and provenance entries |
| `render-ci-configuration.json` | Secret/variable names and configured status only; no hook value |
| `render-initial-deploy-log.txt`, `render-ci-deploy-log.txt` | Actual Render/CI log excerpts; deployment duration is not cold-start latency |
| `render-idle-wake-log.txt` | Actual three shutdown/startup pairs from the Render application log |
| `render-health-*.txt`, `render-notes-*.json` | Actual public HTTP responses before the idle experiments |
| `warm.json` | Five final v0.1.1 warm requests; p50 **0.330455 seconds** |
| `warm-initial.json` | Earlier v0.1.0 warm series; not mixed into the final series |
| `idle-cycle-N.json` | One independent idle interval: wall-clock times, platform shutdown/startup, no application polling, linked measurements and persistence result |
| `cold-N.json` | Raw curl metadata for exactly one cold health request, including HTTP status, TLS result and `time_total` |
| `cold-N-body.txt`, `cold-N-headers.txt` | Corresponding actual response, proving QuickNotes JSON rather than a proxy loading page |
| `note-before-idle.json`, `note-before-idle-N.json`, `notes-after-cold-N.json` | Distinctive synthetic notes and the actual list after each wake; match title/creation time, not a reusable ID alone |
| `render-note-before-idle-initial.json` | Earlier bootstrap probe, lost across redeployment; not used as an isolated idle test |
| `local-checks.txt`, `latency-local-arm64.json` | Original local builds/tests/helper validation; loopback timings are **not** cloud measurements |
| `final-checks.txt` | Actual final helper-test, workflow-lint, document-link and saved-evidence verification results |

`warm.json` is the measurement helper's report format. Cold JSON files are curl's raw `%{json}` output, with their experiment context in separate `idle-cycle-N.json` files. All times are seconds unless a field explicitly says otherwise. Wall-clock UTC and curl's elapsed durations have different roles: the former proves the idle interval, the latter measures the request.

No personal notes or local data volumes were uploaded. No credentials belong in this directory. The fake `DO_NOT_PRINT` hook in the helper's offline test fixture is not a real deploy credential.
