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

from icon4py.model.common.diagnostic_calculations.stencils.diagnose_temperature import (
    diagnose_temperature,
)
from icon4py.model.common.dimension import CellDim, KDim
from icon4py.model.common.test_utils.helpers import StencilTest, random_field, zero_field
from icon4py.model.common.type_alias import vpfloat


class TestDiagnoseTemperature(StencilTest):
    PROGRAM = diagnose_temperature
    OUTPUTS = ("temperature",)

    @staticmethod
    def reference(grid, theta_v: np.array, exner: np.array, **kwargs) -> dict:
        temperature = theta_v * exner
        return dict(
            temperature=temperature,
        )

    @pytest.fixture
    def input_data(self, grid):
        theta_v = random_field(grid, CellDim, KDim, dtype=vpfloat)
        exner = random_field(grid, CellDim, KDim, dtype=vpfloat)
        temperature = zero_field(grid, CellDim, KDim, dtype=vpfloat)

        return dict(
            theta_v=theta_v,
            exner=exner,
            temperature=temperature,
            horizontal_start=0,
            horizontal_end=int32(grid.num_cells),
            vertical_start=0,
            vertical_end=int32(grid.num_levels),
        )