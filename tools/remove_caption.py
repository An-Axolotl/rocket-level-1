"""Remove the Snapchat "Let's go" caption bar from the rocket photo.

The caption bar is a translucent black strip (~61% opacity) with white text.
1) Undo the darkening inside the strip (divide by the measured transmittance).
2) Inpaint the white text and the strip's soft edge rows.
    python tools/remove_caption.py SRC.jpg images/rocket.jpg
"""
import sys
import cv2
import numpy as np

src, dst = sys.argv[1], sys.argv[2]
img = cv2.imread(src).astype(np.float32)
Y0, Y1 = 926, 1017                       # strip interior rows (inclusive)
EDGE = [925, 1018]                        # partially darkened boundary rows

# transmittance per channel, measured from plain wall just above vs inside the strip
t = img[Y0 + 3:Y0 + 9, 600:900].mean((0, 1)) / img[Y0 - 9:Y0 - 3, 600:900].mean((0, 1))
out = img.copy()
out[Y0:Y1 + 1] = np.clip(img[Y0:Y1 + 1] / t, 0, 255)

# The text ("Let's go", y 957-994, x 404-546) partly covers the rocket body.
TY0, TY1, TX0, TX1 = 950, 1001, 398, 556
ROCKET_X1 = 456                            # rocket body is left of this column here
# over the rocket (vertical cylinder): interpolate each column top-to-bottom
for x in range(TX0, ROCKET_X1):
    top, bot = out[TY0 - 1, x], out[TY1 + 1, x]
    w = np.linspace(0, 1, TY1 - TY0 + 1)[:, None]
    out[TY0:TY1 + 1, x] = top * (1 - w) + bot * w
# over the shelf (horizontal bands): copy each row's colour from just right of the text
out[TY0:TY1 + 1, ROCKET_X1:TX1] = np.median(out[TY0:TY1 + 1, TX1 + 4:TX1 + 60], axis=1)[:, None]

# colour-match the rocket body inside the strip to the body just above/below it
RX0 = 388
ref = np.concatenate([out[Y0 - 25:Y0 - 3, RX0:ROCKET_X1 - 4], out[Y1 + 3:Y1 + 25, RX0:ROCKET_X1 - 4]]).mean((0, 1))
cur = out[Y0:Y1 + 1, RX0:ROCKET_X1 - 4].mean((0, 1))
out[Y0:Y1 + 1, RX0:ROCKET_X1 - 4] = np.clip(out[Y0:Y1 + 1, RX0:ROCKET_X1 - 4] * (ref / cur), 0, 255)

mask = np.zeros(img.shape[:2], np.uint8)
for y in EDGE:
    mask[y - 1:y + 2] = 255
mask[TY0 - 1:TY1 + 2, ROCKET_X1 - 2:ROCKET_X1 + 3] = 255   # soften the seam between the two fills

out = cv2.inpaint(np.clip(out, 0, 255).astype(np.uint8), mask, 5, cv2.INPAINT_TELEA)
cv2.imwrite(dst, out, [cv2.IMWRITE_JPEG_QUALITY, 92])
print(dst, "transmittance", t.round(3))
