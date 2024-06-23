## Introduction

This project is a web-based application called TheaterTainment, designed to emulate the functionalities of Cinemark. TheaterTainment is a theater with a single, unspecified location, offering a comprehensive online experience similar to that of Cinemark.

## Features

- **User authentication and authorization**
    - Login and registration for users.
- **Movie ticket purchases**
    - Users can browse and purchase tickets for available movies.
- **Watchlist management**
    - Members can add movies to their personal watchlist for future viewing.
- **Profile management**
    - Members can update their profile information.
- **Payment options**
    - Members can add and manage a default credit card.
- **Purchase history**
    - Members can view a history of all their purchases.
- **Purchase receipts**
    - Both guests and members can view purchase receipts.
- **Movie management (employee)**
    - Employees can add, delete, update, activate, and inactivate movies available for streaming.
- **Showtime management (employee)**
    - Employees can add movie showtimes.
- **Change tracking (employee)**
    - Employees can view the changes they have made.
- **Theater Auditoriums (Employee)**
    - Employees can view auditoriums in the theater.
- **Ticket Information(employee)**
    - Employees can view purchased tickets' information.

## Installation

1. Clone the repository:
    
    ```
    git clone <https://github.com/mnsrt-pb/TheaterTainment.git>
    ```
    
2. Add a environment file with the following data
    
    ```bash
    TMDB_API_KEY = 'your_api_key_here'
    SECRET_KEY = 'your_secret_key_here'
    EMPLOYEE_KEY = 'your_employee_key_here'
    ```
    
    *Note: EMPLOYEE_KEY is needed to register employees*
    
3. Navigate to the project directory:
    
    ```
    cd TheaterTainment
    ```
    
4. Install dependencies:

   Must have node and pip installed.
    ```
    pip install -r requirements.txt
    ```
    or 
    ```
    pip install -r requirements-alt.txt
    ```
    or
    ```
    pip install email_validator
    pip install Flask
    pip install flask-wtf
    pip install flask-bcrypt
    pip install flask-login
    pip install flask-sqlalchemy
    pip install phonenumbers
    pip install pytest
    pip install pytest-flask
    pip install python-dotenv
    pip install pytz
    pip install requests
    pip install schwifty
    pip install tmdbsimple
    pip install flask-qrcode
    ```
6. Run the project:
    
    ```
    flask --app app run
    ```
    

## Usage

To use this project, sign up as a member or associate and log in to access the features, or navigate the site as a guest. 

## Testing

To ensure the project functions correctly, you can run the provided tests. Follow these steps to run the tests:

1. Make sure all dependencies are installed:
    
    ```
    pip install pytest
    pip install pytest-flask
    ```
    
2. Run the tests:
    
    ```
    pytest
    ```
    

### Test Coverage

I have implemented unit tests to cover the main functionalities of the project.

## Author

Monserat Pavia-Bravo

- [**GitHub**](https://github.com/mnsrt-pb)

## Acknowledgements

- [**Cinemark**](https://www.cinemark.com)
- **Flask** - for the back-end framework
- **Pytest** - for running tests
- [**The Movie Database API**](https://developer.themoviedb.org/docs/getting-started)
- [**tmdbsimple**](https://github.com/celiao/tmdbsimple) - wrapper for TMDB API
- [**Flask Tutorials**](https://www.youtube.com/playlist?list=PL-osiE80TeTs4UjLw5MM6OjgkjFeUxCYH)
