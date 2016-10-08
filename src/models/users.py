"""Class definition of a slack user / poolbot player instance.."""

class User(object):
    """Represents a slack user / poolbot player."""

    USER_ATTRS = (
        'slack_id',
        'name',
        'is_bot',
        'joined',
    )
    PLAYER_ATTRS = (
        'age',
        'active',
        'nickname',
        'country',

        'total_elo',
        'total_win_count',
        'total_loss_count',
        'total_match_count',
        'total_grannies_given_count',
        'total_grannies_taken_count',

        'season_elo',
        'season_win_count',
        'season_loss_count',
        'season_match_count',
        'season_grannies_given_count',
        'season_grannies_taken_count',
    )


    def __init__(self, **kwargs):
        # Using **kwargs for the constructor when we have required fields
        # is a bit strange, but it allows us to convienitently pass a
        # dictionary of key/value pairs taken from the slack / poolbot server
        # inside the poolbot store_users() method
        for required_attr in self.USER_ATTRS + self.PLAYER_ATTRS:
            try:
                setattr(self, required_attr, kwargs[required_attr])
            except KeyError:
                raise TypeError(
                    '{} must be passed as a kwarg to __init_().'.format(required_attr)
                )

    def __str__(self):
        return self.username

    @property
    def username(self):
        return self.name.title()

    def update_from_dict(self, data):
        for attr, value in data.iteritems():
            setattr(self, attr, value)

    @property
    def included_in_leaderboard(self, season=True):
        """Determine if the user should be included in the leaderboard."""
        match_count_field = 'season_match_count' if season else 'total_match_count'
        return self.active and getattr(self, match_count_field)
