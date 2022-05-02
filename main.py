import os
from functools import wraps
from flask import Flask, render_template, url_for, redirect, flash, request, Blueprint, session, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc, or_, and_
from werkzeug.exceptions import abort
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from sqlalchemy.orm import relationship, backref
from datetime import datetime, time
from werkzeug.utils import secure_filename


app = Flask(__name__)
data = {}
teacher_data = {}
subjects = []
ALLOWED_EXTENSIONS = {'pdf'}
app.config['SECRET_KEY'] = 'any-secret-key-you-choose'
app.config['UPLOAD_FOLDER'] = "static/uploads/"
# app.config['FILES'] = '../static/uploads'
app.config['MAX_CONTENT_PATH'] = 5 * 1000 * 1000
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///authentication.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///lms.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


class User(UserMixin, db.Model):
    __tablename__ = 'user'
    user_id = db.Column(db.Integer, primary_key=True, unique=True)
    password = db.Column(db.String(100))
    role = db.Column(db.String(30))
    profile = relationship('Profile', back_populates='u_profile', uselist=False)
    student_s = relationship('Student', back_populates='student_id')
    teacher_s = relationship('Teacher', back_populates='teacher_id')

    def get_id(self):
        return (self.user_id)


class Teacher(db.Model):
    __tablename__ = 'teacher'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    username = db.Column(db.String(100))
    t_class = db.Column(db.String(100))
    t_section = db.Column(db.String(5))
    # profile = relationship('Profile')
    # profile_id = db.Column(db.Integer, db.ForeignKey('profiles.id'))
    # attendances = relationship('Attendance', back_populates='t_attendance')
    # assignments = relationship('Assignment', back_populates='t_assignment')

    link = relationship('Link')
    # link_id = db.Column(db.Integer, db.ForeignKey('links.id'))

    note = relationship('Notes')
    # notes_id = db.Column(db.Integer, db.ForeignKey('note.id'))

    teacher_id = relationship('User', back_populates='teacher_s')
    # birthdate = db.Column(db.String(20))

    semester = relationship('Semester')


class Update(db.Model):
    __tablename__ = 'update'
    id = db.Column(db.Integer, primary_key=True, unique=True)
    update = db.Column(db.Text, nullable=False)
    t_id = db.Column(db.Integer, db.ForeignKey('teacher.id'))
    teacher = relationship('Teacher')


class Semester(db.Model):
    __tablename__ = 'semester'
    id = db.Column(db.Integer, primary_key=True, unique=True)
    semester = db.Column(db.Integer, nullable=False)
    section = db.Column(db.String(50), nullable=False)
    sub_id = db.Column(db.Integer, db.ForeignKey('subject.id'))
    t_id = db.Column(db.Integer, db.ForeignKey('teacher.id'))
    subject = relationship('Subject')


class Student(db.Model):
    __tablename__ = 'student'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    username = db.Column(db.String(1000))
    s_class = db.Column(db.String(100))
    s_section = db.Column(db.String(5))
    # profile = relationship('Profile', back_populates='s_profile')
    # profile_id = db.Column(db.Integer, db.ForeignKey('profiles.id'))

    attendance = relationship('Attendance', back_populates='s_attendance')
    # attendance_id = db.Column(db.Integer, db.ForeignKey('attendances.id'))

    assignments = relationship('Assignment', secondary='student_assignments')
    # assignment_id = db.Column(db.Integer, db.ForeignKey('assignments.id'))
    # links = relationship('Link', back_populates='s_link')
    # note = relationship('Notes', back_populates='s_notes')
    student_id = relationship('User', back_populates='student_s')
    # s_assignment = relationship('Assignment', secondary=student_assignments, lazy='subquery', backref=backref('student', lazy=True))


class Profile(db.Model):
    __tablename__ = 'profiles'
    id = db.Column(db.Integer, primary_key=True)
    u_profile = relationship('User', back_populates='profile')
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    username = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    sem = db.Column(db.Integer)
    contact = db.Column(db.Integer)
    section = db.Column(db.String(10))
    address = db.Column(db.String(500))
    pin_code = db.Column(db.Integer)
    state = db.Column(db.String(100))
    city = db.Column(db.String(100))
    # t_profile = relationship('Teacher', back_populates='profile')
    # s_profile = relationship('Student', back_populates='profile')


