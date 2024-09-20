import unittest
from tableapp.models.skillmap import AdminData, EmployeeData, SkillList, QualificationList, TrainingList, EmployeeSkill, EmployeeQualification, EmployeeTraining, PendingSkill, PendingQualification, PendingTraining, RegistrationHistory

class TestSkillmap(unittest.TestCase):
    # テストケースの定義
    def test_admin_set_password(self):
        admin = AdminData()
        admin.set_password('test_password')
        self.assertTrue(admin.check_password('test_password'))

    def test_admin_check_password(self):
        admin = AdminData()
        admin.set_password('test_password')
        self.assertTrue(admin.check_password('test_password'))
        self.assertFalse(admin.check_password('wrong_password'))

    def test_employee_set_password(self):
        employee = EmployeeData()
        employee.set_password('test_password')
        self.assertTrue(employee.check_password('test_password'))

    def test_employee_check_password(self):
        employee = EmployeeData()
        employee.set_password('test_password')
        self.assertTrue(employee.check_password('test_password'))
        self.assertFalse(employee.check_password('wrong_password'))

    # 他のテストケースもここに追加

if __name__ == '__main__':
    unittest.main()