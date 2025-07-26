import boto3
import json
import sys

# Initialize boto3 clients
iam_client = boto3.client('iam')
secrets_client = boto3.client('secretsmanager')

def create_iam_user(username):
    try:
        response = iam_client.create_user(UserName=username)
        print(f"IAM user '{username}' created.")
        return response['User']['UserName']
    except iam_client.exceptions.EntityAlreadyExistsException:
        print(f"User '{username}' already exists.")
        return username
    except Exception as e:
        print(f"Error creating user: {e}")
        sys.exit(1)

def create_access_key(username):
    try:
        response = iam_client.create_access_key(UserName=username)
        access_key = response['AccessKey']
        print(f"Access key created for user '{username}'.")
        return access_key['AccessKeyId'], access_key['SecretAccessKey']
    except Exception as e:
        print(f"Error creating access key: {e}")
        sys.exit(1)

def store_access_keys(username, access_key_id, secret_access_key):
    secret_name = f"iam/{username}/access-keys"
    secret_value = json.dumps({
        "AccessKeyId": access_key_id,
        "SecretAccessKey": secret_access_key
    })
    try:
        # Try to create the secret
        secrets_client.create_secret(
            Name=secret_name,
            SecretString=secret_value
        )
        print(f"Secret created in Secrets Manager for user '{username}'.")
    except secrets_client.exceptions.ResourceExistsException:
        # If secret exists, update it
        secrets_client.update_secret(
            SecretId=secret_name,
            SecretString=secret_value
        )
        print(f"Secret updated in Secrets Manager for user '{username}'.")
    except Exception as e:
        print(f"Error storing secret: {e}")
        sys.exit(1)

def get_access_keys(username):
    secret_name = f"iam/{username}/access-keys"
    try:
        response = secrets_client.get_secret_value(SecretId=secret_name)
        secret = json.loads(response['SecretString'])
        print(f"Retrieved secrets for user '{username}'.")
        return secret['AccessKeyId'], secret['SecretAccessKey']
    except Exception as e:
        print(f"Error retrieving secret: {e}")
        return None, None

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python iam_secrets_manager.py <username>")
        sys.exit(1)
    
    user = sys.argv[1]

    # Create user (if not exists)
    create_iam_user(user)

    # Create access keys
    access_key_id, secret_access_key = create_access_key(user)

    # Store keys in Secrets Manager
    store_access_keys(user, access_key_id, secret_access_key)

    # Retrieve and print to verify
    stored_access_key_id, stored_secret_access_key = get_access_keys(user)
    print(f"Stored AccessKeyId: {stored_access_key_id}")
    # Do NOT print secret access key in real scripts; only for testing here
    print(f"Stored SecretAccessKey: {stored_secret_access_key}")
