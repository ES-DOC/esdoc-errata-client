.. _ESGF: http://pcmdi9.llnl.gov/

.. _synopsis:

Synopsis
========

The publication workflow on the ESGF nodes requires to deal with errata issues. The background of the version changes
 has to be published alongside the data: what was updated, retracted or removed, and why. Consequently, the
 publication of a new version of a dataset has to be motivated by an issue.

``esgissue`` allows the referenced data providers to easily create, document, update, close or remove a validated issue
 . "esgissue" relies on the GitHub API v3 to deal with private repositories.

 The issue registration always appears prior to the publication process and should be mandatory for additional
 version, version removal or retraction.

``esgissue`` works with both *JSON* and *TXT* files. This allows the data provider in charge of ESGF issues to manage
one or several JSON templates gathering the issues locally.

.. note:: ``esgissue`` allows to:
   i. Create ESGF issues from a *JSON* template to the GitHub repository;
   ii. Update ESGF issues from a *JSON* template to the GitHub repository;
   iii. Close ESGF issues on the GitHub repository;
   iv. Retrieve ESGF issues from the GitHub repository to a *JSON* template.

Features
********

**Template as input**
  You only need to document your issue following a user-friendly *JSON* template.

**Compatiblity with ESGF node configuration file(s)**
  Each `ESGF`_ node:
   * Declares all technical attributes (e.g., the checksum type) into the ``[default]`` of a configuration INI file
   called ``esg.ini``,
   * Centralizes all projects definitions (DRS, facets) into the ``project:<project>`` sections of the same ``esg
   .ini`` or from independent files called ``esg.<project>.ini``.

  To manage only one configuration, ``esgissue`` works from these INI files.

**Standalone**
  Security policies of computing centres, that often host `ESGF`_ nodes, do not allow to use ``esgissue``
  within a node that is conventionally used to generate mapfiles.

**Output directory**
  An output directory can be defined to store and organized your issue templates.

**Use a logfile**
  You can initiate a logger instead of the standard output. This could be useful for automatic workflows. The
  logfile name is automatically defined and unique (using the the job's name, the date and the job's ID). You can
  define an output directory for your logs too.
