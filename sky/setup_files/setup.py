import atexit
import io
import os
import platform
import re
import subprocess
import sys
from typing import Dict, List

import setuptools

ROOT_DIR = os.path.dirname(__file__)
INIT_FILE_PATH = os.path.join(ROOT_DIR, 'sky', '__init__.py')
_COMMIT_FAILURE_MESSAGE = (
    'WARNING: SkyPilot fail to {verb} the commit hash in '
    f'{INIT_FILE_PATH!r} (SkyPilot can still be normally used): '
    '{error}')

original_init_content = None

system = platform.system()


def find_version():
    # Extract version information from filepath
    # Adapted from:
    #  https://github.com/ray-project/ray/blob/master/python/setup.py
    with open(INIT_FILE_PATH, 'r', encoding='utf-8') as fp:
        version_match = re.search(r'^__version__ = [\'"]([^\'"]*)[\'"]',
                                  fp.read(), re.M)
        if version_match:
            return version_match.group(1)
        raise RuntimeError('Unable to find version string.')


def get_commit_hash():
    with open(INIT_FILE_PATH, 'r', encoding='utf-8') as fp:
        commit_match = re.search(r'^_SKYPILOT_COMMIT_SHA = [\'"]([^\'"]*)[\'"]',
                                 fp.read(), re.M)
        if commit_match:
            commit_hash = commit_match.group(1)
        else:
            raise RuntimeError('Unable to find commit string.')

    if 'SKYPILOT_COMMIT_SHA' not in commit_hash:
        return commit_hash
    try:
        # Getting the commit hash from git, and check if there are any
        # uncommitted changes.
        # TODO: keep this in sync with sky/__init__.py
        cwd = os.path.dirname(__file__)
        commit_hash = subprocess.check_output(
            ['git', 'rev-parse', 'HEAD'],
            cwd=cwd,
            universal_newlines=True,
            stderr=subprocess.DEVNULL).strip()
        changes = subprocess.check_output(['git', 'status', '--porcelain'],
                                          cwd=cwd,
                                          universal_newlines=True,
                                          stderr=subprocess.DEVNULL).strip()
        if changes:
            commit_hash += '-dirty'
        return commit_hash
    except Exception as e:  # pylint: disable=broad-except
        print(_COMMIT_FAILURE_MESSAGE.format(verb='get', error=str(e)),
              file=sys.stderr)
        return commit_hash


def replace_commit_hash():
    """Fill in the commit hash in the __init__.py file."""
    try:
        with open(INIT_FILE_PATH, 'r', encoding='utf-8') as fp:
            content = fp.read()
            global original_init_content
            original_init_content = content
            content = re.sub(r'^_SKYPILOT_COMMIT_SHA = [\'"]([^\'"]*)[\'"]',
                             f'_SKYPILOT_COMMIT_SHA = \'{get_commit_hash()}\'',
                             content,
                             flags=re.M)
        with open(INIT_FILE_PATH, 'w', encoding='utf-8') as fp:
            fp.write(content)
    except Exception as e:  # pylint: disable=broad-except
        # Avoid breaking the installation when there is no permission to write
        # the file.
        print(_COMMIT_FAILURE_MESSAGE.format(verb='replace', error=str(e)),
              file=sys.stderr)
        pass


def revert_commit_hash():
    try:
        if original_init_content is not None:
            with open(INIT_FILE_PATH, 'w', encoding='utf-8') as fp:
                fp.write(original_init_content)
    except Exception as e:  # pylint: disable=broad-except
        # Avoid breaking the installation when there is no permission to write
        # the file.
        print(_COMMIT_FAILURE_MESSAGE.format(verb='replace', error=str(e)),
              file=sys.stderr)


def parse_readme(readme: str) -> str:
    """Parse the README.md file to be pypi compatible."""
    # Replace the footnotes.
    readme = readme.replace('<!-- Footnote -->', '#')
    footnote_re = re.compile(r'\[\^([0-9]+)\]')
    readme = footnote_re.sub(r'<sup>[\1]</sup>', readme)

    # Remove the dark mode switcher
    mode_re = re.compile(
        r'<picture>[\n ]*<source media=.*>[\n ]*<img(.*)>[\n ]*</picture>',
        re.MULTILINE)
    readme = mode_re.sub(r'<img\1>', readme)
    return readme


# NOTE: Change the templates/jobs-controller.yaml.j2 file if any of the
# following packages dependencies are changed.
aws_dependencies = [
    # botocore does not work with urllib3>=2.0.0, according to https://github.com/boto/botocore/issues/2926
    # We have to explicitly pin the version to optimize the time for
    # poetry install. See https://github.com/orgs/python-poetry/discussions/7937
    'urllib3<2',
    # NOTE: this installs CLI V1. To use AWS SSO (e.g., `aws sso login`), users
    # should instead use CLI V2 which is not pip-installable. See
    # https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html.
    'awscli>=1.27.10',
    'botocore>=1.29.10',
    'boto3>=1.26.1',
    # NOTE: required by awscli. To avoid ray automatically installing
    # the latest version.
    'colorama < 0.4.5',
]


