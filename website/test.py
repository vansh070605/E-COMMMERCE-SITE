from intasend import APIService  # Ensure the APIService class is correctly imported
from config import API_TOKEN, API_PUBLISHABLE_KEY  # Import from the config file

# Use the API keys defined in the config file
service = APIService(
    public_key=API_PUBLISHABLE_KEY,  # Use the API_PUBLISHABLE_KEY from config.py
    private_key=API_TOKEN,           # Use the API_TOKEN from config.py
    test=True                         # Set to True if you are in test mode
)

# Make the API call to initiate the order
create_order = service.collect.mpesa_stk_push(
    phone_number=8810223022,           # Replace with a valid phone number
    email='vansh070605@gmail.com',             # Replace with the customer's email
    amount=100,                         # Replace with the transaction amount
    narrative="Payment for Order #12345"  # Add a narrative describing the transaction
)

# Output the response from the API call
print("Order created successfully:", create_order)
print(f"API_TOKEN: {API_TOKEN}")