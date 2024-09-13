from flask import flash, render_template, request, redirect, url_for, session
from tableapp import app, db
from tableapp.models.skillmap import AdminData, EmployeeData, SkillList, QualificationList, EmployeeSkill, EmployeeQualification, TrainingList, EmployeeTraining, PendingSkill, PendingQualification, PendingTraining, RegistrationHistory
from datetime import datetime
import csv

# 1. Login Page
@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('tableapp/index.html')

@app.route('/employee_login', methods=['POST'])
def employee_login():
    employee_num = request.form.get('employee_num')
    
    user = EmployeeData.query.filter_by(employee_num=employee_num).first()
    if user:
        session['user_id'] = user.id
        session['user_role'] = 'employee'
        session['employee_num'] = employee_num
        session['is_evaluator'] = len(user.evaluation_target) > 0  # Set is_evaluator flag
        return redirect(url_for('my_page', id=user.id))
    return "Invalid employee number or you are not an employee"

@app.route('/admin_login', methods=['POST'])
def admin_login():
    admin_num = request.form.get('admin_num')
    user = AdminData.query.filter_by(admin_num=admin_num).first()
    if user:
        session['user_id'] = user.id
        session['user_role'] = 'admin'
        session['admin_num'] = admin_num
        return redirect(url_for('view_skillmap'))
    return "Invalid admin number or you are not an admin"

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# 2. View Skill Map Page
@app.route('/view_skillmap')
def view_skillmap():
    employees = EmployeeData.query.all()
    skills = SkillList.query.all()
    qualifications = QualificationList.query.all()
    trainings = TrainingList.query.all()
    
    skillmap = []
    
    # Adding skills to skillmap
    for skill in skills:
        row = {'name': skill.skill_name, 'category': 'skill'}
        for employee in employees:
            emp_skill = EmployeeSkill.query.filter_by(employee_num=employee.employee_num, skill_id=skill.id).first()
            if emp_skill:
                row[employee.employee_num] = emp_skill.level
            else:
                row[employee.employee_num] = ''  # レベルが指定されていない場合は空文字列にする
        skillmap.append(row)
    
    # Adding qualifications to skillmap
    for qualification in qualifications:
        row = {'name': qualification.qualification_name, 'category': 'qualification'}
        for employee in employees:
            qual = EmployeeQualification.query.filter_by(employee_num=employee.employee_num, qualification_id=qualification.id).first()
            row[employee.employee_num] = '〇' if qual else '' # レベルが指定されていない場合は空文字列にする
        skillmap.append(row)
    
    # Adding trainings to skillmap
    for training in trainings:
        row = {'name': training.training_name, 'category': 'training'}
        for employee in employees:
            emp_training = EmployeeTraining.query.filter_by(employee_num=employee.employee_num, training_id=training.id).first()
            row[employee.employee_num] = '〇' if emp_training else '' # レベルが指定されていない場合は空文字列にする
        skillmap.append(row)
    
    # Extract unique companies, units, and divisions
    companies = list(set(employee.company for employee in employees))
    units = list(set(employee.unit for employee in employees))
    divisions = list(set(employee.division for employee in employees))

    return render_template('tableapp/view_skillmap.html', skillmap=skillmap, employees=employees, skills=skills, qualifications=qualifications, trainings=trainings, companies=companies, units=units, divisions=divisions)

