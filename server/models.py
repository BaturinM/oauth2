from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'user_table'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(), unique=True, nullable=False)
    password = db.Column(db.String(), nullable=False)
    email = db.Column(db.String())
    phone = db.Column(db.String())

    def __str__(self):
        return f'{self.username}: {self.email}'


class Client(db.Model):
    name = db.Column(db.String())
    client_id = db.Column(db.String(), primary_key=True)
    client_secret = db.Column(db.String(), unique=True, nullable=False)
    client_type = db.Column(db.String())
    _redirect_uris = db.Column(db.Text)
    _default_scopes = db.Column(db.Text, default='email phone')

    @property
    def redirect_uris(self):
        return self._redirect_uris.split() if self._redirect_uris else []

    @property
    def default_redirect_uri(self):
        return self.redirect_uris[0]

    @property
    def default_scopes(self):
        return self._default_scopes.split() if self._default_scopes else []


class Grant(db.Model):
    __tablename__ = 'grant_table'

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user_table.id', ondelete='CASCADE'))
    user = db.relationship('User')

    client_id = db.Column(db.String(), db.ForeignKey('client.client_id'), nullable=False)
    client = db.relationship('Client')

    code = db.Column(db.String(), nullable=False)
    redirect_uri = db.Column(db.String())
    _scopes = db.Column(db.Text)
    expires = db.Column(db.DateTime)

    def delete(self):
        db.session.delete(self)
        db.session.commit()
        return self

    @property
    def scopes(self):
        return self._scopes.split() if self._scopes else None


class Token(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user_table.id', ondelete='CASCADE'))
    user = db.relationship('User')
    client_id = db.Column(db.String(), db.ForeignKey('client.client_id'), nullable=False)
    client = db.relationship('Client')

    token_type = db.Column(db.String(40))

    access_token = db.Column(db.String(255), unique=True)
    refresh_token = db.Column(db.String(255), unique=True)
    expires = db.Column(db.DateTime)
    _scopes = db.Column(db.Text)

    def delete(self):
        db.session.delete(self)
        db.session.commit()
        return self

    @property
    def scopes(self):
        return self._scopes.split() if self._scopes else None
