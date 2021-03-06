from datetime import datetime
import json

from pony import orm

import db
import percentage

class Community(db.refuge_db.Entity):
    name = orm.PrimaryKey(str)
    policies = orm.Optional(str)
    created = orm.Required(datetime)
    updated = orm.Required(datetime)
    last_lottery_run_at = orm.Optional(datetime)
    session_runs_updated_at = orm.Optional(datetime)
    sessions = orm.Set('Session')


class Player(db.refuge_db.Entity, percentage.PlayerMixIn):
    # TODO(shanel): Figure out if name maybe should be something else? (email, etc.)
    name = orm.PrimaryKey(str)
    # ideally screen_name would be per community I assume?
    screen_name = orm.Optional(str)
    pronouns = orm.Optional(str)
    created = orm.Required(datetime)
    updated = orm.Required(datetime)

    # A lot of these could feasibly be figured out via a query and minimize
    # record keeping. Might be a cost ($$$) tradeoff there.
    #
    # lotteries signed up for
    lotteries_signed_up_for = orm.Optional(orm.Json)
    lotteries_participated_in = orm.Optional(orm.Json)
    # lotteries won
    lotteries_won = orm.Optional(orm.Json)
    # games attended
    sessions_played_in = orm.Optional(orm.Json) #  Currently unused
    # games waitlisted for
    sessions_waitlisted_for = orm.Optional(orm.Json)
    # These two I see as a dict of session id to timestamp
    sessions_via_waitlist = orm.Optional(orm.Json)
    sessions_dropped = orm.Optional(orm.Json)

    def join_waitlist(self, lottery_id):
        sessions_waitlisted_for = []
        if self.sessions_waitlisted_for:
            sessions_waitlisted_for = json.loads(self.sessions_waitlisted_for)
        sessions_waitlisted_for.append(lottery_id)
        self.sessions_waitlisted_for = json.dumps(sessions_waitlisted_for)

class Session(db.refuge_db.Entity):
    community = orm.Required(Community)
    # This probably should be a slug?
    # Hmm... So this ideally would be unique to the community it is a part of,
    # but it shouldn't need to be unique across all communities...
    name = orm.Required(str)
    orm.PrimaryKey(community, name)
    # TODO(shanel): In theory this should be an int but all the data comes
    # in from the post as a string... Later we can do the needful and make
    # specific things into ints before sticking them into the datastore.
    max_players = orm.Optional(str)
    min_players = orm.Optional(str)
    # list of people signed up for lottery
    lottery_participants = orm.Optional(orm.Json)
    # when the lottery should happen
    lottery_scheduled_for = orm.Optional(datetime)
    # when lottery happened
    lottery_occurred_at = orm.Optional(datetime)
    # datetime of the session
    # TODO(shanel): Should this be required here? (Or shold we just require it in form?)
    starts_at = orm.Optional(datetime)
    # list of people in the session
    players = orm.Optional(orm.Json)
    # list of people on the waitlist
    waitlisted_players = orm.Optional(orm.Json)
    # TODO(shanel): Should this be a relation?
    # TODO(shanel): Should this be required here? (Or shold we just require it in form?)
    created_by = orm.Optional(str)
    other_sessions_in_series = orm.Optional(orm.Json)
    give_preference_to_those_who_can_attend_most_sessions = orm.Optional(bool)
    created = orm.Required(datetime)
    updated = orm.Required(datetime)
    # These two I see as a dict of user id to timestamp
    drops = orm.Optional(orm.Json)
    moves_from_waitlist = orm.Optional(orm.Json)
    session_started = orm.Optional(bool)
    show_lottery_participants_before_lottery_run = orm.Optional(bool)

    # How to handle series and the neccesary lottery tweaks?

orm.sql_debug(True)
db.refuge_db.generate_mapping(create_tables=True)
