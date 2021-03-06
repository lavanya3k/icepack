# Copyright (C) 2020 by Daniel Shapero <shapero@uw.edu>
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

r"""Solvers for ice physics models"""

import firedrake
from firedrake import dx, Constant
from icepack.optimization import MinimizationProblem, NewtonSolver
from . import utilities
from ..utilities import default_solver_parameters

class FlowSolver(object):
    r"""Solves the diagnostic and prognostic models of ice physics

    The actual solver data is initialized lazily on the first call
    """
    def __init__(self, model, **kwargs):
        self._model = model
        self._fields = {}

        self.dirichlet_ids = kwargs.pop('dirichlet_ids', [])
        self.side_wall_ids = kwargs.pop('side_wall_ids', [])
        self.tolerance = kwargs.pop('tolerance', 1e-12)

    @property
    def model(self):
        r"""The physics model that this object solves"""
        return self._model

    @property
    def fields(self):
        r"""Dictionary of all fields that are part of the simulation"""
        return self._fields

    def _diagnostic_setup(self, **kwargs):
        for name, field in kwargs.items():
            if name in self.fields.keys():
                self.fields[name].assign(field)
            else:
                self.fields[name] = utilities.copy(field)

        # Create homogeneous BCs for the Dirichlet part of the boundary
        u = self.fields['u']
        V = u.function_space()
        # NOTE: This will have to change when we do Stokes!
        bcs = None
        if self.dirichlet_ids:
            bcs = firedrake.DirichletBC(V, Constant((0, 0)), self.dirichlet_ids)

        # Find the numeric IDs for the ice front
        boundary_ids = u.ufl_domain().exterior_facets.unique_markers
        ice_front_ids_comp = set(self.dirichlet_ids + self.side_wall_ids)
        ice_front_ids = list(set(boundary_ids) - ice_front_ids_comp)

        # Create the action and scale functionals
        _kwargs = {
            'side_wall_ids': self.side_wall_ids,
            'ice_front_ids': ice_front_ids
        }
        action = self.model.action(**self.fields, **_kwargs)
        scale = self.model.scale(**self.fields, **_kwargs)

        # Set up a minimization problem and solver
        quadrature_degree = self.model.quadrature_degree(**self.fields)
        params = {'quadrature_degree': quadrature_degree}
        problem = MinimizationProblem(action, scale, u, bcs, params)
        self._diagnostic_solver = NewtonSolver(problem, self.tolerance)

    def diagnostic_solve(self, **kwargs):
        r"""Solve the diagnostic model physics for the ice velocity"""
        # Set up the diagnostic solver if it hasn't been already, otherwise
        # copy all the input field values
        if not hasattr(self, '_diagnostic_solver'):
            self._diagnostic_setup(**kwargs)
        else:
            for name, field in kwargs.items():
                if isinstance(field, firedrake.Function):
                    self.fields[name].assign(field)

        # Solve the minimization problem and return the velocity field
        self._diagnostic_solver.solve()
        return self.fields['u'].copy(deepcopy=True)

    def _prognostic_setup(self, **kwargs):
        for name, field in kwargs.items():
            if name in self.fields.keys():
                self.fields[name].assign(field)
            else:
                self.fields[name] = utilities.copy(field)

        # Create the residual equation represending the PDE
        dt = Constant(1.)
        dh_dt = self.model.continuity(dt, **self.fields)
        h = self.fields['h']
        h_0 = h.copy(deepcopy=True)
        q = firedrake.TestFunction(h.function_space())
        F = (h - h_0) * q * dx - dt * dh_dt

        # Create problem and solver objects for this equation
        # TODO: make form compiler and solver parameters customizable
        problem = firedrake.NonlinearVariationalProblem(F, h)
        self._prognostic_solver = firedrake.NonlinearVariationalSolver(
            problem, solver_parameters=default_solver_parameters
        )
        self._thickness_old = h_0
        self._timestep = dt

    def prognostic_solve(self, dt, **kwargs):
        r"""Solve the prognostic model physics for the new value of the ice
        thickness"""
        if not hasattr(self, '_prognostic_solver'):
            self._prognostic_setup(**kwargs)
        else:
            for name, field in kwargs.items():
                if isinstance(field, firedrake.Function):
                    self.fields[name].assign(field)

        h = self.fields['h']
        self._thickness_old.assign(h)
        self._timestep.assign(dt)
        self._prognostic_solver.solve()
        return h.copy(deepcopy=True)
