.. _api:


ES-DOC-ERRATA API
=================

The ``esdoc-errata-client`` uses various endpoints that can also be used by third party software to use the features that
the ES-DOC-ERRATA project has to offer.

Issue Creation
**************

Endpoint used for issue creation. Requires proper authentication and authorization.

Path: ``1/issue/create``
Method: ``post``
Tags: "Issue Management"
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
Tags: "Issue Management:"
Summary: "Update an issue"
OperationId: "updateIssue"

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
Tags: "Issue Management:"
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
Tags: "Issue Management:"
Summary: "downloads issue files"
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

Pid search
**********

This endpoint enables users to query the errata service for issues in specific set of dataset PIDs.
This is the advanced search endpoint, it seeks information about all versions of every dataset.
This endpoint requires no authentication nor authentication.

Path: ``1/issue/pid``
Method: ``get``
Tags: "Issue Management:"
Summary: "checks dataset (and entire version history) for issues "
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

- description: "list of uids to download"

- required: false

Responses
---------

405: "Bad Method"

Simple-Pid search
*****************

This endpoint enables users to query the errata service for issues in specific set of dataset PIDs.
This is the simple response version of the pid endpoint, only the queried versions will be inspected.
This endpoint requires no authentication nor authentication.

Path: ``1/issue/simple_pid``
Method: ``get``
Tags: "Issue Management:"
Summary: "checks dataset for issues"
OperationId: "simplePidSearch"

Consumes
--------

- param: ``pids``

Produces
--------

- ``application/json``

Parameters
----------

- name: ``pids``

- description: "list of uids to download"

- required: false

Responses
---------

405: "Bad Method"
