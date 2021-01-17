import json
import pprint
from datetime import datetime

import flask
from pony import orm

import refuge_types

# TODO(shanel): We'll want to make sure Create/Update/Delete (ie not GET methods)
# can only be called by the binary itself.

@orm.db_session
def new():
    if flask.request.method == 'POST':
        playername = flask.request.form.get('name')
        if not playername:
            return 'name field missing', 400, {
                'Content-Type': 'text/plain; charset=utf-8'
            }
        if not orm.select(p for p in refuge_types.Player if p.name == playername)[:]:
            params = {
                k: v
                for k, v in flask.request.form.items()
                if v and k != 'id'
            }
            params['name'] = playername
            params['created'] = datetime.utcnow()
            params['updated'] = datetime.utcnow()
            refuge_types.Player(**params)

        # It might be a pre-optimization, but ideally we'd just use the object
        # to create the page and not do another lookup (lookups cost $)
        #
        # Also, if we try to do a create and a user with that name already
        # exists (eventually) we'll want to return an error, not the data.
        return flask.redirect(
            flask.url_for('player.show_or_update_or_delete',
                          playername=playername))
    if flask.request.method == 'GET':
        return 'NOPE', 200, {'Content-Type': 'text/plain; charset=utf-8'}


@orm.db_session
def show_or_update_or_delete(playername):
    results = orm.select(p for p in refuge_types.Player if p.name == playername)[:]
    if results:
        player = results[0]  # names are unique so there sould only be one
        if flask.request.method == 'DELETE':
            player.delete()
            return flask.redirect(flask.url_for('player.new'))
        if flask.request.method == 'PUT':
            # NOTE: This makes the assumption that the form will be filled with
            # all the current data plus any changes.
            for k, v in flask.request.form.items():
                if k in ('id', 'name'):
                    continue
                if getattr(player, k, None) is not None:
                    setattr(player, k, v)
                    setattr(player, 'updated', datetime.now())
        out = pprint.PrettyPrinter(indent=4).pformat(player)
        return out, 200, {'Content-Type': 'text/plain; charset=utf-8'}
    else:
        return 'no user with name {} found'.format(playername), 404, {
            'Content-Type': 'text/plain; charset=utf-8'
        }
