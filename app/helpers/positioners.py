from customtkinter import *

def h1(label: CTkLabel):
    label.pack(ipady=15, ipadx=25)

def h2(label: CTkLabel):
    label.pack(ipady=12, ipadx=25)

def nest(inner: CTkFrame):
    inner.place(relx=0.5, rely=0.5, anchor="center")

def btn(button: CTkButton):
    button.pack(ipady=5,ipadx=8, padx=10, pady=7)