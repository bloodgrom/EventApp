import shutil
import os
from datetime import date

today = date.today()
#today = today.strftime("%d-%m-%Y")

script_path = os.path.abspath(__file__) # i.e. /path/to/dir/foobar.py
script_dir = os.path.split(script_path)[0] #i.e. /path/to/dir/

rel_path_origin = "CalendarApp/db.sqlite3"
rel_path_backup = "CalendarApp/db_backup/db_" + str(today) + ".sqlite3"
original_db = os.path.join(script_dir, rel_path_origin)
backup_db = os.path.join(script_dir, rel_path_backup)

shutil.copyfile(original_db, backup_db)

print("DB copied successfuly")