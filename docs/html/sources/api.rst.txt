.. _api:

Application Programming Interface
=================================

The Errata Service uses various endpoints that can also be used by third party software to use the features that the errata has to offer.

Issue Creation
**************

Endpoint used for issue creation. Requires proper authentication and authorization.

Path: ``1/issue/create``

Method: ``post``

Tags: `Issue Management`

Summary: "Create a new issue"

OperationId: "createIssue"

Consumes
--------
- ``application/json``

Produces
--------
- ``application/json``

Parameters
----------
- name: ``body``
- description: "Issue json schema"
- required: ``true``

Responses
---------
401: "Unauthenticated"
403: "Unauthorized"
405: "Bad Method"

Security
--------
- github personal access token: - "org:read"

Issue Update
************

Endpoint used for issue update. Requires proper authentication and authorization.
Local files need to be updated, if tampered with beforehand, they can be downloaded using the retrieve endpoint.

Path: ``1/issue/update``

Method: ``post``

Tags: `Issue Management`

Summary: "Update an issue"

OperationId: "updateIssue"`

Consumes
--------
- ``application/json``

Produces
--------
- ``application/json``

Parameters
----------
- name: ``body``
- description: "Issue json schema"
- required: true

Responses
---------
401: "Unauthenticated"
403: "Unauthorized"
405: "Bad Method"

Security
--------
- github personal access token: - "org:read"

Issue Close
***********

Endpoint used to close an issue marking its lifecycle's end. Requires proper authentication and authorization.

Path: ``1/issue/close``

Method: ``post``

Tags: `Issue Management`

Summary: "closes an issue"

OperationId: "closeIssue"

Consumes
--------
- ``application/json``

Produces
--------
- ``application/json``

Parameters
----------
- name: ``body``
- description: "Issue json schema"
- required: true

Responses
---------
401: "Unauthenticated"
403: "Unauthorized"
405: "Bad Method"

Security
--------
- github personal access token: - "org:read"

Issue Retrieve
**************

This endpoint serves as download endpoint for issue local files (e.g. the issue.json and datasets.txt)
This endpoint requires no authentication nor authentication.

Path: ``1/issue/retrieve``

Method: ``get``

Tags: `Issue Management`

Summary: "Downloads issue files"

OperationId: "retrieveIssue"

Consumes
--------
- param: ``uid``

Produces
--------
- ``application/json``

Parameters
----------
- name: ``uid``
- description: "list of uids to download"
- required: false

Responses
---------
405: "Bad Method"

PID Tracker
***********

This endpoint enables users to query the errata service for issues in specific set of dataset PIDs.
This is the advanced search endpoint, it seeks information about all versions of every dataset.
This endpoint requires no authentication nor authentication.

Path: ``1/resolve/pid``

Method: ``get``

Tags: `Issue Management`

Summary: "Checks dataset (and entire version history) for issues "

OperationId: "pidSearch"

Consumes
--------
- param: ``pids``

Produces
--------
- ``application/json``

Parameters
----------
- name: ``pids``
- description: List of pid handle strings, dataset ids with '.v' as seperator for version or '%23' the percent-encoding for '#'. The list separator is a comma ','
- required: true

Responses
---------
405: "Bad Method"


Example of usage
----------------
GET https://errata.es-doc.org/1/resolve/pid?pids=list_of_pids

Simple-PID search
*****************

This endpoint enables users to query the errata service for issues in specific set of dataset PIDs.
This is the simple response version of the pid endpoint, only the queried versions will be inspected.
This endpoint requires no authentication nor authentication.

Path: ``1/resolve/simple-pid``

Method: ``get``

Tags: `Issue Management`

Summary: "checks dataset for issues"

OperationId: "simplePidSearch"

Consumes
--------
- param: ``datasets``

Produces
--------
- ``application/json``

Parameters
----------
- name: ``datasets``
- description: Dataset string list seperated with a comma ','. Can also be list of PIDs, or a mixed list of datasets and PID handle strings. This endpoint returns a simpler return than the PID endpoint. It does not provide version history. Due to URL encoding restriction, the '#' character is reserved and should be replaced by either '.v' or '%23' which is the percent-encoding of the '#' character as specified in the rfc3986.
- required: true

Responses
---------
405: "Bad Method"

Example of usage
----------------
GET https://errata.es-doc.org/1/resolve/simple-pid?datasets=dataset_ids
