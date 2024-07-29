## Mass Messenger Sender  
Python program for sending mass messages to users in messenger through selenium.  
 
- Write the content you want to send at message.txt file  
- Add image as an attachment through <img>image_relative_path_wrt_main.py</img>  
  
**The script cannot detect wrong credentials.**

---
**send_to_messenger.py**
- <b>send_message_to_user</b>(user_id, message_text, images_list=None)  
&emsp;&emsp;Load user message section, fill the message and images and send to the user.  
&emsp;&emsp;user_id is the unique identifier associated with a user. It can be discovered by visiting the facebook page of that user and extracting from the URI  
  
`https://www.facebook.com/profile.php?id=10000000000000`  
`https://www.facebook.com/10000000000`  
  
&emsp;&emsp;Sends messages to users by reading csv_file.  
  
  
&emsp;&emsp;To send multiple messages one after another, add the entry in `contentFiles`  
&emsp;&emsp;To send message directly through user_id, add the userId in `userIDList`  
&emsp;&emsp;To send message to list of users from csv, add the file in `userCsvFile` and write the userId header in `csvHeader`  
  
  
**createImage.py**
Embeds text in an image.  
- <b>createInvitationCard</b>(srcImg, text, destImg, overwrite=False, cordinates=(None, None), color=(0,0,0), fontPath=None, fontSize=50, display=False)  
&emsp;&emsp;Executed only when `imageCreation:true`  
&emsp;&emsp;`createOnlyImage` to test the invitation image without sending any messages.  
&emsp;&emsp;`textForCreateOnlyImage` places the specified text in the image when "createOnlyImage" variable is true.  
&emsp;&emsp;`fontSize` is valid only when you explicitly define font.    
&emsp;&emsp;`csvUserNameHeader` is the csv header name containing the string to embed in the image.  
&emsp;&emsp;`prefixToAdd` is any specific prefix that may need to be added with the csv string.  
  
---

**To get the program running**
1. Clone the repo  
`git clone https://github.com/prab205/Messenger_Mass_Invitation.git`
2. Enter the project directory  
`cd Messenger_Mass_Invitation`
3. Create python virtual environment and activate it  
`python3 -m venv .venv`  
&emsp; Linux/MacOS  
`source .venv/bin/activate`  
&emsp; Windows  
`.venv\Scripts\activate [Windows]`  
4. Install dependencies  
`pip install -r requirements.txt`  
5. Configure the variables at variables.json
6. Run the program  
`python3 main.py`  
