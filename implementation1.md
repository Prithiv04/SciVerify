# Implement Phase 17.1 — Fix Live Quota-Abort Reporting Path

Implement the approved Phase 17.1 plan in the SciVerify repository.

## First: Inspect Before Editing

Review the current implementation of:

* `backend/app/evaluation/run.py`
* `backend/app/evaluation/report.py`
* `backend/app/evaluation/live_diagnostics.py`
* `backend/app/evaluation/checkpoint.py`
* `backend/app/services/llm/provider.py`
* existing tests under `backend/app/tests/`

Pay particular attention to the current return-value flow between:

```text
main()
→ _run_live_evaluation()
→ write_reports()
→ build_report_payload()
```

Do not assume the architecture described in the plan is still identical to the current code. Adapt the implementation to the actual repository state.

## Primary Bug to Fix

The latest live run correctly detected Groq daily quota exhaustion:

```text
Skipped live case ... llm_failure - LLM quota exhausted (daily token limit reached).
```

However, after processing the quota failures, the application crashed with:

```text
AttributeError: 'int' object has no attribute 'aggregate'
```

The traceback indicates that an integer exit code from `_run_live_evaluation()` is being passed into report generation, where an evaluation result object is expected.

Fix this cleanly.

## Implementation Requirements

### 1. Separate evaluation result from process exit code

Ensure `_run_live_evaluation()` and `main()` have a consistent contract.

The evaluation result object and CLI exit status must not be confused.

A preferred design is:

```text
_run_live_evaluation()
    ↓
returns evaluation result
    ↓
main()
    ↓
generates report
    ↓
returns exit code
```

If the existing architecture requires another design, use the smallest safe refactor that achieves the same separation.

Do not break the offline evaluation path.

### 2. Correct quota-abort behavior

When:

```python
LiveFailureCategory.LLM_QUOTA_EXCEEDED
```

is detected:

* stop processing additional live cases;
* do not wait for the provider retry timer;
* preserve the checkpoint;
* preserve failed-case information;
* construct a valid partial evaluation result;
* generate a partial report when possible;
* print a clear quota-abort summary;
* return a non-zero CLI exit code.

Do not make additional unnecessary LLM requests.

### 3. Preserve checkpoint/resume functionality

Keep the existing:

```text
--checkpoint-dir
--resume
--resume-live
```

behavior intact.

The checkpoint must remain valid after quota exhaustion.

Do not reset previously recorded cases.

Verify that `--resume-live` still maps correctly to `--resume`.

### 4. Fix report generation

Ensure:

```python
write_reports(result, ...)
```

always receives the actual live evaluation result object.

Never pass:

```python
1
```

or another integer exit code into:

```python
build_report_payload()
```

A quota-aborted run must not crash while generating its report.

If no cases were successfully evaluated, do not fabricate accuracy metrics. Represent unavailable metrics appropriately.

The partial report should still contain useful information such as:

* total eligible cases
* successfully evaluated cases
* skipped cases
* verification failures
* quota failures
* retrieval diagnostics
* failure categories
* checkpoint/resume information where supported

### 5. Add regression tests

Add/update tests in:

```text
backend/app/tests/
```

Cover:

#### Quota abort

Simulate:

```text
LLM_QUOTA_EXCEEDED
```

and verify:

* no crash;
* checkpoint persisted;
* partial result created;
* report generation succeeds;
* non-zero exit code returned.

#### Successful live evaluation

Verify:

* evaluation result reaches report generation;
* report generation succeeds;
* exit code is `0`.

#### Resume

Verify:

```text
--resume-live
```

loads the checkpoint and skips already completed cases.

#### Offline regression

Ensure the existing offline evaluation remains unchanged.

Use mocks for LLM calls. Do NOT consume real Groq quota during tests.

## Testing

Run:

```powershell
cd C:\Users\shaki\OneDrive\Desktop\SciVerify\backend
python -m pytest -q
```

The complete suite must pass.

Then run:

```powershell
git diff --check
git status
```

Fix any trailing whitespace or formatting problems.

## Important Safety Constraints

Do NOT modify:

* verification agent logic
* evidence ranking
* retrieval algorithms
* verdict determination
* offline benchmark fixtures
* `.env`
* API keys
* Groq configuration
* unrelated production logic

Keep the changes narrowly scoped to:

```text
live evaluation
quota-abort flow
result/exit-code handling
partial reporting
checkpoint/resume behavior
tests
```

## Do NOT Run a Real Live Benchmark

Do not execute:

```powershell
python -m app.evaluation.run --live ...
```

during implementation.

The current Groq daily token quota is exhausted, and the purpose of this phase is to fix the control flow using mocked tests.

Only run the full pytest suite and other non-quota-consuming validation.

## Final Output

After implementation, report:

1. Files changed.
2. Root cause of the `int has no attribute aggregate` error.
3. How the result/exit-code flow was fixed.
4. How quota-abort behavior now works.
5. Tests added/updated.
6. Final pytest result.
7. `git diff --check` result.
8. Whether the working tree is clean or what remains to commit.

Do not modify unrelated files or automatically start another implementation phase.