class Assignment(db.Model):
    __tablename__ = 'assignments'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, default=datetime.now().date())
    assign_name = db.Column(db.Text, nullable=False)
    sub_id = db.Column(db.Integer, db.ForeignKey('subject.id'))
    section = db.Column(db.String(20), nullable=False)
    # assign_num = db.Column(db.Integer, nullable=False, unique=True)
    students = relationship('Student', secondary='student_assignments')
    t_id = db.Column(db.Integer, db.ForeignKey('teacher.id'))
    # s_id = db.Column(db.Integer, db.ForeignKey('student.id'))
    subject = relationship('Subject')


class Student_Assignments(db.Model):
    __tablename__ = 'student_assignments'
    id = db.Column(db.Integer, primary_key = True)
    assign_id = db.Column(db.Integer, db.ForeignKey('assignments.id'))
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'))
    upload_file = db.Column(db.String(500))
    submission_date = db.Column(db.Date, default=datetime.now().date())
    student = relationship(Student, backref=backref('student_assignments', cascade='all, delete-orphan'))
    assignments = relationship(Assignment, backref=backref('student_assignments', cascade='all, delete-orphan'))


class Link(db.Model):
    __tablename__ = 'links'
    id = db.Column(db.Integer, primary_key=True)
    sub_id = db.Column(db.Integer, db.ForeignKey('subject.id'))
    meeting_link = db.Column(db.String(500))
    start_time = db.Column(db.TIME(), default=datetime.now())
    end_time = db.Column(db.TIME(), default=datetime.now())
    # t_link = relationship('Teacher', back_populates='link')
    t_id = db.Column(db.Integer, db.ForeignKey('teacher.id'))
    section = db.Column(db.String(20), nullable=False)
    sem = db.Column(db.String(20), nullable=False)
    subject = relationship('Subject')


class Attendance(db.Model):
    __tablename__ = 'attendances'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False, default=datetime.now().date())
    student_id = db.Column(db.String(250), db.ForeignKey('student.id'))
    sub_id = db.Column(db.Integer, db.ForeignKey('subject.id'))
    # status = db.Column(db.String(10), nullable=False)
    total_present = db.Column(db.Integer, nullable=False)
    # t_attendance = relationship('Teacher', back_populates='attendance')
    # t_id = db.Column(db.Integer, db.ForeignKey('teacher.user_id'))
    s_attendance = relationship('Student', back_populates='attendance')
    # s_id = db.Column(db.Integer, db.ForeignKey('student.id'))


class Notes(db.Model):
    __tablename__ = 'notes'
    id = db.Column(db.Integer, primary_key=True)
    # user_id = db.Column(db.Integer, db.ForeignKey('teacher.user_id'))
    notes_link = db.Column(db.Text, nullable=False)
    teacher = relationship('Teacher')
    sub_id = db.Column(db.Integer, db.ForeignKey('subject.id'))
    t_id = db.Column(db.Integer, db.ForeignKey('teacher.id'))
    subject = relationship('Subject')
    # s_notes = relationship('Student', back_populates='note')


class Subject(db.Model):
    __tablename__ = 'subject'
    id = db.Column(db.Integer, primary_key=True)
    sub_name = db.Column(db.String(50), unique=True)
    sub_id = db.Column(db.String(50), unique=True)
    total_count = db.Column(db.Integer, nullable=False)

# db.create_all()


def admin_only(f):
    @wraps(f)
    def inside_function(*args, **kwargs):
        try:
            if not current_user.is_authenticated or current_user.user_id != 16 :
                return abort(403, description='Unauthorized access')
        except AttributeError:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return inside_function


