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

    The publication workflow on the ESGF nodes requires to deal with errata issues. The background of
    the version changes has to be published alongside the data: what was updated, retracted or removed,
    and why. Consequently, the publication of a new version of a dataset has to be motivated by an
    issue.

    "issue-manager" allows the referenced data providers to easily create, document, update, close or
    remove a validated issue. The issue registration always appears prior to the publication process and
    should be mandatory for additional version, version removal or retraction.

    "issue-manager" works with both JSON and TXT files. This allows the data provider in charge of ESGF
    issues to manage one or several JSON templates gathering the issues locally.

    See full documentation on http://esgissue.readthedocs.org/

    Optional arguments:
      -h, --help  Show this help message and exit.

      -V          Program version.

    Issue actions:

        create    Creates ESGF issues from a JSON template to the errata database.
                  See "issue-manager create -h" for full help.

        update    Updates ESGF issues from a JSON template to the errata database.
                  See "issue-manager update -h" for full help.

        close     Closes ESGF issues on the errata repository.
                  See "issue-manager close -h" for full help.

        retrieve  Retrieves ESGF issues from the errata repository to a JSON template.
                  See "issue-manager retrieve -h" for full help.

    Developed by:
    Levavasseur, G. (UPMC/IPSL - glipsl@ipsl.jussieu.fr)
    Bennasser, A. (UPMC/IPSL - abennasser@ipsl.jussieu.fr




Create an issue
---------------

Creating an issue is a vital part of the errata service, as the all idea revolves around the community contributions.
However, creating an issue must abide to a set of rules enforced by the json validation.

Mandatory issue json file fields:

  - title,
  - description,
  - severity,
  - models

dataset list txt file should not be empty, otherwise the command will fail.

.. note the log argument is optional, if not used, the standard output will be used.

.. code-block:: bash

   $> issue-manager create --issue /path/to/issue.json --dsets /path/to/datasets.txt --log /path/to/logfile


    2016/09/06 11:00:50 AM INFO Validating of issue...
    2016/09/06 11:00:51 AM INFO Validation Result: SUCCESSFUL
    2016/09/06 11:00:51 AM INFO Requesting issue #03c2e168-7418-443b-82e7-c5d398366144 creation from errata service...
    2016/09/06 11:00:51 AM INFO Updating fields of payload after remote issue creation...
    2016/09/06 11:00:51 AM INFO Issue json schema has been updated, persisting in file...
    2016/09/06 11:00:51 AM INFO Issue file has been created successfully!


If a the issue.json or dsets.txt file is missing from options:

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
    2016/09/06 12:06:06 PM ERROR The responsible schema part is: {u'title': u'ESGF issue JSON schema', u'required': [u'dateCreated', u'title', u'description', u'severity', u'project', u'models', u'datasets', u'variables', u'experiments'], u'additionalProperties': False, u'$schema': u'http://json-schema.org/schema#', u'type': u'object', u'properties': {u'status': {u'enum': [u'new', u'onhold', u'wontfix', u'resolved'], u'type': u'string'}, u'datasets': {u'minItems': 1, u'items': {u'minLength': 1, u'type': u'string'}, u'uniqueItems': True, u'type': u'array'}, u'severity': {u'enum': [u'low', u'medium', u'high', u'critical'], u'type': u'string'}, u'title': {u'minLength': 1, u'type': u'string'}, u'institute': {u'minLength': 1, u'type': u'string'}, u'variables': {u'uniqueItems': True, u'items': {u'minLength': 1, u'type': u'string'}, u'type': u'array'}, u'dateCreated': {u'type': u'string', u'format': u'date-time'}, u'project': {u'minLength': 1, u'enum': [u'cmip5', u'cmip6'], u'type': u'string'}, u'models': {u'uniqueItems': True, u'items': {u'minLength': 1, u'type': u'string'}, u'type': u'array'}, u'materials': {u'uniqueItems': True, u'items': {u'pattern': u'\\.(jpg|gif|png|tiff)$', u'type': u'string'}, u'type': u'array'}, u'url': {u'minLength': 1, u'type': u'string'}, u'uid': {u'pattern': u'^[0-9a-f]{8}(-[0-9a-f]{4}){3}-[0-9a-f]{12}$', u'type': u'string'}, u'experiments': {u'uniqueItems': True, u'items': {u'minLength': 1, u'type': u'string'}, u'type': u'array'}, u'description': {u'minLength': 1, u'type': u'string'}}}

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

.. note On success the local issue file will be modified, so please make sure the client has sufficient writing rights
to the file. The creation and update dates will be appended as well as the issue uid and status.

Update an issue
---------------

Once an issue is created, it might be subject to some changes, whether it regards the content of the issue (description
for instance) or the status of the issue (changing status). The update of an issue is a key part of the issue life-cycle.

It has a similar structure as the creation command, and also similar constraints, plus a few more that will be detailed here.

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

.. note The previously explained safeguards for the issue creation are also valid in the update context, empty dataset
lists are rejected as well as malformed dataset ids. The issue json should always be conform to the templates otherwise
an exception will be thrown.


Close an issue
--------------

At the end of an issue's lifecycle, it should be marked as a closed issue.
To do so a specific close command is made available in the errata client.
.. note To close an issue it should not have a status Wont_fix or New.

The close command has a similar structure to the creation and update.

.. code-block:: bash

   $> issue-manager close --issue /path/to/issue.json --dsets /path/to/new_datasets.txt --log /path/to/logfile

    2016/09/06 06:27:53 PM INFO Validating of issue...
    2016/09/06 06:27:53 PM INFO Validation Result: SUCCESSFUL
    2016/09/06 06:27:53 PM INFO Closing issue #66b1b471-221a-42ac-ad69-0a048e924cd4
    2016/09/06 06:27:53 PM INFO Issue has been closed successfully!

.. note The close command also modifies the issue files by adding the close date and changing the status.


Retrieving issues:
------------------

At some point it might be a good idea to keep a local copy of the errata information hosted within the errata system.
The retrieve command has been designed in the aim of either downloading a specific issue files, a set of specific issues,
or the whole lot of issues hosted within the errata system (for archiving purposes for example).

The command takes as arguments the list of uids (optional, leave blank if all issues are expected), the json file directory
and the dataset list txt file directory the user wishes to use.

.. Note in case of multiple issues download it is mandatory the path provided for issues and directories be a directory.
In the case of a single issue download, a json and txt file would be sufficient.

.. code-block:: bash


    $> issue-manager retrieve --issue esgissue/samples/downloads --dsets esgissue/samples/downloads
    --id 66b1b471-221a-42ac-ad69-0a048e924cd4

    2016/09/06 06:44:28 PM INFO processing id 66b1b471-221a-42ac-ad69-0a048e924cd4
    2016/09/06 06:44:28 PM INFO Issue has been downloaded.

This command the issue with id #66b1b471-221a-42ac-ad69-0a048e924cd4 has been downloaded to the downloads directory.
The naming convention used in creating the issue related files is issue_<uid>.json & dset_<uid>.txt

.. note if needed we could have specified json and txt file in this example since we are downloading a single issue.

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
   [0]: Successful scanning of all files encountered,
   [1]: No valid data or files have been found and no mapfile was produced,
   [2]: A mapfile was produced but some files were skipped.

   See full documentation on http://esgissue.readthedocs.org/

   The default values are displayed next to the corresponding flags.

   Positional arguments:
     directory                             One or more directories to recursively scan. Unix wildcards
                                           are allowed.

   Optional arguments:
     --project <project_id>                Required lower-cased project name.

     -i /esg/config/esgcet/.               Initialization/configuration directory containing "esg.ini"
                                           and "esg.<project>.ini" files. If not specified, the usual
                                           datanode directory is used.

     --mapfile {dataset_id}.{version}.map  Specifies template for the output mapfile(s) name.
                                           Substrings {dataset_id}, {version}, {job_id} or {date}
                                           (in YYYYDDMM) will be substituted where found. If
                                           {dataset_id} is not present in mapfile name, then all
                                           datasets will be written to a single mapfile, overriding
                                           the default behavior of producing ONE mapfile PER dataset.

     --outdir $PWD                         Mapfile(s) output directory. A "mapfile_drs" can be defined
                                           in "esg.ini" and joined to build a mapfiles tree.

     --all-versions                        Generates mapfile(s) with all versions found in the
                                           directory recursively scanned (default is to pick up only
                                           the latest one). It disables --no-version.

     --version 20162704                    Generates mapfile(s) scanning datasets with the
                                           corresponding version number only. It takes priority over
                                           --all-versions. If directly specified in positional
                                           argument, use the version number from supplied directory.

     --latest-symlink                      Generates mapfile(s) following latest symlinks only. This
                                           sets the {version} token to "latest" into the mapfile name,
                                           but picked up the pointed version to build the dataset
                                           identifier (if --no-version is disabled).

     --no-version                          Does not includes DRS version into the dataset identifier.

     --no-checksum                         Does not include files checksums into the mapfile(s).

     --filter ".*\.nc$"                    Filter files matching the regular expression (default only
                                           support NetCDF files). Regular expression syntax is defined
                                           by the Python re module.

     --tech-notes-url <url>                URL of the technical notes to be associated with each
                                           dataset.

     --tech-notes-title <title>            Technical notes title for display.

     --dataset <dataset_id>                String name of the dataset. If specified, all files will
                                           belong to the specified dataset, regardless of the DRS.

     --max-threads 4                       Number of maximal threads for checksum calculation.

     --log [$PWD]                          Logfile directory. If not, standard output is used.

     -h, --help                            Show this help message and exit.

     -v                                    Verbose mode.

     -V                                    Program version.

   Developed by:
   Levavasseur, G. (UPMC/IPSL - glipsl@ipsl.jussieu.fr)
   Berger, K. (DKRZ - berger@dkrz.de)
   Iwi, A. (STFC/BADC - alan.iwi@stfc.ac.uk)

Tutorials
---------

To generate a mapfile with verbosity using default parameters:

.. warning:: Default behavior to pickup the latest version in the DRS is ensured with a date version format (e.g., v20151023).

.. code-block:: bash

   $> esgscan_directory /path/to/scan --project PROJECT -v
   ==> Scan started
   dataset_ID1.vYYYYMMDD <-- /path/to/scan/.../vYYYYMMDD/.../file1.nc
   dataset_ID2.vYYYYMMDD <-- /path/to/scan/.../vYYYYMMDD/.../file2.nc
   dataset_ID3.vYYYYMMDD <-- /path/to/scan/.../vYYYYMMDD/.../file3.nc
   Delete temporary directory /tmp/tmpzspsLH
   ==> Scan completed (3 files)

   $> cat dataset_ID.v*.map
   dataset_ID1.vYYYYMMDD
   dataset_ID1.vYYYYMMDD | /path/to/scan/.../vYYYYMMDD/.../file1.nc | size1 | mod_time1 | checksum1 | checksum_type=SHA256

   dataset_ID2.vYYYYMMDD.map
   dataset_ID2.vYYYYMMDD | /path/to/scan/.../vYYYYMMDD/.../file2.nc | size2 | mod_time2 | checksum2 | checksum_type=SHA256

   dataset_ID3.vYYYYMMDD.map
   dataset_ID3.vYYYYMMDD | /path/to/scan/.../vYYYYMMDD/.../file3.nc | size3 | mod_time3 | checksum3 | checksum_type=SHA256

To generate a mapfile without files checksums:

.. note:: The ``-v`` raises the tracebacks of thread-processes (default is the "silent" mode).

.. warning:: The ``--project`` is case-sensitive.

.. code-block:: bash

   $> esgscan_directory /path/to/scan --project PROJECT --no-checksum
   ==> Scan started
   dataset_ID1.vYYYYMMDD <-- /path/to/scan/.../vYYYYMMDD/.../file1.nc
   dataset_ID2.vYYYYMMDD <-- /path/to/scan/.../vYYYYMMDD/.../file2.nc
   dataset_ID3.vYYYYMMDD <-- /path/to/scan/.../vYYYYMMDD/.../file3.nc
   Delete temporary directory /tmp/tmpzspsLH
   ==> Scan completed (3 files)

   $> cat dataset_ID.v*.map
   dataset_ID1.vYYYYMMDD.map
   dataset_ID1.vYYYYMMDD | /path/to/scan/.../vYYYYMMDD/.../file1.nc | size1 | mod_time1

   dataset_ID2.vYYYYMMDD.map
   dataset_ID2.vYYYYMMDD | /path/to/scan/.../vYYYYMMDD/.../file2.nc | size2 | mod_time2

   dataset_ID3.vYYYYMMDD.map
   dataset_ID3.vYYYYMMDD | /path/to/scan/.../vYYYYMMDD/.../file3.nc | size3 | mod_time3

To generate a mapfile without DRS versions:

.. code-block:: bash

   $> esgscan_directory /path/to/scan --p PROJECT --no-version
   ==> Scan started
   dataset_ID1.vYYYYMMDD <-- /path/to/scan/.../vYYYYMMDD/.../file1.nc
   dataset_ID2.vYYYYMMDD <-- /path/to/scan/.../vYYYYMMDD/.../file2.nc
   dataset_ID3.vYYYYMMDD <-- /path/to/scan/.../vYYYYMMDD/.../file3.nc
   Delete temporary directory /tmp/tmpzspsLH
   ==> Scan completed (3 files)

   $> cat dataset_ID.v*.map
   dataset_ID1.vYYYYMMDD.map
   dataset_ID1 | /path/to/scan/.../vYYYYMMDD/.../file1.nc | size1 | mod_time1 | checksum1 | checksum_type=SHA256

   dataset_ID2.vYYYYMMDD.map
   dataset_ID2 | /path/to/scan/.../vYYYYMMDD/.../file2.nc | size2 | mod_time2 | checksum2 | checksum_type=SHA256

   dataset_ID3.vYYYYMMDD.map
   dataset_ID3 | /path/to/scan/.../vYYYYMMDD/.../file3.nc | size3 | mod_time3 | checksum3 | checksum_type=SHA256

Define mapfile name using tokens:

.. warning:: If ``{dataset_id}`` is not present in mapfile name, then all datasets will be written to a single mapfile, overriding the default behavior of producing ONE mapfile PER dataset.

.. code-block:: bash

   $> esgscan_directory /path/to/scan --project PROJECT --mapfile {dataset_id}.{job_id}
   ==> Scan started
   dataset_ID1.job_id <-- /path/to/scan/.../vYYYYMMDD/.../file1.nc
   dataset_ID2.job_id <-- /path/to/scan/.../vYYYYMMDD/.../file2.nc
   dataset_ID3.job_id <-- /path/to/scan/.../vYYYYMMDD/.../file3.nc
   ==> Scan completed (3 files)

   $> cat dataset_ID*.job_id.map
   dataset_ID1.job_id.map
   dataset_ID1.vYYYYMMDD | /path/to/scan/.../vYYYYMMDD/.../file1.nc | size1 | mod_time1 | checksum1 | checksum_type=SHA256

   dataset_ID2.job_id.map
   dataset_ID2.vYYYYMMDD | /path/to/scan/.../vYYYYMMDD/.../file2.nc | size2 | mod_time2 | checksum2 | checksum_type=SHA256

   dataset_ID3.job_id.map
   dataset_ID3.vYYYYMMDD | /path/to/scan/.../vYYYYMMDD/.../file3.nc | size3 | mod_time3 | checksum3 | checksum_type=SHA256

   $> esgscan_directory /path/to/scan --project PROJECT --mapfile {date}
   ==> Scan started
   date <-- /path/to/scan/.../vYYYYMMDD/.../file1.nc
   date <-- /path/to/scan/.../vYYYYMMDD/.../file2.nc
   date <-- /path/to/scan/.../vYYYYMMDD/.../file3.nc
   ==> Scan completed (3 files)

   $> cat date.map
   dataset_ID1.vYYYYMMDD | /path/to/scan/.../vYYYYMMDD/.../file1.nc | size1 | mod_time1 | checksum1 | checksum_type=SHA256
   dataset_ID2.vYYYYMMDD | /path/to/scan/.../vYYYYMMDD/.../file2.nc | size2 | mod_time2 | checksum2 | checksum_type=SHA256
   dataset_ID3.vYYYYMMDD | /path/to/scan/.../vYYYYMMDD/.../file3.nc | size3 | mod_time3 | checksum3 | checksum_type=SHA256

To specify the configuration directory:

.. code-block:: bash

   $> esgscan_directory /path/to/scan --project PROJECT -i /path/to/configfiles/

To use a logfile (the logfile directory is optional):

.. code-block:: bash

   $> esgscan_directory /path/to/scan --project PROJECT -log /path/to/logdir -v

   $> cat /path/to/logfile/esgmapfiles-YYYYMMDD-HHMMSS-PID.log
   YYYY/MM/DD HH:MM:SS INFO ==> Scan started
   YYYY/MM/DD HH:MM:SS INFO dataset_ID1.vYYYYMMDD <-- /path/to/scan/.../vYYYYMMDD/.../file1.nc
   YYYY/MM/DD HH:MM:SS INFO dataset_ID2.vYYYYMMDD <-- /path/to/scan/.../vYYYYMMDD/.../file2.nc
   YYYY/MM/DD HH:MM:SS INFO dataset_ID3.vYYYYMMDD <-- /path/to/scan/.../vYYYYMMDD/.../file3.nc
   YYYY/MM/DD HH:MM:SS WARNING Delete temporary directory /tmp/tmpzspsLH
   YYYY/MM/DD HH:MM:SS INFO ==> Scan completed (3 files)

To specify an output directory:

.. code-block:: bash

   $> esgscan_directory /path/to/scan --project PROJECT --outdir /path/to/mapfiles/
   ==> Scan started
   dataset_ID1.vYYYYMMDD <-- /path/to/scan/.../vYYYYMMDD/.../file1.nc
   dataset_ID2.vYYYYMMDD <-- /path/to/scan/.../vYYYYMMDD/.../file2.nc
   dataset_ID3.vYYYYMMDD <-- /path/to/scan/.../vYYYYMMDD/.../file3.nc
   Delete temporary directory /tmp/tmpzspsLH
   ==> Scan completed (3 files)

   $> cat /path/to/mapfiles/dataset_ID*.v*.map
   dataset_ID1.vYYYYMMDD.map
   dataset_ID1.vYYYYMMDD | /path/to/scan/.../vYYYYMMDD/.../file1.nc | size1 | mod_time1 | checksum1 | checksum_type=SHA256

   dataset_ID2.vYYYYMMDD.map
   dataset_ID2.vYYYYMMDD | /path/to/scan/.../vYYYYMMDD/.../file2.nc | size2 | mod_time2 | checksum2 | checksum_type=SHA256

   dataset_ID3.vYYYYMMDD.map
   dataset_ID3.vYYYYMMDD | /path/to/scan/.../vYYYYMMDD/.../file3.nc | size3 | mod_time3 | checksum3 | checksum_type=SHA256

To add a mapfile tree to an output directory (i.e., if a ``mapfile_drs`` has been defined):

.. code-block:: bash

   $> esgscan_directory /path/to/scan --project PROJECT --outdir /path/to/mapfiles/
   ==> Scan started
   dataset_ID1.vYYYYMMDD <-- /path/to/scan/.../vYYYYMMDD/.../file1.nc
   dataset_ID2.vYYYYMMDD <-- /path/to/scan/.../vYYYYMMDD/.../file2.nc
   dataset_ID3.vYYYYMMDD <-- /path/to/scan/.../vYYYYMMDD/.../file3.nc
   ==> Scan completed (3 files)

   $> cat /path/to/mapfiles/facet1/facet2/facet3/dataset_ID1.vYYYYMMDD.map
   dataset_ID1.vYYYYMMDD | /path/to/scan/.../vYYYYMMDD/.../file1.nc | size1 | mod_time1 | checksum1 | checksum_type=SHA256

   $> cat /path/to/mapfiles/facet1/facet2/facet3/dataset_ID2.vYYYYMMDD.map
   dataset_ID2.vYYYYMMDD | /path/to/scan/.../vYYYYMMDD/.../file2.nc | size2 | mod_time2 | checksum2 | checksum_type=SHA256

   $> cat /path/to/mapfiles/facet1/facet2/facet3/dataset_ID3.vYYYYMMDD.map
   dataset_ID3.vYYYYMMDD | /path/to/scan/.../vYYYYMMDD/.../file3.nc | size3 | mod_time3 | checksum3 | checksum_type=SHA256


To generate a mapfile walking through *latest* directories only:

.. code-block:: bash

   $> esgscan_directory /path/to/scan --project PROJECT --latest-symlink
   ==> Scan started
   dataset_ID1.latest <-- /path/to/scan/.../latest/.../file1.nc
   dataset_ID2.latest <-- /path/to/scan/.../latest/.../file2.nc
   dataset_ID3.latest <-- /path/to/scan/.../latest/.../file3.nc
   Delete temporary directory /tmp/tmpzspsLH
   ==> Scan completed (3 files)

   $> cat dataset_ID*.latest.map
   dataset_ID1.latest.map
   dataset_ID1.vYYYYMMDD | /path/to/scan/.../latest/.../file1.nc | size1 | mod_time1 | checksum1 | checksum_type=SHA256

   dataset_ID2.latest.map
   dataset_ID2.vYYYYMMDD | /path/to/scan/.../latest/.../file2.nc | size2 | mod_time2 | checksum2 | checksum_type=SHA256

   dataset_ID3.latest.map
   dataset_ID3.vYYYYMMDD | /path/to/scan/.../latest/.../file3.nc | size3 | mod_time3 | checksum3 | checksum_type=SHA256

To generate a mapfile walking through a particular version only:

.. warning:: By default ``esgscan_directory`` pick up the latest version only.

.. note:: Use the ``--all-versions`` flag to generate a mapfile walking through all versions.

.. code-block:: bash

   $> esgscan_directory /path/to/scan --project PROJECT --version 20151104
   ==> Scan started
   dataset_ID1.v20151104 <-- /path/to/scan/.../v20151104/.../file1.nc
   dataset_ID2.v20151104 <-- /path/to/scan/.../v20151104/.../file2.nc
   dataset_ID3.v20151104 <-- /path/to/scan/.../v20151104/.../file3.nc
   Delete temporary directory /tmp/tmpzspsLH
   ==> Scan completed (3 files)

   $> cat dataset_ID*.v20151104.map
   dataset_ID1.v20151104.map
   dataset_ID1.v20151104 | /path/to/scan/.../v20151104/.../file1.nc | size1 | mod_time1 | checksum1 | checksum_type=SHA256

   dataset_ID2.v20151104.map
   dataset_ID2.v20151104 | /path/to/scan/.../v20151104/.../file2.nc | size2 | mod_time2 | checksum2 | checksum_type=SHA256

   dataset_ID3.v20151104.map
   dataset_ID3.v20151104 | /path/to/scan/.../v20151104/.../file3.nc | size3 | mod_time3 | checksum3 | checksum_type=SHA256

.. note:: All the previous examples can be combined safely.
