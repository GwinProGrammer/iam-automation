import boto3
from datetime import datetime, timezone
import sys

# Settings
USERNAME = "gwins-mac"  # <-- Replace this
MAX_KEY_AGE_DAYS = 90
STORE_IN_SECRETS_MANAGER = False
SECRET_NAME = f"{USERNAME}_access_keys"

# Clients
iam = boto3.client('iam')
secretsmanager = boto3.client('secretsmanager')

def get_key_age(key):
    create_date = key['CreateDate']
    age = (datetime.now(timezone.utc) - create_date).days
    return age

def rotate_access_key(username):
    print(f"🔄 Rotating access key for user: {username}")

    # Step 1: List access keys
    keys = iam.list_access_keys(UserName=username)['AccessKeyMetadata']
    print(f"🔑 Found {len(keys)} key(s).")

    # Step 2: Check for active keys and their age
    for key in keys:
        age = get_key_age(key)
        print(f"🕒 Key {key['AccessKeyId']} is {age} days old.")

        if age >= MAX_KEY_AGE_DAYS:
            print("⚠️ Key is too old, rotating...")
            
            # Step 3: Create new access key
            new_key = iam.create_access_key(UserName=username)['AccessKey']
            print(f"✅ New key created: {new_key['AccessKeyId']}")

            # Step 4: Deactivate old key
            iam.update_access_key(UserName=username,
                                  AccessKeyId=key['AccessKeyId'],
                                  Status='Inactive')
            print(f"🚫 Deactivated old key: {key['AccessKeyId']}")

            # Step 5: Optionally delete old key
            iam.delete_access_key(UserName=username,
                                  AccessKeyId=key['AccessKeyId'])
            print(f"❌ Deleted old key: {key['AccessKeyId']}")

            # Step 6: Optionally store new key in Secrets Manager
            if STORE_IN_SECRETS_MANAGER:
                store_in_secrets_manager(new_key)

            return
    
    print("✅ No keys required rotation.")

def store_in_secrets_manager(new_key):
    secret_value = {
        "aws_access_key_id": new_key['AccessKeyId'],
        "aws_secret_access_key": new_key['SecretAccessKey']
    }

    try:
        secretsmanager.create_secret(
            Name=SECRET_NAME,
            SecretString=str(secret_value)
        )
        print(f"🔐 Stored keys in Secrets Manager under: {SECRET_NAME}")
    except secretsmanager.exceptions.ResourceExistsException:
        secretsmanager.update_secret(
            SecretId=SECRET_NAME,
            SecretString=str(secret_value)
        )
        print(f"🔄 Updated existing secret: {SECRET_NAME}")

if __name__ == "__main__":
    try:
        rotate_access_key(USERNAME)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
