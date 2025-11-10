from __future__ import annotations
import re
from typing import List, Dict, Any, Optional
from .dependency_engine import init_all

_WORD = re.compile(r"[a-z0-9]+", re.I)

def _norm(s: str|None) -> str:
    return (s or "").strip().lower()

def _tokens(s: str) -> set[str]:
    return set(_WORD.findall(_norm(s)))

class IntentSearchEngine:
    def __init__(self):
        self.deps = init_all()
        self.df = self.deps.items_df.copy()
        self.df["title_l"] = self.df["title"].astype(str).str.lower()
        self.df["brand_l"] = self.df["brand"].astype(str).str.lower()
        self.df["category_l"] = self.df["category"].astype(str).str.lower()
        self.df["desc_l"] = self.df["description"].astype(str).str.lower()
        self.cats = {
            "laptop": {"laptop","notebook","macbook"},
            "headphones": {"headphone","headphones","earphone","audio"},
            "smartphone": {"phone","smartphone","iphone","android"},
            "microwave": {"microwave","oven"},
            "ac": {"ac","air","conditioner","airconditioner"},
        }

    def _parse_budget(self, q: str):
        ql = q.lower().replace(",", "")
        m = re.search(r"(under|below|<=|less than)\s*₹?\s*(\d+)", ql)
        if m: return (None, float(m.group(2)))
        m = re.search(r"between\s*₹?\s*(\d+)\s*(and|-|to)\s*₹?\s*(\d+)", ql)
        if m:
            a,b = sorted([float(m.group(1)), float(m.group(3))]); return (a,b)
        m = re.search(r"(around|about|~)\s*₹?\s*(\d+)", ql)
        if m:
            x = float(m.group(2)); return (0.8*x, 1.2*x)
        return (None, None)

    def _parse_brand(self, q: str) -> Optional[str]:
        brands = set(self.df["brand_l"].dropna().unique().tolist())
        for tok in _tokens(q):
            if tok in brands: return tok
        return None

    def _parse_category(self, q: str) -> Optional[str]:
        toks = _tokens(q)
        best = None
        for cat, keys in self.cats.items():
            if toks & keys: best = cat
        return best

    def search(self, query: str, max_results: int = 10) -> List[Dict[str,Any]]:
        q = query or ""
        lo, hi = self._parse_budget(q)
        brand = self._parse_brand(q)
        category = self._parse_category(q)
        df = self.df.copy()
        if brand: df = df[df["brand_l"] == brand]
        if category: df = df[df["category_l"] == category]
        if lo is not None: df = df[df["price"] >= lo]
        if hi is not None: df = df[df["price"] <= hi]
        qtokens = _tokens(q)

        def score_row(r):
            text = f"{r['title_l']} {r['desc_l']} {r['brand_l']} {r['category_l']}"
            toks = _tokens(text)
            overlap = len(qtokens & toks)
            s = overlap
            if brand and r["brand_l"] == brand: s += 2.5
            if category and r["category_l"] == category: s += 2.0
            if hi is not None:
                target = hi if lo is None else (lo+hi)/2
                s += max(0, 1.5 * (1 - abs((r['price'] - target) / max(target,1))))
            return float(s)

        df["__score"] = df.apply(score_row, axis=1)
        df = df.sort_values(["__score","rating"], ascending=[False, False]).head(max_results)
        out = []
        for _, r in df.iterrows():
            out.append({
                "id": r["id"], "title": r["title"], "brand": r["brand"], "category": r["category"],
                "price": float(r["price"]), "rating": float(r["rating"]),
                "url": r.get("url"), "image_url": r.get("image_url"), "description": r.get("description"),
                "score": float(r["__score"]),
            })
        return out
