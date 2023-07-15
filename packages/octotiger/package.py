# Copyright 2013-2023 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

# ----------------------------------------------------------------------------
# If you submit this package back to Spack as a pull request,
# please first remove this boilerplate and all FIXME comments.
#
# This is a template package file for Spack.  We've put "FIXME"
# next to all the things you'll want to change. Once you've handled
# them, you can save this file and test your package like this:
#
#     spack install octotiger
#
# You can edit this file again by typing:
#
#     spack edit octotiger
#
# See the Spack documentation for more information on packaging.
# ----------------------------------------------------------------------------

from spack.package import *


class Octotiger(CMakePackage):
    """FIXME: Put a proper description of your package here."""

    # FIXME: Add a proper url for your package's homepage here.
    homepage = "https://github.com/STEllAR-GROUP/octotiger"
    url = "https://github.com/STEllAR-GROUP/octotiger"
    git = "https://github.com/STEllAR-GROUP/octotiger"

    version("master", branch="master", submodules=True)

    variant('cuda', default=True,
            description='Build octotiger with CUDA (also allows Kokkos kernels to run with CUDA)')
    variant('kokkos', default=True,
            description='Build octotiger with kokkos based kernels')
    variant(
        'griddim', default='8', description='Octotiger grid size',
        values=('8'), multi=False
    )
    variant(
        'theta_minimum', default='0.34', description='Octotiger minimal allowed theta value',
        values=('0.34', '0.5', '0.16'), multi=False
    )


    depends_on('cppuddle +hpx_support')

    depends_on('hpx-kokkos@master +cuda',
               when='+kokkos +cuda',
               )
    depends_on('hpx-kokkos@master -cuda',
               when='+kokkos -cuda',
               )

    depends_on('cmake@3.16.0:', type='build')
    depends_on('vc@1.4.1')
    depends_on('boost@1.74.0: cxxstd=17')
    depends_on('hdf5 +threadsafe +szip +hl -mpi')
    #depends_on('hdf5 -mpi +threadsafe  +szip +hl', when='-mpi')
    depends_on('silo@4.11-bsd -mpi')
    #depends_on('silo@4.10.2 -mpi ', when='-mpi')

    depends_on('cuda', when='+cuda')

    hpx_string = 'hpx@1.8.0: cxxstd=17'
    depends_on(hpx_string + ' +cuda', when='+cuda') #networking=mpi ?
    depends_on(hpx_string + ' -cuda', when='-cuda')

    kokkos_string = 'kokkos +serial +hpx +hpx_async_dispatch +aggressive_vectorization '
    depends_on(kokkos_string + ' +cuda +cuda_lambda +wrapper ', when='+kokkos +cuda')
    depends_on(kokkos_string + ' -cuda -cuda_lambda -wrapper',when='+kokkos -cuda')

    #depends_on('kokkos-nvcc-wrapper', when='+kokkos')
    depends_on('spack.pkg.builtin.kokkos-nvcc-wrapper', when='+kokkos',
              patches=['adapt-kokkos-wrapper-for-nix.patch', 'adapt-kokkos-wrapper-for-hpx.patch',]
            )
    def cmake_args(self):
        spec = self.spec
        args = []

        # CUDA
        args.append(self.define_from_variant('OCTOTIGER_WITH_CUDA', 'cuda'))
        args.append(self.define_from_variant('OCTOTIGER_WITH_KOKKOS', 'kokkos'))

        # test
        args.append(self.define('OCTOTIGER_WITH_TESTS', self.run_tests))
        args.append(self.define('OCTOTIGER_KOKKOS_SIMD_EXTENSION', 'SCALAR'))
        args.append(self.define('OCTOTIGER_WITH_VC', 'ON'))
        args.append(self.define('OCTOTIGER_WITH_LEGACY_VC', 'OFF'))

        # griddim
        args.append(
            '-DOCTOTIGER_WITH_GRIDDIM={0}'.format(spec.variants['griddim'].value))

        # theta_minimum
        args.append(
            '-DOCTOTIGER_THETA_MINIMUM={0}'.format(spec.variants['theta_minimum'].value))

        # set nvcc_wrapper as compiler
        #if '+kokkos' in spec and '+cuda' in spec:
         #   args.append("-DCMAKE_CXX_COMPILER=%s" %
         #               self.spec["kokkos-nvcc-wrapper"].kokkos_cxx)

        return args


#    def check(self):
#        """Run ctest after building project."""
#        with working_dir(self.build_directory):
#            ctest("--output-on-failure")
