
- [Bot](#bot)
  - [`!announce` - Announcements](#announce---announcements)
    - [`nosleep` - Disables automatic sleep](#nosleep---disables-automatic-sleep)
    - [`start` - Re-enables announcements after being disabled](#start---re-enables-announcements-after-being-disabled)
    - [`stop` - Disables announcements completely](#stop---disables-announcements-completely)
    - [`time` - Sets the frequency of Announcements](#time---sets-the-frequency-of-announcements)
    - [`list` - Lists all of the commands to the console](#list---lists-all-of-the-commands-to-the-console)
    - [`del` - Deletes an announcement by ID.](#del---deletes-an-announcement-by-id)
    - [`add` - Adds a new announcement to Default category](#add---adds-a-new-announcement-to-default-category)
    - [`enable` - Enables an announcement by ID](#enable---enables-an-announcement-by-id)
    - [`disable` - Disables an announcement by ID](#disable---disables-an-announcement-by-id)
    - [`status` - Displays status in chat](#status---displays-status-in-chat)
    - [`category` - Base command](#category---base-command)
      - [`add` - Add a new category](#add---add-a-new-category)
      - [`del` - Deletes a category by ID](#del---deletes-a-category-by-id)
      - [`list` - Lists the available categories to the console](#list---lists-the-available-categories-to-the-console)
      - [`assign` - Assign an announcement to a category](#assign---assign-an-announcement-to-a-category)
      - [`activate` - Sets a category as active](#activate---sets-a-category-as-active)
  - [`!channelpoint_cooldown` - Base command](#channelpoint_cooldown---base-command)
    - [`attention` - Sets Attention cooldown](#attention---sets-attention-cooldown)
    - [`treat` - Sets Treat cooldown](#treat---sets-treat-cooldown)
  - [`!disable_attn` - Disable Attention](#disable_attn---disable-attention)
  - [`!treatme` - Sends a Treat](#treatme---sends-a-treat)
  - [`!topic` - Chat Topic](#topic---chat-topic)
    - [`!topic set` - Sets a topic](#topic-set---sets-a-topic)
- [Web](#web)
  - [`/send_command`](#send_command)
    - [`POST` - Send a command to the bot](#post---send-a-command-to-the-bot)
  - [`/topic`](#topic)
    - [`GET` - Show chat topic](#get---show-chat-topic)
    - [`POST` - Set chat topic](#post---set-chat-topic)
- [MQTT](#mqtt)

# Bot
## `!announce` - Announcements
Permissions: Admin (for all sub commands)

Base command, doesn't do anything directly
### `nosleep` - Disables automatic sleep
### `start` - Re-enables announcements after being disabled
This is saved in the database and will survive restarts.
### `stop` - Disables announcements completely
This is saved in the database and will survive restarts.

### `time` - Sets the frequency of Announcements
Send the time in seconds as a parameter for frequency of announcements.

### `list` - Lists all of the commands to the console
### `del` - Deletes an announcement by ID.
Send the ID as a parameter.
If message is the last in the active category, resets active category to Default

### `add` - Adds a new announcement to Default category
Send the Announcement you want to add as the parameter

### `enable` - Enables an announcement by ID
Send the ID to be enabled as the parameter

### `disable` - Disables an announcement by ID
Send the ID to be disable as the parameter

### `status` - Displays status in chat
### `category` - Base command
Doesn't do anything directly
#### `add` - Add a new category
Send name of new category as paremeter

#### `del` - Deletes a category by ID
Send ID as parameter to delete category.
Must not have any announcements assigned
Can not delete Default

#### `list` - Lists the available categories to the console
#### `assign` - Assign an announcement to a category
Send {AnnouncementID:int} {CategoryID:int} as parameters

#### `activate` - Sets a category as active
Sets the {CategoryID:int} as the active category.

## `!channelpoint_cooldown` - Base command
Permission: Admin
For setting channelpoint cooldowns
### `attention` - Sets Attention cooldown
Permission: Admin
Send new cooldown in seconds as parameter

### `treat` - Sets Treat cooldown
Permission: Admin
Send new cooldown in seconds as parameter

## `!disable_attn` - Disable Attention
Permissions: Admin
Disables sending the MQTT publish to twitch-attn-indi
## `!treatme` - Sends a Treat
Permissions: Everyone
Sends a MQTT publish of 1 to dispense-treat-toggle
## `!topic` - Chat Topic
Permissions: Everyone
Posts to chat the currently set topic
### `!topic set` - Sets a topic
Permissions: Admin
- `!topic set New topic text`


# Web
## `/send_command`
### `POST` - Send a command to the bot
Requires
- `access_token` header
- JSON object as the data with:
  - command: The command to send
  - args: Arguments to pass to the command, include subcommands here. Must be a LIST ex: `[arg1, arg2, arg3]`

Example with curl:
> `curl --header "Content-Type: application/json" --header "access_token: testKey" --request POST --data '{"command":"!topic", "args":["set", "New", "topic"], "silent":false}' http://localhost:5000/send_command`

## `/topic`
### `GET` - Show chat topic
Returns the current Bot topic as a json object of `{"topic":"Topic text"}`

### `POST` - Set chat topic
Requires
- `access_token` header
- JSON object as the data with `topic` as the only needed key, and text as the value.
    > `{"topic":"Topic text"}`


Example with curl:

> `curl --header "Content-Type: application/json" --header "access_token: testKey" --request POST --data '{"topic":"Test topic sent from a json post"}' http://{WEB_HOSTNAME}/topic`

# MQTT
- `dispense-treat-toggle` Sending 1 triggers the treat bot. Bot should reset to 0 when done.
- `twitch-attn-indi`  Sending 1 triggers the Attention bot. Bot should reset to 0 when done.
-
