# Copyright 2013-2023 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack.package import *


class Cppuddle(CMakePackage):
    """Utility library to handle small, reusable pools of both device memory buffers (via allocators)
    and device executors (with multiple scheduling policies and optional work aggregation)."""

    homepage = "https://github.com/SC-SGS/CPPuddle"
    url = "https://github.com/SC-SGS/CPPuddle"
    git = "https://github.com/SC-SGS/CPPuddle"

    maintainers("G-071")

    version("master", branch="master")

    variant("counters", default=False, description="Activate allocation counters")
    variant("hpx_support", default=False, description="Build with HPX support")
    #variant("mutex_type", default="std", values=("std", "hpx"), description="Internal mutex type")
    variant("max_worker_count", default=128, values=lambda x: isinstance(x, str) and x.isdigit(),  description="Maximum number of supported workers")
    variant("gpu_count", default=1, values=lambda x: isinstance(x, str) and x.isdigit(), description="Number of GPUs to be used")
    variant("disable_recycling", default=False, description="Disable buffer recycling altogether")
    variant("disable_aggressive_allocators", default=False, description="Disable aggressive content reusage")


    depends_on("cmake@3.16:")
    depends_on("hpx", when="+hpx_support")
    depends_on("boost +program_options", type=("test"))

    build_directory = "spack-build"


    def cmake_args(self):
        spec, args = self.spec, []
        args += [
                self.define("CPPUDDLE_WITH_COUNTERS", self.run_tests),
                self.define("CPPUDDLE_WITH_TESTS", self.run_tests),
                self.define_from_variant("CPPUDDLE_WITH_HPX", "hpx_support"),
                self.define_from_variant("CPPUDDLE_WITH_HPX_AWARE_ALLOCATORS", "hpx_support"),
                self.define_from_variant("CPPUDDLE_WITH_HPX_MUTEX", "hpx_support"),
                self.define_from_variant("CPPUDDLE_WITH_MAX_NUMBER_WORKERS", "max_worker_count"),
                self.define_from_variant("CPPUDDLE_WITH_NUMBER_GPUS", "gpu_count"),
                self.define_from_variant("CPPUDDLE_DEACTIVATE_BUFFER_RECYCLING", "disable_recycling"),
                self.define_from_variant("CPPUDDLE_DEACTIVATE_AGGRESSIVE_ALLOCATORS", "disable_aggressive_allocators"),
                ]
        return args

    def check(self):
        if self.run_tests:
            with working_dir(self.build_directory):
                ctest("--output-on-failure -j4 ")


