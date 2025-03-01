import os
import shutil
import subprocess
import sys
from tox import run
from coverage import Coverage
import coverage
import io


# -------------------------------------------------------------

def main():
    cwd = os.getcwd()
    os.environ['REPO_DIRPATH'] = cwd
    os.environ['TOX_ENVNAME'] = get_tox_envname()
    mode = 'pkg' if is_package(dirpath=cwd) else 'req'
    script_dirpath = os.path.dirname(__file__)
    tox_fpath = os.path.join(script_dirpath, 'tox.ini')

    args = ('-c', tox_fpath , '-e', mode)
    if len(sys.argv) > 1:
        args = (*args,sys.argv[1])

    build_dirpath = os.path.join(cwd, 'build')
    if os.path.isdir(build_dirpath):
        print(f'- Deleting build directory {build_dirpath}')
        shutil.rmtree(build_dirpath)

    print(f'-------------------------- Launching tox tests --------------------------')
    run.run(args)


def cov():
    home_dirpath = os.path.expanduser('~')
    env_dirpath = os.path.join(home_dirpath, '.tox', get_tox_envname())
    cov_fpath = os.path.join(env_dirpath, '.coverage')

    covfefe = coverage.Coverage(data_file=cov_fpath)
    covfefe.load()
    output_buffer = io.StringIO()

    covfefe.report(file=output_buffer)
    report_content = output_buffer.getvalue()
    output_buffer.close()

    print(report_content)

def get_tox_envname() -> str:
    cwd = os.getcwd()
    return os.path.basename(cwd)

def is_package(dirpath : str):
    fnames = os.listdir(dirpath)
    has_setup = 'setup.py' in fnames
    has_pyproject = 'pyproject.toml' in fnames
    return has_setup or has_pyproject
