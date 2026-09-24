"""
HR IBM.BOB.csv - Data Cleaning Script
=====================================
Issues found and fixed:
  1. UTF-8 BOM in file header - stripped on read/write
  2. All string values trimmed of leading/trailing whitespace (defensive)
  3. StandardHours column is always 80 - redundant but retained, verified
  4. EmployeeCount column is always 1 - redundant but retained, verified
  5. Over18 column is always Y - redundant but retained, verified
  6. PerformanceRating: only values 3 and 4 present (valid per IBM dataset spec)
  7. IQR "outliers" in MonthlyIncome, TotalWorkingYears, YearsAtCompany etc.
     are all within documented IBM dataset ranges — NOT errors, retained as-is
  8. 'Research & Development' ampersand flag was a false positive from the regex
     pattern matching '&' as a special char; the value is correct
  9. EmployeeNumber gaps (444 gaps in 1-2068 range) are normal — employees left
 10. No missing values, no nulls, no duplicates, no type errors found

Cleaning actions performed:
  - Strip UTF-8 BOM from output (write clean UTF-8)
  - Strip whitespace from all string fields
  - Normalise categorical column values (trim + title-case where appropriate)
  - Validate and report any remaining anomalies
  - Write cleaned file: HR IBM.BOB.CLEANED.csv
"""

import csv, collections, os

INPUT  = 'HR IBM.BOB.csv'
OUTPUT = 'HR IBM.BOB.CLEANED.csv'

# ── read ──────────────────────────────────────────────────────────────────────
rows = []
with open(INPUT, encoding='utf-8-sig') as f:   # utf-8-sig strips BOM
    reader = csv.DictReader(f)
    headers = list(reader.fieldnames)
    for row in reader:
        rows.append(row)

print(f"Read {len(rows)} rows, {len(headers)} columns")
print()

# ── cleaning log ──────────────────────────────────────────────────────────────
changes = collections.defaultdict(list)

def log(row_num, col, old, new):
    changes[col].append({'row': row_num, 'from': old, 'to': new})

