.. _usage:


Generic usage
=============

Check the help
**************

.. code-block:: bash

    $> esgissue -h
    $> esgissue SUBCOMMAND -h

Check the version
*****************

.. code-block:: bash

    $> esgissue -v

Use a logfile
*************

All information are logged into a file named ``esgissue-YYYYMMDD-HHMMSS-PID.log`` only if ``--log`` is submitted.
If not, the standard output is used following the verbose mode.
By default, the logfiles are stored in your current working directory.
It can be changed by adding a optional logfile directory to the flag.

.. code-block:: bash

    $> esgissue SUBCOMMAND --log
    $> esgissue SUBCOMMAND --log /PATH/TO/LOGDIR/

Exit status
***********

- [0]: Successful execution of the requested operation,
- [1]: Missing or invalid title in issue json file,
- [2]: Missing or invalid description in issue json file,
- [3]: Missing or invalid datasets in issue json file,
- [4]: Missing or invalid severity in issue json file,
- [5]: Missing or invalid project (mip era) in issue json file,
- [6]: Missing or invalid models (source id) in issue json file,
- [7]: Missing or invalid status in issue json file (status should be one of [new, onhold, wontfix, resolved]),
- [8]: Missing or invalid institute (institution id) in issue json file,
- [9]: Missing or invalid materials in issue json file,
- [10]: Missing or invalid urls in issue json file,
- [11]: Missing or invalid id (uid) in issue json file (do not attempt to tamper with already generated uids download a fresh copy of issue files if necessary),
- [12]: Missing or invalid creation date (creation date should not be altered, download fresh copy of local issue files if necessary),
- [13]: Missing or invalid update date (update date should not be altered, download fresh copy of local issue files if necessary),
- [14]: Missing or invalid close date (close date should not be altered, download fresh copy of local issue files if necessary).
- [15]: Incoherent dataset id with project drs structure, please make sure both are coherent.
- [16]: Multiple facet declaration in issue creation/update not permitted (e.g. multiple institutes detected)
- [17]: Authentication failed. Make sure the credentials are correct.
- [18]: User lacks required privilege. Make sure you're part of the institute's errata publication team on github. Contact admins for further information.
- [19]: Connection failed, server probably down. Contact admins.
- [20]: Connection timed out, try again later.
- [21]: Multiple issue ids were provided along with a single file destination, aborting.
- [22]: Json file validation failed for an unknown reason, please check said file.
- [23]: Command is unknown, check the documentation or help for further information
- [24]: WS request failed for unknown reason.
- [25]: Field only supports single input per issue declaration.
- [26]: Project indicated in issue is not supported by errata service.
- [27]: A dataset list is required for either creation or update operation. This message also shows in case user tries to close an issue by indicating an empty dataset file.
- [28]: Dataset malformed and doesn't comply to the expected regex.
- [29]: Facet type not recognized by the selected project configuration.
- [30]: Facet value not recognized by the selected project configuration.
- [31]: Errata servers are down or under maintenance.
- [99]: An unexpected error has caused the task to fail. Check the error message for fix and/or contact the developers.

