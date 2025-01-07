# Access email using username and password stored in seperate file
# Use JSON to store username and password

# Access Inbox
# Set a batch of 20
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
    username = data['username_dave']
    password = data['password_dave']
# Make sure username and password are not empty
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

status, messages = mail.search(None, 'ALL')
email_ids = messages[0].split()
print(status)
print(email_ids[-1].decode())

status, msg_data = mail.fetch(email_ids[-1].decode(), '(RFC822)')
# mail.fetch return data is tuples
# for each tuple in msg_data...
for response_part in msg_data:
    # if response_part is tuple, which it should be...
    if isinstance(response_part, tuple):
        email_message = email.message_from_bytes(response_part[1])
        # print(email_message['To'])
        from_name, from_email = email.utils.parseaddr(email_message['From'])
        print('Email from: ' + from_email)
        print('Subject: ' + email_message['Subject'])

