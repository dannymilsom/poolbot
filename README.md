# Poolbot

Poolbot is a slack bot designed for connaisseurs of pool. Record results, compare form and generate odds... all from the comfort of the slack command line.

## Commands

Explicitly interacting with poolbot requires the use of commands. To provide a consistent interface, all poolbot commands follow this structure...

```
@poolbot: <command> <@mention> <expression>
```

For example you can record the result of a pool game in a persistent database for later analysis like so:

```
@poolbot: record I just grannied @toby
```

You can read about all of the available command here.

## Reactions

Poolbot will also react to certain messages and events in the slack channel without being prompted or mentioned in the message.

For example when a new user joins a channel with poolbot in, poolbot will welcome the user and add them to the players database table.

You can read about all of the available reactions here.

## Contributioning

To get the development environment up and running follow these steps...

1. To persist data and provide a RESTful(ish) API, clone the [poolbot-server](https://github.com/dannymilsom/poolbot-server) repository.
   This is a django app, so install all the python module dependencies using `virtualenv` and boot the development server via `manage.py runserver`.
2. Add a custom bot integration to your slack team. This process, and more information about bot users in slack, is well described in the [official slack docs](https://api.slack.com/bot-users).
3. Create a `config.yaml` in the `src` directory and add all the values listed in `example_config.yaml`. This includes:
 * `API_TOKEN` which you can find on your slack bots settings page.
 * `BOT_ID` which is the unique ID assigned to your custom bot.
 * `SERVER_HOST` which is probably `http://127.0.0.1:8000/` if you're running the django development server included with [poolbot-server](https://github.com/dannymilsom/poolbot-server).
 * `SERVER_TOKEN` which you need to send in the `Authorization` header of every request to the [poolbot-server](https://github.com/dannymilsom/poolbot-server). These are generated in
   a post save signal for every user, so you just need to look at the `Token` model via django admin and copy the token key.
3. Finally run `python poolbot.py` and all messages sent by the slack RTM API in rooms which your custom bot are in, will be consumed by poolbot.

## Wish List

* Leaderboard for a duration (day/week/month/year/alltime)
* Add some tests (need to mock replies form the slack websocket API).
* Give odds on the result of two players playing each other.
* Suggest who to play given on recent form.
* Detect inactive vs active users and recommend a user who might want to play.
* More funny reactions.
* Get started script
* Cron job to celebrate anniversaries of grannies
