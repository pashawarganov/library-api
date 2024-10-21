# Library Service API

This project is a Library API built using Python and Django REST framework. It allows users to borrow books, manage payments, and handle overdue fines.

## Features

- Borrow books from the library
- Manage payments for borrowed books
- Handle overdue fines
- User authentication and authorization (JWT)
- Admin panel for managing books, users, borrowings, and payments
- Daily notifications for overdue borrowings
- Telegram bot notifications for borrowing creation and successful payments
- Stripe API for payment processing
- Swagger documentation for API

## Technologies Used

- Python
- Django
- Django REST framework
- Stripe API for payment processing

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/pashawarganov/library-api.git
   cd library-api

2. Create and activate a virtual environment:
    ```bash
    python -m venv venv
    # On Windows use
    venv\Scripts\activate
    # On macOS/Linux use
    source venv/bin/activate
3. Install the dependencies:
    ```bash
    pip install -r requirements.txt
4. Set up the database:
    ```bash
    python manage.py migrate
5. Create a superuser:
    ```bash
    python manage.py createsuperuser
6. Run the development server:
    ```bash
    python manage.py runserver

## Start with Docker

To run the application using Docker, execute the following command:
```bash
    docker-compose up --build
```
Load Data from Fixtures
To load sample data into the database, run:
```bash
  docker-compose exec library python manage.py loaddata data_sample.json
```
## API Endpoints
### User Management:

- POST /api/users/register/
- POST /api/users/token/
- POST /api/users/token/refresh/
- POST /api/users/token/verify/
- GET /api/users/me/
### Payments:

- POST /api/payments/create-payment/
- GET /api/payments/success/
- GET /api/payments/cancel/
### Borrowings:

- GET /api/borrowings/
- POST /api/borrowings/
- GET /api/borrowings/{id}/
- PUT /api/borrowings/{id}/return/

### Books:

- GET /api/books/
- POST /api/books/
- GET /api/books/{id}/
- PUT /api/books/{id}/
- DELETE /api/books/{id}/

### Documentation:

- GET /api/schema/
- GET /api/doc/swagger/
- GET /api/doc/redoc/

## Usage
- Register a new user or log in with an existing user.
    Example credentials:

    - Login: michael_no_jackson
    - Password: 1qazxcde3
- Borrow a book by making a POST request to /api/borrowings/.

- Make a payment for the borrowed book by making a POST request to /api/payments/.

- Return the borrowed book by making a PUT request to /api/borrowings/{id}/return/.

## Contributing
- Fork the repository. 
- Create a new branch
```bash
    git checkout -b feature/branch-name
```
- Make changes and commit
```bash
    git add .
    git commit -m "commit message"
```
- Push to the branch
```bash
    git push origin feature/branch-name
```
