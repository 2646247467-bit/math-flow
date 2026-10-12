# Module family: recurrent

Extra checks for RNN / LSTM / GRU and stateful temporal modules.

## Must define

- Time axis and whether the step is written per-timestep or for the full sequence
- Hidden/cell state shapes and initial state assumptions
- Gate equations with element-wise $\odot$ where required (LSTM/GRU)
- Bidirectional concatenation behavior and resulting channel/feature size

## Shape discipline

If unrolling over $T$, state whether intermediate outputs are stacked to `(B, T, D)` or only the final state `(B, D)` is returned.
