import datetime
import logging
import json
import pprint
import random

import flask
from pony import orm

import refuge_types


PROTECTED_CREATION_ATTRIBUTES = [
    'id', 'created', 'updated',
    'lottery_scheduled_for', 'lottery_occurred_at'
]

# TODO(shanel): We'll want to make sure Create/Update/Delete (ie not GET methods)
# can only be called by the binary itself.


# TODO(shanel): Need to handle initial players - which must update
# those players with the fact that they are in a new game.
@orm.db_session
def new(communityname):
    if flask.request.method == 'POST':
        sessionname = flask.request.form.get('name')
        if sessionname is None:
            return 'session or community name field missing', 400, {
                'Content-Type': 'text/plain; charset=utf-8'
            }
            community_key = ndb.Key('Community', communityname)
        results = orm.select(c for c in refuge_types.Community if c.name == communityname)[:]
        if results:
            # Names should be unique.
            community = results[0]
            # This feels inefficient...
            if sessionname not in (s.name for s in community.sessions):
                params = {
                    k: v
                    for k, v in flask.request.form.items()
                    if v and k not in PROTECTED_CREATION_ATTRIBUTES
                }
                # Things we can't just dump right in or want to disallow
                params['name'] = sessionname
                if 'lottery_scheduled_for' in flask.request.form:
                    params['lottery_scheduled_for'] = datetime.datetime.strptime(
                        # '2019-08-10 21:04:01.217037'
                        flask.request.form['lottery_scheduled_for'],
                        '%Y-%m-%d %H:%M:%S.%f')
                params['community'] = community
                params['created'] = datetime.datetime.utcnow()
                params['updated'] = datetime.datetime.utcnow()
                refuge_types.Session(**params)
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
@orm.db_session
def show_or_update_or_delete(communityname, sessionname):
    results = orm.select(c for c in refuge_types.Community if c.name == communityname)[:]
    if results:
        # Names should be unique.
        community = results[0]
        # This feels inefficient...
        sessions = [s for s in community.sessions if s.name == sessionname]
        if sessions:
            session = sessions[0]

            # TODO(shanel): We'll need to limit this to the creator only. (Or maybe community
            # owner.)
            # TODO(shanel): This will need to also remove the data from the players too.
            if flask.request.method == 'DELETE':
                session.delete()
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
                    for k, v in flask.request.form.items():
                        if k in ('id', 'created', 'updated'):
                            continue
                        if getattr(session, k, None) is not None:
                            setattr(session, k, v)
            # This should be removed once we are even remotely live.
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

@orm.db_session
def run_a_lottery(communityname, session):
    lottery_id = communityname + '|' + session.name
    participant_ids = json.loads(session.lottery_participants)
    participants = list(orm.select(p for p in refuge_types.Player if p.name in participant_ids))
    winner_ids = []
    waitlist_ids = []
    original_participants = participants[:]
    for _ in range(0, int(session.max_players)):
        winner = run_a_single_lottery_draw(participants)
        if winner:
            # Assuming this isn't removing the players from db?
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

@orm.db_session
def run_lotteries():
    """Will run all the lotteries that need to be run.
    """
    # Get all sessions which have unrun lotteries with lotteries scheduled for before now.

    results = orm.select(s for s in refuge_types.Session if s.lottery_scheduled_for != None)
    results = orm.select(s for s in results if s.lottery_scheduled_for <= datetime.datetime.utcnow())
    sessions_with_unrun_lotteries = orm.select(s for s in results if s.lottery_occurred_at == None)[:]
    for s in sessions_with_unrun_lotteries:
        winner_ids, waitlist_ids = run_a_lottery(s.community.name, s)
        players = []
        if s.players:
            players = json.loads(s.players)
        players.extend(winner_ids)
        s.players = json.dumps(players)
        s.waitlisted_players = json.dumps(waitlist_ids)
        s.lottery_occurred_at = datetime.datetime.utcnow()
        s.community.last_lottery_run_at = datetime.datetime.utcnow()
    return '{} lotteries run'.format(
        len(sessions_with_unrun_lotteries)), 200, {
            'Content-Type': 'text/plain; charset=utf-8'
        }

def update_promoted_players_waitlist_data(promoted_player, communityname,
                                          sessionname):
    if promoted_player.sessions_waitlisted_for:
        wf = json.loads(
            promoted_player.sessions_waitlisted_for)
        if communityname + '|' + sessionname in wf:
            wf.remove(communityname + '|' + sessionname)
        promoted_player.sessions_waitlisted_for = json.dumps(wf)
    if promoted_player.sessions_via_waitlist:
        vw = json.loads(
            promoted_player.sessions_via_waitlist)
        vw[communityname + '|' + sessionname] = str(
            datetime.datetime.utcnow())
        promoted_player.sessions_via_waitlist = json.dumps(vw)
    # for testing
    orm.commit()
    return promoted_player

