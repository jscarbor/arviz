"""Autocorrelation plot of data."""
import numpy as np

from ..data import convert_to_dataset
from .plot_utils import (
    _scale_fig_size,
    default_grid,
    xarray_var_iter,
    _create_axes_grid,
    filter_plotters_list,
)
from ..utils import _var_names


def plot_autocorr(
    data,
    var_names=None,
    max_lag=None,
    combined=False,
    figsize=None,
    textsize=None,
    ax=None,
    backend=None,
    show=True,
):
    """Bar plot of the autocorrelation function for a sequence of data.

    Useful in particular for posteriors from MCMC samples which may display correlation.

    Parameters
    ----------
    data : obj
        Any object that can be converted to an az.InferenceData object
        Refer to documentation of az.convert_to_dataset for details
    var_names : list of variable names, optional
        Variables to be plotted, if None all variable are plotted.
        Vector-value stochastics are handled automatically.
    max_lag : int, optional
        Maximum lag to calculate autocorrelation. Defaults to 100 or num draws, whichever is smaller
    combined : bool
        Flag for combining multiple chains into a single chain. If False (default), chains will be
        plotted separately.
    figsize : tuple
        Figure size. If None it will be defined automatically.
        Note this is not used if ax is supplied.
    textsize: float
        Text size scaling factor for labels, titles and lines. If None it will be autoscaled based
        on figsize.
    ax: axes
        Matplotlib axes
    backend: str
        Select plotting backend {"matplotlib","bokeh"}. Default "matplotlib".

    Returns
    -------
    axes : matplotlib axes or bokeh.figure

    Examples
    --------
    Plot default autocorrelation

    .. plot::
        :context: close-figs

        >>> import arviz as az
        >>> data = az.load_arviz_data('centered_eight')
        >>> az.plot_autocorr(data)

    Plot subset variables by specifying variable name exactly

    .. plot::
        :context: close-figs

        >>> az.plot_autocorr(data, var_names=['mu', 'tau'] )


    Combine chains collapsing by variable

    .. plot::
        :context: close-figs

        >>> az.plot_autocorr(data, var_names=['mu', 'tau'], combined=True)


    Specify maximum lag (x axis bound)

    .. plot::
        :context: close-figs

        >>> az.plot_autocorr(data, var_names=['mu', 'tau'], max_lag=200, combined=True)
    """
    data = convert_to_dataset(data, group="posterior")
    var_names = _var_names(var_names, data)

    # Default max lag to 100 or max length of chain
    if max_lag is None:
        max_lag = min(100, data["draw"].shape[0])

    plotters = filter_plotters_list(
        list(xarray_var_iter(data, var_names, combined)), "plot_autocorr"
    )
    length_plotters = len(plotters)
    rows, cols = default_grid(length_plotters)

    figsize, _, titlesize, xt_labelsize, linewidth, _ = _scale_fig_size(
        figsize, textsize, rows, cols
    )

    if ax is None:
        _, axes = _create_axes_grid(
            length_plotters,
            rows,
            cols,
            figsize=figsize,
            squeeze=False,
            sharex=True,
            sharey=True,
            backend=backend,
        )
    else:
        axes = ax

    axes = np.atleast_2d(axes)  # in case of only 1 plot

    autocorr_plot_args = dict(
        axes=axes,
        plotters=plotters,
        max_lag=max_lag,
        combined=combined,
        linewidth=linewidth,
        xt_labelsize=xt_labelsize,
        titlesize=titlesize,
    )

    if backend == "bokeh":
        from .backends.bokeh.bokeh_autocorrplot import _plot_autocorr

        autocorr_plot_args.pop("xt_labelsize")
        autocorr_plot_args.pop("titlesize")
        autocorr_plot_args["line_width"] = autocorr_plot_args.pop("linewidth")
        autocorr_plot_args["show"] = show
        axes = _plot_autocorr(**autocorr_plot_args)  # pylint: disable=unexpected-keyword-arg
    else:
        from .backends.matplotlib.mpl_autocorrplot import _plot_autocorr

        axes = _plot_autocorr(**autocorr_plot_args)

    return axes
