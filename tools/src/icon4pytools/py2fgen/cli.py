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

import pathlib

import click

from icon4pytools.icon4pygen.bindings.utils import write_string
from icon4pytools.py2fgen.cffi import generate_and_compile_cffi_plugin
from icon4pytools.py2fgen.generate import (
    generate_c_header,
    generate_f90_interface,
    generate_python_wrapper,
)
from icon4pytools.py2fgen.parsing import parse
from icon4pytools.py2fgen.utils import Backend


@click.command("py2fgen")
@click.argument(
    "module_import_path",
    type=str,
)
@click.argument("function_name", type=str)
@click.option(
    "--build-path",
    "-b",
    type=click.Path(dir_okay=True, resolve_path=True, path_type=pathlib.Path),
    default=".",
    help="Specify the directory for generated code and compiled libraries.",
)
@click.option(
    "--debug-mode",
    "-d",
    is_flag=True,
    help="Enable debug mode to print additional runtime information.",
)
@click.option(
    "--gt4py-backend",
    "-g",
    type=click.Choice([e.name for e in Backend], case_sensitive=False),
    default="ROUNDTRIP",
    help="Set the gt4py backend to use.",
)
def main(
    module_import_path: str,
    function_name: str,
    build_path: pathlib.Path,
    debug_mode: bool,
    gt4py_backend: str,
) -> None:
    """Generate C and F90 wrappers and C library for embedding a Python module in C and Fortran."""
    backend = Backend[gt4py_backend]
    build_path.mkdir(exist_ok=True, parents=True)

    plugin = parse(module_import_path, function_name)

    c_header = generate_c_header(plugin)
    python_wrapper = generate_python_wrapper(plugin, backend.value, debug_mode)
    f90_interface = generate_f90_interface(plugin)

    generate_and_compile_cffi_plugin(plugin.plugin_name, c_header, python_wrapper, build_path)
    write_string(f90_interface, build_path, f"{plugin.plugin_name}.f90")

    if debug_mode:
        write_string(python_wrapper, build_path, f"{plugin.plugin_name}.py")


if __name__ == "__main__":
    main()