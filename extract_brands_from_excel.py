import pandas as pd
from pathlib import Path

# ===== CONFIG =====
EXCEL_FILE = "brands.xlsx"
OUTPUT_FILE = "brands.txt"

# ===== READ EXCEL =====
df = pd.read_excel(EXCEL_FILE, header=None)

brands = []

# Column B = index 1
for value in df.iloc[:, 1]:
    if isinstance(value, str):
        brand = value.strip()
        if brand:
            brands.append(brand)
    elif isinstance(value, (int, float)):
        brands.append(str(value).strip())

# ===== CLEAN & SORT =====
# remove duplicates
brands = list(set(brands))

# sort by length DESC, then alphabetically (stable & predictable)
brands.sort(key=lambda x: (-len(x), x.upper()))

# ===== WRITE TXT =====
output_path = Path(OUTPUT_FILE)

with output_path.open("w", encoding="utf-8") as f:
    for brand in brands:
        f.write(brand + "\n")

print(f"✅ Exported {len(brands)} brands to {OUTPUT_FILE}")
print("🔽 Sorted from longest name to shortest")
