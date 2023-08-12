from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'app.sqlite')
db = SQLAlchemy(app)
ma = Marshmallow(app)

class Guide(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), unique=False)
    content = db.Column(db.String(144), unique=False)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    decks = db.relationship('Deck', backref='user', lazy=True)




class Deck(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    image = db.Column(db.String, nullable=False)
    wins = db.Column(db.String, nullable=False)
    losses = db.Column(db.String, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # def __init__(self, name, image, wins, losses):
    #     self.name=name
    #     self.image = image
    #     self.wins= wins
    #     self.losses = losses
    #     self.user_id = user_id



class UserSchema(ma.Schema):
    class Meta:
        fields = ('username', 'decks')

class DeckSchema(ma.Schema):
    class Meta:
        fields = ('name', 'image', 'wins', 'losses')


user_schema = UserSchema()
users_schema = UserSchema(many=True)
deck_schema = DeckSchema()
decks_schema = DeckSchema(many=True)

# Endpoint to create a new guide
@app.route('/user', methods=["POST"])
def add_user():
    try:
        data = request.get_json()
        username = data['username']
        decks = data['decks']

        user = User(username=username)

        for deck_data in decks:
            deck_name = deck_data['name']
            deck_image = deck_data['image']
            deck_wins = deck_data['wins']
            deck_losses = deck_data['losses']

            deck = Deck(name=deck_name, image= deck_image, wins = deck_wins, losses= deck_losses)
            user.decks.append(deck)

        db.session.add(user)
        db.session.commit()

        return jsonify(data), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Endpoint to query all guides
@app.route("/users", methods=["GET"])
def  get_users():
    all_users = Guide.query.all()
    result = user_schema.dump(all_users)
    return jsonify(result)

# Endpoint to query a single user
@app.route("/user/<id>", methods=["GET"])
def get_user(id):
    try:
        user = User.query.get(id)
        if user:
            user_data = {
                'id': id,
                'username': user.username,
                'decks': [
                    {
                        'id': deck.id,
                        'name': deck.name,
                        'image': deck.image,
                        'wins': deck.wins,
                        'losses': deck.losses
                    }
                    for deck in user.decks
                ]
            }
            return jsonify(user_data), 200
        else:
            return jsonify({'error': 'User not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

#Endpoint for updating a guide
@app.route("/guide/<id>", methods=["PUT"])
def guide_update(id):
    guide = Guide.query.get(id)
    title = request.json['title']
    content = request.json['content']

    guide.title=title
    guide.content = content

    db.session.commit()
    return guide_schema.jsonify(guide)



if __name__ == '__main__':
    app.run(debug=True)

