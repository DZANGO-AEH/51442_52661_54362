=====================
Docker Compose
=====================

You can use Docker Compose to easily run the project in a containerized environment.

Just run the following commands.

First you need to make database migrations.

.. code-block:: console

    docker-compose run django python manage.py makemigrations

.. code-block:: console

    docker-compose run django python manage.py migrate

It would be a good idea to create a superuser to access the Django admin.

.. code-block:: console

    docker-compose run django python manage.py createsuperuser

Then you can start the project.

.. code-block:: console

    docker-compose up


If you don't want to use Docker Compose, you can run the project with the following commands:

.. code-block:: console

    python -m venv venv

    .\venv\Scripts\activate

    pip install -r minimal-requirements.txt

    cd onlyvans

    python manage.py makemigrations

    python manage.py migrate

    python manage.py createsuperuser

    python manage.py runserver
