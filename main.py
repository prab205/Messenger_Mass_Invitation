import os
import csv
import json
import random
import time
from createImage import createInvitationCard
from send_to_messenger import send_to_messenger

# Randomized delay between messages so requests don't fire at a fixed
# machine-like cadence, which is one of the patterns Facebook's bot
# detection flags and reacts to with checkpoints/restore prompts.
# Bounds come from variables.json (messenger.minDelaySeconds/maxDelaySeconds).
def human_delay(min_delay_seconds, max_delay_seconds):
    time.sleep(random.uniform(min_delay_seconds, max_delay_seconds))

def load_message_texts(contentFiles):
    texts = []
    for path in contentFiles:
        with open(path, 'r') as f:
            texts.append(f.read())
    return texts

def read_csv_rows(userCsvFile):
    with open(userCsvFile, newline='') as f:
        return list(csv.DictReader(f))

def send_without_image_creation(userCsvFile, csvHeader, messageTexts, min_delay_seconds, max_delay_seconds):
    rows = read_csv_rows(userCsvFile)
    print(f"Processing {userCsvFile}")
    for row in rows:
        userID = row.get(csvHeader)
        if userID:
            for message_text in messageTexts:
                m1.send_message_to_user(userID, message_text)
                human_delay(min_delay_seconds, max_delay_seconds)

def send_with_image_creation(userCsvFile, csvHeader, messageTexts, image_dictionary, min_delay_seconds, max_delay_seconds):
    _, _, _, invitationSource, generatedImageName, viewGeneratedImage, overwriteIfExists, xCoordinate, yCoordinate, rgb_color, font, fontSize, csvUserNameHeader, prefixToAdd = image_dictionary.values()

    rows = read_csv_rows(userCsvFile)
    for index, row in enumerate(rows):
        try:
            userID = row.get(csvHeader)
            if userID:
                createInvitationCard(srcImg=invitationSource, text=prefixToAdd + row[csvUserNameHeader], destImg=generatedImageName, overwrite=overwriteIfExists, cordinates=(xCoordinate, yCoordinate), color=tuple(rgb_color), fontPath=font, fontSize=fontSize, display=viewGeneratedImage)
                for message_text in messageTexts:
                    m1.send_message_to_user(userID, message_text)
                    human_delay(min_delay_seconds, max_delay_seconds)
                if os.path.exists(generatedImageName):
                    os.remove(generatedImageName)
        except KeyError as e:
            print(f"Keyerror, {e} column mentioned at row {index+2} doesnot exist in csv file")
            exit(-1)
        except Exception as e:
            print(f"Exception occured on row {index+2}, ", e)


if __name__ == "__main__":
    with open('variables.json') as varFiles:
        variables = json.load(varFiles)

    if variables['image']['createOnlyImage'] and variables['image']['imageCreation']:
        _, _, textForCreateOnlyImage, invitationSource, generatedImageName, viewGeneratedImage, overwriteIfExists, xCoordinate, yCoordinate, rgb_color, font, fontSize, _, _ = variables['image'].values()
        createInvitationCard(srcImg=invitationSource, text=textForCreateOnlyImage, destImg=generatedImageName, overwrite=overwriteIfExists, cordinates=(xCoordinate, yCoordinate), color=tuple(rgb_color), fontPath=font, fontSize=fontSize, display=True)
        exit(-1)

    headless, profileDir, email, credentialFile, contentFiles, userIDList, userCsvFile, csvHeader, minDelaySeconds, maxDelaySeconds = variables['messenger'].values()

    m1 = send_to_messenger(headless=headless, profile_dir=profileDir)

    with open(credentialFile, 'r') as file:
        password = file.readline().strip()
    print(m1.login_to_facebook(email, password))

    messageTexts = load_message_texts(contentFiles)

    for userID in userIDList:
        for message_text in messageTexts:
            m1.send_message_to_user(userID, message_text)
            human_delay(minDelaySeconds, maxDelaySeconds)

    if userCsvFile:
        try:
            if variables['image']['imageCreation']:
                send_with_image_creation(userCsvFile, csvHeader, messageTexts, variables['image'], minDelaySeconds, maxDelaySeconds)
            else:
                send_without_image_creation(userCsvFile, csvHeader, messageTexts, minDelaySeconds, maxDelaySeconds)
        except FileNotFoundError as e:
            print(f"File {userCsvFile} not found. Please verify its location")
        except KeyError as e:
            print(f"Keyerror, {e} column mentioned doesnot exist in csv file")
        except Exception as e:
            print(f"Exception occured, ", e)

    del m1
