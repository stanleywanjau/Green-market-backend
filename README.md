## Green-market-backend

For this project you'll be working with green market backend.
This is a web application built using flask.
The purpose of the app is to provide an API for managing products, users and orders in a virtual green market.  It provides an API for interacting with the data
It provides an API for the frontend to interact with, and includes user authentication via JWTs (JSON Web Tokens).

## Getting Started
These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. 

## Setup

To get started git clone the repo:
git clone git@github.com:stanleywanjau/Green-market-backend.git

Then cd green-market-backend.

To download the dependencies for the backend, run:

```bash
pipenv install
pipenv shell

There is some starter code in the app/seed.py file so that once you've generated the models, you'll be able to create data to test your application.

Create data by running;
python seed.py
You can run your Flask API on localhost:5555 by running:
python app.py

Depending on your preference, you can either check your progress by:
Running the Flask server and using Postman to make requests.


Relationships:
1.User
Each user can have a farmer profile.
Users can place many orders.
Users can write multiple reviews.
Users can send and receive messages.

2.Farmer
Every farmer has a user profile.
Farmers can sell multiple products.

3.Reviews
Reviews are written by users.
Each review is for a specific product.

4.Product
Products are sold by farmers.
Products can have multiple reviews.

5.Order
Users buy products through orders.
Each order contains one product.
Orders can have multiple payments.

6.Payment
Each payment is tied to an order.

7.ChatMessage
Messages are sent and received by users.

Then, run the migrations and seed file:
flask db upgrade
python seed.py


Routes Setup
Overview
In this section, we'll outline the routes required for our application, along with the expected JSON data format and the corresponding HTTP verbs.

Routes
1.GET /users

Description: Retrieves a list of all users.
Response JSON Format:
[
  {
    "id": 1,
    "username": "cain",
    "email": "cain@example.com",
    "role": "customer",
    "registration_date": "2024-03-14T10:00:00",
    "image": "https://i.pinimg.com/236x/4c/31/ca/4c31ca4229f3240ec02151da4c21f888.jpg"
  },
  {
    "id": 2,
    "username": "Lorenza",
    "email": "lorenza@example.com",
    "role": "farmer",
    "registration_date": "2024-03-15T08:30:00",
    "image": "https://i.pinimg.com/236x/4c/31/ca/4c31ca4229f3240ec02151da4c21f888.jpg"
  }
]
HTTP Verb: GET
2.GET /users/:id

Description: Retrieves details of a specific user identified by ID.
Response JSON Format:
{
  "id": 1,
  "username": "cain",
  "email": "cain@example.com",
  "role": "customer",
  "registration_date": "2024-03-14T10:00:00",
  "image": "https://i.pinimg.com/236x/4c/31/ca/4c31ca4229f3240ec02151da4c21f888.jpg"
}
HTTP Verb: GET
3.POST /users

Description: Creates a new user.
Request Body JSON Format:
{
  "username": "cain",
  "email": "cain@example.com",
  "role": "customer",
  "password": "password123",
  "image": "https://i.pinimg.com/236x/4c/31/ca/4c31ca4229f3240ec02151da4c21f888.jpg"
}
Response JSON Format:

{
  "id": 3,
  "username": "cain",
  "email": "cain@example.com",
  "role": "customer",
  "registration_date": "2024-03-16T14:45:00",
  "image": "https://i.pinimg.com/236x/4c/31/ca/4c31ca4229f3240ec02151da4c21f888.jpg"
}
HTTP Verb: POST
4.PUT /users/:id

Description: Updates details of a specific user identified by ID.
Request Body JSON Format:

{
  "email": "updated_email@example.com",
  "image": "updated_image_url"
}
Response JSON Format:
{
  "id": 1,
  "username": "example_user",
  "email": "updated_email@example.com",
  "role": "customer",
  "registration_date": "2024-03-14T10:00:00",
  "image": "https://i.pinimg.com/236x/4c/31/ca/4c31ca4229f3240ec02151da4c21f888.jpg"
}
HTTP Verb: PUT
5.DELETE /users/:id

Description: Deletes a specific user identified by ID.
HTTP Verb: DELETE


License
This project is licensed under the MIT License - see the LICENSE file for details.

Authors;
Stanley Muiruri
Samuel Njuguna
Dian Jeruto





