from sqlalchemy import Table, MetaData
from app import db

conn = db.engine.connect()
meta = MetaData(bind=db.engine)

projects = Table('projects', meta, autoload=True)
conn.execute(projects.insert(), name='test')

a = projects.select(projects.c.name == 'test').execute()
for aa in a: print(aa)

a = projects.select(projects.c.name == 'test').execute().first()
print(a)


# from sqlalchemy import Table
# from app import db
#
# conn = db.conn
# meta = db.Base.metadata
#
# users = Table('users', meta, autoload=True)
# # conn.execute(users.insert(), nickname='debbie', usermail='debbie@ciceron.me', password='1111')
# result = users.select(users.c.id == 2).execute().first()
# print(result)
#
# conn.close()
