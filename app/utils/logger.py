from typing import Literal


def log(message: str = "", type: Literal["info", "error"] = "info") -> None:
    """
    Wyświetla komunikat na konsoli

    Args:
        message (str): Treść komunikatu
        type (Literal["info", "error"]): Typ komunikatu, domyślnie "info"
    """
    if type == "info":
        print(f"[INFO] {message}")
    elif type == "error":
        print(f"[ERROR] {message}")
    else:
        raise ValueError("Nieprawidłowy typ komunikatu. Użyj 'info' lub 'error'")
    
def info(message: str) -> None:
    """
    Wyświetla komunikat typu [INFO]

    Args:
        message (str): Treść komunikatu
    """
    log(message, "info")

def error(message: str) -> None:
    """
    Wyświetla komunikat typu [ERROR]

    Args:
        message (str): Treść komunikatu
    """
    log(message, "error")