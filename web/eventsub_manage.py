#!/usr/bin/env python
import argparse
import datetime
import json
from os import getenv
from time import sleep

import requests
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker

from models import Settings

channel = getenv("TWITCH_CHANNEL")
host = f"https://{getenv('WEB_HOSTNAME')}/twitch/eventsub"
signing_secret = getenv("TWITCH_SIGNING_SECRET")

mysql_database = getenv("MYSQL_DATABASE")
mysql_user = getenv("MYSQL_USER")
mysql_pass = getenv("MYSQL_PASSWORD")

engine = create_engine(f"mysql+mysqlconnector://{mysql_user}:{mysql_pass}@mysql:3306/{mysql_database}")

session = scoped_session(sessionmaker(bind=engine))

# Used for checking current subscriptions instead of redoing the subscribes
parser = argparse.ArgumentParser()
parser.add_argument("--check", action="store_true")
parser.add_argument("--disable", action="store_true")
args = parser.parse_args()

if args.check and args.disable:
    print("Can't run both check and disable at the same time.")
    raise SystemExit


def get_app_key(force_update: bool = False):

    # Get client_id and client_secret
    res = session.query(Settings).filter(Settings.key == "twitch_client").one_or_none()
    if not res:
        # Just in case it wasn't in the database, get it from environment variables and insert it
        client_id = getenv("CLIENT_ID") or getenv("client_id")
        client_secret = getenv("CLIENT_SECRET") or getenv("client_secret")
        res = Settings(key="twitch_client", value=json.dumps({"id": client_id, "secret": client_secret}))
        session.add(res)
        session.commit()

    res = json.loads(res.value)
    client_id = res["id"]
    client_secret = res["secret"]

    # Grab the app key
    app_key = session.query(Settings).filter(Settings.key == "twitch_app_access").one_or_none()
    if app_key and not force_update:
        # Check to make sure it isn't expired already
        values = json.loads(app_key.value)
        values["client_id"] = client_id
        values["expires_at"] = datetime.datetime.fromisoformat(values["expires_at"])
        app_key_expired = True if datetime.datetime.now() > values["expires_at"] else False

        if not app_key_expired:
            # Key existed in database, and is valid
            return values

    # Get the app_key
    scopes = [""]  # Scopes for the key request
    url = f"https://id.twitch.tv/oauth2/token?client_id={client_id}&client_secret={client_secret}&grant_type=client_credentials&scope={' '.join(scopes)}"  # noqa E501

    r = requests.post(url)
    content = json.loads(r.content.decode("utf-8"))

    content["expires_at"] = datetime.datetime.now() + datetime.timedelta(seconds=content["expires_in"] - 60)
    # Remove the expires_in because it will be inaccurate when retrieved from database
    del content["expires_in"]

    res = (
        session.query(Settings)
        .filter(Settings.key == "twitch_app_access")
        .update({"value": json.dumps(content, default=str)})
    )
    if not res:
        ins = Settings(key="twitch_app_access", value=json.dumps(content, default=str))
        session.add(ins)
        session.commit()
        content["client_id"] = client_id  # Don't want to add this to this database entry
        return content
    else:
        print("twitch_app_access updated")
        session.commit()
        content["client_id"] = client_id  # Don't want to add this to this database entry
        return content


def get_url(url, counter: int = 0):
    """Retrieves the URL passed, handling 401 errors and forcing an update of the app_key in the process"""
    app_key = get_app_key(force_update=counter)  # Won't force on the first run, but will on subsequent
    headers = {"client-id": app_key["client_id"], "Authorization": f"Bearer {app_key['access_token']}"}

    try:
        r = requests.get(url, headers=headers)
        r.raise_for_status()
        return r
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            if counter > 3:
                print(f"Unable to successfully query {url} - {e}. Exiting...")
                raise SystemExit
            else:
                print(f"Sleeping {counter} seconds")
                sleep(counter)
                return get_url(url, counter=counter + 1)

        raise (e)
    except requests.exceptions.ConnectionError as e:
        print(f"Connection error for {url} - {e}. Exiting...")
        raise SystemExit


def post_url(url, event: dict, counter: int = 0):
    """Retrieves the URL passed, handling 401 errors and forcing an update of the app_key in the process"""
    app_key = get_app_key(force_update=counter)  # Won't force on the first run, but will on subsequent
    headers = {
        "client-id": app_key["client_id"],
        "Authorization": f"Bearer {app_key['access_token']}",
        "Content-Type": "application/json",
    }

    try:
        r = requests.post(url, data=json.dumps(event), headers=headers)
        r.raise_for_status()
        return r
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            if counter > 3:
                print(f"Unable to successfully query {url} - {e}. Exiting...")
                raise SystemExit
            else:
                print(f"Sleeping {counter} seconds")
                sleep(counter)
                return post_url(url, event, counter=counter + 1)
        elif e.response.status_code == 400:
            print(f"Invalid values sent to the server for {event}")
            raise SystemExit

        raise (e)
    except requests.exceptions.ConnectionError as e:
        print(f"Connection error for {url} - {e}. Exiting...")
        raise SystemExit


