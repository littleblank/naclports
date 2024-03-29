# Copyright (c) 2014 The Native Client Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

NACLPORTS_CPPFLAGS+=" -I ${START_DIR}"

ConfigureStep() {
  MakeDir ${BUILD_DIR}
  cp -rf ${START_DIR}/* ${BUILD_DIR}
}

BuildStep() {
  MAKE_TARGETS="libcli_main.a libnacl_spawn.a"
  if [ "${NACL_LIBC}" = "glibc" -o "${NACL_LIBC}" = "bionic" ]; then
    NACLPORTS_CFLAGS+=" -fPIC"
    NACLPORTS_CXXFLAGS+=" -fPIC"
    MAKE_TARGETS+=" libnacl_spawn.so"
  fi

  if [ "${NACL_LIBC}" = "glibc" ]; then
    MAKE_TARGETS+=" test"
  else
    NACLPORTS_CPPFLAGS+=" -I${NACLPORTS_INCLUDE}/glibc-compat"
  fi

  MAKEFLAGS+=" TOOLCHAIN=${TOOLCHAIN}"
  MAKEFLAGS+=" NACL_ARCH=${NACL_ARCH_ALT}"
  export CFLAGS="${NACLPORTS_CPPFLAGS} ${NACLPORTS_CFLAGS}"
  export CXXFLAGS="${NACLPORTS_CPPFLAGS} ${NACLPORTS_CXXFLAGS}"
  DefaultBuildStep
}

InstallStep() {
  MakeDir ${DESTDIR_LIB}
  LogExecute cp libnacl_spawn.a ${DESTDIR_LIB}
  if [ "${NACL_LIBC}" = "glibc" -o "${NACL_LIBC}" = "bionic" ]; then
    LogExecute cp libnacl_spawn.so ${DESTDIR_LIB}
  fi
  LogExecute cp libcli_main.a ${DESTDIR_LIB}
  MakeDir ${DESTDIR_INCLUDE}
  LogExecute cp -f ${START_DIR}/spawn.h ${DESTDIR_INCLUDE}/
  LogExecute cp -f ${START_DIR}/nacl_main.h ${DESTDIR_INCLUDE}/
  if [ $TOOLCHAIN = bionic ]; then
    LogExecute cp -f ${START_DIR}/bsd_spawn.h ${DESTDIR_INCLUDE}/
  fi
}
