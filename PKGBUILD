# Maintainer: Karl Ludwig Brennan <karlludwigbrennan@outlook.com>
# Contributer: Sven-Hendrik Haase <svenstaro@gmail.com>
# Contributer: Konstantin Gizdov <arch@kge.pw>

pkgname=(cuda11.8 cuda11.8-tools)
pkgbase=cuda11.8
pkgver=11.8.0
_driverver=520.61.05
pkgrel=1
pkgdesc="NVIDIA's GPU programming toolkit (version 11.8)"
arch=('x86_64')
# Install side by side with any other CUDA, matching the cuda-11.1 convention.
# Using /opt/cuda would clobber (or be clobbered by) the distro cuda package.
_cudaroot=/opt/cuda-11.8
url="https://developer.nvidia.com/cuda-zone"
license=('custom:NVIDIA')
depends=('gcc10-libs' 'gcc10' 'opencl-nvidia' 'nvidia-utils' 'python')
options=(!strip staticlibs)
install=cuda.install
source=(https://developer.download.nvidia.com/compute/cuda/${pkgver}/local_installers/cuda_${pkgver}_${_driverver}_linux.run
        cuda.sh
        cuda.conf
        cuda-findgllib_mk.diff
        accinj64.pc
        cublas.pc
        cuda.pc
        cudart.pc
        cufft.pc
        cufftw.pc
        cuinj64.pc
        curand.pc
        cusolver.pc
        cusparse.pc
        nppc.pc
        nppial.pc
        nppicc.pc
        nppicom.pc
        nppidei.pc
        nppif.pc
        nppig.pc
        nppim.pc
        nppi.pc
        nppist.pc
        nppisu.pc
        nppitc.pc
        npps.pc
        nvgraph.pc
        nvidia-ml.pc
        nvjpeg.pc
        nvrtc.pc
        nvToolsExt.pc)
