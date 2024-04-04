backenddir = join_paths(PKGDATA_DIR, 'weeb/backend')

config_file = configure_file(
  input: 'constants.in',
  output: 'constants.py',
  configuration: configuration_data({
    'APP_ID': APPLICATION_ID,
    'APP_VERSION': meson.project_version()
  }),
  install: true,
  install_dir: backenddir
)

weeb_sources = [
    '__init__.py',
]

install_data(weeb_sources, install_dir: backenddir)