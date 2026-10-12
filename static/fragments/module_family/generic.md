# Module family: generic

Fallback when the module is not clearly attention / convolution / normalization / aggregation / recurrent.

## Must define

- A one-sentence computational role (map / mix / gate / route / sample / …)
- Every axis name that appears in shapes
- Deterministic ordering of fused paper ops when the paper draws a single block diagram

## Rule

Prefer splitting a “black-box” block into atomic shape-changing steps over writing one opaque formula that hides reshapes.
