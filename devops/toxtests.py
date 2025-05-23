import io
import os
import shutil
import subprocess
import sys

import coverage
from tox import run
import devops.discovery

# -------------------------------------------------------------

def main():
    os.environ['REPO_DIRPATH'] = CWD
    os.environ['TOX_WORKDIR'] = TOX_WORKDIR
    os.environ['DISCOVERY_FPATH'] = os.path.join(os.path.dirname(__file__), DISCOVERY_FNAME)
    mode = 'pkg' if is_package(dirpath=CWD) else 'req'
    script_dirpath = os.path.dirname(__file__)
    tox_fpath = os.path.join(script_dirpath, 'tox.ini')

    args = ('-c', tox_fpath , '-e', mode)
    if len(sys.argv) > 1:
        args = (*args,sys.argv[1])

    build_dirpath = os.path.join(CWD, 'build')
    if os.path.isdir(build_dirpath):
        print(f'- Deleting build directory {build_dirpath}')
        shutil.rmtree(build_dirpath)

    print(f'-------------------------- Launching tox tests --------------------------')
    run.run(args)


def cov():
    cov_fpath = os.path.join(get_tox_workdir(), '.coverage')

    covfefe = coverage.Coverage(data_file=cov_fpath)
    covfefe.load()
    output_buffer = io.StringIO()

    covfefe.report(file=output_buffer)
    report_content = output_buffer.getvalue()
    output_buffer.close()

    print(report_content)

def toxlibs():
    env = 'pkg' if 'pkg' in os.listdir(TOX_WORKDIR) else 'req'
    venv_python_fpath = os.path.join(TOX_WORKDIR, env, 'bin', 'python')
    process = subprocess.Popen([venv_python_fpath, '-m', 'pip', 'list'], text=True)
    stdout, stderr = process.communicate()
    print(stdout, stderr)


def get_tox_workdir() -> str:
    home_dirpath = os.path.expanduser('~')
    env_name = os.path.basename(os.getcwd())
    return os.path.join(home_dirpath, '.tox', env_name)

def is_package(dirpath : str):
    fnames = os.listdir(dirpath)
    has_setup = 'setup.py' in fnames
    has_pyproject = 'pyproject.toml' in fnames
    return has_setup or has_pyproject


TOX_WORKDIR = get_tox_workdir()
CWD = os.getcwd()
DISCOVERY_FNAME = os.path.basename(devops.discovery.__file__)