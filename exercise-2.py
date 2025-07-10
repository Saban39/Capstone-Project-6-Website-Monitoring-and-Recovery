import boto3
from datetime import datetime

# Initialize IAM client
iam = boto3.client('iam')

# Get list of IAM users
response = iam.list_users()
users = response.get("Users", [])

last_active_user = None

print(f"{'UserName':<25} {'PasswordLastUsed'}")
print("-" * 50)

for user in users:
    username = user["UserName"]
    last_used = user.get("PasswordLastUsed")

    # Print user and last login time (or 'Never')
    if last_used:
        print(f"{username:<25} {last_used}")
    else:
        print(f"{username:<25} Never logged in")

    # Find the most recently active user
    if last_used:
        if last_active_user is None or last_used > last_active_user["PasswordLastUsed"]:
            last_active_user = user

print("\nMost recently active user:")
if last_active_user:
    print(f"User ID   : {last_active_user['UserId']}")
    print(f"Username  : {last_active_user['UserName']}")
    print(f"Last Used : {last_active_user['PasswordLastUsed']}")
else:
    print("No user has logged in yet.")
