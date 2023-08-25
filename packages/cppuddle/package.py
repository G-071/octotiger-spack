# Copyright 2013-2023 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack.error import SpackError
from spack.package import *


class Cppuddle(CMakePackage):
    """Utility library to handle small, reusable pools of both device
    memory buffers (via allocators) and device executors (with multiple
    scheduling policies and optional work aggregation / kernel fusion)."""

    homepage = "https://github.com/SC-SGS/CPPuddle"
    url = "https://github.com/SC-SGS/CPPuddle/archive/refs/tags/v0.1.0.zip"
    git = "https://github.com/SC-SGS/CPPuddle"

    maintainers("G-071")

    version("develop", branch="develop")
    version("master", branch="master")
    version("0.3.0", sha256="5e9c10e0069dc5bfb48a52510868d7aadeb5b60da12ab9b2e777ffaafc8fd999", preferred=True)
    version("0.2.1", sha256="f230008a8edbd46c7436af51a03f2b98ccf3b89af0391b4321a50a778232c693")
    version("0.2.0", sha256="1e92f8d6372295696a98e75dd6af577bdbe1107486011a1359381a56e0ae8923")
    version("0.1.0", sha256="6d3be4b835f6c2bcbac940a09f953ec2aa31e16230c3c4605e3c6a0a64b19d13")

    variant("allocator_counters", when="@0.1.0:", default=False, description="Activate allocation counters")
    variant("buffer_recycling", when="@0.2.1:", default=True,
            description="Enable buffer recycling [+recommended]")
    variant("buffer_content_recycling", when="@0.2.1:", default=True,
            description="Enable aggressive content recycling")
    variant("hpx", default=True, description="Build with HPX support", when="@0.1.0:")
    variant("number_buffer_buckets", when="@0.3.0: +hpx", default=128, values=lambda x: isinstance(x, str)
            and x.isdigit(),  description="Maximum number of supported workers")
    variant("max_number_gpus", when="@0.3.0:", default=1, values=lambda x: isinstance(x, str)
            and x.isdigit(), description="Number of GPUs to be used")
    variant("enable_gpu_tests", when="@0.1.0:", default=False, 
            description="Build GPU tests as well")

    depends_on("cmake@3.16:")
    depends_on("hpx@:1.7.1", when="+hpx @0.1.0")
    depends_on("hpx@1.7.1:", when="+hpx @0.2.0:")

    # Tests need more dependencies...
    depends_on("boost +program_options", type=("test"))
    depends_on("kokkos@4.0.01 +cuda", type=("test"), when="+enable_gpu_tests")
    depends_on("hpx-kokkos@master +cuda", type=("test"), when="+enable_gpu_tests")
    depends_on("cuda", type=("test"), when="+enable_gpu_tests")

    conflicts("+enable_gpu_tests", when="~hpx")

    build_directory = "spack-build"

    def cmake_args(self):
        spec, args = self.spec, []
        args += [
                self.define_from_variant("CPPUDDLE_WITH_COUNTERS", "allocator_counters"),
                self.define("CPPUDDLE_WITH_TESTS", self.run_tests),
                self.define("CPPUDDLE_WITH_HPX_MUTEX", False),
                self.define_from_variant("CPPUDDLE_WITH_CUDA", "enable_gpu_tests"),
                self.define_from_variant("CPPUDDLE_WITH_KOKKOS", "enable_gpu_tests"),
                self.define_from_variant("CPPUDDLE_WITH_HPX", "hpx"),
                self.define_from_variant("CPPUDDLE_WITH_HPX_AWARE_ALLOCATORS", "hpx"),
                self.define_from_variant("CPPUDDLE_WITH_NUMBER_BUCKETS", "number_buffer_buckets"),
                self.define_from_variant("CPPUDDLE_WITH_MAX_NUMBER_GPUS", "max_number_gpus"),
                self.define_from_variant("CPPUDDLE_WITH_BUFFER_RECYCLING", "buffer_recycling"),
                self.define_from_variant("CPPUDDLE_WITH_AGGRESSIVE_CONTENT_RECYCLING",
                                         "buffer_content_recycling"),
                ]
                #self.define_from_variant("CPPUDDLE_WITH_HPX_MUTEX", "hpx"),
        if self.run_tests and spec.satisfies("~allocator_counters"):
            raise SpackError("Building and running the cppuddle tests requires +allocator_counters")
        if spec.satisfies("~buffer_recycling"):
            tty.warn("Building cppuddle with disabled buffer recycling. This "
                     "can lead to substantially degraded performance and should "
                     "only be done for certain benchmarks!")
        if spec.satisfies("~buffer_content_recycling"):
            tty.warn("Building cppuddle with disabled buffer content recycling. This "
                     "can lead to sligtly degraded performance!")
        if spec.satisfies("^hpx +rocm"):
            args += [self.define("CMAKE_CXX_COMPILER", self.spec["hip"].hipcc)]
        if spec.satisfies("^hpx +sycl"):
            args += [self.define("CMAKE_CXX_COMPILER",
                     "{0}/bin/clang++".format(spec["dpcpp"].prefix))]
        return args

    def check(self):
        if self.run_tests:
            with working_dir(self.build_directory):
                ctest("--output-on-failure ")
