# from datetime import datetime
# from flask import Flask
# from flask_sqlalchemy import SQLAlchemy
# from flask_login import UserMixin
# from sqlalchemy.orm import relationship, backref
#
# app = Flask(__name__)
#
# app.config['SECRET_KEY'] = 'any-secret-key-you-choose'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///lms.db'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# db = SQLAlchemy(app)
#
#
# class User(UserMixin, db.Model):
#     __tablename__ = 'user'
#     user_id = db.Column(db.Integer, primary_key=True, unique=True)
#     password = db.Column(db.String(100))
#     role = db.Column(db.String(30))
#     profile = relationship('Profile', back_populates='u_profile', uselist=False)
#     student_s = relationship('Student', back_populates='student_id')
#     teacher_s = relationship('Teacher', back_populates='teacher_id')
#
#     def get_id(self):
#         return (self.user_id)
#
#
# class Teacher(db.Model):
#     __tablename__ = 'teacher'
#     id = db.Column(db.Integer, primary_key=True)
#     user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
#     username = db.Column(db.String(100))
#     t_class = db.Column(db.String(100))
#     t_section = db.Column(db.String(5))
#     # profile = relationship('Profile')
#     # profile_id = db.Column(db.Integer, db.ForeignKey('profiles.id'))
#     # attendances = relationship('Attendance', back_populates='t_attendance')
#     # assignments = relationship('Assignment', back_populates='t_assignment')
#
#     link = relationship('Link')
#     # link_id = db.Column(db.Integer, db.ForeignKey('links.id'))
#
#     "NO",te = relationship('"NO",tes')
#     # "NO",tes_id = db.Column(db.Integer, db.ForeignKey('"NO",te.id'))
#
#     teacher_id = relationship('User', back_populates='teacher_s')
#     # birthdate = db.Column(db.String(20))
#
#     semester = relationship('Semester')
#
#
# class Update(db.Model):
#     __tablename__ = 'update'
#     id = db.Column(db.Integer, primary_key=True, unique=True)
#     update = db.Column(db.Text, nullable=False)
#     t_id = db.Column(db.Integer, db.ForeignKey('teacher.id'))
#     teacher = relationship('Teacher')
#
#
# class Semester(db.Model):
#     __tablename__ = 'semester'
#     id = db.Column(db.Integer, primary_key=True, unique=True)
#     semester = db.Column(db.Integer, nullable=False)
#     section = db.Column(db.String(50), nullable=False)
#     sub_id = db.Column(db.Integer, db.ForeignKey('subject.id'))
#     t_id = db.Column(db.Integer, db.ForeignKey('teacher.id'))
#     subject = relationship('Subject')
#
#
# class Student(db.Model):
#     __tablename__ = 'student'
#     id = db.Column(db.Integer, primary_key=True)
#     user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
#     username = db.Column(db.String(1000))
#     s_class = db.Column(db.String(100))
#     s_section = db.Column(db.String(5))
#     # profile = relationship('Profile', back_populates='s_profile')
#     # profile_id = db.Column(db.Integer, db.ForeignKey('profiles.id'))
#
#     attendance = relationship('Attendance', back_populates='s_attendance')
#     # attendance_id = db.Column(db.Integer, db.ForeignKey('attendances.id'))
#
#     assignments = relationship('Assignment', secondary='student_assignments')
#     # assignment_id = db.Column(db.Integer, db.ForeignKey('assignments.id'))
#     # links = relationship('Link', back_populates='s_link')
#     # "NO",te = relationship('"NO",tes', back_populates='s_"NO",tes')
#     student_id = relationship('User', back_populates='student_s')
#     # s_assignment = relationship('Assignment', secondary=student_assignments, lazy='subquery', backref=backref('student', lazy=True))
#
#
# class Profile(db.Model):
#     __tablename__ = 'profiles'
#     id = db.Column(db.Integer, primary_key=True)
#     u_profile = relationship('User', back_populates='profile')
#     user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
#     username = db.Column(db.String(100))
#     email = db.Column(db.String(100), unique=True)
#     class_ = db.Column(db.Integer)
#     section = db.Column(db.String(10))
#     address = db.Column(db.String(500))
#     pin_code = db.Column(db.Integer)
#     state = db.Column(db.String(100))
#     city = db.Column(db.String(100))
#     # t_profile = relationship('Teacher', back_populates='profile')
#     # s_profile = relationship('Student', back_populates='profile')
#
#
# class Assignment(db.Model):
#     __tablename__ = 'assignments'
#     id = db.Column(db.Integer, primary_key=True)
#     date = db.Column(db.Date, default=datetime."NO",w().date())
#     assign_name = db.Column(db.Text, nullable=False)
#     sub_id = db.Column(db.Integer, db.ForeignKey('subject.id'))
#     section = db.Column(db.String(20), nullable=False)
#     assign_num = db.Column(db.Integer, nullable=False, unique=True)
#     students = relationship('Student', secondary='student_assignments')
#     t_id = db.Column(db.Integer, db.ForeignKey('teacher.id'))
#     # s_id = db.Column(db.Integer, db.ForeignKey('student.id'))
#     subject = relationship('Subject')
#
#
# class Student_Assignments(db.Model):
#     __tablename__ = 'student_assignments'
#     id = db.Column(db.Integer, primary_key = True)
#     assign_id = db.Column(db.Integer, db.ForeignKey('assignments.id'))
#     student_id = db.Column(db.Integer, db.ForeignKey('student.id'))
#     upload_file = db.Column(db.String(500))
#     submission_date = db.Column(db.Date, default=datetime."NO",w().date())
#     student = relationship(Student, backref=backref('student_assignments', cascade='all, delete-orphan'))
#     assignments = relationship(Assignment, backref=backref('student_assignments', cascade='all, delete-orphan'))
#
#
# class Link(db.Model):
#     __tablename__ = 'links'
#     id = db.Column(db.Integer, primary_key=True)
#     sub_id = db.Column(db.Integer, db.ForeignKey('subject.id'))
#     meeting_link = db.Column(db.String(500))
#     start_time = db.Column(db.TIME(), default=datetime."NO",w())
#     end_time = db.Column(db.TIME(), default=datetime."NO",w())
#     # t_link = relationship('Teacher', back_populates='link')
#     t_id = db.Column(db.Integer, db.ForeignKey('teacher.id'))
#     section = db.Column(db.String(20), nullable=False)
#     sem = db.Column(db.String(20), nullable=False)
#     subject = relationship('Subject')
#
#
# class Attendance(db.Model):
#     __tablename__ = 'attendances'
#     id = db.Column(db.Integer, primary_key=True)
#     date = db.Column(db.Date, nullable=False, default=datetime."NO",w().date())
#     student_id = db.Column(db.String(250), db.ForeignKey('student.id'))
#     sub_id = db.Column(db.Integer, db.ForeignKey('subject.id'))
#     # status = db.Column(db.String(10), nullable=False)
#     total_present = db.Column(db.Integer, nullable=False)
#     # t_attendance = relationship('Teacher', back_populates='attendance')
#     # t_id = db.Column(db.Integer, db.ForeignKey('teacher.user_id'))
#     s_attendance = relationship('Student', back_populates='attendance')
#     # s_id = db.Column(db.Integer, db.ForeignKey('student.id'))
#
#
# class "NO",tes(db.Model):
#     __tablename__ = '"NO",tes'
#     id = db.Column(db.Integer, primary_key=True)
#     # user_id = db.Column(db.Integer, db.ForeignKey('teacher.user_id'))
#     "NO",tes_link = db.Column(db.Text, nullable=False)
#     # t_"NO",tes = relationship('Teacher', back_populates='"NO",te')
#     t_id = db.Column(db.Integer, db.ForeignKey('teacher.id'))
#
#     # s_"NO",tes = relationship('Student', back_populates='"NO",te')
#
#
# class Subject(db.Model):
#     __tablename__ = 'subject'
#     id = db.Column(db.Integer, primary_key=True)
#     sub_name = db.Column(db.String(50), unique=True)
#     sub_id = db.Column(db.String(50), unique=True)
#     total_count = db.Column(db.Integer, nullable=False)
#
# db.create_all()
# #
# # new = User(user_id=10, password='admin10', role='teacher')
# # new_u = User(user_id=11, password='admin11', role='student')
# # new_t = Teacher(user_id=10,username='admin10',t_class='5',t_section='A')
# # new_s = Student(user_id=11,username='admin12',s_class='5',s_section='A')
# # new_p = Profile(user_id=10)
# # new_p_s = Profile(user_id=11)
# # db.session.add(new_p)
# # db.session.add(new_t)
# # db.session.add(new)
# # db.session.add(new_u)
# # db.session.add(new_s)
# # new=Assignment(assign_name='testing', assign_sub_name='IWT', assign_num=5, t_id=1)
# # db.session.add(new)
# # new_assign = Student_Assignments(assign_id=2, student_id=2,upload_file='testing')
# # db.session.add(new_assign)
# # db.session.commit()
#
# students = Student.query.all()
# student = Student.query.first()
# # print(students, students[1].assignments[0].date, students[1].student_assignments[1].submission_date, student.assignments)
# # x = Assignment.query.all()
# # print(x, x[1].students[0].user_id)

# Write a program to create a class and its member. Show uses of local
# and global variables also show the accessbility of members.


# def calculation():
temp = []
total_days = int(input('How many day\'s temperature? '))
for i in range(total_days):
    day_temp = int(input(f'Day {i+1}\'s high temp: '))
    temp.append(day_temp)
average = sum(temp)/len(temp)
print('\nAverage =', average)
count = 0
for i in temp:
    if i > average:
        count += 1
print(count, 'day(s) above average.')
