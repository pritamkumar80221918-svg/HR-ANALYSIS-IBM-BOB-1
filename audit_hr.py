import csv, collections

rows = []
with open('HR IBM.BOB.csv', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    for row in reader:
        rows.append(row)

print('=== DETAILED DATA QUALITY AUDIT ===')
print(f'Total rows: {len(rows)}')
print()

# 1. BOM check
with open('HR IBM.BOB.csv', 'rb') as f:
    bom = f.read(3)
bom_present = bom == b'\xef\xbb\xbf'
print(f'--- 1. BOM: {"UTF-8 BOM present (will strip)" if bom_present else "No BOM"}')
print()

# 2. Whitespace issues
print('--- 2. Whitespace / Trailing Spaces ---')
ws_found = False
for col in list(rows[0].keys()):
    ws_issues = [(i+2, repr(r[col])) for i, r in enumerate(rows) if r[col] != r[col].strip()]
    if ws_issues:
        ws_found = True
        print(f'  {col}: {len(ws_issues)} rows with leading/trailing spaces')
        for line, val in ws_issues[:3]:
            print(f'    line {line}: {val}')
if not ws_found:
    print('  No whitespace issues found')
print()

# 3. Case inconsistencies
print('--- 3. Case Inconsistencies ---')
cat_cols = ['Attrition','BusinessTravel','Department','EducationField','Gender','JobRole','MaritalStatus','Over18','OverTime']
case_found = False
for col in cat_cols:
    vals = set(r[col].strip() for r in rows)
    lower_map = collections.defaultdict(list)
    for v in vals:
        lower_map[v.lower()].append(v)
    problems = {k: v for k, v in lower_map.items() if len(v) > 1}
    if problems:
        case_found = True
        print(f'  {col}: {problems}')
if not case_found:
    print('  No case inconsistencies found')
print()

# 4. Logical consistency checks
print('--- 4. Logical Inconsistencies ---')

bad_years = [(i+2, r['YearsAtCompany'], r['TotalWorkingYears'])
             for i, r in enumerate(rows)
             if int(r['YearsAtCompany']) > int(r['TotalWorkingYears'])]
if bad_years:
    print(f'  YearsAtCompany > TotalWorkingYears: {len(bad_years)} rows')
    for line, a, t in bad_years[:10]:
        print(f'    line {line}: YearsAtCompany={a}, TotalWorkingYears={t}')
else:
    print('  YearsAtCompany <= TotalWorkingYears: OK')

bad_role = [(i+2, r['YearsInCurrentRole'], r['YearsAtCompany'])
            for i, r in enumerate(rows)
            if int(r['YearsInCurrentRole']) > int(r['YearsAtCompany'])]
if bad_role:
    print(f'  YearsInCurrentRole > YearsAtCompany: {len(bad_role)} rows (logically possible - role predates company)')
else:
    print('  YearsInCurrentRole <= YearsAtCompany: OK')

bad_promo = [(i+2, r['YearsSinceLastPromotion'], r['YearsAtCompany'])
             for i, r in enumerate(rows)
             if int(r['YearsSinceLastPromotion']) > int(r['YearsAtCompany'])]
if bad_promo:
    print(f'  YearsSinceLastPromotion > YearsAtCompany: {len(bad_promo)} rows')
    for line, a, t in bad_promo[:10]:
        print(f'    line {line}: YearsSinceLastPromotion={a}, YearsAtCompany={t}')
else:
    print('  YearsSinceLastPromotion <= YearsAtCompany: OK')

bad_mgr = [(i+2, r['YearsWithCurrManager'], r['YearsAtCompany'])
           for i, r in enumerate(rows)
           if int(r['YearsWithCurrManager']) > int(r['YearsAtCompany'])]
if bad_mgr:
    print(f'  YearsWithCurrManager > YearsAtCompany: {len(bad_mgr)} rows')
    for line, a, t in bad_mgr[:10]:
        print(f'    line {line}: YearsWithCurrManager={a}, YearsAtCompany={t}')
else:
    print('  YearsWithCurrManager <= YearsAtCompany: OK')

print()

# 5. Age vs TotalWorkingYears
print('--- 5. Age vs TotalWorkingYears ---')
bad_age = [(i+2, r['Age'], r['TotalWorkingYears'])
           for i, r in enumerate(rows)
           if int(r['TotalWorkingYears']) > int(r['Age']) - 16]
if bad_age:
    print(f'  TotalWorkingYears > (Age-16): {len(bad_age)} rows')
    for line, age, twk in bad_age[:15]:
        print(f'    line {line}: Age={age}, TotalWorkingYears={twk}')
else:
    print('  TotalWorkingYears vs Age: OK')
print()

# 6. Constant-value columns check
print('--- 6. Constant/Fixed Columns ---')
for col, expected in [('StandardHours','80'), ('EmployeeCount','1'), ('Over18','Y')]:
    vals = collections.Counter(r[col].strip() for r in rows)
    wrong = {k: v for k, v in vals.items() if k != expected}
    if wrong:
        print(f'  {col} has unexpected values: {wrong}')
    else:
        print(f'  {col}: all correct ({expected})')
print()

# 7. PerformanceRating - valid values 1-4 (IBM dataset typically shows 3-4)
print('--- 7. PerformanceRating Values ---')
pr_vals = collections.Counter(r['PerformanceRating'].strip() for r in rows)
print(f'  Distribution: {dict(sorted(pr_vals.items()))}')
bad_pr = [(i+2, r['PerformanceRating']) for i, r in enumerate(rows) if r['PerformanceRating'].strip() not in ['1','2','3','4']]
if bad_pr:
    print(f'  Invalid values: {bad_pr[:10]}')
print()

# 8. Education valid range 1-5
print('--- 8. Education Values ---')
edu_vals = collections.Counter(r['Education'].strip() for r in rows)
print(f'  Distribution: {dict(sorted(edu_vals.items()))}')
print()

# 9. Duplicate rows
print('--- 9. Duplicate Rows ---')
row_tuples = [tuple(r[k].strip() for k in rows[0].keys()) for r in rows]
dup_count = len(row_tuples) - len(set(row_tuples))
print(f'  Duplicate rows: {dup_count}')

# Find exact duplicate rows
seen = {}
dups = []
for i, rt in enumerate(row_tuples):
    if rt in seen:
        dups.append((i+2, seen[rt]+2))
    else:
        seen[rt] = i
if dups:
    print(f'  Duplicate at lines: {dups[:10]}')
print()

# 10. Numeric range check
print('--- 10. Numeric Range Violations ---')
num_ranges = {
    'Age': (18, 70),
    'DailyRate': (100, 1500),
    'DistanceFromHome': (1, 29),
    'Education': (1, 5),
    'EmployeeCount': (1, 1),
    'EnvironmentSatisfaction': (1, 4),
    'HourlyRate': (30, 100),
    'JobInvolvement': (1, 4),
    'JobLevel': (1, 5),
    'JobSatisfaction': (1, 4),
    'MonthlyIncome': (1009, 19999),
    'MonthlyRate': (2094, 26999),
    'NumCompaniesWorked': (0, 9),
    'PercentSalaryHike': (11, 25),
    'PerformanceRating': (1, 4),
    'RelationshipSatisfaction': (1, 4),
    'StandardHours': (80, 80),
    'StockOptionLevel': (0, 3),
    'TotalWorkingYears': (0, 40),
    'TrainingTimesLastYear': (0, 6),
    'WorkLifeBalance': (1, 4),
    'YearsAtCompany': (0, 40),
    'YearsInCurrentRole': (0, 18),
    'YearsSinceLastPromotion': (0, 15),
    'YearsWithCurrManager': (0, 17),
}
range_issues = False
for col, (lo, hi) in num_ranges.items():
    bad = []
    for i, r in enumerate(rows):
        val = r[col].strip()
        try:
            v = float(val)
            if v < lo or v > hi:
                bad.append((i+2, val))
        except:
            bad.append((i+2, f'NON-NUMERIC:{val!r}'))
    if bad:
        range_issues = True
        print(f'  {col} (expected {lo}-{hi}): {len(bad)} issues -> {bad[:5]}')
if not range_issues:
    print('  All numeric values within expected ranges')
print()

# 11. Non-numeric in numeric columns
print('--- 11. Non-numeric Values in Numeric Columns ---')
nn_found = False
for col in num_ranges.keys():
    bad = [(i+2, r[col]) for i, r in enumerate(rows) if not r[col].strip().lstrip('-').replace('.','',1).isdigit() and r[col].strip() != '']
    if bad:
        nn_found = True
        print(f'  {col}: {bad[:5]}')
if not nn_found:
    print('  No non-numeric values found in numeric columns')
print()

# 12. Salary hike vs performance rating (hike should correlate)
print('--- 12. PercentSalaryHike vs PerformanceRating ---')
hike_by_rating = collections.defaultdict(list)
for r in rows:
    hike_by_rating[r['PerformanceRating'].strip()].append(int(r['PercentSalaryHike'].strip()))
for rating, hikes in sorted(hike_by_rating.items()):
    print(f'  PerformanceRating={rating}: Hike range {min(hikes)}-{max(hikes)}, avg={sum(hikes)/len(hikes):.1f}')
print()

print('=== AUDIT COMPLETE ===')