# 3. Employee Detail Page
@app.route('/employee_detail/<int:employee_id>')
def employee_detail(employee_id):
    employee = EmployeeData.query.get_or_404(employee_id)
    skills = EmployeeSkill.query.filter_by(employee_num=employee.employee_num).all()
    qualifications = EmployeeQualification.query.filter_by(employee_num=employee.employee_num).all()
    trainings = EmployeeTraining.query.filter_by(employee_num=employee.employee_num).all()
    
    skill_details = []
    for skill in skills:
        skill_info = SkillList.query.get(skill.skill_id)
        proficiency_levels = {
            '1': skill_info.prof_level_1,
            '2': skill_info.prof_level_2,
            '3': skill_info.prof_level_3,
            '4': skill_info.prof_level_4,
            '5': skill_info.prof_level_5,
        }
        skill_details.append({
            'name': skill_info.skill_name,
            'level': skill.level,
            'prof_level': proficiency_levels.get(str(skill.level), '-')  # Get proficiency level description
        })
    
    qualification_details = []
    for qualification in qualifications:
        qualification_info = QualificationList.query.get(qualification.qualification_id)
        qualification_details.append({
            'name': qualification_info.qualification_name,
            'newacq_renewal': qualification.newacq_renewal,
            'acq_renew_date': qualification.acq_renew_date,
            'expiry_date': qualification.expiry_date
        })
    
    training_details = []
    for training in trainings:
        training_info = TrainingList.query.get(training.training_id)
        training_details.append({
            'name': training_info.training_name,
            'start_date': training.start_date,
            'end_date': training.end_date
        })
    
    return render_template('tableapp/employee_detail.html', employee=employee, skills=skill_details, qualifications=qualification_details, trainings=training_details)

# 4. My Page (Employee Only)
@app.route('/my_page', methods=['GET', 'POST'])
def my_page():
    if 'user_id' in session and 'employee_num' in session:
        employee = EmployeeData.query.get(session['user_id'])
        
        if request.method == 'POST':
            # Update Employee Information
            employee.name = request.form.get('name')
            employee.email = request.form.get('email')
            employee.company = request.form.get('company')
            employee.division = request.form.get('division')
            employee.unit = request.form.get('unit')
            employee.subunit_team = request.form.get('subunit_team')
            employee.rank = request.form.get('rank')
            
            # Convert string date to Python date object
            date_of_join_str = request.form.get('date_of_join')
            try:
                employee.date_of_join = datetime.strptime(date_of_join_str, '%Y-%m-%d').date()
            except ValueError:
                flash('Invalid date format', 'danger')
                return redirect(url_for('my_page'))
            
            db.session.commit()
            flash('Employee information updated successfully', 'success')
        
        # Fetch pending registrations
        pending_skills = PendingSkill.query.filter_by(employee_num=employee.employee_num).all()
        pending_qualifications = PendingQualification.query.filter_by(employee_num=employee.employee_num).all()
        pending_trainings = PendingTraining.query.filter_by(employee_num=employee.employee_num).all()

        # Fetch registration history
        registration_history = RegistrationHistory.query.filter_by(employee_num=employee.employee_num).order_by(RegistrationHistory.date.desc()).all()
        
        return render_template('tableapp/my_page.html', employee=employee, pending_skills=pending_skills, pending_qualifications=pending_qualifications, pending_trainings=pending_trainings, registration_history=registration_history)
    return redirect(url_for('index'))

