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

Example of usage:
-----------------

https://errata.es-doc.org/1/issue/retrieve?uid=4398be50-66d0-42f3-81a3-033e92e64c5e


Pid search
**********

This endpoint enables users to query the errata service for issues in specific set of dataset PIDs.
This is the advanced search endpoint, it seeks information about all versions of every dataset.
This endpoint requires no authentication nor authentication.

Path: ``1/resolve/pid``
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

Example of usage
----------------

Retrieving entire version history of a specific dataset:

https://errata.es-doc.org/1/resolve/pid?pids=CMIP6.DAMIP.NASA-GISS.GISS-E2-1-G.hist-sol.r1i1p1f1.AERmon.bldep.gn.v20180912,CMIP6.DAMIP.NASA-GISS.GISS-E2-1-G.hist-sol.r1i1p1f1.AERmon.bldep.gn.v20181001,CMIP6.DAMIP.NASA-GISS.GISS-E2-1-G.hist-sol.r1i1p1f1.AERmon.bldep.gn.v20181101

Retrieving entire version history of a multiple datasets (identifiers are seperated using a comma):

https://errata.es-doc.org/1/resolve/pid?pids=CMIP6.DAMIP.NASA-GISS.GISS-E2-1-G.hist-sol.r1i1p1f1.AERmon.bldep.gn.v20180912,CMIP6.DAMIP.NASA-GISS.GISS-E2-1-G.hist-sol.r1i1p1f1.AERmon.bldep.gn.v20181001,CMIP6.DAMIP.NASA-GISS.GISS-E2-1-G.hist-sol.r1i1p1f1.AERmon.bldep.gn.v20181101,CMIP6.ScenarioMIP.NIMS-KMA.KACE-1-0-G.ssp245.r1i1p1f1.day.tasmax.gr#20191227

It is also possible to use the pid string instead of the dataset identifier, this is the only way to query a file
instead of a dataset. The query structure remains the same.

Simple-Pid search
*****************

This endpoint enables users to query the errata service for issues in specific set of dataset PIDs.
This is the simple response version of the pid endpoint, only the queried versions will be inspected.
This endpoint requires no authentication nor authentication.

Path: ``1/resolve/simple_pid``
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

Example of usage
----------------
Retrieving errata information regarding a single version of a specific dataset:

https://errata.es-doc.org/1/resolve/simple-pid?datasets=CMIP6.DAMIP.NASA-GISS.GISS-E2-1-G.hist-sol.r1i1p1f1.AERmon.bldep.gn.v20180912

Retrieving errata information regarding a single version of a multiple datasets (identifiers are seperated using a comma):

https://errata.es-doc.org/1/resolve/simple-pid?datasets=CMIP6.DAMIP.NASA-GISS.GISS-E2-1-G.hist-sol.r1i1p1f1.AERmon.bldep.gn.v20180912,CMIP6.DAMIP.NASA-GISS.GISS-E2-1-G.hist-sol.r1i1p1f1.AERmon.bldep.gn.v20181001,CMIP6.DAMIP.NASA-GISS.GISS-E2-1-G.hist-sol.r1i1p1f1.AERmon.bldep.gn.v20181101

It is also possible to use the pid string instead of the dataset identifier, this is the only way to query a file
instead of a dataset. The query structure remains the same.