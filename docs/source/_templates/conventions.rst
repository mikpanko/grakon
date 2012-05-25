.. _ref-conventions:

Conventions for developers
==========================

Backend
~~~~~~~

Code styling
------------
    * Use 4 space indentation, no tabulations
    * Line length **can exceed** 80 symbols if it makes sence

Database migration
------------------
`South`_ is used for database migration.

Adding new application::

    python manage.py schemamigration app --initial

Changing models in existing application::

    python manage.py schemamigration app --auto

Performing migration::

    python manage.py migrate

TODO: migration of custom fields

Using new libraries
-------------------

If library can be installed using pip, it should be added to deployment/requirements.txt.
Otherwise deployment/fabfile.py must be modified.

Front-end
~~~~~~~~~

Django template system documentation
------------------------------------
* `Syntax overview`_
* `Built-in tags and filters`_

Templates
---------
    
* use {{ ADMIN_EMAIL }} instead of admin@grakon.org as our contact email
* use {{ URL_PREFIX }} instead of http://grakon.org
* {{ SLOGAN }} - "Гражданский контроль за работой властей"
* {{ STATIC_URL }} instead of /static/
* Use 4 space indentation, no tabulations

Images
------

* Use dashes in names
* Use sprites to minimize the number of images

CSS
---
* Group styles by page/part of page and label groups with comments

Javascript
----------
* use jQuery, jQuery UI

.. _Syntax overview: https://docs.djangoproject.com/en/1.4/topics/templates/
.. _Built-in tags and filters: https://docs.djangoproject.com/en/1.4/ref/templates/builtins/
.. _South: http://south.aeracode.org/
