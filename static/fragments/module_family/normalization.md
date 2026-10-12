# Module family: normalization

Extra checks for BN / LN / GN / IN and affine variants.

## Must define

- Normalized axes (which dimensions share mean/var)
- Whether affine $\gamma, \beta$ exist and their broadcast shape
- Training vs inference only if the formula differs (e.g. running stats); otherwise keep math train-agnostic
- Interaction with residual branches (pre-norm vs post-norm) when relevant to the enclosing block

## Shape discipline

Normalization usually preserves shape. If a step claims a shape change, it must be a surrounding reshape/projection, not the normalize op itself—unless the paper defines a fused op.
