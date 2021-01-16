import pprint
from datetime import datetime

import flask
import db
from pony import orm

# TODO(shanel): We'll want to make sure Create/Update/Delete (ie not GET methods)
# can only be called by the binary itself.


class Community(db.refuge_db.Entity):
    name = orm.Required(str, unique=True)
    policies = orm.Optional(str, unique=True)
    created = orm.Required(datetime)
    updated = orm.Required(datetime)
    last_lottery_run_at = orm.Optional(datetime)
    session_runs_updated_at = orm.Optional(datetime)


@db_session
def new():
    if flask.request.method == 'POST':
        # NOTE: This field will become the id for the entity - it can't be changed
        # without losing all the data.
        communityname = flask.request.form.get('name')
        if communityname is None:
            return 'name field missing', 400, {
                'Content-Type': 'text/plain; charset=utf-8'
            }
        if not orm.select(c for c in Community if c.name == communityname)[:]:
            params = {
                k: v
                for k, v in flask.request.form.items()
                if v and k != 'id'
            }
            params['id'] = communityname
            Community(**params)

        # It might be a pre-optimization, but ideally we'd just use the object
        # to create the page and not do another lookup (lookups cost $)
        #
        # Also, if we try to do a create and a user with that name already
        # exists (eventually) we'll want to return an error, not the data.
        return flask.redirect(
            flask.url_for('community.show_or_update_or_delete',
                          communityname=communityname))
    if flask.request.method == 'GET':
        return 'NOPE', 200, {'Content-Type': 'text/plain; charset=utf-8'}


# TODO(shanel): Should it be possible to delete communities?
def show_or_update_or_delete(communityname):
    # Assume GOOGLE_APPLICATION_CREDENTIALS is set in environment
    client = ndb.Client()

    with client.context() as context:
        key = ndb.Key('Community', communityname)
        community = key.get()
        if community:
            if flask.request.method == 'DELETE':
                community.key.delete()
                return flask.redirect(flask.url_for('community.new'))
            if flask.request.method == 'PUT':
                # NOTE: This makes the assumption that the form will be filled with
                # all the current data plus any changes.
                altered = False
                for k, v in flask.request.form.items():
                    if k == 'id':
                        continue
                    if getattr(community, k, None) is not None:
                        altered = True
                        setattr(community, k, v)
                if altered:
                    community.put()
            out = pprint.PrettyPrinter(indent=4).pformat(community)
            return out, 200, {'Content-Type': 'text/plain; charset=utf-8'}
        return 'no community with name {} found'.format(
            communityname), 404, {
                'Content-Type': 'text/plain; charset=utf-8'
            }