# 5. Register Page (Employee Only)
@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session and session['user_role'] == 'employee':
        if request.method == 'POST':
            # Register Skill
            if 'register_skill' in request.form:
                skill_name = request.form.get('skill_name')
                level = request.form.get('level', type=int)
                if level < 1 or level > 5:
                    flash('Skill level must be between 1 and 5', 'danger')
                else:
                    new_pending_skill = PendingSkill(
                        employee_num=session['employee_num'],
                        skill_name=skill_name,
                        level=level
                    )
                    db.session.add(new_pending_skill)
                    db.session.commit()
                    
                    # Log the registration action
                    history = RegistrationHistory(
                        employee_num=session['employee_num'],
                        action_type='Skill',
                        action_detail=f'{skill_name} Level {level}',
                        status='申請中'
                    )
                    db.session.add(history)
                    db.session.commit()
                    flash('Skill registration submitted for approval', 'success')

            # Register Qualification
            if 'register_qualification' in request.form:
                qualification_name = request.form.get('qualification_name')
                newacq_renewal = request.form.get('newacq_renewal')
                acq_renew_date = request.form.get('acq_renew_date')
                expiry_date = request.form.get('expiry_date')
                new_pending_qualification = PendingQualification(
                    employee_num=session['employee_num'],
                    qualification_name=qualification_name,
                    newacq_renewal=newacq_renewal,
                    acq_renew_date=acq_renew_date,
                    expiry_date=expiry_date
                )
                db.session.add(new_pending_qualification)
                db.session.commit()
                
                # Log the registration action
                history = RegistrationHistory(
                    employee_num=session['employee_num'],
                    action_type='Qualification',
                    action_detail=qualification_name,
                    status='申請中'
                )
                db.session.add(history)
                db.session.commit()
                flash('Qualification registration submitted for approval', 'success')

            # Register Training
            if 'register_training' in request.form:
                training_name = request.form.get('training_name')
                start_date = request.form.get('start_date')
                end_date = request.form.get('end_date')
                new_pending_training = PendingTraining(
                    employee_num=session['employee_num'],
                    training_name=training_name,
                    start_date=start_date,
                    end_date=end_date
                )
                db.session.add(new_pending_training)
                db.session.commit()
                
                # Log the registration action
                history = RegistrationHistory(
                    employee_num=session['employee_num'],
                    action_type='Training',
                    action_detail=training_name,
                    status='申請中'
                )
                db.session.add(history)
                db.session.commit()
                flash('Training registration submitted for approval', 'success')

        # Fetch available skills, qualifications, and trainings
        skills = SkillList.query.all()
        qualifications = QualificationList.query.all()
        trainings = TrainingList.query.all()

        return render_template('tableapp/register.html', skills=skills, qualifications=qualifications, trainings=trainings)
    return redirect(url_for('index'))

