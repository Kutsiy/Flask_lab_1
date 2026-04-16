from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///clinic.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class Doctor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    appointments = db.relationship('Appointment', backref='doctor', lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name
        }


class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    phone = db.Column(db.String(20))
    appointments = db.relationship('Appointment', backref='patient', lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "phone": self.phone
        }


class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'), nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "doctor": self.doctor.to_dict(),
            "patient": self.patient.to_dict(),
            "date": self.date.isoformat()
        }

def init():
    if Doctor.query.count() == 0:
        db.session.add_all([
            Doctor(first_name='John', last_name='Doe'),
            Doctor(first_name='Alice', last_name='Smith'),
            Doctor(first_name='Bob', last_name='Brown'),
            Doctor(first_name='Maria', last_name='Garcia'),
            Doctor(first_name='James', last_name='Wilson'),
        ])

    if Patient.query.count() == 0:
        db.session.add_all([
            Patient(first_name='Oleg', last_name='Melnyk', phone='111'),
            Patient(first_name='Anna', last_name='Ivanova', phone='222'),
            Patient(first_name='Dima', last_name='Petrov', phone='333'),
            Patient(first_name='Ira', last_name='Koval', phone='444'),
            Patient(first_name='Max', last_name='Bondar', phone='555'),
        ])

    if Appointment.query.count() == 0:
        db.session.add_all([
            Appointment(doctor_id=1, patient_id=1),
            Appointment(doctor_id=2, patient_id=2),
            Appointment(doctor_id=3, patient_id=3),
            Appointment(doctor_id=1, patient_id=4),
            Appointment(doctor_id=2, patient_id=5),
        ])

    db.session.commit()


def paginate(query):
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 5, type=int)

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return {
        "data": [item.to_dict() for item in pagination.items],
        "meta": {
            "page": page,
            "total": pagination.total,
            "pages": pagination.pages
        }
    }



@app.route('/api/patients')
def get_patients():
    search = request.args.get('search', '')

    query = Patient.query
    if search:
        query = query.filter(Patient.first_name.contains(search))

    return jsonify(paginate(query))


@app.route('/api/patients/<int:id>')
def get_patient(id):
    patient = Patient.query.get_or_404(id)
    return jsonify(patient.to_dict())


@app.route('/api/doctors')
def get_doctors():
    return jsonify(paginate(Doctor.query))


@app.route('/api/doctors/<int:id>')
def get_doctor(id):
    doctor = Doctor.query.get_or_404(id)
    return jsonify(doctor.to_dict())


@app.route('/api/appointments')
def get_appointments():
    search = request.args.get('search', '')

    query = Appointment.query.join(Patient).join(Doctor)
    if search:
        query = query.filter(
            Patient.first_name.contains(search) |
            Doctor.first_name.contains(search)
        )

    return jsonify(paginate(query))


@app.route('/api/appointments/<int:id>')
def get_appointment(id):
    appt = Appointment.query.get_or_404(id)
    return jsonify(appt.to_dict())


@app.route('/api/patients', methods=['POST'])
def create_patient():
    data = request.json

    if not data or not data.get('first_name') or not data.get('last_name'):
        return jsonify({"error": "Invalid data"}), 400

    patient = Patient(
        first_name=data['first_name'],
        last_name=data['last_name'],
        phone=data.get('phone', '')
    )

    db.session.add(patient)
    db.session.commit()

    return jsonify(patient.to_dict()), 201


@app.route('/api/patients/<int:id>', methods=['PUT'])
def update_patient(id):
    patient = Patient.query.get_or_404(id)
    data = request.json

    if not data:
        return jsonify({"error": "No data"}), 400

    patient.first_name = data.get('first_name', patient.first_name)
    patient.last_name = data.get('last_name', patient.last_name)
    patient.phone = data.get('phone', patient.phone)

    db.session.commit()

    return jsonify(patient.to_dict())


@app.route('/api/patients/<int:id>', methods=['DELETE'])
def delete_patient(id):
    patient = Patient.query.get_or_404(id)

    db.session.delete(patient)
    db.session.commit()

    return jsonify({"message": "Deleted"})


@app.route('/api/stats')
def stats():
    total_patients = Patient.query.count()
    total_doctors = Doctor.query.count()
    total_appointments = Appointment.query.count()

    avg_per_doctor = total_appointments / total_doctors if total_doctors else 0

    return jsonify({
        "patients": total_patients,
        "doctors": total_doctors,
        "appointments": total_appointments,
        "avg_appointments_per_doctor": avg_per_doctor
    })


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        init()

    app.run(debug=True)