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
        product5 = Product(name="Carrots", price="200 per kg", description="Fresh from the soil ",                       quantity_available=2000,
                           category="Farm Product", image="https://unsplash.com/photos/orange-carrots-on-human-hand-ZgDHMMd72I8")

        product6 = Product(name="Broccoli", price="350 per kg", description="Fresh from the soil ",                       quantity_available=400,
                                category="Farm Product", image="https://unsplash.com/photos/green-broccoli-in-close-up-photography-wpJzb1lX5Ac")

        product7 = Product(name="Potatoes", price="150 per kg", description="Fresh from the soil ", quantity_available=5000,
                                category="Farm Product", image="https://unsplash.com/photos/brown-potato-lot-B0s3Xndk6tw")
                                        
        product8 = Product(name="Lettuce", price= "50" , description="Fresh from the soil ", quantity_available=800,
                                category="Farm Product", image="https://unsplash.com/photos/purple-and-green-vegetable-plant-s4gWFbWdcWg")                           

        product9 = Product(name="Yellow, red and green bell peppers", price="150 per kg", description="Fresh from the soil ", quantity_available=5000,
                                category="Farm Product", image="https://unsplash.com/photos orange-bell-peppers-on-white-ceramic-plate-gpP-OkJ5BbI")                        

        product10 = Product(name="Red Onions", price="150 per kg", description="Fresh from the soil ", quantity_available=5000,
                                category="Farm Product", image="https://unsplash.com/photos/red-onion-on-brown-wooden-table-D9h2-RxM1rE")                         

        product11 = Product(name="Green Peas", price="200 per kg", description="Fresh from the soil ", quantity_available=5000,
                                category="Farm Product", image="https://unsplash.com/photos/green-peas-in-macro-lens-bwKUJ3Y5JS4")                       

        product12 = Product(name="Chicken", price="500", description="Different types of chicken avilable", quantity_available=800,
                                category="Farm Product", image="https://unsplash.com/photos/five-brown-hens-on-ground-beside-fence-8wWpDF4Av-Y")

        product13 = Product(name="White Cabbage", price="150", description="Fresh from the soil ", quantity_available=5000,
                                category="Farm Product", image="https://unsplash.com/photos/brown-potato-lot-B0s3Xndk6tw")


        product14 = Product(name="Egg Plant", price="60", description="Fresh from the soil ", quantity_available=5000,
                                category="Farm Product", image="https://unsplash.com/photos/purple-and-green-vegetable-on-blue-plastic-container-iyEc3PHk2ZM")

        product15 = Product(name="Beetroot", price="150", description="Fresh from the soil ", quantity_available=5000,
                                category="Farm Product", image="https://unsplash.com/photos/turnips-on-brown-wooden-surface-udo5pIvRfrA")

        product16 = Product(name="Cauliflower", price="100", description="Fresh from the soil ", quantity_available=5000,
                                category="Farm Product", image="https://unsplash.com/photos/cauliflower-lot-zNsSGYXaeP8")

        product17 = Product(name="Strawberry", price="200 per kg", description="Fruit ", quantity_available=5000,
                                category="Farm Product", image="https://unsplash.com/photos/strawberry-lot-FCrgmqqvl-w")

        product18 = Product(name="Blueberries", price="200 per kg", description="Fruit ", quantity_available=5000,
                                category="Farm Product", image="https://unsplash.com/photos/blue-berries-on-brown-tree-branch-K_sWk4fDf28")

        product19 = Product(name="Banana", price="150", description="Fresh from the soil ", quantity_available=5000,
                                category="Farm Product", image="https://unsplash.com/photos/green-banana-fruit-during-daytime-OrK8DrZuTF8")

        product20 = Product(name="Apples", price="100 per kg", description="Fresh from the soil ", quantity_available=5000,
                                category="Farm Product", image="https://unsplash.com/photos/red-and-green-apple-fruits-6xyUDUCMYcU")
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
