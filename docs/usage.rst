.. _usage:

Usage
=====

Generic commands
++++++++++++++++

Check the help
--------------

.. code-block:: bash

   $> issue-manager -h

    usage: esgissue [-h] [-V]  ...

    The publication workflow on the ESGF nodes requires to deal with errata issues.
    The cause behind the version changes has to be published alongside the data: what was updated,
    retracted or removed, and why. Consequently, the publication of a new version of a dataset has to
    be motivated by an issue.

    "issue-manager" allows the referenced data providers to easily create, document, update, close or
    remove a validated issue. The issue registration always appears prior to the publication process and
    should be mandatory for additional version, version removal or retraction.

    "issue-manager" works with both json and txt files. This allows the data provider in charge of ESGF
    issues to manage one or several json templates gathering the issues locally.

    See full documentation on http://esgissue.readthedocs.org/

    Optional arguments:
      -h, --help  Show this help message and exit.

      -V          Program version.

    Issue actions:

        create    Creates ESGF issues from a json template to the errata database.
                  See "issue-manager create -h" for full help.

        update    Updates ESGF issues from a json template to the errata database.
                  See "issue-manager update -h" for full help.

        close     Closes ESGF issues on the errata repository.
                  See "issue-manager close -h" for full help.

        retrieve  Retrieves ESGF issues from the errata repository to a json template.
                  See "issue-manager retrieve -h" for full help.

    Developed by:
    Levavasseur, G. (UPMC/IPSL - glipsl@ipsl.jussieu.fr)
    Bennasser, A. (UPMC/IPSL - abennasser@ipsl.jussieu.fr




Create an issue
---------------

Issue creation is the first step in the issue life cycle, and is a vital part of the errata service as it revolves around
community contributions.
However, creating an issue must abide to a set of rules enforced by the json validation.

Mandatory issue json file fields:

  - title,
  - description,
  - severity,
  - models

dataset list txt file should not be empty, otherwise the command will raise an exception and exit.

.. note:: the log argument is optional, if not used, the standard output will be used.

.. code-block:: bash

   $> issue-manager create --issue /path/to/issue.json --dsets /path/to/datasets.txt --log /path/to/logfile


    2016/09/06 11:00:50 AM INFO Validating of issue...
    2016/09/06 11:00:51 AM INFO Validation Result: SUCCESSFUL
    2016/09/06 11:00:51 AM INFO Requesting issue #03c2e168-7418-443b-82e7-c5d398366144 creation from errata service...
    2016/09/06 11:00:51 AM INFO Updating fields of payload after remote issue creation...
    2016/09/06 11:00:51 AM INFO Issue json schema has been updated, persisting in file...
    2016/09/06 11:00:51 AM INFO Issue file has been created successfully!


If the issue.json or dsets.txt file is missing from options:

.. code-block:: bash

   $> issue-manager create --dsets esgissue/samples/dsets1.txt

    issue-manager create --dsets esgissue/samples/dsets1.txt usage: esgissue create [--log [$PWD]] [-v] [-h] --issue [PATH/issue.json] --dsets [PATH/dsets.list]
    esgissue create: error: argument --issue is required

If a the the issue json file is not properly formed as described in the json templates:

.. code-block:: bash


   $> issue-manager create --issue /path/to/issue_missing_title.json --dsets /path/to/datasets.txt --log /path/to/logfile

    - Missing title (applies to all mandatory parameters):
    2016/09/06 12:06:06 PM INFO Validating of issue...
    2016/09/06 12:06:06 PM ERROR Validation error: u'title' is a required property for required, while validating deque([]).
    2016/09/06 12:06:06 PM ERROR The responsible schema part is: {u'title': u'ESGF issue json schema', u'required': [u'dateCreated', u'title', u'description', u'severity', u'project', u'models', u'datasets', u'variables', u'experiments'], u'additionalProperties': False, u'$schema': u'http://json-schema.org/schema#', u'type': u'object', u'properties': {u'status': {u'enum': [u'new', u'onhold', u'wontfix', u'resolved'], u'type': u'string'}, u'datasets': {u'minItems': 1, u'items': {u'minLength': 1, u'type': u'string'}, u'uniqueItems': True, u'type': u'array'}, u'severity': {u'enum': [u'low', u'medium', u'high', u'critical'], u'type': u'string'}, u'title': {u'minLength': 1, u'type': u'string'}, u'institute': {u'minLength': 1, u'type': u'string'}, u'variables': {u'uniqueItems': True, u'items': {u'minLength': 1, u'type': u'string'}, u'type': u'array'}, u'dateCreated': {u'type': u'string', u'format': u'date-time'}, u'project': {u'minLength': 1, u'enum': [u'cmip5', u'cmip6'], u'type': u'string'}, u'models': {u'uniqueItems': True, u'items': {u'minLength': 1, u'type': u'string'}, u'type': u'array'}, u'materials': {u'uniqueItems': True, u'items': {u'pattern': u'\\.(jpg|gif|png|tiff)$', u'type': u'string'}, u'type': u'array'}, u'url': {u'minLength': 1, u'type': u'string'}, u'uid': {u'pattern': u'^[0-9a-f]{8}(-[0-9a-f]{4}){3}-[0-9a-f]{12}$', u'type': u'string'}, u'experiments': {u'uniqueItems': True, u'items': {u'minLength': 1, u'type': u'string'}, u'type': u'array'}, u'description': {u'minLength': 1, u'type': u'string'}}}

If the dataset list txt file is empty:

.. code-block:: bash


   $> issue-manager create --issue /path/to/issue.json --dsets /path/to/empty_dataset_list.txt --log /path/to/logfile

    2016/09/06 12:24:15 PM INFO Validating of issue...
    2016/09/06 12:24:15 PM ERROR Validation error: [] is too short for minItems, while validating deque([u'datasets']).
    2016/09/06 12:24:15 PM ERROR The responsible schema part is: {u'minItems': 1, u'items': {u'minLength': 1, u'type': u'string'}, u'uniqueItems': True, u'type': u'array'}


If the dataset list txt file contains malformed dataset_ids:

.. code-block:: bash


   $> issue-manager create --issue /path/to/issue.json --dsets /path/to/malformed_datasets.txt --log /path/to/logfile

    2016/09/06 03:15:50 PM INFO Validating of issue...
    2016/09/06 03:15:51 PM ERROR Validation Result: FAILED // Dataset IDs have invalid format, error code: 3

.. note:: On success the local issue file will be modified, so please make sure the client has sufficient writing rights
          to the file. The creation and update dates will be appended as well as the issue uid and status.

Update an issue
---------------

Once an issue is created, it will be subject to some changes, whether it regards the content of the issue (description
for instance) or the status of the issue (changing status). The update of an issue is a key part of the issue life-cycle.

The update command has a similar structure as the creation command, and also similar constraints, plus a few more that
will be detailed here.

Some attributes cannot be changed. If a mistake occurred while declaring the issue, it should be reported to the admins.
These attributes consist in:

- Title
- Project
- Institute.

As well as the key dates in the issue file (creation, update, closed dates), those should not be modified in order to
preserve an authentic set of records, in case of compromised local records users can use the retrieve command to download
fresh copies from the errata server.

Another major additional constraint is the modification of the issue description. As a matter of fact updating the
description is controlled by a variation threshold that should not be exceeded. Which is currently set at 20%, if the
description is to be changed more than that, the issue should be closed and the creation of a brand new issue is required.


.. code-block:: bash

   $> issue-manager update --issue /path/to/issue.json --dsets /path/to/new_datasets.txt --log /path/to/logfile


    2016/09/06 05:45:14 PM INFO Validating of issue...
    2016/09/06 05:45:15 PM INFO Validation Result: SUCCESSFUL
    2016/09/06 05:45:15 PM INFO Update issue #66b1b471-221a-42ac-ad69-0a048e924cd4
    2016/09/06 05:45:15 PM INFO Issue has been updated successfully!



If a the issue.json or dsets.txt file is missing from options:

.. code-block:: bash

   $> issue-manager update --dsets esgissue/samples/dsets1.txt

    issue-manager update --dsets esgissue/samples/dsets1.txt usage: esgissue update [--log [$PWD]] [-v] [-h] --issue [PATH/issue.json] --dsets [PATH/dsets.list]
    esgissue update: error: argument --issue is required

.. note:: The previously explained safeguards for the issue creation are also valid in the update context, empty dataset
          lists are rejected as well as malformed dataset ids. The issue json should always be conform to the templates otherwise
          an exception will be thrown.


Close an issue
--------------

At the end of an issue's lifecycle, it should be marked as a closed issue, in order to prevent confusion.
To do so a specific close command is made available in the errata client.
.. note:: To close an issue it should not have a status Wont_fix or New.

The close command has a similar structure to the creation and update.

.. code-block:: bash

   $> issue-manager close --issue /path/to/issue.json --dsets /path/to/new_datasets.txt --log /path/to/logfile

    2016/09/06 06:27:53 PM INFO Validating of issue...
    2016/09/06 06:27:53 PM INFO Validation Result: SUCCESSFUL
    2016/09/06 06:27:53 PM INFO Closing issue #66b1b471-221a-42ac-ad69-0a048e924cd4
    2016/09/06 06:27:53 PM INFO Issue has been closed successfully!

.. note:: The close command also modifies the issue files by adding the close date and changing the status.


Retrieving issues:
------------------

At some point it might be a good idea to keep a local copy of the errata information hosted within the errata system.
The retrieve command has been designed in the aim of either downloading a specific issue files, a set of specific issues,
or the whole lot of issues hosted within the errata system (for archiving purposes for example).

The command takes as arguments the list of uids (optional, leave blank if all issues are expected), the json file directory
and the dataset list txt file directory the user wishes to use.

.. note:: in case of multiple issues download it is mandatory the path provided for issues and directories be a directory.
          In the case of a single issue download, a json and txt file would be sufficient.

.. code-block:: bash


    $> issue-manager retrieve --issue esgissue/samples/downloads --dsets esgissue/samples/downloads
    --id 66b1b471-221a-42ac-ad69-0a048e924cd4

    2016/09/06 06:44:28 PM INFO processing id 66b1b471-221a-42ac-ad69-0a048e924cd4
    2016/09/06 06:44:28 PM INFO Issue has been downloaded.

This command the issue with id #66b1b471-221a-42ac-ad69-0a048e924cd4 has been downloaded to the downloads directory.
The naming convention used in creating the issue related files is issue_<uid>.json & dset_<uid>.txt

.. note:: if needed we could have specified json and txt file in this example since we are downloading a single issue.

Multiple downloads:

.. code-block:: bash

    $> issue-manager retrieve --issue esgissue/samples/downloads --dsets esgissue/samples/downloads
    --id 66b1b471-221a-42ac-ad69-0a048e924cd4 8f8178db-d772-449d-86d2-90385479f8e6

    2016/09/06 06:49:39 PM INFO processing id 66b1b471-221a-42ac-ad69-0a048e924cd4
    2016/09/06 06:49:39 PM INFO Issue has been downloaded.
    2016/09/06 06:49:39 PM INFO processing id 8f8178db-d772-449d-86d2-90385479f8e6
    2016/09/06 06:49:39 PM INFO Issue has been downloaded.

Multiple downloads with file instead of directory as argument:

.. code-block:: bash

    $>issue-manager retrieve --issue esgissue/samples/issue.json --dsets esgissue/samples/dset.txt
    --id 66b1b471-221a-42ac-ad69-0a048e924cd4 8f8178db-d772-449d-86d2-90385479f8e6

    You have provided multiple ids but a single file as destination, aborting.


Exit status:

- [0]: Successful execution of the requested task,
- [99]: An unexpected error has caused the task to fail. Check the error message for fix and/or contact the developers.

See full documentation on http://esgissue.readthedocs.org/

The default values are displayed next to the corresponding flags.

Positional arguments:
 command                               One of the four possible actions, create, update, close and retrieve.

Optional arguments:
 --issue                               Issue json file.

 --dsets                               dataset list txt file.

 --log                                 Directory for log output.

 -h, --help                            Show this help message and exit.

 -v                                    Verbose mode.

 -V                                    Program version.

Developed by:
Levavasseur, G. (UPMC/IPSL - glipsl@ipsl.jussieu.fr)
Ben Nasser, A. (IPSL - abennasser@ipsl.jussieu.fr)
