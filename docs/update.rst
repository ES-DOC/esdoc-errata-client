.. _update:

Update an issue
===============

Once an issue is created, it inevitably will be subject to some changes, whether it regards the content of the issue (description
for instance), its status or the list of affected datasets.

Requirements
************

Updating an issue on the ES-DOC Errata server requires modifying the corresponding issue template or list of affected
datasets on local files.
In case of those files have been locally removed or compromised, users can easily retrieve fresh copies from the ES-DOC
Errata server using the :ref:`retrieve` subcommand.
The new issue JSON file is still constrained and validated against a new JSON schema.
In fact, to guarantee the issue quality some attributes are immutable.

+-------------------+-----------------------------------------------+
| Field             | Requirement                                   |
+===================+===============================================+
| ``uid``           | Mandatory and unchanged                       |
+-------------------+-----------------------------------------------+
| ``title``         | Mandatory and unchanged                       |
+-------------------+-----------------------------------------------+
| ``description``   | Mandatory and value-controlled                |
+-------------------+-----------------------------------------------+
| ``mip_era``       | Mandatory and unchanged                       |
+-------------------+-----------------------------------------------+
| ``severity``      | Mandatory and value-controlled                |
+-------------------+-----------------------------------------------+
| ``status``        | Mandatory and value-controlled                |
+-------------------+-----------------------------------------------+
| ``landing_page``  | Optional                                      |
+-------------------+-----------------------------------------------+
| ``materials``     | Optional                                      |
+-------------------+-----------------------------------------------+
| ``dateCreated``   | Mandatory and unchanged                       |
+-------------------+-----------------------------------------------+
| ``dateUpdated``   | Mandatory and unchanged                       |
+-------------------+-----------------------------------------------+
| ``dateClosed``    | Not expected                                  |
+-------------------+-----------------------------------------------+

.. warning::

   Safeguards requirements are:
    - Empty attributes are disallowed.
    - As a matter of fact updating the description is controlled by a variation threshold that should not be exceeded.
    Which is currently set at 20%, if the description is to be changed more than that, the issue should be closed and the creation of a brand new issue is required.
    - All optional URLs must be valid (i.e., accessible).
    - A status “new” will be affected by the server on the creation.
    - The creation date should not be modified in order to preserve an authentic set of records.
    - The updated date is returned by the server.
    - The issue status cannot change back to "new".

.. note::

    If a mistake occurred while declaring the issue, it should be reported to the administrators (see :ref:`credits`).

Finally, feel free to remove, add or modify any dataset identifiers into the corresponding list if necessary.

Example
*******

The life cycle of an issue may incorporate a few changes within the contents of an issue.
The ``issue.json`` needs to be at contain the same fields as in after the creation action. If your local file is corrupted
consider using the :ref:`retrieve` subcommand to download a fresh copy.

From our previous issue template (see :ref:`create`), we altered the description of the issue, the severity, the status status and added 2 new affected datasets.
This will lead to updated files files as follows:

``issue.json``:

.. code-block:: json

    {
        "uid": "017597ba-d6ab-41c8-a1d2-e0aa3f0dd0c1",
        "title": "Test issue title",
        "description": "This is a NEW test description, void of meaning.",
        "project": "cmip5",
        "severity": "critical",
        "materials": [
            "http://errata.ipsl.upmc.fr/static/images_errata/time.jpg",
            "http://errata.ipsl.upmc.fr/static/images_errata/time5.jpg"
        ],
        "url": "http://websitetest.com/",
        "status": "onhold",
        "dateClosed": "YYYY-MM-DD HH:MM:SS",
        "dateUpdated": "YYYY-MM-DD HH:MM:SS"
    }

``dataset.txt``:

.. code-block:: none

    cmip5.output1.IPSL.IPSL-CM5A-MR.historical.mon.land.Lmon.r1i1p1#20111119
    cmip5.output1.IPSL.IPSL-CM5A-MR.historical.mon.land.Lmon.r2i2p2#20121212
    cmip5.output1.IPSL.IPSL-CM5A-LR.historical.mon.land.Lmon.r3i1p1#20130514
    cmip5.output1.IPSL.IPSL-CM5A-LR.piControl.mon.land.Lmon.r3i1p1#20130514
    [...]

The update command has a similar structure as the creation command:

.. code-block:: bash

   $> esgissue update --issue /path/to/issue.json --dsets /path/to/new_datasets.txt
    2016/09/06 05:45:14 PM INFO Validating of issue...
    2016/09/06 05:45:15 PM INFO Validation Result: SUCCESSFUL
    2016/09/06 05:45:15 PM INFO Update issue #66b1b471-221a-42ac-ad69-0a048e924cd4
    2016/09/06 05:45:15 PM INFO Issue has been updated successfully!

On success the local issue file will be modified again. The update date will be modified accordingly:

.. code-block:: json

    {
        "uid": "017597ba-d6ab-41c8-a1d2-e0aa3f0dd0c1",
        "title": "Test issue title",
        "description": "This is a NEW test description, void of meaning.",
        "project": "cmip5",
        "severity": "critical",
        "materials": [
            "http://errata.ipsl.upmc.fr/static/images_errata/time.jpg",
            "http://errata.ipsl.upmc.fr/static/images_errata/time5.jpg"
        ],
        "url": "http://websitetest.com/",
        "status": "onhold",
        "dateClosed": "YYYY-MM-DD HH:MM:SS",
        "dateUpdated": "YYYY-MM-DD HH:MM:SS"
    }

The updates now are registered both in the remote errata service and are reflected in the local issue files.


Mistakes to avoid
*****************

.. warning::

    The previously explained safeguards for the issue creation are also valid in the update context, empty dataset
    lists are rejected as well as malformed dataset ids. The issue json should always be conform to the templates otherwise
    an exception will be thrown.
