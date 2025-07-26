import boto3

iam = boto3.client('iam')
sts = boto3.client('sts')

def get_account_alias():
    try:
        aliases = iam.list_account_aliases()['AccountAliases']
        return aliases[0] if aliases else "No alias"
    except Exception:
        return "Error retrieving alias"

def get_account_id():
    return sts.get_caller_identity()['Account']

def list_users():
    return iam.list_users()['Users']

def get_console_access_info(username):
    try:
        login_profile = iam.get_login_profile(UserName=username)
        password_enabled = True
    except iam.exceptions.NoSuchEntityException:
        password_enabled = False
    user_info = iam.get_user(UserName=username)['User']
    password_last_used = user_info.get('PasswordLastUsed')
    return password_enabled, password_last_used

def main():
    alias = get_account_alias()
    account_id = get_account_id()
    
    print(f"\n🧾 AWS Account Info:\n - Alias: {alias}\n - ID: {account_id}\n")
    print("👤 IAM Users:")

    for user in list_users():
        username = user['UserName']
        password_enabled, password_last_used = get_console_access_info(username)
        last_used_str = password_last_used.strftime('%Y-%m-%d') if password_last_used else "Never"

        print(f"\n - Username: {username}")
        print(f"   Password Enabled: {password_enabled}")
        print(f"   Password Last Used: {last_used_str}")

if __name__ == "__main__":
    main()
