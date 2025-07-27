import boto3
from botocore.exceptions import ClientError
import hvac

iam = boto3.client('iam')

def create_iam_user(username, generate_keys=False):
    try:
        iam.create_user(UserName=username)

        if generate_keys:
            keys = iam.create_access_key(UserName=username)
            access_key = keys['AccessKey']['AccessKeyId']
            secret_key = keys['AccessKey']['SecretAccessKey']

            # Connect to OpenBao (Vault-compatible API)
            client = hvac.Client(
                url="http://127.0.0.1:8200",  # replace with actual OpenBao URL
                token="your-openbao-token"
            )

            client.secrets.kv.v2.create_or_update_secret(
                path=f"iam/{username}",
                secret={
                    "aws_access_key_id": access_key,
                    "aws_secret_access_key": secret_key
                }
            )
            print(f"Keys stored in OpenBao at iam/{username}")

    except ClientError as e:
        print("Error:", e)

# import boto3
# from botocore.exceptions import ClientError
# import hvac

# # Initialize IAM client
# iam = boto3.client('iam')

# def create_iam_user(username, group_name=None, policy_arn=None, generate_keys=False):
#     try:
#         # 1. Create the IAM user
#         print(f"Creating user: {username}")
#         iam.create_user(UserName=username)
        
#         # 2. Add user to a group (optional)
#         if group_name:
#             print(f"Adding user to group: {group_name}")
#             iam.add_user_to_group(
#                 GroupName=group_name,
#                 UserName=username
#             )

#         # 3. Attach policy directly (optional)
#         if policy_arn:
#             print(f"Attaching policy: {policy_arn}")
#             iam.attach_user_policy(
#                 UserName=username,
#                 PolicyArn=policy_arn
#             )

#         # 4. Generate access keys (optional)
#         if generate_keys:
#             print("Generating access keys...")
#             keys = iam.create_access_key(UserName=username)
#             access_key = keys['AccessKey']['AccessKeyId']
#             secret_key = keys['AccessKey']['SecretAccessKey']
#             print("Access Key:", access_key)
#             print("Secret Key:", secret_key)

#         print(f"IAM user '{username}' created successfully.")
    
#     except ClientError as e:
#         print("Error:", e)

# # === Example usage ===
# if __name__ == "__main__":
#     create_iam_user(
#         username="dev_user2",
#         group_name="Developers",  # Optional: must exist
#         policy_arn="arn:aws:iam::aws:policy/ReadOnlyAccess",  # Optional
#         generate_keys=True  # Optional
#     )

# if generate_keys:
#     print("Generating access keys...")
#     keys = iam.create_access_key(UserName=username)
#     access_key = keys['AccessKey']['AccessKeyId']
#     secret_key = keys['AccessKey']['SecretAccessKey']

#     # Initialize OpenBao client
#     client = openbao.Client()  # uses local environment (VAULT_ADDR, VAULT_TOKEN)

#     secret_path = f"iam/{username}"
#     secret_data = {
#         "aws_access_key_id": access_key,
#         "aws_secret_access_key": secret_key
#     }

#     # Write the secrets to OpenBao
#     client.secrets.kv.v2.create_or_update_secret(
#         path=secret_path,
#         secret=secret_data
#     )

#     print(f"Stored credentials in OpenBao under path: {secret_path}")