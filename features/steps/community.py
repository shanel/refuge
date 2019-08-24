import requests
import time

from behave import *

community_name = 'SomeCommunity%d' % int(time.time())


@given(u'the community does not currenty exist in the system')
def step_impl(context):
    # Do a GET for /SomeCommunity and get a 404 (as opposed to no perms - eventaully we'll want auth for this
    # with a public view and a private one?)
    url = 'http://localhost:8080/%s' % community_name
    resp = requests.get(url=url)
    assert resp.status_code == 404, "want 404; got %d" % resp.status_code


@when(u'we pass in the requisite community data')
def step_impl(context):
    # Do a POST to /communities
    url = 'http://localhost:8080/communities'
    resp = requests.post(url=url,
                         data={
                             'name': community_name,
                             'policies': 'we-have-them'
                         })
    assert resp.status_code == 200, "want 200; got %d" % resp.status_code


@then(u'a barebones community is created.')
def step_impl(context):
    # Do a GET for /SomeCommunity and get a 200
    url = 'http://localhost:8080/%s' % community_name
    resp = requests.get(url=url)
    assert resp.status_code == 200, "want 200; got %d" % resp.status_code


@given(u'the community exists in the system')
def step_impl(context):
    # Make sure it exists by trying to create it then fetching it.
    url = 'http://localhost:8080/communities'
    resp = requests.post(url=url,
                         data={
                             'name': community_name,
                             'policies': 'we-have-them'
                         })
    url = 'http://localhost:8080/%s' % community_name
    resp = requests.get(url=url)
    assert resp.status_code == 200, "want 200; got %d" % resp.status_code


@when(u'we request the community\'s data')
def step_impl(context):
    url = 'http://localhost:8080/%s' % community_name
    resp = requests.get(url=url)
    assert resp.status_code == 200, "want 200; got %d" % resp.status_code


@then(u'we get the requested community\'s data.')
def step_impl(context):
    url = 'http://localhost:8080/%s' % community_name
    resp = requests.get(url=url)
    assert resp.status_code == 200, "want 200; got %d" % resp.status_code


@when(u'we pass in the fields to be updated for the community')
def step_impl(context):
    url = 'http://localhost:8080/%s' % community_name
    resp = requests.put(url=url, data={'policies': 'we-have-more'})
    assert resp.status_code == 200, "want 200; got %d" % resp.status_code


@then(u'the requested community\'s data is updated accordingly.')
def step_impl(context):
    url = 'http://localhost:8080/%s' % community_name
    resp = requests.get(url=url)
    assert resp.status_code == 200, "want 200; got %d" % resp.status_code and 'we-have-more' in resp.text


@when(u'we request the community be deleted from the system')
def step_impl(context):
    url = 'http://localhost:8080/%s' % community_name
    resp = requests.delete(url=url, data={'name': community_name})
    assert resp.status_code == 200, "want 200; got %d" % resp.status_code


@then(u'the community\'s data is deleted from the system.')
def step_impl(context):
    url = 'http://localhost:8080/%s' % community_name
    resp = requests.get(url=url)
    assert resp.status_code == 404, "want 404; got %d" % resp.status_code
