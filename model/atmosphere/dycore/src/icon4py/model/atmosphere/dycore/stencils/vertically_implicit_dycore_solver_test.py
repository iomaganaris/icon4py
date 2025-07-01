# ICON4Py - ICON inspired code in Python and GT4Py
#
# Copyright (c) 2022-2024, ETH Zurich and MeteoSwiss
# All rights reserved.
#
# Please, refer to the LICENSE file in the root directory.
# SPDX-License-Identifier: BSD-3-Clause

from typing import Final

import gt4py.next as gtx
from gt4py.next.ffront.experimental import concat_where
from gt4py.next.ffront.fbuiltins import astype, broadcast

from icon4py.model.common import (
    constants,
    dimension as dims,
    field_type_aliases as fa,
    model_options,
    type_alias as ta,
)
from icon4py.model.common.type_alias import vpfloat, wpfloat
from icon4py.model.common.dimension import Koff


@gtx.field_operator
def _compute1() -> tuple[
    fa.CellKField[ta.wpfloat],
]:
    out = broadcast(wpfloat("0.0"), (dims.CellDim, dims.KDim))

    return (
        out,
    )

@gtx.field_operator
def _compute2(
    tmp: fa.CellKField[ta.vpfloat],
    input: fa.CellKField[ta.wpfloat],
) -> tuple[
    fa.CellKField[ta.vpfloat],
    fa.CellKField[ta.wpfloat],
]:
    tmp2 = concat_where(
        dims.KDim == 80,
        input,
        broadcast(wpfloat("1.0"), (dims.CellDim, dims.KDim))
    )
    out = tmp2(Koff[1]) + tmp

    return (
        tmp2,
        out,
    )

@gtx.field_operator
def _compute3(
    tmp1: fa.CellKField[ta.vpfloat],
    tmp2: fa.CellKField[ta.wpfloat],
) -> tuple[
    fa.CellKField[ta.vpfloat],
]:
    out = tmp1 + tmp2

    return (
        out,
    )

@gtx.program
def vertically_implicit_solver_at_corrector_step(
    a: fa.CellKField[ta.wpfloat],
    b: fa.CellKField[ta.vpfloat],
    c: fa.CellKField[ta.vpfloat],
    out: fa.CellKField[ta.wpfloat],
    start_cell_index_nudging: gtx.int32,
    end_cell_index_local: gtx.int32,
    vertical_start_index_model_top: gtx.int32,
    vertical_end_index_model_surface: gtx.int32,
):
    _compute1(
        out=(
            c,
        ),
        domain={
            dims.CellDim: (20, 500),
            dims.KDim: (80, 81),
        },
    )
    _compute2(
        tmp=b,
        input=c,
        out=(
            c,
            out,
        ),
        domain={
            dims.CellDim: (20, 500),
            dims.KDim: (0, 80),
        },
    )

    _compute3(
        tmp1=c,
        tmp2=out,
        out=(
            out,
        ),
        domain={
            dims.CellDim: (20, 500),
            dims.KDim: (0, 80),
        },
    )