@app.route('/admin-register', methods=['GET','POST'])
@admin_only
def register():
    if request.method == 'POST':
        if request.args.get('role') == 'teacher':
            print(request.form.get('name'), request.form.get('section'), request.form.get('contact number'), request.form.get('semester'), request.form.getlist('subject'))
        else:
            print(request.form.get('name'), request.form.get('section'), request.form.get('contact number'),
             request.form.get('semester'))
        return
    return render_template('register.html')


@app.route('/sign-up', methods=["GET","POST"])
def sign_up():
    if request.method == "POST":
        valid_user = User.query.filter_by(user_id=request.form.get('user_id')).first()
        print(valid_user.password)
        if valid_user != None and valid_user.role == request.form.get('user') and valid_user.password == '' or valid_user.password == None:
            data['user'] = request.form.get('user')
            new_pass = generate_password_hash(request.form.get('password'),
                    method='pbkdf2:sha256',
                    salt_length=8)
            User.query.filter_by(user_id=request.form.get('user_id')).update(dict(
                        user_id=request.form['user_id'],
                        password=new_pass,
                        role=request.form.get('user'))
                    )
            db.session.commit()
            login_user(valid_user)
            cl = request.form.get('user')
            if cl.lower() == 'student' :
                new_entry = Student(
                    username=request.form['username'],
                    user_id=current_user.user_id,
                )
                db.session.add(new_entry)
                db.session.commit()
                for sub_id in range(1,5):
                    new_student_attendance = Attendance(
                            date=datetime.now().date(),
                            student_id=current_user.student_s[0].id,
                            sub_id=sub_id,
                            total_present=0)
                    db.session.add(new_student_attendance)
                    db.session.commit()
            elif cl.lower() == 'teacher':
                new_entry = Teacher(
                    username=request.form['username'],
                    user_id=current_user.user_id,
                )

                db.session.add(new_entry)
                db.session.commit()
            if request.form.get('user').lower() == 'teacher':
                return redirect(url_for('teacher_select', user_id=valid_user.user_id))
            return redirect(url_for(request.form.get('user').lower(), user_id=valid_user.user_id))
        elif valid_user.password != '':
            flash('You have already Signed Up')
            return redirect(url_for('login'))
        else:
            flash('Please enter valid details.')
    return render_template('sign_up.html', sign_up=False)


@app.route('/', methods=["GET","POST"])
def login():
    if request.method == "POST":
        data['user'] = request.form["user"].title()
        data['user_id'] = request.form['user_id']
        data['password'] = request.form['password']
        # print(data)
        # print(data["user"])
        user = User.query.filter_by(user_id=data['user_id']).first()
        print(user)
        if user and user.role == data['user'].lower():
            if check_password_hash(pwhash=user.password, password=data['password']):
            # if user.password == data['password']:
                login_user(user)
                if request.form["user"].lower() == "teacher":
                    return redirect(url_for('teacher_select', user_id=data['user_id']))
                elif request.form["user"].lower() == "admin":
                    return redirect(url_for('register'))
                else:
                    return redirect(url_for('student', user_id=data['user_id']))
            elif user.password == '':
                flash('You are not signed up.')
                return redirect(url_for('sign_up'))
            else:
                flash('Please enter correct password')
        else:
            flash('No such user exists')
        # elif request.form["user"].lower() == "student":
        #     user = Student.query.filter_by(user_id=data['user_id']).first()
        #     if user:
        #         if check_password_hash(pwhash=user.password, password=data['password']):
        #             login_user(user)
        #         else:
        #             flash('Please enter correct password')
    return render_template("login.html", sign_up=True)


