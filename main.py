import logging
import socket

import flask

import player

app = flask.Flask(__name__)

app.add_url_rule('/players',
                 'new',
                 player.new,
                 methods=['POST', 'GET'])
app.add_url_rule('/players/<playername>', 'show',
                 player.show)

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
