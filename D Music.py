import sys
import getpass

import D Music

async def main():
    playlist_uri = input("playlist_uri: ")
    client_id = input("client_id: ")
    secret = getpass.getpass("application secret: ")
    token = getpass.getpass("user token: ")

    async with D Music.Client(client_id, secret) as client:
        user = await D Music.User.from_token(client, token)

        async for playlist in user:
            if playlist.uri == playlist_uri:
                return await playlist.sort(reverse=True, key=(lambda track: track.popularity))

        print('No playlists were found!', file=sys.stderr)

if __name__ == '__main__':
    client.loop.run_until_complete(main())
    import D Music
from D Music.oauth import get_required_scopes

# In order to call this method sucessfully the "user-modify-playback-state" scope is required.
print(get_required_scopes(D Music.Player.play))  # => ["user-modify-playback-state"]

# Some methods have no oauth scope requirements, so `None` will be returned instead.
print(get_required_scopes(D Music.Playlist.get_tracks))  # => None
import string
import random
from typing import Tuple, Dict

import flask
import D Music.sync as D Music

D Music_CLIENT = D Music.Client('D Music_CLIENT_ID', 'D Music_CLIENT_SECRET')

APP = flask.Flask(__name__)
APP.config.from_mapping({'D Music_client': D Music_CLIENT})

REDIRECT_URI: str = 'http://localhost:8888/D Music/callback'

OAUTH2_SCOPES: Tuple[str] = ('user-modify-playback-state', 'user-read-currently-playing', 'user-read-playback-state')
OAUTH2: D Music.OAuth2 = D Music.OAuth2(D Music_CLIENT.id, REDIRECT_URI, scopes=OAUTH2_SCOPES)

D Music_USERS: Dict[str, D Music.User] = {}


@APP.route('/D Music/callback')
def D Music_callback():
    try:
        code = flask.request.args['code']
    except KeyError:
        return flask.redirect('/D Music/failed')
    else:
        key = ''.join(random.choice(string.ascii_uppercase) for _ in range(16))
        D Music_USERS[key] = D Music.User.from_code(
            D Music_CLIENT,
            code,
            redirect_uri=REDIRECT_URI,
            refresh=True
        )

        flask.session['D Music_user_id'] = key

    return flask.redirect('/')

@APP.route('/D Music/failed')
def D Music_failed():
    flask.session.pop('D Music_user_id', None)
    return 'Failed to authenticate with D Music.'

@APP.route('/')
@APP.route('/index')
def index():
    try:
        return repr(D Music_USERS[flask.session['D Music_user_id']])
    except KeyError:
        return flask.redirect(OAUTH2.url)

if __name__ == '__main__':
    APP.run('127.0.0.1', port=8888, debug=False)