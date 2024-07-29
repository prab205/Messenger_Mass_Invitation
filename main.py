import os
import json
import pandas as pd
from createImage import createInvitationCard
from send_to_messenger import send_to_messenger

def send_without_image_creation(m1, userCsvFile, csvIndex, contentFiles):
    df = pd.read_csv(userCsvFile)
    print(f"Processing {userCsvFile}")
    for userID in df[csvIndex]:
        for file in contentFiles:
            with open(file, 'r') as file:
                message_text = file.read()
            m1.send_message_to_user(userID, message_text) 

def send_with_image_creation(m1, userCsvFile, csvIndex, contentFiles, image_dictionary):
    _, _, _, invitationSource, generatedImageName, viewGeneratedImage, overwriteIfExists, xCoordinate, yCoordinate, rgb_color, font, fontSize, csvUserNameIndex, prefixToAdd = image_dictionary.values()

    df = pd.read_csv(userCsvFile)
    for index, row in df.iterrows():
        try:
            createInvitationCard(srcImg=invitationSource, text=prefixToAdd + row[csvUserNameIndex], destImg=generatedImageName, overwrite=overwriteIfExists, cordinates=(xCoordinate, yCoordinate), color=tuple(rgb_color), fontPath=font, fontSize=fontSize, display=viewGeneratedImage)
            for file in contentFiles:
                with open(file, 'r') as file:
                    message_text = file.read()
                m1.send_message_to_user(row[csvIndex], message_text)
            os.remove(generatedImageName)
        except KeyError as e:
            print(f"Keyerror, {e} column mentioned at line {e.__traceback__.tb_lineno} doesnot exist in csv file")
            exit(-1)
        except Exception as e:
            print(f"Exception occured on line {index+2}, ", e)


if __name__ == "__main__":
    with open('variables.json') as varFiles:
        variables = json.load(varFiles)

    if variables['image']['createOnlyImage']:
        _, _, textForCreateOnlyImage, invitationSource, generatedImageName, viewGeneratedImage, overwriteIfExists, xCoordinate, yCoordinate, rgb_color, font, fontSize, _, _ = variables['image'].values()
        createInvitationCard(srcImg=invitationSource, text=textForCreateOnlyImage, destImg=generatedImageName, overwrite=overwriteIfExists, cordinates=(xCoordinate, yCoordinate), color=tuple(rgb_color), fontPath=font, fontSize=fontSize, display=True)
        exit(-1)
    
    headless, email, credentialFile, contentFiles, userIDList, userCsvFile, csvIndex = variables['messenger'].values()

    m1 = send_to_messenger(headless=headless)

    with open(credentialFile, 'r') as file:
        password = file.readline()
    print(m1.login_to_facebook(email, password))

    for userID in userIDList:
        for file in contentFiles:
            with open(file, 'r') as file:
                message_text = file.read()
            m1.send_message_to_user(userID, message_text)

    if userCsvFile:
        try:
            if variables['image']['imageCreation']:
                send_with_image_creation(m1, userCsvFile, csvIndex, contentFiles, variables['image'])
            else:
                send_without_image_creation(m1, userCsvFile, csvIndex, contentFiles)
        except FileNotFoundError as e:
            print(f"File {userCsvFile} not found. Please verify its location")             
        except KeyError as e:
            print(f"Keyerror, {e} column mentioned at line {e.__traceback__.tb_lineno} doesnot exist in csv file")
        except Exception as e:
            print(f"Exception occured, ", e) 

    del m1
