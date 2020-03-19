.. _client:


Command Line Interface
======================

The ESGF errata client, called ``esgissue`` is a piece of software that enables the interaction with the errata service.
Like the web forms, it can be used to easily create, update, close and retrieve issues. The client is basically aimed to be used by publishing teams, data providers and managers
that are notified of the existence of an issue regarding one or many datasets/files.

This lightweight CLI relies on ``.json`` and ``.txt`` file records. This enables the data provider, in charge of ESGF issues, to efficiently manage one or several issues remotely and locally.

.. note::
    `Some screencasts are available on YouTube <https://www.youtube.com/channel/UCFVy0HC9cnGbIKc6UsDIHDA/playlists>`_ to learn about the Errata CLI usage.


.. toctree::
    :maxdepth: 1

    installation
    configuration
    usage
    create_cli
    update_cli
    close_cli
    retrieve_cli