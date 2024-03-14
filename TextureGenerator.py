import numpy as np

from panda3d.core import PNMImage
from perlin_numpy import generate_perlin_noise_2d


height_map = PNMImage(1024, 1024)
height_map.make_grayscale()
noise: np.ndarray = generate_perlin_noise_2d((1024, 1024), (16, 16))

for y in range(0, 1024):
    for x in range(0, 1024):
        val = (noise[x, y] + 1.0) * 0.5
        height_map.set_gray(x, y, val)

height_map.write("HeightMap.png")
