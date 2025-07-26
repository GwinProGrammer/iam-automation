import boto3
from datetime import datetime, timezone, timedelta

iam = boto3.client('iam')

# Define how old is "too old"
STALE_DAYS = 90

def is_key_stale(last_used_date):
    """Check if the access key is older than the stale threshold."""
    if last_used_date is None:
        return True  # Key has never been used
    age = datetime.now(timezone.utc) - last_used_date
    return age.days >= STALE_DAYS

def check_user_keys(user_name):
    """Check access keys for a given user."""
    keys = iam.list_access_keys(UserName=user_name)['AccessKeyMetadata']
    for key in keys:
        key_id = key['AccessKeyId']
        key_status = key['Status']
        key_create_date = key['CreateDate']

        try:
            usage = iam.get_access_key_last_used(AccessKeyId=key_id)
            last_used = usage['AccessKeyLastUsed'].get('LastUsedDate')
        except Exception as e:
            print(f"[ERROR] Couldn't get usage for key {key_id}: {e}")
            continue

        if is_key_stale(last_used):
            last_used_str = last_used.strftime("%Y-%m-%d") if last_used else "Never used"
            print(f"[STALE KEY] User '{user_name}' | Key '{key_id}' last used: {last_used_str} | Status: {key_status}")

def main():
    print("Auditing IAM access keys for staleness...\n")
    users = iam.list_users()
    for user in users['Users']:
        user_name = user['UserName']
        print(f"Checking user: {user_name}")
        check_user_keys(user_name)
    print("\nAccess key audit complete.")

if __name__ == "__main__":
    main()
