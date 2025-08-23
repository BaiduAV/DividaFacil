from datetime import datetime
from typing import Union


def brl(value) -> str:
    try:
        num = float(value)
    except Exception:
        return str(value)
    s = f"{num:,.2f}"
    s = s.replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {s}"


def datebr(value: Union[str, datetime]):
    try:
        if hasattr(value, "strftime"):
            return value.strftime("%d/%m/%Y")
        if isinstance(value, str):
            try:
                dt = datetime.fromisoformat(value)
                return dt.strftime("%d/%m/%Y")
            except Exception:
                return value
    except Exception:
        return value
    return str(value)


def split_label(value: str) -> str:
    mapping = {
        "EQUAL": "Igual",
        "EXACT": "Valores exatos",
        "PERCENTAGE": "Percentuais",
    }
    return mapping.get(value, value)


def monthbr(value: str) -> str:
    try:
        if isinstance(value, str) and len(value) >= 7 and value[4] == "-":
            year = value[0:4]
            month = int(value[5:7])
            meses = [
                "",
                "jan",
                "fev",
                "mar",
                "abr",
                "mai",
                "jun",
                "jul",
                "ago",
                "set",
                "out",
                "nov",
                "dez",
            ]
            if 1 <= month <= 12:
                return f"{meses[month]}/{year}"
    except Exception:
        pass
    return value
