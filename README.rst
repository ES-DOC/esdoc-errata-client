********
esgissue
********

`See full documentation here <http://es-doc.github.io/esdoc-errata-client>`_

Description
-----------

ESGF errata client is a piece of software that enables the interaction
with the errata service. It can be used to create, update, close and
retrieve issues. The client is basically aimed to be used by publishing
teams that are notified of the existence of an issue regarding one or
many datasets/files.

Installation
------------

To install the esgf errata client, you can either clone the `GitHub
repository`_ or use pip using the command
``pip install esgf-errata-client`` .

After installing, in order to set the work environment run the following
command in the project’s directory: ``source activate`` .

How To Use
----------

1. Creating an issue :
^^^^^^^^^^^^^^^^^^^^^^

the errata issue manager enables users to create an issue related to a
number of datasets using the command:

``issue-client create --issue path/to/issue.json --dsets path/to/datasets.txt``

This will request an issue creation from the errata server and if
accepted, it will be added to the errata db.

The json file needs to contain specific fields that are detailed in the
user manuel.

The txt file is just a listing of affected datasets seperated by break
lines.

On success, the local files will also be updated in accordance with the
remote issue. #### 2. Updating an issue : If something changes about the
issue, the errata client enables users to modify the contents using the
update command:

``issue-client update --issue path/to/issue.json --dsets path/to/datasets.txt``

Similar to the creation process, it suffices to update the local records
of the issue to have it updated remotely.

Also like in the creation process, on success this will update the local
files.

Some fields cannot be updated in order to preserve the authenticity of
information. #### 3. Closing an issue : If the issue is properly handled
or has just been acknowledged and won’t be fixed, the proper course of
action would be to close the issue, which is made possible by the close
command:

``issue-client close --issue path/to/issue.json --dsets path/to/datasets.txt``

Special care needs to be applied to the status field of issue, as a
matter of fact if the issue status is on hold or the update is
suggesting the issue should go back to new status from a different
status, the request will be rejected.

Like both previous operations, this will update local files.

4. Retrieving an issue :
^^^^^^^^^^^^^^^^^^^^^^^^

If one needs to create a local archive of remote issues or needs a
specific issue to update or close, it is possible to download the issue
files (e.g. issue.json, dsets.txt) via the retrieve command:

``issue-client retrieve --issues /path/to/director/or/file --dsets  /path/to/director/or/file --uid <list of uids>``

This will download the issue file or files depending on the list. In
case of a single uid, a json and txt file would be sufficient for the
command to operate, however in the case of multiple uids input, a
directory should be indicated, the file names will have the structure
issue\_.json and dset\_.txt.

.. _GitHub repository: http://github.com/ES-DOC/esdoc-errata-client