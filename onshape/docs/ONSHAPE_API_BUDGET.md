# Onshape API budget: rules for this project

The Onshape account's API quota runs out (we hit "402 API limit exceeded" for about a week in November 2026).
Every request counts, including failed ones and retries. These rules apply to anyone (human or Claude) running the scripts in `tools/`.

## What things cost (requests, measured on the 2026-11-16 V6 build)

| Job | Requests |
|---|---|
| List the document's tabs | 1 |
| Upload the FeatureScript source + check it compiles | 3 |
| Build one part studio (new tab, add feature, read status, download meshes) | 5 |
| Change parameters of an existing feature (update in place) | 2-3 |
| Download meshes of one part studio (also feeds the STL export) | 1 |
| V5 "still identical" check (scratch build + delete) | 6 |
| Build an assembly with all mates (ASM-V5 / ASM-V6 style) | about 40 |
| STEP export | 3-5 |
| **Whole V6 job (upload, V5 check, V6-A, V6-B, ASM-V6, STL export)** | **about 70** |

## Rules

1. **Offline first.** Design, check and iterate on the cached meshes (`$AIRBRAKE_WORK/*.pkl`) and on STLs. Go to Onshape only to build the final version of a change.
2. **One build per batch of changes.** Collect all edits, then do one upload and one rebuild. Never upload after each small tweak.
3. **Say the cost before starting.** Before any Onshape work, Claude states the estimated number of requests (from the table) and asks the user first if it is more than 50.
4. **Update features in place** (POST to the existing feature) rather than creating new tabs or rebuilding assemblies. Assemblies follow their part studio automatically; rebuild an assembly only when the list of parts changes.
5. **No polling, no loops of GETs.** One status read after a build. The helper retries a rate-limit error once only.
6. **Hard cap per run.** `tools/osapi.py` stops a script after `ONSHAPE_CALL_BUDGET` requests (default 150). Raise it only on purpose.
7. **Log everything.** Each request is appended to `$AIRBRAKE_WORK/api_calls.log` (time, method, status, path). Count this month's calls with
   `grep -c "^2026-11" $AIRBRAKE_WORK/api_calls.log`.
8. **Exports:** download the meshes once per part studio and make every STL, plate and picture from that local copy.
9. **When the quota is low** (or a 402 appears): stop, do not retry, and switch to offline STL edits; record what still has to be built in Onshape in HANDOFF.md.

## Checking the remaining quota
The quota depends on the Onshape plan and is shown in the account owner's Onshape developer / API usage page (look under the account menu or the Onshape developer portal). The scripts cannot read it, so the log above is the running count on our side.
