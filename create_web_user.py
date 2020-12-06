#!/usr/bin/python3
import argparse
import json
from os import _exit

try:
    from passlib.context import CryptContext
except ImportError:
    print("You need to run")
    print("pip install passlib bcrypt")
    _exit()


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

try:
    with open("web_user_db.json", "r") as f:
        users_db = json.loads(f.read())
except FileNotFoundError:
    users_db = {}
    print("web_user_db.json file does not exist.")
    _exit()

parser = argparse.ArgumentParser(description="Create user for web authentication")
parser.add_argument("--user", help="Specifiy the username", required=True)
parser.add_argument("--email", help="Specify email address")
parser.add_argument("--name", help="Users name")

args = parser.parse_args()

password = input("Enter new password: ")

if args.user not in users_db.keys():
    users_db[args.user] = dict()
    users_db[args.user]["username"] = None
    users_db[args.user]["email"] = None
    users_db[args.user]["full_name"] = None
    users_db[args.user]["hashed_password"] = None
    users_db[args.user]["disabled"] = False


users_db[args.user]["username"] = args.user
if args.email:
    users_db[args.user]["email"] = args.email
if args.name:
    users_db[args.user]["full_name"] = args.name

# Create new password hash
new_hash = pwd_context.hash(password)
users_db[args.user]["hashed_password"] = new_hash

with open("web_user_db.json", "w") as f:
    f.write(json.dumps(users_db, indent=1))
