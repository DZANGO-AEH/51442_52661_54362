# OnlyVans: 51442_52661_54362
![Python version](https://img.shields.io/badge/python-3.10.x-blue.svg)
![Django version](https://img.shields.io/badge/django-5.x-orange.svg)
![License](https://img.shields.io/badge/license-MIT-green)
![Build](https://img.shields.io/badge/work%20in-progress-yellow)

**The aim of this project is to create a platform similar to OnlyFans**, which allows content creators to share unique materials with their subscribers. The project is built using the Django framework and is intended for educational/development purposes.
## Functions 🌟
- user authentication
- adding posts with images and/or videos
- profile editing
- setting tier prices
- subscription to other users
- sending messages to other users
- Stripe payment integration
- user search

## Technologies 🛠
- [Django](https://www.djangoproject.com/)
- [Bootstrap 5.3](https://getbootstrap.com/)
- [Bootswatch](https://bootswatch.com/)
- [Crispy Forms](https://django-crispy-forms.readthedocs.io/en/latest/)
- [Pillow](https://pillow.readthedocs.io/en/stable/)

## Prerequisites 📋
Make sure you have Python version 3.10.x and pip installed. The project has been tested on Linux, Windows, and macOS operating systems.

## Installation 🔧
To run this project locally, follow these steps.
### Cloning the repository
```bash
git clone https://github.com/DZANGO-AEH/51442_52661_54362.git
```
```bash
cd  51442_52661_54362
```
### Creating and activating a virtual environment
For Windows:
```bash
python -m venv venv
```
```bash
.\venv\Scripts\activate
```
For Unix/Linux/macOS systems:
```bash
python3 -m venv venv
```
```bash
source venv/bin/activate
```
### Installing dependencies
```bash
pip install -r requirements.txt
```
### Database migrations
```bash
cd onlyvans
```
```bash
python manage.py makemigrations
```
```bash
python manage.py migrate
```
### Starting the development server
```bash
python manage.py runserver
```
The project should be available at http://127.0.0.1:8000/.

## License 📄

This project is licensed under the MIT License. Detailed information can be found in the [LICENSE](LICENSE) file.