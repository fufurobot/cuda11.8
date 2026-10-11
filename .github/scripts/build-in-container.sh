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
    makepkg --noconfirm --force
    echo "== produced =="
    ls -la "$PKGDEST"
  '
