import datetime
import json
import pprint
import random

import flask
from google.cloud import ndb

# TODO(shanel): We'll want to make sure Create/Update/Delete (ie not GET methods)
# can only be called by the binary itself.


class Session(ndb.Model):
    name = ndb.StringProperty()
    # TODO(shanel): In theory this should be an int but all the data comes
    # in from the post as a string... Later we can do the needful and make
    # specific things into ints before sticking them into the datastore.
    max_players = ndb.StringProperty()
    min_players = ndb.StringProperty()
    # list of people signed up for lottery
    lottery_participants = ndb.JsonProperty()
    # when the lottery should happen
    lottery_scheduled_for = ndb.DateTimeProperty()
    # when lottery happened
    lottery_occurred_at = ndb.DateTimeProperty()
    # datetime of the session
    starts_at = ndb.DateTimeProperty()
    # list of people in the session
    players = ndb.JsonProperty()
    # list of people on the waitlist
    waitlisted_players = ndb.JsonProperty()
    created_by = ndb.StringProperty()
    other_sessions_in_series = ndb.JsonProperty()
    give_preference_to_those_who_can_attend_most_sessions = ndb.BooleanProperty(
    )
    created = ndb.DateTimeProperty(auto_now_add=True)
    updated = ndb.DateTimeProperty(auto_now=True)
    # These two I see as a dict of user id to timestamp
    drops = ndb.JsonProperty()
    moves_from_waitlist = ndb.JsonProperty()

    # How to handle series and the neccesary lottery tweaks?


# TODO(shanel): Need to handle inital players - which must update
# those players with the fact that they are in a new game.
def new(communityname):
    if flask.request.method == 'POST':
        sessionname = flask.request.form.get('name')
        if sessionname is None:
            return 'session or community name field missing', 400, {
                'Content-Type': 'text/plain; charset=utf-8'
            }
        client = ndb.Client()
        with client.context() as context:
            community_key = ndb.Key('Community', communityname)
            if community_key.get():
                key = ndb.Key('Community', communityname, 'Session',
                              sessionname)
                if not key.get():
                    special = [
                        'id', 'created', 'updated',
                        'lottery_scheduled_for', 'lottery_occurred_at'
                    ]
                    params = {
                        k: v
                        for k, v in flask.request.form.items()
                        if v and k not in special
                    }
                    # Things we can't just dump right in or want to disallow
                    params['id'] = sessionname
                    new_session = Session(parent=community_key, **params)
                    if 'lottery_scheduled_for' in flask.request.form:
                        new_session.lottery_scheduled_for = datetime.datetime.strptime(
                            # '2019-08-10 21:04:01.217037'
                            flask.request.form['lottery_scheduled_for'],
                            '%Y-%m-%d %H:%M:%S.%f')
                    key = new_session.put()
            else:
                return 'could not find community {}'.format(
                    communityname), 404, {
                        'Content-Type': 'text/plain; charset=utf-8'
                    }

        # It might be a pre-optimization, but ideally we'd just use the object
        # to create the page and not do another lookup (lookups cost $)
        #
        # Also, if we try to do a create and a user with that name already
        # exists (eventually) we'll want to return an error, not the data.
        return flask.redirect(
            flask.url_for('session.show_or_update_or_delete',
                          communityname=communityname,
                          sessionname=sessionname))
    if flask.request.method == 'GET':
        return 'CALENDAR GOES HERE', 200, {
            'Content-Type': 'text/plain; charset=utf-8'
        }


# TODO(shanel): We'll need to add to this as things become necessary to test for
def session_to_dict(session):
    out = {
        'name': session.name,
        'players': [],
        'waitlisted_players': [],
        'lottery_participants': [],
        'max_players': session.max_players
    }
    if session.players:
        out['players'] = json.loads(session.players)
    if session.waitlisted_players:
        out['waitlisted_players'] = json.loads(session.waitlisted_players)
    if session.lottery_participants:
        out['lottery_participants'] = json.loads(session.lottery_participants)
    return out


# TODO(shanel): This should be broken up into some helper methods - I worry it
# might end up getting complicated and lead to missing things.
def show_or_update_or_delete(communityname, sessionname):
    # Assume GOOGLE_APPLICATION_CREDENTIALS is set in environment
    client = ndb.Client()

    with client.context() as context:
        key = ndb.Key('Community', communityname, 'Session', sessionname)
        session = key.get()
        if session:
            # TODO(shanel): We'll need to limit this to the creator only. (Or maybe community
            # owner.)
            # TODO(shanel): This will need to also remove the data from the players too.
            if flask.request.method == 'DELETE':
                session.key.delete()
                return flask.redirect(
                    flask.url_for('session.new', communityname=communityname))
            if flask.request.method == 'PUT':
                if 'drop' in flask.request.args:
                    try:
                        drop_player_from_session(flask.request.form['caller'],
                                                 communityname, sessionname)
                    except ValueError as e:
                        return (
                            'problem encountered with request: {}'.format(e),
                            400, {
                                'Content-Type': 'text/plain; charset=utf-8'
                            })
                elif 'add' in flask.request.args:
                    try:
                        add_player_to_session(flask.request.form['caller'],
                                              communityname, sessionname)
                    except ValueError as e:
                        return (
                            'problem encountered with request: {}'.format(e),
                            400, {
                                'Content-Type': 'text/plain; charset=utf-8'
                            })
                else:
                    # NOTE: This makes the assumption that the form will be filled with
                    # all the current data plus any changes.
                    altered = False
                    for k, v in flask.request.form.items():
                        if k == 'id':
                            continue
                        if getattr(session, k, None) is not None:
                            altered = True
                            setattr(session, k, v)
                    if altered:
                        session.put()
            session = key.get()
            out = pprint.PrettyPrinter(indent=4).pformat(session)
            if 'json' in flask.request.args:
                out = json.dumps(session_to_dict(session))
            return out, 200, {'Content-Type': 'text/plain; charset=utf-8'}

        return 'no session with name {} found in community {}'.format(
            sessionname, communityname), 404, {
                'Content-Type': 'text/plain; charset=utf-8'
            }


