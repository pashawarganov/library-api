# Library API

Django project for managing borrowings in library

You can use following user:
- Login: michael_no_jackson
- Password: 1qazxcde3

## Start with Docker

```shell
docker-compose up --build
```

### Load data from fixtures

```shell
docker-compose exec "python manage.py loaddata data_sample.json"
```

## Features

* JWT authentication functionality for users
* Managing books, users, borrowings and payments directly from website interface
* Filter for borrowings by `is_active` and `user_id` fields
* Powerful admin panel for advanced managing
* Notification in telegram bot, when borrowing created and when payment successful
* Daily-based notification for checking borrowings overdue
* Stripe payments
* Swagger documentation
