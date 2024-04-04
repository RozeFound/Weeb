frontenddir = join_paths(PKGDATA_DIR, 'weeb/frontend')

configure_file(
  input: 'weeb.in',
  output: 'weeb',
  configuration: conf,
  install: true,
  install_dir: get_option('bindir'),
  install_mode: 'r-xr-xr-x'
)

subdir('views')

weeb_sources = [
  '__init__.py',
  'main.py',
]

install_data(weeb_sources, install_dir: frontenddir)