@app.route('/student', methods=["GET","POST"])
@login_required
def student():
    if current_user.user_id == int(request.args.get('user_id')):
        user = Student.query.filter_by(user_id=request.args['user_id']).first()
        assignments = Assignment.query.filter_by(section=user.s_section).all()
        assign_count = len(assignments)
        notes = Notes.query.all()
        subjects = Subject.query.all()
        updates = Update.query.all()
        # attendance = Attendance.query.filter_by(student_id=1).all()
        student_total_attendance = 0
        subject_total_count = 0
        for sub in subjects:
            # print(sub.id, sub.sub_name, sub.sub_id, sub.total_count)
            total_count = Subject.query.filter_by(sub_id=sub.sub_id).first().total_count
            # sub_attendance = Attendance.query.filter(Attendance.student_id==1, Attendance.sub_id==sub.id).first()
            subject_total_count += total_count
            try:
                sub_attendance = Attendance.query.filter_by(student_id=user.id, sub_id=sub.id).first().total_present
                student_total_attendance += sub_attendance
            except AttributeError:
                student_total_attendance += 0
        final_attendance = int(student_total_attendance/subject_total_count *100)
        # print(attendance[0].total_present/total_count * 100)
        # print(user.assignments, assignments)
        # print(user.id, type(user.id))
        graph_attendance = Attendance.query.filter_by(student_id=user.id).all()
        sub_total = Subject.query.all()
        show_link = []
        try:
            links = Link.query.filter_by(section=user.s_section).order_by(Link.start_time).all()
            time = str(datetime.now().strftime('%H:%M')).split(':')
            for link in links:
                compare_s = str(link.start_time).split(':')
                compare_e = str(link.end_time).split(':')
                # print(int(compare_s[1]), int(time[1]),int(compare_e[0]), int(time[0]),int(compare_e[0]+compare_e[1]) , int(time[0]+time[1]))
                # print(int(compare_s[0]) <= int(time[0]), int(compare_s[0]+compare_s[1]) >= int(time[0]+time[1]),int(compare_e[0]) >= int(time[0]), int(compare_e[0]+compare_e[1]) >= int(time[0]+time[1]))
                if int(compare_s[0])<=int(time[0]) and int(compare_s[0]+compare_s[1]) <= int(time[0]+time[1]) and int(compare_e[0]) >= int(time[0]) and int(compare_e[0]+compare_e[1]) > int(time[0]+time[1]):
                    # print(link.meeting_link, link.subject.sub_name)
                    show_link = link
                    # print(show_link)
                elif int(compare_e[0]+compare_e[1]) < int(time[0]+time[1]):
                    # print('elif m')
                    db.session.delete(link)
                    db.session.commit()
                else:
                    print('No meeting scheduled')
        except Exception:
            show_link = []
        return render_template('code.html', user=user, show_link=show_link, sub_total=sub_total, graph=graph_attendance, data=data, attendance=final_attendance, assign_count=assign_count, notes_count=len(notes), notes=notes, assignments=assignments, updates=updates, today=datetime.now().date())
    else:
        flash('Unauthorized access')
        return redirect(url_for('logout'))



@app.route('/teacher-select', methods=["GET","POST"])
@login_required
def teacher_select():
    if current_user.user_id == int(request.args['user_id']):
        user = Teacher.query.filter_by(user_id=request.args['user_id']).first()
        assignments = Assignment.query.filter_by(t_id=user.id).all()
        notes = user.note
        all_subjects = Semester.query.filter_by(t_id=user.id).all()
        # sec = []
        # [sec.append(sem.section) for sem in Semester.query.filter_by(t_id=user.id).all() if sem.section not in sec]
        sec = (user.t_section).split(',')
        teacher_data['subject'] = ''
        for subject in all_subjects:
            if subject.subject.sub_name not in subjects:
                subjects.append(subject.subject.sub_name)
        if request.method == 'POST':
            user_answer = request.form['activity']
            print(user_answer)
            return redirect(url_for('teacher', section=request.form['activity'], user_id=current_user.user_id))
        return render_template('teacher_select.html', user_id=request.args['user_id'], user=user, assign_count=len(assignments), notes_count=len(notes), subjects=subjects, sec=sec)
    else:
        flash('Unauthorized access')
        return redirect(url_for('logout'))



