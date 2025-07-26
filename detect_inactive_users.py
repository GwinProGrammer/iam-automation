import boto3
from datetime import datetime, timezone, timedelta

iam = boto3.client('iam')

# Threshold for inactivity
INACTIVE_DAYS = 90

def is_user_inactive(password_last_used):
    """Return True if the user has not signed in within the threshold."""
    if password_last_used is None:
        return True  # Never signed in
    delta = datetime.now(timezone.utc) - password_last_used
    return delta.days >= INACTIVE_DAYS

def main():
    print("Scanning IAM users for inactivity...\n")
    users = iam.list_users()
    
    for user in users['Users']:
        user_name = user['UserName']
        password_last_used = user.get('PasswordLastUsed')  # May be None
        
        if is_user_inactive(password_last_used):
            last_used_str = password_last_used.strftime("%Y-%m-%d") if password_last_used else "Never"
            print(f"[INACTIVE USER] {user_name} | Last sign-in: {last_used_str}")

    print("\nUser inactivity scan complete.")

if __name__ == "__main__":
    main()
