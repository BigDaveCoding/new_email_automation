

# Access email using username and password stored in seperate file
# Use JSON to store username and password

# Access Inbox
# Set a batch of 100
# Create dictionary to store email address and count of emails recieved
# Example : { 'email address' : count }

# Go through batch of emails and store email address in dictionary if it doesnt exist - start count at 1
# If email address exists increment count
# Print dictionary or print email address and count of emails recieved

# Go through each Item in dictionary and ask user what they want to do with the emails recieved from that email address

# Check folders in email - compare folder name to email address
# If folder name contains x amount of chars from email address - Ask user if they want to move emails from that email address to that folder
# If yes - move emails to folder
# If no - continue
# If folder does not exist or user says no - ask user for folder name and create folder
# Move emails to folder

# Repeat process for next email address in dictionary

# Once all emails have been processed - ask user if they want to continue to next batch of emails
# If yes - repeat process
# If no - exit program

import imaplib
import email
import json
from email.header import decode_header

# Load username and password from JSON file
with open('email_credentials.json', 'r') as file:
    data = json.load(file)
    username = data['username']
    password = data['password']

if username == '' or password == '':
    print('Username or Password is empty')
    exit()

try:
    mail = imaplib.IMAP4_SSL('imap.gmail.com')
    mail.login(username, password)
    print('Login Successful')
    inbox = mail.select('inbox')
    print(f'Inbox found {inbox}')
except imaplib.IMAP4.error as e:
    print(f'Login Failed: {e}')

batch_size = 50
email_dict = {}

def get_emails():
    
    status, messages = mail.search(None, 'ALL')
    if status != 'OK':
        print('No Messages found')
        return
    
    email_ids = messages[0].split()
    total_emails = len(email_ids)
    print(f'{len(email_ids)} emails found')

    for i in range(total_emails - batch_size, total_emails):
        email_id = email_ids[i]
        # print(i)
        # print(email_ids[i])

        res, msg_data = mail.fetch(email_ids[i], '(RFC822)')
        # print(res)

        for response_part in msg_data:
            if isinstance(response_part, tuple):
                msg = email.message_from_bytes(response_part[1])
                
                # Get the 'From' field, which contains the email address
                from_header = msg.get("From")
                if from_header:
                    # Parse the 'From' field to extract the email address
                    from_address = email.utils.parseaddr(from_header)[1]
                    # print(f"Email ID: {email_id}, From: {from_address}")
                    if from_address in email_dict:
                        email_dict[from_address] += 1
                    else:
                        email_dict[from_address] = 1
    return

get_emails()
print(email_dict)

def checkForFolder():
    pass