@app.route('/<user_id>/<section>', methods=["GET","POST"])
@login_required
def teacher(section,user_id):
    x = [i.strip() for i in current_user.teacher_s[0].t_section.split(',')]
    if current_user.user_id == int(user_id) and section in x:
        user = Teacher.query.filter_by(user_id=user_id).first()
        change = False
        update = Update.query.filter_by(t_id=user.id).all()
        # assignments = Assignment.query.filter_by(t_id=user.id, section=section).order_by(desc(Assignment.assign_num)).all()
        notes = user.note
        # print(Teacher.query.join(Teacher.note).filter_by(id=3).first())
        # print(db.session.query(Semester).join(Teacher).filter(Semester.t_id==user.id, Semester.section=='A').all())
        subjects = Semester.query.filter_by(t_id=user.id, section=section).all()
        given_assignments = Assignment.query.filter_by(section=section, t_id=user.id).all()
        total_students = Student.query.filter_by(s_section=section).all()
        assignments = Student_Assignments.query.join(Student_Assignments.assignments).filter_by(t_id=user.id).join(Student_Assignments.student).filter_by(s_section=section).order_by(desc(Student_Assignments.assign_id)).all()
        # current_assignment = Assignment.query.filter_by(id=1).first()
        current_assignment = False
        print(assignments)
        submitted = 0
        not_sub = 0
        link_created = False
        m_link = []
        print('1 td', teacher_data.get('subject'))
        links = Link.query.filter_by(section=section).order_by(Link.start_time).all()
        time = str(datetime.now().strftime('%H:%M')).split(':')
        print(links, Link.query.all())
        for link in links:
            compare_e = str(link.end_time).split(':')
            print('for link in links',int(compare_e[0] + compare_e[1]), int(time[0] + time[1]))
            if int(compare_e[0] + compare_e[1]) <= int(time[0] + time[1]):
                db.session.delete(link)
                db.session.commit()
        style=''
        try:
            style = ('#' + teacher_data.get('subject') + '{background-color:black;}')
            assignments = Student_Assignments.query.filter_by(assign_id=request.form['assign_id']).join(Student_Assignments.student).filter_by(
                s_section=section).order_by(desc(Student_Assignments.assign_id)).all()
            current_assignment = Assignment.query.filter_by(id=request.form['assign_id']).first()
            sub_id = (Subject.query.filter_by(sub_name=teacher_data['subject']).first()).id
            m_link = Link.query.filter_by(sem=user.t_class, section=section, sub_id=sub_id).first()

        except:
            pass
        if request.method == 'POST':
            # print(teacher_data.get('subject') == None  , teacher_data.get('subject') != request.form['button'], request.args.get('other_button'))
            try:
                print('line 447 waala', teacher_data, teacher_data.get('subject'))
                if teacher_data.get('subject') == None  or teacher_data.get('subject') != request.form['button'] and request.form['button'] != '' and not request.args.get('other_button'):
                     teacher_data['subject'] = request.form['button']
                print(style)
                print('line 451 waala', teacher_data, teacher_data.get('subject'))
                style = ('#'+('').join(teacher_data.get('subject').split())+'{background-color:black;}')
                print('453',style)
                sub_id = (Subject.query.filter_by(sub_name=teacher_data['subject']).first()).id
            except:
                pass
            # print(teacher_data['subject'])
            if request.args.get('link'):
                sub_id = (Subject.query.filter_by(sub_name=teacher_data['subject']).first()).id
                if request.args.get('meeting_link'):
                    formatted_start_time = datetime.strptime(request.form['stime'], '%H:%M').time()
                    formatted_end_time = datetime.strptime(request.form['etime'], '%H:%M').time()
                    new_entry = Link(sub_id=sub_id,
                                    meeting_link=request.form['mlink'],
                                    start_time=formatted_start_time,
                                    end_time=formatted_end_time,
                                    t_id=user.id,
                                    section=section,
                                    sem=user.t_class)
                    link_created = True
                elif request.args.get('reference_notes'):
                    # sub_id = (Subject.query.filter_by(sub_name=request.form['button']).first()).id
                    new_entry = Notes(notes_link=request.form['notes_link'],
                                      sub_id=sub_id,
                                      t_id=user.id)
                elif request.args.get('update'):
                    new_entry = Update(update=request.form['update'],
                                       t_id=user.id)
                elif request.args.get('assignment'):
                    # sub_id = (Subject.query.filter_by(sub_name=request.form['button']).first()).id
                    new_entry = Assignment(date=datetime.now().date(),assign_name=request.form['assign_name'],
                                           sub_id=sub_id ,section=section,t_id=user.id)
                db.session.add(new_entry)
                db.session.commit()
            print(sub_id)
            given_assignments = Assignment.query.filter_by(section=section, t_id=user.id, sub_id=sub_id).all()
            try:
                assignments = Student_Assignments.query.filter_by(assign_id=request.form['assign_id']).join(Student_Assignments.assignments).filter_by(sub_id=sub_id).join(Student_Assignments.student).filter_by(s_section=section).order_by(desc(Student_Assignments.assign_id)).all()
            except:
                assignments = Student_Assignments.query.join(
                    Student_Assignments.assignments).filter_by(sub_id=sub_id).join(
                    Student_Assignments.student).filter_by(s_section=section).order_by(
                    desc(Student_Assignments.assign_id)).all()
            # print('asts',asts)
            notes = user.note
            update = Update.query.filter_by(t_id=user.id).all()
            try:
                m_link = Link.query.filter_by(sem=user.t_class, section=section, sub_id=sub_id).first()
            except:
                pass
            print(m_link)
            print('3',teacher_data, teacher_data.get('subject'))
            # print(Student_Assignments.query.join(Student_Assignments.assignments).join(Student_Assignments.student).filter_by( s_section=section).all())
            # print('sub', request.form['button'])
            submitted = len(assignments)
            not_sub = len(total_students) - submitted
            print('507',style)
            return render_template('teacher.html', current_assignment=current_assignment, teacher_data=teacher_data.get('subject'), style=style, mlink=m_link, user=user, section=section, updates=update,
                                   link_created=link_created, assign_count=len(given_assignments), given_assignments=given_assignments, change=True, assignments=assignments,
                                   notes_count=len(notes), subjects=subjects, submitted=submitted, not_sub=not_sub, sub_selected=True)
        return render_template('teacher.html', user=user, mlink=m_link, current_assignment=current_assignment, teacher_data=teacher_data.get('subject'), section=section, updates= update, assign_count=len(given_assignments),
                               given_assignments=given_assignments, change=True, assignments=assignments, style=style, notes_count=len(notes), subjects=subjects, submitted=submitted, not_sub=not_sub)
    else:
        flash('Unauthorized access')
        return redirect(url_for('logout'))


