import datetime
import json
import requests
import time

from behave import *

community_name = 'SomeCommunity%d' % int(time.time())
session_name = 'SomeSession%d' % int(time.time())
player_name = 'SomePlayer%d' % int(time.time())

@given(u'the session does not currenty exist in the system')
def step_impl(context):
    # Make sure community exists by trying to create it then fetching it.
    url = 'http://localhost:8080/communities'
    resp = requests.post(url=url,data={'name': community_name, 'policies': 'we-have-them'})
    url = 'http://localhost:8080/%s' % community_name
    resp = requests.get(url=url)
    assert resp.status_code == 200, "want 200 for community; got %d" % resp.status_code
    # Do a GET for /SomeCommunity/sessions/SomeSession and get a 404 (as opposed to no perms - eventaully we'll want auth for this
    # with a public view and a private one?)
    url = 'http://localhost:8080/%s/sessions/%s' % (community_name, session_name)
    resp = requests.get(url=url)
    assert resp.status_code == 404, "want 404; got %d" % resp.status_code


@when(u'we pass in the requisite session data')
def step_impl(context):
    # Do a POST to /SomeCommunity/sessions
    url = 'http://localhost:8080/%s/sessions' % community_name
    resp = requests.post(url=url,data={'name': session_name, 'max_players': 4})
    assert resp.status_code == 200, "want 200; got %d" % resp.status_code


@then(u'a barebones session is created.')
def step_impl(context):
    # Do a GET for /SomeCommunity/sessions/SomeSession and get a 200
    url = 'http://localhost:8080/%s/sessions/%s' % (community_name, session_name)
    resp = requests.get(url=url)
    assert resp.status_code == 200, "want 200; got %d" % resp.status_code


@given(u'the session exists in the system')
def step_impl(context):
    url = 'http://localhost:8080/communities'
    resp = requests.post(url=url,data={'name': community_name, 'policies': 'we-have-them'})
    url = 'http://localhost:8080/%s' % community_name
    resp = requests.get(url=url)
    assert resp.status_code == 200, "want 200 for community; got %d" % resp.status_code
    # Make sure it exists by trying to create it then fetching it.
    url = 'http://localhost:8080/%s/sessions' % community_name
    resp = requests.post(url=url,data={'name': session_name, 'max_players': 4})
    url = 'http://localhost:8080/%s/sessions/%s' % (community_name, session_name)
    resp = requests.get(url=url)
    assert resp.status_code == 200, "want 200; got %d" % resp.status_code


@when(u'we request the session\'s data')
def step_impl(context):
    url = 'http://localhost:8080/%s/sessions/%s' % (community_name, session_name)
    resp = requests.get(url=url)
    assert resp.status_code == 200, "want 200; got %d" % resp.status_code


@then(u'we get the requested session\'s data.')
def step_impl(context):
    url = 'http://localhost:8080/%s/sessions/%s' % (community_name, session_name)
    resp = requests.get(url=url)
    assert resp.status_code == 200, "want 200; got %d" % resp.status_code


@when(u'we pass in the fields to be updated for the session')
def step_impl(context):
    url = 'http://localhost:8080/%s/sessions/%s' % (community_name, session_name)
    resp = requests.put(url=url,data={'max_players': 123})
    assert resp.status_code == 200, "want 200; got %d" % resp.status_code


@then(u'the requested session\'s data is updated accordingly.')
def step_impl(context):
    url = 'http://localhost:8080/%s/sessions/%s' % (community_name, session_name)
    resp = requests.get(url=url)
    assert resp.status_code == 200, "want 200; got %d" % resp.status_code and '123' in resp.text


@when(u'we request the session be deleted from the system')
def step_impl(context):
    url = 'http://localhost:8080/%s/sessions/%s' % (community_name, session_name)
    resp = requests.delete(url=url,data={'name': session_name})
    assert resp.status_code == 200, "want 200; got %d" % resp.status_code


@then(u'the session\'s data is deleted from the system.')
def step_impl(context):
    url = 'http://localhost:8080/%s/sessions/%s' % (community_name, session_name)
    resp = requests.get(url=url)
    assert resp.status_code == 404, "want 404; got %d" % resp.status_code

@given(u'a lottery was scheduled to run before now with {participants} participants, a minimum of {minimum} players, and a maximum of {maximum} players and has not')
def step_impl(context, participants, minimum, maximum):
    url = 'http://localhost:8080/communities'
    resp = requests.post(url=url,data={'name': community_name, 'policies': 'we-have-them'})
    url = 'http://localhost:8080/%s' % community_name
    resp = requests.get(url=url)
    assert resp.status_code == 200, "want 200 for community; got %d" % resp.status_code
    # Create the requisite number of players
    parts = []
    for i in range(0, int(participants)):
        url = 'http://localhost:8080/players'
        new_name = player_name+str(i)
        resp = requests.post(url=url,data={'name': new_name})
        url = 'http://localhost:8080/players/%s' % new_name
        resp = requests.get(url=url)
        assert resp.status_code == 200, "want 200; got %d" % resp.status_code
        parts.append(new_name)
    # Make sure it exists by trying to create it then fetching it.
    url = 'http://localhost:8080/%s/sessions' % community_name
    resp = requests.post(
            url=url,
            data={'name': session_name,
                  'max_players': maximum,
                  'min_players': minimum,
                  'lottery_participants': json.dumps(parts),
                  'lottery_scheduled_for': datetime.datetime.utcnow() - datetime.timedelta(minutes=15)
                 }
    )
    assert resp.status_code == 200, "want 200; got %d" % resp.status_code

@when(u'we run the lottery')
def step_impl(context):
    url = 'http://localhost:8080/%s/lotteries' % community_name
    resp = requests.get(url=url)
    assert resp.status_code == 200, "want 200; got %d" % resp.status_code


@then(u'there are {players} players in the session')
def step_impl(context, players):
    raise NotImplementedError(u'STEP: Then there are 4 players in the session')


@then(u'there are {players} players on the session\'s waitlist')
def step_impl(context, players):
    raise NotImplementedError(u'STEP: Then there are 3 players on the session\'s waitlist')
