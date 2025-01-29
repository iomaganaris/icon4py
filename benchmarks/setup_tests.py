import pytest
import json
import os

BENCHMARKS = {}
PREFIX = "track_"
BENCHMARK_DIR = os.environ.get("ASV_BUILD_DIR", None)
COMMIT_HASH = os.environ.get("ASV_COMMIT", None)
BENCHMARK_FILENAME = f"benchmark_runtimes_{COMMIT_HASH}.json"

benchmark_file_path = os.path.join(BENCHMARK_DIR, BENCHMARK_FILENAME) if BENCHMARK_DIR else BENCHMARK_FILENAME
with open(benchmark_file_path, "r") as f:
    benchmark_data = json.load(f)

    for benchmark in benchmark_data["benchmarks"]:
        benchmark_name = benchmark["name"]
        time = benchmark["stats"]["median"]
        asv_runtime_name = "{}runtime_{}".format(PREFIX, benchmark_name.replace("-", "_").replace("=", "_").replace("[", "_").replace("]", "_"))
        def asv_runtime_method(self, t=time): return t
        asv_runtime_method.unit = "s"
        asv_runtime_method.number = 1
        asv_runtime_method.repeat = 1
        BENCHMARKS[asv_runtime_name] = asv_runtime_method
        mem_high_watermark = benchmark["extra_info"]["memory_high_watermark"]
        asv_mem_name = "{}mem_{}".format(PREFIX, benchmark_name.replace("-", "_").replace("=", "_").replace("[", "_").replace("]", "_"))
        def asv_memray_method(self, mem_high_watermark=mem_high_watermark): return mem_high_watermark
        asv_memray_method.unit = "MB"
        asv_memray_method.number = 1
        asv_memray_method.repeat = 1
        BENCHMARKS[asv_mem_name] = asv_memray_method