@app.route('/edit-profile', methods=['GET','POST'])
@login_required
def edit_profile():
    if current_user.role == 'teacher':
        current_sec = request.args.get('current_sec')
        user = Teacher.query.filter_by(user_id=current_user.user_id).first()
        role = 'teacher'
        sec = []
        subjects = []
        [subjects.append(sem.subject.sub_name) for sem in Semester.query.filter_by(t_id=user.id).all() if sem.subject.sub_name not in subjects]
        [sec.append(sem.section) for sem in Semester.query.filter_by(t_id=user.id).all() if sem.section not in sec]

    elif current_user.role == 'student':
        user = Student.query.filter_by(user_id=current_user.user_id).first()
        role = 'student'
        sec = user.s_section
        current_sec = ''
        subjects=[]
    try:
        profile = Profile.query.filter_by(user_id=user.user_id).first()
    except:
        profile = None
    if request.method == "POST":
        add_profile = Profile(
            user_id=request.form['user_id'],
            username=request.form['name'],
            email=request.form['email'],
            sem=request.form['sem'],
            contact=request.form['contact'],
            address=request.form['address'],
            section=sec,
            pin_code=request.form['pincode'],
            city=request.form['city'],
            state=request.form['state']
        )
        if profile != None:
            try:
                Profile.query.filter_by(user_id=user.user_id).update(dict(
                    email=request.form['email'],
                    contact=request.form['contact'],
                    address=request.form['address'],
                    pin_code=request.form['pincode'],
                    city=request.form['city'],
                    state=request.form['state'])
                )
            except :
                flash('Entered email is already registered.')
                return redirect(url_for('edit_profile', current_sec=current_sec))
        else:
            db.session.add(add_profile)
        db.session.commit()
        if role == 'teacher':
            return redirect(url_for('teacher', user_id=user.user_id, section=current_sec))
        else:
            return redirect(url_for('student', user_id=user.user_id))
    return render_template('edit_profile.html', subjects=subjects, user=user, role=role, current_sec=current_sec, all_sec=sec, profile=profile)


