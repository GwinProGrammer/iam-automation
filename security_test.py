import boto3
import logging
from datetime import datetime, timezone

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

iam = boto3.client('iam')

# Simulated compromised key ID (replace with actual key ID to test)
COMPROMISED_ACCESS_KEY_ID = 'AKIAS24SAAI3ANUDYDGA'

def list_user_access_keys(username):
    response = iam.list_access_keys(UserName=username)
    return response['AccessKeyMetadata']

def disable_access_key(username, access_key_id):
    iam.update_access_key(UserName=username, AccessKeyId=access_key_id, Status='Inactive')
    logging.info(f"Disabled access key {access_key_id} for user {username}")

def create_access_key(username):
    response = iam.create_access_key(UserName=username)
    access_key = response['AccessKey']
    logging.info(f"Created new access key {access_key['AccessKeyId']} for user {username}")
    return access_key

def find_user_by_access_key(access_key_id):
    # List all users and their keys (may be expensive in prod)
    paginator = iam.get_paginator('list_users')
    for page in paginator.paginate():
        for user in page['Users']:
            keys = list_user_access_keys(user['UserName'])
            for key in keys:
                if key['AccessKeyId'] == access_key_id:
                    return user['UserName']
    return None

def simulate_compromised_key_detection():
    # In a real system, detection might come from logs or anomaly detection
    compromised_key_id = COMPROMISED_ACCESS_KEY_ID
    logging.warning(f"Detected compromised access key: {compromised_key_id}")
    return compromised_key_id

def handle_compromised_key(access_key_id):
    username = find_user_by_access_key(access_key_id)
    if not username:
        logging.error(f"Access key {access_key_id} not found for any user")
        return

    logging.info(f"Handling compromised key for user: {username}")

    # Disable old key
    disable_access_key(username, access_key_id)

    # Create new key
    new_key = create_access_key(username)

    # Log the incident (could be extended to send email or webhook)
    incident_log = {
        'user': username,
        'old_key': access_key_id,
        'new_key': new_key['AccessKeyId'],
        'timestamp': datetime.now(timezone.utc).isoformat()
    }
    logging.info(f"Security incident handled: {incident_log}")

def main():
    compromised_key = simulate_compromised_key_detection()
    handle_compromised_key(compromised_key)

if __name__ == '__main__':
    main()
