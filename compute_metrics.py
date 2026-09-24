import csv, collections, json

rows = []
with open('HR IBM.BOB.CLEANED.csv', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        rows.append(row)

total = len(rows)
attr_yes = [r for r in rows if r['Attrition'] == 'Yes']
attr_no  = [r for r in rows if r['Attrition'] == 'No']

metrics = {
    'total': total,
    'attrition_count': len(attr_yes),
    'attrition_rate': round(len(attr_yes)/total*100, 2),
    'avg_monthly_income': round(sum(int(r['MonthlyIncome']) for r in rows)/total, 2),
    'avg_monthly_income_attr': round(sum(int(r['MonthlyIncome']) for r in attr_yes)/len(attr_yes), 2),
    'avg_monthly_income_retain': round(sum(int(r['MonthlyIncome']) for r in attr_no)/len(attr_no), 2),
    'avg_age': round(sum(int(r['Age']) for r in rows)/total, 2),
    'avg_age_attr': round(sum(int(r['Age']) for r in attr_yes)/len(attr_yes), 2),
    'avg_years_company': round(sum(int(r['YearsAtCompany']) for r in rows)/total, 2),
    'avg_years_company_attr': round(sum(int(r['YearsAtCompany']) for r in attr_yes)/len(attr_yes), 2),
}
print(json.dumps(metrics, indent=2))

def group_stats(key_fn, rows):
    g = collections.defaultdict(lambda: {'total':0,'attr':0})
    for r in rows:
        k = key_fn(r)
        g[k]['total'] += 1
        if r['Attrition'] == 'Yes':
            g[k]['attr'] += 1
    return {k: {'total':v['total'],'attr':v['attr'],'pct':round(v['attr']/v['total']*100,1)} for k,v in g.items()}

print('\n--- Department ---')
dept = group_stats(lambda r: r['Department'], rows)
for k,v in sorted(dept.items()): print(f"  {k}: {v}")

print('\n--- JobRole ---')
roles = group_stats(lambda r: r['JobRole'], rows)
for k,v in sorted(roles.items(), key=lambda x: x[1]['attr'], reverse=True): print(f"  {k}: {v}")

print('\n--- OverTime ---')
ot = group_stats(lambda r: r['OverTime'], rows)
for k,v in sorted(ot.items()): print(f"  {k}: {v}")

print('\n--- Gender ---')
gen = group_stats(lambda r: r['Gender'], rows)
for k,v in sorted(gen.items()): print(f"  {k}: {v}")

print('\n--- JobSatisfaction ---')
js = group_stats(lambda r: r['JobSatisfaction'], rows)
for k,v in sorted(js.items()): print(f"  Level {k}: {v}")

print('\n--- WorkLifeBalance ---')
wlb = group_stats(lambda r: r['WorkLifeBalance'], rows)
for k,v in sorted(wlb.items()): print(f"  Level {k}: {v}")

print('\n--- MaritalStatus ---')
ms = group_stats(lambda r: r['MaritalStatus'], rows)
for k,v in sorted(ms.items()): print(f"  {k}: {v}")

print('\n--- BusinessTravel ---')
bt = group_stats(lambda r: r['BusinessTravel'], rows)
for k,v in sorted(bt.items()): print(f"  {k}: {v}")

def dist_bucket(r):
    d = int(r['DistanceFromHome'])
    if d <= 5: return 'Near (1-5)'
    elif d <= 15: return 'Mid (6-15)'
    else: return 'Far (16-29)'

print('\n--- DistanceFromHome ---')
dist = group_stats(dist_bucket, rows)
for k,v in [('Near (1-5)',dist.get('Near (1-5)',{})),('Mid (6-15)',dist.get('Mid (6-15)',{})),('Far (16-29)',dist.get('Far (16-29)',{}))]:
    print(f"  {k}: {v}")

def age_bucket(r):
    a = int(r['Age'])
    if a <= 25: return '18-25'
    elif a <= 35: return '26-35'
    elif a <= 45: return '36-45'
    elif a <= 55: return '46-55'
    else: return '56+'

print('\n--- Age Groups ---')
age = group_stats(age_bucket, rows)
for k in ['18-25','26-35','36-45','46-55','56+']:
    print(f"  {k}: {age.get(k,{})}")

def tenure_bucket(r):
    y = int(r['YearsAtCompany'])
    if y <= 2: return '0-2 yrs'
    elif y <= 5: return '3-5 yrs'
    elif y <= 10: return '6-10 yrs'
    else: return '11+ yrs'

print('\n--- Tenure Groups ---')
tenure = group_stats(tenure_bucket, rows)
for k in ['0-2 yrs','3-5 yrs','6-10 yrs','11+ yrs']:
    print(f"  {k}: {tenure.get(k,{})}")

print('\n--- JobLevel ---')
jl = group_stats(lambda r: r['JobLevel'], rows)
for k,v in sorted(jl.items()): print(f"  Level {k}: {v}")

# High-risk profile
hr_all = [r for r in rows if (
    r['OverTime'] == 'Yes' and
    int(r['JobSatisfaction']) <= 2 and
    int(r['WorkLifeBalance']) <= 2 and
    int(r['YearsAtCompany']) <= 3 and
    int(r['Age']) <= 35
)]
hr_attr = [r for r in hr_all if r['Attrition'] == 'Yes']
print(f'\n--- High-Risk Profile ---')
print(f"  Total matching: {len(hr_all)}, Attrited: {len(hr_attr)}, Rate: {round(len(hr_attr)/len(hr_all)*100,1) if hr_all else 0}%")

# OverTime attr detail
ot_yes_attr = sum(1 for r in rows if r['OverTime']=='Yes' and r['Attrition']=='Yes')
ot_yes_total = sum(1 for r in rows if r['OverTime']=='Yes')
ot_no_attr = sum(1 for r in rows if r['OverTime']=='No' and r['Attrition']=='Yes')
ot_no_total = sum(1 for r in rows if r['OverTime']=='No')
print(f'\nOverTime Yes attr rate: {ot_yes_attr}/{ot_yes_total} = {ot_yes_attr/ot_yes_total*100:.1f}%')
print(f'OverTime No attr rate:  {ot_no_attr}/{ot_no_total} = {ot_no_attr/ot_no_total*100:.1f}%')

# Dept avg income
print('\n--- Avg Income by Dept ---')
dept_income = collections.defaultdict(list)
for r in rows:
    dept_income[r['Department']].append(int(r['MonthlyIncome']))
for d in sorted(dept_income):
    v = dept_income[d]
    print(f"  {d}: avg={round(sum(v)/len(v))}, min={min(v)}, max={max(v)}")
