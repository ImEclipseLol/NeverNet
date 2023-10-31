from pysondb import PysonDB


db = PysonDB('testing_db.json')

id = db.add({
    'name': 'adwaith',
    'age': 4,
    'knows_python': True
})
print(id)