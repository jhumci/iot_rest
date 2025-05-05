#!/usr/bin/env python
# encoding: utf-8
import json
from flask import Flask, request, jsonify, render_template
import datetime
from tinydb import TinyDB, Query
from functools import wraps

app = Flask(__name__)

REQUIRED_FIELDS = ["name", "machine_id", "date", "granulate_color", "amount_in_g"]
REQUIRED_FIELDS_GET = ["name"]

def validate_json(required_fields):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if not request.is_json:
                return jsonify({"error": "Invalid input, JSON required"}), 400
            
            data = request.get_json()
            
            missing_fields = [field for field in required_fields if field not in data]
            if missing_fields:
                return jsonify({"error": "Missing fields", "missing_fields": missing_fields}), 400
            
            return f(*args, **kwargs)
        return wrapper
    return decorator

@app.route("/")
def home():
    print("Home")
    return render_template("home.html")

@app.route('/about')
def about():
    return render_template("about.html")

@app.route('/contact')
def contact():
    return render_template("contact.html")

@app.route('/lager', methods=['GET'])
@validate_json(REQUIRED_FIELDS_GET)
def query_records():
    record = request.get_json()
    name = record['name']
    db = TinyDB('db.json')
    Record = Query()
    if name == "all":
        records = db.all()
        return jsonify(records)
    else:
        records = db.search(Record.name == name)
        return jsonify(records)

@app.route('/test', methods=['POST'])
def test():
    return request.data



@app.route('/lager', methods=['PUT'])
@validate_json(REQUIRED_FIELDS)
def create_record():
    
    # check if the data is a valid json
    record = request.get_json()
    print(f"[{datetime.datetime.now()}] New record received at /lager (PUT): {json.dumps(record, indent=2)}")
    # Initialize the database, assuming the file is named 'db.json'
    db = TinyDB('db.json')

    record["bestell_status"] = "ok"



    # Make the Datum in the format of YYYY-MM-DD HH:MM and add one day and 3 hours
    geplantes_lieferdatum = datetime.datetime.now() + datetime.timedelta(days=1, hours=3)
    record["geplantes_lieferdatum"] = geplantes_lieferdatum.strftime("%Y-%m-%d %H:%M")

    # Insert the record into the database
    db.insert(record)
    return jsonify(record)


if __name__ == "__main__":
    app.run(debug=False, host='0.0.0.0', port=5000)