sha512sums=('e96e1389abed34b5093b3a1d4e6ae9f3d4f8406621b1475f378efae65868657efce22da03b5b4e0a548d9635e406b8690b18b17b186d03ecb3ca0703c5d5787a'
            '6a0cfe7d3918c20218f430e8c79ea4f358a870374e8e7d5c2c9a6a5c166be5b831337a990c6b3be940b7665464fb37d2f924b33bf26f9310271fcbc9920fbb93'
            '4ab376237e82dca084ca24c8d0b311f6da988a8df0abd281542393696392340dca92522141b1dfcaa1bfc9826c61162aff4ceb3618be1162ec88ffc15c5fb1bd'
            '41d6b6cad934f135eafde610d1cbd862033977fd4416a4b6abaa47709a70bab7fcf6f8377c21329084fb9db13f2a8c8c20e93c15292d7d4a6448d70a33b23f1b'
            '2ceec94cc34db69965dd15066eaf22eac119ddbddfdc15dd5e8e8485c21667e703f3e0f6bef54a4ec9eb0864b3fed74aabc7eca8be7d189a2f4f425d01cfb0bf'
            'ebf9635ccc940d801818a14a1410570b54e1528f9f73245d03e3d434c3c62ed3b018962d53764f9d45f3e71217eeb49964cb577693333e2898150ca70c644610'
            '0e0d932ff263fd497d0cc461f2c2d58821a52815f6d11d156b6070b0d637e060c48075041dd323978e66dde96cffebed88f87433770be1bfdc3866ced883261c'
            'a586f8d0eed73d90db44b5a08d6ae6c23e67ba54da29dbe9b822c80d5f2b87893f7cfb3100fa3fd80c797e46380812f790427cbde3c5055812bc077848f3cb05'
            '8b7873ce64f198d43f2ca4808ea4793dfe23cbedb3fbcb7bfd141e2a2fde011b15e3173f3380d1176fea27680522e0511058d3310a357db3d2a13d3a3f29a3fe'
            '8900f502b9e08d702462756e5f7bfc2ad1ae87935c6473bf1cb7ed6c749c976c2884177b227216526d74f7a598b12fb0036f9634cc409103aaa6707a1938a258'
            'e27682ba33c89c6b5791673b4b8d8df927267dbdee64bd9d3b7ec676a438c4c44c9842f667fdea2e749af291cabb12a602e1ea609cf28d0b9febce840aea23b6'
            '750073a24697a705cc4fa725f25407c072babe75c15dde7304360c67f426fba5d4d8015dc142a2f20b1b18045571f608879adaba9bcc34eb35376e9723f815e4'
            '68b983da20b892d99cb5abce69641591b5b584cb72a0b9e92b8699110d9573ee6593738160e92ae53e39d7db2299ba94d9980040560bf216d9e8788633e357ff'
            'c041f89a6a4dc966c29fc6ca22dfba4969d1da6d195275aa30f3b96fa15f3ed9a9351d0cff4911504c5ec6afd3522264b6468902ad08c87a2148b34a1c92dbbf'
            '4511d3c8f28932df7af5b898fdaa21983be487eecc3912637f96c27c0d3dadf2306f02b87abc337b81288e417bedcbdd2fb9a1e8dc37aa3fa93430e436b64179'
            '69e4ef1aac20e4f4bc987b48db6e56dcd65e7289f4a26fb612b7be4a68c9328c957bc1ab3ccaa2af3163defd1b757b79d5baebcbe6f26dc357a8c4871534738a'
            'e345cd392729ab3edb55f9f4695220137b2d26cf2c7d0fffa01b063bf1ab902999338d165d414ba666be7734617d1400a9ace8b477734cc57e115a446ba77624'
            'a3d6a946f4840f50a51c8bffb84ce48c4492776327cf03ee989508bbb60617b7fb3a272109130b2e741401a5880aff32723f35fc8f27d785cbcd5c54078c9ad8'
            'b3927ccf9f9e0f23b93c198babe669103c0d5a6c3921a5d043b9fef58faa8522cc4bd97b374c6e3bcd86fe14c89d84244b4df90fb37297ebc2271710b2463b47'
            '567635540dbec677909b6230635427ab8a65171286f65ed8bd487e400460adbde50132973227ef4b8f2193e4ebc2d6660c095d038f261e2d32af2cf0cd2f2af8'
            '3005d959ebd00891d0f7d3f668c3ced430635d170c140445fdcd15d81a15ab05a4b208f3dfac8362e07ca7efffc7253303eb3dcd8eaaec4fcc58445cc87761a8'
            'c811248f54036017a3a99e13263fecfb512b301b016a69599f05754a8b7fb01b0e6c0353699e30ca09ad5940e3f5d4f10c32bdf2130e1908f5d7565aeffa20e0'
            'f25495857d34c94e08812c0bb361da79ef72630ae8c367db56280a3f2845da755b05a23f033aed1833ee7417d132a9436175e8e1e37e75116663442add089a3d'
            '69a44c48e6360929b099888f0aacba4d7fb8f610d5fcb742a49fb5aae21c8945cdbcdff5ac57f376c8dd81550ff72417587644b43975198f64079376dfccb1df'
            'a4c301e7871170f18adaef1fe10d6a0f4e4e08428080cecd22de665bef1fc245bacfb9e76e90152d836466bd3db7d84b9fb7d34031e671024c96e604af15e4b8'
            '19d7f67bb63da636137e83e6401299ebb37146b6f7e41e58596dfbcd3ef0610b19c89a38a99b642db072382be547a0f95182df03fe2d4f2788479418192ce460'
            'c86d64a7c31980b7abb642c985c05f8c6343b0f1116c8ab50db72131b142d4421dba44fb5b088123a93ae82ad9b3c38c33c3d14d8b1474489effec3bac62684e'
            'c48c2c244340ad590eac6e189302ce037bbe12f3ae37ae76d05d72b4af43e900341051ae66d6c8244bb127246e2d40d2b64998031a931128e2e0e0ca31184e75'
            'd2ea315dde84562fa6ed417ce64a1d4e6422bac4bafe09595f9732fd80691fcca8d45ead0cd4fa5e9a7817308f8d4a4217a92e4c838e18d30fc66862901a7d6e'
            '3214bb3ee6e2b23fe82b3335e5cb904551e37bd78d5656b5a021394dcfd607132bb1559d79fd237c926d34f9a74a12d5260681e0ee59d9d72b4ee7b2103d72af'
            '6d6a5c784350c0fb63f7cadbc7c1a6c45ba8a3aa9bf41167ee343d8d9b7595184939f66c9e9b6b022711ebd5cc1105aeae23a97f4fc33316487fa6b368b22fbe'
            '02aa49ec130270ed733685d7a96f84fb1d711b0219a366848461269b3c462f0b6b6edf876b45b69519b98dee8b2b2a70e8f3a853eec20b60067633f23dec098e')

