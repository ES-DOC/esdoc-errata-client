.. _ESGF: http://pcmdi9.llnl.gov/

.. _synopsis:

Synopsis
========

Proper handling of errata information in the ESGF publication workflow has major impact on the quality of data.
Version changes should be documented and justified by explaining what was updated, retracted and/or removed.
This leads to the unspoken rule that any publication of a newer version of a dataset needs to have a valid motivation,
which we will refer to as an issue.

``esdoc errata client`` allows the referenced data providers to easily create, document, update, close or remove a validated issue
 . esdoc errata client implements a similar issue-management system to github's and is completely hosted within the
 esgf-errata-service.

 The issue registration should be executed prior to the publication process and is ought to be mandatory for additional
 version, version removal or retraction.

``esdoc errata client`` relies on *JSON* and *TXT* file records. This enables the data provider, in charge of ESGF issues, to
efficiently manage one or several issues remotely and locally.

.. note:: ``esdoc errata client`` allows to:
   i. Create ESGF issues from a *JSON* template to the errata service database;
   ii. Update ESGF issues from a *JSON* template to the errata service database;
   iii. Close ESGF issues on the errata service database;
   iv. Retrieve ESGF issues from the errata service database to a local *JSON* record.

Features
********

**Template as input**
  You only need to document your issue following a user-friendly *JSON* template as well as list the affected datasets
  in a *TXT* file.

**Compatiblity with ESGF node configuration file(s)**
  For the time being, the esgf-errata-client is completely independent from the ESGF stack.


**Standalone**
  The issue client is perfectly capable of running as a stand-alone project.


**Output directory**
  An output directory can be defined to store and organize your issue templates on command.
  There's no limitation about directories used to locally store issue files.


**Use a logfile**
  You can initiate a logger instead of the standard output. This could be useful for automatic workflows. The
  logfile name is automatically defined and unique (using the the job's name, the date and the job's ID). You can
  define an output directory for your logs too.
  If not defined by user, the log used is the standard output.