#!/bin/bash
# Builds cuda11.8 inside an Arch Linux container.
#
# This lives in its own file rather than inline in the workflow because the
# script needs nested quoting (docker run ... bash -c '... sudo ... bash -c
# "..."'). Nested single quotes terminate the outer block, so an inline version
# silently passes a truncated script to the container and fails with
# "cd: /work: No such file or directory".
set -euo pipefail

echo "== refreshing the keyring =="
pacman-key --init >/dev/null 2>&1 || true
pacman-key --populate archlinux >/dev/null 2>&1 || true
pacman -Sy --noconfirm --needed --noprogressbar archlinux-keyring >/dev/null
pacman -S --noconfirm --needed --noprogressbar base-devel sudo git >/dev/null

# makepkg refuses to run as root; the image runs as root.
useradd -m -s /bin/bash builder
echo "builder ALL=(ALL) NOPASSWD: ALL" > /etc/sudoers.d/builder
chmod 0440 /etc/sudoers.d/builder
chown -R builder:builder /work

# sudo resets the environment, so MAKEPKG_DIR must be passed explicitly rather
# than inherited; with 'set -u' an inherited-but-absent variable aborts.
exec sudo -u builder -H \
  MAKEPKG_DIR="$MAKEPKG_DIR" \
  bash -euo pipefail -c '
    cd /work
    export BUILDDIR="$MAKEPKG_DIR/build"
    export SRCDEST="$MAKEPKG_DIR/src"
    export PKGDEST="$MAKEPKG_DIR/pkg"
    echo "== makepkg =="
    # --nodeps: gcc10 and gcc10-libs are AUR-only packages (they provide the
    # GCC 10 host compiler CUDA 11.8 requires). Compiling GCC from source in CI
    # would add roughly an hour to every release, and the dependency is a
    # runtime requirement that pacman resolves for the end user anyway. The
    # nvcc smoke test below proves the packaged toolkit actually works.
    makepkg --noconfirm --force --nodeps
    echo "== produced =="
    ls -la "$PKGDEST"
  '

# Compile a real kernel with the freshly built nvcc. This replaces the
# dependency check that --nodeps skipped, proving the packaged toolkit works
# rather than merely unpacking.
#
# CUDA 11.8 needs an old host compiler: verified locally that GCC 10 compiles
# cleanly while GCC 16 fails with "user-defined literal operator not found" and
# "__malloc__ does not take arguments". gcc10 is AUR-only, so it is built here
# and cached between runs (~40 min once, seconds thereafter).
echo "== preparing an old host compiler for the smoke test =="
if ls /work/.makepkg/gcc10/*.pkg.tar.zst >/dev/null 2>&1; then
  echo "using cached gcc10 packages"
else
  echo "building gcc10 from the AUR (cached after this run)"
  mkdir -p /work/.makepkg/gcc10
  chown builder:builder /work/.makepkg/gcc10
  builddir=$(mktemp -d)
  chown builder:builder "$builddir"
  sudo -u builder -H bash -euo pipefail -c "
    cd $builddir
    curl -fsSL 'https://aur.archlinux.org/cgit/aur.git/snapshot/gcc10.tar.gz' -o gcc10.tar.gz
    tar xzf gcc10.tar.gz
    cd gcc10
    # Not optional: the PKGBUILD verifies PGP signatures on the GCC release
    # tarball with validpgpkeys, and a fresh container has none of them, so
    # makepkg aborts with "One or more PGP signatures could not be verified!".
    gpg --keyserver hkps://keyserver.ubuntu.com --recv-keys \
      F3691687D867B81B51CE07D9BBE43771487328A9 \
      86CFFCA918CF3AF47147588051E8B148A9999C34 \
      13975A70E63C361C73AE69EF6EEB81F8981C74C7
    makepkg --noconfirm --nodeps
  "
  # Cache the packages themselves rather than an unpacked copy, so the cached
  # artifact stays installable. The g++-10 binary is then unpacked where the
  # smoke test can use it; the package is not part of the release.
  cp "$builddir"/gcc10/*.pkg.tar.zst /work/.makepkg/gcc10/
fi

echo "== smoke-testing the packaged nvcc =="
cudaroot=$(grep -m1 '^_cudaroot=' /work/PKGBUILD | cut -d= -f2)
# Unpack the cached packages into an isolated prefix; only g++-10 is needed.
hostdir=/work/.makepkg/gcc10-unpacked
rm -rf "$hostdir" && mkdir -p "$hostdir"
for pkg in /work/.makepkg/gcc10/*.pkg.tar.zst; do
  bsdtar -xf "$pkg" -C "$hostdir" usr/bin usr/lib usr/lib64 usr/include 2>/dev/null || true
done
hostcc="$hostdir/usr/bin/g++-10"
test -x "$hostcc" || { echo "ERROR: no usable g++-10 for the smoke test"; exit 1; }
workdir=$(mktemp -d)
cd "$workdir"
printf '%s\n' '__global__ void k(int *o){ *o = 118; }' \
  'int main(){ int *d; cudaMalloc(&d,sizeof(int)); k<<<1,1>>>(d);' \
  'int h=0; cudaMemcpy(&h,d,sizeof(int),cudaMemcpyDeviceToHost);' \
  'cudaFree(d); return h==118?0:1; }' > smoke.cu
"${cudaroot}/bin/nvcc" -ccbin "$hostcc" -arch=sm_75 -U_GNU_SOURCE \
  -I"${cudaroot}/include" -L"${cudaroot}/lib64" -o smoke smoke.cu
"${cudaroot}/bin/cuobjdump" --list-elf smoke | head -3
echo "nvcc smoke test passed"

