#!python

import numpy as np
from PIL import Image


def generate_random_overlay(size, threshold=0.7):
    """return a random image of size with patches of grayscale """
    assert size[0] % 16 == 0 and size[1] % 16 == 0
    qsize = (size[0] // 16, size[1] // 16)  # patch size = 1/16 of size
    thresholding = np.vectorize(lambda x: 255 * x if x > threshold else 0)
    Z = thresholding(np.random.random(qsize)).astype(np.uint8)
    im = Image.fromarray(Z, mode="L").resize(size, resample=Image.NEAREST)
    return im


# note source image MUST be "RGBA"
image: Image = Image.open("./base.jpg").convert("RGBA")
size = (image.size[0], image.size[1])

overlay_mask = generate_random_overlay(size)
# overlay_mask.save("./mask.png")
# solidfill = Image.new(mode="RGBA", size=size, color=(255, 0, 0))

# with copy
overlayed = Image.composite((255, 0, 0), image, mask=overlay_mask)
overlayed.save("./overlayed.png")

# in-place
image.paste((255, 0, 0), mask=overlay_mask)
image.save("./out.png")

