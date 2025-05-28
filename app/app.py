import os
from customtkinter import *
from utils import logger
from helpers.api import *
from helpers.positioners import *
from secrets import token_urlsafe

def app(host, port):

    hostname = f"{host}:{port}"

    def switch_to(frame_fn):
        logger.info(f"Przełączam na {frame_fn.__name__}")
        nonlocal current_frame
        if current_frame:
            current_frame.destroy()
        current_frame = frame_fn()

        header = CTkFrame(current_frame)  # header
        header.pack(pady=10, padx=10, fill=X, expand=True, anchor=N)
        h1(CTkLabel(header, text="Frog Store", font=("Arial", 24)))
        h1(CTkLabel(header, 
                    text=
                    f"Witaj, {current_session['name']} {current_session['surname']}" 
                    if current_session else "Witaj, gościu!",
                    font=("Arial", 16))
                )
        current_frame.pack(expand=True, fill=BOTH)

    def render_main():
        frame = CTkFrame(root)
        inner = CTkFrame(frame) # Wrapper

        h1(CTkLabel(inner, text="Strona główna", font=("Arial", 20)))
        btn(CTkButton(inner, text="Logowanie", command=lambda: switch_to(render_login)))
        btn(CTkButton(inner, text="Przeglądaj katalog", command=lambda: switch_to(render_catalog)))

        nest(inner)

        return frame
    
    def render_catalog():
        frame = CTkFrame(root)
        inner = CTkFrame(frame)

        h1(CTkLabel(inner, text="Katalog produktów", font=("Arial", 20)))

        products = list_products(client_token, hostname)
        logger.info(f"Pobrano produkty: {products} - {type(products)}")

        if products.get("error"):
            CTkLabel(inner, text=f"Błąd podczas pobierania produktów: {products.get('error')}", text_color="red").pack(pady=5)
        else:
            if len(products.get("products")) == 0:
                h2(CTkLabel(inner, text="Brak produktów w katalogu", text_color="red"))
                logger.log("Wyświetlam brak produktow")
            else:
                columns = get_product(0, client_token, hostname)
                if columns.get("error"):
                    CTkLabel(inner, text=f"Błąd podczas pobierania nagłowków: {products.get('error')}", text_color="red").pack(pady=5)
                else:
                    nest(render_table(inner, columns, products.get("products")), padx=20, pady=20)

        if current_session and current_session.get("is_admin", True):
            btn(CTkButton(inner, text="Dodaj produkt", command=lambda: switch_to(render_add_product)))
            btn(CTkButton(inner, text="Usuń produkt", command=lambda: switch_to(render_remove_product)))
                
        btn(CTkButton(inner, text="Wróć do głownej", command=lambda: switch_to(render_main)))
        
        nest(inner)
        return frame
    
    def render_table(frame: CTkFrame, columns: list, rows: dict):
        tframe = CTkFrame(frame, bg_color="#A0A79D")
        header:list[CTkLabel] = []
        for i, col in enumerate(columns):
            header_cell = CTkLabel(tframe, text=col, font=("Arial", 15, "bold"), bg_color="#4C872B", border_color="#FFFFFF")
            header_cell.grid(row=0, column=i, padx=10, pady=5)
            header.insert(header_cell)
        
        oldwidth:int
        
        for i, row in enumerate(rows):
            for j, data in enumerate(row):
                cur_width = len(data) * 3
                if cur_width > oldwidth:
                    header[j].configure(width=cur_width)
                data_cell = CTkLabel(tframe, width=oldwidth, text=data, font=("Arial", 12, "regular"), border_color="#FFFFFF")
                data_cell.grid(row=i, column=j, padx=10, pady=5)

        return tframe



    def render_add_product():
        frame = CTkFrame(root)
        inner = CTkFrame(frame)

        h1(CTkLabel(inner, text="Dodaj produkt", font=("Arial", 20)))

        name = CTkEntry(inner, justify=CENTER, placeholder_text="Nazwa produktu")
        name.pack(pady=5)

        price = CTkEntry(inner, justify=CENTER, placeholder_text="Cena (PLN)")
        price.pack(pady=5)

        quantity = CTkEntry(inner, justify=CENTER, placeholder_text="Ilość")
        quantity.pack(pady=5)

        description = CTkEntry(inner, justify=CENTER, placeholder_text="Opis")
        description.pack(pady=5)

        category = CTkEntry(inner, justify=CENTER, placeholder_text="Kategoria")
        category.pack(pady=5)

        btn(CTkButton(inner, text="Dodaj produkt", command=lambda: on_add_product_click(name, price, quantity, description, category, inner)))
        btn(CTkButton(inner, text="Wróć do katalogu", command=lambda: switch_to(render_catalog)))
        
        nest(inner)

        return frame
    
    def on_add_product_click(name: CTkEntry, price: CTkEntry, quantity: CTkEntry, description: CTkEntry, category: CTkEntry, inner: CTkFrame):
        n = str(name.get())
        p = str(price.get())
        q = str(quantity.get())
        d = str(description.get())
        c = str(category.get())

        logger.info(f"Dodawanie produktu: {n}, {p}, {q}, {d}, {c}")
        nonlocal err
        if not n or not p or not q or not d or not c:
            err.pack_forget() if err else None
            err = CTkLabel(inner, text="Wszystkie pola muszą być wypełnione!", text_color="red")
            logger.error("Proba dodania produktu z pustymi polami")
            err.pack(pady=5)
            return
        
        response = add_product({
            "name": n,
            "price": float(p),
            "quantity": int(q),
            "description": d,
            "category": c
        }, client_token, hostname)

        logger.info(f"Reakcja serwera: {response}")
        if not response.get("error"):
            logger.info("Produkt dodany pomyślnie")
            err.pack_forget() if err else None
            CTkLabel(inner, text="Produkt dodany pomyślnie!", text_color="green").pack(pady=5)
        else:
            logger.error("Błąd podczas dodawania produktu")
            err.pack_forget() if err else None
            err = CTkLabel(inner, text=f"Błąd podczas dodawania produktu: {response.get('error')}", text_color="red")
            err.pack(pady=5)

    def render_remove_product():
        frame = CTkFrame(root)
        inner = CTkFrame(frame)

        h1(CTkLabel(inner, text="Usuń produkt", font=("Arial", 20)))

        product_id = CTkEntry(inner, justify=CENTER, placeholder_text="ID produktu do usunięcia")
        product_id.pack(pady=5)

        btn(CTkButton(inner, text="Usuń produkt", command=lambda: on_remove_product_click(product_id, inner)))
        btn(CTkButton(inner, text="Wróć do katalogu", command=lambda: switch_to(render_catalog)))

        nest(inner)

        return frame

    def on_remove_product_click(product_id: CTkEntry, inner: CTkFrame):
        pid = str(product_id.get())
        logger.info(f"Usuwanie produktu o ID: {pid}")
        nonlocal err
        if not pid:
            err.pack_forget() if err else None
            err = CTkLabel(inner, text="ID produktu nie może być puste!", text_color="red")
            logger.error("Proba usunięcia produktu z pustym ID")
            err.pack(pady=5)
            return
        
        response = remove_product(int(pid), client_token, hostname)

        logger.info(f"Odpoeiedz serwera: {response}")
        if not response.get("error"):
            logger.info("Produkt usunięty pomyślnie")
            err.pack_forget() if err else None
            CTkLabel(inner, text="Produkt usunięty pomyślnie!", text_color="green").pack(pady=5)
        else:
            logger.error("Błąd podczas usuwania produktu")
            err.pack_forget() if err else None
            err = CTkLabel(inner, text=f"Błąd podczas usuwania produktu: {response.get('error')}", text_color="red")
            err.pack(pady=5)

    def render_login():
        frame = CTkFrame(root)
        inner = CTkFrame(frame)

        h1(CTkLabel(inner, text="Strona logowania", font=("Arial", 20)))

        login = CTkEntry(inner, justify=CENTER)
        login.pack(pady=5)
    
        passwd = CTkEntry(inner, show="*", justify=CENTER)
        passwd.pack(pady=5)

        btn(CTkButton(inner, text="Zaloguj", command=lambda: on_login_click(login, passwd, inner)))
        btn(CTkButton(inner, text="Rejestracja", command=lambda: switch_to(render_register)))
        btn(CTkButton(inner, text="Wróć do głownej", command=lambda: switch_to(render_main)))

        nest(inner)

        return frame

    def render_register():
        frame = CTkFrame(root)
        inner = CTkFrame(frame)

        h1(CTkLabel(inner, text="Strona rejestracji", font=("Arial", 20)))

        login = CTkEntry(inner, justify=CENTER, placeholder_text="Login")
        login.pack(pady=5)

        passwd = CTkEntry(inner, show="*", justify=CENTER, placeholder_text="Hasło (min. 8 znaków)")
        passwd.pack(pady=5)

        name = CTkEntry(inner, justify=CENTER, placeholder_text="Imię")
        name.pack(pady=5)

        surname = CTkEntry(inner, justify=CENTER, placeholder_text="Nazwisko")
        surname.pack(pady=5)

        age = CTkEntry(inner, justify=CENTER, placeholder_text="Wiek")
        age.pack(pady=5)

        btn(CTkButton(inner, text="Zarejestruj", command=lambda: on_login_click(login, passwd, inner, True, name, surname, age)))
        btn(CTkButton(inner, text="Wróć do logowania", command=lambda: switch_to(render_login)))
        btn(CTkButton(inner, text="Wróć do głownej", command=lambda: switch_to(render_main)))

        nest(inner)

        return frame

    err: CTkLabel | None = None

    def on_login_click(login: CTkEntry, passwd: CTkEntry, inner: CTkFrame, register = False, name: CTkEntry | None = None, surname: CTkEntry | None = None, age: CTkEntry | None = None):
            l = str(login.get())
            p = str(passwd.get())
            n = str(name.get()) if name else None
            s = str(surname.get())  if surname else None
            a = str(age.get()) if age else None
            
            logger.info(f"Login: {l}, Hasło: {p}")
            nonlocal err, registered, current_session
            if not l or not p:
                err.pack_forget() if err else None
                err = CTkLabel(inner, text="Login i hasło nie mogą być puste!", text_color="red")
                logger.error("Proba logowania z pustym loginem lub hasłem")
                err.pack(pady=5)
                return
            if len(p) < 8:
                err.pack_forget() if err else None
                err = CTkLabel(inner, text="Hasło musi mieć co najmniej 8 znaków!", text_color="red")
                logger.error("Proba logowania z hasłem krótszym niż 8 znaków")
                err.pack(pady=5)
                return
            if register: 
                if not n or not s or not a:
                    err.pack_forget() if err else None
                    err = CTkLabel(inner, text="Wszystkie pola muszą być wypełnione!", text_color="red")
                    logger.error("Proba rejestracji z pustymi polami")
                    err.pack(pady=5)
                    return
                
                response = handle_register(l, p, client_token, hostname, n, s, a)
                logger.info(f"Rejestracja: {response}")
                if not response.get("error"):
                    logger.info("Rejestracja zakończona pomyślnie")
                    err.pack_forget() if err else None
                    if not registered:
                        CTkLabel(inner, text="Rejestracja zakończona pomyślnie! Możesz się teraz zalogować.", text_color="green").pack(pady=5)
                    registered = True
                else:
                    logger.error("Rejestracja nie powiodła się")
                    err.pack_forget() if err else None
                    err = CTkLabel(inner, text=f"Rejestracja nie powiodła się! {response.get("error")}", text_color="red")
                    err.pack(pady=5)
            else:
                response = handle_login(l, p, client_token, hostname)
                logger.info(f"Logowanie: {response}")
                if not response.get("error"):
                    logger.info("Logowanie zakończone pomyślnie")
                    err.pack_forget() if err else None
                    current_session = response;
                    CTkLabel(inner, text="Zalogowano pomyślnie!", text_color="green").pack(pady=5)
                    switch_to(render_main)
                else:
                    logger.error("Logowanie nie powiodło się")
                    err.pack_forget() if err else None
                    err = CTkLabel(inner, text=f"Logowanie nie powiodło się! {response.get("error")}", text_color="red")
                    err.pack(pady=5)

    logger.info("Uruchamiam aplikację")

    # W root żadnych widgetów nie powinno być, lecz oni będą tu renderowane dynamicznie

    client_token = token_urlsafe(16)
    registered = False
    current_session = None
    current_frame = None


    logger.info(f"Generuję token klienta: {client_token}")

    root = CTk()
    root.title("Frog Store")
    root.iconbitmap(os.path.join(os.getcwd(), "resources", "favicon.ico"))
    root.geometry(f"1280x720+{(root.winfo_screenwidth() - 1280) // 2}+{(root.winfo_screenheight() - 720) // 2}")
    root.resizable(False, False)

    set_appearance_mode("dark")
    set_default_color_theme("green")
    set_widget_scaling(1.0)

    switch_to(render_main)

    root.mainloop()