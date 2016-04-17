# nbshared

This is a Jupyter extension that shows a list of notebooks that users
can easily preview and copy for their own use.

The targeted application is a JupyterHub deployment, where it is useful to
distribute a collection of curated examples or templates and make it possible
for hub uses to quickly share notebooks.

A new "Shared Notebooks" page lists notebooks from some configured storage. For each notebook
there are two buttons, "preview" and "use".



Clicking "preview" shows a static HTML version of the notebook.

Clicking "use" opens a dialog box to prompt user for a filename or filepath
(relative to their home dir).

![Fetch](docs/fetch-dialog.png)

On the notebook toolbar, a new "Share this notebook" button (the "paper airplane"
icon at right) submits the notebook to the list of "Shared Notebooks".

![Share this Notebook button](docs/share-button.png)

### URL scheme

* `/tree#shared` is the "Shared Notebooks" tab on the user's home page
* `/shared` returns JSON that populates the contents of that tab
* `/shared/preview?notebook_id=xpcs.ipynb` shows a static HTML preview (similar to
  nbviewer)
* `/shared/fetch?notebook_id=xpcs.ipynb&dest=my-xpcs.ipynb` makes a copy of
  the notebook in the user's home directory, stripping out the example output
* `/shared/submit?notebook_id=my-new-example.ipynb` copies a clean notebook into a shared
* `/shared/delete?notebook_id=my-new-example.ipynb` delete a notebook to the storage

### Requirements

* nbconvert
* nbformat
* hdfs for the hdfs storage

### Installation

```
python setup.py install
```

In addition to installing the `nshared` packages, the installation adds a
server extension to the jupyter notebook config file:

```python
c.NotebookApp.server_extensions.append('nbshared.handlers')
```

### Configuration

Mutilple configuration possible:

* Local
* hdfs

#### Local

Set the location of the shared notebooks to be distributed by adding this
line to the jupyter notebook config file:

```python
c.SharedManager.storage_class = "nbshared.LocalStorage"
c.SharedManager.storage_options = {
    "path": "/path/to/directory/to/share"
}
```

The intention is that `path` is a globally-writable directory.

#### Hdfs

Set the location of the shared notebooks to be distributed by adding this
line to the jupyter notebook config file:

```python
c.SharedManager.storage_class = "nbshared.HdfsStorage"
c.SharedManager.storage_options = {
    "url": "http://NAMENODE_ADDRESS:PORT",
    "hdfsUser": None,
    "path": "/path/to/directory/to/share"
}
```

If hdfsUser is set to None, the user who launch the jupyter instance will be use.

### Related Work

This project is indebted to the [nbexamples](https://github.com/danielballan/nbexamples) project and the [nbgrader](nbgrader.readthedocs.org) project,
a related (and much more complex!) application.
