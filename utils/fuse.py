import os, math, glob
from pathlib import Path
from PIL import Image

export_name = input("Introduce el nombre con el que se exportarán las imágenes: ")
while True:
    try:
        icons = input("Make icons? [y/n]")
        if icons in ["y", "n"] or icons in ["Y", "N"]:
            break
        else:
            print("Invalid option")
    except:
        print("Invalid option")

i = 0
for file in glob.iglob("**/*.bmp", recursive=True):
    if os.path.exists(file) and (file[-8:] == "_sup.bmp" or file[-8:] == "_inf.bmp"):
        filepath = Path(file)
        name = filepath.stem
        name = name[:-4]
        
        filepath_sup = Path(os.path.join(filepath.parent, f"{name}_sup.bmp"))
        filepath_inf = Path(os.path.join(filepath.parent, f"{name}_inf.bmp"))

        img_sup = Image.open(filepath_sup)
        img_inf = Image.open(filepath_inf)

        imgs_w, imgs_h = img_sup.size
        if icons in ["y", "Y"]:
            img_sup_crop = img_sup.crop((math.floor(((imgs_w)/2)-(imgs_h/2)), 0, math.floor(((imgs_w)/2)+(imgs_h/2)), imgs_h))

            icon = img_sup_crop.resize((48, 48), Image.Resampling.LANCZOS)
            icon.save(os.path.join(filepath.parent, f"{export_name}{i}_icon.png"))

        imgi_w, imgi_h = img_inf.size

        fused_img = Image.new('RGBA', (imgs_w, (imgs_h+imgi_h)))
        fused_img_w, fused_img_h = fused_img.size
        fused_img.paste(img_sup, (0, 0))
        fused_img.paste(img_inf, (math.floor((fused_img_w/2)-(imgi_w/2)), math.floor(fused_img_h/2)))

        fused_img.save(os.path.join(filepath.parent, f"{export_name}{i}_fused.png"))

        os.remove(os.path.join(filepath.parent, f"{name}_sup.bmp"))
        os.remove(os.path.join(filepath.parent, f"{name}_inf.bmp"))
        i += 1