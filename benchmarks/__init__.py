# Write the benchmarking functions here.
# See "Writing benchmarks" in the asv docs for more information.

import singleton

class BenchmarkMetaclass(type):
    def __dir__(cls):
        return list(singleton.BENCHMARKS.keys())
    def __getattr__(cls, name):
        if not name.startswith(singleton.PREFIX):
            raise AttributeError
        setattr(cls, name, singleton.BENCHMARKS[name])
        return getattr(cls, name)

class Benchmarks(metaclass=BenchmarkMetaclass):
    def __getattr__(self, name):
        if not name.startswith(singleton.PREFIX):
            raise AttributeError
        setattr(type(self), name, singleton.BENCHMARKS[name])
        return getattr(self, name)
