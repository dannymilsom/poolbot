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

All patches to fix bugs and add features are welcome!

To get the development environment up and running follow these steps... TODO

* Create a `config.yaml` in the `src` directory and add all the values listed in `example_config.yaml`. This includes the `SLACK_API_TOKEN`!
TODO

## Wish List

* Leaderboard for a duration (day/week/month/year/alltime)
* Add some tests (need to mock replies form the slack websocket API).
* Give odds on the result of two players playing each other.
* Suggest who to play given on recent form.
* Detect inactive vs active users and recommend a user who might want to play.
* More funny reactions.
* Get started script
* Cron job to celebrate anniversaries of grannies
