# Module family: aggregation

Extra checks for pooling, SPP/ASPP, GAP/GMP, token merging, gather/scatter.

## Must define

- Aggregation domain: spatial, temporal, token, graph neighborhood, etc.
- Reduce vs keep dimensions; whether `keepdim` applies
- Multi-branch concat order and channel arithmetic ($C_1+C_2+\ldots$)
- Any upsample/restore path that returns to the original resolution

## Shape discipline

Explicitly show collapsed axes (e.g. `(B, C, H, W) -> (B, C, 1, 1)` then squeeze to `(B, C)` if that is what the paper does). Do not hide squeeze/unsqueeze.
