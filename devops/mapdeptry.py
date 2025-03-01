from __future__ import annotations

import shutil
from pathlib import Path
from typing import TYPE_CHECKING

import click
from deptry.cli import configure_logger, COMMA_SEPARATED_TUPLE, COMMA_SEPARATED_MAPPING, DEFAULT_EXCLUDE, \
    display_deptry_version, DEFAULT_REQUIREMENTS_FILES
from deptry.config import read_configuration_from_pyproject_toml
from deptry.core import Core

if TYPE_CHECKING:
    from collections.abc import Mapping, MutableMapping


@click.command()
@click.argument("root", type=click.Path(exists=True, path_type=Path), nargs=-1, required=True)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help=(
        "Boolean flag for verbosity. Using this flag will display more information about files, imports and"
        " dependencies while running."
    ),
    expose_value=False,
    is_eager=True,
    callback=configure_logger,
)
@click.option(
    "--config",
    type=click.Path(path_type=Path),
    is_eager=True,
    callback=read_configuration_from_pyproject_toml,
    help="Path to the pyproject.toml file to read configuration from.",
    default="pyproject.toml",
)
@click.option(
    "--no-ansi",
    is_flag=True,
    help="Disable ANSI characters in terminal output.",
)
@click.option(
    "--ignore",
    "-i",
    type=COMMA_SEPARATED_TUPLE,
    help="""A comma-separated list of error codes to ignore. e.g. `deptry --ignore DEP001,DEP002`
    For more information regarding the error codes, see https://deptry.com/issue-codes/""",
    default=(),
)
@click.option(
    "--per-rule-ignores",
    "-pri",
    type=COMMA_SEPARATED_MAPPING,
    help="""A comma-separated mapping of packages or modules to be ignored per error code.
    . e.g. ``deptry . --per-rule-ignores DEP001=matplotlib,DEP002=pandas|numpy``
    For more information regarding the error codes, see https://deptry.com/issue-codes/""",
    default={},
)
@click.option(
    "--exclude",
    "-e",
    multiple=True,
    type=str,
    help=f"""A regular expression for directories or files in which .py files should not be scanned for imports to determine if there are dependency issues.
    Can be used multiple times by specifying the argument multiple times. re.match() is used to match the expressions, which by default checks for a match only at the beginning of a string.
    For example: `deptry . -e ".*/foo/" -e bar"` Note that this overwrites the defaults.
    [default: {", ".join(DEFAULT_EXCLUDE)}]""",
)
@click.option(
    "--extend-exclude",
    "-ee",
    type=str,
    multiple=True,
    help="""Like --exclude, but adds additional files and directories on top of the excluded ones instead of overwriting the defaults.
    (Useful if you simply want to add to the default) `deptry . -ee ".*/foo/" -ee bar"`""",
    default=(),
    show_default=True,
)
@click.option(
    "--ignore-notebooks",
    "-nb",
    is_flag=True,
    help="Boolean flag to specify if notebooks should be ignored while scanning for imports.",
)
@click.option(
    "--version",
    is_flag=True,
    is_eager=True,
    expose_value=False,
    callback=display_deptry_version,
    help="Display the current version and exit.",
)
@click.option(
    "--requirements-files",
    "-rf",
    type=COMMA_SEPARATED_TUPLE,
    help=f""".txt files to scan for dependencies. If a file called pyproject.toml with a [tool.poetry.dependencies] or [project] section is found, this argument is ignored
    and the dependencies are extracted from the pyproject.toml file instead. Can be multiple e.g. `deptry . --requirements-files req/prod.txt,req/extra.txt`
    [default: {", ".join(DEFAULT_REQUIREMENTS_FILES)}]""",
)
@click.option(
    "--requirements-files-dev",
    "-rfd",
    type=COMMA_SEPARATED_TUPLE,
    help=""".txt files to scan for additional development dependencies. If a file called pyproject.toml with a [tool.poetry.dependencies] or [project] section is found, this argument is ignored
    and the dependencies are extracted from the pyproject.toml file instead. Can be multiple e.g. `deptry . --requirements-files-dev req/dev.txt,req/test.txt`""",
    default=("dev-requirements.txt", "requirements-dev.txt"),
    show_default=True,
)
@click.option(
    "--known-first-party",
    "-kf",
    type=str,
    multiple=True,
    help="Modules to consider as first party ones.",
    default=(),
    show_default=True,
)
@click.option(
    "--json-output",
    "-o",
    type=str,
    help="""If specified, a summary of the dependency issues found will be written to the output location specified. e.g. `deptry . -o deptry.json`""",
    show_default=True,
)
@click.option(
    "--package-module-name-map",
    "-pmnm",
    type=COMMA_SEPARATED_MAPPING,
    help="""Manually defined module names belonging to packages. For example; `deptry . --package-module-name-map package_1=module_a,package_2=module_b|module_c`.""",
    default={},
    show_default=False,
)
@click.option(
    "--pep621-dev-dependency-groups",
    "-ddg",
    type=COMMA_SEPARATED_TUPLE,
    help="""For projects that use PEP621 and that do not use a build tool that has its own method of declaring development dependencies,
    this argument provides the option to specify which groups under [project.optional-dependencies] in pyproject.toml
    should be considered development dependencies. For example, use `--pep621-dev-dependency-groups tests,docs` to mark the dependencies in
    the groups 'tests' and 'docs' as development dependencies.""",
    default=(),
    show_default=False,
)
@click.option(
    "--experimental-namespace-package",
    is_flag=True,
    help="Enable experimental support for namespace package (PEP 420) when detecting local modules (https://peps.python.org/pep-0420/).",
)
def cli(
    root: tuple[Path, ...],
    config: Path,
    no_ansi: bool,
    ignore: tuple[str, ...],
    per_rule_ignores: Mapping[str, tuple[str, ...]],
    exclude: tuple[str, ...],
    extend_exclude: tuple[str, ...],
    ignore_notebooks: bool,
    requirements_files: tuple[str, ...],
    requirements_files_dev: tuple[str, ...],
    known_first_party: tuple[str, ...],
    json_output: str,
    package_module_name_map: MutableMapping[str, tuple[str, ...]],
    pep621_dev_dependency_groups: tuple[str, ...],
    experimental_namespace_package: bool,
) -> None:
    """Find dependency issues in your Python project.

    ROOT is the path to the root directory of the project to be scanned. For instance, to invoke deptry in the current
    directory:

        deptry .

    If your project has multiple source directories, multiple ROOT can be specified.  For instance, to invoke deptry in
    both 'src' and 'worker' directories:

        deptry src worker

    """

    default_pkg_to_module_map = {'pillow' : 'PIL',
                                 'beautifulsoup4' : 'bs4',
                                 'progressbar2' : 'progressbar',
                                 'PyYAML' : 'yaml'}
    for pkg in default_pkg_to_module_map:
        module = default_pkg_to_module_map[pkg]
        package_module_name_map[pkg] = (module,)


    Core(
        root=root,
        config=config,
        no_ansi=no_ansi,
        exclude=exclude or DEFAULT_EXCLUDE,
        extend_exclude=extend_exclude,
        using_default_exclude=not exclude,
        ignore_notebooks=ignore_notebooks,
        ignore=ignore,
        per_rule_ignores=per_rule_ignores,
        requirements_files=requirements_files or DEFAULT_REQUIREMENTS_FILES,
        using_default_requirements_files=not requirements_files,
        requirements_files_dev=requirements_files_dev,
        known_first_party=known_first_party,
        json_output=json_output,
        package_module_name_map=package_module_name_map,
        pep621_dev_dependency_groups=pep621_dev_dependency_groups,
        experimental_namespace_package=experimental_namespace_package,
    ).run()



def deptry() -> None:
    column_size, _line_size = shutil.get_terminal_size()
    cli(max_content_width=column_size)