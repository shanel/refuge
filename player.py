import flask
from google.cloud import ndb

# TODO(shanel): We'll want to make sure Create/Update/Delete (ie not GET methods)
# can only be called by the binary itself.


class Player(ndb.Model):
    name = ndb.StringProperty()
    created = ndb.DateTimeProperty(auto_now_add=True)
    updated = ndb.DateTimeProperty(auto_now=True)


# This should probably eventually just accept a dict.
def add_player(client, name):
    with client.context() as context:
        new = Player(name=name)
        return new.put()


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
                    np = Player(name=playername)
                    np.put()

            # It might be a pre-optimization, but ideally we'd just use the object
            # to create the page and not do another lookup (lookups cost $)
            #
            # Also, if we try to do a create and a user with that name already
            # exists (eventually) we'll want to return an error, not the data.
            return flask.redirect(
                flask.url_for('show', playername=playername))
    if flask.request.method == 'GET':
        return 'NOPE', 403, {'Content-Type': 'text/plain; charset=utf-8'}


def show(playername):
    # Assume GOOGLE_APPLICATION_CREDENTIALS is set in environment
    client = ndb.Client()

    with client.context() as context:
        query = Player.query(Player.name == playername)
        players = []
        for i in query:
            players.append(i)
            # There should only be one, so...
            break
        try:
            out = 'Player Name: {}\n'.format(players[0].name)
            return out, 200, {'Content-Type': 'text/plain; charset=utf-8'}
        except IndexError:
            return 'no user with name {} found'.format(playername), 404, {
                'Content-Type': 'text/plain; charset=utf-8'
            }
