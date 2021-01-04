
- [Bot](#bot)
  - [`!topic` - Chat Topic](#topic---chat-topic)
    - [`!topic set` - Sets a topic](#topic-set---sets-a-topic)
- [Web](#web)
  - [`/send_command`](#send_command)
    - [`POST` - Send a command to the bot](#post---send-a-command-to-the-bot)
  - [`/topic`](#topic)
    - [`GET` - Show chat topic](#get---show-chat-topic)
    - [`POST` - Set chat topic](#post---set-chat-topic)

# Bot
## `!topic` - Chat Topic
Posts to chat the currently set topic
### `!topic set` - Sets a topic
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