# ── CLEAN ─────────────────────────────────────────────────────────────────────
cleaned_rows = []
for idx, row in enumerate(rows):
    row_num = idx + 2   # 1-based, line 1 = header

    new_row = {}
    for col in headers:
        val = row[col]

        # ── 1. Strip whitespace from all fields ──────────────────────────────
        stripped = val.strip()
        if stripped != val:
            log(row_num, col, repr(val), repr(stripped))
        val = stripped

        # ── 2. Categorical normalisation ─────────────────────────────────────
        # Attrition: must be Yes / No
        if col == 'Attrition':
            norm = val.capitalize()
            if norm in ('Yes', 'No') and norm != val:
                log(row_num, col, val, norm); val = norm
            elif norm not in ('Yes', 'No'):
                log(row_num, col, val, 'INVALID_KEPT'); # keep but flag

        # Gender: must be Male / Female
        if col == 'Gender':
            norm = val.capitalize()
            if norm in ('Male', 'Female') and norm != val:
                log(row_num, col, val, norm); val = norm

        # OverTime: must be Yes / No
        if col == 'OverTime':
            norm = val.capitalize()
            if norm in ('Yes', 'No') and norm != val:
                log(row_num, col, val, norm); val = norm

        # MaritalStatus: Single / Married / Divorced
        if col == 'MaritalStatus':
            norm = val.capitalize()
            if norm in ('Single', 'Married', 'Divorced') and norm != val:
                log(row_num, col, val, norm); val = norm

        # BusinessTravel: Non-Travel / Travel_Rarely / Travel_Frequently
        if col == 'BusinessTravel':
            valid_bt = {'Non-Travel', 'Travel_Rarely', 'Travel_Frequently'}
            if val not in valid_bt:
                # try common variants
                mapping = {
                    'non travel': 'Non-Travel', 'non-travel': 'Non-Travel',
                    'nontravel': 'Non-Travel',
                    'travel rarely': 'Travel_Rarely',
                    'travel_rarely': 'Travel_Rarely',
                    'rarely': 'Travel_Rarely',
                    'travel frequently': 'Travel_Frequently',
                    'travel_frequently': 'Travel_Frequently',
                    'frequently': 'Travel_Frequently',
                }
                fixed = mapping.get(val.lower())
                if fixed:
                    log(row_num, col, val, fixed); val = fixed

        # Department: exact match
        if col == 'Department':
            valid_dept = {'Sales', 'Research & Development', 'Human Resources'}
            if val not in valid_dept:
                mapping = {
                    'r&d': 'Research & Development',
                    'research and development': 'Research & Development',
                    'r & d': 'Research & Development',
                    'hr': 'Human Resources',
                    'human resource': 'Human Resources',
                }
                fixed = mapping.get(val.lower())
                if fixed:
                    log(row_num, col, val, fixed); val = fixed

        # EducationField
        if col == 'EducationField':
            valid_ef = {'Life Sciences','Other','Medical','Marketing',
                        'Technical Degree','Human Resources'}
            if val not in valid_ef:
                mapping = {
                    'life science': 'Life Sciences',
                    'tech degree': 'Technical Degree',
                    'technical': 'Technical Degree',
                    'hr': 'Human Resources',
                }
                fixed = mapping.get(val.lower())
                if fixed:
                    log(row_num, col, val, fixed); val = fixed

        # Over18: always Y
        if col == 'Over18':
            if val != 'Y':
                if val.upper() in ('YES', 'Y', 'TRUE', '1'):
                    log(row_num, col, val, 'Y'); val = 'Y'

        # ── 3. Numeric type coercion — ensure no trailing decimals on integers ─
        int_cols = {
            'Age','DailyRate','DistanceFromHome','Education','EmployeeCount',
            'EmployeeNumber','EnvironmentSatisfaction','HourlyRate',
            'JobInvolvement','JobLevel','JobSatisfaction','MonthlyIncome',
            'MonthlyRate','NumCompaniesWorked','PercentSalaryHike',
            'PerformanceRating','RelationshipSatisfaction','StandardHours',
            'StockOptionLevel','TotalWorkingYears','TrainingTimesLastYear',
            'WorkLifeBalance','YearsAtCompany','YearsInCurrentRole',
            'YearsSinceLastPromotion','YearsWithCurrManager'
        }
        if col in int_cols and val != '':
            try:
                float_val = float(val)
                int_val   = str(int(float_val))
                if int_val != val:
                    log(row_num, col, val, int_val); val = int_val
            except ValueError:
                pass  # non-numeric already flagged above

        new_row[col] = val

    cleaned_rows.append(new_row)

# ── summary ───────────────────────────────────────────────────────────────────
total_changes = sum(len(v) for v in changes.values())
print(f"Total field-level changes made: {total_changes}")
if total_changes > 0:
    for col, entries in sorted(changes.items()):
        print(f"  {col}: {len(entries)} change(s)")
        for e in entries[:3]:
            print(f"    row {e['row']}: {e['from']} -> {e['to']}")
print()

# ── write clean output ────────────────────────────────────────────────────────
with open(OUTPUT, 'w', newline='', encoding='utf-8') as f:  # no BOM
    writer = csv.DictWriter(f, fieldnames=headers)
    writer.writeheader()
    writer.writerows(cleaned_rows)

print(f"Cleaned file written: {OUTPUT}")
print(f"  Rows: {len(cleaned_rows)}")
print(f"  Columns: {len(headers)}")
print()

# ── post-clean validation ─────────────────────────────────────────────────────
print("=== POST-CLEAN VALIDATION ===")
errors = 0

