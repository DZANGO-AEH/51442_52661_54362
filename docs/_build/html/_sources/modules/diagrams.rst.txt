================================================
Database choice and diagrams
================================================

This application is divided into several apps, each one with its own set of models and views. The following diagrams show the class diagram for each app.
Application uses PostgreSQL as a main database, and SQLite for testing purposes.

PostgreSQL was selected as the primary database for several reasons:

1. **Reliability**: PostgreSQL is known for its stability and robustness, making it a reliable choice for managing critical data.
2. **Feature-Rich**: It offers a rich set of features, including support for advanced data types, full-text search, and powerful indexing capabilities.
3. **Scalability**: PostgreSQL can efficiently handle large volumes of data and high-concurrency workloads, ensuring the application can scale as needed.
4. **Standards Compliance**: It adheres to SQL standards, which promotes compatibility and eases the integration with other systems.
5. **Community Support**: PostgreSQL has a strong, active community that contributes to its continuous improvement and provides extensive documentation and support resources.
6. **Open Source**: As an open-source database, PostgreSQL offers cost-effectiveness without compromising on quality and features.

SQLite was chosen for testing purposes due to its simplicity and ease of use. It is a lightweight, serverless database that can be easily set up and used for testing purposes. SQLite is well-suited for testing because it runs in-memory and does not require any configuration, making it convenient for running tests quickly and efficiently.

The following diagrams illustrate the model structure of each app in the project:

Account App Class Diagram
------------------------------------------------------------------------

.. image:: ./img/account-class-diagram.svg
   :alt: Account Class Diagram
   :width: 100%
   :align: center


Client App Class Diagram
------------------------------------------------------------------------

.. image:: ./img/client-class-diagram.svg
   :alt: Client Class Diagram
   :width: 100%
   :align: center


Creator App Class Diagram
------------------------------------------------------------------------

.. image:: ./img/creator-class-diagram.svg
   :alt: Creator Class Diagram
   :width: 100%
   :align: center


Finances App Class Diagram
------------------------------------------------------------------------

.. image:: ./img/finances-class-diagram.svg
   :alt: Finances Class Diagram
   :width: 100%
   :align: center

Interactions App Class Diagram
------------------------------------------------------------------------

.. image:: ./img/interactions-class-diagram.svg
   :alt: Interactions Class Diagram
   :width: 100%
   :align: center

Project Class Diagram
------------------------------------------------------------------------

.. image:: ./img/onlyvans-class-diagram.svg
   :alt: Whole System Class Diagram
   :width: 100%
   :align: center


Project Class Diagram (App Specific)
------------------------------------------------------------------------
.. image:: ./img/onlyvans-er-diagram.svg
   :alt: Whole System Class Diagram
   :width: 100%
   :align: center