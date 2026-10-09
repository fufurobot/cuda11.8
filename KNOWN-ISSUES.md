# CUDA 11.8 on modern Arch: known constraints

Two environment-level constraints were confirmed while building and testing this
package. Neither is a defect in the PKGBUILD; both are worth knowing before you
try to compile against this toolkit.

## 1. glibc >= 2.42 breaks the CUDA 11.8 headers

Symptom, when compiling any `.cu` file:

```
/usr/include/bits/mathcalls.h(83): error: exception specification is
incompatible with that of previous function "cospi"
.../opt/cuda/include/crt/math_functions.h(5551): here
```

Six functions are affected: `cospi`, `sinpi`, `rsqrt` and their `float`
variants (`cospif`, `sinpif`, `rsqrtf`).

Cause: recent glibc declares these C23 math functions with `__THROW`
(equivalently `noexcept`), while the CUDA 11.8 headers declare them without an
exception specification. The two declarations conflict, and nvcc cannot
reconcile them.

The declarations in `glibc` are gated on
`__GLIBC_USE (IEC_60559_FUNCS_EXT_C23)`, which `bits/libc-header-start.h`
computes as:

```c
#if __GLIBC_USE (IEC_60559_FUNCS_EXT) || __GLIBC_USE (ISOC23)
# define __GLIBC_USE_IEC_60559_FUNCS_EXT_C23 1
```

Because that block starts with `#undef`, passing
`-D__GLIBC_USE_IEC_60559_FUNCS_EXT_C23=0` has no effect. The macro is switched
on through `__USE_GNU` (equivalently `_GNU_SOURCE`).

### Workaround

Drop `_GNU_SOURCE` for CUDA compilation:

```sh
nvcc -U_GNU_SOURCE -ccbin g++-10 -arch=sm_75 ... hello.cu
```

Verified: with `-U_GNU_SOURCE` the sample compiles, links and emits real
`sm_75` cubins. Note that this disables GNU extensions for the translation
unit, which can break code that relies on e.g. `strdup` or `asprintf` without
declaring `_GNU_SOURCE` itself.

## 2. Host compiler must be GCC 10

The package depends on `gcc10` and symlinks `/opt/cuda/bin/gcc` ->
`/usr/bin/gcc-10`. Modern GCC (16.x) is far outside the range CUDA 11.8
supports. Pass the host compiler explicitly:

```sh
nvcc -ccbin /usr/bin/g++-10 ...
```

## Verified build

`makepkg` produces `cuda11.8-11.8.0-1-x86_64.pkg.tar.zst` containing
`nvcc` 11.8.89, which compiles a `sm_75` kernel successfully.
