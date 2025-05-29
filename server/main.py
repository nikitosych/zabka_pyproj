"""
Prosty API serwer do zarządzania produktami i użytkownikami.
Serwer ten umożliwia dodawanie, usuwanie i przeglądanie produktów oraz zarządzanie użytkownikami 
w systemie
Serwer korzysta z FastAPI do obsługi ządań HTTP i Pandas do zarządzania danymi w formacie CSV i excel
"""


import os
import pandas as pd
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from random import randint

database = os.path.join(os.getcwd(), "DATABASE")
products_file = os.path.join(database, "products.csv")
users_file = os.path.join(database, "customers.xlsx")

current_sessions = {}  # Proste zabiezpieczeństw


class Product(BaseModel):
    name: str
    price: str
    quantity: int
    description: str
    category: str

class User(BaseModel):
    login: str
    password: str  # fernet encrypted
    name: str | None = None
    surname: str | None = None
    age: str | None = None
    token: str

app = FastAPI()

def read_products_file(filepath):
    try:
        return pd.read_csv(filepath)
    except FileNotFoundError:
        df = pd.DataFrame(columns=['id', 'name', 'price', 'quantity', 'description', 'category'])
        df.to_csv(filepath, index=False)
        return df

def read_users_file(filepath):
    try:
        return pd.read_excel(filepath)
    except FileNotFoundError:
        df = pd.DataFrame(columns=['id', 'name', 'surname', 'age', 'login', 'password', 'admin'])
        df.to_excel(filepath, index=False)
        return df

def write_file(filepath, df: pd.DataFrame, index=True, is_excel=False):
    df = df.drop_duplicates()
    if is_excel:
        df.to_excel(filepath, index=index)
    else:
        df.to_csv(filepath, index=index)

def check_token(performer_token: str, requiresAdmin: bool = False) -> bool:
    if performer_token not in current_sessions.values():
        return False

    if requiresAdmin:
        users = read_users_file(users_file)
        login = next((k for k, v in current_sessions.items() if v == performer_token), None)
        user = users[users["login"] == login]

        if user.empty or not bool(user.iloc[0]["admin"]):
            return False

    return True

@app.get("/products")
async def get_products():
    try:
        products = read_products_file(products_file)
        return JSONResponse(content={"products": products.to_dict(orient="records")})
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.get("/products/{product_id}")
async def get_product(product_id: int):
    try:
        products = read_products_file(products_file)

        product = products[products['id'] == product_id]
        if product.empty:
            return JSONResponse(content={"error": "Product not found"}, status_code=404)
        return JSONResponse(content={k: str(v) for k, v in product.to_dict(orient="records")[0].items()})
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.post("/add_product")
async def add_product(product: Product, performer_token: str):
    try:
        if not check_token(performer_token, requiresAdmin=True):
            return JSONResponse(content={"error": "Brak uprawnień do wykonania tej operacji"}, status_code=401)
        products = read_products_file(products_file)
        new_id = (products['id'].max() + 1) if not products.empty else 1
        new_product = pd.DataFrame([{
            'id': new_id,
            'name': product.name,
            'price': product.price,
            'quantity': product.quantity,
            'description': product.description,
            'category': product.category
        }])
        products = pd.concat([products, new_product], ignore_index=True)
        write_file(products_file, products)
        return JSONResponse(content={"message": "Product added successfully"})
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.post("/remove_product/{product_id}")
async def remove_product(product_id: int | str, performer_token: str):
    try:
        if not check_token(performer_token, requiresAdmin=True):
            return JSONResponse(content={"error": "Brak uprawnień do wykonania tej operacji"}, status_code=401)
        
        products = read_products_file(products_file)

        # https://stackoverflow.com/questions/3501382/checking-whether-a-variable-is-an-integer-or-not
        if isinstance(product_id, int):
            if products[products['id'] == product_id].empty:
                return JSONResponse(content={"message": "Nie znaleziono produktu"}, status_code=404)
            products = products[products['id'] != product_id]
        else:
            if products[products['name'] == product_id].empty:
                return JSONResponse(content={"message": "Nie znaleziono produktu"}, status_code=404)
            products = products[products['name'] != product_id]

        write_file(users_file, products)

        return JSONResponse(content={"message": "Product removed successfully"}, status_code=200)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.get("/users")
