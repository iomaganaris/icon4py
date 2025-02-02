# ICON4Py - ICON inspired code in Python and GT4Py
#
# Copyright (c) 2022-2024, ETH Zurich and MeteoSwiss
# All rights reserved.
#
# Please, refer to the LICENSE file in the root directory.
# SPDX-License-Identifier: BSD-3-Clause

import ast
import importlib
import inspect
import re
from inspect import signature, unwrap
from types import ModuleType
from typing import Callable, List

from gt4py.next import Dimension
from gt4py.next.ffront.decorator import Program
from gt4py.next.type_system.type_translation import from_type_hint

from icon4py.tools.py2fgen.template import CffiPlugin, Func, FuncParameter
from icon4py.tools.py2fgen.utils import parse_type_spec


class ImportStmtVisitor(ast.NodeVisitor):
    """AST Visitor to extract import statements."""

    def __init__(self):
        self.import_statements: list[str] = []

    def visit_Import(self, node):
        for alias in node.names:
            import_statement = f"import {alias.name}" + (
                f" as {alias.asname}" if alias.asname else ""
            )
            self.import_statements.append(import_statement)

    def visit_ImportFrom(self, node):
        for alias in node.names:
            import_statement = f"from {node.module} import {alias.name}" + (
                f" as {alias.asname}" if alias.asname else ""
            )
            self.import_statements.append(import_statement)


class TypeHintVisitor(ast.NodeVisitor):
    """AST Visitor to extract function parameter type hints."""

    def __init__(self):
        self.type_hints: dict[str, str] = {}

    def visit_FunctionDef(self, node):
        for arg in node.args.args:
            if arg.annotation:
                annotation = ast.unparse(arg.annotation)
                self.type_hints[arg.arg] = annotation
            else:
                raise TypeError(
                    f"Missing type hint for parameter '{arg.arg}' in function '{node.name}'"
                )


def parse(module_name: str, functions: list[str], plugin_name: str) -> CffiPlugin:
    module = importlib.import_module(module_name)
    parsed_imports = _extract_import_statements(module)

    parsed_functions: list[Func] = []
    for f in functions:
        parsed_functions.append(_parse_function(module, f))

    return CffiPlugin(
        module_name=module_name,
        plugin_name=plugin_name,
        functions=parsed_functions,
        imports=parsed_imports,
    )


def _extract_import_statements(module: ModuleType) -> list[str]:
    src = inspect.getsource(module)
    tree = ast.parse(src)
    visitor = ImportStmtVisitor()
    visitor.visit(tree)
    return visitor.import_statements


def _parse_function(module: ModuleType, function_name: str) -> Func:
    func = unwrap(getattr(module, function_name))
    is_gt4py_program = isinstance(func, Program)
    type_hints = _extract_type_hint_strings(module, func, is_gt4py_program, function_name)

    params = (
        _get_gt4py_func_params(func, type_hints)
        if is_gt4py_program
        else _get_simple_func_params(func, type_hints)
    )

    return Func(name=function_name, args=params, is_gt4py_program=is_gt4py_program)


def _extract_type_hint_strings(
    module: ModuleType, func: Callable, is_gt4py_program: bool, function_name: str
):
    src = extract_function_signature(
        inspect.getsource(module) if is_gt4py_program else inspect.getsource(func), function_name
    )
    tree = ast.parse(src)
    visitor = TypeHintVisitor()
    visitor.visit(tree)
    return visitor.type_hints


def extract_function_signature(code: str, function_name: str) -> str:
    # This pattern attempts to match function definitions
    pattern = rf"\bdef\s+{re.escape(function_name)}\s*\(([\s\S]*?)\)\s*:"

    match = re.search(pattern, code)

    if match:
        # Constructing the full signature with empty return for ease of parsing by AST visitor
        signature = match.group()
        return signature.strip() + "\n  return None"
    else:
        raise Exception(f"Could not parse function signature from the following code:\n {code}")


def _get_gt4py_func_params(func: Program, type_hints: dict[str, str]) -> List[FuncParameter]:
    return [
        FuncParameter(
            name=p.id,
            d_type=parse_type_spec(p.type)[1],
            dimensions=parse_type_spec(p.type)[0],
            py_type_hint=type_hints[p.id],
        )
        for p in func.past_stage.past_node.params
    ]


def _get_simple_func_params(func: Callable, type_hints: dict[str, str]) -> List[FuncParameter]:
    sig_params = signature(func, follow_wrapped=False).parameters
    return [
        FuncParameter(
            name=s,
            d_type=parse_type_spec(from_type_hint(param.annotation))[1],
            dimensions=[
                Dimension(value=d.value)
                for d in parse_type_spec(from_type_hint(param.annotation))[0]
            ],
            py_type_hint=type_hints.get(s, None),
        )
        for s, param in sig_params.items()
    ]
