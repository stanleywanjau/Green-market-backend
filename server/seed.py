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
        user1 = User(
            username="Cain",
            email="cain@example.com",
            role="customer",
            contact="04889383433",
            registration_date=datetime.now(),
            image="https://i.pinimg.com/236x/a9/6a/b2/a96ab2f4fa3969802fc17cde9df4b427.jpg"
        )
        user1.password_hash = "password"

        user2 = User(
            username="Lorenza",
            email="Lorenza@example.com",
            role="farmer",
            contact="0488638638",
            registration_date=datetime.now(),
            image="https://i.pinimg.com/236x/4c/31/ca/4c31ca4229f3240ec02151da4c21f888.jpg"
        )
        user2.password_hash = "password"

        user3 = User(
            username="Stanley",
            email="Stanleyl@example.com",
            role="customer",
            contact="04889387383",
            registration_date=datetime.now(),
            image="https://i.pinimg.com/236x/4c/31/ca/4c31ca4229f3240ec02151da4c21f888.jpg"
        )
        user3.password_hash = "password"
        user4 = User(
            username="Stacy",
            email="Stacy@example.com",
            role="farmer",
            contact="04884747",
            registration_date=datetime.now(),
            image="https://i.pinimg.com/236x/4c/31/ca/4c31ca4229f3240ec02151da4c21f888.jpg"
        )
        user4.password_hash = "password"
        user5 = User(
            username="Samuel",
            email="Samuel@example.com",
            role="farmer",
            contact="048865775",
            registration_date=datetime.now(),
            image="https://i.pinimg.com/236x/4c/31/ca/4c31ca4229f3240ec02151da4c21f888.jpg"
        )
        user5.password_hash = "password"

        farmer1 = Farmer(farm_name="Green Farms",
                         location="Somewhere", )
        farmer1.user = user2
        farmer2 = Farmer(farm_name="skyfruits",
                         location="Kenol")
        farmer2.user = user4
        farmer3 = Farmer(farm_name="joyview",
                         location="thika", )
        farmer3.user = user5

        db.session.add_all([user1, user2, user3, user4,
                           user5, farmer1, farmer2, farmer3])
        db.session.commit()

        review1 = Reviews(customer_id=user1.id, product_id=1, rating=4,
                          comments="Great product!", review_date=datetime.now())
        db.session.add(review1)
        db.session.commit()

        product1 = Product(name="Apple", price=1, description="Fresh apples", quantity_available=100,
                           category="Fruit", image="https://i.pinimg.com/236x/41/6a/67/416a671f74edf7f2357e3cad537635b5.jpg")
        product2 = Product(name="Eggs", price=15, description="Brown hen Eggs", quantity_available=100,
                           category="Animal product", image="https://i.pinimg.com/564x/98/04/e2/9804e24442e977e5cb4da454b81d62af.jpg")
        product3 = Product(name="Milk", price=65, description="fresh milk from the farmer", quantity_available=10,
                           category="Animal product", image="https://i.pinimg.com/564x/ce/cc/84/cecc84661e9148366b24b6c130138efc.jpg")
        product4 = Product(name="white meat", price=165, description="Thick chicken thigh ", quantity_available=150,
                           category="Animal product", image="https://i.pinimg.com/564x/a7/ab/95/a7ab95e2c50ccae974c3b701e19bcec1.jpg")
        product1.farmer = farmer1
        product2.farmer = farmer1
        product3.farmer = farmer1
        product4.farmer = farmer1
        db.session.add_all([product1, product2, product3, product4])
        db.session.commit()

        # Create order1 and associate it with product1
        order1 = Order(customer_id=user1.id, order_date=datetime.now(
        ), quantity_ordered=5, total_price=10, order_status="completed", product_id=product1.id)
        order2 = Order(customer_id=user3.id, order_date=datetime.now(
        ), quantity_ordered=5, total_price=10, order_status="in progess", product_id=product1.id)
        db.session.add(order1, order2)

        chat_message1 = ChatMessage(sender_id=user1.id, receiver_id=user2.id,
                                    message_text="Hello, I would like to order some apples.", timestamp=datetime.now())
        db.session.add(chat_message1)

        payment1 = Payment(order_id=order1.id, payment_amount=5, payment_date=datetime.now(
        ), payment_method="Credit Card", status="completed", transaction_id=123456789)

        db.session.add_all([payment1])

        db.session.execute(association_table_order_product.insert().values(
            order_id=order1.id, product_id=product1.id))
        db.session.execute(association_table_order_product.insert().values(
            order_id=order1.id, product_id=product2.id))
        db.session.execute(association_table_product_review.insert().values(
            product_id=product1.id, review_id=review1.id))

        db.session.commit()


seed_data()
print("seed completed")
