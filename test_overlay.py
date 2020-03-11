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


def load_npy(file, index):
    npy = np.load(file).copy()
    npy[np.nonzero(npy)] = 255  # map all category to 255
    im = Image.fromarray(npy[index], mode="L")
    return im


# note source image MUST be "RGBA"
image: Image = Image.open("./base.png").convert("RGBA")
size = (image.size[0], image.size[1])

# overlay_mask: Image = generate_random_overlay(size)
overlay_mask: Image = load_npy("./dicompyler/resources/TCGA-17-Z019.npy", index=15)
overlay_mask.save("./mask.png")

# with copy
overlayed: Image = Image.composite((255, 0, 0), image, mask=overlay_mask)
overlayed.save("./out.composite.png")

# in-place
image.paste((255, 0, 0), mask=overlay_mask)
image.save("./out.inplace.png")
