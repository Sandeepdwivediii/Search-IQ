import os
from typing import Optional
import pandas as pd
from dotenv import load_dotenv

load_dotenv()
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

DEFAULT_ITEMS_CSV = os.getenv("ITEMS_CSV", os.path.join(BASE_DIR, "data", "items.csv"))
DEFAULT_ORDERS_CSV = os.getenv("ORDERS_CSV", os.path.join(BASE_DIR, "data", "spares", "xyz_user_orders.csv"))
DEFAULT_SPARES_CSV = os.getenv("SPARES_CSV", os.path.join(BASE_DIR, "data", "spares", "xyz_spares.csv"))

class Dependencies:
    items_df: Optional[pd.DataFrame] = None
    orders_df: Optional[pd.DataFrame] = None
    spares_df: Optional[pd.DataFrame] = None

deps = Dependencies()

def _ensure_cols(df: pd.DataFrame, cols):
    for c in cols:
        if c not in df.columns:
            df[c] = None

def load_items_df(path: str = DEFAULT_ITEMS_CSV):
    df = pd.read_csv(path)
    _ensure_cols(df, ["id","title","brand","category","price","rating","description","url","image_url"])
    return df

def load_orders_df(path: str = DEFAULT_ORDERS_CSV):
    df = pd.read_csv(path)
    _ensure_cols(df, ["invoice_number","user_name","category","product_model","purchase_date","company"])
    return df

def load_spares_df(path: str = DEFAULT_SPARES_CSV):
    df = pd.read_csv(path)
    _ensure_cols(df, ["part_name","part_number","price_usd","product_url","compatible_models","category","company"])
    df["compatible_models"] = df["compatible_models"].fillna("").astype(str)
    return df

def init_all():
    if deps.items_df is None:
        deps.items_df = load_items_df()
    if deps.orders_df is None:
        deps.orders_df = load_orders_df()
    if deps.spares_df is None:
        deps.spares_df = load_spares_df()
    return deps
