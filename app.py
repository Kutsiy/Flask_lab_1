from flask import Flask, render_template, request, redirect, url_for
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

class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    phone = db.Column(db.String(20))
    appointments = db.relationship('Appointment', backref='patient', lazy=True)

class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'), nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)

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
        # 5 random appointments
        db.session.add_all([
            Appointment(doctor_id=1, patient_id=1),
            Appointment(doctor_id=2, patient_id=2),
            Appointment(doctor_id=3, patient_id=3),
            Appointment(doctor_id=1, patient_id=4),
            Appointment(doctor_id=2, patient_id=5),
        ])
    db.session.commit()


@app.route('/')
def index():
    return render_template('index.html',
        patients=Patient.query.count(),
        doctors=Doctor.query.count(),
        appointments=Appointment.query.count()
    )
@app.route('/patients')
def patients():
    page = request.args.get('page', 1, type=int)
    q = request.args.get('q', '')
    query = Patient.query
    if q:
        query = query.filter(Patient.first_name.contains(q))
    pagination = query.paginate(page=page, per_page=5)
    return render_template('patients.html', pagination=pagination, q=q)

@app.route('/patient/<int:id>')
def patient_detail(id):
    p = Patient.query.get_or_404(id)
    return render_template('patient_detail.html', p=p)

@app.route('/add', methods=['GET', 'POST'])
def add_patient():
    if request.method == 'POST':
        p = Patient(
            first_name=request.form['first_name'],
            last_name=request.form['last_name'],
            phone=request.form['phone']
        )
        db.session.add(p)
        db.session.commit()
        return redirect(url_for('patients'))
    return render_template('form.html', p=None)

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_patient(id):
    p = Patient.query.get_or_404(id)
    if request.method == 'POST':
        p.first_name = request.form['first_name']
        p.last_name = request.form['last_name']
        p.phone = request.form['phone']
        db.session.commit()
        return redirect(url_for('patients'))
    return render_template('form.html', p=p)

@app.route('/delete/<int:id>')
def delete_patient(id):
    p = Patient.query.get_or_404(id)
    db.session.delete(p)
    db.session.commit()
    return redirect(url_for('patients'))

@app.route('/doctors')
def doctors():
    page = request.args.get('page', 1, type=int)
    q = request.args.get('q', '')
    query = Doctor.query
    if q:
        query = query.filter(Doctor.first_name.contains(q) | Doctor.last_name.contains(q))
    pagination = query.paginate(page=page, per_page=5)
    return render_template('doctors.html', pagination=pagination, q=q)

@app.route('/doctor/<int:id>')
def doctor_detail(id):
    doctor = Doctor.query.get_or_404(id)
    return render_template('doctor_detail.html', doctor=doctor)

@app.route('/appointments')
def appointments():
    page = request.args.get('page', 1, type=int)
    q = request.args.get('q', '')
    query = Appointment.query.join(Patient).join(Doctor)
    if q:
        query = query.filter(Patient.first_name.contains(q) | Doctor.first_name.contains(q))
    pagination = query.paginate(page=page, per_page=5)
    return render_template('appointments.html', pagination=pagination, q=q)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        init()
    app.run(debug=True)