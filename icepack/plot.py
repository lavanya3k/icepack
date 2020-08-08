# Copyright (C) 2017-2020 by Daniel Shapero <shapero@uw.edu>
#
# This file is part of icepack.
#
# icepack is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# The full text of the license can be found in the file LICENSE in the
# icepack source directory or at <http://www.gnu.org/licenses/>.

r"""Utilities for plotting gridded data, meshes, and finite element fields

This module contains thin wrappers around functionality in matplotlib for
plotting things. For example, `triplot`, `tricontourf`, and `streamplot`
all call the equivalent matplotlib functions under the hood for plotting
respectively an unstructured mesh, a scalar field on an unstructured mesh,
and a vector field on an unstructured mesh.

The return types should be the same as for the corresponding matplotlib
function. Usually the return type is something that inherits from the
class `ScalarMappable` so that you can make a colorbar out of it.
"""

import warnings
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter
import firedrake
import icepack


def _get_coordinates(mesh):
    r"""Return the coordinates of a mesh if the mesh is piecewise linear,
    or interpolate them to piecewise linear if the mesh is curved"""
    coordinates = mesh.coordinates
    element = coordinates.function_space().ufl_element()
    if element.degree() != 1:
        from firedrake import VectorFunctionSpace, interpolate
        V = VectorFunctionSpace(mesh, element.family(), 1)
        coordinates = interpolate(coordinates, V)

    return coordinates


def subplots(*args, **kwargs):
    subplot_kw = kwargs.get('subplot_kw', {})
    subplot_kw['adjustable'] = subplot_kw.get('adjustable', 'box')
    kwargs['subplot_kw'] = subplot_kw
    fig, axes = plt.subplots(*args, **kwargs)

    def fmt(ax):
        ax.set_aspect('equal')
        ax.xaxis.set_major_formatter(ScalarFormatter(useOffset=True))
        ax.yaxis.set_major_formatter(ScalarFormatter(useOffset=True))
        ax.xaxis.get_major_formatter().set_powerlimits((0, 0))
        ax.yaxis.get_major_formatter().set_powerlimits((0, 0))

    try:
        for ax in axes:
            fmt(ax)
    except TypeError:
        fmt(axes)

    return fig, axes


def triplot(mesh, *args, **kwargs):
    r"""Plot a mesh with a different color for each boundary segment"""
    return firedrake.triplot(mesh, *args, **kwargs)


def _project_to_2d(function):
    mesh = function.ufl_domain()
    return function if mesh.layers is None else icepack.depth_average(function)


def tricontourf(function, *args, **kwargs):
    r"""Create a filled contour plot of a finite element field"""
    return firedrake.tricontourf(_project_to_2d(function), *args, **kwargs)


def tricontour(function, *args, **kwargs):
    r"""Create a contour plot of a finite element field"""
    return firedrake.tricontour(_project_to_2d(function), *args, **kwargs)


def tripcolor(function, *args, **kwargs):
    r"""Create a pseudo-color plot of a finite element field"""
    return firedrake.tripcolor(_project_to_2d(function), *args, **kwargs)


def quiver(function, *args, **kwargs):
    r"""Make a quiver plot of a vector field"""
    return firedrake.quiver(_project_to_2d(function), *args, **kwargs)


def streamplot(u, **kwargs):
    r"""Draw streamlines of a vector field"""
    if u.ufl_shape != (2,):
        raise ValueError('Stream plots only defined for 2D vector fields!')

    if 'precision' in kwargs:
        warnings.warn("'precision' argument is deprecated", DeprecationWarning)

    if 'density' in kwargs:
        warnings.warn("'density' argument is deprecated", DeprecationWarning)
        kwargs['resolution'] = kwargs.pop('density')

    u = _project_to_2d(u)
    return firedrake.streamplot(u, **kwargs)