# 6. Approve Page (Evaluators Only)
@app.route('/approve/<int:id>', methods=['GET', 'POST'])
def approve(id):
    if 'user_id' in session and 'employee_num' in session:
        user = EmployeeData.query.get(session['user_id'])
        if user.evaluation_target:
            if request.method == 'POST':
                # Approve or Deny Skill
                if 'approve_skill' in request.form:
                    pending_id = request.form.get('pending_id', type=int)
                    action = request.form.get('approve_skill')
                    pending_skill = PendingSkill.query.get(pending_id)
                    if pending_skill:
                        skill = SkillList.query.filter_by(skill_name=pending_skill.skill_name).first()
                        if skill:
                            if action == 'approve':
                                existing_skill = EmployeeSkill.query.filter_by(employee_num=pending_skill.employee_num, skill_id=skill.id).first()
                                if existing_skill:
                                    existing_skill.level = pending_skill.level
                                else:
                                    new_skill = EmployeeSkill(
                                        employee_num=pending_skill.employee_num,
                                        skill_id=skill.id,
                                        level=pending_skill.level
                                    )
                                    db.session.add(new_skill)
                                db.session.commit()
                                
                                # Log the approval action
                                history = RegistrationHistory(
                                    employee_num=pending_skill.employee_num,
                                    action_type='Skill',
                                    action_detail=f'{pending_skill.skill_name} Level {pending_skill.level}',
                                    status='承認'
                                )
                                db.session.add(history)
                                db.session.commit()
                            elif action == 'deny':
                                db.session.commit()
                                
                                # Log the denial action
                                history = RegistrationHistory(
                                    employee_num=pending_skill.employee_num,
                                    action_type='Skill',
                                    action_detail=f'{pending_skill.skill_name} Level {pending_skill.level}',
                                    status='拒否'
                                )
                                db.session.add(history)
                                db.session.commit()
                            db.session.delete(pending_skill)
                            db.session.commit()

                # Approve or Deny Qualification
                if 'approve_qualification' in request.form:
                    pending_id = request.form.get('pending_id', type=int)
                    action = request.form.get('approve_qualification')
                    pending_qualification = PendingQualification.query.get(pending_id)
                    if pending_qualification:
                        qualification = QualificationList.query.filter_by(qualification_name=pending_qualification.qualification_name).first()
                        if qualification:
                            if action == 'approve':
                                existing_qualification = EmployeeQualification.query.filter_by(employee_num=pending_qualification.employee_num, qualification_id=qualification.id).first()
                                if existing_qualification:
                                    existing_qualification.newacq_renewal = pending_qualification.newacq_renewal
                                    existing_qualification.acq_renew_date = pending_qualification.acq_renew_date
                                    existing_qualification.expiry_date = pending_qualification.expiry_date
                                else:
                                    new_qualification = EmployeeQualification(
                                        employee_num=pending_qualification.employee_num,
                                        qualification_id=qualification.id,
                                        newacq_renewal=pending_qualification.newacq_renewal,
                                        acq_renew_date=pending_qualification.acq_renew_date,
                                        expiry_date=pending_qualification.expiry_date
                                    )
                                    db.session.add(new_qualification)
                                db.session.commit()
                                
                                # Log the approval action
                                history = RegistrationHistory(
                                    employee_num=pending_qualification.employee_num,
                                    action_type='Qualification',
                                    action_detail=pending_qualification.qualification_name,
                                    status='承認'
                                )
                                db.session.add(history)
                                db.session.commit()
                            elif action == 'deny':
                                db.session.commit()
                                
                                # Log the denial action
                                history = RegistrationHistory(
                                    employee_num=pending_qualification.employee_num,
                                    action_type='Qualification',
                                    action_detail=pending_qualification.qualification_name,
                                    status='拒否'
                                )
                                db.session.add(history)
                                db.session.commit()
                            db.session.delete(pending_qualification)
                            db.session.commit()

                # Approve or Deny Training
                if 'approve_training' in request.form:
                    pending_id = request.form.get('pending_id', type=int)
                    action = request.form.get('approve_training')
                    pending_training = PendingTraining.query.get(pending_id)
                    if pending_training:
                        training = TrainingList.query.filter_by(training_name=pending_training.training_name).first()
                        if training:
                            if action == 'approve':
                                existing_training = EmployeeTraining.query.filter_by(employee_num=pending_training.employee_num, training_id=training.id).first()
                                if existing_training:
                                    existing_training.start_date = pending_training.start_date
                                    existing_training.end_date = pending_training.end_date
                                else:
                                    new_training = EmployeeTraining(
                                        employee_num=pending_training.employee_num,
                                        training_id=training.id,
                                        start_date=pending_training.start_date,
                                        end_date=pending_training.end_date
                                    )
                                    db.session.add(new_training)
                                db.session.commit()
                                
                                # Log the approval action
                                history = RegistrationHistory(
                                    employee_num=pending_training.employee_num,
                                    action_type='Training',
                                    action_detail=pending_training.training_name,
                                    status='承認'
                                )
                                db.session.add(history)
                                db.session.commit()
                            elif action == 'deny':
                                db.session.commit()
                                
                                # Log the denial action
                                history = RegistrationHistory(
                                    employee_num=pending_training.employee_num,
                                    action_type='Training',
                                    action_detail=pending_training.training_name,
                                    status='拒否'
                                )
                                db.session.add(history)
                                db.session.commit()
                            db.session.delete(pending_training)
                            db.session.commit()

            # Filter pending submissions by evaluation targets
            pending_skills = PendingSkill.query.filter(PendingSkill.employee_num.in_(user.evaluation_target)).all()
            pending_qualifications = PendingQualification.query.filter(PendingQualification.employee_num.in_(user.evaluation_target)).all()
            pending_trainings = PendingTraining.query.filter(PendingTraining.employee_num.in_(user.evaluation_target)).all()
            
            return render_template('tableapp/approve_page.html', pending_skills=pending_skills, pending_qualifications=pending_qualifications, pending_trainings=pending_trainings)
    return redirect(url_for('index'))


