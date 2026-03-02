# We need -lm for all C code (assuming it uses math functions, which is safe to
# assume for NumPy). For C++ it isn't needed, because libstdc++/libc++ is
# guaranteed to depend on it.
m_dep = cc.find_library('m', required : false)
mlib_linkflag = ''
if m_dep.found()
  mlib_linkflag = '-lm'
  add_project_link_arguments(mlib_linkflag, language : 'c')
endif

# Platform detection
is_windows = host_machine.system() == 'windows'
is_mingw = is_windows and cc.get_define('__MINGW32__') != ''

if is_mingw
  is_mingw_built_python = run_command(
    py, ['-c', 'import sysconfig; print(sysconfig.get_platform())'],
    check: true).stdout().strip().startswith('mingw')
  if not is_mingw_built_python
    # For mingw-w64, link statically against the UCRT.
    gcc_link_args = ['-lucrt', '-static']
    add_project_link_arguments(gcc_link_args, language: ['c', 'cpp'])
    # Force gcc to float64 long doubles for compatibility with MSVC
    # builds, for C only.
    add_project_arguments('-mlong-double-64', language: 'c')
  endif
  # Make fprintf("%zd") work (see https://github.com/rgommers/scipy/issues/118)
  add_project_arguments('-D__USE_MINGW_ANSI_STDIO=1', language: ['c', 'cpp'])
endif

# We install libnpymath and libnpyrandom; ensure they're using a `.lib` rather
# than a `.a` file extension in order not to break including them in a
# distutils-based build (see gh-23981 and
# https://mesonbuild.com/FAQ.html#why-does-building-my-project-with-msvc-output-static-libraries-called-libfooa)
if is_windows and cc.get_id() in ['msvc', 'clang-cl']
  name_prefix_staticlib = ''
  name_suffix_staticlib = 'lib'
else
  name_prefix_staticlib = []
  name_suffix_staticlib = []
endif

# Enable UNIX large file support on 32-bit systems (64 bit off_t,
# lseek -> lseek64, etc.)
cflags_large_file_support = []
if host_machine.system() == 'aix'
  cflags_large_file_support += '-D_LARGE_FILES'
else
  cflags_large_file_support += [
    '-D_FILE_OFFSET_BITS=64',
    '-D_LARGEFILE_SOURCE=1',
    '-D_LARGEFILE64_SOURCE=1',
  ]
endif

# Determine whether it is necessary to link libatomic with gcc. This
# could be the case on 32-bit platforms when atomic operations are used
# on 64-bit types or on RISC-V using 8-bit atomics, so we explicitly
# check for both 64 bit and 8 bit operations.  The check is adapted from
# SciPy, who copied it from Mesa.
null_dep = dependency('', required : false)
atomic_dep = null_dep
code_non_lockfree = '''
  #include <stdint.h>
  #include <stddef.h>
  int main() {
   struct {
     void *p;
     uint8_t u8v;
   } x;
   x.p = NULL;
   x.u8v = 0;
   uint8_t res = __atomic_load_n(&x.u8v, __ATOMIC_SEQ_CST);
   __atomic_store_n(&x.u8v, 1, __ATOMIC_SEQ_CST);
   void *p = __atomic_load_n((void **)x.p, __ATOMIC_SEQ_CST);
   __atomic_store_n((void **)x.p, NULL, __ATOMIC_SEQ_CST);
   return 0;
   }
'''
if cc.get_id() != 'msvc'
  if not cc.links(
      code_non_lockfree,
      name : 'Check atomic builtins without -latomic'
    )
    atomic_dep = cc.find_library('atomic', required: false)
    if atomic_dep.found()
      # We're not sure that with `-latomic` things will work for all compilers,
      # so verify and only keep libatomic as a dependency if this works. It is
      # possible the build will fail later otherwise - unclear under what
      # circumstances (compilers, runtimes, etc.) exactly and this may need to
      # be extended when support is added for new CPUs
      if not cc.links(
          code_non_lockfree,
          dependencies: atomic_dep,
          name : 'Check atomic builtins with -latomic'
        )
        atomic_dep = null_dep
      endif
    endif
  endif
endif

# Copy the main __init__.py|pxd files to the build dir (needed for Cython)
__init__py = fs.copyfile('__init__.py')
_cython_tree = [__init__py]

python_sources = [
  '__init__.py',
  'asmtobin.py',
  'bintoasm.py',
  'instruction_set.py',
]

py.install_sources(
  python_sources,
  subdir: 'rvemu'
)

pure_subdirs = []
if py.version().version_compare('<3.12')
  pure_subdirs += 'distutils'
endif

np_dir = py.get_install_dir() / 'rvemu'

# Generate version.py for sdist
meson.add_dist_script(
   ['_build_utils/gitversion.py', '--meson-dist', '--write',
     'rvemu/version.py']
)
if not fs.exists('version.py')
  generate_version = custom_target(
    'generate-version',
    install: true,
    build_always_stale: true,
    build_by_default: true,
    output: 'version.py',
    input: '_build_utils/gitversion.py',
    command: [py, '@INPUT@', '--write', '@OUTPUT@'],
    install_dir: np_dir,
    install_tag: 'python-runtime'
  )
else
  # When building from sdist, version.py exists and should be included
  py.install_sources(
    ['version.py'],
    subdir : 'rvemu'
  )
endif

foreach subdir: pure_subdirs
  install_subdir(subdir, install_dir: np_dir, install_tag: 'python-runtime', exclude_directories: ['tests'])
  if fs.is_dir(subdir/'tests')
    install_subdir(subdir/'tests', install_dir: np_dir/subdir, install_tag: 'tests')
  endif
endforeach

install_subdir('tests', install_dir: np_dir, install_tag: 'tests')

compilers = {
  'C': cc,
  'CPP': cpp,
  'CYTHON': cy,
}

machines = {
  'HOST': host_machine,
  'BUILD': build_machine,
}

conf_data = configuration_data()

# Set compiler information
foreach name, compiler : compilers
  conf_data.set(name + '_COMP', compiler.get_id())
  conf_data.set(name + '_COMP_LINKER_ID', compiler.get_linker_id())
  conf_data.set(name + '_COMP_VERSION', compiler.version())
  conf_data.set(name + '_COMP_CMD_ARRAY', ', '.join(compiler.cmd_array()))
  conf_data.set(name + '_COMP_ARGS', ', '.join(
      get_option(name.to_lower() + '_args')
    )
  )
  conf_data.set(name + '_COMP_LINK_ARGS', ', '.join(
      get_option(name.to_lower() + '_link_args')
    )
  )
endforeach

# Machines CPU and system information
foreach name, machine : machines
  conf_data.set(name + '_CPU', machine.cpu())
  conf_data.set(name + '_CPU_FAMILY', machine.cpu_family())
  conf_data.set(name + '_CPU_ENDIAN', machine.endian())
  conf_data.set(name + '_CPU_SYSTEM', machine.system())
endforeach

conf_data.set('CROSS_COMPILED', meson.is_cross_build())

# Python information
conf_data.set('PYTHON_PATH', py.full_path())
conf_data.set('PYTHON_VERSION', py.language_version())

subdir('compiler')
