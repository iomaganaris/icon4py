# ICON4Py - ICON inspired code in Python and GT4Py
#
# Copyright (c) 2022-2024, ETH Zurich and MeteoSwiss
# All rights reserved.
#
# Please, refer to the LICENSE file in the root directory.
# SPDX-License-Identifier: BSD-3-Clause
from typing import Any

import gt4py.next as gtx
import numpy as np
import pytest
from gt4py.next.ffront.fbuiltins import int32

from icon4py.model.atmosphere.dycore.stencils.vertically_implicit_dycore_solver_test import (
    vertically_implicit_solver_at_corrector_step,
)
from icon4py.model.common import (
    constants,
    dimension as dims,
    model_options,
)
from icon4py.model.common.grid import base, horizontal as h_grid
from icon4py.model.common.states import utils as state_utils
from icon4py.model.common.utils import data_allocation as data_alloc
from icon4py.model.testing import helpers


class TestVerticallyImplicitSolverAtCorrectorStep(helpers.StencilTest):
    PROGRAM = vertically_implicit_solver_at_corrector_step
    OUTPUTS = (
        "c",
        "out",
    )
    MARKERS = (pytest.mark.infinite_concat_where,)

    @staticmethod
    def reference(
        connectivities: dict[gtx.Dimension, np.ndarray],
        a: np.ndarray,
        b: np.ndarray,
        c: np.ndarray,
        out: np.ndarray,
        **kwargs: Any,
    ) -> dict:
        horizontal_start = kwargs["start_cell_index_nudging"]
        horizontal_end = kwargs["end_cell_index_local"]
        n_lev = kwargs["vertical_end_index_model_surface"] - 1

        c = np.zeros_like(a, dtype=np.float32)
        out = np.ones_like(a, dtype=np.float32)

        return dict(
            c=c,
            out=out,
        )

    @pytest.fixture
    def input_data(self, grid: base.BaseGrid) -> dict[str, gtx.Field | state_utils.ScalarType]:
        a = data_alloc.random_field(grid, dims.CellDim, dims.KDim)
        b = data_alloc.random_field(grid, dims.CellDim, dims.KDim)
        c = data_alloc.random_field(grid, dims.CellDim, dims.KDim)
        out = data_alloc.random_field(grid, dims.CellDim, dims.KDim)

        cell_domain = h_grid.domain(dims.CellDim)
        start_cell_nudging = grid.start_index(cell_domain(h_grid.Zone.NUDGING))
        end_cell_local = grid.end_index(cell_domain(h_grid.Zone.LOCAL))

        return dict(
            a=a,
            b=b,
            c=c,
            out=out,
            start_cell_index_nudging=start_cell_nudging,
            end_cell_index_local=end_cell_local,
            vertical_start_index_model_top=gtx.int32(0),
            vertical_end_index_model_surface=gtx.int32(grid.num_levels + 1),
        )