install_requires = [
    'wheel',
    'cachetools',
    # NOTE: ray requires click>=7.0.
    'click >= 7.0',
    'colorama',
    'cryptography',
    # Jinja has a bug in older versions because of the lack of pinning
    # the version of the underlying markupsafe package. See:
    # https://github.com/pallets/jinja/issues/1585
    'jinja2 >= 3.0',
    'jsonschema',
    'networkx',
    'pandas>=1.3.0',
    'pendulum',
    # PrettyTable with version >=2.0.0 is required for the support of
    # `add_rows` method.
    'PrettyTable >= 2.0.0',
    'python-dotenv',
    'rich',
    'tabulate',
    # Light weight requirement, can be replaced with "typing" once
    # we deprecate Python 3.7 (this will take a while).
    "typing_extensions",
    'filelock >= 3.6.0',
    'packaging',
    'psutil',
    'pulp',
    # Cython 3.0 release breaks PyYAML 5.4.* (https://github.com/yaml/pyyaml/issues/601)
    # <= 3.13 may encounter https://github.com/ultralytics/yolov5/issues/414
    'pyyaml > 3.13, != 5.4.*',
    'requests',
]+ aws_dependencies

local_ray = [
    # Lower version of ray will cause dependency conflict for
    # click/grpcio/protobuf.
    # Excluded 2.6.0 as it has a bug in the cluster launcher:
    # https://github.com/ray-project/ray/releases/tag/ray-2.6.1
    'ray[default] >= 2.2.0, != 2.6.0',
]

remote = [
    # Adopted from ray's setup.py: https://github.com/ray-project/ray/blob/ray-2.4.0/python/setup.py
    # SkyPilot: != 1.48.0 is required to avoid the error where ray dashboard fails to start when
    # ray start is called (#2054).
    # Tracking issue: https://github.com/ray-project/ray/issues/30984
    "grpcio >= 1.32.0, <= 1.49.1, != 1.48.0; python_version < '3.10' and sys_platform == 'darwin'",  # noqa:E501
    "grpcio >= 1.42.0, <= 1.49.1, != 1.48.0; python_version >= '3.10' and sys_platform == 'darwin'",  # noqa:E501
    # Original issue: https://github.com/ray-project/ray/issues/33833
    "grpcio >= 1.32.0, <= 1.51.3, != 1.48.0; python_version < '3.10' and sys_platform != 'darwin'",  # noqa:E501
    "grpcio >= 1.42.0, <= 1.51.3, != 1.48.0; python_version >= '3.10' and sys_platform != 'darwin'",  # noqa:E501
    # Adopted from ray's setup.py:
    # https://github.com/ray-project/ray/blob/ray-2.9.3/python/setup.py#L343
    'protobuf >= 3.15.3, != 3.19.5',
    # Some pydantic versions are not compatible with ray. Adopted from ray's
    # setup.py: https://github.com/ray-project/ray/blob/ray-2.9.3/python/setup.py#L254
    'pydantic!=2.0.*,!=2.1.*,!=2.2.*,!=2.3.*,!=2.4.*,<3',
]


extras_require: Dict[str, List[str]] = {
    'docker': ['docker'] + local_ray,
    'lambda': local_ray,
    'cloudflare': aws_dependencies,
    'scp': local_ray,
    'oci': ['oci'] + local_ray,
    'kubernetes': ['kubernetes>=20.0.0'],
    'remote': remote,
    'runpod': ['runpod>=1.5.1'],
    'fluidstack': [],  # No dependencies needed for fluidstack
    'cudo': ['cudo-compute>=0.1.10'],
    'paperspace': [],  # No dependencies needed for paperspace
    'vsphere': [
        'pyvmomi==8.0.1.0.2',
        # vsphere-automation-sdk is also required, but it does not have
        # pypi release, which cause failure of our pypi release.
        # https://peps.python.org/pep-0440/#direct-references
        # We have the instruction for its installation in our
        # docs instead.
        # 'vsphere-automation-sdk @ git+https://github.com/vmware/vsphere-automation-sdk-python.git@v8.0.1.0'
    ],
}

extras_require['all'] = sum(extras_require.values(), [])

long_description = ''
readme_filepath = 'README.md'
# When sky/backends/wheel_utils.py builds wheels, it will not contain the
# README.  Skip the description for that case.
if os.path.exists(readme_filepath):
    long_description = io.open(readme_filepath, 'r', encoding='utf-8').read()
    long_description = parse_readme(long_description)

atexit.register(revert_commit_hash)
replace_commit_hash()

setuptools.setup(
    # NOTE: this affects the package.whl wheel name. When changing this (if
    # ever), you must grep for '.whl' and change all corresponding wheel paths
    # (templates/*.j2 and wheel_utils.py).
    name='gss',
    version=find_version(),
    packages=setuptools.find_packages(),
    author='gss team',
    license='Apache 2.0',
    readme='README.md',
    description='SkyPilot: An intercloud broker for the clouds',
    long_description=long_description,
    long_description_content_type='text/markdown',
    setup_requires=['wheel'],
    requires_python='>=3.7',
    install_requires=install_requires,
    extras_require=extras_require,
    entry_points={
        'console_scripts': ['sky = sky.cli:cli'],
    },
    include_package_data=True,
    classifiers=[
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Distributed Computing',
    ],
)