async def list_users():
    try:
        users = read_users_file(users_file)
        return JSONResponse(content={"users": users.to_dict(orient="records")})
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.post("/register")
async def register(user: User):
    try:
        if user.login in current_sessions:
            return JSONResponse(content={"error": "Użytkownik o podanym loginie jest już zalogowany"}, status_code=400)
        
        users = read_users_file(users_file)

        if not users[users["login"] == user.login].empty:
            return JSONResponse(content={"error": "Użytkownik o podanym login już istnieje w BD"}, status_code=400)

        rid = 1
        ids= users["id"].to_list()
        while True:
            c = randint(1, 9999)
            if c not in ids:
                rid = c
                break

        new_user = pd.DataFrame([{
            'id': rid,
            'name': user.name,
            'surname': user.surname,
            'age': user.age,
            'login': user.login,
            'password': user.password,
            'admin': False
        }])
        users = pd.concat([users, new_user], ignore_index=True)
        write_file(users_file, users, is_excel=True)
        user_id = new_user["id"].iloc[0]
        open(os.path.join(database, f"{user_id}.txt"), "w").close()
        return JSONResponse(content={"message": "Pomyślnie zarejestrowano użytkownika"})
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.post("/login")
async def login(user: User):
    try:
        users = read_users_file(users_file)
        target = users[users["login"] == user.login]

        if target.empty:
            return JSONResponse(content={"error": "Nie udało się znaleźć użytkownika"}, status_code=400)
        
        if target.shape[0] > 1:
            return JSONResponse(content={"error": "W bazie znajduje się więcej niż 1 użytkownik o podanym loginie"})

        stored_password = str(target.iloc[0]["password"])
        
        if stored_password != user.password:
            return JSONResponse(content={"error": f"Błędne hasło ({stored_password} {type(stored_password)}!={user.password} {type(user.password)})"}, status_code=401)
    
        current_sessions[user.login] = user.token
        return JSONResponse(content={
            "message": "Pomyślnie zalogowano", 
            "login": str(target.iloc[0]["login"]),
            "name": str(target.iloc[0]["name"]),
            "surname": str(target.iloc[0]["surname"]),
            "age": str(target.iloc[0]["age"]),
            "token": str(user.token),
        })
        
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.get("/logout/{login}")
async def logout(login: str, performer_token: str):
    if not check_token(performer_token):
        return JSONResponse(content={"error": "Brak uprawnień do wykonania tej operacji"}, status_code=401)
    if login in current_sessions:
        del current_sessions[login]
        return JSONResponse(content={"message": "Pomyślnie wylogowano"}, status_code=200)
    return JSONResponse(content={"error": "Użytkownik nie jest zalogowany"}, status_code=400)

@app.post("/remuser/{login}")
async def remuser(login: str, performer_token: str):    
    try:
        if not check_token(performer_token, requiresAdmin=True):
            return JSONResponse(content={"error": "Brak uprawnień do wykonania tej operacji"}, status_code=401)

        users = read_users_file(users_file)
        if users[users["login"] == login].empty:
            return JSONResponse(content={"error": "Użytkownik o podanym loginie nie istnieje"}, status_code=404)

        users = users[users["login"] != login]
        write_file(users_file, users, is_excel=True)
        return JSONResponse(content={"message": "Pomyślnie usunięto użytkownika"})
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.get("/check_token/{login}")
async def check_user_token(performer_token: str, login: str | None = None):
    if not check_token(performer_token):
        return JSONResponse(content={"error": "Brak uprawnień do wykonania tej operacji"}, status_code=401)
    
    if login and login in current_sessions:
        return JSONResponse(content={"message": "Użytkownik jest zalogowany"}, status_code=200)
    
    return JSONResponse(content={"error": "Użytkownik nie jest zalogowany"}, status_code=400)
