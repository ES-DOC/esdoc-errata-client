.. _create:

Create an issue
===============

Issue creation is the first step in the issue life cycle and is a vital part of the errata service as it revolves around community contributions. However, creating an issue must abide to a set of rules.

#. :ref:`Log in to the Errata Service <login>`

#. From the `Errata Service home page <https://errata.es-doc.org/>`_, click on "**Create**" in the upper-right menu.

    .. image:: images/create_button.png
        :scale: 70 %
        :alt: Create Issue Form
        :align: center

#. Fill the form following the requirements:

    - The project is mandatory and value-controlled.
    - A title between 16 and 255 characters is mandatory.

        .. warning::
            You won't be able to change the project and the title again !

    - A description between 16 and 1023 characters is mandatory. A precise and concise issue description that must make sense for end users (not just “wrong data”) is highly recommended.
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

    - Optional links and materials are expected to be a valid URL(s) (checked upon validation).
    - The datasets list is mandatory and gathers all the identifiers of the affected datasets.

        .. note::
            A dataset identifier is a sequence of dot-separated facets that follows the *Data Reference Syntax* of the corresponding project.
            The dataset identifiers has to append the dataset version number. If one of the dataset ID is malformed or if the dataset list is empty, the form will raise an error.

    .. image:: images/create_form.png
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
    The Errata Service will automatically assign the status "**New**".

.. note::
    The Errata Service automatically generates a unique identifier on issue creation and assigns to the issue throughout its life cycle.
    This identifier can be use to retrieve the issue through :ref:`the Errata Service CLI <client>`.

.. note::
    The creation date and authors are also automatically assigned to the issue by the server.
