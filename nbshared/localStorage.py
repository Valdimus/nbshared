import os
import shutil
import sys
import json
import glob

from nbshared import Storage;
from nbshared.m_utils import *;

static = os.path.join(os.path.dirname(__file__), 'static')

class LocalStorage(Storage):
    """
    Class to use a local directory to share notebooks
    """
    def __init__(self, path="/tmp/nbshared", **kwargs):
        """
        :param path: Path to the local directory to use
        """
        Storage.__init__(self, **kwargs);
        self.path = path;

        self.log.info("Load LocalStorage for nbshared");

    def do_list(self, path=""):
        """
        List all avaible notebooks in a directory
        :param path: Path to the directory
        """
        notebooks = [];
        filepaths = glob.glob(os.path.join(os.path.join(self.path, path), '*.ipynb'));
        uid = os.getuid();
        for fp in filepaths:
            notebooks.append({
                "filepath": os.path.abspath(fp).replace(self.path+"/", ""),
                "filename": os.path.basename(fp),
                "owned": os.stat(fp).st_uid == uid,
                "type": "FILE"
            });

        return notebooks;

    def do_delete(self, filepath):
        """
        Remove a shared notebook
        :param filepath: File to delete

        :return Boolean, True if file is delete, False otherwise
        """
        fp = os.path.join(os.path.join(self.path, filepath.replace("../", "")));
        if not os.path.isfile(fp):
            return False
        try:
            os.remove(fp);
            return True;
        except:
            return False;

    def do_read(self, filepath):
        """
        Read a notebook on local storage
        :param filepath: Path to the notebook

        :return the content of the notebook (just read its content, so return a string)
        """
        fp = os.path.join(os.path.join(self.path, filepath.replace("../", "")));
        with open(fp, "r") as reader:
            return reader.read();

    def do_write(self, filepath, content):
        """
        Write a notebook on local storage
        :param filepath: Path to the file to delete
        :param content: Content of the file to write, must be a string

        :return a boolean
        """
        fp = os.path.join(os.path.join(self.path, filepath.replace("../", "")));
        with open(fp, "w") as writer:
            writer.write(content);
            writer.flush();
        return True;
