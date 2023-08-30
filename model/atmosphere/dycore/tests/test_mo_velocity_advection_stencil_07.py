# ICON4Py - ICON inspired code in Python and GT4Py
#
# Copyright (c) 2022, ETH Zurich and MeteoSwiss
# All rights reserved.
#
# This file is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the
# Free Software Foundation, either version 3 of the License, or any later
# version. See the LICENSE.txt file at the top-level directory of this
# distribution for a copy of the license or check <https://www.gnu.org/licenses/>.
#
# SPDX-License-Identifier: GPL-3.0-or-later

import numpy as np
import pytest

from icon4py.model.atmosphere.dycore.mo_velocity_advection_stencil_07 import (
    mo_velocity_advection_stencil_07,
)
from icon4py.model.common.dimension import CellDim, EdgeDim, KDim, VertexDim
from icon4py.model.common.test_utils.helpers import (
    StencilTest,
    random_field,
    zero_field,
)


class TestMoVelocityAdvectionStencil07(StencilTest):
    PROGRAM = mo_velocity_advection_stencil_07
    OUTPUTS = ("z_v_grad_w",)

    @staticmethod
    def reference(
        mesh,
        vn_ie: np.array,
        inv_dual_edge_length: np.array,
        w: np.array,
        z_vt_ie: np.array,
        inv_primal_edge_length: np.array,
        tangent_orientation: np.array,
        z_w_v: np.array,
        **kwargs,
    ) -> np.array:
        inv_dual_edge_length = np.expand_dims(inv_dual_edge_length, axis=-1)
        inv_primal_edge_length = np.expand_dims(inv_primal_edge_length, axis=-1)
        tangent_orientation = np.expand_dims(tangent_orientation, axis=-1)

        w_e2c = w[mesh.e2c]
        z_w_v_e2v = z_w_v[mesh.e2v]

        red_w = w_e2c[:, 0] - w_e2c[:, 1]
        red_z_w_v = z_w_v_e2v[:, 0] - z_w_v_e2v[:, 1]

        z_v_grad_w = (
            vn_ie * inv_dual_edge_length * red_w
            + z_vt_ie * inv_primal_edge_length * tangent_orientation * red_z_w_v
        )
        return dict(z_v_grad_w=z_v_grad_w)

    @pytest.fixture
    def input_data(self, mesh):
        vn_ie = random_field(mesh, EdgeDim, KDim)
        inv_dual_edge_length = random_field(mesh, EdgeDim)
        w = random_field(mesh, CellDim, KDim)
        z_vt_ie = random_field(mesh, EdgeDim, KDim)
        inv_primal_edge_length = random_field(mesh, EdgeDim)
        tangent_orientation = random_field(mesh, EdgeDim)
        z_w_v = random_field(mesh, VertexDim, KDim)
        z_v_grad_w = zero_field(mesh, EdgeDim, KDim)

        return dict(
            vn_ie=vn_ie,
            inv_dual_edge_length=inv_dual_edge_length,
            w=w,
            z_vt_ie=z_vt_ie,
            inv_primal_edge_length=inv_primal_edge_length,
            tangent_orientation=tangent_orientation,
            z_w_v=z_w_v,
            z_v_grad_w=z_v_grad_w,
        )