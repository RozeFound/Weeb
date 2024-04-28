backenddir = join_paths(PKGDATA_DIR, 'weeb/backend')

config_file = configure_file(
  input: 'constants.py',
  output: 'constants.py',
  configuration: configuration_data({
    'APP_ID': APPLICATION_ID,
    'APP_VERSION': meson.project_version(),
    'BUILD_ENV': 'debug',
  }),
  install: true,
  install_dir: backenddir
)

subdir('utils')
subdir('providers')

weeb_sources = [
    '__init__.py',
    'primitives.py',
    'providers_manager.py',
    'downloader.py',
    'settings.py',
]

install_data(weeb_sources, install_dir: backenddir)