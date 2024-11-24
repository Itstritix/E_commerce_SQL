import random
from faker import Faker
from decimal import Decimal
import hashlib
import faker_commerce
import mysql.connector


Db_con = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="e_commerce"
)

if Db_con.is_connected():
    print("Connected to the DB")
else:
    print("Failed to connect to the DB")

fake = Faker()
fake.add_provider(faker_commerce.Provider)
cursor = Db_con.cursor()

for _ in range(10):
    #Generate fake user data
    first_name = fake.first_name()
    last_name = fake.last_name()
    email = fake.email()

    #Hash the password
    user_password = fake.password()
    SaltCode = "PassSalt12391238"
    Database_Pass = user_password + SaltCode
    DbHash = hashlib.md5(Database_Pass.encode())
    password = DbHash.hexdigest()

    sql = "INSERT INTO User (First_name, Last_name, Email, Password) VALUES (%s, %s, %s, %s)"
    values = (first_name, last_name, email, password)
    cursor.execute(sql, values)

    #Get the last user_id inserted
    cursor.execute("SELECT LAST_INSERT_ID()")
    user_id = cursor.fetchone()[0]


    #Address
    delivery_phone = fake.phone_number()
    fake_address = fake.street_address()
    fake_extra_info = "Floor " + str(random.randint(1, 12))
    fake_postal_code = fake.zipcode()
    fake_city = fake.city()
    fake_country = fake.country()

    sql = "INSERT INTO Address (FK_User_ID, Address, Extra_info, Postal_Code, City, Country) VALUES (%s, %s, %s, %s, %s, %s)"
    values = (user_id, fake_address, fake_extra_info, fake_postal_code, fake_city, fake_country)
    cursor.execute(sql, values)

    #Get Address id
    cursor.execute("SELECT LAST_INSERT_ID()")
    address_id = cursor.fetchone()[0]
    print(address_id)



    #Product
    product_name = fake.ecommerce_name()
    product_description = fake.sentence()
    product_category = fake.ecommerce_category()
    product_price = Decimal(fake.random_number(2))

    sql = "INSERT INTO Product (Name, Description, Category, Price) VALUES (%s, %s, %s, %s)"
    values = (product_name, product_description, product_category, product_price)
    cursor.execute(sql, values)

    #Get Product_id
    cursor.execute("SELECT LAST_INSERT_ID()")
    product_id = cursor.fetchone()[0]



    #Cart
    sql = "INSERT INTO Cart (FK_user_ID) VALUES ("+ str(user_id) +")"
    cursor.execute(sql)

    #Get Cart_ID
    cursor.execute("SELECT LAST_INSERT_ID()")
    cart_id = cursor.fetchone()[0]



    #Cart Content
    quantity = fake.random_int(min=1, max=5)
    sql = "INSERT INTO Cart_content (FK_cart_ID, FK_product_ID, Quantity) VALUES (%s, %s, %s)"
    values = (cart_id, product_id, quantity)
    cursor.execute(sql, values)



    #Card
    name_on_card = first_name + " " + last_name
    card_number = fake.credit_card_number(card_type="mastercard")
    expiration_date = fake.credit_card_expire()
    cvc = fake.credit_card_security_code(card_type="mastercard")

    sql = "INSERT INTO Card (FK_user_ID, Card_owner, Card_number, Expiration_date, Cvc) VALUES (%s, %s, %s, %s, %s)"
    values = (user_id, name_on_card, card_number, expiration_date, cvc)
    cursor.execute(sql, values)

    #Get card_id
    cursor.execute("SELECT LAST_INSERT_ID()")
    card_id = cursor.fetchone()[0]

    # Command
    order_date = fake.date_this_decade()
    payment_method = fake.random_int(min=1, max=2)
    total_price = fake.pyfloat(2, 2, True, 0.1, 100.0)

    sql = "INSERT INTO Command (FK_cart_ID, FK_user_ID, FK_address_ID, FK_method_ID, FK_card_ID, Order_date, Total_price) VALUES (%s, %s, %s, %s, %s, %s, %s)"
    values = (cart_id, user_id, address_id, payment_method, card_id, order_date, total_price)
    cursor.execute(sql, values)

    # Get command_id
    cursor.execute("SELECT LAST_INSERT_ID()")
    command_id = cursor.fetchone()[0]

    # Invoices
    sql = "INSERT INTO Invoices (FK_user_ID, FK_command_ID) VALUES (%s, %s)"
    values = (user_id, command_id)
    cursor.execute(sql, values)

    # Photo
    photo_link = fake.image_url()
    type_photo = fake.random_int(min=1, max=2)
    sql = "INSERT INTO Photo (FK_id_type, Entity_ID, url) VALUES (%s, %s, %s)"
    values = []
    if type_photo == 1:
        values = (type_photo, product_id, photo_link)
    elif type_photo == 2:
        values = (type_photo, user_id, photo_link)
    cursor.execute(sql, values)

    #Rate
    rate_value = fake.pyfloat(1, 1, True, 0.1, 5)
    review = fake.text(50)

    sql = "INSERT INTO Rate (FK_product_ID, FK_user_ID, Rating, Review) VALUES (%s, %s, %s, %s)"
    values = (product_id, user_id, rate_value, review)
    cursor.execute(sql, values)


Db_con.commit()

cursor.close()
Db_con.close()