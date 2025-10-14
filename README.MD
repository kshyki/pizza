# Pizzeria Web Application

My own pet project made with using framework FastAPI.

## Overview

This projects looks like basic pizzeria ordering site(but with very bad front) introducing to you opportunities to look for pizzas, create your own profile, login to your profile, watch some your personal information, create an order and look for all your previous orders.

## Technologies

1. There were used a plenty of python libs such as:
    - **FastAPI** - as the core framework 
    - **SQLAlchemy** - as the ORM to use SQLite
    - **JWT** - as the Authentication service
    - **bcrypt** - for password hashing 
    - **Jinja2** - for html templates

## How to start?

1. **Navigate to the project directory**

2. **Install required libs**:

pip install fastapi uvicorn sqlalchemy bcrypt jinja2 PyJWT

3. **Run the application with writing to console**:

uvicorn main:app --reload

4. **Access the application**:
   Navigate to `http://localhost:8000` in your web browser

### How does that works?
First of all, on the main page you can see our Menu with just clicking on the menu button. However, it is the only one function for which you have an access without registration so:

1. **Account Registration**:
   - Access the registration page
   - Provide name, email address, and password
   - Submit the registration form
   - Then you will be redirected to the login page 

2. **User Login**:
   - Navigate to the login page
   - Enter registered email and password credentials
   - After successful authentication, you will be redirected to user profile

### Application Functionality

3. **Menu Navigation**:
   - Access the menu page to view available products
   - Select individual items to view detailed information

4. **Order Placement**:
   - Navigate to the order page
   - Specify quantities for desired products
   - Submit the order for processing
   - Access order history through the user profile

5. **Session Management**:
   - Select logout option to terminate the current session

### Architecture of Authenfication 

When you register on the site, server will hash your password and put it with your name and email to the DB. You will be assigned special user_id which will be unique for you. Your email also can't be the same with someone's. After succesful registration you will be redirected to the login page, here you need to put your email and password.

After that you will receive JWT token which will be immediately saved to Cookie, and then you will be redireted to the profile page, which you can access only with working token.
