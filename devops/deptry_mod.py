from __future__ import annotations

import shutil
from deptry.cli import cli


def deptry() -> None:
    default_pkg_to_module_map = {'pillow' : 'PIL',
                                 'beautifulsoup4' : 'bs4',
                                 'progressbar2' : 'progressbar',
                                 'PyYAML' : 'yaml'}
    package_module_name_map = {}
    for pkg in default_pkg_to_module_map:
        module = default_pkg_to_module_map[pkg]
        package_module_name_map[pkg] = (module,)

    column_size, _line_size = shutil.get_terminal_size()
    cli(max_content_width=column_size)