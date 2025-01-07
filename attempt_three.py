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
import email.utils
import sys
import os

# Load username and password from JSON file
with open('email_credentials.json', 'r') as file:
    data = json.load(file)
    username = data['username_kankei']
    password = data['password_kankei']
# Make sure username and password are not empty
if username == '' or password == '':
    print('Username or Password is empty')
    exit()

try:
    mail = imaplib.IMAP4_SSL('imap.123-reg.co.uk')
    mail.login(username, password)
    print('Login Successful')
    inbox = mail.select('inbox')
    print(f'Inbox found {inbox}')
except imaplib.IMAP4.error as e:
    print(f'Login Failed: {e}')

def get_email_ids():
    status, messages = mail.search(None, 'ALL')
    if status == 'OK':
        email_ids = messages[0].split()
        return email_ids
    else:
        print('Failed to search emails')
        return []

status, messages = mail.search(None, 'ALL')
email_ids = get_email_ids()
# print(status)
# print(email_ids[-1].decode())


batch_size = 30

folders_list = []

def getFolders():
    status, folders = mail.list()
    if status == 'OK':
        for folder in folders:
            folder_name = folder.decode().split('"/"')[-1].strip().strip('"')
            # if '[Gmail]' not in folder_name:
            #     folders_list.append(folder_name)
            if folder_name and folder_name[0] == 'z':
                folders_list.append(folder_name[1:])
            else:
                folders_list.append(folder_name)   
    folders_list.sort()
getFolders()

# print(folders_list)
# breakpoint()

def findAllFromEmails(email_address):
    status, messages = mail.search(None, f'FROM "{email_address}"')
    email_ids = messages[0].split()

    print(f'Emails from {email_address}: {len(email_ids)}')
    return email_ids

def email_details(email_id):
    status, msg_data = mail.fetch(email_id, '(RFC822)')
    for response_part in msg_data:
        if isinstance(response_part, tuple):
            email_message = email.message_from_bytes(response_part[1])
            from_name, from_email = email.utils.parseaddr(email_message['From'])
            print('Email from: ' + from_email)
            print('Subject: ' + email_message['Subject'])

def moveEmails(email_ids):

    emails_to_delete = []

    while True:
        # print("Folders available:\n " + "\n".join(folders_list))
        print("Type 'new' to create a new folder")
        print("Type folder name to move emails to that folder")
        print("Type 'pass' to skip")
        print("Type 'quit' to exit")
        choice = input('What would you like to do: ')
        if choice.lower() == 'quit':
            sys.exit()
        if choice.lower() == 'new':
            folder_name = input('Enter folder name: ')
            mail.create(folder_name)
            print(f'Folder {folder_name} created')
            for email_id in email_ids:
                # breakpoint()
                print(email_id)
                email_details(email_id)
                mail.copy(email_id, folder_name)
                emails_to_delete.append(email_id)
            break
        elif choice.lower() == 'pass':
            break
        elif choice in folders_list:
            for email_id in email_ids:
                print(email_id)
                email_details(email_id)

                mail.copy(email_id, choice)
                emails_to_delete.append(email_id)
            break
        else:
            print('Invalid choice, Please try again')
    
    # breakpoint()
    
    for email_id in emails_to_delete:
        mail.store(email_id, '+FLAGS', '\\Deleted')
    
    mail.expunge()
    os.system('clear')
    

if email_ids:
    while email_ids:
        for i in range(-1, -min(batch_size, len(email_ids))-1, -1):
            print(i)
            if i < -len(email_ids):
                print(f'Invalid index: {i}')
                continue
            try:
                status, msg_data = mail.fetch(email_ids[i].decode(), '(RFC822)')
                if status == 'OK':
                    for response_part in msg_data:
                        if isinstance(response_part, tuple):
                            email_message = email.message_from_bytes(response_part[1])
                            from_name, from_email = email.utils.parseaddr(email_message['From'])
                            print("Folders available:\n " + "\n".join(folders_list))
                            print('\nEmail from: ' + from_email)
                            print('Name: ' + from_name)
                            print('Subject: ' + email_message['Subject'])

                            ids = findAllFromEmails(from_email)
                            print('ids = ' + str(ids))
                            moveEmails(ids)
                else:
                    print(f'Failed to fetch email with ID {email_ids[i].decode()}')
            except imaplib.IMAP4.error as e:
                print(f'Error fetching email with ID {email_ids[i].decode()}: {e}')
        email_ids = get_email_ids()
else:
    print('No emails found')