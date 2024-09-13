document.addEventListener('DOMContentLoaded', function() {
    const applyFilterButton = document.getElementById('applyFilter');
    const clearFilterButton = document.getElementById('clearFilter');
    const skillCheckboxes = document.querySelectorAll('.skill-checkbox');
    const skillLevelSelects = document.querySelectorAll('.skill-level-select');
    const qualificationCheckboxes = document.querySelectorAll('#qualificationFilter .form-check-input');
    const trainingCheckboxes = document.querySelectorAll('#trainingFilter .form-check-input');
    const employeeNameFilter = document.getElementById('employeeNameFilter');
    const companyFilter = document.getElementById('companyFilter');
    const unitFilter = document.getElementById('unitFilter');
    const divisionFilter = document.getElementById('divisionFilter');
    const filterList = document.getElementById('filterList');

    const createFilterBubble = (type, label, value) => {
        const bubble = document.createElement('div');
        bubble.className = `filter-bubble filter-bubble-${type}`;
        bubble.innerHTML = `${label}: ${value} <span class="remove-filter">&times;</span>`;
        bubble.dataset.label = label;
        bubble.dataset.value = value;
        bubble.dataset.type = type;
        filterList.appendChild(bubble);
    };

    const updateFilterList = () => {
        filterList.innerHTML = '';
        
        skillCheckboxes.forEach((checkbox, index) => {
            if (checkbox.checked) {
                const skillLevel = skillLevelSelects[index].value;
                createFilterBubble('skill', checkbox.value, `レベル: ${skillLevel || '指定なし'}`);
            }
        });
        
        qualificationCheckboxes.forEach(checkbox => {
            if (checkbox.checked) {
                createFilterBubble('qualification', checkbox.value, '');
            }
        });
        
        trainingCheckboxes.forEach(checkbox => {
            if (checkbox.checked) {
                createFilterBubble('training', checkbox.value, '');
            }
        });
        
        if (employeeNameFilter.value) {
            createFilterBubble('basic', '名前', employeeNameFilter.value);
        }
        
        if (companyFilter.value) {
            createFilterBubble('basic', '会社', companyFilter.value);
        }
        
        if (unitFilter.value) {
            createFilterBubble('basic', 'ユニット', unitFilter.value);
        }
        
        if (divisionFilter.value) {
            createFilterBubble('basic', '部門', divisionFilter.value);
        }

        document.querySelectorAll('.remove-filter').forEach(button => {
            button.addEventListener('click', function() {
                const bubble = button.parentElement;
                const type = bubble.dataset.type;
                const label = bubble.dataset.label;
                const value = bubble.dataset.value;

                // Remove corresponding filter
                if (type === 'skill') {
                    skillCheckboxes.forEach((checkbox, index) => {
                        if (checkbox.value === label) {
                            checkbox.checked = false;
                            skillLevelSelects[index].value = '';
                        }
                    });
                } else if (type === 'qualification') {
                    qualificationCheckboxes.forEach(checkbox => {
                        if (checkbox.value === label) {
                            checkbox.checked = false;
                        }
                    });
                } else if (type === 'training') {
                    trainingCheckboxes.forEach(checkbox => {
                        if (checkbox.value === label) {
                            checkbox.checked = false;
                        }
                    });
                } else if (type === 'basic') {
                    if (label === '名前') {
                        employeeNameFilter.value = '';
                    } else if (label === '会社') {
                        companyFilter.value = '';
                    } else if (label === 'ユニット') {
                        unitFilter.value = '';
                    } else if (label === '部門') {
                        divisionFilter.value = '';
                    }
                }

                bubble.remove();
                filterColumns();
            });
        });
    };

    const filterColumns = () => {
        console.log('Applying filters...');  // Debugging log

        const selectedSkills = Array.from(skillCheckboxes).filter(checkbox => checkbox.checked).map(checkbox => checkbox.value.toLowerCase());
        const skillLevels = Array.from(skillLevelSelects).map(select => select.value);
        const selectedQualifications = Array.from(qualificationCheckboxes).filter(checkbox => checkbox.checked).map(checkbox => checkbox.value.toLowerCase());
        const selectedTrainings = Array.from(trainingCheckboxes).filter(checkbox => checkbox.checked).map(checkbox => checkbox.value.toLowerCase());
        const employeeName = employeeNameFilter.value.toLowerCase();
        const company = companyFilter.value.toLowerCase();
        const unit = unitFilter.value.toLowerCase();
        const division = divisionFilter.value.toLowerCase();

        const employeeHeaders = document.querySelectorAll('.employee-header');
        const rows = document.querySelectorAll('#skillmapTable tbody tr');

        employeeHeaders.forEach(header => {
            let showEmployee = true;
            const employeeNum = header.dataset.employee;

            // Skill filter
            if (selectedSkills.length > 0) {
                const skillCells = document.querySelectorAll(`.employee-skill[data-employee="${employeeNum}"]`);
                let skillMatch = false;
                skillCells.forEach((cell, index) => {
                    const skillName = cell.parentElement.querySelector('.item-name').textContent.toLowerCase();
                    if (selectedSkills.includes(skillName)) {
                        const skillLevel = skillLevels[selectedSkills.indexOf(skillName)];
                        if (!skillLevel && cell.dataset.level !== '') {  // レベルが指定されていない場合、任意のレベルが許容される
                            skillMatch = true;
                        } else if (skillLevel && cell.dataset.level === skillLevel) {
                            skillMatch = true;
                        }
                    }
                });
                if (!skillMatch) {
                    showEmployee = false;
                }
            }

            // Qualification filter
            if (selectedQualifications.length > 0) {
                const qualificationCells = document.querySelectorAll(`.employee-qualification[data-employee="${employeeNum}"]`);
                let qualificationMatch = false;
                qualificationCells.forEach(cell => {
                    if (selectedQualifications.includes(cell.parentElement.querySelector('.item-name').textContent.toLowerCase()) && cell.textContent.trim() === '〇') {
                        qualificationMatch = true;
                    }
                });
                if (!qualificationMatch) {
                    showEmployee = false;
                }
            }

            // Training filter
            if (selectedTrainings.length > 0) {
                const trainingCells = document.querySelectorAll(`.employee-training[data-employee="${employeeNum}"]`);
                let trainingMatch = false;
                trainingCells.forEach(cell => {
                    if (selectedTrainings.includes(cell.parentElement.querySelector('.item-name').textContent.toLowerCase()) && cell.textContent.trim() === '〇') {
                        trainingMatch = true;
                    }
                });
                if (!trainingMatch) {
                    showEmployee = false;
                }
            }

            // Employee name filter
            if (employeeName && !header.dataset.name.toLowerCase().includes(employeeName)) {
                showEmployee = false;
            }

            // Company filter
            if (company && !header.dataset.company.toLowerCase().includes(company)) {
                showEmployee = false;
            }

            // Unit filter
            if (unit && !header.dataset.unit.toLowerCase().includes(unit)) {
                showEmployee = false;
            }

            // Division filter
            if (division && !header.dataset.division.toLowerCase().includes(division)) {
                showEmployee = false;
            }

            // Show or hide employee column
            const employeeCells = document.querySelectorAll(`td[data-employee="${employeeNum}"]`);
            if (showEmployee) {
                header.style.display = '';
                employeeCells.forEach(cell => cell.style.display = '');
            } else {
                header.style.display = 'none';
                employeeCells.forEach(cell => cell.style.display = 'none');
            }
        });

        updateFilterList();
    };

    applyFilterButton.addEventListener('click', function() {
        console.log('Apply filter button clicked');  // Debugging log
        filterColumns();
    });

    clearFilterButton.addEventListener('click', function() {
        console.log('Clear filter button clicked');  // Debugging log
        skillCheckboxes.forEach(checkbox => checkbox.checked = false);
        skillLevelSelects.forEach(select => select.value = '');
        qualificationCheckboxes.forEach(checkbox => checkbox.checked = false);
        trainingCheckboxes.forEach(checkbox => checkbox.checked = false);
        employeeNameFilter.value = '';
        companyFilter.value = '';
        unitFilter.value = '';
        divisionFilter.value = '';
        filterColumns();
    });

    filterColumns();  // Initial filter on page load
});