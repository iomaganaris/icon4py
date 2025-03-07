# ICON4Py - ICON inspired code in Python and GT4Py
#
# Copyright (c) 2022-2024, ETH Zurich and MeteoSwiss
# All rights reserved.
#
# Please, refer to the LICENSE file in the root directory.
# SPDX-License-Identifier: BSD-3-Clause
import dataclasses
import os
from enum import Enum
from functools import cached_property
from types import ModuleType

import numpy as np
from gt4py.next import backend as gtx_backend, itir_python as run_roundtrip
from gt4py.next.program_processors.runners.gtfn import (
    run_gtfn_cached,
    run_gtfn_gpu_cached,
)


try:
    import dace  # type: ignore[import-untyped]
    from gt4py.next.program_processors.runners.dace import (
        run_dace_cpu,
        run_dace_cpu_noopt,
        run_dace_gpu,
        run_dace_gpu_noopt,
    )
except ImportError:
    from types import ModuleType
    from typing import Optional

    dace: Optional[ModuleType] = None  # type: ignore[no-redef] # definition needed here


def env_flag_to_bool(name: str, default: bool) -> bool:  # copied from gt4py.next.config
    """Recognize true or false signaling string values."""
    flag_value = None
    if name in os.environ:
        flag_value = os.environ[name].lower()
    match flag_value:
        case None:
            return default
        case "0" | "false" | "off":
            return False
        case "1" | "true" | "on":
            return True
        case _:
            raise ValueError(
                "Invalid environment flag value: use '0 | false | off' or '1 | true | on'."
            )


class Device(Enum):
    CPU = "CPU"
    GPU = "GPU"


class GT4PyBackend(Enum):
    CPU = "run_gtfn_cached"
    GPU = "run_gtfn_gpu_cached"
    ROUNDTRIP = "run_roundtrip"
    DACE_CPU = "run_dace_cpu"
    DACE_GPU = "run_dace_gpu"
    DACE_CPU_NOOPT = "run_dace_cpu_noopt"
    DACE_GPU_NOOPT = "run_dace_gpu_noopt"


@dataclasses.dataclass
class Icon4PyConfig:
    parallel_run: bool = dataclasses.field(
        default_factory=lambda: env_flag_to_bool("ICON4PY_PARALLEL", True)
    )

    @cached_property
    def icon4py_backend(self) -> str:
        backend = os.environ.get("ICON4PY_BACKEND", "CPU")
        if hasattr(GT4PyBackend, backend):
            return backend
        else:
            raise ValueError(
                f"Invalid ICON4Py backend: {backend}. \n"
                f"Available backends: {', '.join([f'{k}' for k in GT4PyBackend.__members__.keys()])}"
            )

    @cached_property
    def icon4py_dace_orchestration(self) -> bool:
        # Any value other than None will be considered as True
        return env_flag_to_bool("ICON4PY_DACE_ORCHESTRATION", False)

    @cached_property
    def array_ns(self) -> ModuleType:
        if self.device == Device.GPU:
            import cupy as cp  # type: ignore # either `import-not-found` or `import-untyped`

            return cp
        else:
            return np

    @cached_property
    def gt4py_runner(self) -> gtx_backend.Backend:
        backend_map: dict[str, gtx_backend.Backend] = {
            GT4PyBackend.CPU.name: run_gtfn_cached,
            GT4PyBackend.GPU.name: run_gtfn_gpu_cached,
            GT4PyBackend.ROUNDTRIP.name: run_roundtrip,
        }
        if dace:
            backend_map |= {
                GT4PyBackend.DACE_CPU.name: run_dace_cpu,
                GT4PyBackend.DACE_GPU.name: run_dace_gpu,
                GT4PyBackend.DACE_CPU_NOOPT.name: run_dace_cpu_noopt,
                GT4PyBackend.DACE_GPU_NOOPT.name: run_dace_gpu_noopt,
            }
        return backend_map[self.icon4py_backend]

    @cached_property
    def device(self) -> Device:
        device_map = {
            GT4PyBackend.CPU.name: Device.CPU,
            GT4PyBackend.GPU.name: Device.GPU,
            GT4PyBackend.ROUNDTRIP.name: Device.CPU,
        }
        if dace:
            device_map |= {
                GT4PyBackend.DACE_CPU.name: Device.CPU,
                GT4PyBackend.DACE_GPU.name: Device.GPU,
                GT4PyBackend.DACE_CPU_NOOPT.name: Device.CPU,
                GT4PyBackend.DACE_GPU_NOOPT.name: Device.GPU,
            }
        device = device_map[self.icon4py_backend]
        return device


config = Icon4PyConfig()
backend = config.gt4py_runner
dace_orchestration = config.icon4py_dace_orchestration
device = config.device
