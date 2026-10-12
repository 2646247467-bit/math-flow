# Module family: convolution

Extra checks for convolution / local-kernel modules.

## Must define

- Input layout: usually $X \in \mathbb{R}^{B \times C_{\mathrm{in}} \times H \times W}$
- Kernel size $k$, stride $s$, padding $p$, dilation $d$, groups $g$
- Output channels $C_{\mathrm{out}}$ and spatial size formula for $H', W'$
- Whether depthwise / pointwise / separable stages are separate steps
- Bias and activation placement if they matter to shape or residual fusion

## Spatial size reminder

For standard Conv2d-style ops:

$$
H' = \left\lfloor \frac{H + 2p - d(k-1) - 1}{s} \right\rfloor + 1
$$

(and likewise for $W'$). If the paper uses “same” padding, state the assumed $H'=H$ condition explicitly as `[Assumption]` when not proven.
