from PIL import Image, ImageDraw, ImageFont
import urllib.request, os

# Pixel font (Press Start 2P, from Google Fonts)
FONT = "PressStart2P-Regular.ttf"
if not os.path.exists(FONT):
    urllib.request.urlretrieve(
        "https://github.com/google/fonts/raw/main/ofl/pressstart2p/PressStart2P-Regular.ttf",
        FONT,
    )

TEXT = "> JOSHUA"
SIZE = 48      # font size
PIXEL = 6      # larger = chunkier pixels
PAD = 24

font = ImageFont.truetype(FONT, SIZE)
bbox = font.getbbox(TEXT)
w = bbox[2] - bbox[0] + PAD * 2
h = bbox[3] - bbox[1] + PAD * 2

# 1. Draw the text as a black-and-white mask
mask = Image.new("L", (w, h), 0)
ImageDraw.Draw(mask).text((PAD - bbox[0], PAD - bbox[1]), TEXT, font=font, fill=255)

# 2. Pixelate the mask
small = mask.resize((w // PIXEL, h // PIXEL), Image.NEAREST).resize((w, h), Image.NEAREST)

# 3. Build a horizontal gradient: blue -> purple -> pink
def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))

BLUE, PURPLE, PINK = (90, 140, 230), (150, 100, 210), (220, 100, 140)
grad = Image.new("RGB", (w, h))
gd = ImageDraw.Draw(grad)
for x in range(w):
    t = x / (w - 1)
    c = lerp(BLUE, PURPLE, t / 0.5) if t < 0.5 else lerp(PURPLE, PINK, (t - 0.5) / 0.5)
    gd.line([(x, 0), (x, h)], fill=c)

# 4. Composite the gradient onto a dark background through the mask
BG = Image.new("RGB", (w, h), (30, 32, 45))
Image.composite(grad, BG, small).save("joshua-banner.png")
print("Saved joshua-banner.png")
