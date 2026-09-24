import csv, re, collections

rows = []
with open('HR IBM.BOB.csv', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    headers = list(reader.fieldnames)
    for row in reader:
        rows.append(row)

print(f'Headers ({len(headers)}): {headers}')
print()

# Blank/invalid column names
print('--- Blank/Extra Columns ---')
for h in headers:
    if not h.strip():
        print(f'  BLANK COLUMN: {repr(h)}')
print('  Done')
print()

# Row length check
print('--- Row Column Count ---')
issues = 0
for i, r in enumerate(rows):
    if len(r) != len(headers):
        issues += 1
        print(f'  Row {i+2} has {len(r)} columns (expected {len(headers)})')
if issues == 0:
    print('  All rows have correct column count')
print()

# Special chars in string columns
print('--- Special Characters in String Columns ---')
str_cols = ['Attrition','BusinessTravel','Department','EducationField','Gender','JobRole','MaritalStatus','Over18','OverTime']
special = False
for col in str_cols:
    for i, r in enumerate(rows):
        val = r[col]
        if re.search(r'[&<>"\x00-\x1f]', val):
            special = True
            print(f'  {col} line {i+2}: {repr(val)}')
if not special:
    print('  No special characters found')
print()

# Outlier detection using IQR for numeric cols
print('--- Statistical Outliers (IQR method) ---')
num_cols = ['Age','DailyRate','DistanceFromHome','HourlyRate','MonthlyIncome',
            'MonthlyRate','NumCompaniesWorked','PercentSalaryHike','TotalWorkingYears',
            'TrainingTimesLastYear','YearsAtCompany','YearsInCurrentRole',
            'YearsSinceLastPromotion','YearsWithCurrManager']

for col in num_cols:
    vals = sorted(float(r[col]) for r in rows)
    n = len(vals)
    q1 = vals[n//4]
    q3 = vals[3*n//4]
    iqr = q3 - q1
    lo = q1 - 1.5 * iqr
    hi = q3 + 1.5 * iqr
    outliers = [(i+2, r[col]) for i, r in enumerate(rows) if float(r[col]) < lo or float(r[col]) > hi]
    if outliers:
        print(f'  {col} [IQR range {lo:.1f}-{hi:.1f}]: {len(outliers)} outliers')
        for line, val in outliers[:5]:
            print(f'    line {line}: {val}')
print()

print('=== DEEP AUDIT COMPLETE ===')
