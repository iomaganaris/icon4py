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

from gt4py.next.common import GridType
from gt4py.next.ffront.decorator import field_operator, program
from gt4py.next.ffront.fbuiltins import Field, neighbor_sum

from icon4py.model.common.dimension import E2C2EO, E2C2EODim, EdgeDim, KDim


@field_operator
def _mo_solve_nonhydro_stencil_25(
    geofac_grdiv: Field[[EdgeDim, E2C2EODim], float],
    z_graddiv_vn: Field[[EdgeDim, KDim], float],
) -> Field[[EdgeDim, KDim], float]:
    z_graddiv2_vn = neighbor_sum(z_graddiv_vn(E2C2EO) * geofac_grdiv, axis=E2C2EODim)
    return z_graddiv2_vn


@program(grid_type=GridType.UNSTRUCTURED)
def mo_solve_nonhydro_stencil_25(
    geofac_grdiv: Field[[EdgeDim, E2C2EODim], float],
    z_graddiv_vn: Field[[EdgeDim, KDim], float],
    z_graddiv2_vn: Field[[EdgeDim, KDim], float],
):
    _mo_solve_nonhydro_stencil_25(geofac_grdiv, z_graddiv_vn, out=z_graddiv2_vn)