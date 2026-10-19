# Judge evaluation results

| Run | Note | Model | Agreed | Errors | Agreement |
|---|---|---|---|---|---|
| 2026-10-17 01:43 | baseline: run 1 | claude-haiku-4-5 | 191/200 | 0 | 95.5% |
| 2026-10-17 02:23 | baseline: run 2 | claude-haiku-5-5 | 193/200 | 0 | 96.5% |
| 2026-10-17 02:30 | baseline: run 3 | claude-sonnet-5-5 | 197/200 | 0 | 98.5% |
| 2026-10-19 01:57 | prompt v2: 5 false-rules + ignore unrelated | claude-haiku-5-5 | 197/200 | 0 | 98.5% |
| 2026-10-19 02:11 | prompt v3: 6 false-rules (+ natural verb, absurd meaning, idiom) + ignore unrelated | claude-haiku-5-5 | 195/200 | 0 | 97.5% |
| 2026-10-19 02:26 | prompt v4: v2 + idiom rule (reverted natural-verb and absurdity clauses) | claude-haiku-5-5 | 195/200 | 0 | 97.5% |
| 2026-10-19 02:41 | prompt v4: run 2 | claude-haiku-5-5 | 196/200 | 0 | 98.0% |
| 2026-10-19 02:47 | prompt v4: run 3 | claude-haiku-5-5 | 196/200 | 0 | 98.0% |
| 2026-10-19 02:54 | prompt v4: run 4 | claude-haiku-5-5 | 197/200 | 0 | 98.5% |
| 2026-10-19 03:00 | prompt v4: run 5 | claude-haiku-5-5 | 197/200 | 0 | 98.5% |
