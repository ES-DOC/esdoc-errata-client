.. _retrieve:

Retrieve an issue
=================

At some point it might be a good idea to keep a local copy of the errata information hosted within the errata system.
The `retrieve`` command has been designed in the aim of either downloading a specific issue files, a set of specific issues,
or the whole lot of issues hosted within the errata system (for archiving purposes for example).
`
Requirements
************

The command takes as arguments a list of UIDs, the JSON file directory and the dataset list file directory the user wishes to use.
If no UIDs are submitted, all issues are expected.

.. warning::
    In case of multiple issues download it is mandatory the path provided for issues and directories be a directory.
    In the case of a single issue download, a ``json`` and ``txt`` file would be sufficient.

Example
*******

In order to download the issue with id ``66b1b471-221a-42ac-ad69-0a048e924cd4``:

.. code-block:: bash

    $> esgissue retrieve --issue esgissue/samples/downloads --dsets esgissue/samples/downloads --id 66b1b471-221a-42ac-ad69-0a048e924cd4
    2016/09/06 06:44:28 PM INFO processing id 66b1b471-221a-42ac-ad69-0a048e924cd4
    2016/09/06 06:44:28 PM INFO Issue has been downloaded.

.. note::

    The naming convention used in creating the issue related files is ``issue_<uid>.json`` and ``dset_<uid>.txt``.
    If needed we could have specified ``json`` and ``txt`` file in this example since we are downloading a single issue.

For multiple downloads:

.. code-block:: bash

    $> esgissue retrieve --issue esgissue/samples/downloads --dsets esgissue/samples/downloads --id 66b1b471-221a-42ac-ad69-0a048e924cd4 8f8178db-d772-449d-86d2-90385479f8e6
    2016/09/06 06:49:39 PM INFO processing id 66b1b471-221a-42ac-ad69-0a048e924cd4
    2016/09/06 06:49:39 PM INFO Issue has been downloaded.
    2016/09/06 06:49:39 PM INFO processing id 8f8178db-d772-449d-86d2-90385479f8e6
    2016/09/06 06:49:39 PM INFO Issue has been downloaded.
    $> ls -l esgissue/samples/downloads
    issue_66b1b471-221a-42ac-ad69-0a048e924cd4.json
    issue_8f8178db-d772-449d-86d2-90385479f8e6.json
    $> ls -l esgissue/samples/downloads
    dset_66b1b471-221a-42ac-ad69-0a048e924cd4.json
    dset_8f8178db-d772-449d-86d2-90385479f8e6.json

Mistakes to avoid
*****************

If multiple downloads with file instead of directory as argument:

.. code-block:: bash

    $> esgissue retrieve --issue esgissue/samples/issue.json --dsets esgissue/samples/dset.txt --id 66b1b471-221a-42ac-ad69-0a048e924cd4 8f8178db-d772-449d-86d2-90385479f8e6
    You have provided multiple ids but a single file as destination, aborting.
