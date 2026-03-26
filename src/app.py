"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Character, Planet, Favorite
# from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace(
        "postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object


@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints


@app.route('/')
def sitemap():
    return generate_sitemap(app)


@app.route('/seed', methods=['GET'])
def seed_data():

    if User.query.first():
        return jsonify({"msg": "Ya hay datos"})

    luke = Character(name="Luke Skywalker", gender="male", hair_color="blond")
    vader = Character(name="Darth Vader", gender="male", hair_color="none")

    tatooine = Planet(name="Tatooine", population="200000", climate="arid")

    user1 = User(email="test@test.com", password="1234", is_active=True)

    db.session.add_all([luke, vader, tatooine, user1])
    db.session.commit()

    return jsonify({"msg": "Datos insertados"})


@app.route('/people', methods=['GET'])
def get_people():
    people = Character.query.all()
    results = [p.serialize() for p in people]
    return jsonify(results), 200


@app.route('/people/<int:people_id>', methods=['GET'])
def get_one_person(people_id):
    person = Character.query.get(people_id)

    if person is None:
        return jsonify({"msg": "Person not found"}), 404

    return jsonify(person.serialize()), 200


@app.route('/planets', methods=['GET'])
def get_planets():
    planets = Planet.query.all()
    results = [p.serialize() for p in planets]
    return jsonify(results), 200


@app.route('/planets/<int:planet_id>', methods=['GET'])
def get_one_planet(planet_id):
    planet = Planet.query.get(planet_id)

    if planet is None:
        return jsonify({"msg": "Planet not found"}), 404

    return jsonify(planet.serialize()), 200


@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    results = [u.serialize() for u in users]
    return jsonify(results), 200


@app.route('/users/favorites', methods=['GET'])
def get_user_favorites():
    favorites = Favorite.query.all()
    results = [f.serialize() for f in favorites]
    return jsonify(results), 200



@app.route('/favorite/planet/<int:planet_id>', methods=['POST'])
def add_favorite_planet(planet_id):

    new_fav = Favorite(
        user_id=1,
        planet_id=planet_id
    )


    db.session.add(new_fav)
    db.session.commit()

    return jsonify({"msg": "Favorite planet added"}), 201


@app.route('/favorite/planet/<int:planet_id>', methods=['DELETE'])
def delete_favorite_planet(planet_id):

    fav = Favorite.query.filter_by(planet_id=planet_id, user_id=1).first()

    if fav is None:
        return jsonify({"msg": "Not found"}), 404

    db.session.delete(fav)
    db.session.commit()

    return jsonify({"msg": "Deleted"}), 200


@app.route('/favorite/people/<int:people_id>', methods=['DELETE'])
def delete_favorite_people(people_id):


    fav = Favorite.query.filter_by(character_id=people_id, user_id=1).first()

    if fav is None:
        return jsonify({"msg": "Not found"}), 404

    db.session.delete(fav)
    db.session.commit()

    return jsonify({"msg": "Deleted"}), 200


@app.route('/favorite/people/<int:people_id>', methods=['POST'])
def add_favorite_people(people_id):

    new_fav = Favorite(
        user_id=1,
        character_id=people_id
    )

    db.session.add(new_fav)
    db.session.commit()

    return jsonify({"msg": "Favorite character added"}), 201


# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
