.. _pid:

PID tracker
===========

This client functionality enables users to query the errata service for issues in specific set of dataset PIDs.
This is the advanced search endpoint, it finds information about all versions of every dataset.
This action requires no authentication nor authentication.

.. code-block:: bash

   $> esgissue check --id your_list_of_dataset_ids (optional --full for full history --latest for only latest)


Flags
************

+----------------------+-----------------------------------------------+
| flag                 | Requirement                                   |
+======================+===============================================+
| ``--id or -i``       | list of dataset ids or file handle strings    |
|                      | Mandatory                                     |
+----------------------+-----------------------------------------------+
| ``--full or -f``     | Full history of queried id (optional)         |
+----------------------+-----------------------------------------------+
| ``--latest or -lat`` | Only returns the latest version (optional)    |
+----------------------+-----------------------------------------------+

.. note::
    This command uses the same api endpoint as the front-end pid search,
    you should expect the same results.

