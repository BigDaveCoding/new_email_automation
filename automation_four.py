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
    

login()
email_ids = get_email_ids()
emails_from = findAllEmails(email_ids)
print(emails_from)
