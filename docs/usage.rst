.. _usage:

Generic usage
=============

Check the help
**************

.. code-block:: bash

   $> esgissue -h

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

        create     Creates ESGF issues from a json template to the errata database.
                   See "issue-manager create -h" for full help.

        update     Updates ESGF issues from a json template to the errata database.
                   See "issue-manager update -h" for full help.

        close      Closes ESGF issues on the errata repository.
                   See "issue-manager close -h" for full help.

        retrieve   Retrieves ESGF issues from the errata repository to a json template.
                   See "issue-manager retrieve -h" for full help.

        credset    Sets user's credentials.

        credreset  Resets user's credentials.

        changepass Changes the old passphrase into a new one of user's choice.

    Developed by:
    Levavasseur, G. (UPMC/IPSL - glipsl@ipsl.jussieu.fr)
    Bennasser, A. (UPMC/IPSL - abennasser@ipsl.jussieu.fr



Positional arguments:
 command                               One of the four possible actions, create, update, close and retrieve.

Optional arguments:
 --issue                               Issue json file.

 --dsets                               dataset list txt file.

 --log                                 Directory for log output.

 -h, --help                            Show this help message and exit.

 -V                                    Program version.

Exit status
***********

- [0]: Successful execution of the requested task,
- [1]: Missing or invalid title,
- [2]: Missing or invalid description,
- [3]: Missing or invalid datasets,
- [4]: Missing or invalid severity,
- [5]: Missing or invalid project,
- [6]: Missing or invalid models,
- [7]: Missing or invalid status,
- [8]: Missing or invalid institute,
- [9]: Missing or invalid materials,
- [10]: Missing or invalid urls,
- [11]: Missing or invalid id (uid),
- [12]: Missing or invalid creation date,
- [13]: Missing or invalid update date,
- [14]: Missing or invalid close date.
- [15]: Incoherent dataset id with project drs structure, please make sure both are coherent.
- [16]: Multiple facet declaration in issue creation/update not permitted (e.g. multiple institutes detected)
- [17]: Authentication failed. Make sure the credentials are correct.
- [18]: User lacks required privilege. Contact admins for further information.
- [19]: Connection failed, server probably down. Contact admins.
- [20]: Connection timed out, try again later.
- [21]: Multiple issue ids were provided along with a single file destination, aborting.
- [22]: Json file validation failed for an unknown reason, please check said file.
- [23]: Command is unknown, check the documentation or help for further information
- [24]: WS request failed for unknown reason.
- [25]: Field only supports single input per issue declaration.
- [26]: Project indicated in issue is not supported by errata service.
- [27]: A dataset list is required for either creation or update operation. This message also shows in case user tries
to close an issue by indicating an empty dataset file.
- [99]: An unexpected error has caused the task to fail. Check the error message for fix and/or contact the developers.

