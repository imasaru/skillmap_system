from tableapp import db
from sqlalchemy.dialects.postgresql import JSON  # PostgreSQLを使う場合
from datetime import date

class AdminData(db.Model):
    __tablename__ = 'admin_data'
    id = db.Column(db.Integer, primary_key=True)
    admin_num = db.Column(db.Integer, unique=True, nullable=False)
    name = db.Column(db.String(255))
    email = db.Column(db.String(255))

class EmployeeData(db.Model):
    __tablename__ = 'employee_data'
    id = db.Column(db.Integer, primary_key=True)
    employee_num = db.Column(db.Integer, unique=True, nullable=False)
    name = db.Column(db.String(255))
    email = db.Column(db.String(255))
    company = db.Column(db.String(255))
    division = db.Column(db.String(255))
    unit = db.Column(db.String(255))
    subunit_team = db.Column(db.String(255))
    rank = db.Column(db.String(255))
    date_of_join = db.Column(db.Date)
    evaluation_target = db.Column(JSON, default=[])  # JSONフィールドとして定義
    pending_skills = db.relationship('PendingSkill', back_populates='employee', cascade='all, delete-orphan')
    pending_qualifications = db.relationship('PendingQualification', back_populates='employee', cascade='all, delete-orphan')
    pending_trainings = db.relationship('PendingTraining', back_populates='employee', cascade='all, delete-orphan')
    registration_history = db.relationship('RegistrationHistory', back_populates='employee', cascade='all, delete-orphan')
    employee_skills = db.relationship('EmployeeSkill', back_populates='employee', cascade='all, delete-orphan')
    employee_qualifications = db.relationship('EmployeeQualification', back_populates='employee', cascade='all, delete-orphan')
    employee_trainings = db.relationship('EmployeeTraining', back_populates='employee', cascade='all, delete-orphan')

class SkillList(db.Model):
    __tablename__ = 'skill_list'
    id = db.Column(db.Integer, primary_key=True)
    skill_name = db.Column(db.String(255))
    prof_level_1 = db.Column(db.String(255))
    prof_level_2 = db.Column(db.String(255))
    prof_level_3 = db.Column(db.String(255))
    prof_level_4 = db.Column(db.String(255))
    prof_level_5 = db.Column(db.String(255))
    employee_skills = db.relationship('EmployeeSkill', back_populates='skill', cascade='all, delete-orphan')
    
class QualificationList(db.Model):
    __tablename__ = 'qualification_list'
    id = db.Column(db.Integer, primary_key=True)
    qualification_name = db.Column(db.String(255))
    employee_qualifications = db.relationship('EmployeeQualification', back_populates='qualification', cascade='all, delete-orphan')

class TrainingList(db.Model):
    __tablename__ = 'training_list'
    id = db.Column(db.Integer, primary_key=True)
    training_name = db.Column(db.String(255))
    employee_trainings = db.relationship('EmployeeTraining', back_populates='training', cascade='all, delete-orphan')

class EmployeeSkill(db.Model):
    __tablename__ = 'employee_skill'
    id = db.Column(db.Integer, primary_key=True)
    employee_num = db.Column(db.Integer, db.ForeignKey('employee_data.employee_num'), nullable=False)
    skill_id = db.Column(db.Integer, db.ForeignKey('skill_list.id'), nullable=False)
    level = db.Column(db.Integer)
    skill = db.relationship('SkillList', back_populates='employee_skills')
    employee = db.relationship('EmployeeData', back_populates='employee_skills')

class EmployeeQualification(db.Model):
    __tablename__ = 'employee_qualification'
    id = db.Column(db.Integer, primary_key=True)
    employee_num = db.Column(db.Integer, db.ForeignKey('employee_data.employee_num'), nullable=False)
    qualification_id = db.Column(db.Integer, db.ForeignKey('qualification_list.id'), nullable=False)
    newacq_renewal = db.Column(db.String(255))
    acq_renew_date = db.Column(db.Date)
    expiry_date = db.Column(db.Date)
    qualification = db.relationship('QualificationList', back_populates='employee_qualifications')
    employee = db.relationship('EmployeeData', back_populates='employee_qualifications')

class EmployeeTraining(db.Model):
    __tablename__ = 'employee_training'
    id = db.Column(db.Integer, primary_key=True)
    employee_num = db.Column(db.Integer, db.ForeignKey('employee_data.employee_num'), nullable=False)
    training_id = db.Column(db.Integer, db.ForeignKey('training_list.id'), nullable=False)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    training = db.relationship('TrainingList', back_populates='employee_trainings')
    employee = db.relationship('EmployeeData', back_populates='employee_trainings')

class PendingSkill(db.Model):
    __tablename__ = 'pending_skill'
    id = db.Column(db.Integer, primary_key=True)
    employee_num = db.Column(db.Integer, db.ForeignKey('employee_data.employee_num'), nullable=False)
    skill_name = db.Column(db.String(255))
    level = db.Column(db.Integer)
    submitted_date = db.Column(db.Date, default=date.today)
    employee = db.relationship('EmployeeData', back_populates='pending_skills')

class PendingQualification(db.Model):
    __tablename__ = 'pending_qualification'
    id = db.Column(db.Integer, primary_key=True)
    employee_num = db.Column(db.Integer, db.ForeignKey('employee_data.employee_num'), nullable=False)
    qualification_name = db.Column(db.String(255))
    newacq_renewal = db.Column(db.String(255))
    acq_renew_date = db.Column(db.Date)
    expiry_date = db.Column(db.Date)
    submitted_date = db.Column(db.Date, default=date.today)
    employee = db.relationship('EmployeeData', back_populates='pending_qualifications')

class PendingTraining(db.Model):
    __tablename__ = 'pending_training'
    id = db.Column(db.Integer, primary_key=True)
    employee_num = db.Column(db.Integer, db.ForeignKey('employee_data.employee_num'), nullable=False)
    training_name = db.Column(db.String(255))
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    submitted_date = db.Column(db.Date, default=date.today)
    employee = db.relationship('EmployeeData', back_populates='pending_trainings')

class RegistrationHistory(db.Model):
    __tablename__ = 'registration_history'
    id = db.Column(db.Integer, primary_key=True)
    employee_num = db.Column(db.Integer, db.ForeignKey('employee_data.employee_num'), nullable=False)
    action_type = db.Column(db.String(255))  # 'Skill', 'Qualification', 'Training'
    action_detail = db.Column(db.String(255))  # Detailed description (e.g., 'Python Level 3')
    status = db.Column(db.String(50))  # '申請中', '承認', '拒否'
    date = db.Column(db.Date, default=date.today)
    employee = db.relationship('EmployeeData', back_populates='registration_history')