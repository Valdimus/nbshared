import os
import hdfs

from nbshared import Storage;

class HdfsStorage(Storage):
    """
    Use Hdfs to store shared notebooks
    """
    def __init__(self, url, hdfsUser, path, **kwargs):
        """
        :param url: Url to the webhdfs
        :param hdfsUser: User for authentification on webhdfs (use InsecureClient)
        :param path: Path to the directory to share on hdfs
        """
        Storage.__init__(self, **kwargs);

        self.log.info("Load HdfsStorage for nbshared");

        self.path = path;
        self.url=url;
        self.hdfsUser = hdfsUser if hdfsUser != None else os.environ['USER'];
        self.client = hdfs.InsecureClient(url, user=self.hdfsUser);

    def do_list(self, path=""):
        """
        List all avaible notebooks in a directory
        :param path: Path to the direcory

        :return A list of File or Directory
        """
        m_path = os.path.join(self.path, path);
        notebooks = [];
        for nb in self.client.list(m_path):
            status = self.client.status(os.path.join(m_path, nb));
            directory = ""
            if status["type"] == "FILE" and nb.endswith(".ipynb"):
                notebooks.append({
                    'filepath': os.path.join(directory, nb),
                    'filename': nb,
                    'metadata': False,
                    'owned': status['owner'] == os.environ['USER'],
                    'type': "FILE"
                })
        return notebooks;

    def do_delete(self, filepath):
        """
        Remove a shared notebook
        :param filepath: path to the file to delete

        :return Boolean, True if file is delete, False otherwise
        """
        try:
            fp = os.path.join(os.path.join(self.path, filepath.replace("../", "")));
            if self.client.status(fp)['type'] == "FILE":
                self.client.delete(fp)
                return True;
        except:
            return False;
        return False;

    def do_read(self, filepath):
        """
        Read a notebook on hdfs storage
        :param filepath: Path to the notebook

        :return the content of the notebook (just read its content, so return a string)
        """
        fp = os.path.join(os.path.join(self.path, filepath.replace("../", "")));
        with self.client.read(fp, encoding='utf-8') as reader:
            return reader.read();

    def do_write(self, filepath, content):
        """
        Write a notebook on hdfs storage
        :param filepath: Path to the file to delete
        :param content: Content of the file to write, must be a string

        :return a boolean
        """
        fp = os.path.join(os.path.join(self.path, filepath.replace("../", "")));
        with self.client.write(fp, encoding='utf-8') as writer:
            writer.write(content);
        return True;
