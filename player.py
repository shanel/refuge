import pprint

import flask
from google.cloud import ndb

# TODO(shanel): We'll want to make sure Create/Update/Delete (ie not GET methods)
# can only be called by the binary itself.


class Player(ndb.Model):
    name = ndb.StringProperty()
    pronouns = ndb.StringProperty()
    created = ndb.DateTimeProperty(auto_now_add=True)
    updated = ndb.DateTimeProperty(auto_now=True)


def new():
    if flask.request.method == 'POST':
        # NOTE: This field will become the id for the entity - it can't be changed(?)
        playername = flask.request.form.get('name')
        if playername == None:
            return 'name field missing', 400, {
                'Content-Type': 'text/plain; charset=utf-8'
            }
        else:
            client = ndb.Client()
            with client.context() as context:
                key = ndb.Key('Player', playername)
                if not key.get():
                    params = {k: v for k, v in flask.request.form.items() if v and k != 'id'}
                    params['id'] = playername
                    np = Player(**params)
                    np.put()

            # It might be a pre-optimization, but ideally we'd just use the object
            # to create the page and not do another lookup (lookups cost $)
            #
            # Also, if we try to do a create and a user with that name already
            # exists (eventually) we'll want to return an error, not the data.
            return flask.redirect(
                flask.url_for('show_or_update_or_delete',
                              playername=playername))
    if flask.request.method == 'GET':
        return 'NOPE', 200, {'Content-Type': 'text/plain; charset=utf-8'}


def show_or_update_or_delete(playername):
    # Assume GOOGLE_APPLICATION_CREDENTIALS is set in environment
    client = ndb.Client()

    with client.context() as context:
        key = ndb.Key('Player', playername)
        player = key.get()
        if player:
            if flask.request.method == 'DELETE':
                player.key.delete()
                return flask.redirect(flask.url_for('new'))
            if flask.request.method == 'PUT':
                # NOTE: This makes the assumption that the form will be filled with
                # all the current data plus any changes.
                altered = False
                for k, v in flask.request.form.items():
                    if k == 'id':
                        continue
                    if getattr(player, k, None) != None:
                        altered = True
                        setattr(player, k, v)
                if altered:
                    player.put()
            out = pprint.PrettyPrinter(indent=4).pformat(player)
            return out, 200, {'Content-Type': 'text/plain; charset=utf-8'}
        else:
            return 'no user with name {} found'.format(playername), 404, {
                'Content-Type': 'text/plain; charset=utf-8'
            }
