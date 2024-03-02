from datetime import datetime
from config import db, bcrypt
from app import app
from models import User, Farmer, Reviews, Product, Order, Payment, ChatMessage, association_table_order_product, association_table_product_review

def delete_data():
    with app.app_context():
        db.session.execute(association_table_order_product.delete())
        db.session.execute(association_table_product_review.delete())
        ChatMessage.query.delete()
        Payment.query.delete()
        Order.query.delete()
        Product.query.delete()
        Reviews.query.delete()
        Farmer.query.delete()
        User.query.delete()
        db.session.commit()

delete_data()

def seed_data():
    with app.app_context():
        user1 = User(username="Cain", email="cain@example.com", password_hash=bcrypt.generate_password_hash("password"), role="customer", registration_date=datetime.now(), image="https://i.pinimg.com/236x/a9/6a/b2/a96ab2f4fa3969802fc17cde9df4b427.jpg")
        user2 = User(username="Lorenza", email="Lorenza@example.com", password_hash=bcrypt.generate_password_hash("password"), role="farmer", registration_date=datetime.now(), image="https://i.pinimg.com/236x/4c/31/ca/4c31ca4229f3240ec02151da4c21f888.jpg")

        farmer1 = Farmer(farm_name="Green Farms", location="Somewhere", contact="1234567890")
        farmer1.user = user2

        db.session.add_all([user1, user2, farmer1])
        db.session.commit()

        review1 = Reviews(customer_id=user1.id, product_id=1, rating=4, comments="Great product!", review_date=datetime.now())
        db.session.add(review1)
        db.session.commit()

        product1 = Product(name="Apple", price=1, description="Fresh apples", quantity_available=100, category="Fruit", image="https://i.pinimg.com/236x/41/6a/67/416a671f74edf7f2357e3cad537635b5.jpg")
        product1.farmer = farmer1
        db.session.add(product1)
        db.session.commit()

        # Create order1 and associate it with product1
        order1 = Order(customer_id=user1.id, order_date=datetime.now(), quantity_ordered=5, total_price=5, order_status="completed", product_id=product1.id)
        db.session.add(order1)
        
        chat_message1 = ChatMessage(sender_id=user1.id, receiver_id=user2.id, message_text="Hello, I would like to order some apples.", timestamp=datetime.now())
        db.session.add(chat_message1)

        payment1 = Payment(order_id=order1.id, payment_amount=5, payment_date=datetime.now(), payment_method="Credit Card", status="completed", transaction_id=123456789)

        db.session.add_all([payment1])

        db.session.execute(association_table_order_product.insert().values(order_id=order1.id, product_id=product1.id))
        db.session.execute(association_table_product_review.insert().values(product_id=product1.id, review_id=review1.id))

        db.session.commit()

seed_data()
print("seed completed")
