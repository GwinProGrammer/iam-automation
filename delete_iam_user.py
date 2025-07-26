import boto3
from botocore.exceptions import ClientError

iam = boto3.client('iam')

def delete_iam_user(username):
    try:
        print(f"\nDeleting user: {username}")

        # 1. Detach managed policies
        policies = iam.list_attached_user_policies(UserName=username)['AttachedPolicies']
        for policy in policies:
            print(f" Detaching policy: {policy['PolicyName']}")
            iam.detach_user_policy(
                UserName=username,
                PolicyArn=policy['PolicyArn']
            )

        # 2. Remove user from all groups
        groups = iam.list_groups_for_user(UserName=username)['Groups']
        for group in groups:
            print(f" Removing from group: {group['GroupName']}")
            iam.remove_user_from_group(
                GroupName=group['GroupName'],
                UserName=username
            )

        # 3. Delete access keys
        keys = iam.list_access_keys(UserName=username)['AccessKeyMetadata']
        for key in keys:
            print(f" Deleting access key: {key['AccessKeyId']}")
            iam.delete_access_key(
                UserName=username,
                AccessKeyId=key['AccessKeyId']
            )

        # 4. Delete login profile (if user has console password)
        try:
            iam.delete_login_profile(UserName=username)
            print(" Deleted login profile (console password)")
        except ClientError as e:
            if e.response['Error']['Code'] != 'NoSuchEntity':
                raise

        # 5. Delete inline policies
        inline_policies = iam.list_user_policies(UserName=username)['PolicyNames']
        for policy_name in inline_policies:
            print(f" Deleting inline policy: {policy_name}")
            iam.delete_user_policy(
                UserName=username,
                PolicyName=policy_name
            )

        # 6. Finally, delete the user
        iam.delete_user(UserName=username)
        print(f"✅ Successfully deleted user '{username}'\n")

    except ClientError as e:
        print("❌ Error:", e)

# === Example usage ===
if __name__ == "__main__":
    delete_iam_user("dev_user2")
