#!/usr/bin/env python
# Copyright (c) 2013 The Native Client Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""Script to patch a configure script in-place such that the libtool
dynamic library detection works for NaCl.

Once this patch makes it into upstream libtool it should eventually
be possible to remove this completely.
"""
import optparse
import os
import re
import sys

# Shell fragment for detecting shared library support in the compiler.
detect_so_support = \
    'libc_so=`$CC -print-file-name=libc.so` && [ "$libc_so" != libc.so ]'

# There are essentailly three patches here, which will make configure do
# the right things for shared library support when used with the NaCl
# GLIBC toolchain.
CONFIGURE_PATCHS = [
# Correct result for "dynamic linker characteristics"
['(\n\*\)\n  dynamic_linker=no)',
'''
nacl)
  # Patched by naclports using patch_configure.py
  if %s; then
    dynamic_linker="GNU/NaCl ld.so"
    version_type=linux
    library_names_spec='${libname}${release}${shared_ext}$versuffix ${libname}${release}${shared_ext}${major} ${libname}${shared_ext}'
    soname_spec='${libname}${release}${shared_ext}$major'
  else
    dynamic_linker=no
  fi
  ;;
\\1''' % detect_so_support],
# Correct result for "supports shared libraries"
['''(
  netbsd\*\)
    if echo __ELF__ \| \$CC -E - \| grep __ELF__ >/dev/null; then
      archive_cmds_CXX='\$LD -Bshareable  -o \$lib \$predep_objects \$libobjs \$deplibs \$postdep_objects \$linker_flags')
''',
'''
  # Patched by naclports using patch_configure.py
  nacl)
    if %s; then
      ld_shlibs_CXX=yes
    else
      ld_shlibs_CXX=no
    fi
    ;;

\\1
''' % detect_so_support],
# Correct result for "how to recognize dependent libraries"
['''
(.*linux.*)\)
  lt_cv_deplibs_check_method=pass_all''',
'''
# Patched by naclports using patch_configure.py
\\1 | nacl*)
  lt_cv_deplibs_check_method=pass_all''']
]

def main(args):
  usage = 'usage: %prog [options] <configure_script>'
  parser = optparse.OptionParser(usage=usage, description=__doc__)
  args = parser.parse_args(args)[1]
  if not args:
    parser.error('no configure script specified')
  configure = args[0]

  if not os.path.exists(configure):
    sys.stderr.write('configure script not found: %s\n' % configure)
    sys.exit(1)

  # Read configure
  with open(configure) as input_file:
    filedata = input_file.read()

  if 'Patched by naclports' in filedata:
    sys.stderr.write('Configure script already patched\n')
    return 0

  # Check for patch location
  for i, (pattern, replacement) in enumerate(CONFIGURE_PATCHS):
    if not re.search(pattern, filedata):
      sys.stderr.write('Failed to find patch %s location in configure '
                       'script: %s\n' % (i, configure))
      continue

    # Apply patch
    filedata = re.sub(pattern, replacement, filedata)

  # Overwrite input file with patched file data
  with open(configure, 'w') as output_file:
    output_file.write(filedata)

  return 0

if __name__ == '__main__':
  sys.exit(main(sys.argv[1:]))
