import logging

import flask

import db
import community
import player
#import session

app = flask.Flask(__name__)

app.add_url_rule('/communities',
                 'community.new',
                 community.new,
                 methods=['POST', 'GET'])
app.add_url_rule('/<communityname>',
                 'community.show_or_update_or_delete',
                 community.show_or_update_or_delete,
                 methods=['PUT', 'GET', 'DELETE'])
#app.add_url_rule('/<communityname>/sessions',
#                 'session.new',
#                 session.new,
#                 methods=['POST', 'GET'])
#app.add_url_rule('/<communityname>/sessions/<sessionname>',
#                 'session.show_or_update_or_delete',
#                 session.show_or_update_or_delete,
#                 methods=['PUT', 'GET', 'DELETE'])
app.add_url_rule('/players', 'player.new', player.new, methods=['POST', 'GET'])
app.add_url_rule('/players/<playername>',
                 'player.show_or_update_or_delete',
                 player.show_or_update_or_delete,
                 methods=['PUT', 'GET', 'DELETE'])
#app.add_url_rule('/lotteries', 'session.run_lotteries',
#                 session.run_lotteries)


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
    db.refuge_db.generate_mapping(create_tables=True)
    app.run(host='127.0.0.1', port=8080, debug=True)
