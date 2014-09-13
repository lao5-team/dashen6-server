#! /usr/bin/env python
#
# author: yafei
# mongodb test
import pymongo

# configurations
hostname='localhost'
port=27017
db_name='db1'
user_table='user'
activity_table='activity'

# db code
con=pymongo.Connection(hostname, port)
db=con[db_name]
user_coll=db[user_table]
activity_coll=db[activity_table]
user_coll.remove()
activity_coll.remove()

# test code
user_coll.insert([
    {'name':'laowu'},
    {'name':'yafei'},
    {'name':'kunzi'}
])

user_coll.find_and_modify(
    query={'name':'laowu'},
    update={'$push':{'activity':128}}
)

user_coll.find_and_modify(
    query={'name':'laowu'},
    update={'$push':{'activity':{'$each':[129,130]}}}
)

user_coll.find_and_modify(
    query={'name':'not exist'},
    update={'$push':{'activity':128}}
)

bulk=user_coll.initialize_ordered_bulk_op()
for i in range(10,20):
    bulk.insert({'key %d' % i:'value %d' % i})
bulk.execute()

for item in user_coll.find():
    print item
