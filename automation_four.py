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
    

login()
email_ids = get_email_ids()
