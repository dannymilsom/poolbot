"""Mock data from the poolbot server player endpoint (`api/player/`)."""

PLAYER_1 = {
    "slack_id": "U1111111111",
    "name": "danny",
    "joined": "2016-04-26T20:05:06.997380Z",
    "age": 25,
    "nickname": "quiet thrust",
    "country": "uk",
    "total_win_count": 10,
    "total_loss_count": 10,
    "total_match_count": 20,
    "total_grannies_given_count": 1,
    "total_grannies_taken_count": 2,
    "elo": 1400,
    "active": True,
}

PLAYER_2 = {
    "slack_id": "U2222222222",
    "name": "toby",
    "joined": "2016-04-26T20:05:07.072295Z",
    "age": 24,
    "nickname": "cambridge pocket square",
    "country": "uk",
    "total_win_count": 5,
    "total_loss_count": 10,
    "total_match_count": 15,
    "total_grannies_given_count": 3,
    "total_grannies_taken_count": 0,
    "elo": 1200,
    "active": True,
}

PLAYER_3 = {
    "slack_id": "U3333333333",
    "name": "simon",
    "joined": "2016-04-29T22:25:20.579144Z",
    "age": 28,
    "nickname": "simon",
    "country": "scotland",
    "total_win_count": 2,
    "total_loss_count": 2,
    "total_match_count": 4,
    "total_grannies_given_count": 0,
    "total_grannies_taken_count": 0,
    "elo": 1100,
    "active": False,
}

PLAYER_4 = {
    "slack_id": "U4444444444",
    "name": "nathanjones",
    "joined": "2016-05-18T21:48:04.617372Z",
    "age": 27,
    "nickname": "joner",
    "country": "weston",
    "total_win_count": 0,
    "total_loss_count": 0,
    "total_match_count": 0,
    "total_grannies_given_count": 0,
    "total_grannies_taken_count": 0,
    "elo": 1000,
    "active": True,
}

PLAYER_LIST_RESP = [PLAYER_1, PLAYER_2, PLAYER_3, PLAYER_4]

PLAYER_DICT = {
    player['slack_id']: player for player in PLAYER_LIST_RESP
}
