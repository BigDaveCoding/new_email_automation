import email
import imaplib
import os
import sys
from email.header import decode_header
import json


mail = imaplib.IMAP4_SSL('imap.gmail.com')

def login():
    with open('email_credentials.json', 'r') as file:
        credentials = json.load(file)
        username = credentials['username_dave']
        password = credentials['password_dave']

    if username == '' or password == '':
        print('Username or Password is empty')
        exit()

    try:
        mail.login(username, password)
        if mail.state == 'AUTH':
            print('Login Successful')
        else:
            print('Login Failed')
            exit()
    except imaplib.IMAP4.error as e:
        print(f'Login Failed: {e}')
        exit()


def get_email_ids():
    mail.select('inbox')
    status, messages = mail.search(None, 'ALL')
    print(status)
    if status == 'OK':
        email_ids = messages[0].split()
        print(len(email_ids))
        return email_ids
    else:
        print('Failed to search emails')
        return []
    
def findAllEmails(email_ids):
    for email_id in email_ids[::-1]:
        status, message = mail.fetch(email_id, '(RFC822)')
        if status == 'OK':
            email_message = email.message_from_bytes(message[0][1])
            from_name, email_address = email.utils.parseaddr(email_message['From'])
            print(f'from: {from_name}') 
            print(f'email: {email_address}')
            print(f'subject: {email_message["Subject"]}')

            status, messages = mail.search(None, f"FROM {email_address}")
            print(f'You have {len(messages[0].split())} from this sender')
            
            if len(messages[0].split()) < 5:
                print('Less than 5 emails from this sender')
                continue
            else:
                return messages[0].split() 
        else:
            print('Failed to fetch email')
            exit()

def moveEmails(ids_from_address):
    try:
        for email_id in ids_from_address:
            status, message = mail.fetch(email_id, '(RFC822)')
            if status == 'OK':
                email_message = email.message_from_bytes(message[0][1])
                from_name, email_address = email.utils.parseaddr(email_message['From'])
            else:
                print('Failed to fetch email')
    except Exception as e:
        print(f'Error: {e}')

def getFolders():
    folders_list = []
    status, folders = mail.list()
    if status == 'OK':
        for folder in folders:
            folder_name = folder.decode().split('"/"')[-1].strip().strip('"')
            folders_list.append(folder_name)
    return folders_list



def moveWhere(folders_list):
    while True:
        print("Folders available: \n" + "\n".join(folders_list))
        print('Type the folder name you want to move the emails to')
        print("'new' to create a new folder")
        print("type 'skip' to skip email")
        print("type 'exit' to exit")
        user_choice = input()
        if user_choice.lower() != 'new' or user_choice.lower() != 'skip' or user_choice.lower() != 'exit' or user_choice not in folders_list:
            print('Invalid choice')
            continue
        else:
            return user_choice

login()
email_ids = get_email_ids()
ids_from_address = findAllEmails(email_ids)
get_folders = getFolders()