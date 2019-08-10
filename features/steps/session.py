import requests
import time

from behave import *

community_name = 'SomeCommunity%d' % int(time.time())
session_name = 'SomeSession%d' % int(time.time())

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

@given(u'the lottery has not run yet')
def step_impl(context):
    raise NotImplementedError(u'STEP: Given the lottery has not run yet')


@given(u'the lottery was scheduled for 15 minutes ago')
def step_impl(context):
    raise NotImplementedError(u'STEP: Given the lottery was scheduled for 15 minutes ago')


@given(u'there are {num} participants in the lottery')
def step_impl(context, num):
    raise NotImplementedError(u'STEP: Given there are 7 participants in the lottery')


@given(u'there is a minimum of {minimum} players')
def step_impl(context, minimum):
    raise NotImplementedError(u'STEP: Given there is a minimum of 2 players')


@given(u'there is a maximum of {maximum} players')
def step_impl(context, maximum):
    raise NotImplementedError(u'STEP: Given there is a maximum of 4 players')


@when(u'we run the lottery')
def step_impl(context):
    raise NotImplementedError(u'STEP: When we run the lottery')


@then(u'there are {players} players in the session')
def step_impl(context, players):
    raise NotImplementedError(u'STEP: Then there are 4 players in the session')


@then(u'there are {players} players on the session\'s waitlist')
def step_impl(context, players):
    raise NotImplementedError(u'STEP: Then there are 3 players on the session\'s waitlist')
