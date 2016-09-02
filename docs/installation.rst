.. _installation:


Installation
============

Usual PIP installation 
**********************

.. code-block:: bash

  pip install esdoc-errata-client

PIP installation from GitHub
****************************

.. code-block:: bash

  pip install -e git@github.com:ES-DOC/esdoc-errata-client.git@master#egg=esgissue

Installation from GitHub
************************

1. Create a new directory:

.. code-block:: bash

  mkdir esgissue
  cd esgissue

2. Clone `our GitHub project <http://github.com/ES-DOC/esdoc-errata-client/>`_:

.. code-block:: bash

  git init
  git clone git@github.com:ES-DOC/esdoc-errata-client.git@master

3. Run the ``setup.py``:

.. code-block:: bash

  python setup.py install

4. Set up environment variables:

.. code-block:: bash
  source activate

5. The ``esgissue`` command-line is ready.


Dependencies
************

``esgissue`` uses the following basic Python libraries includes in Python 2.5+. Becareful your Python
environment includes:

 * `os <https://docs.python.org/2/library/os.html>`_, `sys <https://docs.python.org/2/library/sys.html>`_, `re
 <https://docs.python.org/2/library/re.html>`_, `logging <https://docs.python.org/2/library/logging.html>`_
 * `argparse <https://docs.python.org/2/library/argparse.html>`_
 * `ConfigParser <https://docs.python.org/2/library/configparser.html>`_
 * `datetime <https://docs.python.org/2/library/datetime.html>`_
 * `uuid <https://docs.python.org/2/library/uuid.html>`_
 * `requests <http://docs.python-requests.org/en/master/>`_
 * `string <https://docs.python.org/2/library/string.html>`_
 * `textwrap <https://docs.python.org/2/library/textwrap.html>`_
 * `collections <https://docs.python.org/2/library/collections.html>`_
 * `json <https://docs.python.org/2/library/json.html>`_
 * `copy <https://docs.python.org/2/library/copy.html>`_

``esgissue`` requires the following libraries not included in most Python distributions:

 * *esgfpid*
 * `jsonschema <https://pypi.python.org/pypi/jsonschema>`_
 * `requests <https://pypi.python.org/pypi/requests/2.11.1>`
