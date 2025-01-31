"""Bokeh Distplot."""
import bokeh.plotting as bkp
import numpy as np

from ...kdeplot import plot_kde
from ...plot_utils import get_bins


def _plot_dist_bokeh(
    values,
    values2=None,
    color="C0",
    kind="auto",
    cumulative=False,
    label=None,
    rotated=False,
    rug=False,
    bw=4.5,
    quantiles=None,
    contour=True,
    fill_last=True,
    plot_kwargs=None,
    fill_kwargs=None,
    rug_kwargs=None,
    contour_kwargs=None,
    contourf_kwargs=None,
    pcolormesh_kwargs=None,
    hist_kwargs=None,
    ax=None,
    show=True,
):

    if ax is None:
        tools = ",".join(
            [
                "pan",
                "wheel_zoom",
                "box_zoom",
                "lasso_select",
                "poly_select",
                "undo",
                "redo",
                "reset",
                "save,hover",
            ]
        )
        ax = bkp.figure(width=500, height=500, output_backend="webgl", tools=tools)

    if kind == "auto":
        kind = "hist" if values.dtype.kind == "i" else "kde"

    if kind == "hist":
        _histplot_bokeh_op(
            values=values, values2=values2, rotated=rotated, ax=ax, hist_kwargs=hist_kwargs
        )
    elif kind == "kde":
        if plot_kwargs is None:
            plot_kwargs = {}

        plot_kwargs.setdefault("line_color", color)
        legend = label is not None

        plot_kde(
            values,
            values2,
            cumulative=cumulative,
            rug=rug,
            label=label,
            bw=bw,
            quantiles=quantiles,
            rotated=rotated,
            contour=contour,
            legend=legend,
            fill_last=fill_last,
            plot_kwargs=plot_kwargs,
            fill_kwargs=fill_kwargs,
            rug_kwargs=rug_kwargs,
            contour_kwargs=contour_kwargs,
            contourf_kwargs=contourf_kwargs,
            pcolormesh_kwargs=pcolormesh_kwargs,
            ax=ax,
            backend="bokeh",
            show=False,
        )
    else:
        raise TypeError('Invalid "kind":{}. Select from {{"auto","kde","hist"}}'.format(kind))

    if show:
        bkp.show(ax, toolbar_location="above")
    return ax


def _histplot_bokeh_op(values, values2, rotated, ax, hist_kwargs):
    """Add a histogram for the data to the axes."""
    if values2 is not None:
        raise NotImplementedError("Insert hexbin plot here")

    legend_label = hist_kwargs.pop("label", None)
    if legend_label:
        hist_kwargs["legend_label"] = legend_label

    color = hist_kwargs.pop("color", False)
    if color:
        hist_kwargs["fill_color"] = color
        hist_kwargs["line_color"] = color

    # remove defaults for mpl
    hist_kwargs.pop("rwidth", None)
    hist_kwargs.pop("align", None)
    hist_kwargs.pop("density", None)
    hist_kwargs.pop("orientation", None)

    bins = hist_kwargs.pop("bins", None)
    if bins is None:
        bins = get_bins(values)
    density = hist_kwargs.pop("density", True)
    hist, edges = np.histogram(values, density=density, bins=bins)
    if hist_kwargs.pop("cumulative", False):
        hist = np.cumsum(hist)
        hist /= hist[-1]
    if rotated:
        ax.quad(top=edges[:-1], bottom=edges[1:], left=0, right=hist, **hist_kwargs)
    else:
        ax.quad(top=hist, bottom=0, left=edges[:-1], right=edges[1:], **hist_kwargs)
    return ax
