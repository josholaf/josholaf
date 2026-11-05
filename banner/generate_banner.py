from PIL import Image, ImageDraw, ImageFont
import urllib.request, os

# Pixel font (Press Start 2P, from Google Fonts)
FONT = "PressStart2P-Regular.ttf"
if not os.path.exists(FONT):
    urllib.request.urlretrieve(
        "https://github.com/google/fonts/raw/main/ofl/pressstart2p/PressStart2P-Regular.ttf",
        FONT,
    )

SIZE = 48      # font size
PIXEL = 6      # larger = chunkier pixels
PAD = 24
LINE_H = 108   # vertical spacing between lines

LINES = ["> HELLO", "AM JOSHUA", "LET'S BUILD"]

def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))

def make_gradient(w, h):
    BLUE, PURPLE, PINK = (90, 140, 230), (150, 100, 210), (220, 100, 140)
    grad = Image.new("RGB", (w, h))
    gd = ImageDraw.Draw(grad)
    for x in range(w):
        t = x / (w - 1)
        c = lerp(BLUE, PURPLE, t / 0.5) if t < 0.5 else lerp(PURPLE, PINK, (t - 0.5) / 0.5)
        gd.line([(x, 0), (x, h)], fill=c)
    return grad

def pixelate_banner(text):
    font = ImageFont.truetype(FONT, SIZE)
    bbox = font.getbbox(text)
    w = bbox[2] - bbox[0] + PAD * 2
    h = bbox[3] - bbox[1] + PAD * 2
    grad = make_gradient(w, h)
    mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mask).text((PAD - bbox[0], PAD - bbox[1]), text, font=font, fill=255)
    small = mask.resize((w // PIXEL, h // PIXEL), Image.NEAREST).resize((w, h), Image.NEAREST)
    bg = Image.new("RGB", (w, h), (30, 32, 45))
    return Image.composite(grad, bg, small)

# --- Static name banner (joshua-banner.png) ---
pixelate_banner("> JOSHUA").save("joshua-banner.png")
print("Saved joshua-banner.png")

# --- Animated three-line banner (joshua-hello.gif) ---
font = ImageFont.truetype(FONT, SIZE)

# Canvas sized for the widest line plus a trailing cursor, and all three lines.
widest = max(font.getbbox(line + "_")[2] for line in LINES)
w = widest + PAD * 2
h = PAD * 2 + SIZE * 2 + LINE_H * (len(LINES) - 1)
grad = make_gradient(w, h)

def render(lines, cursor_line, cursor_char):
    mask = Image.new("L", (w, h), 0)
    draw = ImageDraw.Draw(mask)
    for i, line in enumerate(lines):
        text = line
        if i == cursor_line:
            text = line + cursor_char
        y = PAD + i * LINE_H
        if text:
            draw.text((PAD, y), text, font=font, fill=255)
    small = mask.resize((w // PIXEL, h // PIXEL), Image.NEAREST).resize((w, h), Image.NEAREST)
    bg = Image.new("RGB", (w, h), (30, 32, 45))
    return Image.composite(grad, bg, small)

frames = []
durations = []

# Type each line in sequence; cursor sits at the end of the line being typed.
for li, line in enumerate(LINES):
    for i in range(1, len(line) + 1):
        state = [LINES[j] for j in range(li)] + [line[:i]] + ["" for _ in range(li + 1, len(LINES))]
        frames.append(render(state, li, "_"))
        durations.append(140)

# All lines complete, cursor blinks on the last line.
for blink in range(6):
    cursor = "_" if blink % 2 == 0 else " "
    frames.append(render(LINES, len(LINES) - 1, cursor))
    durations.append(420)

frames[0].save(
    "joshua-hello.gif",
    save_all=True,
    append_images=frames[1:],
    duration=durations,
    loop=0,
    disposal=2,
)
print("Saved joshua-hello.gif")
