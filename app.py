from flask import Flask, request, jsonify, render_template, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_sqlalchemy import inspect
from datetime import datetime

app = Flask(__name__)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'

db = SQLAlchemy(app)

class User(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	room = db.Column(db.String(50))
	temp = db.Column(db.Float)
	hum = db.Column(db.Float)
	time = db.Column(db.DateTime, default=datetime.now)

def get_columns(model):
	return [col.key for col in model.__table__.columns if col.key != 'id']

def row_as_dict(row):
    return {col.key: getattr(row, col.key) for col in inspect(row).mapper.column_attrs}

def query_as_dict(query):
	all_rows_as_dicts = [row_as_dict(row) for row in query]

	query_dict = {}

	for row in all_rows_as_dicts:
		id = row['id']
		del row['id']
		query_dict[id] = row
	return query_dict

@app.route('/')
def show_all():
	headers = get_columns(User)
	rows = query_as_dict(User.query.order_by(User.time).all())
	print(rows)
	recent = next(iter(rows.values()))
	temp, hum = recent['temp'], recent['hum']
	return render_template('index.html', rows=rows, headers=headers, temp=temp, hum=hum)

@app.route('/new', methods=['POST'])
def parse_entry():
	data = request.json
	room = data['room']
	temp = data['temp']
	hum = data['hum']
	entry = User(room=room, temp=temp, hum=hum)
	db.session.add(entry)
	db.session.commit()
	return "Success"

@app.route('/room/<room>', methods=['GET'])
def get_room(room):
	result = User.query.filter_by(room=room).all()
	rows = query_as_dict(result)
	headers = get_columns(User)
	return render_template("index.html", rows=rows, headers=headers)

if __name__ == '__main__':
	app.run(debug=True)
