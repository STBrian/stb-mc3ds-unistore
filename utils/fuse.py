import os, math
from pathlib import Path
from PIL import Image

filename = input("Introduce el nombre base de la screenshot: ")
export_name = input("Introduce el nombre con el que se exportarán las imágenes: ")
filepath_sup = Path(f"{filename}_sup.bmp")
filepath_inf = Path(f"{filename}_inf.bmp")

img_sup = Image.open(filepath_sup)
img_inf = Image.open(filepath_inf)

imgs_w, imgs_h = img_sup.size
img_sup_crop = img_sup.crop((math.floor(((imgs_w)/2)-(imgs_h/2)), 0, math.floor(((imgs_w)/2)+(imgs_h/2)), imgs_h))

icon = img_sup_crop.resize((48, 48), Image.Resampling.LANCZOS)
icon.save(f"{export_name}_icon.png")

imgi_w, imgi_h = img_inf.size

fused_img = Image.new('RGBA', (imgs_w, (imgs_h+imgi_h)))
fused_img_w, fused_img_h = fused_img.size
fused_img.paste(img_sup, (0, 0))
fused_img.paste(img_inf, (math.floor((fused_img_w/2)-(imgi_w/2)), math.floor(fused_img_h/2)))

fused_img.save(f"{export_name}_fused.png")

os.remove(f"{filename}_sup.bmp")
os.remove(f"{filename}_inf.bmp")