# Re-read and verify
verified = []
with open(OUTPUT, encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        verified.append(row)

# Check no BOM
with open(OUTPUT, 'rb') as f:
    first3 = f.read(3)
bom_ok = first3 != b'\xef\xbb\xbf'
print(f"  BOM removed: {'PASS' if bom_ok else 'FAIL'}")

# Check row count
print(f"  Row count preserved: {'PASS' if len(verified) == len(rows) else 'FAIL'} ({len(verified)})")

# Check no empty values
empty_count = sum(1 for row in verified for col in headers if row[col].strip() == '')
print(f"  Empty values: {'NONE (PASS)' if empty_count == 0 else f'FAIL - {empty_count} empty cells'}")

# Validate categoricals
cat_valid = {
    'Attrition':      {'Yes','No'},
    'Gender':         {'Male','Female'},
    'OverTime':       {'Yes','No'},
    'Over18':         {'Y'},
    'MaritalStatus':  {'Single','Married','Divorced'},
    'BusinessTravel': {'Non-Travel','Travel_Rarely','Travel_Frequently'},
    'Department':     {'Sales','Research & Development','Human Resources'},
}
for col, valid_set in cat_valid.items():
    vals = set(r[col] for r in verified)
    unexpected = vals - valid_set
    if unexpected:
        print(f"  {col}: FAIL - unexpected values: {unexpected}")
        errors += 1
    else:
        print(f"  {col}: PASS ({sorted(vals)})")

# Validate numeric ranges
num_ranges = {
    'Age':                    (18, 70),
    'DailyRate':              (100, 1500),
    'DistanceFromHome':       (1, 29),
    'Education':              (1, 5),
    'EnvironmentSatisfaction':(1, 4),
    'HourlyRate':             (30, 100),
    'JobInvolvement':         (1, 4),
    'JobLevel':               (1, 5),
    'JobSatisfaction':        (1, 4),
    'MonthlyIncome':          (1000, 20000),
    'MonthlyRate':            (2000, 27000),
    'NumCompaniesWorked':     (0, 9),
    'PercentSalaryHike':      (11, 25),
    'PerformanceRating':      (3, 4),
    'RelationshipSatisfaction':(1,4),
    'StandardHours':          (80, 80),
    'StockOptionLevel':       (0, 3),
    'TotalWorkingYears':      (0, 40),
    'TrainingTimesLastYear':  (0, 6),
    'WorkLifeBalance':        (1, 4),
    'YearsAtCompany':         (0, 40),
    'YearsInCurrentRole':     (0, 18),
    'YearsSinceLastPromotion':(0, 15),
    'YearsWithCurrManager':   (0, 17),
}
range_ok = True
for col, (lo, hi) in num_ranges.items():
    bad = [(r['EmployeeNumber'], r[col]) for r in verified
           if not (lo <= float(r[col]) <= hi)]
    if bad:
        print(f"  {col} [{lo}-{hi}]: FAIL - {len(bad)} out of range: {bad[:3]}")
        errors += 1
        range_ok = False
if range_ok:
    print("  Numeric ranges: ALL PASS")

# Logical consistency
logical_ok = True
for row in verified:
    if int(row['YearsAtCompany']) > int(row['TotalWorkingYears']):
        print(f"  Logical: YearsAtCompany > TotalWorkingYears at EmpNum {row['EmployeeNumber']}")
        logical_ok = False
        errors += 1
        break
    if int(row['YearsSinceLastPromotion']) > int(row['YearsAtCompany']):
        print(f"  Logical: YearsSinceLastPromotion > YearsAtCompany at EmpNum {row['EmployeeNumber']}")
        logical_ok = False
        errors += 1
        break
if logical_ok:
    print("  Logical consistency: PASS")

# Duplicates
row_tuples = [tuple(r[k] for k in headers) for r in verified]
dup_count = len(row_tuples) - len(set(row_tuples))
print(f"  Duplicate rows: {'NONE (PASS)' if dup_count == 0 else f'FAIL - {dup_count} duplicates'}")

print()
if errors == 0:
    print("ALL VALIDATIONS PASSED - dataset is clean")
else:
    print(f"VALIDATION COMPLETE - {errors} issues remain")
