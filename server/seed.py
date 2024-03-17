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

<<<<<<< HEAD
        review1 = Reviews(
            customer_id=1,
            product_id=2,
            rating=4,
            comments="Great product! Would buy again.",
            review_date=datetime(2023, 12, 6),
        )

        review2 = Reviews(
            customer_id=2,
            product_id=1,
            rating=3,
            comments="Decent, but could be improved.",
            review_date=datetime(2023, 12, 3),
        )

        review3 = Reviews(
            customer_id=3,
            product_id=4,
            rating=5,
            comments="Absolutely love it!",
            review_date=datetime(2023, 11, 30),
        )

        review4 = Reviews(
            customer_id=4,
            product_id=3,
            rating=2,
            comments="Not what I expected. Disappointing.",
            review_date=datetime(2023, 12, 8),
        )

        review5 = Reviews(
            customer_id=5,
            product_id=1,
            rating=4,
            comments="Good quality for the price.",
            review_date=datetime(2023, 12, 5),
        )
        review6 = Reviews(
            customer_id=1,  # User 1 reviews a new product
            product_id=3,
            rating=2,
            comments="Not as good as their other products.",
            review_date=datetime(2023, 12, 2),
        )

        review7 = Reviews(
            customer_id=2,
            product_id=4,
            rating=5,
            comments="Amazing, will definitely buy again.",
            review_date=datetime(2023, 12, 9),
        )

        review8 = Reviews(
            customer_id=3,
            product_id=1,
            rating=3,
            comments="Does the job.",
            review_date=datetime(2023, 11, 28),
        )

        review9 = Reviews(
            customer_id=4,
            product_id=2,
            rating=4,
            comments="Impressed with the quality.",
            review_date=datetime(2023, 12, 6),
        )

        review10 = Reviews(
            customer_id=5,
            product_id=3,
            rating=1,
            comments="Very poor experience.",
            review_date=datetime(2023, 12, 10),
        )
        review11 = Reviews(
            customer_id=1,  # User 1 needs one more review
            product_id=2,  # The only product available
            rating=3,
            comments="It's alright.",
            review_date=datetime(2023, 12, 9),
        )

        review12 = Reviews(
            customer_id=2,
            product_id=2,  # User 2 needs one more review
            rating=4,
            comments="Great value for the price.",
            review_date=datetime(2023, 12, 3),
        )

        review13 = Reviews(
            customer_id=3,
            product_id=2,  # User 3 needs one more review
            rating=5,
            comments="Exceeded my expectations!",
            review_date=datetime(2023, 12, 5),
        )

        review14 = Reviews(
            customer_id=4,
            product_id=2,  # User 4 needs one more review
            rating=2,
            comments="Not a fan. Wouldn't purchase again.",
            review_date=datetime(2023, 12, 1),
        )

        review15 = Reviews(
            customer_id=5,
            product_id=2,  # User 5 needs one more review
            rating=3,
            comments="It does the job, but nothing special.",
            review_date=datetime(2023, 12, 6),
        )

        db.session.add(review1)
        db.session.add(review2)
        db.session.add(review3)
        db.session.add(review4)
        db.session.add(review5)
        db.session.add(review6)
        db.session.add(review7)
        db.session.add(review8)
        db.session.add(review9)
        db.session.add(review10)
        db.session.add(review11)
        db.session.add(review12)
        db.session.add(review13)
        db.session.add(review14)
        db.session.add(review15)
        db.session.commit()
