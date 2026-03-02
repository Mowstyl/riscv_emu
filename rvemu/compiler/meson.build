largefile_define = []
if host_machine.system() == 'aix' or host_machine.system() == 'AIX'
  largefile_define += '-D_LARGE_FILES'
endif

if not fs.exists('RISC-V-Parser/README.md')
  error('Missing the `RISC-V-Parser` git submodule! Run `git submodule update --init` to fix this.')
endif

py.extension_module('_rvparser_handler',
  ['_rvparser_handler.c'],
  c_args: largefile_define,
  install: true,
  subdir: 'rvemu/compiler',
)

py.install_sources(
  [
    '__init__.py',
    '_rvparser.py',
  ],
  subdir: 'rvemu/compiler'
)

#py.install_sources(
#  [
#    'tests/__init__.py',
#    'tests/test_rvparser.py',
#  ],
#  subdir: 'rvemu/compiler/tests',
#  install_tag: 'tests'
#)
