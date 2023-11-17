from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = ''

db = SQLAlchemy(app)

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    eventType = db.Column(db.String(50))
    timestamp = db.Column(db.String(50))
    message = db.Column(db.String(200))

    def __init__(self, eventType, timestamp, message):
        self.eventType = eventType
        self.timestamp = timestamp
        self.message = message

@app.route('/events', methods=['POST'])
def create_event():
    data = request.json
    event = Event(data['eventType'], data['timestamp'], data['message'])

    try:
        db.session.add(event)
        db.session.commit()
        return 'Event created successfully', 201
    except Exception as e:
        db.session.rollback()
        return f'Error: {str(e)}', 500
    finally:
        db.session.close()

if __name__ == '__main__':
    # Create database tables
    with app.app_context():
        db.create_all()

    # Run the Flask app
    app.run()
