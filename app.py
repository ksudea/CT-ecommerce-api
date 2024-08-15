from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from marshmallow import fields, ValidationError, validate
from mysql.connector import Error
import enum
from datetime import timedelta 


my_password = "0711"
db_name = "e_commerce_db_2"
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+mysqlconnector://root:{my_password}@localhost/{db_name}'
db = SQLAlchemy(app)
ma = Marshmallow(app)

# Schema 

class CustomerSchema(ma.Schema):
    #Regex validation for email and phone
    # Note: shows warning for invalid escape sequence when running app
    name = fields.String(required=True, validate=validate.Length(min=2))
    email = fields.String(required=True, validate=validate.Regexp(regex="^[\w\.]+@([\w-]+\.)+[\w-]{2,4}$", error="E-mail is invalid"))
    phone = fields.String(required=True, validate=validate.Regexp(regex='^[+]*[(]{0,1}[0-9]{1,4}[)]{0,1}[-\s\./0-9]{5,9}$', error="Phone number is invalid"))

    class Meta:
        fields = ("name", "email", "phone", "id")

class ProductSchema(ma.Schema):
    name = fields.String(required=True, validate=validate.Length(min=1))
    price = fields.Float(required=True, validate=validate.Range(min=0))

    class Meta:
        fields = ("name", "price", "id")

#Enum for status of orders, used in OrderSchema
class StatusEnum(enum.Enum):
    preparing = 1
    on_the_way = 2
    delayed = 3
    delivered = 4

#Schema for basic order inputs
class OrderInputSchema(ma.Schema):
    customer_id = fields.Integer(required=True)
    date = fields.Date()
    product_ids = fields.List(fields.Integer())
    class Meta:
        fields = ("customer_id", "date", "product_ids", "id")

#Schema for detailed complete order information 
class OrderSchema(ma.Schema):
    customer_id = fields.Integer(required=True)
    date = fields.Date()
    expected_delivery_date = fields.Date()
    status = fields.Enum(StatusEnum)
    products = fields.List(fields.Nested(ProductSchema))
    class Meta:
        fields = ("customer_id", "date", "expected_delivery_date", "status", "products", "id")

class CustomerAccountSchema(ma.Schema):
    username = fields.String(required=True)
    password = fields.String(required=True)
    customer_id = fields.Integer(required=True)

    class Meta:
        fields = ("username","password", "customer_id", "id")

customer_schema = CustomerSchema()
customers_schema = CustomerSchema(many=True)

product_schema = ProductSchema()
products_schema = ProductSchema(many=True)

customer_account_schema = CustomerAccountSchema()

order_input_schema = OrderInputSchema()

order_schema = OrderSchema()
orders_schema = OrderSchema(many=True)

#Database models

class Customer(db.Model):
    __tablename__ = 'Customers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(320))
    phone = db.Column(db.String(15))
    orders = db.relationship('Order', backref='customer')
    
class CustomerAccount(db.Model):
    __tablename__ = 'Customer_Accounts'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('Customers.id'))
    customer = db.relationship('Customer', backref='customer_account', uselist=False)


order_product = db.Table('Order_Product', 
    db.Column('order_id', db.Integer, db.ForeignKey('Orders.id'), primary_key=True),
    db.Column('product_id', db.Integer, db.ForeignKey('Products.id'), primary_key=True))

class Order(db.Model):
    __tablename__ = 'Orders'
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('Customers.id'))
    date = db.Column(db.Date, nullable=False)
    expected_delivery_date = db.Column(db.Date)
    status = db.Column(db.Enum(StatusEnum))
    products = db.relationship('Product', secondary=order_product, back_populates='orders')

class Product(db.Model):
    __tablename__ = 'Products'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    price = db.Column(db.Float, nullable=False)
    orders = db.relationship('Order', secondary=order_product, back_populates='products')

# CRUD for Customers

