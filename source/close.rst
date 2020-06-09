.. _close:


Close an issue
==============

At the end of an issue's lifecycle, it should be marked as a closed issue in order to prevent confusion. Closure is a particular step of the :ref:`update <update>` procedure with similar rules.

#. :ref:`Log in to the Errata Service <login>`

#. From the `Errata Service home page <https://errata.es-doc.org/>`_, click on any issue your are authorized to modify on behalf of your institute.

#. The corresponding issue pops up.

#. Click on "**Edit**" in the upper-right menu.

    .. image:: images/edit_button.png
        :scale: 70 %
        :alt: Create Issue Form
        :align: center

#. Use the update form to choose the appropriate status:

    .. note::
        "Resolved"
            The issue has been resolved **AND** the corrected files have been published on ESGF with a new dataset version.
        "Wontfix"
            The issue cannot/won't be fixed by the data provider. This may occur in the following cases:

                - the model should be re-run to correct the issue,
                - an "Low" severity issue without any consequences on the analyzes.

    .. warning::
        The previously explained safeguards for the :ref:`issue update <update>` are also valid in this context.

#. Click on "**Save**" in the upper-right menu.

    .. image:: images/save_button.png
        :scale: 70 %
        :alt: Create Menu
        :align: center

#. Your request will be processed and validated by the server.

#. If successfully saved, you are redirected to the newly generated view of your issue.

    .. image:: images/success.png
        :scale: 50 %
        :alt: Creation Success
        :align: center

#. If invalid issue, you are requested to correct the form depending on the error message and try again.

    .. image:: images/fail.png
        :scale: 50 %
        :alt: Creation Fail
        :align: center

#. The issue is now closed and is kept for archiving/consultation purposes.

.. note::
    The update date and authors are automatically modified to the issue by the server.
