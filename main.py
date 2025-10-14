from fastapi import FastAPI, Depends, HTTPException, Request, Form
from fastapi.responses import Response, RedirectResponse
from databes import Base, engine, get_db
from models import Menu, User, Orders
from sqlalchemy.orm import Session
import bcrypt 
from fastapi.templating import Jinja2Templates
from typing import Annotated
from config import descriptions, photo_links, SECRET_KEY
import jwt
from jwttokens import create_access_token, access_token_required

Base.metadata.create_all(bind=engine)
templates = Jinja2Templates(directory="templates")
db = Session(bind=engine)

if db.query(Menu).count() == 0:
    pizzas = [
        Menu(name='Peperoni', price=100, description = descriptions['Peperoni'], photo_link = photo_links["Peperoni"]),
        Menu(name='Caprese', price=200, description = descriptions['Caprese'], photo_link = photo_links["Caprese"]),
        Menu(name='Cheese', price=300, description = descriptions['Cheese'], photo_link = photo_links["Cheese"])
    ]
    db.add_all(pizzas)
    db.commit()
db.close()

app = FastAPI()
    
@app.get("/")
async def root(request: Request):
    token = request.cookies.get("my_access_token")
    return templates.TemplateResponse("index.html", {"request": request, "token": token})


@app.get("/menu")
async def menu(request: Request, db: Session = Depends(get_db)):
    menu = db.query(Menu).all()
    return templates.TemplateResponse("menu.html", {"request": request, "menu": menu})

@app.get("/menu/{pizza_name}")
async def pizza(pizza_name: str, request: Request, db: Session = Depends(get_db)):
    pizza = db.query(Menu).filter(Menu.name == pizza_name).first()
    return templates.TemplateResponse("pizza.html", {"request": request, "pizza": pizza})

@app.post("/register")
async def register(name:Annotated[str, Form()], email : Annotated[str, Form()], password: Annotated[str, Form()], db: Session = Depends(get_db)):
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode("utf-8")
        user_name, user_email = name, email
        if(db.query(User).filter(User.email == email)) != None:
            raise HTTPException(status_code=400, detail="User with same email is already exists")
        new_user = User(name = user_name, email = user_email, password = hashed_password)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        redirect_response = RedirectResponse(url="/login", status_code=303)
        return redirect_response

@app.get("/register")
async def registerr(request : Request, db: Session = Depends(get_db)):
    token = request.cookies.get("my_access_token")
    if token:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            if payload.get("type") == "access":
                return RedirectResponse(url="/profile", status_code=303)
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
            pass
    return templates.TemplateResponse("register.html", {"request": request})

@app.post("/login")
async def login(email : Annotated[str, Form()], password1: Annotated[str, Form()], response: Response, db: Session = Depends(get_db)):
        encoded_password = password1.encode('utf-8')
        user = db.query(User).filter(User.email == email).first()
        if user is None:
            raise HTTPException(status_code=400, detail="Invalid email or password")
        users_password = user.password.encode('utf-8')
        if bcrypt.checkpw(encoded_password, users_password):
            user_id = user.id
            token = create_access_token(user_id=str(user_id))
            redirect_response = RedirectResponse(url="/profile", status_code=303)
            redirect_response.set_cookie(
                key="my_access_token",
                value=token,
                httponly=True,
                path="/"
            )
            return redirect_response 
        else:
            raise HTTPException(status_code=400, detail="Invalid email or password")

@app.get("/login")
async def loginn(request : Request, db: Session = Depends(get_db)):
    token = request.cookies.get("my_access_token")
    if token:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            if payload.get("type") == "access":
                return RedirectResponse(url="/profile", status_code=303)
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
            pass  
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/profile")
async def profile(request : Request, payload : dict = Depends(access_token_required), db: Session = Depends(get_db)):
    if isinstance(payload, RedirectResponse):
        return payload
    user_id = payload.get("sub")
    print(user_id)
    user = db.query(User).filter(User.id == user_id).first()

    return templates.TemplateResponse("profile.html", {"request": request, "user": user})

@app.get("/profile/orders")
async def orders(request: Request, db: Session = Depends(get_db), payload : dict = Depends(access_token_required)):
    if isinstance(payload, RedirectResponse):
        return payload
    user_id = payload.get("sub")
    orders = db.query(Orders).filter(Orders.user_id == user_id)
    return templates.TemplateResponse("orders.html", {"request": request, "orders": orders})

@app.get("/order")
async def order(request: Request):
    return templates.TemplateResponse("order.html", {"request": request})

@app.post("/makeorder")
async def makeorder(
    request: Request,
    peperoni_amount: Annotated[int, Form()],
    caprese_amount: Annotated[int, Form()],
    cheese_amount: Annotated[int, Form()],
    db: Session = Depends(get_db),
    payload: dict = Depends(access_token_required)
):
    if isinstance(payload, RedirectResponse):
        return payload 
    user_id = payload.get("sub")
    menu = db.query(Menu)

    peperoni = menu.filter(Menu.name == "Peperoni").first()
    caprese = menu.filter(Menu.name == "Caprese").first()
    cheese = menu.filter(Menu.name == "Cheese").first()

    if not all([peperoni, caprese, cheese]):
        raise HTTPException(status_code=400, detail="Menu items not found")

    total_price = (
        peperoni_amount * peperoni.price
        + caprese_amount * caprese.price
        + cheese_amount * cheese.price
    )

    new_order = Orders(
        content={
            "peperoni": peperoni_amount,
            "caprese": caprese_amount,
            "cheese": cheese_amount
        },
        price=total_price,
        user_id=user_id
    )

    db.add(new_order)
    db.commit()
    db.refresh(new_order)
    redirect_response = RedirectResponse(url="/profile/orders", status_code=303)
    return redirect_response

@app.get("/logout")
async def logout():
    response = RedirectResponse(url="/", status_code=303)
    response.delete_cookie("my_access_token")
    return response