def run_a_single_lottery_draw(participants):
    participant_ratings = {}
    for participant in participants:
        participant_ratings[participant.name] = participant.get_rank()

    sorted_participant_ids = sorted(participant_ratings.items(),
                                    key=lambda kv: (kv[1], kv[0]))
    sorted_participants = []
    for item in sorted_participant_ids:
        for part in participants:
            if item[0] == part.name:
                sorted_participants.append((part, item[1]))
                break
    to_return = []
    if not sorted_participants:
        return None
    check_for = sorted_participants[0][1]
    for h in sorted_participants:
        if check_for == h[1]:
            to_return.append(h)
    if len(to_return) == 1:
        return to_return[0][0]
    return random.choice(to_return)[0]


def run_a_lottery(communityname, session):
    lottery_id = communityname + '|' + session.name
    participant_ids = json.loads(session.lottery_participants)
    participant_keys = [ndb.Key('Player', sid) for sid in participant_ids]
    participants = ndb.get_multi(participant_keys)
    winner_ids = []
    waitlist_ids = []
    original_participants = participants[:]
    for _ in range(0, int(session.max_players)):
        winner = run_a_single_lottery_draw(participants)
        if winner:
            participants.remove(winner)
            winner_ids.append(winner.name)
    for _ in range(0, len(original_participants) - int(session.max_players)):
        insertee = run_a_single_lottery_draw(participants)
        if insertee:
            participants.remove(insertee)
            waitlist_ids.append(insertee.name)
    for winner in winner_ids:
        for p in original_participants:
            if winner == p.name:
                p.win_lottery(lottery_id)
                # TODO(shanel): This needs to setup the players entries in the session
    for waiter in waitlist_ids:
        for p in original_participants:
            if waiter == p.name:
                p.join_waitlist(lottery_id)
    # TODO(shanel): Need to create the waitlist
    for h in original_participants:
        p.enter_lottery(lottery_id)
        h.exit_lottery()
    return winner_ids, waitlist_ids


# TODO(shanel): This REALLY should just be *all* lotteries - otherwise we need
# to know every single community and call /lotteries for each one.
def run_lotteries(communityname):
    """Will run all the lotteries that need to be run.

      Args:
        communityname: the name of the community sessions are being checked for.
    """
    # Get all sessions which have unrun lotteries with lotteries scheduled for before now.
    client = ndb.Client()
    with client.context() as context:
        community_key = ndb.Key('Community', communityname)
        sessions_with_unrun_lotteries = Session.query(
            Session.lottery_scheduled_for != None,
            Session.lottery_scheduled_for <= datetime.datetime.utcnow(),
            Session.lottery_occurred_at == None,
            ancestor=community_key).fetch()
        for s in sessions_with_unrun_lotteries:
            winner_ids, waitlist_ids = run_a_lottery(communityname, s)
            #sk = ndb.Key('Community', communityname, 'Session', s.name)
            #s = sk.get()
            players = []
            if s.players:
                players = json.loads(s.players)
            players.extend(winner_ids)
            s.players = json.dumps(players)
            s.waitlisted_players = json.dumps(waitlist_ids)
            s.lottery_occurred_at = datetime.datetime.utcnow()
            s.put()
    return '{} lotteries run'.format(
        len(sessions_with_unrun_lotteries)), 200, {
            'Content-Type': 'text/plain; charset=utf-8'
        }


