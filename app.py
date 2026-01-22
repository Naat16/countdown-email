from flask import Flask, request, Response
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import io

app = Flask(__name__)


@app.get("/")
def home():
    return "ok"


def _compute_text(end_dt: datetime, now_dt: datetime) -> str:
    total = int((end_dt - now_dt).total_seconds())
    if total < 0:
        total = 0

    d = total // 86400
    h = (total % 86400) // 3600
    m = (total % 3600) // 60
    s = total % 60

    # Format: DD  HH  MM  SS (comme ton exemple)
    return f"{d:02d}  {h:02d}  {m:02d}  {s:02d}"


@app.get("/cd.png")
def cd_png():
    end = request.args.get("end")  # ex: 2026-02-15T23:59:59
    tz = request.args.get("tz", "Europe/Paris")

    if not end:
        return Response("missing end", status=400)

    end_dt = datetime.fromisoformat(end).replace(tzinfo=ZoneInfo(tz))
    now = datetime.now(ZoneInfo(tz))

    text = _compute_text(end_dt, now)

    W, H = 600, 140
    img = Image.new("RGB", (W, H), (15, 15, 15))
    draw = ImageDraw.Draw(img)

    # Police simple; on pourra styliser plus tard
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


@app.get("/cd.gif")
def cd_gif():
    end = request.args.get("end")  # ex: 2026-02-15T23:59:59
    tz = request.args.get("tz", "Europe/Paris")

    if not end:
        return Response("missing end", status=400)

    end_dt = datetime.fromisoformat(end).replace(tzinfo=ZoneInfo(tz))
    now = datetime.now(ZoneInfo(tz))

    W, H = 600, 140
    bg = (15, 15, 15)
    fg = (255, 255, 255)
    font = ImageFont.load_default()

    frames = []
    for i in range(60):  # 60 secondes d’animation
        t = now + timedelta(seconds=i)
        text = _compute_text(end_dt, t)

        img = Image.new("RGB", (W, H), bg)
        draw = ImageDraw.Draw(img)

        bbox = draw.textbbox((0, 0), text, font=font)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        draw.text(((W - tw) // 2, (H - th) // 2), text, font=font, fill=fg)

        frames.append(img)

    buf = io.BytesIO()
    frames[0].save(
        buf,
        format="GIF",
        save_all=True,
        append_images=frames[1:],
        duration=1000,  # 1 seconde par frame
        loop=0,         # boucle infinie
        disposal=2
    )
    gif = buf.getvalue()

    return Response(
        gif,
        headers={
            "Content-Type": "image/gif",
            "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
            "Pragma": "no-cache",
            "Expires": "0",
        },
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
