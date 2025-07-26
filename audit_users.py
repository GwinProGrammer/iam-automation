import boto3
from botocore.exceptions import ClientError


# Force an API call to register activity
def trigger_access_key_usage():
    sts = boto3.client("sts")
    try:
        identity = sts.get_caller_identity()
        print(f"Triggered usage: {identity['Arn']}")
    except Exception as e:
        print(f"Failed to trigger usage: {e}")

trigger_access_key_usage()

iam = boto3.client('iam')

def audit_iam_users():
    try:
        response = iam.list_users()
        users = response['Users']

        print("\n📋 IAM User Access Audit")
        print("-" * 60)

        for user in users:
            username = user['UserName']
            created = user['CreateDate'].strftime('%Y-%m-%d %H:%M:%S')

            # Default values
            last_console_login = "N/A"
            access_key_info = "N/A"

            # 1. Check for console login
            try:
                login_profile = iam.get_login_profile(UserName=username)
                user_detail = iam.get_user(UserName=username)
                last_console_login = user_detail['User'].get('PasswordLastUsed', "Never")
                if last_console_login != "Never":
                    last_console_login = last_console_login.strftime('%Y-%m-%d %H:%M:%S')
            except ClientError as e:
                if e.response['Error']['Code'] != 'NoSuchEntity':
                    raise

            # 2. Check access keys and last usage
            access_keys = iam.list_access_keys(UserName=username)['AccessKeyMetadata']
            if access_keys:
                for key in access_keys:
                    key_id = key['AccessKeyId']
                    key_status = key['Status']
                    last_used_resp = iam.get_access_key_last_used(AccessKeyId=key_id)
                    last_used_date = last_used_resp['AccessKeyLastUsed'].get('LastUsedDate', 'Never')
                    if last_used_date != 'Never':
                        last_used_date = last_used_date.strftime('%Y-%m-%d %H:%M:%S')
                    access_key_info = f"{key_id} (Status: {key_status}, Last Used: {last_used_date})"

            # Print user details
            print(f"👤 User: {username}")
            print(f"   🕒 Created: {created}")
            print(f"   🔐 Console Login: {last_console_login}")
            print(f"   🔑 Access Key: {access_key_info}")
            print("-" * 60)

    except ClientError as e:
        print("❌ Error:", e)

# === Run the audit ===
if __name__ == "__main__":
    audit_iam_users()