def drop_player_from_session(playername, communityname, sessionname):
    """Drop a user from a session and perform all other necessary changes.

    Args:
      playername: the caller's username (the player who will be dropped)
      communityname: the name of the community the session exists in.
      sessionname: the name of the session the player is being dropped from.

    Raises:
      ValueError: if any of the args don't exist or the callername and the
        playername do not match.
    """
    # TODO(shanel): Eventually there needs to be an actual auth check on the caller.
    # Make sure the session exists
    client = ndb.Client()
    with client.context() as context:
        # make sure the player exists
        player_key = ndb.Key('Player', playername)
        player = player_key.get()
        if not player:
            raise ValueError("%s does not exists in the player db" %
                             playername)
        key = ndb.Key('Community', communityname, 'Session', sessionname)
        session = key.get()
        if session:
            # make sure the player is currently in the session
            waitlist = []
            if session.waitlisted_players:
                waitlist = json.loads(session.waitlisted_players)
            players = []
            if session.players:
                players = json.loads(session.players)
            if playername in players:
                # remove the player from the session
                players.remove(playername)
                # update the player's drop info
                player_drops = {}
                if player.sessions_dropped:
                    player_drops = json.loads(player.sessions_dropped)
                player_drops[communityname + '|' + sessionname] = str(
                    datetime.datetime.utcnow())
                player.sessions_dropped = json.dumps(player_drops)
                player.put()
                # update session's drops info
                drops = {}
                if session.drops:
                    drops = json.loads(session.drops)
                drops[playername] = str(datetime.datetime.utcnow())
                session.drops = json.dumps(drops)
                # move the person at the head of the waitlist into the session
                if waitlist:
                    promoted = waitlist.pop(0)
                    promoted_key = ndb.Key('Player', promoted)
                    promoted_player = promoted_key.get()
                    if promoted_player:
                        # update the promoted player's waitlist move info
                        if promoted_player.sessions_waitlisted_for:
                            wf = json.loads(
                                promoted_player.sessions_waitlisted_for)
                            if communityname + '|' + sessionname in wf:
                                wf.remove(communityname + '|' + sessionname)
                            promoted_player.sessions_waitlisted_for = json.dumps(
                                wf)
                        if promoted_player.sessions_via_waitlist:
                            vw = json.loads(
                                promoted_player.sessions_via_waitlist)
                            vw[communityname + '|' + sessionname] = str(
                                datetime.datetime.utcnow())
                            promoted_player.sessions_via_waitlist = json.dumps(
                                vw)
                        promoted_player.put()
                        session.waitlisted_players = json.dumps(waitlist)
                        # update the session's moves_from_waitlist info
                        moves = {}
                        if session.moves_from_waitlist:
                            moves = json.loads(session.moves_from_waitlist)
                        moves[promoted_player.name] = str(
                            datetime.datetime.utcnow())
                        players.append(promoted)
                        session.waitlisted_players = json.dumps(waitlist)
                session.players = json.dumps(players)
                session.put()
            elif playername in waitlist:
                waitlist.remove(playername)
                wf = json.loads(player.sessions_waitlisted_for)
                if communityname + '|' + sessionname in wf:
                    wf.remove(communityname + '|' + sessionname)
                player.sessions_waitlisted_for = json.dumps(wf)
                session.waitlisted_players = json.dumps(waitlist)
                session.put()
                player.put()
            else:
                raise ValueError("%s not in session %v" %
                                 (playername, sessionname))
        else:
            raise ValueError("session %s does not exist" % sessionname)


def add_player_to_session(playername, communityname, sessionname):
    """Add a user to a session and perform all other necessary changes.

    Args:
      playername: the caller's username (the player who will be added)
      communityname: the name of the community the session exists in.
      sessionname: the name of the session the player is being added to.

    Raises:
      ValueError: if any of the args don't exist or the callername and the
        playername do not match.
    """
    # TODO(shanel): Eventually there needs to be an actual auth check on the caller.
    # Make sure the session exists
    client = ndb.Client()
    with client.context() as context:
        # make sure the player exists
        player_key = ndb.Key('Player', playername)
        player = player_key.get()
        if not player:
            raise ValueError("%s does not exists in the player db" %
                             playername)
        key = ndb.Key('Community', communityname, 'Session', sessionname)
        session = key.get()
        if session:
            # Check to see if the lottery has happened yet. If not, add the player
            # as a participant.
            # If the lottery has happened check if there is space in players. If
            if session.lottery_occurred_at:
                players = []
                if session.players:
                    players = json.loads(session.players)
                if len(players) < int(session.max_players):
                    players.append(playername)
                    session.players = json.dumps(players)
                else:
                    waitlist = []
                    if session.waitlisted_players:
                        waitlist = json.loads(session.waitlisted_players)
                    waitlist.append(playername)
                    session.waitlisted_players = json.dumps(waitlist)
                    wf = []
                    if player.sessions_waitlisted_for:
                        wf = json.loads(player.sessions_waitlisted_for)
                    wf.append(communityname + '|' + sessionname)
                    player.sessions_waitlisted_for = json.dumps(wf)
                    player.put()
                session.put()
            else:
                participants = []
                if session.lottery_participants:
                    participants = json.loads(session.lottery_participants)
                participants.append(playername)
                session.lottery_participants = json.dumps(participants)
                lotteries_signed_up_for = []
                if player.lotteries_signed_up_for:
                    lotteries_signed_up_for = json.loads(
                        player.lotteries_signed_up_for)
                lotteries_signed_up_for.append(communityname + '|' +
                                               sessionname)
                player.lotteries_signed_up_for = json.dumps(
                    lotteries_signed_up_for)
                player.put()
                session.put()
            out = key.get()
            print(out)
        else:
            raise ValueError("session %s does not exist" % sessionname)
