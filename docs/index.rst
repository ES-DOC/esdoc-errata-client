.. _index:


ESGF Errata Service
===================

As part of the `ES-DOC <https://es-doc.org/>`_ ecosystem, the Errata Service centralizes timely information about known issues of ESGF data.

Proper handling of errata information in the ESGF publication workflow has major impact on the quality of data.
Version changes should be documented and justified by explaining what was updated, retracted and/or removed.
This leads to the unspoken rule that any publication of a newer version of a dataset needs to have a valid motivation,
which we will refer to as an issue.
Consequently, the publication of a new version of a dataset, as well as the unpublication of a dataset version, has to be motivated by an issue and conversely.

.. note::
    The issue registration should be executed prior to the publication process and is ought to be mandatory for additional versions, version removal or retraction.

.. image:: images/errata_service.png
   :scale: 20%
   :alt: ESGF Errata Service Overview
   :align: center

The Errata Service offers to ESGF users to query about modifications and/or corrections applied to their data in different ways:

    - Through a user-friendly filtered list of ESGF known issues,
    - Through a search interface based on a dedicated API to get the version history of a (set of) file(s)/dataset(s).

.. note::
    CMIP6, CMIP5 and CORDEX projects are currently supported by the Errata Service, with more to come in the next months.

.. toctree::
    :maxdepth: 1

    searchUI
    lookup
    viewer
    login
    create
    update
    close
    client
    api
    faq
    credits
    log

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