prepare() {
  sh cuda_${pkgver}_${_driverver}_linux.run --target "${srcdir}" --noexec

  # Fix up samples that use findgllib.mk.
  #
  # CUDA 11.8 no longer bundles the samples (they moved to a separate GitHub
  # repository), so the glob below usually matches nothing. Guard it with
  # nullglob: without that, the unmatched pattern is passed to patch verbatim
  # and patch tries to create a file literally named "*".
  shopt -s nullglob
  local _findgllib=(builds/cuda_samples/*/*/findgllib.mk)
  shopt -u nullglob

  if (( ${#_findgllib[@]} )); then
    for f in "${_findgllib[@]}"; do
      patch "$f" cuda-findgllib_mk.diff
    done
  fi
}

build() {
  local _prepdir="${srcdir}/prep"

  cd "${srcdir}/builds"

  rm -rf NVIDIA*.run bin
  mkdir -p "${_prepdir}${_cudaroot}/extras"

  # CUDA 11.8 no longer ships the samples in the installer, so only move the
  # directory when the installer actually provided one.
  if [[ -d cuda_samples ]]; then
    mv cuda_samples "${_prepdir}${_cudaroot}/samples"
  fi

  mv integration nsight_compute nsight_systems EULA.txt "${_prepdir}${_cudaroot}"
  mv cuda_sanitizer_api/compute-sanitizer "${_prepdir}${_cudaroot}/extras/compute-sanitizer"
  rmdir cuda_sanitizer_api
  for lib in *; do
    if [[ "$lib" =~ .*"version.json".* ]]; then
      continue
    fi
    cp -r $lib/* "${_prepdir}${_cudaroot}/"
  done

  # Delete some unnecessary files. Only the paths that exist are removed, since
  # the sample tree is absent in 11.8 and the uninstaller moved into
  # cuda_demo_suite.
  rm -rf "${_prepdir}${_cudaroot}"/bin/cuda-uninstaller \
         "${_prepdir}${_cudaroot}"/samples/bin/cuda-uninstaller \
         "${_prepdir}${_cudaroot}"/extras/demo_suite/cuda-uninstaller

  # Define compilers for CUDA to use.
  # This allows us to use older versions of GCC if we have to.
  ln -s /usr/bin/gcc-10 "${_prepdir}${_cudaroot}/bin/gcc"
  ln -s /usr/bin/g++-10 "${_prepdir}${_cudaroot}/bin/g++"

  # Install profile and ld.so.config files
  install -Dm755 "${srcdir}/cuda.sh" "${_prepdir}/etc/profile.d/cuda.sh"
  install -Dm644 "${srcdir}/cuda.conf" "${_prepdir}/etc/ld.so.conf.d/cuda.conf"

  # Install pkgconfig files
  mkdir -p "$_prepdir"/usr/lib/pkgconfig
  cp "${srcdir}"/*.pc "${_prepdir}"/usr/lib/pkgconfig

  mkdir -p "${_prepdir}/usr/share/licenses/${pkgname}"
  ln -s "${_cudaroot}/EULA.txt" "${_prepdir}/usr/share/licenses/${pkgname}/EULA.txt"
  ln -s "${_cudaroot}/README" "${_prepdir}/usr/share/licenses/${pkgname}/README"

  # Allow newer compilers to work. This is not officially supported in the Arch package but
  # if users want to try, let them try.
  # See https://docs.nvidia.com/cuda/cuda-installation-guide-linux/index.html#system-requirements
  # for official requirements
  sed -i "/.*unsupported GNU version.*/d" "${_prepdir}${_cudaroot}"/targets/x86_64-linux/include/crt/host_config.h
  sed -i "/.*unsupported clang version.*/d" "${_prepdir}${_cudaroot}"/targets/x86_64-linux/include/crt/host_config.h

  # Fix Makefile paths to CUDA
  for f in $(find "${_prepdir}${_cudaroot}" -name Makefile); do
    sed -i "s|/usr/local/cuda|${_cudaroot}|g" "$f"
  done
}

package_cuda11.8() {
#  replaces=('cuda-toolkit' 'cuda-sdk' 'cuda-static')
  # This toolkit installs to /opt/cuda-11.8 so it can coexist with the distro
  # `cuda` package and any other CUDA version. It therefore must NOT claim
  # provides=('cuda') nor conflict with it: doing both would make pacman refuse
  # to install a package that is explicitly designed to sit alongside it.
  # No conflicts: an empty array would emit a malformed "conflicts = " line.
  provides=('cuda11.8-toolkit')
  optdepends=('gdb: for cuda-gdb'
              'glu: required for some profiling tools in CUPTI')

  local _prepdir="${srcdir}/prep"

  cd "${_prepdir}"
  cp -al * "${pkgdir}"

  # The tools (nvvp, nsight, samples) belong to cuda11.8-tools. Some of these
  # paths do not exist in CUDA 11.8, so only remove what is present.
  rm -rf "${pkgdir}${_cudaroot}"/bin/nvvp \
         "${pkgdir}${_cudaroot}"/bin/computeprof \
         "${pkgdir}${_cudaroot}"/libnvvp \
         "${pkgdir}${_cudaroot}"/nsight* \
         "${pkgdir}${_cudaroot}"/samples
}

package_cuda11.8-tools() {
  pkgdesc="NVIDIA's GPU programming toolkit (extra tools: nvvp, nsight, samples) (version 11.8)"
  # Same reasoning as cuda11.8: these live under the versioned prefix and do
  # not replace the distro cuda-tools package.
  provides=('cuda11.8-tools')
  depends=('cuda11.8' 'java-runtime=8' 'nss')
  optdepends=('glu: required for some CUDA samples'
              'freeglut: required for some CUDA samples'
              'perl: required by some NVVP plugins')

  local _prepdir="${srcdir}/prep"

  mkdir -p "${pkgdir}${_cudaroot}/bin"
  mv "${_prepdir}${_cudaroot}"/nsight* "${pkgdir}${_cudaroot}"
  mv "${_prepdir}${_cudaroot}"/bin/nvvp "${pkgdir}${_cudaroot}/bin/nvvp"
  mv "${_prepdir}${_cudaroot}"/bin/computeprof "${pkgdir}${_cudaroot}/bin/computeprof"
  mv "${_prepdir}${_cudaroot}"/libnvvp "${pkgdir}${_cudaroot}"

  # CUDA 11.8 does not bundle the samples, so only split them out when the
  # installer provided them.
  if [[ -d "${_prepdir}${_cudaroot}/samples" ]]; then
    mv "${_prepdir}${_cudaroot}"/samples "${pkgdir}${_cudaroot}"
  fi

  # licenses
  mkdir -p "${pkgdir}/usr/share/licenses"
  ln -s /usr/share/licenses/cuda "${pkgdir}/usr/share/licenses/${pkgname}"
}

# vim:set ts=2 sw=2 et:
