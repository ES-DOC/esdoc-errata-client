.. _close:


Close an issue
==============

At the end of an issue's lifecycle, it should be marked as a closed issue in order to prevent confusion. To do so a specific ``close`` subcommand is made available in the ESGF errata client .

Requirements
************

Closing an issue on the ES-DOC Errata server requires the corresponding issue template and list of affected datasets.
In case of those files have been locally removed or compromised, users can easily retrieve fresh copies from the ES-DOC Errata server using the :ref:`retrieve` subcommand.
Contrary to the :ref:`update` step, closing an issue doesn't require to modify the local files.
Similar constraints and safeguards are applied to the issue JSON fields (see :ref:`update`)

.. note:: The ``close`` subcommand also modifies the issue files by adding the close date and changing the status to "wontfix" or "resolved" depending the user choice.

.. note:: If the issue status has already been updated to "wontfix" or "resolved" the ``close`` subcommand just close the issue on the ES-DOC Errata server.

.. warning:: The previously explained safeguards for the issue creation are also valid in the update context, empty dataset
    lists are rejected as well as malformed dataset ids. The issue json should always be conform to the templates otherwise
    an exception will be thrown.

Close the issue
***************

The final step remaining in the life cycle of the issue is either to close the issue and mark it as done with, or flag it as a "wontfix", that will however keep the issue
open for other users to be careful about the affected files in future use. To mark it as a "wontfix", an update as shown above is sufficient.
To close an issue, users are required to use the client's ``close`` command. Which will mark issue as closed in the remote ESGF Errata server and reflect this change in the local
files in coherence with every step in the issue life cycle.

From our previous issue (see :ref:`update`), the ``close`` subcommand has a similar structure to the creation and update:

.. code-block:: bash

   $> esgissue close --issue /path/to/issue.json --dsets /path/to/new_datasets.txt

On success the local issue file will be modified one last time by adding the close date accordingly:

.. code-block:: json

    {
        "uid": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
        "title": "Test issue title",
        "description": "This is a NEW test description, void of meaning.",
        "project": "cmip6",
        "severity": "critical",
        "materials": [
            "http://myerrata.com/images/before.jpg",
            "http://myerrata.com/images/after.jpg"
        ],
        "url": "http://websitetest.com/",
        "status": "resolved",
        "dateClosed": "YYYY-MM-DD HH:MM:SS",
        "dateUpdated": "YYYY-MM-DD HH:MM:SS",
        "dateClosed": "YYYY-MM-DD HH:MM:SS"
    }

The issue is now closed and is kept for archiving/consultation purposes.
