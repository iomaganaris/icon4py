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

from gt4py.next.ffront.decorator import field_operator, program
from gt4py.next.ffront.fbuiltins import Field

from icon4py.atm_dyn_iconam.calculate_diagnostics_for_turbulence import (
    _calculate_diagnostics_for_turbulence,
)
from icon4py.atm_dyn_iconam.temporary_fields_for_turbulence_diagnostics import (
    _temporary_fields_for_turbulence_diagnostics,
)
from icon4py.common.dimension import C2EDim, CellDim, EdgeDim, KDim


@field_operator
def _calculate_diagnostic_quantities_for_turbulence(
    kh_smag_ec: Field[[EdgeDim, KDim], float],
    vn: Field[[EdgeDim, KDim], float],
    e_bln_c_s: Field[[CellDim, C2EDim], float],
    geofac_div: Field[[CellDim, C2EDim], float],
    diff_multfac_smag: Field[[KDim], float],
    wgtfac_c: Field[[CellDim, KDim], float],
) -> tuple[Field[[CellDim, KDim], float], Field[[CellDim, KDim], float]]:
    kh_c, div = _temporary_fields_for_turbulence_diagnostics(
        kh_smag_ec, vn, e_bln_c_s, geofac_div, diff_multfac_smag
    )
    div_ic, hdef_ic = _calculate_diagnostics_for_turbulence(div, kh_c, wgtfac_c)
    return div_ic, hdef_ic


@program
def calculate_diagnostic_quantities_for_turbulence(
    kh_smag_ec: Field[[EdgeDim, KDim], float],
    vn: Field[[EdgeDim, KDim], float],
    e_bln_c_s: Field[[CellDim, C2EDim], float],
    geofac_div: Field[[CellDim, C2EDim], float],
    diff_multfac_smag: Field[[KDim], float],
    wgtfac_c: Field[[CellDim, KDim], float],
    div_ic: Field[[CellDim, KDim], float],
    hdef_ic: Field[[CellDim, KDim], float],
):
    _calculate_diagnostic_quantities_for_turbulence(
        kh_smag_ec,
        vn,
        e_bln_c_s,
        geofac_div,
        diff_multfac_smag,
        wgtfac_c,
        out=(div_ic, hdef_ic),
    )