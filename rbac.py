import boto3
import sys

iam_client = boto3.client('iam')

def create_iam_user(username):
    try:
        response = iam_client.create_user(UserName=username)
        print(f"IAM user '{username}' created.")
    except iam_client.exceptions.EntityAlreadyExistsException:
        print(f"User '{username}' already exists.")
    except Exception as e:
        print(f"Error creating user: {e}")
        sys.exit(1)

def assign_user_to_group(username, role):
    role_to_group = {
        'admin': 'Admins',
        'developer': 'Developers',
        'auditor': 'Auditors'
    }

    group_name = role_to_group.get(role.lower())
    if not group_name:
        print(f"No group mapping found for role '{role}'. User not assigned.")
        return

    try:
        iam_client.add_user_to_group(GroupName=group_name, UserName=username)
        print(f"User '{username}' added to group '{group_name}'.")
    except Exception as e:
        print(f"Error adding user to group: {e}")

def tag_user(username, tags):
    try:
        iam_client.tag_user(UserName=username, Tags=tags)
        print(f"User '{username}' tagged with {tags}.")
    except Exception as e:
        print(f"Error tagging user: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python rbac_user_management.py <username> <role> [<department>]")
        sys.exit(1)

    username = sys.argv[1]
    role = sys.argv[2]
    department = sys.argv[3] if len(sys.argv) > 3 else None

    create_iam_user(username)
    assign_user_to_group(username, role)

    if department:
        tags = [{'Key': 'Department', 'Value': department}, {'Key': 'Role', 'Value': role}]
    else:
        tags = [{'Key': 'Role', 'Value': role}]

    tag_user(username, tags)
