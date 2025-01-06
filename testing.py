import imaplib
import email
import json
from email.header import decode_header

# Load username and password from JSON file
with open('email_credentials.json', 'r') as file:
    data = json.load(file)
    username = data['username_kankei']
    password = data['password_kankei']

if username == '' or password == '':
    print('Username or Password is empty')
    exit()

try:
    mail = imaplib.IMAP4_SSL('imap.123-reg.co.uk')
    mail.login(username, password)
    print('Login Successful')
    mail.select('inbox')
except imaplib.IMAP4.error as e:
    print(f'Login Failed: {e}')
    exit()

batch_size = 10
email_dict = {}
folders_list = []

def get_emails():
    """Retrieve the latest batch of emails and populate the email dictionary."""
    status, messages = mail.search(None, 'ALL')
    if status != 'OK':
        print('No Messages found')
        return []
    
    email_ids = messages[0].split()
    total_emails = len(email_ids)
    print(f'{total_emails} emails found')

    # Get the latest batch of emails
    batch_ids = email_ids[max(total_emails - batch_size, 0):total_emails]
    for email_id in batch_ids:
        res, msg_data = mail.fetch(email_id, '(RFC822)')
        for response_part in msg_data:
            if isinstance(response_part, tuple):
                msg = email.message_from_bytes(response_part[1])
                from_header = msg.get("From")
                if from_header:
                    from_address = email.utils.parseaddr(from_header)[1]
                    if from_address:
                        email_dict[from_address] = email_dict.get(from_address, 0) + 1
    return batch_ids


def checkForFolder():
    """Retrieve the list of folders, excluding [Gmail] folders."""
    status, folders = mail.list()
    if status == 'OK':
        for folder in folders:
            decoded_folder = folder.decode()
            folder_name = decoded_folder.split('"/"')[-1].strip().strip('"')
            if not folder_name.startswith('[Gmail]'):
                folders_list.append(folder_name)
        folders_list.sort()
    else:
        print('Failed to get folders')
    return


def find_matching_folder(email, folders):
    """Match email prefix substrings with folder names based on full or partial matches."""
    email_prefix = email.split('@')[0].lower()  # Get the email prefix (before @) and convert to lowercase
    matched_folders = []

    # Check for folder names that directly contain the email prefix (case-insensitive)
    for folder in folders:
        folder_lower = folder.lower()

        # Match if the folder name contains the email prefix or some common variations
        if email_prefix in folder_lower or folder_lower.startswith('z' + email_prefix):
            matched_folders.append(folder)

    return matched_folders


def get_matching_folders(email_address):
    """Retrieve matching folders based on email prefix."""
    matching_folders = find_matching_folder(email_address, folders_list)
    # Return matching folders or all folders if no match
    return matching_folders if matching_folders else folders_list


def moveEmails(batch_ids):
    """Process only the batch of emails for actions like moving to folders."""
    batch_emails = list(email_dict.keys())  # Get the batch of email addresses from the dictionary

    # Ensure batch_ids is not empty
    if not batch_ids:
        print("No emails to move. Exiting.")
        return

    for key in batch_emails:
        value = email_dict[key]
        print(f'\nYou have {value} emails from {key}')
        
        # Get the matching folders based on the email address
        matching_folders = get_matching_folders(key)
        
        if matching_folders:
            print(f'Available folders: {matching_folders}')
        else:
            # Print 'No similar folders' if no matching folders are found
            print("No similar folders")
            continue  # Skip to the next email in the batch

        while True:
            choice = input(
                f'Choose a folder to move emails to, type "New" to create a new folder, or "Pass" to skip: ').strip()
            
            if choice.lower() in (folder.lower() for folder in matching_folders):
                # Move batch emails to the existing folder
                print(f'Moving emails from {key} to {choice}...')
                processed_count = 0  # Track the number of emails moved
                for email_id in batch_ids:
                    if processed_count >= batch_size:
                        break
                    # Check if email_id is valid (non-empty and a proper ID)
                    if not email_id:
                        print(f"Skipping invalid email ID: {email_id}")
                        continue
                    # Fetch the email to verify the sender
                    try:
                        res, msg_data = mail.fetch(email_id, '(RFC822)')
                        if res != 'OK':
                            print(f"Failed to fetch email ID {email_id}")
                            continue
                    except imaplib.IMAP4.error as e:
                        print(f"Error fetching email ID {email_id}: {e}")
                        continue
                    
                    # Now process the email
                    for response_part in msg_data:
                        if isinstance(response_part, tuple):
                            msg = email.message_from_bytes(response_part[1])
                            from_header = msg.get("From")
                            if from_header:
                                from_address = email.utils.parseaddr(from_header)[1]
                                if from_address == key:  # Only move emails from the correct sender
                                    try:
                                        mail.copy(email_id, choice)
                                        mail.store(email_id, '+FLAGS', '\\Deleted')
                                        processed_count += 1
                                    except Exception as e:
                                        print(f'Error moving email ID {email_id}: {e}')
                mail.expunge()
                print(f'{processed_count} emails from {key} moved to {choice}.')
                break

            elif choice.lower() == 'new':
                # Create a new folder and move batch emails
                new_folder = input('Enter new folder name: ').strip()
                try:
                    status, _ = mail.create(new_folder)
                    if status != 'OK':
                        print(f'Failed to create folder: {new_folder}')
                        continue
                except Exception as e:
                    print(f'Error creating folder {new_folder}: {e}')
                    continue

                folders_list.append(new_folder)
                print(f'Moving emails from {key} to {new_folder}...')
                processed_count = 0  # Track the number of emails moved
                for email_id in batch_ids:
                    if processed_count >= batch_size:
                        break
                    # Fetch the email to verify the sender
                    try:
                        res, msg_data = mail.fetch(email_id, '(RFC822)')
                        if res != 'OK':
                            print(f"Failed to fetch email ID {email_id}")
                            continue
                    except imaplib.IMAP4.error as e:
                        print(f"Error fetching email ID {email_id}: {e}")
                        continue
                    
                    for response_part in msg_data:
                        if isinstance(response_part, tuple):
                            msg = email.message_from_bytes(response_part[1])
                            from_header = msg.get("From")
                            if from_header:
                                from_address = email.utils.parseaddr(from_header)[1]
                                if from_address == key:  # Only move emails from the correct sender
                                    try:
                                        mail.copy(email_id, new_folder)
                                        mail.store(email_id, '+FLAGS', '\\Deleted')
                                        processed_count += 1
                                    except Exception as e:
                                        print(f'Error moving email ID {email_id}: {e}')
                mail.expunge()
                print(f'{processed_count} emails from {key} moved to {new_folder}.')
                break

            elif choice.lower() == 'pass':
                # Skip processing this email sender
                print(f'Skipping emails from {key}.')
                break

            else:
                print('Invalid choice. Please try again.')

    return



# Main Process
while True:
    batch_ids = get_emails()  # Fetch emails for the batch
    checkForFolder()  # Check for available folders
    print("\nEmail Dictionary:", email_dict)
    print("Folders List:", folders_list)
    moveEmails(batch_ids)  # Move emails based on user input

    # Ask the user if they want to continue to the next batch
    continue_batch = input('Do you want to process another batch of emails? (y/n): ').strip().lower()
    if continue_batch != 'y':
        print('Exiting program.')
        break
