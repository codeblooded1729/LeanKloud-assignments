from collections import OrderedDict
import os
from flask import Flask, request
from flask_restplus import Api, Resource, fields
from werkzeug.contrib.fixers import ProxyFix
import datetime
import sqlite3 as sql




app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)
api = Api(app, version='1.0', title='TodoMVC API',
    description='A simple TodoMVC API',
)

ns = api.namespace('todos', description='TODO operations')

todo = api.model('Todo', {
    'id': fields.Integer(readonly=True, description='The task unique identifier'),
    'task': fields.String(required=True, description='The task details'),
    'due_by':fields.Date(required=True, description='Due date'),
    'status':fields.String(required=True, description='Current status') 
})

class Task(object):
    def __init__(self,Id,task,due_by,status):
        self.id=Id
        self.task=task
        self.due_by=due_by
        self.status=status

class TodoDAO(object):
    def __init__(self):
        with sql.connect('tasks.db') as conn:
            cursor=conn.execute('SELECT * from TODO')
        self.counter = len(cursor.fetchall())

    def get(self, Id):
        with sql.connect('tasks.db') as conn:
            cursor=conn.execute('SELECT * from TODO where ID=?',(Id,))
        row=None
        for r in cursor:
            row=r
        if not row:
            api.abort(404, "Todo {} doesn't exist".format(id))
        return Task(*row)
        

    def create(self, data):
        if 'task' not in data or 'due_by' not in data:
            return 
        self.counter = self.counter + 1
        Id,task,due_by,status=self.counter,data['task'],datetime.date.fromisoformat(data['due_by']),'not started'
        with sql.connect('tasks.db') as conn:
            conn.execute("INSERT INTO TODO (ID,TASK,DUEBY,STATUS) \
                  VALUES (?,?,?,?)",(Id,task,due_by,status))
        print(self.counter)
        return self.get(Id)

    def update_task(self, Id, data):
        task=data['task']
        with sql.connect('tasks.db') as conn:
            conn.execute("UPDATE TODO set TASK=? where ID=?",(task,Id))
        return self.get(Id)
    
    def start(self,Id):
        with sql.connect('tasks.db') as conn:
            conn.execute("UPDATE TODO set STATUS=? where ID=?",('In progress',Id))
        return self.get(Id)

    def finished(self,Id):
        with sql.connect('tasks.db') as conn:
            conn.execute("UPDATE TODO set STATUS=? where ID=?",('Finished',Id))
        return self.get(Id)

    def delete(self, Id):
        with sql.connect('tasks.db') as conn:
            conn.execute("DELETE from TODO where ID=?",(Id,))


DAO = TodoDAO()

@ns.route('/')
class TodoList(Resource):
    '''Shows a list of all todos, and lets you POST to add new tasks'''
    @ns.doc('list_todos')
    @ns.marshal_list_with(todo)
    def get(self):
        '''List all task'''
        with sql.connect('tasks.db') as conn:
            rows=conn.execute("SELECT id from TODO")
        todos=[DAO.get(row[0]) for row in rows]
        return todos

    @ns.doc('create_todo')
    @ns.expect(todo)
    @ns.marshal_with(todo, code=201)
    def post(self):
        '''Create a new task'''
        data=request.form
        if 'start' in data:
            return DAO.start(data['id'])
        if 'finish' in data:
            return DAO.finished(data['id'])
        return DAO.create(data), 201


@ns.route('/<int:Id>')
@ns.response(404, 'Todo not found')
@ns.param('Id', 'The task identifier')
class Todo(Resource):
    '''Show a single todo item and lets you delete them'''
    @ns.doc('get_todo')
    @ns.marshal_with(todo)
    def get(self, Id):
        '''Fetch a given resource'''
        return DAO.get(Id)

    @ns.doc('delete_todo')
    @ns.response(204, 'Todo deleted')
    def delete(self, Id):
        '''Delete a task given its identifier'''
        DAO.delete(Id)
        return '', 204

    @ns.expect(todo)
    @ns.marshal_with(todo)
    def put(self, Id):
        
        '''Update a task given its identifier'''
        return DAO.update_task(Id, request.form)

@ns.route('/due')
class Due(Resource):
    @ns.marshal_list_with(todo)
    def get(self):
        ''' List of all tasks due on given date'''
        due_date= request.args.get('due_date')
        with sql.connect('tasks.db') as conn:
            rows=conn.execute("SELECT id,task,dueby,status from TODO where DUEBY=?",(due_date,))
        ans=[]
        for row in rows:
            if row[3]!='Finished':
                ans+=[DAO.get(row[0])]
        return ans

@ns.route('/overdue')
class Overdue(Resource):
    @ns.marshal_list_with(todo)
    def get(self):
        '''List of all task overdue by today'''
        today=datetime.date.today()
        with sql.connect('tasks.db') as conn:
            rows=conn.execute("SELECT id,task,dueby,status from TODO")
        ans=[]
        for row in rows:
            if datetime.date.fromisoformat(row[2])<today and row[3]!='Finished':
                ans+=[DAO.get(row[0])]
        return ans

@ns.route('/finished')
class finished(Resource):
    @ns.marshal_list_with(todo)
    def get(self):
        '''List of all finished tasks'''
        with sql.connect('tasks.db') as conn:
            rows=conn.execute("SELECT id,status from TODO where STATUS='Finished'")
        ans=[]
        for row in rows:
            ans+=[DAO.get(row[0])]
        return ans  
        


if __name__ == '__main__':
    app.run(debug=True)
