import \
    sqlite3
from pathlib import Path


ROOT_DIR = Path(__file__).parent
DB_NAME = 'db.sqllite3'
DB_FILE = ROOT_DIR / DB_NAME

TABLE_NAME = 'custormers'

con = sqlite3.connect(DB_FILE)
cursos = con.cursor()

cursos.execute(f'CREATE TABLE IF NOT EXISTS {TABLE_NAME}'
               '('
               'id INTEGER PRIMARY KEY AUTOINCREMENT,'
               'name TEXT,'
               'weight REAL'
               ')')

con.commit()

# cursos.execute(f'''
#     INSERT INTO {TABLE_NAME} (name, weight)
#     VALUES (?, ?)
# ''', [
#     'Soso',
#     '95'])
# 
# cursos.executemany(f'''
#     INSERT INTO {TABLE_NAME} (name, weight)
#     VALUES (?, ?)
# ''', [
#     [
#         'Raquel',
#         '60'],
#     [
#         'MeninoEd',
#         '100']])
# 
# cursos.execute(f'''
#     INSERT INTO {TABLE_NAME} (name, weight)
#     VALUES (:name, :weight)
# ''', {'name': 'Nova Pessoa', 'weight': '70'})
# 
# cursos.executemany(f'''
#     INSERT INTO {TABLE_NAME} (name, weight)
#     VALUES (:name, :weight)
# ''', (
#     {'name': 'Joao 1', 'weight': '10'},
#     {'name': 'Joao 2', 'weight': '20'},
#     {'name': 'Joao 3', 'weight': '30'},
#     {'name': 'Joao 4', 'weight': '40'},
#     {'name': 'Joao 5', 'weight': '50'},
# ))
# 
# con.commit()

cursos.execute(f'''SELECT * FROM {TABLE_NAME}''')

for row in cursos.fetchall():
     _id, _name, _weight = row
     print(_id, _name, _weight)
    
con.commit()

cursos.execute(f'''UPDATE {TABLE_NAME}
    SET NAME = :newName
    WHERE ID = :id
''', {"newName": "NOVO VALOR", "id": 1})

con.commit()

# delete sem where
# cursos.execute(f'''
#     DELETE FROM {TABLE_NAME}
# ''')
# 
# cursos.execute(f'''
#     DELETE FROM sqlite_sequence WHERE name = "{TABLE_NAME}"
# ''')
# 
# con.commit()


cursos.close()
con.close()
