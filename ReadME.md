# Theater Booking System

A simple and user-friendly theater booking system built with Django. This web application helps manage movie screenings, seat bookings, and theater operations.

## Features

### For Users
- Browse current and upcoming movies
- View movie details and showtimes
- Select and book seats
- View booking history
- User registration and login

### For Theater Staff
- Manage movies and showtimes
- Monitor bookings and seat availability
- View booking statistics
- Handle screen management

## Tech Stack

- Python 3.8+
- Django 4.2
- PostgreSQL
- Bootstrap 5
- JavaScript (Vanilla)

## Setup Guide

### 1. Prerequisites

Make sure you have the following installed:
- Python 3.8 or higher
- PostgreSQL
- pip

### 2. Create Virtual Environment

```bash
# Install pipenv if you haven't already
pip install pipenv

# Create and activate virtual environment
pipenv install
pipenv shell
```

### 3. Database Setup

```bash
# Install PostgreSQL and create database
psql
CREATE DATABASE theater;
```

### 4. Environment Setup

Create a `.env` file in the project root:

```env
DEBUG=True
SECRET_KEY=your-secret-key-here
DB_NAME=theater
DB_USER=your-db-user
DB_PASSWORD=your-db-password
DB_HOST=localhost
DB_PORT=5432
```

To generate a secret key:
```python
python
>>> from django.core.management.utils import get_random_secret_key
>>> print(get_random_secret_key())
```

### 5. Install Dependencies

```bash
# Install project dependencies
pipenv install

# For development, include dev packages
pipenv install --dev
```

### 6. Database Migration

```bash
# Run migrations
python manage.py migrate

# Create admin user
python manage.py createsuperuser
```

### 7. Run Development Server

```bash
python manage.py runserver
```

Visit http://localhost:8000 in your browser.
