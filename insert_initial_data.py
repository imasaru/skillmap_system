# insert_initial_data.py
from tableapp import db, app
from tableapp.models.skillmap import AdminData, EmployeeData, SkillList, QualificationList, EmployeeSkill, EmployeeQualification, TrainingList, EmployeeTraining, PendingSkill, PendingQualification, PendingTraining, RegistrationHistory
from datetime import date
import random

# アプリケーションの secret_key を設定
app.secret_key = 'secretsecret'

# アプリケーションのコンテキストを作成
with app.app_context():
    # データベースの初期化（既存のデータを削除）
    db.drop_all()
    db.create_all()

    # 初期データの挿入
    admin1 = AdminData(admin_num=123, name='Admin One', email='admin1@example.com')
    admin1.set_password(str(123))  # Convert to string

    admin2 = AdminData(admin_num=456, name='Admin Two', email='admin2@example.com')
    admin2.set_password(str(456))  # Convert to string

    db.session.add(admin1)
    db.session.add(admin2)

    # Create 30 employees
    employees = []
    for i in range(1, 31):
        employee = EmployeeData(
            employee_num=i,
            name=f'Employee {i}',
            email=f'emp{i}@example.com',
            company=f'Company {chr(65 + (i % 3))}',
            division=f'Division {chr(65 + (i % 3))}',
            unit=f'Unit {chr(65 + (i % 3))}',
            subunit_team=f'Team {chr(65 + (i % 3))}',
            rank=f'Rank {chr(65 + (i % 5))}',
            date_of_join=date(2020, 1, 1),  # Set a fixed date for the date_of_join field for all employees
            evaluation_target=[j for j in range(1, 31) if j != i and random.random() > 0.8]  # Randomly assign evaluation targets
        )
        employee.set_password(str(i))  # Convert to string
        employees.append(employee)
        db.session.add(employee)

    # Skills
    skill1 = SkillList(skill_name='Python', prof_level_1='Basic', prof_level_2='Intermediate', prof_level_3='Advanced', prof_level_4='Expert', prof_level_5='Master')
    skill2 = SkillList(skill_name='Data Analysis', prof_level_1='Basic', prof_level_2='Intermediate', prof_level_3='Advanced', prof_level_4='Expert', prof_level_5='Master')
    skill3 = SkillList(skill_name='Project Management', prof_level_1='Basic', prof_level_2='Intermediate', prof_level_3='Advanced', prof_level_4='Expert', prof_level_5='Master')

    db.session.add(skill1)
    db.session.add(skill2)
    db.session.add(skill3)
    db.session.commit()  # Commit to get IDs

    # Qualifications
    cert1 = QualificationList(qualification_name='PMP')
    cert2 = QualificationList(qualification_name='AWS Certified')
    cert3 = QualificationList(qualification_name='Certified Data Scientist')

    db.session.add(cert1)
    db.session.add(cert2)
    db.session.add(cert3)
    db.session.commit()  # Commit to get IDs

    # Trainings
    training1 = TrainingList(training_name='Leadership Training')
    training2 = TrainingList(training_name='Technical Writing')
    training3 = TrainingList(training_name='Machine Learning Workshop')

    db.session.add(training1)
    db.session.add(training2)
    db.session.add(training3)
    db.session.commit()  # Commit to get IDs

    # Employee Skills, Qualifications, and Trainings
    for employee in employees:
        skill_level = random.randint(1, 5)
        employee_skill = EmployeeSkill(employee_num=employee.employee_num, skill_id=random.choice([skill1.id, skill2.id, skill3.id]), level=skill_level)
        db.session.add(employee_skill)
        
        qualification_id = random.choice([cert1.id, cert2.id, cert3.id])
        employee_qualification = EmployeeQualification(
            employee_num=employee.employee_num,
            qualification_id=qualification_id,
            newacq_renewal=random.choice(['new', 'renewal']),
            acq_renew_date=date(2020, 1, 1),
            expiry_date=date(2023, 1, 1)
        )
        db.session.add(employee_qualification)
        
        training_id = random.choice([training1.id, training2.id, training3.id])
        employee_training = EmployeeTraining(
            employee_num=employee.employee_num,
            training_id=training_id,
            start_date=date(2021, 6, 1),
            end_date=date(2021, 6, 5)
        )
        db.session.add(employee_training)

    # Pending Skills, Qualifications, and Trainings
    pending_skill1 = PendingSkill(employee_num=1, skill_id=skill1.id, level=2, submitted_date=date(2023, 5, 1))
    pending_skill2 = PendingSkill(employee_num=2, skill_id=skill2.id, level=1, submitted_date=date(2023, 5, 2))

    pending_qual1 = PendingQualification(employee_num=1, qualification_id=cert1.id, newacq_renewal='new', acq_renew_date=date(2023, 4, 1), expiry_date=date(2026, 4, 1))
    pending_qual2 = PendingQualification(employee_num=2, qualification_id=cert2.id, newacq_renewal='renewal', acq_renew_date=date(2023, 4, 15), expiry_date=date(2026, 4, 15))

    pending_training1 = PendingTraining(employee_num=1, training_id=training1.id, start_date=date(2023, 6, 1), end_date=date(2023, 6, 5))
    pending_training2 = PendingTraining(employee_num=2, training_id=training2.id, start_date=date(2023, 7, 10), end_date=date(2023, 7, 15))

    db.session.add(pending_skill1)
    db.session.add(pending_skill2)
    db.session.add(pending_qual1)
    db.session.add(pending_qual2)
    db.session.add(pending_training1)
    db.session.add(pending_training2)

    # Registration History
    registration_history1 = RegistrationHistory(employee_num=1, action_type='Skill', action_detail=f'{skill1.skill_name} Level 2', status='申請', date=date(2023, 5, 1))
    registration_history2 = RegistrationHistory(employee_num=2, action_type='Skill', action_detail=f'{skill2.skill_name} Level 1', status='申請', date=date(2023, 5, 2))
    registration_history3 = RegistrationHistory(employee_num=1, action_type='Qualification', action_detail=cert1.qualification_name, status='申請', date=date(2023, 4, 1))
    registration_history4 = RegistrationHistory(employee_num=2, action_type='Qualification', action_detail=cert2.qualification_name, status='申請', date=date(2023, 4, 15))
    registration_history5 = RegistrationHistory(employee_num=1, action_type='Training', action_detail=training1.training_name, status='申請', date=date(2023, 6, 1))
    registration_history6 = RegistrationHistory(employee_num=2, action_type='Training', action_detail=training2.training_name, status='申請', date=date(2023, 7, 10))

    db.session.add(registration_history1)
    db.session.add(registration_history2)
    db.session.add(registration_history3)
    db.session.add(registration_history4)
    db.session.add(registration_history5)
    db.session.add(registration_history6)

    # Commit session
    db.session.commit()

    # Additional data to cover all test cases
    # Employee 31 to Employee 38 to cover all combinations
    for i in range(31, 39):
        employee = EmployeeData(
            employee_num=i,
            name=f'Employee {i}',
            email=f'emp{i}@example.com',
            company=f'Company {chr(65 + (i % 3))}',
            division=f'Division {chr(65 + (i % 3))}',
            unit=f'Unit {chr(65 + (i % 3))}',
            subunit_team=f'Team {chr(65 + (i % 3))}',
            rank=f'Rank {chr(65 + (i % 5))}',
            date_of_join=date(2020, 1, 1)
        )
        employee.set_password(str(i))  # Convert to string
        db.session.add(employee)

        # Assign specific skills, qualifications, and trainings to cover all combinations
        employee_skill = EmployeeSkill(employee_num=employee.employee_num, skill_id=skill1.id, level=5)
        db.session.add(employee_skill)
        
        employee_qualification = EmployeeQualification(
            employee_num=employee.employee_num,
            qualification_id=cert1.id,
            newacq_renewal='new',
            acq_renew_date=date(2020, 1, 1),
            expiry_date=date(2023, 1, 1)
        )
        db.session.add(employee_qualification)
        
        employee_training = EmployeeTraining(
            employee_num=employee.employee_num,
            training_id=training1.id,
            start_date=date(2021, 6, 1),
            end_date=date(2021, 6, 5)
        )
        db.session.add(employee_training)

    # Commit session for additional data
    db.session.commit()