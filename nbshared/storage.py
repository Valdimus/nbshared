import os;

import nbformat;

import logging;

from nbconvert import HTMLExporter;
from operator import itemgetter;
from nbshared.m_utils import *;

class JupyterLocalStorage:
    """
    Certainly a temporary class
    Just a way to abstract the local storage of jupyter.
    """

    def __init__(self, notebook_dir=os.path.expanduser('~'), notebook_shared_dir="Shared Notebooks"):
        """
        :param notebook_dir: notebook directory for an user
        :param notebook_shared_dir: path to the shared notebook directory in the notebook directory
        """
        self.__notebookDir = notebook_dir;
        self.__sharedDirName = notebook_shared_dir;

        # Create the shared notebook directory
        if not os.path.isdir(self.absSharedNotebook):
            os.makedirs(self.absSharedNotebook);

    @property
    def directory(self):
        """
        Return the path to the notebook directory
        """
        return self.__notebookDir;

    @property
    def sharedNotebook(self):
        """
        Return the path to the shared notebook directory in the notebook directory
        """
        return self.__sharedDirName;

    @property
    def absSharedNotebook(self):
        """
        Return the path to the shared directory
        """
        return os.path.join(self.directory, self.__sharedDirName);

    def write(self, filename, content):
        """
        Write a notebook to local storage
        :param filename: Notebook name
        :param content: content of the notebook (must be a string)

        :return True is write is ok else an exception is raise
        """
        fp = os.path.join(self.absSharedNotebook, filename.replace("../", ""));
        with open(fp, "w") as writer:
            writer.write(content);
            writer.flush();
        return True;

    def read(self, filepath):
        """
        Read a notebook from local storage:
        :param filepath: Path t hte file to read

        :return the content of the file as a string
        """
        fp = os.path.join(self.directory, filepath.replace("../", ""));

        with open(fp, "r") as reader:
            return reader.read();

class Storage:
    """
    Abstract storage class
    You must implement methods below:
        - do_list
        - do_delete
        - do_read
        - do_write

    Use case:
        Notebook dir of user must be there home or each user must have an unique directory.
    """

    def __init__(self, log=logging.getLogger("TemporaryLogger"), JupyterStorage_class="nbshared.JupyterLocalStorage", JupyterStorage_opt={}):
        """
        Constructor
        :param JupyterStorage_class: Class to use for local notebook storage
        :param JupyterStorage_opt: Option to pass to JupyterStorage_class
        """

        self.log = log;

        # Create a local Jupyter Storage
        self.__local = create_instance(JupyterStorage_class, JupyterStorage_opt);

    @property
    def local(self):
        """
        Rerturn the local storage object for jupyter
        """
        return self.__local;

    def stripOutput(self, notebook):
        """
        Cleann all output in the notebook
        :param notebook_path: The notebook as NotebookNode object

        :return a NotebookNode object with all ouput striped
        """
        if not "cells" in notebook:
            return notebook;

        for nb in notebook.cells:
            if 'outputs' in nb:
                nb['outputs'] = []
            if 'prompt_number' in nb:
                nb['prompt_number'] = None
            if 'execution_count' in nb:
                nb['execution_count'] = None
        return notebook;

    def read(self, filepath, as_version=4):
        """
        Read a notebook from Storage
        :param filepath: The path on the Storage to the notebook to read
        :param as_version: Version of the notebook

        return A NotebookNode objet
        """
        self.log.debug("Read the notebook store at '%s'" % filepath);
        content = self.do_read(filepath);
        return nbformat.reads(content, as_version);

    def write(self, filepath, notebookNode, version=4):
        """
        Write a notebook to Storage
        :param filepath: The path to the notebook to write on the Storage
        :param notebookNode: notebookNode object to write
        :param version: Version of the notebook

        :return boolean
        """
        self.log.debug("Write the notebook '%s' to storage" % filepath)
        content = nbformat.writes(notebookNode, version);
        return self.do_write(filepath, content);

    def list(self, path=""):
        """
        List all file (directory for the next version) of a directory in the Storage
        :param path: Path to the directory
        :return A list of File
        """
        self.log.debug("List all element of '%s' on sotrage" % path);
        element = self.do_list(path);
        return sorted(element, key=itemgetter('filename'));

    def submit(self, filepath, name=None, stripouput=True, version=4, **kargs):
        """
        Submit a notebook
        :param filepath: notebook to send
        :param name: name of the notebook
        :param stripouput: Strip all output cells
        :param version: Version of the notebook

        :return The path to the notebook on the Sotrage
        """

        nb_name = name if name != None else os.path.basename(filepath);
        nb_name = nb_name.replace("../", "");

        self.log.debug("Submit notebook '%s' to '%s' on storage" % (filepath, nb_name));

        # Read the notebook
        nb_content = nbformat.reads(self.local.read(filepath),as_version=version)

        if stripouput:
            nb_content = self.stripOutput(nb_content);

        return self.write(nb_name, nb_content);

    def preview(self, filepath):
        """
        Preview a notebook store in the Storage
        :param filepath: Path to the notebook to preview on Storage

        :return a notebook in html format
        """
        self.log.debug("Make a Html preview of notebook '%s'" % filepath);
        nb = self.read(filepath);
        html_conveter = HTMLExporter()
        (body, resources) = html_conveter.from_notebook_node(nb)
        return body;

    def fetch(self, filepath, dest):
        """
        Fetch a notebook from Storage to home directory
        :param filepath: Path to the notebook on the storage
        :param dest: Path to the notebook fetched in the home directory of the user

        :return the path to the notebook in the home directory of the user
        """
        self.log.debug("Fetch notebook '%s' to '%s'" % (filepath, dest));
        nb = self.read(filepath);

        if not dest.endswith('.ipynb'):
            dest += '.ipynb'
        # Write the notebook on local storage
        self.local.write(dest, nbformat.writes(nb));

        return os.path.join(self.local.sharedNotebook, dest);

    def delete(self, filepath):
        """
        Delete a notebook on the Storage
        :param filepath: Path to the notebook to delete on the Storage

        :return Boolean
        """
        self.log.debug("Delete notebook '%s' on storage" % filepath);
        return self.do_delete(filepath);

    def do_list(self, path=""):
        """
        You must implement this function
        :param path: List all element of a directory

        :return A list of File or Directory
        """
        raise NotImplemented();

    def do_delete(self, filepath):
        """
        You must implement this function
        :param filepath: Path to the notebook to delete on the Storage

        :return Boolean
        """
        raise NotImplemented();

    def do_read(self, filepath):
        """
        You must implement this function
        :param filepath: Path to the notebook to read on the Storage

        :return You must return the content of the file (just read the notebook and return a the content as string)
        """
        raise NotImplemented();

    def do_write(self, filepath, content):
        """
        You must implement this function
        :param filepath: Path to the notebook to write on the Storage
        :param content: Content of the notebook

        :return a boolean
        """
        raise NotImplemented();
