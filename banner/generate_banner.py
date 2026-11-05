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
WORD = "HELLO"

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

def render(text, canvas_text, grad):
    font = ImageFont.truetype(FONT, SIZE)
    bbox = font.getbbox(canvas_text)
    w = bbox[2] - bbox[0] + PAD * 2
    h = bbox[3] - bbox[1] + PAD * 2

    mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mask).text((PAD - bbox[0], PAD - bbox[1]), text, font=font, fill=255)

    small = mask.resize((w // PIXEL, h // PIXEL), Image.NEAREST).resize((w, h), Image.NEAREST)

    bg = Image.new("RGB", (w, h), (30, 32, 45))
    return Image.composite(grad, bg, small)

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

# --- Animated hello banner (joshua-hello.gif) ---
canvas_text = "> " + WORD + "_"   # widest frame, keeps all frames aligned
probe = ImageFont.truetype(FONT, SIZE)
cb = probe.getbbox(canvas_text)
cw, ch = cb[2] - cb[0] + PAD * 2, cb[3] - cb[1] + PAD * 2
grad = make_gradient(cw, ch)

frames = []
durations = []

# typing, one letter at a time, cursor always on
for i in range(1, len(WORD) + 1):
    frames.append(render("> " + WORD[:i] + "_", canvas_text, grad))
    durations.append(140)

# finished word, cursor blinks
for blink in range(6):
    text = "> " + WORD + ("_" if blink % 2 == 0 else " ")
    frames.append(render(text, canvas_text, grad))
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
