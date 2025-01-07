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


batch_size = 5

folders_list = []

def getFolders():
    status, folders = mail.list()
    for folder in folders:
        folder_name = folder.decode().split('"/"')[-1].strip().strip('"')
        if '[Gmail]' not in folder_name:
            folders_list.append(folder_name)
getFolders()

# print(folders_list)
breakpoint()

def findAllFromEmails(email_address):
    status, messages = mail.search(None, f'FROM "{email_address}"')
    email_ids = messages[0].split()

    print(f'Emails from {email_address}: {len(email_ids)}')
    return email_ids

def moveEmails(email_ids):

    emails_to_delete = []

    while True:
        print("Folders available: " + str(folders_list))
        print("Type 'new' to create a new folder")
        print("Type folder name to move emails to that folder")
        print("Type 'pass' to skip")
        choice = input('What would you like to do: ')
        if choice.lower() == 'new':
            folder_name = input('Enter folder name: ')
            mail.create(folder_name)
            print(f'Folder {folder_name} created')
            for email_id in email_ids:
                # breakpoint()
                print(email_id)
                status, msg_data = mail.fetch(email_id, '(RFC822)')
                for response_part in msg_data:
                    if isinstance(response_part, tuple):
                        email_message = email.message_from_bytes(response_part[1])
                        from_name, from_email = email.utils.parseaddr(email_message['From'])
                        print('Email from: ' + from_email)
                        print('Subject: ' + email_message['Subject'])
                        mail.copy(email_id, folder_name)
                        emails_to_delete.append(email_id)
            break
        elif choice.lower() == 'pass':
            break
        elif choice in folders_list:
            for email_id in email_ids:
                mail.copy(email_id, choice)
                emails_to_delete.append(email_id)
            break
        else:
            print('Invalid choice, Please try again')
    
    breakpoint()
    
    for email_id in emails_to_delete:
        mail.store(email_id, '+FLAGS', '\\Deleted')
    
    mail.expunge()

for i in range(-1, batch_size * -1, -1):
    print(i)
    status, msg_data = mail.fetch(email_ids[i].decode(), '(RFC822)')
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

            ids = findAllFromEmails(from_email)
            print('ids = ' + str(ids))
            moveEmails(ids)