import os
from customtkinter import *
from utils import logger
from ui.handlers import *
from ui.positioners import *

def app(host, port):

    def switch_to(frame_fn):
        logger.info(f"Przełączam na {frame_fn.__name__}")
        nonlocal current_frame
        if current_frame:
            current_frame.destroy()
        current_frame = frame_fn()
        current_frame.pack(expand=True, fill=BOTH)

    def render_main():
        frame = CTkFrame(root)
        inner = CTkFrame(frame) # Wrapper

        h1(CTkLabel(inner, text="Strona główna", font=("Arial", 20)))
        btn(CTkButton(inner, text="Logowanie", command=lambda: switch_to(render_login)))

        nest(inner)

        return frame

    def render_login():
        frame = CTkFrame(root)
        inner = CTkFrame(frame)

        h1(CTkLabel(inner, text="Strona logowania", font=("Arial", 20)))

        login = CTkEntry(inner, justify=CENTER)
        login.pack(pady=5)
    
        passwd = CTkEntry(inner, show="*", justify=CENTER)
        passwd.pack(pady=5)

        btn(CTkButton(inner, text="Zaloguj", command=lambda: on_login_click(login, passwd, inner, register=True)))
        btn(CTkButton(inner, text="Rejestracja", command=lambda: switch_to(render_register)))
        btn(CTkButton(inner, text="Wróć do głownej", command=lambda: switch_to(render_main)))

        nest(inner)

        return frame

    def render_register():
        frame = CTkFrame(root)
        inner = CTkFrame(frame)

        h1(CTkLabel(inner, text="Strona rejestracji", font=("Arial", 20)))

        login = CTkEntry(inner, justify=CENTER)
        login.pack(pady=5)

        passwd = CTkEntry(inner, show="*", justify=CENTER)
        passwd.pack(pady=5)

        btn(CTkButton(inner, text="Zarejestruj", command=lambda: on_login_click(login, passwd, inner, register=True)))
        btn(CTkButton(inner, text="Wróć do logowania", command=lambda: switch_to(render_login)))
        btn(CTkButton(inner, text="Wróć do głownej", command=lambda: switch_to(render_main)))

        nest(inner)

        return frame

    err: CTkLabel | None = None
    def on_login_click(login: CTkEntry, passwd: CTkEntry, inner: CTkFrame, register = False):
            l = login.get()
            p = passwd.get()
            logger.info(f"Login: {l}, Hasło: {p}")
            nonlocal err
            if not l or not p:
                err.pack_forget() if err else None
                err = CTkLabel(inner, text="Login i hasło nie mogą być puste!", text_color="red")
                err.pack(pady=5)
                return
            if len(p) < 8:
                err.pack_forget() if err else None
                err = CTkLabel(inner, text="Hasło musi mieć co najmniej 8 znaków!", text_color="red")
                err.pack(pady=5)
                return
            if register: handle_register(l, p)
            else: handle_login(l, p)

    logger.info("Uruchamiam aplikację")

    # W root żadnych widgetów nie powinno być, lecz oni będą tu renderowane dynamicznie

    root = CTk()
    root.title("Frog Store")
    root.iconbitmap(os.path.join(os.getcwd(), "app", "resources", "favicon.ico"))
    root.geometry(f"1280x720+{(root.winfo_screenwidth() - 1280) // 2}+{(root.winfo_screenheight() - 720) // 2}")
    root.resizable(False, False)

    set_appearance_mode("dark")
    set_default_color_theme("green")
    set_widget_scaling(1.0)

    current_frame = None

    switch_to(render_main)

    root.mainloop()