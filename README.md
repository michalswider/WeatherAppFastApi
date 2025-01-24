# **WeatherAppFastApi**

Application for managing users, their favorite cities, and displaying weather data. This project is built with FastAPI, SQLAlchemy and PostgreSQL.

## **Features**
- **User Management**: Add, update, and delete user profiles.
- **Favorite Cities Management**: Add and manage users' favorite cities.
- **Weather Information**:
  - Retrieve current weather data for any city.
  - View weather for a user's favorite cities.
- **Cached Weather Data**:
  - Store previously fetched weather data in the database for faster access.
  - Remove old cached weather data from the database when no longer needed.
- **REST API**: Fully documented API with Swagger UI for easy access and testing.

## **Technologies**
- **FastAPI**: Web framework for building APIs with Python.
- **SQLAlchemy**: SQL toolkit and Object-Relational Mapping (ORM) library.
- **PostgreSQL**: Relational database for storing user data and cities.
- **Uvicorn**: ASGI server for running FastAPI applications.
- **Requests**: Used for integrating with external weather APIs.
- **Pydantic**: For data validation and serialization in FastAPI.
- **Pytest**: Framework for writing unit tests to ensure application reliability and correctness.
- **Docker**: The application is containerized, making it easy to deploy and run in different environments.

  ## **Installation**

  ### **1. Clone the repository:**
   ```bash
   git clone https://github.com/michalswider/WeatherAppFastApi.git
   ```

## **Configuration**

### **1. Using Docker:**
To run the application with Docker, use the provided `compose.yml` file. Build and start the containers with:
   ```bash
   docker-compose up --build
   ```
Upon startup, the FastAPI application will automatically create an `admin` user in the database with the password `admin`.

The application will be available at the following ports:
- **FastAPI**: `http://localhost:8000`
- **pgadmin4**: `http://localhost:8080`

pgAdmin login:
- **Email Address**: `admin@example.com`
- **Password**: `admin`
