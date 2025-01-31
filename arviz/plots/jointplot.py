"""Joint scatter plot of two variables."""
from ..data import convert_to_dataset
from .plot_utils import _scale_fig_size, xarray_var_iter, get_coords
from ..utils import _var_names


def plot_joint(
    data,
    var_names=None,
    coords=None,
    figsize=None,
    textsize=None,
    kind="scatter",
    gridsize="auto",
    contour=True,
    fill_last=True,
    joint_kwargs=None,
    marginal_kwargs=None,
    ax=None,
    backend=None,
    show=True,
):
    """
    Plot a scatter or hexbin of two variables with their respective marginals distributions.

    Parameters
    ----------
    data : obj
        Any object that can be converted to an az.InferenceData object
        Refer to documentation of az.convert_to_dataset for details
    var_names : Iter of 2 e.g. (var_1, var_2)
        Variables to be plotted, two variables are required.
    coords : mapping, optional
        Coordinates of var_names to be plotted. Passed to `Dataset.sel`
    figsize : tuple
        Figure size. If None it will be defined automatically.
    textsize: float
        Text size scaling factor for labels, titles and lines. If None it will be autoscaled based
        on figsize.
    kind : str
        Type of plot to display (scatter, kde or hexbin)
    gridsize : int or (int, int), optional.
        The number of hexagons in the x-direction. Ignored when hexbin is False. See `plt.hexbin`
        for details
    contour : bool
        If True plot the 2D KDE using contours, otherwise plot a smooth 2D KDE. Defaults to True.
    fill_last : bool
        If True fill the last contour of the 2D KDE plot. Defaults to True.
    joint_kwargs : dicts, optional
        Additional keywords modifying the join distribution (central subplot)
    marginal_kwargs : dicts, optional
        Additional keywords modifying the marginals distributions (top and right subplot)
    ax : tuple of axes, optional
        Tuple containing (axjoin, ax_hist_x, ax_hist_y). If None, a new figure and axes
        will be created.

    Returns
    -------
    axjoin : matplotlib axes, join (central) distribution
    ax_hist_x : matplotlib axes, x (top) distribution
    ax_hist_y : matplotlib axes, y (right) distribution

    Examples
    --------
    Scatter Joint plot

    .. plot::
        :context: close-figs

        >>> import arviz as az
        >>> data = az.load_arviz_data('non_centered_eight')
        >>> az.plot_joint(data,
        >>>             var_names=['theta'],
        >>>             coords={'school': ['Choate', 'Phillips Andover']},
        >>>             kind='scatter',
        >>>             figsize=(6, 6))

    Hexbin Joint plot

    .. plot::
        :context: close-figs

        >>> az.plot_joint(data,
        >>>             var_names=['theta'],
        >>>             coords={'school': ['Choate', 'Phillips Andover']},
        >>>             kind='hexbin',
        >>>             figsize=(6, 6))

    KDE Joint plot

    .. plot::
        :context: close-figs

        >>> az.plot_joint(data,
        >>>                 var_names=['theta'],
        >>>                 coords={'school': ['Choate', 'Phillips Andover']},
        >>>                 kind='kde',
        >>>                 figsize=(6, 6))

    Overlayed plots:

    .. plot::
        :context: close-figs

        >>> data2 = az.load_arviz_data("centered_eight")
        >>> kde_kwargs = {"contourf_kwargs": {"alpha": 0}, "contour_kwargs": {"colors": "k"}}
        >>> ax = az.plot_joint(
        ...     data, var_names=("mu", "tau"), kind="kde", fill_last=False,
        ...     joint_kwargs=kde_kwargs, marginal_kwargs={"color": "k"}
        ... )
        >>> kde_kwargs["contour_kwargs"]["colors"] = "r"
        >>> az.plot_joint(
        ...     data2, var_names=("mu", "tau"), kind="kde", fill_last=False,
        ...     joint_kwargs=kde_kwargs, marginal_kwargs={"color": "r"}, ax=ax
        ... )

    """
    valid_kinds = ["scatter", "kde", "hexbin"]
    if kind not in valid_kinds:
        raise ValueError(
            ("Plot type {} not recognized." "Plot type must be in {}").format(kind, valid_kinds)
        )

    data = convert_to_dataset(data, group="posterior")

    if coords is None:
        coords = {}

    var_names = _var_names(var_names, data)

    plotters = list(xarray_var_iter(get_coords(data, coords), var_names=var_names, combined=True))

    if len(plotters) != 2:
        raise Exception(
            "Number of variables to be plotted must 2 (you supplied {})".format(len(plotters))
        )

    figsize, ax_labelsize, _, xt_labelsize, linewidth, _ = _scale_fig_size(figsize, textsize)

    if joint_kwargs is None:
        joint_kwargs = {}

    if marginal_kwargs is None:
        marginal_kwargs = {}
    marginal_kwargs.setdefault("plot_kwargs", {})
    marginal_kwargs["plot_kwargs"]["linewidth"] = linewidth

    plot_joint_kwargs = dict(
        ax=ax,
        figsize=figsize,
        plotters=plotters,
        ax_labelsize=ax_labelsize,
        xt_labelsize=xt_labelsize,
        kind=kind,
        contour=contour,
        fill_last=fill_last,
        joint_kwargs=joint_kwargs,
        gridsize=gridsize,
        marginal_kwargs=marginal_kwargs,
    )

    if backend == "bokeh":
        from .backends.bokeh.bokeh_jointplot import _plot_joint

        plot_joint_kwargs.pop("ax_labelsize")
        plot_joint_kwargs["marginal_kwargs"]["plot_kwargs"]["line_width"] = plot_joint_kwargs[
            "marginal_kwargs"
        ]["plot_kwargs"].pop("linewidth")
        plot_joint_kwargs["show"] = show
        axes = _plot_joint(**plot_joint_kwargs)  # pylint: disable=unexpected-keyword-arg
    else:
        from .backends.matplotlib.mpl_jointplot import _plot_joint

        axes = _plot_joint(**plot_joint_kwargs)

    return axes
