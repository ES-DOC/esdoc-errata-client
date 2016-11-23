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


The esgf-errata-client doesn't require much configuration.
The activate file once sourced will set the environment variables and proper aliases.
The esgf-client.ini file contains some constants required, that might be subject to change in the future.
However constantly updating the file from the project's repository might be the best practice here.


