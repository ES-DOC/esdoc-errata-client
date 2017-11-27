.. _index:


ESGF Errata Client
==================

Proper handling of errata information in the ESGF publication workflow has major impact on the quality of data.
Version changes should be documented and justified by explaining what was updated, retracted and/or removed.
This leads to the unspoken rule that any publication of a newer version of a dataset needs to have a valid motivation,
which we will refer to as an issue.
Consequently, the publication of a new version of a dataset has to be motivated by an issue and conversely.

The ESGF errata client, called ``esgissue`` is a piece of software that enables the interaction with the errata service.
It can be used to easily create, update, close and retrieve issues. The client is basically aimed to be used by data providers and managers
that are notified of the existence of an issue regarding one or many datasets/files.

.. note:: The issue registration should be executed prior to the publication process and is ought to be mandatory for additional
    versions, version removal or retraction.

.. note:: ``esgissue`` relies on ``.json`` and ``.txt`` file records. This enables the data provider, in charge of ESGF issues, to
    efficiently manage one or several issues remotely and locally.

.. toctree::
   :maxdepth: 1

   installation
   configuration
   usage
   create
   update
   close
   retrieve
   api
   faq
   credits
   log

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
