from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# ===== Load brands from TXT =====
with open("brands.txt", "r", encoding="utf-8") as f:
    BRANDS = {line.strip().upper() for line in f if line.strip()}


# ===== DEFAULT (case 1 & 2) =====
def extract_default(raw_text: str):
    lines = [l.strip() for l in raw_text.splitlines() if l.strip()]
    pairs = []
    current_brand = None

    for line in lines:
        upper = line.upper()

        # CASE 1: brand + id in one line
        for brand in BRANDS:
            if upper.startswith(brand + " "):
                part = line[len(brand):].strip()
                pairs.append((part, brand))
                current_brand = None
                break
        else:
            # CASE 2: brand alone
            if upper in BRANDS:
                current_brand = line
            # CASE 3: id after brand
            elif current_brand:
                pairs.append((line, current_brand))

    return pairs


# ===== TRODO (case 3) =====
def extract_trodo(raw_text: str):
    lines = [l.strip() for l in raw_text.splitlines() if l.strip()]
    pairs = []
    current_brand = None

    for line in lines:
        if line.upper() in BRANDS:
            current_brand = line
        elif current_brand:
            pairs.append((line, current_brand))

    return pairs


# ===== AVTOZAKUP (case 4) =====
def extract_avtozakup(raw_text: str):
    lines = [l.strip() for l in raw_text.splitlines() if l.strip()]
    pairs = []

    i = 0
    while i < len(lines):
        line = lines[i]
        upper = line.upper()

        # нашли бренд
        if upper in BRANDS:
            brand = line
            j = i + 1

            # ищем ID ниже, пропуская мусор
            while j < len(lines):
                candidate = lines[j]
                cand_upper = candidate.upper()

                # если снова бренд — значит ID у текущего бренда нет
                if cand_upper in BRANDS:
                    break

                # пропускаем мусор
                if (
                    "ШТ" in cand_upper
                    or "ДН" in cand_upper
                    or "ТГ" in cand_upper
                    or cand_upper in {
                        "ДЕТАЛЬ", "СРОК", "ДОСТУПНО", "ЦЕНА",
                        "ПРОКЛАДКА", "ФИЛЬТР", "ЕЩЕ ПРЕДЛОЖЕНИЯ",
                    }
                ):
                    j += 1
                    continue

                # ID должен содержать хотя бы одну цифру
                if any(ch.isdigit() for ch in candidate):
                    pairs.append((candidate, brand))
                    break

                j += 1

            i = j
        else:
            i += 1

    return pairs


# ================== ROUTES ==================

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("index.html", {
        "request": request,
        "pairs": [],
        "raw_text": "",
        "count": 0,
        "page": "default"
    })


@app.get("/default", response_class=HTMLResponse)
async def default_page(request: Request):
    return templates.TemplateResponse("index.html", {
        "request": request,
        "pairs": [],
        "raw_text": "",
        "count": 0,
        "page": "default"
    })


@app.post("/default", response_class=HTMLResponse)
async def default_parse(
    request: Request,
    raw_text: str = Form(...),
    analog: str = Form(...),
    col4: str = Form(...)
):
    pairs = extract_default(raw_text)

    output_lines = [
        f"{part}\t{brand}\t{analog}\t{col4}"
        for part, brand in pairs
    ]

    output_text = "\n".join(output_lines)

    return templates.TemplateResponse("index.html", {
        "request": request,
        "output_text": output_text,
        "pairs_count": len(pairs),
        "analog": analog,
        "col4": col4,
        "page": "default"
    })


@app.get("/trodo", response_class=HTMLResponse)
async def trodo_page(request: Request):
    return templates.TemplateResponse("index.html", {
        "request": request,
        "pairs": [],
        "raw_text": "",
        "count": 0,
        "page": "trodo"
    })


@app.post("/trodo", response_class=HTMLResponse)
async def trodo_parse(
    request: Request,
    raw_text: str = Form(...),
    analog: str = Form(...),
    col4: str = Form(...)
):
    pairs = extract_trodo(raw_text)

    output_text = "\n".join(
        f"{p}\t{b}\t{analog}\t{col4}" for p, b in pairs
    )

    return templates.TemplateResponse("index.html", {
        "request": request,
        "output_text": output_text,
        "pairs_count": len(pairs),
        "analog": analog,
        "col4": col4,
        "page": "trodo"
    })


@app.get("/avtozakup", response_class=HTMLResponse)
async def avtozakup_page(request: Request):
    return templates.TemplateResponse("index.html", {
        "request": request,
        "pairs": [],
        "raw_text": "",
        "count": 0,
        "page": "avtozakup"
    })


@app.post("/avtozakup", response_class=HTMLResponse)
async def avtozakup_parse(
    request: Request,
    raw_text: str = Form(...),
    analog: str = Form(...),
    col4: str = Form(...)
):
    pairs = extract_avtozakup(raw_text)

    output_text = "\n".join(
        f"{p}\t{b}\t{analog}\t{col4}" for p, b in pairs
    )

    return templates.TemplateResponse("index.html", {
        "request": request,
        "output_text": output_text,
        "pairs_count": len(pairs),
        "analog": analog,
        "col4": col4,
        "page": "avtozakup"
    })
