"""Matplotlib energyplot."""
import matplotlib.pyplot as plt

from ...kdeplot import plot_kde
from ....stats import bfmi as e_bfmi


def _plot_energy(
    ax,
    series,
    energy,
    kind,
    bfmi,
    figsize,
    xt_labelsize,
    linewidth,
    fill_kwargs,
    plot_kwargs,
    bw,
    legend,
):
    if ax is None:
        _, ax = plt.subplots(figsize=figsize, constrained_layout=True)

    if kind == "kde":
        for alpha, color, label, value in series:
            fill_kwargs["alpha"] = alpha
            fill_kwargs["color"] = color
            plot_kwargs.setdefault("color", color)
            plot_kwargs.setdefault("alpha", 0)
            plot_kwargs.setdefault("linewidth", linewidth)
            plot_kde(
                value,
                bw=bw,
                label=label,
                textsize=xt_labelsize,
                fill_kwargs=fill_kwargs,
                plot_kwargs=plot_kwargs,
                ax=ax,
                legend=False,
            )
    elif kind in {"hist", "histogram"}:
        for alpha, color, label, value in series:
            ax.hist(
                value.flatten(),
                bins="auto",
                density=True,
                alpha=alpha,
                label=label,
                color=color,
                **plot_kwargs
            )

    else:
        raise ValueError("Plot type {} not recognized.".format(kind))

    if bfmi:
        for idx, val in enumerate(e_bfmi(energy)):
            ax.plot([], label="chain {:>2} BFMI = {:.2f}".format(idx, val), alpha=0)
    if legend:
        ax.legend()

    ax.set_xticks([])
    ax.set_yticks([])

    return ax
