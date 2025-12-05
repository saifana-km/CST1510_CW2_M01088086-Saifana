from data.db import connect_database
from data.schema import create_all_tables
from services.user_service import register_user, login_user, migrate_users_from_file
from data.incidents import insert_incident, get_all_incidents
from pathlib import Path
DATA_DIR = Path("DATA")

conn = connect_database()
cursor = conn.cursor()
cursor.execute("DELETE FROM users WHERE username = 'saikm'")
conn.commit()
cursor.execute("DELETE FROM users WHERE username = 'username'")
conn.commit()
conn.close()