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

from icon4py.model.atmosphere.dycore.temporary_fields_for_turbulence_diagnostics import (
    temporary_fields_for_turbulence_diagnostics,
)
from icon4py.model.common.dimension import C2EDim, CellDim, EdgeDim, KDim
from icon4py.model.common.test_utils.helpers import (
    StencilTest,
    random_field,
    zero_field,
)


class TestTemporaryFieldsForTurbulenceDiagnostics(StencilTest):
    PROGRAM = temporary_fields_for_turbulence_diagnostics
    OUTPUTS = ("div", "kh_c")

    @staticmethod
    def reference(
        mesh,
        kh_smag_ec: np.array,
        vn: np.array,
        e_bln_c_s: np.array,
        geofac_div: np.array,
        diff_multfac_smag: np.array,
        **kwargs,
    ) -> dict:
        geofac_div = np.expand_dims(geofac_div, axis=-1)
        vn_geofac = vn[mesh.c2e] * geofac_div
        div = np.sum(vn_geofac, axis=1)

        e_bln_c_s = np.expand_dims(e_bln_c_s, axis=-1)
        diff_multfac_smag = np.expand_dims(diff_multfac_smag, axis=0)
        mul = kh_smag_ec[mesh.c2e] * e_bln_c_s
        summed = np.sum(mul, axis=1)
        kh_c = summed / diff_multfac_smag

        return dict(div=div, kh_c=kh_c)

    @pytest.fixture
    def input_data(self, mesh):
        vn = random_field(mesh, EdgeDim, KDim)
        geofac_div = random_field(mesh, CellDim, C2EDim)
        kh_smag_ec = random_field(mesh, EdgeDim, KDim)
        e_bln_c_s = random_field(mesh, CellDim, C2EDim)
        diff_multfac_smag = random_field(mesh, KDim)

        kh_c = zero_field(mesh, CellDim, KDim)
        div = zero_field(mesh, CellDim, KDim)

        return dict(
            kh_smag_ec=kh_smag_ec,
            vn=vn,
            e_bln_c_s=e_bln_c_s,
            geofac_div=geofac_div,
            diff_multfac_smag=diff_multfac_smag,
            kh_c=kh_c,
            div=div,
        )