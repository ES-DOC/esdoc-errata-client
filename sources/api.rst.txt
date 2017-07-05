.. _configuration:

ESDoc-ERRATA API
================

The ``esdoc-errata-client`` uses various endpoints that can also be used by third party software to use the features that
the ESDoc-ERRATA project has to offer.

Issue Creation
**************

Endpoint used for issue creation. Requires proper authentication and authorization.

Path: ``1/issue/create``
Method: ``post``
tags: "Issue Management"
summary: "Create a new issue"
operationId: "createIssue"
consumes:

- ``application/json``

produces:

- ``application/json``

parameters: in ``body``:

- name: ``body``

- description: "Issue json schema"

- required: ``true``

responses:

401: "Unauthenticated"
403: "Unauthorized"
405: "Bad Method"

security:

- github personal access token: - "org:read"


Issue Update
************

Endpoint used for issue update. Requires proper authentication and authorization.
Local files need to be updated, if tampered with beforehand, they can be downloaded using the retrieve endpoint.


Path: ``1/issue/update``
Method: ``post``
tags: "Issue Management:"
summary: "Update an issue"
operationId: "updateIssue"
consumes:

- ``application/json``

produces:

- ``application/json``

parameters: in ``body``:

- name: ``body``

- description: "Issue json schema"

- required: true

responses:

401: "Unauthenticated"
403: "Unauthorized"
405: "Bad Method"
security:

- github personal access token: - "org:read"


Issue Close
***********

Endpoint used to close an issue marking its lifecycle's end. Requires proper authentication and authorization.


Path: ``1/issue/close``
Method: ``post``
tags: "Issue Management:"
summary: "closes an issue"
operationId: "closeIssue"
consumes:

- ``application/json``

produces:

- ``application/json``

parameters: in ``body``:

- name: ``body``

- description: "Issue json schema"

- required: true

responses:

401: "Unauthenticated"
403: "Unauthorized"
405: "Bad Method"
security:

- github personal access token: - "org:read"

Issue Retrieve
**************

This endpoint serves as download endpoint for issue local files (e.g. the issue.json and datasets.txt)
This endpoint requires no authentication nor authentication.


Path: ``1/issue/retrieve``
Method: ``get``
tags: "Issue Management:"
summary: "downloads issue files"
operationId: "retrieveIssue"
consumes:

- param: ``uid``

produces:

- ``application/json``

parameters: in ``url``:

- name: ``uid``

- description: "list of uids to download"

- required: false

responses:

405: "Bad Method"


Pid search
**********

This endpoint enables users to query the errata service for issues in specific set of dataset PIDs.
This is the advanced search endpoint, it seeks information about all versions of every dataset.
This endpoint requires no authentication nor authentication.

Path: ``1/issue/pid``
Method: ``get``
tags: "Issue Management:"
summary: "checks dataset (and entire version history) for issues "
operationId: "pidSearch"
consumes:

- param: ``pids``

produces:

- ``application/json``

parameters: in ``url``:

- name: ``pids``

- description: "list of uids to download"

- required: false

responses:

405: "Bad Method"


Simple-Pid search
*****************

This endpoint enables users to query the errata service for issues in specific set of dataset PIDs.
This is the simple response version of the pid endpoint, only the queried versions will be inspected.
This endpoint requires no authentication nor authentication.

Path: ``1/issue/simple_pid``
Method: ``get``
tags: "Issue Management:"
summary: "checks dataset for issues"
operationId: "simplePidSearch"
consumes:

- param: ``pids``

produces:

- ``application/json``

parameters: in ``url``:

- name: ``pids``

- description: "list of uids to download"

- required: false

responses:

405: "Bad Method"
