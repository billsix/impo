"""ePiX graphs for the problem notebooks: the curve of an x-y equation.

A graphing exercise ("graph by plotting points: $y = 2x - 3$") gets a figure
drawn with ePiX (github.com/billsix/epix-mirror), the maintainer's C++ figure
library, through its Python front-end `epix`, the way geometricalgebra's
notebooks draw live figures. ePiX is built from source in the notebook image
(study/notebooks/Dockerfile); this module imports it only when a graph is drawn,
so the rest of study/tools works without it. Every argument is passed by keyword.
"""

from __future__ import annotations

from typing import Any

import sympy

import solver

# The light opaque panel every figure sits on (as in geometricalgebra).
BACKGROUND: str = "#f2f2f2"
WINDOW: int = 10  # the graph shows -WINDOW..WINDOW on both axes


def visible_runs(curve: Any, samples: int = 400) -> list[tuple[float, float]]:
    """The x-intervals where the curve is defined and inside the window (ePiX does
    not clip a plot to the picture), found by sampling.

    >>> visible_runs(lambda t: 4 * t)
    [(-2.5, 2.5)]
    """
    runs: list[tuple[float, float]] = []
    start: float | None = None
    step: float = 2 * WINDOW / samples
    previous: float = -WINDOW
    index: int
    for index in range(samples + 1):
        t: float = -WINDOW + index * step
        try:
            inside: bool = abs(float(curve(t))) <= WINDOW
        except (ValueError, ZeroDivisionError, OverflowError, TypeError):
            inside = False
        if inside and start is None:
            start = t
        if not inside and start is not None:
            runs.append((start, previous))
            start = None
        previous = t
    if start is not None:
        runs.append((start, float(WINDOW)))
    return [(a, b) for a, b in runs if b > a]


def graph(problem: str) -> Any:
    """Draw the x-y equation of a graphing problem; returns the ePiX figure (it
    displays itself in a notebook), or None when the problem has no such equation."""
    import epix  # ty: ignore[import-not-found]  # only in the notebook image

    equation: solver.Value = solver.graph_target(problem)
    if equation is None:
        return None
    names: dict[str, sympy.Symbol] = {str(s): s for s in equation.free_symbols}
    x: sympy.Symbol = names.get("x", sympy.Symbol("x", positive=True))
    branches: list[sympy.Expr] = (
        [b for b in sympy.solve(equation, names["y"]) if b.is_real is not False]
        if "y" in names
        else []
    )
    low: Any = epix.Point(x=-WINDOW, y=-WINDOW)
    high: Any = epix.Point(x=WINDOW, y=WINDOW)
    with epix.figure(lower_left=low, upper_right=high, size="3x3in", background=BACKGROUND) as fig:
        epix.pen(color=epix.black(intensity=0.2), width=0.4)
        epix.grid(nx=2 * WINDOW, ny=2 * WINDOW)
        epix.pen(color=epix.black(intensity=0.6), width=0.8)
        epix.line(tail=epix.Point(x=-WINDOW, y=0), head=epix.Point(x=WINDOW, y=0))
        epix.line(tail=epix.Point(x=0, y=-WINDOW), head=epix.Point(x=0, y=WINDOW))
        epix.pen(color=epix.blue(), width=1.4)
        branch: sympy.Expr
        for branch in branches:
            curve: Any = sympy.lambdify(x, branch, "math")
            low_t: float
            high_t: float
            for low_t, high_t in visible_runs(curve):
                epix.plot(
                    f=lambda t, curve=curve: float(curve(t)), t_min=low_t, t_max=high_t, n=100
                )
        if not branches:  # no y in the solved form: a vertical line x = a
            at: float = float(sympy.solve(equation, x)[0])
            epix.line(tail=epix.Point(x=at, y=-WINDOW), head=epix.Point(x=at, y=WINDOW))
    return fig
