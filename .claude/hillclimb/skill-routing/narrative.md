| round | change | test | train | all | recall | specificity | $/run |
|---|---|---|---|---|---|---|---|
| 0 | baseline | 0.894 | 0.825 | 0.862 | 0.77 | 1.00 | $0.0183 |
| 1 | rich descriptions (deliverable, audience, indirect shapes, 'use first, before git', 'Not for') | 1.000 | 1.000 | 1.000 | 1.00 | 1.00 | $0.0176 |

Best so far: v1. All 17 baseline Bash-first misses disappeared; no wrong-skill picks, no false triggers on 'none' cases. Caveat: 100% is the ceiling of this eval (n=22 test, CI wide); it cannot discriminate further.
