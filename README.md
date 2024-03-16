# Green-market-backend
For this assessment, you'll be working with green market.

In this repo, there is a Flask application with some features built out.

Your job is to build out the Flask API to add the functionality described in the deliverables below.

# Setup
To get started git clone the repo;
git clone git@github.com:stanleywanjau/Green-market-backend.git
Then cd green-market-backend.
To download the dependencies for the backend, run:

pipenv install
pipenv shell


There is some starter code in the app/seed.py file so that once you've generated the models, you'll be able to create data to test your application.
Create data by running;
python seed.py
You can run your Flask API on localhost:5555 by running:

python app.py

Depending on your preference, you can either check your progress by:
Running the Flask server and using Postman to make requests.

# Relationships:
1. User
Each user can have a farmer profile:

A user can sign up as a farmer, getting a unique farming profile.
Users can place many orders:

Users can buy multiple products, so they can place several orders.
Users can write multiple reviews:

Users can share their opinions on various products by leaving reviews.
Users can send and receive messages:

Users can chat with each other, sending and receiving messages.
2. Farmer
Every farmer has a user profile:

A farmer is someone who sells products, and each farmer has a regular user account.
Farmers can sell multiple products:

Farmers can list several items for sale, like fruits, vegetables, or homemade products.
3. Reviews
Reviews are written by users:

Anyone who buys a product can leave a review sharing their experience.
Each review is for a specific product:

Reviews are about particular items, letting others know what they think about them.
4. Product
Products are sold by farmers:

Items listed for sale on the platform are offered by individual farmers.
Products can have multiple reviews:

Many people can review the same product, giving different perspectives.
5. Order
Users buy products through orders:

When someone wants to purchase something, they create an order.
Each order contains one product:

Each order is for a single item, whether it's a bag of apples or a handmade craft.
Orders can have multiple payments:

Payment for an order might be split into several transactions.
6. Payment
Each payment is tied to an order:
When someone pays for an order, that payment is linked to the specific order they're paying for.
7. ChatMessage
Messages are sent by users:

Users can communicate with each other through chat messages.
Messages are received by users:

When someone sends a message, it's received by another user.


Then, run the migrations and seed file:
flask db upgrade
python seed.py

Routes Setup
Overview
In this section, we'll outline the routes required for our application, along with the expected JSON data format and the corresponding HTTP verbs.

Routes
1. GET /users
Description:
Retrieves a list of all users.
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
    "email": "another_user@example.com",
    "role": "farmer",
    "registration_date": "2024-03-15T08:30:00",
    "image": "https://i.pinimg.com/236x/4c/31/ca/4c31ca4229f3240ec02151da4c21f888.jpg"
  }
]
HTTP Verb:
GET

2. GET /users/:id
Description:
Retrieves details of a specific user identified by ID.

Response JSON Format:
{
  "id": 1,
  "username": "cain",
  "email": "cain@example.com",
  "role": "customer",
  "registration_date": "2024-03-14T10:00:00",
  "image": "https://i.pinimg.com/236x/4c/31/ca/4c31ca4229f3240ec02151da4c21f888.jpg"
}
HTTP Verb:
GET

3. POST /users
Description:
Creates a new user.

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
HTTP Verb:
POST

4. PUT /users/:id
Description:
Updates details of a specific user identified by ID.

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
HTTP Verb:
PUT

5. DELETE /users/:id
Description:
Deletes a specific user identified by ID.

HTTP Verb:
DELETE


# License
This project is licensed under the MIT License - see the LICENSE file for details.

Author:
1.Stanley Muiruri
2.Samuel Njuguna
3.Dian Jeruto












