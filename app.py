from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///clinic.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class Doctor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))

class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    phone = db.Column(db.String(20))


def init():
    if Patient.query.count() == 0:
        db.session.add_all([
            Patient(first_name='Oleg', last_name='Melnyk', phone='111'),
            Patient(first_name='Anna', last_name='Ivanova', phone='222'),
            Patient(first_name='Dima', last_name='Petrov', phone='333'),
            Patient(first_name='Ira', last_name='Koval', phone='444'),
            Patient(first_name='Max', last_name='Bondar', phone='555'),
        ])
        db.session.commit()


@app.route('/')
def index():
    return render_template('index.html',
        patients=Patient.query.count(),
        doctors=Doctor.query.count()
    )

@app.route('/patients')
def patients():
    q = request.args.get('q', '')
    query = Patient.query

    if q:
        query = query.filter(Patient.first_name.contains(q))

    data = query.all()
    return render_template('patients.html', patients=data)

@app.route('/patient/<int:id>')
def detail(id):
    p = Patient.query.get_or_404(id)
    return render_template('patient_detail.html', p=p)


@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        p = Patient(
            first_name=request.form['first_name'],
            last_name=request.form['last_name'],
            phone=request.form['phone']
        )
        db.session.add(p)
        db.session.commit()
        return redirect('/patients')

    return render_template('form.html', p=None)


@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    p = Patient.query.get_or_404(id)

    if request.method == 'POST':
        p.first_name = request.form['first_name']
        p.last_name = request.form['last_name']
        p.phone = request.form['phone']
        db.session.commit()
        return redirect('/patients')

    return render_template('form.html', p=p)


@app.route('/delete/<int:id>')
def delete(id):
    p = Patient.query.get_or_404(id)
    db.session.delete(p)
    db.session.commit()
    return redirect('/patients')


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        init()
    app.run(debug=True)