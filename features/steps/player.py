import requests
import time

from behave import *

player_name = 'SomePlayer%d' % int(time.time())

@given(u'the player does not currenty exist in the system')
def step_impl(context):
    # Do a GET for /player/SomePlayer and get a 404 (as opposed to no perms - eventaully we'll want auth for this
    # with a public view and a private one?)
    url = 'http://localhost:8080/players/%s' % player_name
    resp = requests.get(url=url)
    assert resp.status_code == 404, "want 404; got %d" % resp.status_code


@when(u'we pass in the requisite player data')
def step_impl(context):
    # Do a POST to /players
    url = 'http://localhost:8080/players'
    resp = requests.post(url=url,data={'name': player_name, 'pronouns': 'he/him'})
    assert resp.status_code == 200, "want 200; got %d" % resp.status_code


@then(u'a barebones player is created.')
def step_impl(context):
    # Do a GET for /player/SomePlayer and get a 200
    url = 'http://localhost:8080/players/%s' % player_name
    resp = requests.get(url=url)
    assert resp.status_code == 200, "want 200; got %d" % resp.status_code


@given(u'the player exists in the system')
def step_impl(context):
    # Make sure it exists by trying to create it then fetching it.
    url = 'http://localhost:8080/players'
    resp = requests.post(url=url,data={'name': player_name, 'pronouns': 'he/him'})
    url = 'http://localhost:8080/players/%s' % player_name
    resp = requests.get(url=url)
    assert resp.status_code == 200, "want 200; got %d" % resp.status_code


@when(u'we request the player\'s data')
def step_impl(context):
    url = 'http://localhost:8080/players/%s' % player_name
    resp = requests.get(url=url)
    assert resp.status_code == 200, "want 200; got %d" % resp.status_code


@then(u'we get the requested player\'s data.')
def step_impl(context):
    url = 'http://localhost:8080/players/%s' % player_name
    resp = requests.get(url=url)
    assert resp.status_code == 200, "want 200; got %d" % resp.status_code


@when(u'we pass in the fields to be updated for the player')
def step_impl(context):
    url = 'http://localhost:8080/players/%s' % player_name
    resp = requests.put(url=url,data={'pronouns': 'they/them'})
    assert resp.status_code == 200, "want 200; got %d" % resp.status_code


@then(u'the requested player\'s data is updated accordingly.')
def step_impl(context):
    url = 'http://localhost:8080/players/%s' % player_name
    resp = requests.get(url=url)
    assert (resp.status_code == 200, "want 200; got %d" % resp.status_code and
            'they/them' in resp.text)


@when(u'we request the player be deleted from the system')
def step_impl(context):
    url = 'http://localhost:8080/players/%s' % player_name
    resp = requests.delete(url=url,data={'name':player_name})
    assert resp.status_code == 200, "want 200; got %d" % resp.status_code


@then(u'the player\'s data is deleted from the system.')
def step_impl(context):
    url = 'http://localhost:8080/players/%s' % player_name
    resp = requests.get(url=url)
    assert resp.status_code == 404, "want 404; got %d" % resp.status_code
