# Sunrise Backend FastAPI

A modern FastAPI-based backend for the Sunrise School Management System, migrated from Flask with MongoDB to FastAPI with PostgreSQL.

## Features

- **FastAPI Framework**: Modern, fast web framework for building APIs
- **PostgreSQL Database**: Robust relational database with SQLAlchemy ORM
- **JWT Authentication**: Secure token-based authentication
- **Automatic API Documentation**: Interactive Swagger UI and ReDoc
- **Async/Await Support**: High-performance asynchronous operations
- **Comprehensive Testing**: Full test suite with pytest
- **Database Migrations**: Alembic for database schema management

## Project Structure

flask_rest_api/
│
├── app/
│ ├── init.py # Initialize the Flask app and Swagger
│ ├── models.py # Define data models (if any)
│ ├── routes.py # Define API routes
│
├── venv/ # Virtual environment
├── app.py # Entry point of the application
├── requirements.txt # Project dependencies
├── README.md # Project overview and setup instructions

## Setup Instructions

### Prerequisites

- Python 3.7+
- Virtual environment (`venv`)

### Installation

Clone the repository:

```sh
# Project is already set up as sunrise-backend-fastapi
cd sunrise-backend-fastapi

## Create and activate a virtual environment:

python -m venv venv
.\venv\Scripts\activate   # For Windows
source venv/bin/activate  # For macOS/Linux

## Install the dependencies

pip install -r requirements.txt

## Start the Flask application:
python app.py

Access the Swagger UI for interactive API documentation at http://127.0.0.1:5000/apidocs/
```
