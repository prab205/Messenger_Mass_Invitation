import os
from PIL import Image, ImageDraw, ImageFont

def createInvitationCard(srcImg, text, destImg, overwrite=False, cordinates=(None, None), color=(0,0,0), fontPath=None, fontSize=50, display=False):
    try:
        img = Image.open(srcImg)
    except:
        print(f"Image {srcImg} couldnot be loaded successfully.\nPlease check the provided path and name.\nInclude file extension as well")
        return

    if os.path.exists(destImg):
        print(f"{destImg} already exists. Overwriting the existing image.")

    editableImage = ImageDraw.Draw(img)

    if fontPath:
        try:
            #loads the font as well as the fontsize if font is provided by user
            fontVar = ImageFont.truetype(fontPath, fontSize)

            #if any one cordinate is missing, then centers text at that cordinate.
            if cordinates[0] and cordinates[1]:
                editableImage.text((cordinates[0], cordinates[1]), text,  fill=color, font=fontVar)
                img.save(destImg)
            elif cordinates[1]:
                W,_ = img.size
                w,_ = fontVar.getsize(text)
                editableImage.text(((W-w)/2, cordinates[1]), text,  fill=color, font=fontVar)
                img.save(destImg)
            elif cordinates[0]:
                _,H = img.size
                _,h = fontVar.getsize(text)
                editableImage.text((cordinates[0], (H-h)/2), text,  fill=color, font=fontVar)
                img.save(destImg)
            else:
                editableImage.text((0,0), text,  fill=color, font=fontVar)
                img.save(destImg)
        except OSError:
            print(f"Cannot load {fontPath} font properly")
        except TypeError as e:
            print(f"No any text provided")
        except Exception as e:
            print(f"Exception occured during font true case{fontPath}, ", e)

    else:
        try:
            if cordinates[0] and cordinates[1]:
                editableImage.text((cordinates[0], cordinates[1]), text,  fill=color)
                img.save(destImg)
            elif cordinates[1]:
                W,_ = img.size
                w,_ = editableImage.textsize(text)
                editableImage.text(((W-w)/2, cordinates[1]), text,  fill=color)
                img.save(destImg)
            elif cordinates[0]:
                _,H = img.size
                _,h = editableImage.textsize(text)
                editableImage.text((cordinates[0], (H-h)/2), text,  fill=color)
                img.save(destImg)
            else:
                editableImage.text((0,0), text,  fill=color)
                img.save(destImg)
        except TypeError as e:
            print(f"No any text provided", e)
        except Exception as e:
            print(f"Exception occured during font false case{fontPath}, ", e) 

    if display:
        img.show()
