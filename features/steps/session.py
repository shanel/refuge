import datetime
import json
import requests
import time

from behave import *

community_name = 'SomeCommunity%f' % time.time()
session_name = 'SomeSession%f' % time.time()
player_name = 'SomePlayer%f' % time.time()


def set_names():
    """Sets all the global names (call in first 'given')."""
    global community_name
    global session_name
    global player_name
    community_name = 'SomeCommunity%f' % time.time()
    session_name = 'SomeSession%f' % time.time()
    player_name = 'SomePlayer%f' % time.time()


@given(u'the session does not currenty exist in the system')
def step_impl(context):
    set_names()
    # Make sure community exists by trying to create it then fetching it.
    url = 'http://localhost:8080/communities'
    resp = requests.post(url=url,
                         data={
                             'name': community_name,
                             'policies': 'we-have-them'
                         })
    url = 'http://localhost:8080/%s' % community_name
    resp = requests.get(url=url)
    assert resp.status_code == 200, "want 200 for community; got %d" % resp.status_code
    # Do a GET for /SomeCommunity/sessions/SomeSession and get a 404 (as opposed to no perms - eventaully we'll want auth for this
    # with a public view and a private one?)
    url = 'http://localhost:8080/%s/sessions/%s' % (community_name,
                                                    session_name)
    resp = requests.get(url=url)
    assert resp.status_code == 404, "want 404; got %d" % resp.status_code


@when(u'we pass in the requisite session data')
def step_impl(context):
    # Do a POST to /SomeCommunity/sessions
    url = 'http://localhost:8080/%s/sessions' % community_name
    resp = requests.post(url=url,
                         data={
                             'name': session_name,
                             'max_players': 4
                         })
    assert resp.status_code == 200, "want 200; got %d" % resp.status_code


@then(u'a barebones session is created.')
def step_impl(context):
    # Do a GET for /SomeCommunity/sessions/SomeSession and get a 200
    url = 'http://localhost:8080/%s/sessions/%s' % (community_name,
                                                    session_name)
    resp = requests.get(url=url)
    assert resp.status_code == 200, "want 200; got %d" % resp.status_code


@given(u'the session exists in the system')
def step_impl(context):
    set_names()
    url = 'http://localhost:8080/communities'
    resp = requests.post(url=url,
                         data={
                             'name': community_name,
                             'policies': 'we-have-them'
                         })
    url = 'http://localhost:8080/%s' % community_name
    resp = requests.get(url=url)
    assert resp.status_code == 200, "want 200 for community; got %d" % resp.status_code
    # Make sure it exists by trying to create it then fetching it.
    url = 'http://localhost:8080/%s/sessions' % community_name
    resp = requests.post(url=url,
                         data={
                             'name': session_name,
                             'max_players': 4
                         })
    url = 'http://localhost:8080/%s/sessions/%s' % (community_name,
                                                    session_name)
    resp = requests.get(url=url)
    assert resp.status_code == 200, "want 200; got %d" % resp.status_code


@when(u'we request the session\'s data')
def step_impl(context):
    url = 'http://localhost:8080/%s/sessions/%s' % (community_name,
                                                    session_name)
    resp = requests.get(url=url)
    assert resp.status_code == 200, "want 200; got %d" % resp.status_code


@then(u'we get the requested session\'s data.')
def step_impl(context):
    url = 'http://localhost:8080/%s/sessions/%s' % (community_name,
                                                    session_name)
    resp = requests.get(url=url)
    assert resp.status_code == 200, "want 200; got %d" % resp.status_code


@when(u'we pass in the fields to be updated for the session')
def step_impl(context):
    url = 'http://localhost:8080/%s/sessions/%s' % (community_name,
                                                    session_name)
    resp = requests.put(url=url, data={'max_players': 123})
    assert resp.status_code == 200, "want 200; got %d" % resp.status_code


@then(u'the requested session\'s data is updated accordingly.')
def step_impl(context):
    url = 'http://localhost:8080/%s/sessions/%s' % (community_name,
                                                    session_name)
    resp = requests.get(url=url)
    assert resp.status_code == 200, "want 200; got %d" % resp.status_code and '123' in resp.text


@when(u'we request the session be deleted from the system')
def step_impl(context):
    url = 'http://localhost:8080/%s/sessions/%s' % (community_name,
                                                    session_name)
    resp = requests.delete(url=url, data={'name': session_name})
    assert resp.status_code == 200, "want 200; got %d" % resp.status_code


