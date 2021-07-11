from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
from random import choice
import json

app = Flask(__name__)

##Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JSON_AS_ASCII'] = False
db = SQLAlchemy(app)
db.make_connector()

API_KEY_FOR_DELETE = "TOPSECRETAPIKEY"

##Cafe TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)

    def to_dict(self):
        # Method 1.
        dictionary = {}
        # Loop through each column in the data record
        for column in self.__table__.columns:
            # Create a new dictionary entry;
            # where the key is the name of the column
            # and the value is the value of the column
            print(getattr(self, column.name))
            dictionary[column.name] = getattr(self, column.name)
        return dictionary


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/random", methods=["GET"])
def random_cafe():
    # if request.method == "GET":
    all_cafes = db.session.query(Cafe).all()
    random_cafe = choice(all_cafes)
    cafe_data={"cafe":{
        "id": random_cafe.id,
        "name": random_cafe.name,
        "map_url": random_cafe.map_url,
        "img_url": random_cafe.img_url,
        "location": random_cafe.location,
        "seats": random_cafe.seats,
        "has_toilet": random_cafe.has_toilet,
        "has_wifi": random_cafe.has_wifi,
        "has_sockets": random_cafe.has_sockets,
        "can_take_calls": random_cafe.can_take_calls,
        "coffee_price": random_cafe.coffee_price
    }}
    rqst_for_api = json.dumps(cafe_data)
    print(rqst_for_api)
    return rqst_for_api


@app.route("/all", methods=["GET"])
def all_cafe():
    # all_cafes = db.session.query(Cafe).all()
    # all_cafes_data = []
    # for cafe in all_cafes:
    #     cafe_data = {
    #         "id": cafe.id,
    #         "name": cafe.name,
    #         "map_url": cafe.map_url,
    #         "img_url": cafe.img_url,
    #         "location": cafe.location,
    #         "seats": cafe.seats,
    #         "has_toilet": cafe.has_toilet,
    #         "has_wifi": cafe.has_wifi,
    #         "has_sockets": cafe.has_sockets,
    #         "can_take_calls": cafe.can_take_calls,
    #         "coffee_price": cafe.coffee_price
    #     }
    #     all_cafes_data.append(cafe_data)
    # all_cafes_json = {"cafes": all_cafes_data}
    # return json.dumps(all_cafes_json)
    cafes = db.session.query(Cafe).all()
    # This uses a List Comprehension but you could also split it into 3 lines.
    return jsonify(cafes=[cafe.to_dict() for cafe in cafes])


@app.route("/search")
def search():
    query_location = request.args.get("loc")
    all_matched_cafe = Cafe.query.filter_by(location=query_location).all()
    if all_matched_cafe:
        return jsonify(cafes=[cafe.to_dict() for cafe in all_matched_cafe])
    else:
        return jsonify(error={"Not Found": "Sorry, we don't have a cafe at that location."})


@app.route("/add", methods=["POST"])
def post_new_cafe():
    new_cafe = Cafe(
        name=request.form.get("name"),
        map_url=request.form.get("map_url"),
        img_url=request.form.get("img_url"),
        location=request.form.get("loc"),
        has_sockets=bool(request.form.get("sockets")),
        has_toilet=bool(request.form.get("toilet")),
        has_wifi=bool(request.form.get("wifi")),
        can_take_calls=bool(request.form.get("calls")),
        seats=request.form.get("seats"),
        coffee_price=request.form.get("coffee_price"),
    )
    db.session.add(new_cafe)
    db.session.commit()
    return jsonify(response={"success": "Successfully added the new cafe."})


@app.route("/update-price/<cafe_id>", methods=["PATCH"])
def update_price(cafe_id):
    query_price = request.args.get("price")
    cafe_selected = Cafe.query.filter_by(id=cafe_id).first()
    if cafe_selected:
        cafe_selected.coffee_price = query_price
        db.session.commit()
        return jsonify(response={"success": "Successfully update the price."})
    else:
        return jsonify(response={"error": "Sorry, A cafe with that is was not found in the database"})


@app.route("/report-closed/<cafe_id>", methods=["DELETE"])
def delete_cafe(cafe_id):
    cafe_selected = Cafe.query.filter_by(id=cafe_id).first()
    api_key = request.args.get("api-key")
    if cafe_selected and api_key == API_KEY_FOR_DELETE:
        db.session.delete(cafe_selected)
        db.session.commit()
        return jsonify(response={"success": "Successfully delete the cafe."})
    elif not cafe_selected:
        return jsonify(response={"error": "Sorry, A cafe with that is was not found in the database"})
    else:
        return jsonify(response={"error": "Sorry, That's not allowed. Make sur you have the correct api_key."})


if __name__ == '__main__':
    app.run(debug=True)
