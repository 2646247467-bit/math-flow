# Core principles

Build a Math-Flow card that lets an engineer reconstruct a module's exact tensor computation without rereading the whole paper.

## Non-negotiable stance

- Trace **specific inputs → intermediate tensors → specific outputs**, not slogan-level intuition.
- Every computational step needs: operation name, formula, shape transform, and a one-line functional explanation.
- Prefer the paper's own symbols when available; if you rename symbols, provide an explicit alias table.
- Keep dimension chains continuous: step $k$ output shape must match step $k+1$ input shape (up to documented view/reshape).
- Separate paper facts from reconstruction and from textbook fallback.
- Leave unavailable details as explicit assumptions; never invent paper-only hyperparameters as if they were printed.

## Scope

Produce only the Math-Flow card (header + Sections 1–4). Do not add:

- full-paper summary or related-work survey;
- training recipes, optimizer settings, or dataset discussion (unless required by the module math);
- runnable training code dumps;
- formal peer-review judgments;
- alternate architectures “you might also try” unless the user asks.

## Provenance classes

Use these labels when a statement is not a direct transcription of the paper equation:

- `[Paper]` — taken from the paper equation/figure/text
- `[Analysis]` — faithful reconstruction from paper description
- `[Assumption]` — hyper-parameter or layout chosen because the source omitted it
- `[Canonical]` — standard definition used in `canonical-fallback` mode

## Language

- Explanatory prose: Simplified Chinese
- Section headings: exactly as specified in the output contract
- Symbols / ops / established English terms: keep canonical forms (`softmax`, `LayerNorm`, `Conv2d`)
