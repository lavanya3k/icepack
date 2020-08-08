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

import numpy as np
import matplotlib.pyplot as plt
import firedrake
from firedrake import interpolate, as_vector
import icepack, icepack.plot

def test_plot_mesh():
    nx, ny = 32, 32
    Lx, Ly = 1e5, 1e5
    mesh = firedrake.RectangleMesh(nx, ny, Lx, Ly)
    fig, axes = icepack.plot.subplots()
    icepack.plot.triplot(mesh, axes=axes)
    legend = axes.legend()
    assert legend is not None


def test_plot_field():
    mesh = firedrake.UnitSquareMesh(32, 32)
    Q = firedrake.FunctionSpace(mesh, family='CG', degree=1)
    x, y = firedrake.SpatialCoordinate(mesh)
    u = interpolate(x * y, Q)

    filled_contours = icepack.plot.tricontourf(u)
    assert filled_contours is not None
    colorbar = plt.colorbar(filled_contours)
    assert colorbar is not None

    contours = icepack.plot.tricontour(u)
    assert contours is not None

    colors = icepack.plot.tripcolor(u)
    assert colors is not None


def test_plot_vector_field():
    nx, ny = 32, 32
    mesh = firedrake.UnitSquareMesh(nx, ny)
    V = firedrake.VectorFunctionSpace(mesh, family='CG', degree=1)

    x, y = firedrake.SpatialCoordinate(mesh)
    u = interpolate(as_vector((x + 0.01, x * y * (1 - y) * (y - 0.5))), V)

    arrows = icepack.plot.quiver(u)
    assert arrows is not None

    streamlines = icepack.plot.streamplot(u, resolution=1 / nx)
    assert streamlines is not None


def test_plot_extruded_field():
    nx, ny = 32, 32
    mesh2d = firedrake.UnitSquareMesh(nx, ny)
    mesh3d = firedrake.ExtrudedMesh(mesh2d, layers=1)
    x, y, z = firedrake.SpatialCoordinate(mesh3d)

    Q = firedrake.FunctionSpace(mesh3d, family='CG', degree=2,
                                vfamily='GL', vdegree=4)
    q = interpolate((x**2 - y**2) * (1 - z**4), Q)
    q_contours = icepack.plot.tricontourf(q)
    assert q_contours is not None

    V = firedrake.VectorFunctionSpace(mesh3d, dim=2, family='CG', degree=2,
                                      vfamily='GL', vdegree=4)
    u = interpolate(as_vector((1 - z**4, 0)), V)
    u_contours = icepack.plot.tricontourf(u)
    assert u_contours is not None