#Create customer
@app.route('/customers', methods=['POST'])
def add_customer():
    try:
        customer_data = customer_schema.load(request.json)
    except ValidationError as e:
        print(f"Error: {e}")
        return jsonify(e.messages), 400
    try:
        new_customer = Customer(name=customer_data['name'], email=customer_data['email'], phone=customer_data['phone'])
        db.session.add(new_customer)
        db.session.commit()
        return jsonify({"message": "New customer added successfully"}), 201
    except Error as e:
        print(f"Error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

#Read customer
@app.route('/customers/<int:id>', methods=['GET'])
def get_customer(id):
    try:
        customer = Customer.query.get_or_404(id)
        return customer_schema.jsonify(customer)
    except Error as e:
        print(f"Error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

#Update customer
@app.route('/customers/<int:id>', methods=['PUT'])
def update_customer(id):
    customer = Customer.query.get_or_404(id)
    try:
        updated_customer = customer_schema.load(request.json)
    except ValidationError as e:
        print(f"Error: {e}")
        return jsonify(e.messages), 400
    try:
        customer.name = updated_customer['name']
        customer.email = updated_customer['email']
        customer.phone = updated_customer['phone']
        db.session.commit()
        return jsonify({"message": "Customer updated successfully"}), 201
    except Error as e:
        print(f"Error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

#Delete customer
@app.route("/customers/<int:id>", methods=["DELETE"])
def delete_customer(id):
    try:
        customer_to_remove = Customer.query.get_or_404(id)
        db.session.delete(customer_to_remove)
        db.session.commit()
        return jsonify({"message": "Customer removed successfully"}), 200
    except Error as e:
        print(f"Error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

# CRUD for CustomerAccounts
#Create customer account
@app.route('/customeraccounts', methods=['POST'])
def add_customer_account():
    try:
        customer_account_data = customer_account_schema.load(request.json)
    except ValidationError as e:
        print(f"Error: {e}")
        return jsonify(e.messages), 400
    try:
        new_customer_account = CustomerAccount(username=customer_account_data['username'], password=customer_account_data['password'], customer_id=customer_account_data['customer_id'])
        db.session.add(new_customer_account)
        db.session.commit()
        return jsonify({"message": "New customer account added successfully"}), 201
    except Error as e:
        print(f"Error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

#Read customer account
@app.route('/customeraccounts/<int:id>', methods=['GET'])
def get_customer_account(id):
    try:
        customer_account = CustomerAccount.query.get_or_404(id)
        return customer_account_schema.jsonify(customer_account)
    except Error as e:
        print(f"Error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

#Update customer account
@app.route('/customeraccounts/<int:id>', methods=['PUT'])
def update_customer_account(id):
    customer_account = CustomerAccount.query.get_or_404(id)
    try:
        updated_account = customer_account_schema.load(request.json)
    except ValidationError as e:
        print(f"Error: {e}")
        return jsonify(e.messages), 400
    try:
        customer_account.username = updated_account['username']
        customer_account.password = updated_account['password']
        customer_account.customer_id = updated_account['customer_id']
        db.session.commit()
        return jsonify({"message": "Customer account updated successfully"}), 201
    except Error as e:
        print(f"Error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

#Delete customer account
@app.route("/customeraccounts/<int:id>", methods=["DELETE"])
def delete_customer_account(id):
    try:
        account_to_remove = CustomerAccount.query.get_or_404(id)
        db.session.delete(account_to_remove)
        db.session.commit()
        return jsonify({"message": "Customer account removed successfully"}), 200
    except Error as e:
        print(f"Error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500
    
# CRUD for Products 
#Create product
@app.route('/products', methods=['POST'])
def add_product():
    try:
        product_data = product_schema.load(request.json)
    except ValidationError as e:
        print(f"Error: {e}")
        return jsonify(e.messages), 400
    try:
        new_product = Product(name=product_data['name'], price=product_data['price'])
        db.session.add(new_product)
        db.session.commit()
        return jsonify({"message": "New product added successfully"}), 201
    except Error as e:
        print(f"Error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

#Read product
@app.route('/products/<int:id>', methods=['GET'])
def get_product(id):
    try:
        product = Product.query.get_or_404(id)
        return product_schema.jsonify(product)
    except Error as e:
        print(f"Error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

#Update product
@app.route('/products/<int:id>', methods=['PUT'])
def update_product(id):
    product = Product.query.get_or_404(id)
    try:
        updated_product = product_schema.load(request.json)
    except ValidationError as e:
        print(f"Error: {e}")
        return jsonify(e.messages), 400
    try:
        product.name = updated_product['name']
        product.price = updated_product['price']
        db.session.commit()
        return jsonify({"message": "Product updated successfully"}), 201
    except Error as e:
        print(f"Error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

#Delete product
@app.route("/products/<int:id>", methods=["DELETE"])
def delete_product(id):
    try:
        product_to_delete = Product.query.get_or_404(id)
        db.session.delete(product_to_delete)
        db.session.commit()
        return jsonify({"message": "Product removed successfully"}), 200
    except Error as e:
        print(f"Error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

# List all products
@app.route('/products', methods=['GET'])
def get_products():
    products = Product.query.all()
    return products_schema.jsonify(products)

# Order Processing

#Add a new order
@app.route('/orders', methods=['POST'])
def add_order():
    try:
        order_input_data = order_input_schema.load(request.json)
    except ValidationError as e:
        print(f"Error: {e}")
        return jsonify(e.messages), 400
    try:
        customer_id = order_input_data['customer_id']
        date = order_input_data['date']
        #formatted_date = datetime.strptime(Begindatestring, "%Y-%m-%d") 
        expected_delivery = date + timedelta(days=10)
        status = StatusEnum.preparing
        product_id_list = order_input_data['product_ids']
        new_order = Order(customer_id=customer_id, date=date, expected_delivery_date=expected_delivery, status=status)
        db.session.add(new_order)
        for id in product_id_list:
            product = Product.query.get_or_404(id)
            new_order.products.append(product)
        db.session.commit()
        return jsonify({"message": "New order added successfully"}), 201
    except Error as e:
        print(f"Error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

# Retrieve order
@app.route('/orders/<int:id>', methods=['GET'])
def get_order(id):
    try:
        order = Order.query.get_or_404(id)
        return order_schema.jsonify(order)
    except Error as e:
        print(f"Error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

#Track order: retrieves basic info like date, expected delivery date, status
@app.route('/orders/track/<int:id>', methods=['GET'])
def get_order_tracking_details(id):
    try:
        order = Order.query.get_or_404(id)
        order_date = order.date
        expected_delivery = order.expected_delivery_date
        status = order.status.name
        return jsonify({"order-date": order_date, "expected delivery date": expected_delivery, "status": status})
    except Error as e:
        print(f"Error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

# Bonus: cancel order    
@app.route("/orders/<int:id>", methods=["DELETE"])
def delete_order(id):
    try:
        order_to_delete = Order.query.get_or_404(id)
        db.session.delete(order_to_delete)
        db.session.commit()
        return jsonify({"message": "Order canceled successfully"}), 200
    except Error as e:
        print(f"Error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

#Bonus: order total price
@app.route('/orders/totalprice/<int:id>', methods=['GET'])
def get_order_total_price(id):
    try:
        order = Order.query.get_or_404(id)
        total = 0.0
        products = order.products
        for product in products:
            total += product.price
        return jsonify({"total cost of order": total})
    except Error as e:
        print(f"Error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)