=======
>>>>>>> 1f9569171c9310f4a5996ad7a22ffebe91c88f71

        product1 = Product(name="Apple", price=50, description="Fresh apples", quantity_available=100,
                           category="Fruit", image="https://i.pinimg.com/236x/41/6a/67/416a671f74edf7f2357e3cad537635b5.jpg")
        product2 = Product(name="Eggs", price=15, description="Brown hen Eggs", quantity_available=100,
                           category="Animal product", image="https://i.pinimg.com/564x/98/04/e2/9804e24442e977e5cb4da454b81d62af.jpg")
        product3 = Product(name="Milk", price=65, description="fresh milk from the farmer", quantity_available=10,
                           category="Animal product", image="https://i.pinimg.com/564x/ce/cc/84/cecc84661e9148366b24b6c130138efc.jpg")
        product4 = Product(name="white meat", price=165, description="Thick chicken thigh ", quantity_available=150,
                           category="Animal product", image="https://i.pinimg.com/564x/a7/ab/95/a7ab95e2c50ccae974c3b701e19bcec1.jpg")
        product5 = Product(name="Carrots", price=200 , description="Fresh from the soil ",                       quantity_available=2000,
                           category="Farm Product", image="https://i.pinimg.com/564x/0a/5c/b9/0a5cb93f270d6dccff985d5124f88d60.jpg")

        product6 = Product(name="Broccoli", price=350 , description="Fresh from the soil ",                       quantity_available=400,
                                category="Farm Product", image="https://i.pinimg.com/564x/ae/c3/5f/aec35f79fe1931cde91c32c61f0e30b3.jpg")

        product7 = Product(name="Potatoes", price=150 , description="Fresh from the soil ", quantity_available=5000,
                                category="Farm Product", image="https://i.pinimg.com/564x/e3/3c/f0/e33cf066de0c2a5543b5c8ee380b2d27.jpg")
                                        
        product8 = Product(name="Lettuce", price= 50 , description="Fresh from the soil ", quantity_available=800,
                                category="Farm Product", image="https://i.pinimg.com/564x/12/b4/d2/12b4d23bb51903a63d1c144258b6f24a.jpg")                           

        product9 = Product(name="Yellow, red and green bell peppers", price=150 , description="Fresh from the soil ", quantity_available=5000,
                                category="Farm Product", image="https://i.pinimg.com/564x/53/0d/ae/530daec371000945e3474d9e5cc551f5.jpg")                        

        product10 = Product(name="Red Onions", price=150 , description="Fresh from the soil ", quantity_available=5000,
                                category="Farm Product", image="https://i.pinimg.com/564x/85/ea/3e/85ea3e8cec7f3cb675c7715658c5dc57.jpg")                         

        product11 = Product(name="Green Peas", price=200, description="Fresh from the soil ", quantity_available=5000,
                                category="Farm Product", image="https://i.pinimg.com/564x/18/62/42/186242542ac53595326ce4b49b062187.jpg")                       

        product12 = Product(name="Chicken", price=500, description="Different types of chicken avilable", quantity_available=800,
                                category="Farm Product", image="https://i.pinimg.com/564x/ed/7f/42/ed7f422ca33d88d12f1549b37602025c.jpg")

        product13 = Product(name="White Cabbage", price=150, description="Fresh from the soil ", quantity_available=5000,
                                category="Farm Product", image="https://i.pinimg.com/564x/e9/bc/c3/e9bcc3b0e3db4ea380c16437ad84570d.jpg")


        product14 = Product(name="Egg Plant", price=60, description="Fresh from the soil ", quantity_available=5000,
                                category="Farm Product", image="https://i.pinimg.com/564x/30/a2/20/30a220d43664fc249dc04dc5e63bf130.jpg")

        product15 = Product(name="Beetroot", price=150, description="Fresh from the soil ", quantity_available=5000,
                                category="Farm Product", image="https://i.pinimg.com/564x/24/c6/17/24c617073a4b5f984add0a9efa6298a3.jpg")

        product16 = Product(name="Cauliflower", price=100, description="Fresh from the soil ", quantity_available=5000,
                                category="Farm Product", image="https://i.pinimg.com/564x/99/70/f0/9970f0d7f40e470c8d7548ea49042d34.jpg")

        product17 = Product(name="Strawberry", price=200 , description="Fruit ", quantity_available=5000,
                                category="Farm Product", image="https://i.pinimg.com/564x/1c/ac/37/1cac37c5520085aba52654b18beb225a.jpg")

        product18 = Product(name="Blueberries", price=200 , description="Fruit ", quantity_available=5000,
                                category="Farm Product", image="https://i.pinimg.com/564x/ef/35/37/ef35375fdc70bbcd607bec57f0f6cc8d.jpg")

        product19 = Product(name="Banana", price=150, description="Fresh from the soil ", quantity_available=5000,
                                category="Farm Product", image="https://i.pinimg.com/564x/67/ff/04/67ff0431ed4ecbf10ebed90c15eb6d0a.jpg")

        product20 = Product(name="Apples", price=100 , description="Fresh from the soil ", quantity_available=5000,
                                category="Farm Product", image="https://i.pinimg.com/564x/f3/4a/2b/f34a2ba240a1fabf2a1f0f63d3e081e2.jpg")
        product1.farmer = farmer1
        product2.farmer = farmer1
        product3.farmer = farmer1
        product4.farmer = farmer2
        product5.farmer = farmer1
        product6.farmer = farmer3
        product7.farmer = farmer2
        product8.farmer = farmer1
        product9.farmer = farmer2
        product10.farmer = farmer1
        product11.farmer = farmer2
        product12.farmer = farmer2
        product13.farmer = farmer3
        product14.farmer = farmer1
        product15.farmer = farmer2
        product16.farmer = farmer3
        product17.farmer = farmer2
        product18.farmer = farmer2
        product19.farmer = farmer1
        product20.farmer = farmer2
        
        db.session.add_all([product1, product2, product3, product4,product5,product6,product7,product8,
                            product9, product10,product10, product11, product12,product13, product14, product15,
                               product16, product17, product18, product19, product20])
        db.session.commit()

        review1 = Reviews(customer_id=user1.id, product_id=1, rating=4,
                          comments="Great product!", review_date=datetime.now())
        db.session.add(review1)
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