from flask import g, render_template, request, redirect, url_for, session
from flask_oauthlib.provider import OAuth2Provider

from .models import db, User, Client, Grant, Token
from .settings import GRANT_TOKEN_EXPIRE

from datetime import datetime, timedelta


def current_user():
    return g.user


def default_provider(app):
    oauth = OAuth2Provider(app)

    @oauth.clientgetter
    def get_client(client_id):
        return Client.query.filter_by(client_id=client_id).first()

    @oauth.grantgetter
    def get_grant(client_id, code):
        return Grant.query.filter_by(client_id=client_id, code=code).first()

    @oauth.tokengetter
    def get_token(access_token=None):
        if access_token:
            return Token.query.filter_by(access_token=access_token).first()
        return None

    @oauth.grantsetter
    def set_grant(client_id, code, request, *args, **kwargs):
        expires = datetime.utcnow() + timedelta(seconds=GRANT_TOKEN_EXPIRE)
        grant = Grant(client_id=client_id,
                      code=code['code'],
                      redirect_uri=request.redirect_uri,
                      _scopes=' '.join(request.scopes),
                      user_id=g.user.id,
                      expires=expires)
        db.session.add(grant)
        db.session.commit()
        return grant

    @oauth.tokensetter
    def set_token(token, request, *args, **kwargs):
        expires_in = token.get('expires_in')
        expires = datetime.utcnow() + timedelta(seconds=expires_in)

        t = Token(access_token=token['access_token'],
                  refresh_token=token['refresh_token'],
                  token_type=token['token_type'],
                  _scopes=token['scope'],
                  expires=expires,
                  client_id=request.client.client_id,
                  user_id=request.user.id)
        db.session.add(t)
        db.session.commit()
        return t

    return oauth


def create_server(app, oauth=None):
    if not oauth:
        oauth = default_provider(app)

    @app.before_request
    def load_user():
        g.user = User.query.filter_by(username=session.get('user_id')).first()

    @app.route('/oauth/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'GET':
            return render_template('login.html')
        user = User.query.filter_by(**request.form).first()
        if not user:
            return {}, 401
        g.user = user
        session['user_id'] = user.username
        return redirect(url_for('authorize', **request.args.to_dict()))

    @app.route('/oauth/authorize', methods=['GET', 'POST'])
    @oauth.authorize_handler
    def authorize(*args, **kwargs):
        if request.method == 'GET':
            client_id = kwargs.get('client_id')
            scopes = kwargs.get('scopes')

            client = Client.query.filter_by(client_id=client_id).first()
            client_name = client.name

            return render_template('confirm.html',
                                   client_name=client_name,
                                   scope=scopes[0])

        confirm = request.form.get('confirm', 'no')
        return confirm == 'yes'

    @app.route('/oauth/token', methods=['POST', 'GET'])
    @oauth.token_handler
    def access_token():
        return {}

    @app.route('/api/client')
    @oauth.require_oauth()
    def client_api():
        oauth = request.oauth
        return {'client': oauth.client.name}

    @app.route('/api/email')
    @oauth.require_oauth('email')
    def email_api():
        oauth = request.oauth
        return {'email': oauth.user.email}

    @app.route('/api/phone')
    @oauth.require_oauth('phone')
    def phone_api():
        oauth = request.oauth
        return {'phone': oauth.user.phone}

    # client stub
    @app.route('/authorized')
    def authorized():
        code = request.args.get('code')
        return {'code': code}
