import boto3
import json
from botocore.exceptions import ClientError

iam = boto3.client('iam')

def is_overly_permissive(statement):
    """Check if a policy statement is too permissive."""
    actions = statement.get('Action', [])
    resources = statement.get('Resource', [])
    
    if isinstance(actions, str):
        actions = [actions]
    if isinstance(resources, str):
        resources = [resources]
    
    return ('*' in actions) or ('*' in resources)

def check_inline_policies(user_name):
    """Check inline policies attached directly to the user."""
    response = iam.list_user_policies(UserName=user_name)
    for policy_name in response['PolicyNames']:
        policy = iam.get_user_policy(UserName=user_name, PolicyName=policy_name)
        document = policy['PolicyDocument']
        statements = document['Statement']
        if isinstance(statements, dict):  # Handle single statement
            statements = [statements]

        for statement in statements:
            if is_overly_permissive(statement):
                print(f"[RISK] Inline policy '{policy_name}' for user '{user_name}' is overly permissive.")

def check_attached_managed_policies(user_name):
    """Check managed policies attached to the user."""
    response = iam.list_attached_user_policies(UserName=user_name)
    for attached in response['AttachedPolicies']:
        policy_arn = attached['PolicyArn']
        policy_name = attached['PolicyName']
        try:
            versions = iam.list_policy_versions(PolicyArn=policy_arn)
            default_version = next(v for v in versions['Versions'] if v['IsDefaultVersion'])
            version = iam.get_policy_version(
                PolicyArn=policy_arn,
                VersionId=default_version['VersionId']
            )
            document = version['PolicyVersion']['Document']
            statements = document['Statement']
            if isinstance(statements, dict):  # Handle single statement
                statements = [statements]

            for statement in statements:
                if is_overly_permissive(statement):
                    print(f"[RISK] Managed policy '{policy_name}' for user '{user_name}' is overly permissive.")
        except ClientError as e:
            print(f"[ERROR] Could not retrieve policy '{policy_name}' for user '{user_name}': {e}")

def main():
    print("Auditing IAM users for overly permissive policies...\n")
    users = iam.list_users()
    for user in users['Users']:
        user_name = user['UserName']
        print(f"Checking user: {user_name}")
        check_inline_policies(user_name)
        check_attached_managed_policies(user_name)
    print("\nAudit complete.")

if __name__ == "__main__":
    main()
