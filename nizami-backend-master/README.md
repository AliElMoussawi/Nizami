
# Django Project with PostgreSQL and JWT Authentication

## Overview
This project is a Django application that uses **PostgreSQL** as the database and **JWT (JSON Web Tokens)** for authentication. It includes features such as user registration, login, and password reset with email support.

## Requirements
- Python 3.9 or higher
- Docker (for containerized setup)
- PostgreSQL (included in the Docker setup)

## Setup Instructions

### 1. Clone the Repository
First, clone this repository to your local machine:
```bash
git clone https://gitlab.com/XoB/backend_rg.git
cd django_project
```

### 2. Install Python Dependencies
If you are not using Docker, you can install the necessary dependencies using **pip**:
```bash
pip install -r requirements.txt
```

### 3. Set up Environment Variables
Create a `.env` file at the root of your project and add the following environment variables:
```plaintext
SECRET_KEY=your_secret_key
DATABASE_URL=postgres://your_db_user:your_db_password@localhost/your_db_name
EMAIL_HOST_USER=your_email@example.com
EMAIL_HOST_PASSWORD=your_email_password
```

### 4. Set up the Database
Run the following commands to set up the database and apply migrations:
```bash
python manage.py migrate
```

### 5. Run the Development Server
To run the development server, use:
```bash
python manage.py runserver
```

### 6. Docker Setup (Optional)
If you prefer to use Docker, you can run the project in containers.

#### Step 1: Build the Docker containers
```bash
docker-compose up --build
```

#### Step 2: Run the containers
After building the containers, run them:
```bash
docker-compose up
```