from flask import Flask, render_template
from datetime import datetime

app = Flask(__name__)

students = [
{
'id': 1,
'name': 'Олена Коваленко',
'group': 'КН-21',
'course': 2,
'gpa': 4.5,
'email': 'kovalenko@college.ua',
'is_active': True,
'subjects': ['Python', 'Бази даних', 'Алгоритми'],
},
{
'id': 2,
'name': 'Андрій Мельник',
'group': 'КН-21',
'course': 2,
'gpa': 3.8,
'email': 'melnyk@college.ua',
'is_active': True,
'subjects': ['Python', 'Веб-технології'],
},
{
'id': 3,
'name': 'Марія Шевченко',
'group': 'КН-22',
'course': 1,
'gpa': 4.9,
'email': 'shevchenko@college.ua',
'is_active': True,
'subjects': ['Вступ до програмування', 'Математика', 'Англійська'],
},
{
'id': 4,
'name': 'Дмитро Бондаренко',
'group': 'КН-20',
'course': 3,
'gpa': 3.2,
'email': 'bondarenko@college.ua',
'is_active': False,
'subjects': ['Операційні системи', 'Мережі'],
},
{
'id': 5,
'name': 'Ірина Ткаченко',
'group': 'КН-22',
'course': 1,
'gpa': 4.1,
'email': 'tkachenko@college.ua',
'is_active': True,
'subjects': ['Вступ до програмування', 'Математика', 'Фізика'],
},
{
'id': 6,
'name': 'Олексій Кравченко',
'group': 'КН-21',
'course': 2,
'gpa': 3.5,
'email': 'kravchenko@college.ua',
'is_active': True,
'subjects': ['Python', 'Бази даних'],
},
]

schedule = {
'Понеділок': [
{'time': '08:30', 'subject': 'Python', 'room': '301', 'type': 'лекція'},
{'time': '10:15', 'subject': 'Бази даних', 'room': '215', 'type': 'практика'},
],
'Вівторок': [
{'time': '08:30', 'subject': 'Алгоритми', 'room': '301', 'type': 'лекція'},
{'time': '10:15', 'subject': 'Англійська', 'room': '118', 'type': 'практика'},
{'time': '12:00', 'subject': 'Веб-технології', 'room': '305', 'type': 'лабораторна'},
],
'Середа': [],
'Четвер': [
{'time': '10:15', 'subject': 'Python', 'room': '305', 'type': 'лабораторна'},
{'time': '12:00', 'subject': 'Математика', 'room': '210', 'type': 'лекція'},
],
"П'ятниця": [
{'time': '08:30', 'subject': 'Бази даних', 'room': '301', 'type': 'лекція'},
],
}

college_info = {
'name': 'Київський фаховий коледж інформаційних технологій',
'short_name': 'КФКІТ',
'founded': 1985,
'address': 'м. Київ, вул. Навчальна, 1',
'phone': '+380 44 123 45 67',
'email': 'info@kfkit.edu.ua',
'departments': [
"Комп'ютерних наук",
'Інформаційних технологій',
'Кібербезпеки',
'Програмної інженерії',
],
}


@app.route('/')
def index():
    return render_template(
        'index.html',
        college=college_info,
        total_students=len(students)
    )

@app.route('/students')
def students_list():
    return render_template('students.html', students=students)

@app.route('/student/<int:student_id>')
def student_detail(student_id):
    student = next((s for s in students if s['id'] == student_id), None)
    return render_template('student.html', student=student)

@app.route('/schedule')
def schedule_view():
    total_lessons = sum(len(lessons) for lessons in schedule.values())
    return render_template(
        'schedule.html',
        schedule=schedule,
        total_lessons=total_lessons
    )

@app.route('/about')
def about():
    age = datetime.now().year - college_info['founded']
    return render_template(
        'about.html',
        info=college_info,
        age=age
    )

if __name__ == "__main__":
    app.run(debug=True)