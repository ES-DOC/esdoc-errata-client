.. _configuration:


Configuration
=============

The most important step towards properly configuring and the good use of the esdoc-errata issue client is the authentication part.
A verified github account is required, along with a generated personal access token.

The personal access token can only be generated on github, if the user's account email has been verified.
It can be found under your profile settings page: https://github.com/settings/profile

.. image:: token_generation.png
   :height: 800px
   :width: 1200px
   :scale: 50 %
   :alt: Github's personal access token generation interface
   :align: center

When generating the new token make sure you specify a description that you feel appropriate to the Errata client and to select proper scopes.
Selecting scopes is a crucial part of the token generation, the errata client doesn't require anything beside the read org and team membership scope.
This enables us to reduce to a minimum the potential threats, which is the whole point of delegating authentication to a third party.

.. image:: token_scope.png
    :width: 800px
    :align: center
    :scale: 70 %
    :height: 900px
    :alt: Github's interface of token scopes

Once the access token has been configured, the authentication part of the errata client is ready.
A user needs, however, proper writing rights to be authorized to create, update and close issues.

Authorization is controlled using github's organizations invitational based structure.
In order to publish issues related to a specific institute, you have to be part of the issue publishing team organisation respective to that institute.
After contacting the admins about this matter, the github profile should be invited to the appropriate organization and team.
After accepting the invitation, the user should imperatively make sure his membership is public, otherwise, it's as if he doesn't have the right to be an
errata publisher. To make your membership public, simply follow this link for a guide: https://help.github.com/articles/publicizing-or-hiding-organization-membership/


After successfully creating the personal access token on github, what remains to be done is simply for the convenience of the user.
Two environment variables should be declared by the user to avoid having to insert username and token for each and every operation.
The user must :

.. code-block:: bash

   $>export ERRATA_CLIENT_USERNAME=username
   $>export ERRATA_CLIENT_TOKEN=token


These two variables will be instead used for each operation to ease the task.


