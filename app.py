from flask import Flask, request, Response
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
from zoneinfo import ZoneInfo
import io

app = Flask(__name__)

@app.get("/")
def home():
    return "ok"

@app.get("/cd.png")
def cd_png():
    end = request.args.get("end")  # ex: 2026-02-15T23:59:59
    tz = request.args.get("tz", "Europe/Paris")

    if not end:
        return Response("missing end", status=400)

    end_dt = datetime.fromisoformat(end).replace(tzinfo=ZoneInfo(tz))
    now = datetime.now(ZoneInfo(tz))

    total = int((end_dt - now).total_seconds())
    if total < 0:
        total = 0

    d = total // 86400
    h = (total % 86400) // 3600
    m = (total % 3600) // 60
    s = total % 60

    text = f"{d:02d}  {h:02d}  {m:02d}  {s:02d}"

    W, H = 600, 140
    img = Image.new("RGB", (W, H), (15, 15, 15))
    draw = ImageDraw.Draw(img)
    font = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text(((W - tw) // 2, (H - th) // 2), text, font=font, fill=(255, 255, 255))

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    png = buf.getvalue()

    return Response(
        png,
        headers={
            "Content-Type": "image/png",
            "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
            "Pragma": "no-cache",
            "Expires": "0",
        },
    )
