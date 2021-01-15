# Generate virtual doc files for the mkdocs site.
# You can also run this script directly to actually write out those files, as a preview.

import sys
import os.path
import mkdocs_gen_files

if not os.path.isdir('crystal'):
    mkdocs_gen_files.log.warning('Skipping API docs because "crystal" directory is missing.')
    sys.exit()

# Get the documentation root object
root = mkdocs_gen_files.config['plugins']['mkdocstrings'].get_handler('crystal').collector.root

# Start a navigation file (to be filled as we go along)
nav = mkdocs_gen_files.open('api/SUMMARY.md', 'a')

with mkdocs_gen_files.open('api/index.md', 'w') as f:
    print(f'::: ::', file=f)
print('* [Top Level Namespace](index.md)', file=nav)


# For each type (e.g. "Foo::Bar")
for typ in root.walk_types():
    # Use the file name "api/Foo/Bar.md"
    filename = typ.abs_id.replace('::', '/') + '.md'
    # Make a file with the content "::: Foo::Bar\n"
    with mkdocs_gen_files.open('api/' + filename, 'w') as f:
        print(f'::: {typ.abs_id}', file=f)

    # Append to the nav: "    * [Bar](api/Foo/Bar.md)"
    indent = '    ' * typ.abs_id.count('::')
    print(indent + f'* [{typ.name}]({filename})', file=nav)
