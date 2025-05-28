from customtkinter import *

def h1(label: CTkLabel, **kwargs):
    label.pack(ipady=15, ipadx=25, **kwargs)

def h2(label: CTkLabel, **kwargs):
    label.pack(ipady=12, ipadx=25, **kwargs)

def nest(inner: CTkFrame, **kwargs):
    inner.place(relx=0.5, rely=0.5, anchor="center", **kwargs)

def btn(button: CTkButton, **kwargs):
    button.pack(ipady=5,ipadx=8, padx=10, pady=7, **kwargs)