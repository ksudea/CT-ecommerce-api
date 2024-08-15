# CT-ecommerce-api
Mini-project: E-Commerce API

API features:

Customer and CustomerAccount Management: CRUD endpoints for managing Customers and their associated CustomerAccounts:
    Create Customer: Add a new customer with essential customer information, including name, email, and phone number.
    Read Customer: Retrieve customer details based on their unique identifier (ID).
    Update Customer: Update customer details, allows modifications to the customer's name, email, and phone number.
    Delete Customer: delete a customer from the system based on their ID.
    Create CustomerAccount: Add a new customer account with fields for a unique username and a password.
    Read CustomerAccount: Retrieve customer account details.
    Update CustomerAccount: Update customer account information, including the username and password.
    Delete CustomerAccount: delete a customer account.
    
Product Catalog: CRUD endpoints for managing Products:
    Create Product: Implement an endpoint to add a new product to the e-commerce database with product name and price.
    Read Product: Retrieve product details based on the product's unique identifier (ID). Provide functionality to query and display product information.
    Update Product: Update product details, allowing modifications to the product name and price.
    Delete Product: Delete a product from the system based on its unique ID.
    List Products: List all available products in the e-commerce platform.

Order Processing: Orders Management functionality to efficiently handle customer orders, ensuring that customers can place, track, and manage their orders seamlessly.
    Place Order: Customer can place a new order, specifying the products they wish to purchase and providing essential order details including customer ID, date, and product IDs.
    Retrieve Order: Allows customers to retrieve details of a specific order based on its unique identifier (ID). Provide a clear overview of the order, including the order date and associated products.
    Track Order: Enables customers to track the status and progress of their orders. Customers should be able to access information such as order dates and expected delivery dates.
    Cancel Order (Bonus): Allows customers to cancel an order.
    Calculate Order Total Price (Bonus): Calculates the total price of items in a specific order, considering the prices of the products included in the order.

Running the application:
Virtual environment:
python -m venv myenv     
myenv\scripts\activate 

Make sure to install dependencies using pip install.

Run the app with the command "flask run".

The repository contains three Postman collections through which a user can interact with the API endpoints. Make sure to import these into Postman in order to seamlessly interact with the API.