# 7. Manage Skills, Qualifications, and Training Page (Admin Only)
@app.route('/admin/manage_skills_qualifications_trainings', methods=['GET', 'POST'])
def manage_skills_qualifications_trainings():
    if 'user_id' in session and session['user_role'] == 'admin':
        if request.method == 'POST':
            # Add Skill
            if 'add_skill' in request.form:
                skill_name = request.form.get('skill_name')
                new_skill = SkillList(skill_name=skill_name)
                db.session.add(new_skill)
                db.session.commit()
                flash('Skill added successfully', 'success')

            # Delete Skill
            if 'delete_skill' in request.form:
                skill_id = request.form.get('skill_id', type=int)
                skill = SkillList.query.get(skill_id)
                if skill:
                    db.session.delete(skill)
                    db.session.commit()
                    flash('Skill deleted successfully', 'success')

            # Add Qualification
            if 'add_qualification' in request.form:
                qualification_name = request.form.get('qualification_name')
                new_qualification = QualificationList(qualification_name=qualification_name)
                db.session.add(new_qualification)
                db.session.commit()
                flash('Qualification added successfully', 'success')

            # Delete Qualification
            if 'delete_qualification' in request.form:
                qualification_id = request.form.get('qualification_id', type=int)
                qualification = QualificationList.query.get(qualification_id)
                if qualification:
                    db.session.delete(qualification)
                    db.session.commit()
                    flash('Qualification deleted successfully', 'success')

            # Add Training
            if 'add_training' in request.form:
                training_name = request.form.get('training_name')
                new_training = TrainingList(training_name=training_name)
                db.session.add(new_training)
                db.session.commit()
                flash('Training added successfully', 'success')

            # Delete Training
            if 'delete_training' in request.form:
                training_id = request.form.get('training_id', type=int)
                training = TrainingList.query.get(training_id)
                if training:
                    db.session.delete(training)
                    db.session.commit()
                    flash('Training deleted successfully', 'success')

        skills = SkillList.query.all()
        qualifications = QualificationList.query.all()
        trainings = TrainingList.query.all()
        return render_template('tableapp/manage_skills_qualifications_trainings.html', skills=skills, qualifications=qualifications, trainings=trainings)
    return redirect(url_for('index'))

# 8. Register Member Page (Admin Only)
@app.route('/register_member', methods=['GET', 'POST'])
def register_member():
    if request.method == 'POST':
        # Process form submission
        employee_num = request.form['employee_num']
        name = request.form['name']
        email = request.form['email']
        company = request.form['company']
        division = request.form['division']
        unit = request.form['unit']
        subunit_team = request.form['subunit_team']
        rank = request.form['rank']
        date_of_join = request.form['date_of_join']
        evaluation_target = request.form['evaluation_target']

        # Convert evaluation_target to list of integers
        if evaluation_target:
            evaluation_target = [int(num) for num in evaluation_target.split(',') if num.strip().isdigit()]
        else:
            evaluation_target = []

        # Convert date_of_join to date object
        try:
            date_of_join = datetime.strptime(date_of_join, '%Y-%m-%d').date()
        except ValueError:
            flash('入社日の形式が正しくありません。YYYY-MM-DD形式で入力してください。', 'danger')
            return redirect(url_for('register_member'))

        # Check if employee already exists
        existing_employee = EmployeeData.query.filter_by(employee_num=employee_num).first()
        if existing_employee:
            flash('社員番号が既に存在します', 'danger')
        else:
            # Create a new EmployeeData object
            new_employee = EmployeeData(
                employee_num=employee_num,
                name=name,
                email=email,
                company=company,
                division=division,
                unit=unit,
                subunit_team=subunit_team,
                rank=rank,
                date_of_join=date_of_join,
                evaluation_target=evaluation_target
            )
            # Add and commit to the database
            db.session.add(new_employee)
            db.session.commit()
            flash('メンバーが正常に登録されました', 'success')
            return redirect(url_for('register_member'))

    # Handle GET request and search functionality
    search_query = request.args.get('search_query')
    search_results = None
    if search_query:
        search_results = EmployeeData.query.filter(
            (EmployeeData.employee_num.like(f'%{search_query}%')) |
            (EmployeeData.name.like(f'%{search_query}%'))
        ).all()

    # Fetch all employees to display
    employees = EmployeeData.query.all()

    return render_template('tableapp/register_member.html', employees=employees, search_results=search_results)


