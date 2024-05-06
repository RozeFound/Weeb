blueprints = custom_target('blueprints',
  input: files(
    'window.blp',
    'help_overlay.blp',
    'preferences.blp',
    'board.blp',
    'tile.blp',
    'tags.blp',
    'tag.blp'
  ),
  output: '.',
  command: [find_program('blueprint-compiler'), 'batch-compile', '@OUTPUT@', '@CURRENT_SOURCE_DIR@', '@INPUT@']
)