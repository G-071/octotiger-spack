# Copyright 2013-2023 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack.package import *


class Octotiger(CMakePackage, CudaPackage, ROCmPackage):
    """Octo-Tiger is an astrophysics program simulating the evolution of star
    systems based on the fast multipole method on adaptive Octrees. It was
    implemented using high-level C++ libraries, specifically HPX and Vc, which
    allows its use on different hardware platforms."""

    homepage = "https://github.com/STEllAR-GROUP/octotiger"
    url = "https://github.com/STEllAR-GROUP/octotiger"
    git = "https://github.com/STEllAR-GROUP/octotiger"

    maintainers("G-071")

    version("master", branch="master", submodules=True)

    variant('cuda', default=True,
            description='Build octotiger with CUDA (also allows Kokkos kernels to run with CUDA)')
    variant('kokkos', default=True,
            description='Build octotiger with kokkos based kernels')
    variant('griddim', default='8', description='Octotiger grid size',
            values=('8'), multi=False)
    variant('theta_minimum', default='0.34', description='Octotiger minimal allowed theta value',
            values=('0.34', '0.5', '0.16'), multi=False)
    variant('kokkos_hpx_kernels', default=False,
            description='Use HPX execution space for CPU Kokkos kernels (instead of the Serial space)')
    variant('monopole_host_tasks', default='1',
            description='Tasks per monopole kernel invocation when using the Kokkos HPX execution space',
            values=('1', '4', '16'), multi=False)
    variant('multipole_host_tasks', default='1',
            description='Tasks per multipole kernel invocation when using the Kokkos HPX execution space',
            values=('1', '4', '16', '64'), multi=False)
    variant('hydro_host_tasks', default='1',
            description='Tasks per hydro kernel invocation when using the Kokkos HPX execution space',
            multi=False)
    variant('simd_library', default='KOKKOS',
            description='Use either kokkos (for kokkos simd types) or std (for std::experimental::simd types)',
            values=('KOKKOS', 'STD'), multi=False)
    variant('simd_extension', default='DISCOVER',
            description='Enforce specific SIMD extension or autoselect (discover) appropriate one',
            values=('DISCOVER', 'SCALAR', 'AVX', 'AVX512', 'NEON', 'SVE'), multi=False)

    depends_on('cppuddle +hpx_support')

    depends_on('hpx-kokkos@master +cuda',
               when='+kokkos +cuda', patches=['version.patch'])
    depends_on('hpx-kokkos@master -cuda',
               when='+kokkos -cuda', patches=['version.patch'])

    depends_on('cmake@3.16.0:', type='build')
    depends_on('vc@1.4.1')
    depends_on('boost@1.74.0: cxxstd=17')
    depends_on('hdf5 +threadsafe +szip +hl -mpi')
    # depends_on('hdf5 -mpi +threadsafe  +szip +hl', when='-mpi')
    depends_on('silo@4.11-bsd -mpi')
    # depends_on('silo@4.10.2 -mpi ', when='-mpi')

    depends_on('cuda', when='+cuda')

    hpx_string = 'hpx@1.8.0: cxxstd=17'
    depends_on(hpx_string + ' +cuda +async_cuda ',
               when='+cuda')  # networking=mpi ?
    depends_on(hpx_string + ' -cuda', when='-cuda')

    kokkos_string = 'kokkos +serial +aggressive_vectorization '
    for sm_ in CudaPackage.cuda_arch_values:
        depends_on(kokkos_string + ' +cuda +cuda_lambda +wrapper cuda_arch={0}'.format(
            sm_), when='+kokkos +cuda cuda_arch={0} %gcc'.format(sm_))
        depends_on(kokkos_string + ' +cuda +cuda_lambda -wrapper cuda_arch={0}'.format(
            sm_), when='+kokkos +cuda cuda_arch={0} %clang'.format(sm_))
    depends_on("kokkos@4.1.00: +hpx +hpx_async_dispatch ",
               when="+kokkos_hpx_kernels")
    depends_on(kokkos_string + ' -cuda -cuda_lambda -wrapper',
               when='+kokkos -cuda')
    depends_on('spack.pkg.builtin.kokkos-nvcc-wrapper', when='+kokkos',
               patches=['adapt-kokkos-wrapper-for-nix.patch', 'adapt-kokkos-wrapper-for-hpx.patch'])

    conflicts("+cuda", when="cuda_arch=none")
    conflicts("+kokkos_hpx_kernels", when="~kokkos")
    conflicts("simd_library=STD", when="%gcc@:10")
    conflicts("simd_library=STD", when="%clang")

    # depends_on(kokkos_string + ' +cuda +cuda_lambda +wrapper ', when='+kokkos
    # +cuda', patches=['adapt-kokkos-wrapper-for-nix.patch',
    # 'adapt-kokkos-wrapper-for-hpx.patch'])
    # depends_on(kokkos_string + ' -cuda -cuda_lambda -wrapper',when='+kokkos
    # -cuda', patches=['adapt-kokkos-wrapper-for-nix.patch',
    # 'adapt-kokkos-wrapper-for-hpx.patch'] )
    # for gfx in ROCmPackage.amdgpu_targets:
    #    depends_on(kokkos_string + ' +cuda +cuda_lambda +wrapper
    #    amdgpu_target={0}'.format(gfx), when='+kokkos +cuda
    #    amdgpu_target={0}'.format(gfx))

    def cmake_args(self):
        spec = self.spec
        args = []

        args.append(self.define('CMAKE_EXPORT_COMPILE_COMMANDSA', 'ON'))

        # CUDA
        args.append(self.define_from_variant('OCTOTIGER_WITH_CUDA', 'cuda'))
        args.append(self.define_from_variant(
            'OCTOTIGER_WITH_KOKKOS', 'kokkos'))
        if '+cuda' in spec:
            cuda_arch_list = spec.variants['cuda_arch'].value
            cuda_arch = cuda_arch_list[0]
            if cuda_arch != 'none':
                args.append('-DOCTOTIGER_CUDA_ARCH=sm_{0}'.format(cuda_arch))

        args.append(self.define_from_variant(
            'OCTOTIGER_KOKKOS_SIMD_LIBRARY', 'simd_library'))
        args.append(self.define_from_variant(
            'OCTOTIGER_KOKKOS_SIMD_EXTENSION', 'simd_extension'))
        args.append(self.define_from_variant(
            'OCTOTIGER_WITH_MONOPOLE_HOST_HPX_EXECUTOR', 'kokkos_hpx_kernels'))
        args.append(self.define_from_variant(
            'OCTOTIGER_WITH_MULTIPOLE_HOST_HPX_EXECUTOR', 'kokkos_hpx_kernels'))
        args.append(self.define_from_variant(
            'OCTOTIGER_WITH_HYDRO_HOST_HPX_EXECUTOR', 'kokkos_hpx_kernels'))
        args.append(self.define_from_variant(
            'OCTOTIGER_WITH_KOKKOS_MULTIPOLE_TASKS', 'multipole_host_tasks'))
        args.append(self.define_from_variant(
            'OCTOTIGER_WITH_KOKKOS_MONOPOLE_TASKS', 'monopole_host_tasks'))
        args.append(self.define_from_variant(
            'OCTOTIGER_WITH_KOKKOS_HYDRO_TASKS', 'hydro_host_tasks'))

        if "~kokkos_hpx_kernels" in spec or "-kokkos_hpx_kernels" in spec:
            if spec.variants["multipole_host_tasks"].value > 1:
                raise SpackError(
                    "multipole_host_tasks > 1 requires +kokkos_hpx_kernels")
            if spec.variants["monopole_host_tasks"].value > 1:
                raise SpackError(
                    "monopole_host_tasks > 1 requires +kokkos_hpx_kernels")
            if spec.variants["hydro_host_tasks"].value > 1:
                raise SpackError(
                    "hydro_host_tasks > 1 requires +kokkos_hpx_kernels")

        # test
        args.append(self.define('OCTOTIGER_WITH_TESTS', self.run_tests))
        args.append(self.define('OCTOTIGER_WITH_VC', 'ON'))
        args.append(self.define('OCTOTIGER_WITH_LEGACY_VC', 'OFF'))

        if spec.satisfies("%clang"):
            args.append(self.define('OCTOTIGER_WITH_BLAST_TEST', 'OFF'))
        else:
            args.append(self.define('OCTOTIGER_WITH_BLAST_TEST', 'ON'))
        args.append(self.define('OCTOTIGER_WITH_UNBUFFERED_STDOUT', 'OFF'))
        args.append(self.define('OCTOTIGER_WITH_MAX_NUMBER_FIELDS', '15'))

        # griddim
        args.append(
            '-DOCTOTIGER_WITH_GRIDDIM={0}'.format(spec.variants['griddim'].value))

        # theta_minimum
        args.append(
            '-DOCTOTIGER_THETA_MINIMUM={0}'.format(spec.variants['theta_minimum'].value))

        return args
