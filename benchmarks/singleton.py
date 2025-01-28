import pytest
import json
import os

BENCHMARKS = {}
PREFIX = "track_"
BENCHMARK_FILENAME = "benchmark_runtimes.json"

file_path = os.path.abspath(__file__)
retcode = pytest.main([os.path.join(os.path.dirname(file_path), "../model/atmosphere/dycore/tests"), "--benchmark-json", BENCHMARK_FILENAME, "--benchmark-only"])
if retcode != 0:
    raise Exception("Benchmarking failed")
with open(BENCHMARK_FILENAME, "r") as f:
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
