#!/usr/bin/env python
# encoding: utf-8
import json
import datetime
from flask import Flask, request, jsonify, render_template
from tinydb import TinyDB, Query
from tinydb.storages import JSONStorage
from tinydb.middlewares import CachingMiddleware
from functools import wraps

app = Flask(__name__)

REQUIRED_FIELDS = ["name", "machine_id", "date", "granulate_color", "amount_in_g"]
REQUIRED_FIELDS_GET = ["name"]

# Safe database access with auto-repair
def safe_open_db():
    try:
        return TinyDB('db.json', storage=CachingMiddleware(JSONStorage))
    except json.JSONDecodeError:
        print("[WARN] db.json is corrupted. Reinitializing with empty data.")
        with open('db.json', 'w') as f:
            f.write('{}')
        return TinyDB('db.json', storage=CachingMiddleware(JSONStorage))

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
    db = safe_open_db()
    Record = Query()
    if name == "all":
        records = db.all()
    else:
        records = db.search(Record.name == name)
    return jsonify(records)

@app.route('/test', methods=['POST'])
def test():
    return request.data

@app.route('/lager', methods=['PUT'])
@validate_json(REQUIRED_FIELDS)
def create_record():
    record = request.get_json()

    # Pretty print the record to console
    print(f"[{datetime.datetime.now()}] New record received at /lager (PUT):\n{json.dumps(record, indent=2)}")

    # Open database safely
    db = safe_open_db()

    # Add additional fields
    record["bestell_status"] = "ok"
    geplantes_lieferdatum = datetime.datetime.now() + datetime.timedelta(days=1, hours=3)
    record["geplantes_lieferdatum"] = geplantes_lieferdatum.strftime("%Y-%m-%d %H:%M")

    # Insert record
    db.insert(record)
    return jsonify(record)

if __name__ == "__main__":
    app.run(debug=False, host='0.0.0.0', port=5000)
