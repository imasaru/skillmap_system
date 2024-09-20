import unittest
from __init__ import AdminData, EmployeeData, SkillList, QualificationList, TrainingList, EmployeeSkill, EmployeeQualification, EmployeeTraining, PendingSkill, PendingQualification, PendingTraining, RegistrationHistory
from werkzeug.security import generate_password_hash, check_password_hash

class TestInit(unittest.TestCase):

    def test_admin_set_password(self):
        admin = AdminData()
        admin.set_password('test_password')
        self.assertTrue(check_password_hash(admin.password_hash, 'test_password'))

    def test_admin_check_password(self):
        admin = AdminData()
        admin.set_password('test_password')
        self.assertTrue(admin.check_password('test_password'))
        self.assertFalse(admin.check_password('wrong_password'))

    def test_employee_set_password(self):
        employee = EmployeeData()
        employee.set_password('test_password')
        self.assertTrue(check_password_hash(employee.password_hash, 'test_password'))

    def test_employee_check_password(self):
        employee = EmployeeData()
        employee.set_password('test_password')
        self.assertTrue(employee.check_password('test_password'))
        self.assertFalse(employee.check_password('wrong_password'))

    def test_admin_data_insertion(self):
        admin = AdminData(admin_num=1, name='Admin', email='admin@example.com')
        self.assertEqual(admin.admin_num, 1)
        self.assertEqual(admin.name, 'Admin')
        self.assertEqual(admin.email, 'admin@example.com')

    def test_employee_data_insertion(self):
        employee = EmployeeData(employee_num=1, name='Employee', email='employee@example.com')
        self.assertEqual(employee.employee_num, 1)
        self.assertEqual(employee.name, 'Employee')
        self.assertEqual(employee.email, 'employee@example.com')

    def test_skill_list_data_insertion(self):
        skill = SkillList(skill_name='Python')
        self.assertEqual(skill.skill_name, 'Python')

    def test_qualification_list_data_insertion(self):
        qualification = QualificationList(qualification_name='Certified Developer')
        self.assertEqual(qualification.qualification_name, 'Certified Developer')

    def test_training_list_data_insertion(self):
        training = TrainingList(training_name='Leadership Training')
        self.assertEqual(training.training_name, 'Leadership Training')

    def test_employee_skill_data_insertion(self):
        emp_skill = EmployeeSkill(employee_num=1, skill_id=1, level=3)
        self.assertEqual(emp_skill.employee_num, 1)
        self.assertEqual(emp_skill.skill_id, 1)
        self.assertEqual(emp_skill.level, 3)

    def test_employee_qualification_data_insertion(self):
        emp_qual = EmployeeQualification(employee_num=1, qualification_id=1, newacq_renewal='new', acq_renew_date='2023-01-01', expiry_date='2024-01-01')
        self.assertEqual(emp_qual.employee_num, 1)
        self.assertEqual(emp_qual.qualification_id, 1)
        self.assertEqual(emp_qual.newacq_renewal, 'new')
        self.assertEqual(emp_qual.acq_renew_date, '2023-01-01')
        self.assertEqual(emp_qual.expiry_date, '2024-01-01')

    def test_employee_training_data_insertion(self):
        emp_trn = EmployeeTraining(employee_num=1, training_id=1, start_date='2023-01-01', end_date='2023-01-05')
        self.assertEqual(emp_trn.employee_num, 1)
        self.assertEqual(emp_trn.training_id, 1)
        self.assertEqual(emp_trn.start_date, '2023-01-01')
        self.assertEqual(emp_trn.end_date, '2023-01-05')

    def test_pending_skill_data_insertion(self):
        pending_skill = PendingSkill(employee_num=1, skill_id=1, level=3, submitted_date='2023-01-01')
        self.assertEqual(pending_skill.employee_num, 1)
        self.assertEqual(pending_skill.skill_id, 1)
        self.assertEqual(pending_skill.level, 3)
        self.assertEqual(pending_skill.submitted_date, '2023-01-01')

    def test_pending_qualification_data_insertion(self):
        pending_qual = PendingQualification(employee_num=1, qualification_id=1, newacq_renewal='new', acq_renew_date='2023-01-01', expiry_date='2024-01-01', submitted_date='2023-01-01')
        self.assertEqual(pending_qual.employee_num, 1)
        self.assertEqual(pending_qual.qualification_id, 1)
        self.assertEqual(pending_qual.newacq_renewal, 'new')
        self.assertEqual(pending_qual.acq_renew_date, '2023-01-01')
        self.assertEqual(pending_qual.expiry_date, '2024-01-01')
        self.assertEqual(pending_qual.submitted_date, '2023-01-01')

    def test_pending_training_data_insertion(self):
        pending_trn = PendingTraining(employee_num=1, training_id=1, start_date='2023-01-01', end_date='2023-01-05', submitted_date='2023-01-01')
        self.assertEqual(pending_trn.employee_num, 1)
        self.assertEqual(pending_trn.training_id, 1)
        self.assertEqual(pending_trn.start_date, '2023-01-01')
        self.assertEqual(pending_trn.end_date, '2023-01-05')
        self.assertEqual(pending_trn.submitted_date, '2023-01-01')

    def test_registration_history_data_insertion(self):
        reg_history = RegistrationHistory(employee_num=1, action_type='Skill', action_detail='Python Level 3', status='申請', date='2023-01-01')
        self.assertEqual(reg_history.employee_num, 1)
        self.assertEqual(reg_history.action_type, 'Skill')
        self.assertEqual(reg_history.action_detail, 'Python Level 3')
        self.assertEqual(reg_history.status, '申請')
        self.assertEqual(reg_history.date, '2023-01-01')

if __name__ == '__main__':
    unittest.main()