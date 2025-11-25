import csv, random, hashlib, datetime
from pathlib import Path

# Helper functions
roles = ['user', 'admin', 'analyst']
incident_types = ['Phishing', 'Malware', 'DDoS', 'Ransomware', 'Data Breach']
severities = ['Critical', 'High', 'Medium', 'Low']
statuses = ['Open', 'Investigating', 'Resolved', 'Closed']
ticket_priorities = severities
categories = ['Network', 'Hardware', 'Software', 'Access', 'Security']

def random_date(start="2023-01-01", end="2025-01-01"):
    start_dt = datetime.datetime.fromisoformat(start)
    end_dt = datetime.datetime.fromisoformat(end)
    delta = end_dt - start_dt
    rand = random.randrange(delta.days * 24 * 3600)
    return (start_dt + datetime.timedelta(seconds=rand)).strftime('%Y-%m-%d %H:%M:%S')

# ---- USERS ----
def make_users(n=10):
    rows = []
    for i in range(n):
        username = f'user{i+1}'
        password_hash = hashlib.sha256(f'pass{i+1}'.encode()).hexdigest()
        role = random.choice(roles)
        created_at = random_date()
        rows.append([i+1, username, password_hash, role, created_at])

    with open('users.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['id','username','password_hash','role','created_at'])
        writer.writerows(rows)

# ---- CYBER INCIDENTS ----
def make_incidents(n=50):
    rows = []
    for i in range(n):
        dt = random_date()
        itype = random.choice(incident_types)
        sev = random.choice(severities)
        status = random.choice(statuses)
        desc = f"Auto-generated incident {i+1}"
        rep = f'user{random.randint(1,10)}'
        rows.append([i+1, dt, itype, sev, status, desc, rep, random_date()])

    with open('cyber_incidents.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['id','date','incident_type','severity','status','description','reported_by','created_at'])
        writer.writerows(rows)

# ---- DATASETS METADATA ----
def make_metadata(n=100):
    rows = []
    for i in range(n):
        dname = f'dataset_{i+1}'
        cat = random.choice(['Security','Operations','HR','Network','Threat Intel'])
        source = random.choice(['Internal','External','Partner','Open Source'])
        updated = random_date()
        rc = random.randint(50,10000)
        fsize = round(random.uniform(0.5,500),2)
        rows.append([i+1, dname, cat, source, updated, rc, fsize, random_date()])

    with open('datasets_metadata.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['id','dataset_name','category','source','last_updated','record_count','file_size_mb','created_at'])
        writer.writerows(rows)

# ---- IT TICKETS ----
def make_tickets(n=50):
    rows = []
    for i in range(n):
        ticket_id = f'TKT-{1000+i}'
        pr = random.choice(ticket_priorities)
        status = random.choice(statuses)
        cat = random.choice(categories)
        subject = f"Issue {i+1}"
        desc = f"Auto-generated ticket {i+1}"
        created = random_date()
        resolved = random_date() if status in ['Resolved','Closed'] else ''
        assigned = f'tech{random.randint(1,5)}'
        rows.append([i+1,ticket_id,pr,status,cat,subject,desc,created,resolved,assigned,random_date()])

    with open('it_tickets.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['id','ticket_id','priority','status','category','subject','description','created_date','resolved_date','assigned_to','created_at'])
        writer.writerows(rows)

# ---- Generate All Files ----
make_users()
make_incidents()
make_metadata()
make_tickets()

print("CSV files generated successfully!")
