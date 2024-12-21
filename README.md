# E-Commerce Website

## Overview
This project is a feature-rich e-commerce platform built using Flask for the backend and a relational database for data storage. Users can browse products, add them to a cart, place orders, and manage their accounts. It also includes integration with a payment gateway for seamless transactions.

## Features
- **User Authentication**:
  - User registration and login.
  - Role-based access for admins and customers.
- **Product Management**:
  - Add, update, and delete products (admin functionality).
  - Display product details and images.
- **Shopping Cart**:
  - Add items to the cart.
  - Update quantities or remove items.
  - View cart summary and total cost.
- **Order Management**:
  - Place orders with payment integration.
  - View past orders.
- **Payment Integration**:
  - MPESA payment integration using IntaSend API.

## Installation

### Prerequisites
- Python (3.8 or higher)
- pip (Python package manager)
- Virtual Environment (optional but recommended)

### Steps
1. Clone the repository:
   ```bash
   git clone https://github.com/vansh070605/E-COMMMERCE-SITE.git
   cd ecommerce-website
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate   # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   Create a `.env` file in the root directory and add the following:
   ```
   FLASK_APP=run.py
   FLASK_ENV=development
   SECRET_KEY=your_secret_key
   API_TOKEN=your_api_token
   API_PUBLISHABLE_KEY=your_api_publishable_key
   ```

5. Initialize the database:
   ```bash
   flask db init
   flask db migrate
   flask db upgrade
   ```

6. Run the application:
   ```bash
   flask run
   ```
   The application will be available at `http://127.0.0.1:5000`.

## Usage
- Access the application via the web browser.
- Browse products, add them to the cart, and place orders.
- Admin users can manage products and view all orders.

## Project Structure
```
|-- ecommerce-website/
    |-- media/
        | -- all the images
    |-- venv/
        | -- virtual environment
    |-- website/
        |-- static/
        |-- templates/
        |-- __init__.py
        |-- admin.py
        |-- auth.py
        |-- config.py
        |-- forms.py
        |-- models.py
        |-- test.py
        |-- views.py
    |-- main.py
    |-- venv/
    |-- requirements.txt
    |-- README.md
```

## Technologies Used
- **Frontend**:
  - HTML, CSS, JavaScript
  - Bootstrap for styling
- **Backend**:
  - Python Flask
  - Jinja2 template engine
- **Database**:
  - SQLite (or other relational databases)

## Known Issues
- Ensure valid API keys are provided for payment integration.
- Proper phone number format is required for MPESA payments.

## Future Enhancements
- Add more payment gateways.
- Implement a wishlist feature.
- Enhance the admin dashboard with analytics.

## License
This project is licensed under the MIT License. See `LICENSE` for more details.

## Acknowledgements
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Bootstrap Documentation](https://getbootstrap.com/)
- [IntaSend API Documentation](https://intasend.com/docs/)