@app.route('/delete', methods=['GET','POST'])
@login_required
def delete():
    print(request.args.get('id'), request.args.get('table'), current_user)
    table = request.args.get('table')
    ids = request.args.get('id')
    if table == 'student_assignments':
        entry = Student_Assignments.query.filter(and_(Student_Assignments.assign_id==int(ids), Student_Assignments.student_id==int(current_user.student_s[0].id))).first()
        # print(entry)
        db.session.delete(entry)
        db.session.commit()
        return redirect(url_for('student', user_id=current_user.user_id))
    if table == 'assignments':
        entry = Assignment.query.get(ids)
        print(entry)
    elif table == 'attendance':
        entry = Attendance.query.get(ids)
    elif table == 'link':
        entry = Link.query.get(ids)
    elif table == 'update':
        entry = Update.query.get(ids)
    print(entry)
    db.session.delete(entry)
    db.session.commit()
    # print(teacher_data)
    return redirect(url_for('teacher', user_id=current_user.user_id, section=request.args.get('section')))


@app.route('/assignment_submission', methods=['GET', 'POST'])
@login_required
def assignment():
    # print(current_user.student_s[0].id)
    # print(request.args.get('assign_id'))
    assign_to_submit = Assignment.query.filter_by(id=request.args.get('assign_id')).first()
    # print(assign_to_submit)
    if request.method == "POST":
        # f = request.files['file']
        # check if the post request has the file part
        print(request.files)
        if 'file' not in request.files:
            flash('No file part')
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = f'{datetime.now().strftime("%H%M%S")}{secure_filename(file.filename)}'
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            query = Student_Assignments(assign_id=request.args.get('assign_id'),
                                        student_id=current_user.student_s[0].id,
                                        upload_file=filename,
                                        submission_date=datetime.now().date()
                                        )
            db.session.add(query)
            db.session.commit()
            return redirect(url_for('student', user_id=current_user.user_id))
        else:
            flash('Please submit file in PDF format only.')
    return render_template('assignment.html', assignment = assign_to_submit)


@app.route('/preview', methods=['GET', 'POST'])
@login_required
def preview():
    print(request.args.get('student_id'))
    try:
        student_id = current_user.student_s[0].id
    except:
        student_id = request.args.get('student_id')
    # print(current_user.student_s[0].id)
    print(student_id, request.args.get('assign_id'))
    query = Student_Assignments.query.filter_by(id=request.args.get('assign_id'), student_id=student_id).first()
    return send_from_directory('./static/uploads', query.upload_file, mimetype='application/pdf')


@app.route('/<section>/<sub_name>/attendance', methods=['GET','POST'])
@login_required
def attendance(section, sub_name):
    students = Student.query.filter_by(s_section=section).all()
    sub_id = Subject.query.filter_by(sub_name=sub_name).first().id
    print(sub_id)
    print(students)
    if request.method == "POST":
        total_count = (Subject.query.filter_by(id=sub_id).first()).total_count + 1
        Subject.query.filter_by(id=sub_id).update(dict(total_count=total_count))
        for student in students:
            total_present = student.attendance[sub_id-1].total_present + int(request.form.get(str(student.user_id)))
            print(student, total_present)
            Attendance.query.filter_by(student_id=student.id, sub_id=sub_id).update(dict(date = datetime.now().date(),total_present = total_present))
            db.session.commit()
            teacher_data['subject'] = sub_name
            return redirect(url_for('teacher', user_id=current_user.user_id, section=section))
    return render_template('attendance.html', students=students, section=section, sub_name=sub_name)

@app.route('/about_us')
@login_required
def about_us():
    return render_template('about.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


if __name__ == "__main__":
    app.run(debug=True)
