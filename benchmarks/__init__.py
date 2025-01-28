# Write the benchmarking functions here.
# See "Writing benchmarks" in the asv docs for more information.

import pytest
import json
import os

BENCHMARKS={}
PREFIX = "track_"

file_path = os.path.abspath(__file__)
retcode = pytest.main([os.path.join(os.path.dirname(file_path), "../model/atmosphere/dycore/tests"), "--benchmark-json", "benchmark_runtimes.json", "--benchmark-only", "-k", "test_solve_tridiagonal_matrix_for_w_back_substitution"])
if retcode != 0:
    raise Exception("Benchmarking failed")
with open("benchmark_runtimes.json", "r") as f:
    benchmark_data = json.load(f)

    for benchmark in benchmark_data["benchmarks"]:
        benchmark_name = benchmark["name"]
        time = benchmark["stats"]["median"]
        asv_name = "{}{}".format(PREFIX, benchmark_name.replace("-", "_").replace("=", "_").replace("[", "_").replace("]", "_"))
        def asv_method(self, t=time): return t
        asv_method.unit = "s"
        asv_method.number = 1
        asv_method.repeat = 1
        BENCHMARKS[asv_name] = asv_method

class BenchmarkMetaclass(type):
    def __dir__(cls):
        return list(BENCHMARKS.keys())
    def __getattr__(cls, name):
        if not name.startswith(PREFIX):
            raise AttributeError
        setattr(cls, name, BENCHMARKS[name])
        return getattr(cls, name)

class Benchmarks(metaclass=BenchmarkMetaclass):
    def __getattr__(self, name):
        if not name.startswith(PREFIX):
            raise AttributeError
        setattr(type(self), name, BENCHMARKS[name])
        return getattr(self, name)
