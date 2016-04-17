import os
from setuptools import setup
from setuptools.command.install import install
from setuptools.command.develop import develop

from jupyter_core.paths import jupyter_config_dir
from IPython.html.nbextensions import install_nbextension
from IPython.html.services.config import ConfigManager

HERE = os.path.abspath(os.path.dirname(__file__))
EXT_DIR = os.path.join(HERE, 'nbshared', 'static')
SERVER_EXT_CONFIG = "c.NotebookApp.server_extensions.append('nbshared.handlers')"

class InstallCommand(install):
    def run(self):
        # Install Python package, possibly containing a kernel extension
        install.run(self)
        _install_server_extension()
        _install_js()


class DevelopCommand(develop):
    def run(self):
        develop.run(self)
        _install_server_extension()
        _install_js()


def _install_server_extension():
    # Install Notebook server extension
    fn = os.path.join(jupyter_config_dir(), 'jupyter_notebook_config.py')
    with open(fn, 'r+') as fh:
        lines = fh.read()
        if SERVER_EXT_CONFIG not in lines:
            fh.seek(0, 2)
            fh.write('\n')
            fh.write(SERVER_EXT_CONFIG)


def _install_js():
    install_nbextension(EXT_DIR, destination='nbshared',
                        overwrite=True, user=True, verbose=2)
    cm = ConfigManager()
    print('Enabling extension for notebook')
    cm.update("notebook", {"load_extensions":
                           {"nbshared/submit-shared-button": True}})
    cm.update("tree", {"load_extensions": {"nbshared/main": True}})

setup(
    name='nbshared',
    version='0.1',
    packages=['nbshared'],
    include_package_data=True
)