def update_session_move_data(session, waitlist, promoted_player, promoted, players):
    # update the session's moves_from_waitlist info
    moves = {}
    if session.moves_from_waitlist:
        moves = json.loads(session.moves_from_waitlist)
    moves[promoted_player.name] = str(
        datetime.datetime.utcnow())
    players.append(promoted)
    session.waitlisted_players = json.dumps([p.name for p in waitlist])
    session.moves_from_waitlist = json.dumps(moves)
    return session, players


def update_session_drop_data(session, playername):
    drops = {}
    if session.drops:
        drops = json.loads(session.drops)
    drops[playername] = str(datetime.datetime.utcnow())
    session.drops = json.dumps(drops)
    return session


def update_player_drop_data(player, communityname, sessionname):
    player_drops = {}
    if player.sessions_dropped:
        player_drops = json.loads(player.sessions_dropped)
    player_drops[communityname + '|' + sessionname] = str(
        datetime.datetime.utcnow())
    player.sessions_dropped = json.dumps(player_drops)
    return player


@orm.db_session
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

    player_results = orm.select(p for p in refuge_types.Player if p.name == playername)[:]
    if player_results:
        # Names should be unique.
        player = player_results[0]
    else:
        raise ValueError("%s does not exists in the player db" %
                         playername)
    results = orm.select(c for c in refuge_types.Community if c.name == communityname)[:]
    if results:
        # Names should be unique.
        community = results[0]
        # This feels inefficient...
        sessions = [s for s in community.sessions if s.name == sessionname]
        if sessions:
            session = sessions[0]
            # make sure the player is currently in the session
            waitlist = []
            if session.waitlisted_players:
                waitlist = list(orm.select(p for p in refuge_types.Player if p.name in json.loads(session.waitlisted_players)))
            players = []
            if session.players:
                players = list(orm.select(p for p in refuge_types.Player if p.name in json.loads(session.players)))
            try:
                for p in players:
                    if p.name == playername:
                        players.remove(p)
                        break
#                players.remove(playername)
                # update the player's drop info
                player = update_player_drop_data(player, communityname, sessionname)
                # update session's drops info
                session = update_session_drop_data(session, playername)
                # move the person at the head of the waitlist into the session
                if waitlist:
                    promoted = waitlist.pop(0)
#                    promoted_key = ndb.Key('Player', promoted)
#                    promoted_player = promoted_key.get()
                    promoted_player = waitlist.pop(0)
                    if promoted_player:
                        # update the promoted player's waitlist move info
                        promoted_player = update_promoted_players_waitlist_data(
                                promoted_player, communityname, sessionname)
                        promoted_player.flush()
#                        promoted_player.put()
                        # update the session's moves_from_waitlist info
                        session, players = update_session_move_data(
                                session, waitlist, promoted_player, promoted,
                                players)
                session.players = json.dumps([p.name for p in players])
#                session.put()
                session.flush()
                orm.commit()
            except ValueError:
                logging.exception("first value error")
                try:
                    for p in waitlist:
                        if p.name == playername:
                            waitlist.remove(p)
                            break
#                    waitlist.remove(playername)
                    wf = json.loads(player.sessions_waitlisted_for)
                    if communityname + '|' + sessionname in wf:
                        wf.remove(communityname + '|' + sessionname)
                    player.sessions_waitlisted_for = json.dumps(wf)
                    session.waitlisted_players = json.dumps([p.name for p in waitlist])
                    session.flush()
                    player.flush()
#                    session.put()
#                    player.put()
                    orm.commit()
                except ValueError:
                    logging.exception("%s not in session %v" %
                                     (playername, sessionname))
                    raise ValueError("%s not in session %v" %
                                     (playername, sessionname))
        else:
            logging.exception("session %s does not exist" % sessionname)
            raise ValueError("session %s does not exist" % sessionname)

def _add_player_to_session(player, session, communityname, sessionname, playername):

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

    return player, session

@orm.db_session
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
    player_results = orm.select(p for p in refuge_types.Player if p.name == playername)[:]
    if player_results:
        # Names should be unique.
        player = player_results[0]
    else:
        raise ValueError("%s does not exists in the player db" %
                         playername)
    results = orm.select(c for c in refuge_types.Community if c.name == communityname)[:]
    if results:
        # Names should be unique.
        community = results[0]
        # This feels inefficient...
        sessions = [s for s in community.sessions if s.name == sessionname]
        if sessions:
            session = sessions[0]
            player, session = _add_player_to_session(player, session, communityname, sessionname, playername)
        else:
            raise ValueError("session %s does not exist" % sessionname)
