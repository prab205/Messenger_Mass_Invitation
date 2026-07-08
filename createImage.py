import os
from PIL import Image, ImageDraw, ImageFont

def createInvitationCard(srcImg, text, destImg, overwrite=False, cordinates=(None, None), color=(0,0,0), fontPath=None, fontSize=50, display=False):
    if os.path.exists(destImg) and not overwrite:
        print(f"{destImg} already exists and overwrite is disabled. Skipping.")
        return

    try:
        img = Image.open(srcImg)
    except (FileNotFoundError, OSError) as e:
        print(f"Image {srcImg} couldnot be loaded successfully.\nPlease check the provided path and name.\nInclude file extension as well")
        return

    if os.path.exists(destImg):
        print(f"{destImg} already exists. Overwriting the existing image.")

    editableImage = ImageDraw.Draw(img)

    if not text:
        print("No any text provided")
        return

    font = ImageFont.truetype(fontPath, fontSize) if fontPath else ImageFont.load_default()

    try:
        left, top, right, bottom = editableImage.textbbox((0, 0), text, font=font)
        w, h = right - left, bottom - top

        if cordinates[0] and cordinates[1]:
            position = (cordinates[0], cordinates[1])
        elif cordinates[1]:
            W, _ = img.size
            position = ((W - w) / 2, cordinates[1])
        elif cordinates[0]:
            _, H = img.size
            position = (cordinates[0], (H - h) / 2)
        else:
            position = (0, 0)

        editableImage.text(position, text, fill=color, font=font)
        img.save(destImg)
    except OSError as e:
        print(f"Cannot load {fontPath} font properly, ", e)
    except Exception as e:
        print(f"Exception occured while drawing text on {srcImg}, ", e)

    if display:
        img.show()
