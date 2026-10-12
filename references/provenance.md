# Provenance and honesty rules

Math-Flow cards must remain usable when the source is incomplete.

## Labels

| Label | Meaning | Typical use |
|-------|---------|-------------|
| `[Paper]` | Directly supported by paper equation/figure/text | Copied or lightly notationally normalized formulas |
| `[Analysis]` | Reconstructed from prose/block diagram | Missing closed form but clear algorithmic intent |
| `[Assumption]` | Chosen because source omitted a value | $B$, $h$, padding, exact `same` size policy |
| `[Canonical]` | Standard definition outside the paper | `canonical-fallback` mode |

## Mode policy

### paper-equation

- Prefer paper symbol names.
- If you rename, add `Symbol alias:` bullets in Section 2.
- Do not replace a paper-specific reduction with a textbook attention block.

### paper-structure

- Reconstruct step-by-step math that implements the described module.
- Mark reconstructed equations `[Analysis]`.
- If two reconstructions are equally plausible, pick the simpler one and list the ambiguity under Assumptions.

### canonical-fallback

- Allowed when the user names a well-known module without paper text.
- Header `Source coverage` must be `Canonical knowledge only`.
- State which canonical variant you use (e.g. Vaswani et al. scaled dot-product MHSA).

## Forbidden

- Presenting guesses as paper equations
- Borrowing hyperparameters from an unrelated implementation silently
- Dropping residual connections that the paper includes
- Changing Q/K/V sharing (self vs cross) without evidence
