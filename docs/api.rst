.. _configuration:

ESDoc-ERRATA API
==============

The esdoc-errata-client uses various endpoints that can also be used by third party software to use the features that
the ESDoc-ERRATA project has to offer.

Issue Creation
**************


Path: 1/issue/create:
Method: post
tags: "Issue Management:"
summary: "Create a new issue"
description: ""
operationId: "createIssue"
consumes:

- "application/json"

produces:

- "application/json"

parameters: in "body":

- name: "body"

- description: "Issue json schema"

- required: true

responses:

401: "Unauthenticated"
403: "Unauthorized"
405: "Bad Method"
security:

- github personal access token: - "org:read"


Issue Update
************

Path: 1/issue/update:
Method: post
tags: "Issue Management:"
summary: "Update an issue"
description: ""
operationId: "updateIssue"
consumes:

- "application/json"

produces:

- "application/json"

parameters: in "body":

- name: "body"

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

Path: 1/issue/close:
Method: post
tags: "Issue Management:"
summary: "closes an issue"
description: ""
operationId: "closeIssue"
consumes:

- "application/json"

produces:

- "application/json"

parameters: in "body":

- name: "body"

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

Path: 1/issue/retrieve:
Method: get
tags: "Issue Management:"
summary: "downloads issue files"
description: ""
operationId: "retrieveIssue"
consumes:

- param: uid

produces:

- "application/json"

parameters: in "url":

- name: "uid"

- description: "list of uids to download"

- required: false

responses:

405: "Bad Method"


Pid search
**********

Path: 1/issue/pid:
Method: get
tags: "Issue Management:"
summary: "checks dataset (and entire version history) for issues "
description: ""
operationId: "pidSearch"
consumes:

- param: pids

produces:

- "application/json"

parameters: in "url":

- name: "pids"

- description: "list of uids to download"

- required: false

responses:

405: "Bad Method"


Simple-Pid search
*****************

Path: 1/issue/simple_pid:
Method: get
tags: "Issue Management:"
summary: "checks dataset for issues"
description: ""
operationId: "simplepidSearch"
consumes:

- param: pids

produces:

- "application/json"

parameters: in "url":

- name: "pids"

- description: "list of uids to download"

- required: false

responses:

405: "Bad Method"
