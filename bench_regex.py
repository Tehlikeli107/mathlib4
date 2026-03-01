import re
import timeit

def with_compile():
    version_pattern = re.compile(r'v4\.\d+\.\d+(?:-rc\d+)?$')
    return version_pattern.match('v4.17.0-rc1')

version_pattern_global = re.compile(r'v4\.\d+\.\d+(?:-rc\d+)?$')
def without_compile():
    return version_pattern_global.match('v4.17.0-rc1')

print("With compile inside:", timeit.timeit(with_compile, number=1000000))
print("With compile outside:", timeit.timeit(without_compile, number=1000000))
