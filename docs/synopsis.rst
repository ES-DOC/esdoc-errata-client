.. _ESGF: http://pcmdi9.llnl.gov/

.. _synopsis:

Synopsis
========

Proper handling of errata information in the ESGF publication workflow has major impact on the quality of data.
Version changes should be documented and justified by explaining what was updated, retracted and/or removed.
This leads to the unspoken rule that any publication of a newer version of a dataset needs to have a valid motivation,
which we will refer to as an issue.
The cause behind the version changes has to be published alongside the data: what was updated, retracted or removed, and why.
Consequently, the publication of a new version of a dataset has to be motivated by an issue.

``esgissue`` allows the referenced data providers to easily create, document, update, close or remove a validated issue.

``esgissue`` implements a similar issue-management system to GitHub, it is completely hosted within the ES-DOC Errata Service.

The issue registration should be executed prior to the publication process and is ought to be mandatory for additional
versions, version removal or retraction.

``esgissue`` relies on ``json`` and ``txt`` file records. This enables the data provider, in charge of ESGF issues, to
efficiently manage one or several issues remotely and locally.

.. note:: ``esgissue`` allows to:

   i. Create ESGF issues from a ``json`` template to the errata service database,
   ii. Update ESGF issues from a ``json`` template to the errata service database,
   iii. Close ESGF issues on the errata service database,
   iv. Retrieve ESGF issues from the errata service database to a local *json* record.

Features
********

Template as input
  You only need to document your issue following a user-friendly ``json`` template as well as list the affected datasets
  in a ``txt`` file.

Compatibility with ESGF node configuration file(s)
  For the time being, the ESGF errata client is completely independent from the ESGF stack.

Standalone
  The issue client is perfectly capable of running as a stand-alone project.

Output directory
  An output directory can be defined to store and organize your issue templates on command.
  There is no limitation about directories used to locally store issue files.

Use a logfile
  You can initiate a logger instead of the standard output. This could be useful for automatic workflows. The
  logfile name is automatically defined and unique (using the the job's name, the date and the job's ID). You can
  define an output directory for your logs too.
