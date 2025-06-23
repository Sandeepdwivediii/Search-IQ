import re
import time
import requests
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 1) Load your CSV of basic parts (with product_url)
df = pd.read_csv("samsung_ac_parts_basic.csv")

# 2) Prepare Selenium (non-headless so JS always runs)
options = Options()
# comment out headless so you can actually see the clicks if needed:
# options.add_argument("--headless")  
options.add_argument("--window-size=1920,1080")
driver = webdriver.Chrome(options=options)

def get_supported_models_via_selenium(url: str) -> str:
    driver.get(url)
    wait = WebDriverWait(driver, 10)
    # 2a) Wait for the tab nav to load, then click "Supported Models"
    tab = wait.until(EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, "Supported Models")))
    tab.click()
    # 2b) Wait for the panel content to appear
    panel = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".tabs-content")))
    html = panel.get_attribute("innerHTML")
    # 2c) Extract codes
    codes = re.findall(r"\b[A-Z0-9/\-]{5,}\b", html)
    # dedupe
    seen = set(); uniq = []
    for c in codes:
        if c not in seen:
            seen.add(c)
            uniq.append(c)
    return "; ".join(uniq)

# 3) Iterate and collect
compatible_lists = []
for url in df["product_url"]:
    try:
        cms = get_supported_models_via_selenium(url)
    except Exception as e:
        print(f"❌ Error on {url}: {e}")
        cms = ""
    compatible_lists.append(cms)

driver.quit()

# 4) Attach and save
df["compatible_models"] = compatible_lists
final = df[[
    "part_name",
    "part_number",
    "price_usd",
    "product_url",
    "compatible_models"
]]
final.to_csv("samsung_ac_parts_final.csv", index=False)
print(f"✅ Done: {len(final)} rows → samsung_ac_parts_final.csv")
