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

from dataclasses import dataclass

from icon4pytools.icon4pygen.bindings.codegen.type_conversion import (
    BUILTIN_TO_CPP_TYPE,
    BUILTIN_TO_ISO_C_TYPE,
)
from icon4pytools.icon4pygen.bindings.codegen.types import FieldEntity
from icon4pytools.icon4pygen.bindings.exceptions import BindingsRenderingException


@dataclass(frozen=True)
class FieldRenderer:
    """A class to render Field attributes for their the respective c++ or f90 bindings."""

    entity: FieldEntity

    def render_pointer(self) -> str:
        """Render c++ pointer."""
        return "" if self.entity.rank() == 0 else "*"

    def render_dim_tags(self) -> str:
        """Render c++ dimension tags."""
        tags = []
        if self.entity.is_dense() or self.entity.is_sparse() or self.entity.is_compound():
            tags.append("unstructured::dim::horizontal")
        if self.entity.has_vertical_dimension:
            tags.append("unstructured::dim::vertical")
        return ",".join(tags)

    def render_sid(self) -> str:
        """Render c++ gridtools sid for field."""
        if self.entity.rank() == 0:
            raise BindingsRenderingException("can not render sid of a scalar")

        # We want to compute the rank without the sparse dimension, i.e. if a field is horizontal, vertical or both.
        dense_rank = self.entity.rank() - int(self.entity.is_sparse() or self.entity.is_compound())
        if dense_rank == 1:
            values_str = "1"
        elif self.entity.is_compound():
            values_str = f"1, {self.entity.get_num_neighbors()} * mesh_.{self.render_stride_type()}"
        else:
            values_str = f"1, mesh_.{self.render_stride_type()}"
        return f"gridtools::hymap::keys<{self.render_dim_tags()}>::make_values({values_str})"

    def render_ranked_dim_string(self) -> str:
        """Render f90 ranked dimension string."""
        return (
            "dimension(" + ",".join([":"] * self.entity.rank()) + ")"
            if self.entity.rank() != 0
            else "value"
        )

    def render_serialise_func(self) -> str:
        """Render c++ serialisation function."""
        _serializers = {
            "E": "serialize_dense_edges",
            "C": "serialize_dense_cells",
            "V": "serialize_dense_verts",
        }
        location = str(self.entity.location)
        if location not in _serializers:
            raise BindingsRenderingException(f"location {location} is not E,C or V")
        return _serializers[location]

    def render_dim_string(self) -> str:
        """Render f90 dimension string."""
        return "dimension(*)" if self.entity.rank() != 0 else "value"

    def render_stride_type(self) -> str:
        """Render c++ stride type."""
        _strides = {"E": "EdgeStride", "C": "CellStride", "V": "VertexStride"}
        if self.entity.is_dense():
            return _strides[str(self.entity.location)]
        elif self.entity.is_sparse() or self.entity.is_compound():
            return _strides[str(self.entity.location[0])]  # type: ignore
        else:
            raise BindingsRenderingException("stride type called on scalar")

    def render_ctype(self, binding_type: str) -> str:
        """Render C datatype for a corresponding binding type."""
        match binding_type:
            case "f90":
                return BUILTIN_TO_ISO_C_TYPE[self.entity.field_type]
            case "c++":
                return BUILTIN_TO_CPP_TYPE[self.entity.field_type]
            case _:
                raise BindingsRenderingException(
                    f"binding_type {binding_type} needs to be either c++ or f90"
                )