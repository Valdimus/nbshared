"""Tornado handlers for nbshared web service."""

import os
import shutil
import sys
import subprocess as sp
import json
import glob

from copy import copy;
from urllib.parse import quote, unquote

from tornado import web

import nbformat
from notebook.utils import url_path_join as ujoin
from notebook.base.handlers import IPythonHandler
from notebook.nbextensions import install_nbextension
from traitlets import Unicode, Dict
from traitlets.config import LoggingConfigurable

static = os.path.join(os.path.dirname(__file__), 'static')

from nbshared.m_utils import *;
from nbshared.localStorage import LocalStorage;
from nbshared.hdfsStorage import HdfsStorage;

class SharedManager(LoggingConfigurable):
    """
    Shared storage manager
    """
    storage_options = Dict({}, config=True, help="Storage options");
    storage_class = Unicode("nbshared.HdfsStorage", config=True, help="Class to use for storage");

    def __init__(self, **kwargs):
        LoggingConfigurable.__init__(self, **kwargs);

        opts = copy(self.storage_options);
        opts.update({
            "log": self.log
        });

        self.log.debug("Create instance of '%s' with options '%s'" % (self.storage_class, json.dumps(self.storage_options)))
        # Create the storage object
        self.__storage = create_instance(self.storage_class, opts);

    @property
    def storage(self):
        """
        Return the storage object
        """
        return self.__storage;

class BaseSharedHandler(IPythonHandler):
    """
    Base handler for sharing Notebook
    """

    @property
    def manager(self):
        """
        Return the shared manager
        """
        return self.settings['shared_manager'];

class SharedHandler(BaseSharedHandler):
    """
    List all notebook shared
    """

    @web.authenticated
    def get(self):
        path = self.get_argument('path', default="")
        self.finish(json.dumps(self.manager.storage.list(path)));

class SharedActionHandler(BaseSharedHandler):
    """
    Action handler for sharing Notebook
    """
    @web.authenticated
    def get(self, action):
        try:
            notebook_id = unquote(self.get_argument('notebook_id'))
            # Submit a notebook
            if action == 'submit':
                name = unquote(self.get_argument('name', default=None))
                dest = self.manager.storage.submit(notebook_id, name, True);
                self.finish(str(dest));

            # Delete a notebook
            elif action == 'delete':
                if self.manager.storage.delete(notebook_id):
                    self.finish("OK");
                else:
                    raise web.HTTPError(404, "Impossible to delete: %s" % notebook_id);

            # Preview a notebook
            elif action == 'preview':
                self.finish(self.manager.storage.preview(notebook_id))

            # Fetch a notebook
            elif action == 'fetch':
                dest = unquote(self.get_argument('dest'))
                if not dest.endswith('.ipynb'):
                    dest += '.ipynb'
                url = quote(self.manager.storage.fetch(notebook_id, dest));
                self.redirect(ujoin(self.base_url, 'notebooks', url))

            else:
                self.finish("%s is not a valid action!" % action);
        except Exception as e:
            self.log.error("Error happen when do %s on %s" % (action, notebook_id))
            self.log.error(str(e));
            raise web.HTTPError(500, "Error happen when do %s on %s" % (action, notebook_id));

_shared_action_regex = r"(?P<action>fetch|preview|submit|delete)"
default_handlers = [
    (r"/shared", SharedHandler),
    (r"/shared/%s" % _shared_action_regex, SharedActionHandler),
]


def load_jupyter_server_extension(nbapp):
    """Load the nbserver"""
    windows = sys.platform.startswith('win')
    webapp = nbapp.web_app
    webapp.settings['shared_manager'] = SharedManager(parent=nbapp)
    base_url = webapp.settings['base_url']

    install_nbextension(static, destination='nbshared', symlink=not windows, user=True)

    # cfgm = nbapp.config_manager
    # cfgm.update('tree', {
    #     'load_extensions': {
    #         'nbexamples/main': True,
    #     }
    # })
    # cfgm.update('notebook', {
    #     'load_extensions': {
    #         'nbexamples/submit-example-button': True,
    #     }
    # })

    webapp.add_handlers(".*$", [
        (ujoin(base_url, pat), handler)
        for pat, handler in default_handlers
    ])
