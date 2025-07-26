import boto3
from botocore.exceptions import ClientError

# Initialize IAM client
iam = boto3.client('iam')

def create_iam_user(username, group_name=None, policy_arn=None, generate_keys=False):
    try:
        # 1. Create the IAM user
        print(f"Creating user: {username}")
        iam.create_user(UserName=username)
        
        # 2. Add user to a group (optional)
        if group_name:
            print(f"Adding user to group: {group_name}")
            iam.add_user_to_group(
                GroupName=group_name,
                UserName=username
            )

        # 3. Attach policy directly (optional)
        if policy_arn:
            print(f"Attaching policy: {policy_arn}")
            iam.attach_user_policy(
                UserName=username,
                PolicyArn=policy_arn
            )

        # 4. Generate access keys (optional)
        if generate_keys:
            print("Generating access keys...")
            keys = iam.create_access_key(UserName=username)
            access_key = keys['AccessKey']['AccessKeyId']
            secret_key = keys['AccessKey']['SecretAccessKey']
            print("Access Key:", access_key)
            print("Secret Key:", secret_key)

        print(f"IAM user '{username}' created successfully.")
    
    except ClientError as e:
        print("Error:", e)

# === Example usage ===
if __name__ == "__main__":
    create_iam_user(
        username="dev_user2",
        group_name="Developers",  # Optional: must exist
        policy_arn="arn:aws:iam::aws:policy/ReadOnlyAccess",  # Optional
        generate_keys=True  # Optional
    )