def delete_url(url, counter: int = 0):
    """Retrieves the URL passed, handling 401 errors and forcing an update of the app_key in the process"""
    app_key = get_app_key(force_update=counter)  # Won't force on the first run, but will on subsequent
    headers = {"client-id": app_key["client_id"], "Authorization": f"Bearer {app_key['access_token']}"}

    try:
        r = requests.delete(url, headers=headers)
        r.raise_for_status()
        return r
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            if counter > 3:
                print(f"Unable to successfully query {url} - {e}. Exiting...")
                raise SystemExit
            else:
                print(f"Sleeping {counter} seconds")
                sleep(counter)
                return delete_url(url, counter=counter + 1)

        raise (e)
    except requests.exceptions.ConnectionError as e:
        print(f"Connection error for {url} - {e}. Exiting...")
        raise SystemExit


user_data = json.loads(get_url(f"https://api.twitch.tv/helix/users?login={channel}").content.decode("utf-8"))["data"][0]
channel_id = user_data["id"]

# Check current subscriptions
url = "https://api.twitch.tv/helix/eventsub/subscriptions"
r = get_url(url)
current_eventsub = json.loads(r.content.decode("utf-8"))

events = [
    {
        "type": "channel.follow",
        "version": "1",
        "condition": {"broadcaster_user_id": channel_id},
        "transport": {"method": "webhook", "callback": f"{host}/channel.follow", "secret": signing_secret},
    },
    {
        "type": "stream.online",
        "version": "1",
        "condition": {"broadcaster_user_id": channel_id},
        "transport": {"method": "webhook", "callback": f"{host}/stream.online", "secret": signing_secret},
    },
    {
        "type": "stream.offline",
        "version": "1",
        "condition": {"broadcaster_user_id": channel_id},
        "transport": {"method": "webhook", "callback": f"{host}/stream.offline", "secret": signing_secret},
    },
    {
        "type": "channel.raid",
        "version": "1",
        "condition": {"to_broadcaster_user_id": channel_id},
        "transport": {"method": "webhook", "callback": f"{host}/channel.raid", "secret": signing_secret},
    },
    {
        "type": "channel.unban",
        "version": "1",
        "condition": {"broadcaster_user_id": channel_id},
        "transport": {"method": "webhook", "callback": f"{host}/channel.unban", "secret": signing_secret},
    },
    {
        "type": "channel.ban",
        "version": "1",
        "condition": {"broadcaster_user_id": channel_id},
        "transport": {"method": "webhook", "callback": f"{host}/channel.ban", "secret": signing_secret},
    },
]

# Make sure all of the events we are subscribed to, we actually want
for current in current_eventsub["data"]:
    desired_eventsub = False

    if not args.disable:
        for event in events:
            a = event["transport"]["method"] == current["transport"]["method"]
            b = event["transport"]["callback"] == current["transport"]["callback"]
            c = current["status"] == "enabled"
            if (
                event["transport"]["method"] == current["transport"]["method"]
                and event["transport"]["callback"] == current["transport"]["callback"]
                and current["status"] == "enabled"
            ):
                desired_eventsub = True
                break

    if args.check:  # Running python eventsub_manage.py --check
        print(
            f"EventSub: {current['type']} for {current['condition']} at {current['transport']['callback']}, Status: {current['status']}"  # noqa E501
        )
    elif not desired_eventsub:
        r = delete_url(f"{url}?id={current['id']}")
        print(f"Deleting {current['type']} for {current['condition']} at {current['transport']['callback']}")
    else:
        print(f"EventSub: {current['type']} for {current['condition']} at {current['transport']['callback']}")

if not args.check:  # Don't do new subscriptions if we're just checking current
    for event in events:
        send_subscribe = True
        for current in current_eventsub["data"]:
            if (
                event["transport"]["method"] == current["transport"]["method"]
                and event["transport"]["callback"] == current["transport"]["callback"]
                and current["status"] == "enabled"
            ):
                send_subscribe = False
                break
        if send_subscribe:
            r = post_url(url, event)
            print(
                f"Subscribed ({r.status_code}): {event['type']} for {event['condition']} at {event['transport']['callback']}"
            )

# Close the database connection
engine.dispose()
