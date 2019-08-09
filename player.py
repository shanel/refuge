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
        playername = flask.request.form.get('name')
        if playername == None:
            return 'name field missing', 400, {
                'Content-Type': 'text/plain; charset=utf-8'
            }
        else:
            client = ndb.Client()
            with client.context() as context:
                query = Player.query(Player.name == playername)
                query_length = 0
                for _ in query:
                    query_length += 1
                    # One is one too many
                    break
                if query_length == 0:
                    params = {k: v for k, v in flask.request.form.items() if v}
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
        # Ideally we wouldn't have to do a query every time.
        # In theory we could just have the username be the unique id:
        # https://cloud.google.com/appengine/docs/standard/python/ndb/creating-entity-keys#specifying_your_own_key_name
        # But that would require the url to be forever locked. Obvs we'll
        # let them set their display name to whatever they want whenever,
        # but the url they visit will be static... Or maybe we just create
        # that for them ala SomeParticularlyFunnyAnimalName... Though if
        # they get one they don't like they are kinda stuck. Maybe let them
        # cycle through?
        query = Player.query(Player.name == playername)
        players = []
        for i in query:
            players.append(i)
            # There should only be one, so...
            break
        try:
            player = players[0]
            if flask.request.method == 'DELETE':
                player.key.delete()
                return flask.redirect(flask.url_for('new'))
            if flask.request.method == 'PUT':
                # NOTE: This makes the assumption that the form will be filled with
                # all the current data plus any changes.
                altered = False
                for k, v in flask.request.form.items():
                    if getattr(player, k, None) != None:
                        altered = True
                        setattr(player, k, v)
                if altered:
                    player.put()
            out = pprint.PrettyPrinter(indent=4).pformat(player)
            return out, 200, {'Content-Type': 'text/plain; charset=utf-8'}
        except IndexError:
            return 'no user with name {} found'.format(playername), 404, {
                'Content-Type': 'text/plain; charset=utf-8'
            }
