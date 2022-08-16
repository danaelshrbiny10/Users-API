from datetime import datetime, timedelta
from flask import Flask, jsonify, request, make_response
from flask_cors import CORS
from flask_restx import Resource, Api, fields
from flask_sqlalchemy import SQLAlchemy
import jwt
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import os



authorization = {
    'apikey' : {
        'type' : 'apiKey',
        'in' : 'header',
        'name' : 'x-access-token'
    }

}


app = Flask(__name__)
api = Api(app, doc = "/", title="User's API", description="a simple REST API for user data", authorizations=authorization)


CORS(app)

base_dir = os.path.dirname(os.path.realpath(__file__))

app.config["SECRET_KEY"] = 'something-secret'
app.config['SQLALCHEMY_TRACT_MODIFICATION'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+os.path.join(base_dir, 'user.db')
app.config['SQLALCHEMY_ECHO'] = True



base_dir = os.path.dirname(os.path.realpath(__file__))

db = SQLAlchemy(app)


class User(db.Model) :
    id =db.Column(db.Integer(), primary_key = True)
    name = db.Column(db.String(30), nullable = False)
    age = db.Column(db.Integer(), nullable = False)
    title = db.Column(db.String(30), nullable = False)
    password = db.Column(db.String())


    def __repr__(self) :
        return self.name

UserModel = api.model(
    "User", {
        'id' : fields.Integer(),
        'name' : fields.String(),
        'age' : fields.Integer(),
        'title' : fields.String(),
    }
)


def token_required(f) :
    @wraps(f)
    def decorated(*args, **kwargs) :
        token = None
        if 'x-access-token' in request.headers :
            token = request.headers['x-access-token']
        if not token :
            return jsonify({'message' : 'Token Is missing'}), 401
        
        try :
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            user = User.query.filter_by(id = data['id']).first()
        except :
            return jsonify({
                "message" : "invalid Token"
            })
        return f(user, *args, **kwargs)
    return decorated

@api.route("/users/")
class UserData(Resource) :
    
    @api.marshal_list_with(UserModel, envelope = "users", code = 200)
    @token_required
    @api.doc(security='apikey')
    def get(self, user) :
        users = User.query.all()
        return users

    @api.marshal_with(UserModel, envelope = "user", code = 201)
    @token_required
    @api.doc(params = {"name" : "User name", "age" : "User age", "title" : "User title", 'password' : "User password"}, security='apikey')
    def post(self, user) :
        data = request.args
        keys = ['name', 'age', 'title', 'password']
        check = [True if data.get(key) is not None else False  for key in keys ]
        if not all(check) :
            return {'message' : 'fill the empty fields please .'}, 400
        name = data.get("name")
        try :
            age = int(data.get("age"))
        except :
            return {'message' : 'enter a correct age format .'}, 400 
        title = data.get("title")
        password = data.get('password')
        new_user = User(name = name, age = age, title = title, password = generate_password_hash(password))
        db.session.add(new_user)
        db.session.commit()
        return new_user



@api.route("/users/<int:id>")
class UserDataPk(Resource) :
    @token_required
    @api.marshal_with(UserModel, envelope = "user_get", code = 201)
    @api.doc(security='apikey')
    def get(self, user, id):
        user = User.query.get_or_404(id)
        return user
    @token_required
    @api.marshal_with(UserModel, envelope = "user_put", code = 201)
    @api.doc(params={'name' : 'User name', 'age' : 'User age', 'title' : 'User title'}, security='apikey')
    def put(self, user, id)  :
        data = request.args
        user = User.query.get_or_404(id)
        if data.get('name') != None :
            user.name = data.get('name')
        if data.get('age') != None :
            try :
                user.age = int(data.get('age'))
            except :
                pass
        if data.get('title') != None :
            user.title = data.get('title')
        db.session.commit()
        return user


    @token_required
    @api.marshal_with(UserModel, envelope = "user", code = 201)
    @api.doc(security='apikey')
    def delete(self, user, id) :
        user = User.query.get_or_404(id)
        db.session.delete(user)
        db.session.commit()
        return user


@api.route('/login/')
class Login(Resource) :
    @api.doc(params = {'id' : 'user id', 'password' : 'user password'}, security = [])
    def post(self) :
        data = request.args
        id = int(data.get('id'))
        password = data.get('password')
        user = User.query.filter_by(id = id).first()
        if (check_password_hash(user.password, password)) :
            token = jwt.encode({
            'id': user.id,
            'exp' : datetime.utcnow() + timedelta(hours=1),
            }, app.config['SECRET_KEY'], algorithm="HS256")
            return make_response(jsonify({'token' : token}), 201)
        return make_response(jsonify('Could not verify',
        403,
        {'WWW-Authenticate' : 'Basic realm ="Wrong Password !!"'}))

@api.route('/signup/')
class Signup(Resource) :
    @api.marshal_with(UserModel, envelope = "signup")
    @api.doc(params = {"name" : "User name", "age" : "User age", "title" : "User title", 'password' : "User password"})
    def post(self) :
        data = request.args
        keys = ['name', 'age', 'title', 'password']
        check = [True if data.get(key) is not None else False  for key in keys ]
        if not all(check) :
            return {'message' : 'fill the empty fields please .'}, 400
        name = data.get("name")
        try :
            age = int(data.get("age"))
        except :
            return {'message' : 'enter a correct age format .'}, 400 
        title = data.get("title")
        password = data.get('password')
        new_user = User(name = name, age = age, title = title, password = generate_password_hash(password))
        db.session.add(new_user)
        db.session.commit()
        return new_user




@app.shell_context_processor
def make_shell_processor() :
    return {
        "db" : db,
        "User" : User
    }


if __name__ == "__main__" :
    app.run(debug=True)

