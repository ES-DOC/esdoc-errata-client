.. _update:

Update an issue
===============

Once an issue is created, it inevitably will be subject to some changes, whether it regards the content of the issue (description
for instance), its status or the list of affected datasets. Updating an issue is still constrained and validated against some rules.
In fact, to guarantee the issue quality some attributes are immutable.

#. :ref:`Log in to the Errata Service <login>`

#. From the `Errata Service home page <https://errata.es-doc.org/>`_, click on any issue your are authorized to modify on behalf of your institute.

#. The corresponding issue pops up.

#. Click on "**Edit**" in the upper-right menu.

    .. image:: images/edit_button.png
        :scale: 70 %
        :alt: Create Issue Form
        :align: center

#. Update the form following the requirements:

    - The project and the title cannot be changed.
    - A description between 16 and 1023 characters is mandatory.

        .. warning::
            As a matter of fact updating the description is controlled by a variation threshold that should not be exceeded. Which is currently set at 20%, if the description is to be changed more than that, the issue should be closed and the creation of a brand new issue is required.

    - The severity is mandatory and value-controlled.

        .. note::
            The accepted terms for issue severity are:

            "Low"
                The issue concerns file management (e.g., addition, removal, period extension, etc.),
            "Medium"
                The issue concerns metadata (NetCDF attributes) without undermining the values of the involved variable,
            "High"
                The issue concerns single point variable or axis values,
            "Critical"
                The issue concerns the variable or axis values undermining the analysis. The use of this data is strongly discouraged.

    - The status is mandatory and value-controlled.

        .. warning::
            An issue status cannot change back to "**New**".

    - Optional links and materials are expected to be a valid URL(s) (checked upon validation).
    - The datasets list is mandatory and gathers all the identifiers of the affected datasets. Any dataset ID can be add or modify as long as the dataset list isn't empty.

        .. note::
            A dataset identifier is a sequence of dot-separated facets that follows the *Data Reference Syntax* of the corresponding project.
            The dataset identifiers has to append the dataset version number. If one of the dataset ID is malformed or if the dataset list is empty, the form will raise an error.

    .. image:: images/update_form.png
        :scale: 70 %
        :alt: Create Issue Form
        :align: center

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

.. note::
    The update date and authors are also automatically assigned/modified to the issue by the server.
