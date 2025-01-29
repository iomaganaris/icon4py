import pytest
import json
import os

BENCHMARKS = {}
PREFIX = "track_"
BENCHMARK_DIR = os.environ.get("ASV_BUILD_DIR", None)
COMMIT_HASH = os.environ.get("ASV_COMMIT", None)
BENCHMARK_FILENAME = f"benchmark_runtimes_{COMMIT_HASH}.json"

if not BENCHMARKS:
    # file_path = os.path.abspath(__file__)
    # retcode = pytest.main([os.path.join(os.path.dirname(file_path), "../model/atmosphere/dycore/tests"), "--benchmark-json", BENCHMARK_FILENAME, "--benchmark-only", "-k", "test_solve_tridiagonal_matrix_for_w_back_substitution"])
    # if retcode != 0:
    #     raise Exception("Benchmarking failed")
    benchmark_file_path = os.path.join(BENCHMARK_DIR, BENCHMARK_FILENAME) if BENCHMARK_DIR else BENCHMARK_FILENAME
    with open(benchmark_file_path, "r") as f:
        benchmark_data = json.load(f)

        for benchmark in benchmark_data["benchmarks"]:
            benchmark_name = benchmark["name"]
            time = benchmark["stats"]["median"]
            asv_runtime_name = "{}{}".format(PREFIX, benchmark_name.replace("-", "_").replace("=", "_").replace("[", "_").replace("]", "_"))
            def asv_runtime_method(self, t=time): return t
            asv_runtime_method.unit = "s"
            asv_runtime_method.number = 1
            asv_runtime_method.repeat = 1
            BENCHMARKS[asv_runtime_name] = asv_runtime_method
            mem_high_watermark = benchmark["extra_info"]["memory_high_watermark"]
            def asv_memray_method(self, mem_high_watermark=mem_high_watermark): return mem_high_watermark
            asv_memray_method.unit = "MB"
            asv_memray_method.number = 1
            asv_memray_method.repeat = 1
            BENCHMARKS[f"{asv_runtime_name}_mem_high_watermark"] = asv_memray_method

