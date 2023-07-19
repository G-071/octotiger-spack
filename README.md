
Repo installation:
```sh
# spack install
git clone --depth=100 --branch=releases/v0.20 https://github.com/spack/spack.git /path/to/spack
cd /path/to/spack
. share/spack/setup-env.sh
# spack repo install
git clone https://github.com/G-071/octotiger-spack.git /path/to/octotiger-spack
spack repo add /path/to/octotiger-spack
# use system packages
spack compiler find # search currently loaded compilers
spack external find cuda # replace cuda by desired packages or leave blank to get everything
# Check package availability and its variants:
spack info octotiger
```

Basic Octo-Tiger installtion:
```sh
# Basic octotiger installation
spack install --fresh --test=root octotiger~cuda~kokkos
# octotiger install with specific compiler/cuda versions and run octotiger tests
spack install --fresh --test=root octotiger+cuda+kokkos%gcc@11^cuda@11.8.89^cmake@3.26.4^kokkos@3.7.00 cuda_arch=75
# Use one of the installs
spack load octotiger~cuda~kokkos
octotiger --help
```

Octo-Tiger cuda dev build (rtx 2060):
```sh
# Get fresh src dir
git clone https://github.com/STEllAR-GROUP/octotiger
cd octotiger
# Setup development shell with all dependencies (drops user into the build process right after cmake)
spack dev-build --fresh --drop-in bash --until cmake --test=root octotiger+cuda+kokkos cuda_arch=75 @master%gcc@11^cuda@11.8.89
cd spack_build_id #exact dir name ist printed by the last command
# Use with usual edit-make-test cycle after editing the src directory...
make -j16
ctest
./octotiger --help
```

Octo-Tiger hip dev build (MI100):
```sh
module load rocm/5.4.6
spack compiler find # should find rocmcc@5.4.6
spack external find hip llvm-amdgpu hsa-rocr-dev # other erquired 5.4.6 packges from the rocm module
spack dev-build --drop-in bash --until cmake --test=root octotiger+rocm+kokkos amdgpu_target=gfx908@master%rocmcc@5.4.6 ^asio@1.16.0^hpx max_cpu_count=128 amdgpu_target=gfx908 ^hip@5.4.6 ^llvm-amdgpu@5.4.6^kokkos amdg
pu_target=gfx908 ^hpx-kokkos amdgpu_target=gfx908
cd spack_build_id #exact dir name ist printed by the last command
# Use with usual edit-make-test cycle after editing the src directory...
make -j16
ctest
