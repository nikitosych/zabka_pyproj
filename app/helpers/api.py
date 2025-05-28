import requests as req

def handle_login(login, password, client_token: str, host):

    res = req.post(
        f"http://{host}/login?performer_token={client_token}",
        json={"login": login, "password": password, "token": client_token}
    )

    return res.json() if res.status_code == 200 else {"error": res.text}


def handle_register(login, password, client_token, host, name, surname, age):
    res = req.post(
        f"http://{host}/register?performer_token={client_token}",
        json={
            "login": login,
            "password": password,
            "name": name,
            "surname": surname,
            "age": age,
            "token": client_token
        }
    )

    return res.json() if res.status_code == 200 else {"error": res.text}


def list_products(client_token: str, host):
    res = req.get(f"http://{host}/products?performer_token={client_token}")
    return res.json() if res.status_code == 200 else {"error": res.text}


def add_product(product: dict, client_token: str, host):
    res = req.post(
        f"http://{host}/add_product?performer_token={client_token}",
        json=product
    )
    return res.json() if res.status_code == 200 else {"error": res.text}


def remove_product(product_id: int, client_token: str, host):
    res = req.post(
        f"http://{host}/remove_product/{product_id}?performer_token={client_token}"
    )
    return res.json() if res.status_code == 200 else {"error": res.text}

def get_product(product_id: int, client_token: str, host):
    res = req.get(
        f"http://{host}/products/{product_id}?performer_token={client_token}"
    )
    return res.json() if res.status_code == 200 else {"error": res.text}
