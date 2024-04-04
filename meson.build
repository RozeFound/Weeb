project('weeb',
          version: '0.1.0',
    meson_version: '>= 0.62.0',
  default_options: [ 'warning_level=2', 'werror=false', ],
)

APPLICATION_ID = 'com.github.RozeFound.Weeb'

PKGDATA_DIR = join_paths(get_option('prefix'), get_option('datadir'), meson.project_name())

i18n = import('i18n')
python = import('python')

conf = configuration_data()
conf.set('PYTHON', python.find_installation('python3').full_path())
conf.set('VERSION', meson.project_version())
conf.set('localedir', get_option('prefix') / get_option('localedir'))
conf.set('pkgdatadir', PKGDATA_DIR)

subdir('weeb')
subdir('data')
subdir('po')

gnome.post_install(
     glib_compile_schemas: true,
    gtk_update_icon_cache: true,
  update_desktop_database: true,
)
