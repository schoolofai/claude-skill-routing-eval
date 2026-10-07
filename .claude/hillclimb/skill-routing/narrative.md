| round | change | test | train | all | recall | specificity | $/run |
|---|---|---|---|---|---|---|---|
| 0 | baseline | 0.894 | 0.825 | 0.862 | 0.77 | 1.00 | $0.0183 |
| 1 | rich descriptions (deliverable, audience, indirect shapes, 'use first, before git', 'Not for') | 1.000 | 1.000 | 1.000 | 1.00 | 1.00 | $0.0176 |

Best so far: v1. All 17 baseline Bash-first misses disappeared; no wrong-skill picks, no false triggers on 'none' cases. Caveat: 100% is the ceiling of this eval (n=22 test, CI wide); it cannot discriminate further.

## Harder eval (53 cases: +12 user look-alikes c43-c54)
| variant | all 53 | train (25) | test (28) | orig 41 | new 12 |
|---|---|---|---|---|---|
| baseline (original descriptions) | 85.5% | 82.7% | 88.1% | 86.2% | 83.3% |
| v1 | 100% | 100% | 100% | 100% | 100% |

Baseline passes all 10 'none' look-alikes and misses both firing ones (c53, c54: Bash-first, 3/3). v1 passes all 12, including the 10 look-alikes, so the 'use this first, before git' wording did not cause false triggers.

## 63 cases (+10 between-two-skills, c55-c64)
| variant | all 63 | train (30) | test (33) | orig 41 | look-alikes 12 | between 10 |
|---|---|---|---|---|---|---|
| baseline | 78.3% | 75.6% | 80.8% | 86.2% | 83.3% | 40.0% |
| v1 | 100% | 100% | 100% | 100% | 100% | 100% |

Baseline missed 6 of 10 between-two cases 3/3 (c55, c56, c57, c60, c61, c64): five Bash-first, c56 text-only. No wrong-skill picks in either variant.
