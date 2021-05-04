# Generate virtual doc files for the mkdocs site.
# You can also run this script directly to actually write out those files, as a preview.

import os.path
import sys

import mkdocs_gen_files

if not os.path.isdir("crystal"):
    mkdocs_gen_files.log.warning('Skipping API docs because "crystal" directory is missing.')
    sys.exit()

# Get the documentation root object
root = mkdocs_gen_files.config["plugins"]["mkdocstrings"].get_handler("crystal").collector.root

nav_data = {}


def add_to_nav(*items):
    *keys, item = items
    current_nav = nav_data
    for part in keys:
        current_nav = current_nav.setdefault(part, {})
    current_nav[""] = item


with mkdocs_gen_files.open("api/index.md", "w") as f:
    print(f"# Top-level namespace\n\n# ::: ::", file=f)
add_to_nav("API", "api/index.md")


def get_parts(typ):
    parts = typ.abs_id.split("::")
    assert parts[0] == "Crystal", parts
    return parts[1:]


nav_items = {}

# For each type (e.g. "Foo::Bar")
for typ in root.walk_types():
    if all("/src/crystal/" in loc.filename for loc in typ.locations):
        continue

    # Use the file name "api/Foo/Bar.md"
    filename = "api/" + typ.abs_id.replace("::", "/") + ".md"
    # Make a file with the content "::: Foo::Bar\n"
    with mkdocs_gen_files.open(filename, "w") as f:
        print(f"# ::: {typ.abs_id}", file=f)

    if not any(
        "/src/compiler/" in loc.filename and
        "/src/compiler/crystal/macros" not in loc.filename
        for loc in typ.locations
    ):
        add_to_nav("API", *typ.abs_id.split("::"), filename)
        continue

    parts = get_parts(typ)
    if parts:
        typ2 = root.lookup("Crystal").lookup(parts[0])
        while (sup := typ2.superclass) and sup.abs_id.startswith("Crystal"):
            parts = get_parts(sup) + parts
            typ2 = sup.lookup()

    nav_items[tuple(parts)] = filename

for parts, filename in sorted(nav_items.items()):
    add_to_nav("Compiler", *parts, filename)


def build_nav(data, indentation=""):
    for key, value in data.items():
        if key != "":
            if "" in value:
                yield f"{indentation}* [{key}]({value['']})\n"
            else:
                yield f"{indentation}* {key}\n"
            yield from build_nav(value, indentation + "    ")


with mkdocs_gen_files.open("SUMMARY.md", "a") as nav_file:
    nav_file.writelines(build_nav(nav_data))
