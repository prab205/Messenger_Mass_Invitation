## Mass Messenger Sender  
Python program for sending mass messages to users in messenger through selenium.  
 
- Write the content you want to send at message.txt file  
- Add image as an attachment through <img>image_relative_path_wrt_main.py</img>  
- Uncomment `chrome_options.add_argument('headless')` at line 12 to run the script headless i.e. without any browser.  

---

- <b>send_message_to_user</b>(user_id, message_text, images_list=None)  
&emsp;&emsp;Load user message section, fill the message and images and send to the user.  
&emsp;&emsp;user_id is the unique identifier associated with a user. It can be discovered by visiting the facebook page of that user and extracting from the URI  
  
`https://www.facebook.com/profile.php?id=10000000000000`  
`https://www.facebook.com/10000000000`  
  
- <b>send_message_csv_file</b>(csv_file, message_text, images=None)  
&emsp;&emsp;Sends messages to users by reading csv_file.  
&emsp;&emsp;csv file must contain 'User_id' column for the default program to run  
&emsp;&emsp;images 

- <b>send_message_list</b>(users_list, message_text, images=None)  
&emsp;&emsp;Sends messages to users through user_ids list.  

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
5. Configure your credentials, i.e. facebook email/username & password at ./confidential/text    
6. Run the program  
`python3 main.py`  
