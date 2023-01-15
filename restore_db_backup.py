import shutil
import os
from datetime import date

script_path = os.path.abspath(__file__) # i.e. /path/to/dir/foobar.py
script_dir = os.path.split(script_path)[0] #i.e. /path/to/dir/

rel_path_backup_folder = "CalendarApp\db_backup"

backup_db_folder = os.path.join(script_dir, rel_path_backup_folder)

file_list = []

for file in os.listdir(backup_db_folder):
  if file.endswith(".sqlite3"):
      file_list.append(file)
      
sorted_list = sorted(file_list, reverse=True)

if len(sorted_list) > 0:

  latest_db_backup = sorted_list[0]
  
  db_backup_path = "CalendarApp\db_backup\\" + latest_db_backup
  db_backup_path_abs = os.path.join(script_dir, db_backup_path)
  
  rel_path_target = "CalendarApp\db.sqlite3"
  
  shutil.copyfile(db_backup_path_abs, rel_path_target)
  
  print("DB restored successfuly")

else:
  print("No backups available")