@then(u'the session\'s data is deleted from the system.')
def step_impl(context):
    url = 'http://localhost:8080/%s/sessions/%s' % (community_name,
                                                    session_name)
    resp = requests.get(url=url)
    assert resp.status_code == 404, "want 404; got %d" % resp.status_code


@given(
    u'a lottery was scheduled to run before now with {participants} participants and a maximum of {maximum} players and has not'
)
def step_impl(context, participants, maximum):
    set_names()
    url = 'http://localhost:8080/communities'
    resp = requests.post(url=url,
                         data={
                             'name': community_name,
                             'policies': 'we-have-them'
                         })
    url = 'http://localhost:8080/%s' % community_name
    resp = requests.get(url=url)
    assert resp.status_code == 200, "want 200 for community; got %d" % resp.status_code
    # Create the requisite number of players
    parts = []
    for i in range(0, int(participants)):
        url = 'http://localhost:8080/players'
        new_name = player_name + str(i)
        resp = requests.post(url=url, data={'name': new_name})
        url = 'http://localhost:8080/players/%s' % new_name
        resp = requests.get(url=url)
        assert resp.status_code == 200, "want 200; got %d" % resp.status_code
        parts.append(new_name)
    # Make sure it exists by trying to create it then fetching it.
    url = 'http://localhost:8080/%s/sessions' % community_name
    resp = requests.post(url=url,
                         data={
                             'name':
                             session_name,
                             'max_players':
                             maximum,
                             'lottery_participants':
                             json.dumps(parts),
                             'lottery_scheduled_for':
                             datetime.datetime.utcnow() -
                             datetime.timedelta(minutes=15)
                         })
    assert resp.status_code == 200, "want 200; got %d" % resp.status_code


@when(u'we run the lottery')
def step_impl(context):
    url = 'http://localhost:8080/lotteries'
    resp = requests.get(url=url)
    assert resp.status_code == 200, "want 200; got %d" % resp.status_code


@then(u'there are {players} players in the session')
def step_impl(context, players):
    url = 'http://localhost:8080/%s/sessions/%s?json=true' % (community_name,
                                                              session_name)
    resp = requests.get(url=url)
    assert resp.status_code == 200, "want 200; got %d" % resp.status_code
    resp_json = json.loads(resp.text)
    assert len(resp_json['players']) == int(
        players), "want %d players enrolled; got %d" % (
            int(players), len(resp_json['players']))


@then(u'there are {players} players on the session\'s waitlist')
def step_impl(context, players):
    url = 'http://localhost:8080/%s/sessions/%s?json=true' % (community_name,
                                                              session_name)
    resp = requests.get(url=url)
    assert resp.status_code == 200, "want 200; got %d" % resp.status_code
    resp_json = json.loads(resp.text)
    assert len(resp_json['waitlisted_players']) == int(
        players), "want %d players on the waitlist; got %d" % (
            int(players), len(resp_json['waitlisted_players']))


# Session Drops

original_waitlist = {}


@when(u'a player drops the session')
def step_impl(context):
    # get list of players in the session
    url = 'http://localhost:8080/%s/sessions/%s?json=true' % (community_name,
                                                              session_name)
    resp = requests.get(url=url)
    assert resp.status_code == 200, "want 200; got %d" % resp.status_code
    resp_json = json.loads(resp.text)
    assert len(
        resp_json['players']) > 0, "want > 0 players enrolled; got %d" % (len(
            resp_json['players']))
    global original_waitlist
    original_waitlist = resp_json['waitlisted_players']
    # pick one and send drop request
    dropper = resp_json['players'][0]
    url = 'http://localhost:8080/%s/sessions/%s?drop=true&json=true' % (
        community_name, session_name)
    resp = requests.put(url=url, data={'caller': dropper})
    assert resp.status_code == 200, "want 200; got %d" % resp.status_code
    resp_json = json.loads(resp.text)
    assert dropper not in resp_json['players'], "player %s is in %s" % (
        dropper, resp_json['players'])


@then(u'the first player on the waitlist moves into the session')
def step_impl(context):
    # get list of players in the session
    url = 'http://localhost:8080/%s/sessions/%s?json=true' % (community_name,
                                                              session_name)
    resp = requests.get(url=url)
    assert resp.status_code == 200, "want 200; got %d" % resp.status_code
    resp_json = json.loads(resp.text)
    assert len(
        resp_json['players']) > 0, "want > 0 players enrolled; got %d" % (len(
            resp_json['players']))
    global original_waitlist
    sorted_waitlist_keys = sorted(original_waitlist.keys())
    assert original_waitlist[sorted_waitlist_keys[0]] in resp_json[
        'players'], "player %s not in %s (%s)" % (original_waitlist[sorted_waitlist_keys[0]],
                                             resp_json['players'], sorted_waitlist_keys)


