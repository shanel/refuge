import datetime
import logging
import socket

import flask
from google.cloud import datastore

app = flask.Flask(__name__)

# TODO(shanel): We'll want to make sure Create/Update/Delete (ie not GET methods)
# can only be called by the binary itself.


# For the real stuff
def create_client(project_id):
    return datastore.Client(project_id)


def add_player(client, name):
    key = client.key('player')

    player = datastore.Entity(key=key)
    player.update({
        'name': name,
        'timestamp': datetime.datetime.utcnow(),
    })

    client.put(player)


@app.route('/player/create', methods=['POST'])
def create_new_player():
    playername = flask.request.form.get('name')
    if playername == None:
        return 'name field missing', 400, {
            'Content-Type': 'text/plain; charset=utf-8'
        }
    else:
        client = datastore.Client()
        query = client.query(kind='player')
        # Ideally we'd use add_filter to find the right name, but in the dev
        # environment there is no index.
        res = None
        results = query.fetch()
        for r in results:
            if r['name'] == playername:
                res = True
                break
        if not res:
            add_player(client, playername)
        return flask.redirect(
            flask.url_for('show_player_profile', playername=playername))


# [START gae_flex_datastore_app]
@app.route('/player/<playername>')
def show_player_profile(playername):
    # eventually this should be a singleton for the app
    ds = datastore.Client()
    #    ds = create_client('refuge-scheduler')

    client = datastore.Client()
    query = client.query(kind='player')
    # Ideally we'd use add_filter to find the right name, but in the dev
    # environment there is no index.
    res = None
    results = query.fetch()
    for r in results:
        if r['name'] == playername:
            res = r
            break

    out = None
    if res:
        out = 'Player Name: {name}\n'.format(**res)
        return out, 200, {'Content-Type': 'text/plain; charset=utf-8'}
    else:
        return 'no user with name {} found'.format(playername), 404, {
            'Content-Type': 'text/plain; charset=utf-8'
        }


# [END gae_flex_datastore_app]


@app.errorhandler(500)
def server_error(e):
    logging.exception('An error occurred during a request.')
    return """
    An internal error occurred: <pre>{}</pre>
    See logs for full stacktrace.
    """.format(e), 500


if __name__ == '__main__':
    # This is used when running locally. Gunicorn is used to run the
    # application on Google App Engine. See entrypoint in app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)
