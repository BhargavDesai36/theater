# Django Theater Project

The Django Theater Project is a web application designed to simplify and enhance the management of movie theater operations. This platform offers a comprehensive solution for both theater administrators and moviegoers to interact with and enjoy movie experiences.

## Key Features

- **Movie Listings:** Explore a curated selection of upcoming movies, complete with show times and descriptions.

- **Ticket Booking:** Easily book movie tickets and select seating preferences.

- **Seat Reservations:** Allow users to reserve specific seats for upcoming movies, ensuring a comfortable and personalized movie-watching experience.

- **Admin Dashboard:** Empower administrators to manage movie schedules, seat arrangements, user bookings, and ticket availability.

## Technology Stack

The Django Theater software uses modern web technologies and follows a client-server architecture. The technology stack includes:

- **Back-end:** Python, Django, REST API
- **Database:** PostgreSQL

## API Documentation

This repository contains the backend API for the Django Theater Project. The API, built using Django Rest Framework, provides endpoints for seamless interaction with the movie theater application.

## Features

- User authentication and registration
- Seat Selection
- Movie/show listings and details
- Booking and ticketing system
- User profiles and preferences
- Admin panel for managing content


# Getting Started

### Local Setup

1. **Install pipenv**: Pipenv is a virtual environment manager. Install it using:
    ```bash
    pip install pipenv
    ```
    

2. **Install Dependencies**: Install required packages using pipenv:
    ```bash
    pipenv install
    ```
    Run this command, if you want to install dev packages.
    ```bash
    pipenv install --dev
    ```
    

3. **Database Configuration**: Install PostgreSQL. Reference: PostgreSQL Installation Guide - https://www.postgresql.org/download/

4. **Set Secret Key Value**: In Python Shell, generate a secret key:
    ```bash
    python
    from django.core.management.utils import get_random_secret_key
    print(get_random_secret_key())
    ```
    

5. **Setup Environment File**: Create a `.env` file using `env.example` as a template. Fill in the environment variable values.

6. **Run Database Migrations**:
    ```bash
    pipenv run python manage.py migrate
    ```
    

7. **Creating Superuser**:
    ```bash
    pipenv run python manage.py createsuperuser
    ```
    

8. **Run Development Server**:
    Start the Django development server:
    ```bash
    pipenv run python manage.py runserver
    ```
    

9. **Run Formatter Before Commit**:
    Run the linter and formatter scripts before committing changes:
    ```bash
    scripts/linter.sh
    scripts/formatter.sh
    ```
    
## Using Docker

Docker provides a way to package and distribute applications along with their dependencies as containers. Using Docker ensures that your Django Theater Project runs consistently across different environments, making it easier to set up and deploy.

Here's how you can set up and run your Django Theater Project using Docker:

1. **Install Docker**: If you don't have Docker installed, you can find installation instructions for your specific platform here: Docker Installation Guide

2. **Build and Run Docker Container**:
    - Open a terminal and navigate to the root directory of your Django Theater Project.
    - Run the following command to build and start the Docker container:
      ```bash
      docker-compose up --build
      ```
      
    - This command will pull the necessary Docker images, build your application, and start the Django development server.


3. **Access the Development Server**:
    - Once the Docker container is up and running, you can access your Django Theater Project by opening your web browser and navigating to `http://localhost:8000`

4. **Stopping the Container**:
    - To stop the Docker container, press `Ctrl+C` in the terminal where you started it. This will gracefully stop the development server and shut down the container.

5. **Cleaning Up**:
    - If you want to remove the Docker container and associated images, run the following command:
      ```bash
      docker-compose down
      ```
      
    - This will stop and remove the container, but it won't delete your database data or media files. To remove those as well, you can add the `--volumes` flag:
      ```bash
      docker-compose down --volumes
      ```
      

Using Docker makes it easier to collaborate on your project, ensures consistent development and deployment environments, and allows for better isolation of your application's dependencies.

Keep in mind that Docker commands may vary slightly based on your operating system and Docker setup. Refer to the Docker documentation for more details and options.