.. _login:


Log in to the Errata Service
============================

An issue on the ESGF data can be detected by any data user or any actor of ESGF community.
This issue has to be reported to the appropriate data provider.
To that end, most of the ESGF netCDF files have a ``contact`` attribute with the email of the corresponding climate modeling group.
If not exists please use the usual `ESGF users mailing list <esgf-user@lists.llnl.gov>`_.

The issue will then be validate from a scientific point of view before its registration into the Errata Service.
Thus, only identified and authorized actors of the corresponding modeling groups can create, update and close issues.

Authentication requires a verified (by email) GitHub account.
Authorization is controlled using GitHub's organizations invitational based structure.
The ES-DOC-ERRATA officers (designated in each group) and administrators are the only persons qualified to add GitHub users to the requested teams.
For the authorization, a user needs to be part of the organization team specified for the institute and the project he/she on behalf of which wishes to publish issues.


#. Sign up on `GitHub <https://github.com/>`_ platform.

    .. image:: images/github.png
        :scale: 70 %
        :alt: Github's home page
        :align: center

#. Please ask to your ES-DOC officer or the ES-DOC :ref:`administrators <credits>` to add your GitHub username to the appropriate GitHub organization team(s). Don't forget to provide the institute(s) and the project(s) on behalf of which you wish to publish issues.

#. Go on `Errata Service home page <https://errata.es-doc.org/>`_.

#. Click on "**Login**" in the upper-right menu?

    .. image:: images/login_button.png
        :scale: 70 %
        :alt: Errata Menu
        :align: center

#. You are requested to sign in to GitHub to authenticate on the Errata Service.

    .. warning::
        At this step you implicitly accept that ES-DOC Errata access to the list of GitHub's organisations (only) which you are associated.

#. Enter your GitHub username and password and click on "**Sign in**".

    .. image:: images/github_auth.png
        :scale: 40 %
        :alt: GitHub Authentication
        :align: center

#. You are redirected to the `Errata Service home page <https://errata.es-doc.org/>`_.

#. You can now create a new issue.

    .. image:: images/create_button.png
        :scale: 70 %
        :alt: Errata Menu
        :align: center

#. Or click on one of your issue in the table to edit it.

    .. image:: images/edit_button.png
        :scale: 70 %
        :alt: Errata Menu
        :align: center
