# ShopSwift

# E-commerce Website

## Description
An e-commerce website built with Django, JavaScript, and Bootstrap.

## Tech Stack
- **Django**: Backend framework for building robust web applications.
- **JavaScript**: For dynamic and interactive front-end behavior.
- **Bootstrap**: Front-end framework for responsive and mobile-first web development.

## Setup Instructions

### Prerequisites
- Python 3.x
- pip (Python package installer)
- Virtualenv (optional but recommended)

### Installation
1. Clone the repository:
    ```sh
    git clone https://github.com/devpavth/ecommerce_project.git
    cd ecommerce_project
    ```

2. Create a virtual environment and activate it:
    ```sh
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. Install the dependencies:
    ```sh
    pip install -r requirements.txt
    ```

4. Apply migrations:
    ```sh
    python manage.py migrate
    ```

5. Start the development server:
    ```sh
    python manage.py runserver
    ```

6. Open your browser and go to `http://127.0.0.1:8000` to see the website.

## Features
- User authentication
- Product listing
- Shopping Cart
- Order management
- Streamlined Checkout process
- User-friendly product review system
- Detailed product views

