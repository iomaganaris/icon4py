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
from gt4py.next.ffront.fbuiltins import int32

from icon4py.model.atmosphere.dycore.mo_solve_nonhydro_stencil_05 import (
    mo_solve_nonhydro_stencil_05,
)
from icon4py.model.common.dimension import CellDim, KDim
from icon4py.model.common.test_utils.helpers import StencilTest, random_field, zero_field
from icon4py.model.common.type_alias import vpfloat


class TestMoSolveNonhydroStencil05(StencilTest):
    PROGRAM = mo_solve_nonhydro_stencil_05
    OUTPUTS = ("z_exner_ic",)

    @staticmethod
    def reference(grid, wgtfac_c: np.array, z_exner_ex_pr: np.array, **kwargs) -> dict:
        z_exner_ex_pr_offset_1 = np.roll(z_exner_ex_pr, shift=1, axis=1)
        z_exner_ic = wgtfac_c * z_exner_ex_pr + (1.0 - wgtfac_c) * z_exner_ex_pr_offset_1
        z_exner_ic[:, 0] = 0
        return dict(z_exner_ic=z_exner_ic)

    @pytest.fixture
    def input_data(self, grid):
        z_exner_ex_pr = random_field(grid, CellDim, KDim, dtype=vpfloat)
        wgtfac_c = random_field(grid, CellDim, KDim, dtype=vpfloat)
        z_exner_ic = zero_field(grid, CellDim, KDim, dtype=vpfloat)

        return dict(
            wgtfac_c=wgtfac_c,
            z_exner_ex_pr=z_exner_ex_pr,
            z_exner_ic=z_exner_ic,
            horizontal_start=int32(0),
            horizontal_end=int32(grid.num_cells),
            vertical_start=int32(1),
            vertical_end=int32(grid.num_levels),
        )