import pprint
import time

import flask
from google.cloud import ndb

# TODO(shanel): We'll want to make sure Create/Update/Delete (ie not GET methods)
# can only be called by the binary itself.


class Session(ndb.Model):
    name = ndb.StringProperty()
    # TODO(shanel): In theory this should be an int but all the data comes
    # in from the post as a string... Later we can do the needful and make
    # specific things into ints before sticking them int.
    max_players = ndb.StringProperty()
    created = ndb.DateTimeProperty(auto_now_add=True)
    updated = ndb.DateTimeProperty(auto_now=True)


def new(communityname):
    if flask.request.method == 'POST':
        sessionname = flask.request.form.get('name')
        if sessionname == None:
            return 'session or community name field missing', 400, {
                'Content-Type': 'text/plain; charset=utf-8'
            }
        else:
            client = ndb.Client()
            with client.context() as context:
                community_key = ndb.Key('Community', communityname)
                if community_key.get():
                    key = ndb.Key('Community', communityname, 'Session', sessionname)
                    if not key.get():
                        params = {k: v for k, v in flask.request.form.items() if v and k != 'id'}
                        params['id'] = sessionname
                        np = Session(parent=community_key,**params)
                        key = np.put()
                else:
                    return 'could not find community {}'.format(communityname), 404, {'Content-Type': 'text/plain; charset=utf-8'}


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
        return 'CALENDAR GOES HERE', 200, {'Content-Type': 'text/plain; charset=utf-8'}


def show_or_update_or_delete(communityname, sessionname):
    # Assume GOOGLE_APPLICATION_CREDENTIALS is set in environment
    client = ndb.Client()

    with client.context() as context:
        key = ndb.Key('Community', communityname, 'Session', sessionname)
        session = key.get()
        if session:
            if flask.request.method == 'DELETE':
                session.key.delete()
                return flask.redirect(flask.url_for('session.new', communityname=communityname))
            if flask.request.method == 'PUT':
                # NOTE: This makes the assumption that the form will be filled with
                # all the current data plus any changes.
                altered = False
                for k, v in flask.request.form.items():
                    if k == 'id':
                        continue
                    if getattr(session, k, None) != None:
                        altered = True
                        setattr(session, k, v)
                if altered:
                    session.put()
            out = pprint.PrettyPrinter(indent=4).pformat(session)
            return out, 200, {'Content-Type': 'text/plain; charset=utf-8'}
        else:
            return 'no session with name {} found in community {}'.format(sessionname, communityname), 404, {
                'Content-Type': 'text/plain; charset=utf-8'
            }
