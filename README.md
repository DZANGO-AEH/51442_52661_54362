﻿    # OnlyVans: 51442_52661_54362
![Python version](https://img.shields.io/badge/python-3.12.x-blue.svg)
![Django version](https://img.shields.io/badge/django-5.0.x-orange.svg)
![License](https://img.shields.io/badge/license-MIT-green)
![Build](https://img.shields.io/badge/work%20in-progress-yellow)

## Trello

- [Click here, not a virus, 100% legit](https://trello.com/b/9cKGJyUt/onlyvans)

**The aim of this project is to create a platform similar to OnlyFans**, which allows content creators to share unique materials with their subscribers. The project is built using the Django framework and is intended for educational/development purposes.
## Features 🌟
- **User Authentication**: Secure login and registration processes.
- **Post Creation**: Add posts with images and/or videos.
- **Profile Editing**: Update and manage user profiles.
- **Tier Pricing**: Set and manage subscription tier prices.
- **User Subscriptions**: Subscribe to content from other users.
- **Messaging**: Send messages directly to other users.
- **Payment Integration**: Seamlessly integrate with Stripe for payments.
- **User Search**: Efficiently search for other users.

## Technologies 🛠
- [Django](https://www.djangoproject.com/)
- [Bootstrap 5.3](https://getbootstrap.com/)
- [Bootswatch](https://bootswatch.com/)
- [Crispy Forms](https://django-crispy-forms.readthedocs.io/en/latest/)
- [Crispy Bootstrap5](https://pypi.org/project/crispy-bootstrap5/)
- [Pillow](https://pillow.readthedocs.io/en/stable/)
- [Stripe](https://stripe.com/)
- [Sphinx Documentation](https://www.sphinx-doc.org/en/master/)
- [PostgreSQL](https://www.postgresql.org/)

## Prerequisites 📋
Make sure you have Python version 3.12 and pip installed. The project has been tested on Linux, Windows, and macOS operating systems.

## Installation 🔧

This project is Dockerized, so you can run it using Docker or Docker Compose. Follow these steps to run the project using Docker Compose.

### Cloning the repository
```commandline
git clone https://github.com/DZANGO-AEH/51442_52661_54362.git
```

```commandline
cd 51442_52661_54362
```

### Using Docker Compose
```commandline
docker-compose up
```
The project should be available at http://127.0.0.1:8000/

---

If you want to run the project without Docker, follow these steps after cloning the repository.

### Creating and activating a virtual environment
For Windows:
```commandline
python -m venv venv
```
```commandline
.\venv\Scripts\activate
```
For Unix/Linux/macOS systems:
```commandline
python3 -m venv venv
```
```commandline
source venv/bin/activate
```
### Installing dependencies
```commandline
pip install -r minimal-requirements.txt
```
### Database migrations
```commandline
cd onlyvans
```
Just remember to change database settings in `./onlyvans/settings.py` to use SQLite or a different database of your choice.

```commandline
python manage.py makemigrations
```
```commandline
python manage.py migrate
```
### Starting the development server
```commandline
python manage.py runserver
```
The project should be available at http://127.0.0.1:8000/.

## License 📄

This project is licensed under the MIT License. Detailed information can be found in the [LICENSE](LICENSE) file.
