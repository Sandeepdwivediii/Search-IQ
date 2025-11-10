from __future__ import annotations
from typing import List, Dict, Optional, Set
import re
import pandas as pd
from .dependency_engine import init_all

def _norm(s: str|None) -> str:
    return (s or "").strip().lower()

def _tokenize_models(cell: str) -> Set[str]:
    raw = (cell or "").replace(",", ";")
    return {t.strip().lower() for t in raw.split(";") if t.strip()}

class WalmartSparePartsAdapter:
    def __init__(self):
        d = init_all()
        self.orders = d.orders_df.copy()
        self.spares = d.spares_df.copy()

        self.orders["company_norm"] = self.orders["company"].astype(str).str.lower()
        self.orders["product_model_norm"] = self.orders["product_model"].astype(str).str.lower()
        self.orders["category_norm"] = self.orders["category"].astype(str).str.lower()

        self.spares["company_norm"] = self.spares["company"].astype(str).str.lower()
        self.spares["category_norm"] = self.spares["category"].astype(str).str.lower()
        self.spares["part_name_norm"] = self.spares["part_name"].astype(str).str.lower()
        self.spares["compatible_tokens"] = self.spares["compatible_models"].apply(_tokenize_models)

    def candidate_orders(self, brand: Optional[str], category: Optional[str],
                         year: Optional[int], month: Optional[int],
                         user_name: Optional[str]) -> List[Dict]:
        df = self.orders.copy()
        if brand:   df = df[df["company_norm"] == _norm(brand)]
        if category:df = df[df["category_norm"] == _norm(category)]
        if year:
            dt = pd.to_datetime(df["purchase_date"], errors="coerce")
            df = df[dt.dt.year == int(year)]
        if month:
            dt = pd.to_datetime(df["purchase_date"], errors="coerce")
            df = df[dt.dt.month == int(month)]
        if user_name:
            df = df[df["user_name"].astype(str).str.contains(user_name, case=False, na=False)]
        if df.empty: return []
        df = df.sort_values("purchase_date", ascending=False)
        return [{
            "invoice_number": r["invoice_number"],
            "user_name": r["user_name"],
            "brand": r["company"],
            "category": r["category"],
            "product_model": r["product_model"],
            "purchase_date": r["purchase_date"],
        } for _, r in df.iterrows()]

    def _score_row(self, row: pd.Series, brand: str, device_model: str, fault_keyword: str) -> float:
        b, m, f = _norm(brand), _norm(device_model), _norm(fault_keyword)
        company_match = 1.0 if row.get("company_norm","") == b else 0.0
        model_match   = 1.0 if (m and m in row.get("compatible_tokens", set())) else 0.0
        fault_match   = 1.0 if (f and f in row.get("part_name_norm","")) else 0.0
        return float(0.4*company_match + 0.4*model_match + 0.2*fault_match)

    def recommend_with_invoice(self, invoice_number: str, fault_keyword: str, top_n: int = 3):
        order = self.orders[self.orders["invoice_number"] == invoice_number]
        if order.empty: return []
        order = order.iloc[0]
        brand = order.get("company","")
        category = _norm(order.get("category"))
        model = order.get("product_model","")

        cands = self.spares.copy()
        if category: cands = cands[cands["category_norm"] == category]
        if brand:    cands = cands[cands["company_norm"] == _norm(brand)]
        if cands.empty: return []

        cands = cands.copy()
        cands["__score"] = cands.apply(lambda r: self._score_row(r, brand, model, fault_keyword), axis=1)
        cands = cands.sort_values("__score", ascending=False).head(top_n)
        return [{
            "part_name": r["part_name"],
            "part_number": r["part_number"],
            "price": float(r["price_usd"]) if pd.notna(r["price_usd"]) else 0.0,
            "availability": "in_stock",
            "compatibility_score": float(r["__score"]),
            "description": None,
            "image_url": None,
            "brand": r["company"],
            "category": r["category"],
        } for _, r in cands.iterrows()]

    def recommend_without_invoice(self, brand: str, device_model: str, fault_keyword: str, top_n: int = 3):
        cands = self.spares.copy()
        if brand: cands = cands[cands["company_norm"] == _norm(brand)]
        if cands.empty: return []
        cands = cands.copy()
        cands["__score"] = cands.apply(lambda r: self._score_row(r, brand, device_model, fault_keyword), axis=1)
        cands = cands.sort_values("__score", ascending=False).head(top_n)
        return [{
            "part_name": r["part_name"],
            "part_number": r["part_number"],
            "price": float(r["price_usd"]) if pd.notna(r["price_usd"]) else 0.0,
            "availability": "in_stock",
            "compatibility_score": float(r["__score"]),
            "description": None,
            "image_url": None,
            "brand": r["company"],
            "category": r["category"],
        } for _, r in cands.iterrows()]

def parse_free_text(msg: str):
    text = (msg or "").strip()
    m_fault = re.search(r"(magnetron|compressor|display|screen|panel|motor|battery|filter|fan|sensor|thermostat)", text, re.I)
    fault = m_fault.group(1) if m_fault else None

    categories = ["microwave","refrigerator","fridge","ac","air conditioner","washing machine","tv","television","laptop","smartphone"]
    category = None
    for c in categories:
        if re.search(rf"\b{re.escape(c)}\b", text, re.I):
            category = "air conditioner" if c in ["ac","air conditioner"] else ("refrigerator" if c in ["refrigerator","fridge"] else c)
            break

    year = None; month = None
    m_year = re.search(r"\b(20\d{2})\b", text)
    if m_year: year = int(m_year.group(1))
    month_names = {name.lower(): i for i, name in enumerate(
        ["January","February","March","April","May","June","July","August","September","October","November","December"], 1)}
    for name, i in month_names.items():
        if re.search(rf"\b{name}\b", text, re.I):
            month = i; break

    m_brand = re.search(r"\b(Samsung|LG|Whirlpool|Daikin|Sony|Bosch|IFB|Haier)\b", text, re.I)
    brand = m_brand.group(1) if m_brand else None

    m_model = re.search(r"\b([A-Z0-9]{4,})\b", text)
    device_model = m_model.group(1) if m_model else None

    return {"fault": fault, "category": category, "year": year, "month": month, "brand": brand, "device_model": device_model}
