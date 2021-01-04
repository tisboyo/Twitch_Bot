
- [Bot](#bot)
  - [`!topic` - Chat Topic](#topic---chat-topic)
    - [`!topic set` - Sets a topic](#topic-set---sets-a-topic)
- [Web](#web)
  - [`/topic` - Show chat topic](#topic---show-chat-topic)
    - [`GET`](#get)
    - [`POST` - Set chat topic](#post---set-chat-topic)

# Bot
## `!topic` - Chat Topic
Posts to chat the currently set topic
### `!topic set` - Sets a topic
- `!topic set New topic text`


# Web
## `/topic` - Show chat topic
### `GET`
Returns the current Bot topic as a json object of `{"topic":"Topic text"}`

### `POST` - Set chat topic
Requires
- `access_token` header
- Json object as the data with `topic` as the only needed key, and text as the value.
    > `{"topic":"Topic text"}`


Example with curl

> `curl --header "Content-Type: application/json" --header "access_token: testKey" --request POST --data '{"topic":"Test topic sent from a json post"}' http://{WEB_HOSTNAME}/topic`
