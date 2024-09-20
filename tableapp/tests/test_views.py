# -*- coding: utf-8 -*-

import unittest
import os
import io
from flask import Flask, session, url_for
from flask_testing import TestCase
from tableapp import app, db
from tableapp.models.skillmap import AdminData, EmployeeData, SkillList, QualificationList, EmployeeSkill, EmployeeQualification, TrainingList, EmployeeTraining, PendingSkill, PendingQualification, PendingTraining, RegistrationHistory
from datetime import datetime, date

class TestViews(TestCase):

    def create_app(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        return app

    def setUp(self):
        db.create_all()
        self.populate_data()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def populate_data(self):
        admin = AdminData(admin_num='admin123')
        admin.set_password('adminpassword')
        db.session.add(admin)

        employee = EmployeeData(employee_num='12345', name='Test Employee', email='test@example.com')
        employee.set_password('password')
        db.session.add(employee)

        skill = SkillList(skill_name='Python')
        qualification = QualificationList(qualification_name='AWS Certified')
        training = TrainingList(training_name='Leadership Training')
        db.session.add(skill)
        db.session.add(qualification)
        db.session.add(training)
        db.session.commit()

        emp_skill = EmployeeSkill(employee_num='12345', skill_id=skill.id, level=3)
        emp_qualification = EmployeeQualification(employee_num='12345', qualification_id=qualification.id, newacq_renewal='new', acq_renew_date=date(2023, 1, 1), expiry_date=date(2024, 1, 1))
        emp_training = EmployeeTraining(employee_num='12345', training_id=training.id, start_date=date(2023, 1, 1), end_date=date(2023, 1, 10))
        db.session.add(emp_skill)
        db.session.add(emp_qualification)
        db.session.add(emp_training)
        db.session.commit()

    def login(self, user_type, num, password):
        if user_type == 'admin':
            return self.client.post('/admin_login', data=dict(admin_num=num, password=password), follow_redirects=True)
        else:
            return self.client.post('/employee_login', data=dict(employee_num=num, password=password), follow_redirects=True)

    # 1. Login Page (6テスト)
    def test_index_initialization(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_employee_login_success(self):
        response = self.login('employee', '12345', 'password')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.location, url_for('my_page', _external=True))

    def test_employee_login_failure(self):
        response = self.login('employee', '12345', 'wrongpassword')
        self.assertIn('パスワードが間違っています'.encode('utf-8'), response.data)

    def test_admin_login_success(self):
        response = self.login('admin', 'admin123', 'adminpassword')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.location, url_for('view_skillmap', _external=True))

    def test_admin_login_failure(self):
        response = self.login('admin', 'admin123', 'wrongpassword')
        self.assertIn('パスワードが間違っています'.encode('utf-8'), response.data)

    def test_logout(self):
        self.login('employee', '12345', 'password')
        response = self.client.get('/logout', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn('ログアウトしました'.encode('utf-8'), response.data)
        self.assertNotIn('user_id', session)

    # 2. View Skill Map Page (8テスト)
    def test_view_skillmap(self):
        self.login('admin', 'admin123', 'adminpassword')
        response = self.client.get('/view_skillmap')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Test Employee'.encode('utf-8'), response.data)
        self.assertIn('Python'.encode('utf-8'), response.data)
        self.assertIn('AWS Certified'.encode('utf-8'), response.data)
        self.assertIn('Leadership Training'.encode('utf-8'), response.data)

    def test_skillmap_skill_display(self):
        self.login('admin', 'admin123', 'adminpassword')
        response = self.client.get('/view_skillmap')
        self.assertIn('Python'.encode('utf-8'), response.data)

    def test_skillmap_qualification_display(self):
        self.login('admin', 'admin123', 'adminpassword')
        response = self.client.get('/view_skillmap')
        self.assertIn('AWS Certified'.encode('utf-8'), response.data)

    def test_skillmap_training_display(self):
        self.login('admin', 'admin123', 'adminpassword')
        response = self.client.get('/view_skillmap')
        self.assertIn('Leadership Training'.encode('utf-8'), response.data)

    def test_skillmap_empty_skill_display(self):
        self.login('admin', 'admin123', 'adminpassword')
        response = self.client.get('/view_skillmap')
        self.assertIn(''.encode('utf-8'), response.data)

    def test_skillmap_empty_qualification_display(self):
        self.login('admin', 'admin123', 'adminpassword')
        response = self.client.get('/view_skillmap')
        self.assertIn(''.encode('utf-8'), response.data)

    def test_skillmap_empty_training_display(self):
        self.login('admin', 'admin123', 'adminpassword')
        response = self.client.get('/view_skillmap')
        self.assertIn(''.encode('utf-8'), response.data)

    def test_skillmap_company_unit_division_display(self):
        self.login('admin', 'admin123', 'adminpassword')
        response = self.client.get('/view_skillmap')
        self.assertIn('company'.encode('utf-8'), response.data)
        self.assertIn('unit'.encode('utf-8'), response.data)
        self.assertIn('division'.encode('utf-8'), response.data)

    # 3. Employee Detail Page (5テスト)
    def test_employee_detail(self):
        self.login('employee', '12345', 'password')
        response = self.client.get('/employee_detail/1')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Test Employee'.encode('utf-8'), response.data)

    def test_employee_detail_not_found(self):
        self.login('employee', '12345', 'password')
        response = self.client.get('/employee_detail/9999')
        self.assertEqual(response.status_code, 404)

    def test_employee_detail_skill_display(self):
        self.login('employee', '12345', 'password')
        response = self.client.get('/employee_detail/1')
        self.assertIn('Python'.encode('utf-8'), response.data)

    def test_employee_detail_qualification_display(self):
        self.login('employee', '12345', 'password')
        response = self.client.get('/employee_detail/1')
        self.assertIn('AWS Certified'.encode('utf-8'), response.data)

    def test_employee_detail_training_display(self):
        self.login('employee', '12345', 'password')
        response = self.client.get('/employee_detail/1')
        self.assertIn('Leadership Training'.encode('utf-8'), response.data)

    # 4. My Page (8テスト)
    def test_my_page_display(self):
        self.login('employee', '12345', 'password')
        response = self.client.get('/my_page')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Test Employee'.encode('utf-8'), response.data)

    def test_my_page_redirect_for_unauthenticated_user(self):
        response = self.client.get('/my_page')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.location, url_for('index', _external=True))

    def test_my_page_skill_display(self):
        self.login('employee', '12345', 'password')
        response = self.client.get('/my_page')
        self.assertIn('Python'.encode('utf-8'), response.data)

    def test_my_page_qualification_display(self):
        self.login('employee', '12345', 'password')
        response = self.client.get('/my_page')
        self.assertIn('AWS Certified'.encode('utf-8'), response.data)

    def test_my_page_training_display(self):
        self.login('employee', '12345', 'password')
        response = self.client.get('/my_page')
        self.assertIn('Leadership Training'.encode('utf-8'), response.data)

    def test_my_page_history_display(self):
        self.login('employee', '12345', 'password')
        history_entry = RegistrationHistory(
            employee_num='12345',
            action_type='Skill',
            action_detail='Python Level 3',
            status='申請',
            date=date.today()
        )
        db.session.add(history_entry)
        db.session.commit()

        response = self.client.get('/my_page')
        self.assertIn('Python Level 3'.encode('utf-8'), response.data)

    def test_my_page_profile_update(self):
        self.login('employee', '12345', 'password')
        response = self.client.post('/my_page', data=dict(
            name='新しい名前',
            email='newemail@example.com',
            company='新しい会社',
            division='新しい部署',
            unit='新しいユニット',
            subunit_team='新しいチーム',
            rank='新しいランク',
            date_of_join='2023-01-01'
        ), follow_redirects=True)
        self.assertIn('従業員情報が適切に更新されました！'.encode('utf-8'), response.data)

    def test_my_page_profile_update_invalid_email(self):
        self.login('employee', '12345', 'password')
        response = self.client.post('/my_page', data=dict(
            name='新しい名前',
            email='invalidemail',
            company='新しい会社',
            division='新しい部署',
            unit='新しいユニット',
            subunit_team='新しいチーム',
            rank='新しいランク',
            date_of_join='2023-01-01'
        ), follow_redirects=True)
        self.assertIn('無効なメールアドレスです'.encode('utf-8'), response.data)

    # 5. Register Page (10テスト)
    def test_register_skill_success(self):
        self.login('employee', '12345', 'password')
        response = self.client.post('/register', data=dict(register_skill=True, skill_id=1, level=3), follow_redirects=True)
        self.assertIn('スキル申請が評価者に送信されました'.encode('utf-8'), response.data)

    def test_register_skill_level_out_of_range(self):
        self.login('employee', '12345', 'password')
        response = self.client.post('/register', data=dict(register_skill=True, skill_id=1, level=6), follow_redirects=True)
        self.assertIn('スキルレベルは１－５の間で選択してください'.encode('utf-8'), response.data)

    def test_register_skill_invalid_skill_id(self):
        self.login('employee', '12345', 'password')
        response = self.client.post('/register', data=dict(register_skill=True, skill_id=9999, level=3), follow_redirects=True)
        self.assertIn('無効なスキルIDです。'.encode('utf-8'), response.data)

    def test_register_qualification_success(self):
        self.login('employee', '12345', 'password')
        response = self.client.post('/register', data=dict(register_qualification=True, qualification_id=1, newacq_renewal='new', acq_renew_date='2023-01-01', expiry_date='2024-01-01'), follow_redirects=True)
        self.assertIn('資格申請が評価者に送信されました'.encode('utf-8'), response.data)

    def test_register_qualification_invalid_qualification_id(self):
        self.login('employee', '12345', 'password')
        response = self.client.post('/register', data=dict(register_qualification=True, qualification_id=9999, newacq_renewal='new', acq_renew_date='2023-01-01', expiry_date='2024-01-01'), follow_redirects=True)
        self.assertIn('無効な資格IDです。'.encode('utf-8'), response.data)

    def test_register_qualification_invalid_date_format(self):
        self.login('employee', '12345', 'password')
        response = self.client.post('/register', data=dict(register_qualification=True, qualification_id=1, newacq_renewal='new', acq_renew_date='invalid-date', expiry_date='2024-01-01'), follow_redirects=True)
        self.assertIn('日付形式が正しくありません'.encode('utf-8'), response.data)

    def test_register_training_success(self):
        self.login('employee', '12345', 'password')
        response = self.client.post('/register', data=dict(register_training=True, training_id=1, start_date='2023-01-01', end_date='2023-01-10'), follow_redirects=True)
        self.assertIn('研修申請が評価者に送信されました'.encode('utf-8'), response.data)

    def test_register_training_invalid_training_id(self):
        self.login('employee', '12345', 'password')
        response = self.client.post('/register', data=dict(register_training=True, training_id=9999, start_date='2023-01-01', end_date='2023-01-10'), follow_redirects=True)
        self.assertIn('無効な研修IDです。'.encode('utf-8'), response.data)

    def test_register_training_invalid_date_format(self):
        self.login('employee', '12345', 'password')
        response = self.client.post('/register', data=dict(register_training=True, training_id=1, start_date='invalid-date', end_date='2023-01-10'), follow_redirects=True)
        self.assertIn('日付形式が正しくありません'.encode('utf-8'), response.data)

    def test_register_training_end_date_before_start_date(self):
        self.login('employee', '12345', 'password')
        response = self.client.post('/register', data=dict(register_training=True, training_id=1, start_date='2023-01-10', end_date='2023-01-01'), follow_redirects=True)
        self.assertIn('終了日が開始日より前の場合、エラーメッセージが表示されること'.encode('utf-8'), response.data)

    # 6. Approve Page (6テスト)
    def test_approve_skill(self):
        self.login('employee', '12345', 'password')
        pending_skill = PendingSkill(employee_num='12345', skill_id=1, level=3, submitted_date=date.today())
        db.session.add(pending_skill)
        db.session.commit()

        response = self.client.post(f'/approve/{pending_skill.id}', data=dict(approve_skill='approve', pending_id=pending_skill.id), follow_redirects=True)
        self.assertIn('スキルが承認されました'.encode('utf-8'), response.data)

    def test_deny_skill(self):
        self.login('employee', '12345', 'password')
        pending_skill = PendingSkill(employee_num='12345', skill_id=1, level=3, submitted_date=date.today())
        db.session.add(pending_skill)
        db.session.commit()

        response = self.client.post(f'/approve/{pending_skill.id}', data=dict(approve_skill='deny', pending_id=pending_skill.id), follow_redirects=True)
        self.assertIn('スキルが拒否されました'.encode('utf-8'), response.data)

    def test_approve_qualification(self):
        self.login('employee', '12345', 'password')
        pending_qualification = PendingQualification(employee_num='12345', qualification_id=1, newacq_renewal='new', acq_renew_date=date(2023, 1, 1), expiry_date=date(2024, 1, 1), submitted_date=date.today())
        db.session.add(pending_qualification)
        db.session.commit()

        response = self.client.post(f'/approve/{pending_qualification.id}', data=dict(approve_qualification='approve', pending_id=pending_qualification.id), follow_redirects=True)
        self.assertIn('資格が承認されました'.encode('utf-8'), response.data)

    def test_deny_qualification(self):
        self.login('employee', '12345', 'password')
        pending_qualification = PendingQualification(employee_num='12345', qualification_id=1, newacq_renewal='new', acq_renew_date=date(2023, 1, 1), expiry_date=date(2024, 1, 1), submitted_date=date.today())
        db.session.add(pending_qualification)
        db.session.commit()

        response = self.client.post(f'/approve/{pending_qualification.id}', data=dict(approve_qualification='deny', pending_id=pending_qualification.id), follow_redirects=True)
        self.assertIn('資格が拒否されました'.encode('utf-8'), response.data)

    def test_approve_training(self):
        self.login('employee', '12345', 'password')
        pending_training = PendingTraining(employee_num='12345', training_id=1, start_date=date(2023, 1, 1), end_date=date(2023, 1, 10), submitted_date=date.today())
        db.session.add(pending_training)
        db.session.commit()

        response = self.client.post(f'/approve/{pending_training.id}', data=dict(approve_training='approve', pending_id=pending_training.id        ), follow_redirects=True)
        self.assertIn('研修が承認されました'.encode('utf-8'), response.data)

    def test_deny_training(self):
        self.login('employee', '12345', 'password')
        pending_training = PendingTraining(employee_num='12345', training_id=1, start_date=date(2023, 1, 1), end_date=date(2023, 1, 10), submitted_date=date.today())
        db.session.add(pending_training)
        db.session.commit()

        response = self.client.post(f'/approve/{pending_training.id}', data=dict(approve_training='deny', pending_id=pending_training.id), follow_redirects=True)
        self.assertIn('研修が拒否されました'.encode('utf-8'), response.data)

    # 7. Training Page (6テスト)
    def test_add_skill(self):
        self.login('admin', 'admin123', 'adminpassword')
        response = self.client.post('/admin/manage_skills_qualifications_trainings', data=dict(add_skill=True, skill_name='新スキル名'), follow_redirects=True)
        self.assertIn('スキルが適切に追加されました'.encode('utf-8'), response.data)

    def test_delete_skill(self):
        self.login('admin', 'admin123', 'adminpassword')
        skill = SkillList(skill_name='新スキル名')
        db.session.add(skill)
        db.session.commit()
        response = self.client.post('/admin/manage_skills_qualifications_trainings', data=dict(delete_skill=True, skill_id=skill.id), follow_redirects=True)
        self.assertIn('スキルが適切に削除されました'.encode('utf-8'), response.data)

    def test_add_qualification(self):
        self.login('admin', 'admin123', 'adminpassword')
        response = self.client.post('/admin/manage_skills_qualifications_trainings', data=dict(add_qualification=True, qualification_name='新資格名'), follow_redirects=True)
        self.assertIn('資格が適切に追加されました'.encode('utf-8'), response.data)

    def test_delete_qualification(self):
        self.login('admin', 'admin123', 'adminpassword')
        qualification = QualificationList(qualification_name='新資格名')
        db.session.add(qualification)
        db.session.commit()
        response = self.client.post('/admin/manage_skills_qualifications_trainings', data=dict(delete_qualification=True, qualification_id=qualification.id), follow_redirects=True)
        self.assertIn('資格が削除されました'.encode('utf-8'), response.data)

    def test_add_training(self):
        self.login('admin', 'admin123', 'adminpassword')
        response = self.client.post('/admin/manage_skills_qualifications_trainings', data=dict(add_training=True, training_name='新研修名'), follow_redirects=True)
        self.assertIn('研修が適切に追加されました'.encode('utf-8'), response.data)

    def test_delete_training(self):
        self.login('admin', 'admin123', 'adminpassword')
        training = TrainingList(training_name='新研修名')
        db.session.add(training)
        db.session.commit()
        response = self.client.post('/admin/manage_skills_qualifications_trainings', data=dict(delete_training=True, training_id=training.id), follow_redirects=True)
        self.assertIn('研修が適切に削除されました'.encode('utf-8'), response.data)

    # 8. Register Member Page (5テスト)
    def test_register_member_success(self):
        self.login('admin', 'admin123', 'adminpassword')
        response = self.client.post('/register_member', data=dict(
            employee_num='67890',
            name='新しい従業員',
            email='newemployee@example.com',
            company='新しい会社',
            division='新しい部署',
            unit='新しいユニット',
            subunit_team='新しいチーム',
            rank='新しいランク',
            date_of_join='2023-01-01',
            evaluation_target=''
        ), follow_redirects=True)
        self.assertIn('従業員が正常に登録されました'.encode('utf-8'), response.data)

    def test_register_member_duplicate_employee_num(self):
        self.login('admin', 'admin123', 'adminpassword')
        response = self.client.post('/register_member', data=dict(
            employee_num='12345',
            name='新しい従業員',
            email='newemployee@example.com',
            company='新しい会社',
            division='新しい部署',
            unit='新しいユニット',
            subunit_team='新しいチーム',
            rank='新しいランク',
            date_of_join='2023-01-01',
            evaluation_target=''
        ), follow_redirects=True)
        self.assertIn('従業員番号が既に存在します'.encode('utf-8'), response.data)

    def test_delete_member(self):
        self.login('admin', 'admin123', 'adminpassword')
        response = self.client.post('/delete_member/12345', follow_redirects=True)
        self.assertIn('従業員が正常に削除されました'.encode('utf-8'), response.data)

    def test_bulk_register_member_success(self):
        self.login('admin', 'admin123', 'adminpassword')
        with open(os.path.join('test_data', 'valid_members.csv'), 'r', encoding='utf-8') as f:
            csv_data = f.read()
        data = {
            'csv_file': (io.StringIO(csv_data), 'valid_members.csv')
        }
        response = self.client.post('/bulk_register_member', data=data, follow_redirects=True)
        self.assertIn('従業員が正常に一括登録されました'.encode('utf-8'), response.data)

    def test_bulk_register_member_invalid_csv(self):
        self.login('admin', 'admin123', 'adminpassword')
        with open(os.path.join('test_data', 'invalid_members.csv'), 'r', encoding='utf-8') as f:
            csv_data = f.read()
        data = {
            'csv_file': (io.StringIO(csv_data), 'invalid_members.csv')
        }
        response = self.client.post('/bulk_register_member', data=data, follow_redirects=True)
        self.assertIn('CSVファイルの形式が正しくありません'.encode('utf-8'), response.data)

    def test_bulk_register_member_duplicate(self):
        self.login('admin', 'admin123', 'adminpassword')
        with open(os.path.join('test_data', 'duplicate_members.csv'), 'r', encoding='utf-8') as f:
            csv_data = f.read()
        data = {
            'csv_file': (io.StringIO(csv_data), 'duplicate_members.csv')
        }
        response = self.client.post('/bulk_register_member', data=data, follow_redirects=True)
        self.assertIn('従業員番号が既に存在します'.encode('utf-8'), response.data)
        
    # 9. Change Password Page (2テスト)
    def test_change_password_success(self):
        self.login('employee', '12345', 'password')
        response = self.client.post('/change_password', data=dict(
            current_password='password',
            new_password='newpassword',
            confirm_password='newpassword'
        ), follow_redirects=True)
        self.assertIn('パスワードが正常に変更されました'.encode('utf-8'), response.data)

    def test_change_password_incorrect_current_password(self):
        self.login('employee', '12345', 'password')
        response = self.client.post('/change_password', data=dict(
            current_password='wrongpassword',
            new_password='newpassword',
            confirm_password='newpassword'
        ), follow_redirects=True)
        self.assertIn('現在のパスワードが正しくありません'.encode('utf-8'), response.data)

    def test_change_password_mismatch(self):
        self.login('employee', '12345', 'password')
        response = self.client.post('/change_password', data=dict(
            current_password='password',
            new_password='newpassword',
            confirm_password='differentpassword'
        ), follow_redirects=True)
        self.assertIn('新しいパスワードが一致しません'.encode('utf-8'), response.data)

if __name__ == '__main__':
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestViews)
    print(f"Number of test methods: {suite.countTestCases()}")
    unittest.TextTestRunner(verbosity=2).run(suite)