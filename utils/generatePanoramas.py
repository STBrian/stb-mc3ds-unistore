import py3dst

from PIL import Image
from pathlib import Path

path = Path("./ui")

for element in path.glob("*.png"):
    image = Image.open(element)
    image = image.resize((128, 128), Image.Resampling.LANCZOS)
    texture = py3dst.Texture3dst().fromImage(image)
    texture.export(f"{element.parent.joinpath(element.stem)}.3dst")