@when(u'a player drops from the waitlist')
def step_impl(context):
    url = 'http://localhost:8080/%s/sessions/%s?json=true' % (community_name,
                                                              session_name)
    resp = requests.get(url=url)
    assert resp.status_code == 200, "want 200; got %d" % resp.status_code
    resp_json = json.loads(resp.text)
    assert len(resp_json['waitlisted_players']
               ) > 0, "want > 0 players waitlisted; got %d" % (len(
                   resp_json['waitlisted_players']))
    global original_waitlist
    original_waitlist = resp_json['waitlisted_players']
    # pick one and send drop request
    players = resp_json['waitlisted_players'].keys()
    for i in players:
        dropper = resp_json['waitlisted_players'][i]
        break
#    dropper = resp_json['waitlisted_players'][players[0]]
    url = 'http://localhost:8080/%s/sessions/%s?drop=true&json=true' % (
        community_name, session_name)
    resp = requests.put(url=url, data={'caller': dropper})
    assert resp.status_code == 200, "want 200; got %d" % resp.status_code
    resp_json = json.loads(resp.text)
    assert dropper not in resp_json[
        'waitlisted_players'].values(), "player %s is in %s" % (
            dropper, resp_json['waitlisted_players'].values())


@given(
    u'a lottery has run before now with {participants} participants and a maximum of {maximum} players'
)
def step_impl(context, participants, maximum):
    set_names()
    url = 'http://localhost:8080/communities'
    resp = requests.post(url=url,
                         data={
                             'name': community_name,
                             'policies': 'we-have-them'
                         })
    url = 'http://localhost:8080/%s' % community_name
    resp = requests.get(url=url)
    assert resp.status_code == 200, "want 200 for community; got %d" % resp.status_code
    # Create the requisite number of players
    parts = []
    for i in range(0, int(participants)):
        url = 'http://localhost:8080/players'
        new_name = player_name + str(i)
        resp = requests.post(url=url, data={'name': new_name})
        url = 'http://localhost:8080/players/%s' % new_name
        resp = requests.get(url=url)
        assert resp.status_code == 200, "want 200; got %d" % resp.status_code
        parts.append(new_name)
    # Make sure it exists by trying to create it then fetching it.
    url = 'http://localhost:8080/%s/sessions' % community_name
    resp = requests.post(url=url,
                         data={
                             'name':
                             session_name,
                             'max_players':
                             maximum,
                             'lottery_participants':
                             json.dumps(parts),
                             'lottery_scheduled_for':
                             datetime.datetime.utcnow() -
                             datetime.timedelta(minutes=15)
                         })
    assert resp.status_code == 200, "want 200; got %d" % resp.status_code
    url = 'http://localhost:8080/lotteries'
    resp = requests.get(url=url)
    assert resp.status_code == 200, "want 200; got %d" % resp.status_code


@when(u'a player signs up')
def step_impl(context):
    # create a new user
    url = 'http://localhost:8080/players'
    new_name = player_name + str(1337)
    resp = requests.post(url=url, data={'name': new_name})
    url = 'http://localhost:8080/players/%s' % new_name
    resp = requests.get(url=url)
    assert resp.status_code == 200, "want 200; got %d" % resp.status_code
    # get list of players in the session
    url = 'http://localhost:8080/%s/sessions/%s?add=true&json=true' % (
        community_name, session_name)
    resp = requests.put(url=url, data={'caller': new_name})
    assert resp.status_code == 200, "want 200; got %d" % resp.status_code
    url = 'http://localhost:8080/%s/sessions/%s?json=true' % (community_name,
                                                              session_name)
    resp = requests.get(url=url)
    assert resp.status_code == 200, "want 200; got %d" % resp.status_code
    resp_json = json.loads(resp.text)


@then(u'there are {new} participants')
def step_impl(context, new):
    url = 'http://localhost:8080/%s/sessions/%s?json=true' % (community_name,
                                                              session_name)
    resp = requests.get(url=url)
    assert resp.status_code == 200, "want 200; got %d" % resp.status_code
    resp_json = json.loads(resp.text)
    assert len(resp_json['lottery_participants']
               ) > 0, "want %s lottery participants; got %d" % (
                   new, len(resp_json['lottery_participants']))
