# ICON4Py - ICON inspired code in Python and GT4Py
#
# Copyright (c) 2022-2024, ETH Zurich and MeteoSwiss
# All rights reserved.
#
# Please, refer to the LICENSE file in the root directory.
# SPDX-License-Identifier: BSD-3-Clause

import pytest

from icon4py.model.common import dimension as dims
from icon4py.model.common.metrics.compute_wgtfac_c import compute_wgtfac_c
from icon4py.model.common.type_alias import wpfloat
from icon4py.model.common.utils import data_allocation as data_alloc
from icon4py.model.testing import datatest_utils as dt_utils, helpers


@pytest.mark.embedded_remap_error
@pytest.mark.datatest
@pytest.mark.parametrize("experiment", [dt_utils.REGIONAL_EXPERIMENT, dt_utils.GLOBAL_EXPERIMENT])
def test_compute_wgtfac_c(icon_grid, metrics_savepoint, backend):  # fixture
    wgtfac_c = data_alloc.zero_field(
        icon_grid, dims.CellDim, dims.KDim, dtype=wpfloat, extend={dims.KDim: 1}, backend=backend
    )
    wgtfac_c_ref = metrics_savepoint.wgtfac_c()
    z_ifc = metrics_savepoint.z_ifc()
    k = data_alloc.index_field(
        grid=icon_grid, dim=dims.KDim, extend={dims.KDim: 1}, backend=backend
    )

    vertical_end = icon_grid.num_levels

    compute_wgtfac_c.with_backend(backend)(
        wgtfac_c,
        z_ifc,
        k,
        nlev=vertical_end,
        offset_provider={"Koff": dims.KDim},
    )

    assert helpers.dallclose(wgtfac_c.asnumpy(), wgtfac_c_ref.asnumpy())
