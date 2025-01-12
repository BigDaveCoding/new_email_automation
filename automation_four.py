import email
import imaplib
import os
import sys
from email.header import decode_header
import json



def login():
    with open('email_credentials.json', 'r') as file:
        credentials = json.load(file)
        username = credentials['username_dave']
        password = credentials['password_dave']

    if username == '' or password == '':
        print('Username or Password is empty')
        exit()

    try:
        mail = imaplib.IMAP4_SSL('imap.gmail.com')
        mail.login(username, password)
        if mail.state == 'AUTH':
            print(mail.state)
            print('Login Successful')
        else:
            print('Login Failed')
            exit()
    except imaplib.IMAP4.error as e:
        print(f'Login Failed: {e}')
        exit()


def get_email_ids():
    pass



login()

