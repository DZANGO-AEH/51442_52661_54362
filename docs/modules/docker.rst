=====================
Docker Compose
=====================

You can use Docker Compose to easily run the project in a containerized environment.

Just run the following command:

.. code-block:: console

    docker-compose up

To turn off the project, run the following command:

.. code-block:: console

    docker-compose down

The project will be available at http://127.0.0.1:8000/

It would be a good idea to create a superuser to access the Django admin.

.. code-block:: console

    docker-compose run django python manage.py createsuperuser


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
