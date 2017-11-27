.. _installation:


Installation
============

Usual PIP installation
**********************

.. code-block:: bash

  pip install esgissue-client

PIP installation from GitHub
****************************

.. code-block:: bash

   pip install -e git@github.com:ES-DOC/esdoc-errata-client.git@master#egg=esdoc-errata-client

Installation from GitHub
************************

1. Clone `our GitHub project <http://github.com/ES-DOC/esdoc-errata-client/>`_:

.. code-block:: bash

  git clone git@github.com:ES-DOC/esdoc-errata-client.git@master

2. Run the ``setup.py``:

.. code-block:: bash

  cd esdoc-errata-client
  python setup.py install

3. The ``esgissue`` command-line is ready.

.. warning:: To run ``esgissue`` you have to be logged into a machine with internet access.


Dependencies and requirements
*****************************

Linux distribution with Python 2.6+ is required. ``esgissue`` uses the following basic Python libraries. Ensure that
your Python environment includes:

 * `os <https://docs.python.org/2/library/os.html>`_
 * `collections <https://docs.python.org/2/library/collections.html>`_
 * `fnmatch <https://docs.python.org/2/library/fnmatch.html>`_
 * `linecache <https://docs.python.org/fr/2.7/library/linecache.html>`_
 * `getpass <https://docs.python.org/fr/2.7/library/getpass.html>`_
 * `sys <https://docs.python.org/2/library/sys.html>`_
 * `re <https://docs.python.org/2/library/re.html>`_
 * `platform <https://docs.python.org/fr/2.7/library/platform.html>`_
 * `argparse <https://docs.python.org/2/library/argparse.html>`_
 * `logging <https://docs.python.org/2/library/logging.html>`_
 * `ConfigParser <https://docs.python.org/2/library/configparser.html>`_
 * `datetime <https://docs.python.org/2/library/datetime.html>`_
 * `uuid <https://docs.python.org/2/library/uuid.html>`_
 * `string <https://docs.python.org/2/library/string.html>`_
 * `json <https://docs.python.org/2/library/json.html>`_
 * `textwrap <https://docs.python.org/2/library/textwrap.html>`_

Some required libraries are not included in most Python distributions. Please install them using the usual PIP command:

 * `jsonschema <https://pypi.python.org/pypi/jsonschema>`_
 * `requests <https://pypi.python.org/pypi/requests/2.11.1>`_
 * `pbkdf2 <https://www.dlitz.net/software/python-pbkdf2/>`_
 * `pyDes <http://twhiteman.netfirms.com/des.html>`_

.. code-block:: bash

   pip install <pkg_name>