@app.route('/bulk_register_member', methods=['POST'])
def bulk_register_member():
    if 'csv_file' not in request.files:
        flash('CSVファイルが見つかりません', 'danger')
        return redirect(url_for('register_member'))

    file = request.files['csv_file']
    if file.filename == '':
        flash('ファイルが選択されていません', 'danger')
        return redirect(url_for('register_member'))

    if file and file.filename.endswith('.csv'):
        csv_file = file.read().decode('utf-8')
        csv_reader = csv.reader(csv_file.splitlines())
        next(csv_reader)  # Skip header row

        for row in csv_reader:
            if len(row) != 10:
                flash('CSVファイルの形式が正しくありません。各行に10個の値が含まれていることを確認してください。', 'danger')
                continue

            employee_num, name, email, company, division, unit, subunit_team, rank, date_of_join, evaluation_target = row
            
            # Convert evaluation_target to list of integers
            if evaluation_target:
                evaluation_target = [int(num) for num in evaluation_target.split(',') if num.strip().isdigit()]
            else:
                evaluation_target = []

            # Convert date_of_join to date object
            try:
                date_of_join = datetime.strptime(date_of_join, '%Y-%m-%d').date()
            except ValueError:
                flash(f'入社日の形式が正しくありません: {date_of_join}. YYYY-MM-DD形式で入力してください。', 'danger')
                continue

            existing_employee = EmployeeData.query.filter_by(employee_num=employee_num).first()
            if not existing_employee:
                new_employee = EmployeeData(
                    employee_num=employee_num,
                    name=name,
                    email=email,
                    company=company,
                    division=division,
                    unit=unit,
                    subunit_team=subunit_team,
                    rank=rank,
                    date_of_join=date_of_join,
                    evaluation_target=evaluation_target
                )
                db.session.add(new_employee)

        db.session.commit()
        flash('従業員が正常に一括登録されました', 'success')
    else:
        flash('無効なファイル形式です。CSVファイルをアップロードしてください。', 'danger')

    return redirect(url_for('register_member'))

@app.route('/delete_member/<int:employee_num>', methods=['POST'])
def delete_member(employee_num):
    try:
        # Fetch the employee to delete
        employee = EmployeeData.query.filter_by(employee_num=employee_num).first()
        if not employee:
            flash('メンバーが見つかりません', 'danger')
            return redirect(url_for('register_member'))

        # Handle related pending training records
        pending_trainings = PendingTraining.query.filter_by(employee_num=employee_num).all()
        for pending_training in pending_trainings:
            db.session.delete(pending_training)

        # Handle related pending skill records
        pending_skills = PendingSkill.query.filter_by(employee_num=employee_num).all()
        for pending_skill in pending_skills:
            db.session.delete(pending_skill)

        # Handle related pending qualification records
        pending_qualifications = PendingQualification.query.filter_by(employee_num=employee_num).all()
        for pending_qualification in pending_qualifications:
            db.session.delete(pending_qualification)

        # Handle related registration history records
        registration_histories = RegistrationHistory.query.filter_by(employee_num=employee_num).all()
        for registration_history in registration_histories:
            db.session.delete(registration_history)

        # Now delete the employee
        db.session.delete(employee)
        db.session.commit()
        flash('メンバーが正常に削除されました', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'エラーが発生しました: {str(e)}', 'danger')

    return redirect(url_for('register_member'))