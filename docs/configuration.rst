.. _configuration:


Authentication
==============

Authentication is key to an optimal use of ``esgissue`` features.

GitHub setup
************

A verified GitHub account is required, as well as a personal access token generated through `your GitHub profile setting page <https://github.com/settings/profile>`_.

1. Go on the bottom of the left menu to access to "Developer Settings":

.. image:: settings.png
   :scale: 70 %
   :alt: Github's personal settings
   :align: center

2. Click on "Personal Access Token":

.. image:: developer_settings.png
   :scale: 70 %
   :alt: Github's developer settings
   :align: center

3. Click on "Generate new token"

.. image:: generate_token.png
   :alt: Github's developer settings
   :align: center

4. Generate your token

.. image:: token_generation.png
   :scale: 50 %
   :alt: Github's personal access token generation interface
   :align: center

Make sure you associate a meaningful name and description for your newly generated token, to help you manage your tokens.

.. image:: token_name.png
   :alt: Github's personal access token generation interface
   :align: center

The next important step is to set the minimum required scope for your personal access token: ``orgs:READ``.
Limiting the number of scopes increases the security of your own personal data associated with your github account.

.. image:: token_scope.png
   :alt: Github's personal access token generation interface
   :align: center

The authentication part is set by creating the personal access token.

Authorization is controlled using GitHub's organizations invitational based structure.
The ES-DOC-ERRATA administrator is the only person qualified to add GitHub users to the requested teams.
For the authorization, a user needs to be part of the organization team specified for the institute and project he/she on behalf of which wishes to publish errata.

Credentials management
**********************

In order to ease the interactions with the ES-DOC-ERRATA web service, a user can save the credentials for recurrent use.
This can be done either through environment variables:

.. code-block:: bash

    $> export ERRATA_CLIENT_GITHUB_TOKEN=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

This will enable the client to retrieve the token whenever the action requires it and stops it from prompting the user to type it in.
However setting the token on environment variables sets it up for grabs in clear text. For this reason an encrypted local file solution is
more encouraged to be employed by users. This file is encrypted using a chosen pass-phrase but it also is valid on the currently used machine only.
In order to generate your token local file:

.. code-block:: bash

    $> esgissue credset

After declaring these credentials, the client will only ask user to provide the pass-phrase from now on.
In case the user forgets the pass-phrase the saved credentials can be reset using the command:

.. code-block:: bash

   $> esgissue credreset

This will obviously result in resetting the saved credentials, and the client will now ask for that information in the next usages.

In the case that the user does recall the pass-phrase and just wishes to modify it, this is possible using the following command:

.. code-block:: bash

   $> esgissue changepass

.. note:: Old and new pass-phrases can be submit on the command-line to avoid the prompt.

In the event of wanting to remove your saved credentials that you have saved on your machine:

.. code-block:: bash

    $> esgissue credremove
