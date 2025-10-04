# TechFlow - Inventory Management System

TechFlow is a **Flask-based web application** designed to manage products, track inventory levels, and handle product movements between multiple locations. It provides an intuitive interface to monitor stock, update quantities, and view balance reports.

## Features

- **Product Management**: Add, update, and delete products with unique IDs.
- **Inventory Tracking**: Maintain accurate stock levels for multiple locations.
- **Product Transfers**: Move stock between locations with automated updates.
- **Balance Grid**: View the current stock of each product at all locations.
- **Web Interface**: Easy-to-use HTML/CSS/JavaScript frontend.

## Installation

1. Clone the repository:
   ```bash
    git clone https://github.com/Piramu03/TechFlow.git
   
2.Navigate to the project directory:
     
     cd TechFlow
3.Create and activate a virtual environment:

    python -m venv venv
    source venv/bin/activate  
4.pip install -r requirements.txt
   
    pip install -r requirements.txt
5.Run the application:
   
    python run.py
## Usage

- **Add Products**: Input Product Name and Initial Quantity.
- **Transfer Stock**: Move items between locations and update quantities automatically.
- **Check Balance**: View current stock status across all locations.
- **View Movements**: Track historical product movements for reference.

## Screenshots

Add Products
<img width="1818" height="888" alt="Screenshot 2025-10-04 085754" src="https://github.com/user-attachments/assets/e0e8f7f5-35ef-4fe0-849a-f56da212965b" />

View Products
<img width="1812" height="900" alt="Screenshot 2025-10-04 085937" src="https://github.com/user-attachments/assets/aa368f54-9531-42ab-a98f-3b55ef7f9a71" />

View Movements
<img width="1840" height="888" alt="Screenshot 2025-10-04 085736" src="https://github.com/user-attachments/assets/87a03e4f-647a-4156-bd58-1f795255666d" />

Report
<img width="1806" height="891" alt="Screenshot 2025-10-03 194201" src="https://github.com/user-attachments/assets/49def81c-697f-4457-bf82-3a26ba4dcaee" />


## Tech Stack
- **Backend**: Flask (Python)
- **Frontend**: HTML, CSS
- **Database**: SQLite (via SQLAlchemy ORM)
- **Environment**: Virtual Environment (venv)


