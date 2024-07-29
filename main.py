import json
import pandas as pd
from createImage import createInvitationCard
from send_to_messenger import send_to_messenger

if __name__ == "__main__":
    with open('variables.json') as varFiles:
        variables = json.load(varFiles)
    
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
            df = pd.read_csv(userCsvFile)
            print(f"Processing {userCsvFile}")
            for userID in df[csvIndex]:
                for file in contentFiles:
                    with open(file, 'r') as file:
                        message_text = file.read()
                    m1.send_message_to_user(userID, message_text)   
        except FileNotFoundError as e:
            print(f"File {userCsvFile} not found. Please verify its location")             
        except KeyError as e:
            print(f"Keyerror, {e} column mentioned at line {e.__traceback__.tb_lineno} doesnot exist in csv file")
        except Exception as e:
            print(f"Exception occured, ", e) 

    del m1
