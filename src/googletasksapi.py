#!/usr/bin/python
# -*- coding: iso-8859-1 -*-
#
#
# googletasksapi.py
#
# Copyright (C) 2011 Lorenzo Carbonell
# lorenzo.carbonell.cerezo@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#
#
from services import GoogleService
from logindialog import LoginDialog
from urllib.parse import urlencode, quote
import os
import json
import io
import comun 
import datetime
import time
import uuid
import rfc3339
import random

'''
Dependencies:
python-gflags


'''
OAUTH2_URL = 'https://accounts.google.com/o/oauth2/'
AUTH_URL = 'https://accounts.google.com/o/oauth2/auth'
TOKEN_URL = 'https://accounts.google.com/o/oauth2/token'
REDIRECT_URI = 'urn:ietf:wg:oauth:2.0:oob'
REDIRECT_URI = 'http://localhost'
APIKEY = 'AIzaSyDZjnvnk8IBZMUvleSSfGWNnktdKLiKlL0'
CLIENT_ID='197445608333-fd998ofp2ivpj090oputel25imtp7ptk.apps.googleusercontent.com'
CLIENT_SECRET='5So18nKZnWZsKGzOG0pmJUWh'
SCOPE='https://www.googleapis.com/auth/tasks'

class Task(dict):
	def __init__(self,entry=None):
		thetime = datetime.datetime.now()
		position = str(int(time.mktime(thetime.timetuple())))
		if len(position)<20:
			position = '0'*(20-len(position))+position
		self['kind'] = "tasks#task"
		self['id'] = str(uuid.uuid4())
		self['title'] = None
		self['updated'] = rfc3339.rfc3339(thetime)
		self['selfLink'] = None
		self['parent'] = None
		self['position'] = position
		self['notes'] = None
		self['status'] = 'needsAction'
		self['due'] = None
		self['completed'] = None
		self['deleted'] = False
		self['hidden'] = False
		self['links'] = []
		self['tasklist_id'] = None
		self['sync'] = False
		self.set_from_entry(entry)
	
	def set_due(self,due):
		self['due'] = rfc3339.rfc3339(due)
	def get_completed(self):
		return (self['status'] == 'completed')
	def set_completed(self,iscompleted = True):
		if iscompleted:
			self['status'] = 'completed'
			self['completed'] = rfc3339.rfc3339(datetime.datetime.now())
		else:
			self['status'] = 'needsAction'
			self['completed'] = None
			
	def set_from_entry(self,entry):
		if entry is not None:
			self.update(entry)

	def __str__(self):
		ans = ''
		for key in self.keys():
			ans += '%s: %s\n'%(key,self[key])
		return ans
	def get_position(self):
		if 'position' in self.keys():
			return(self['position'])
		return None

	def __eq__(self,other):
		for key in self.keys():
			if key is not None and other is not None and key in other.keys():
				if self[key] != other[key]:
					return False
			else:
				return False
		return True

	def __ne__(self,other):
		return not self.__eq__(other)

	def __lt__(self,other):
		return self.get_position() < other.get_position()

	def __le__(self,other):
		return self.get_position() <= other.get_position()

	def __gt__(self,other):
		return self.get_position() > other.get_position()

	def __ge__(self,other):
		return self.get_position() >= other.get_position()

class TaskList(dict):
	def __init__(self,entry=None):
		self['kind'] = "tasks#taskList"
		self['id'] = str(uuid.uuid4())
		self['title'] = None
		self['updated'] = rfc3339.rfc3339(datetime.datetime.now())
		self['selfLink'] = None
		self.renew_position()
		self['tasks'] = {}
		self.set_from_entry(entry)
		
	def renew_position(self):
		thetime = datetime.datetime.now()
		position = str(int(time.mktime(thetime.timetuple())+random.randint(1,100)))
		if len(position)<20:
			position = '0'*(20-len(position))+position
		self['position'] = position
		
	def set_from_entry(self,entry):
		if entry is not None:			
			self['kind'] =  entry['kind'] if 'kind' in entry.keys() else None
			self['id'] = entry['id'] if 'id' in entry.keys() else None
			self['title'] = entry['title'] if 'title' in entry.keys() else None
			self['updated'] = entry['updated'] if 'updated' in entry.keys() else None
			self['selfLink'] = entry['selfLink'] if 'selfLink' in entry.keys() else None
			if 'position' not in entry.keys():
				self.renew_position()
			else:
				self['position'] = entry['position']
			self['tasks'] = {}
			print('aqui')
			if 'tasks' in entry.keys():
				for atask_value in entry['tasks'].values():
					atask = Task(atask_value)
					self['tasks'][atask['id']] = atask

	def get_position(self):
		if 'position' in self.keys():
			return(self['position'])
		return None

	def set_tasks(self,tasks):
		self['tasks'] = tasks

	def set_title(self,title):
		self['title'] = title
		self['updated'] = rfc3339.rfc3339(datetime.datetime.now())
		
	def __str__(self):
		ans = ''
		for key in self.keys():
			ans += '%s: %s\n'%(key,self[key])
		return ans
		
	def __lt__(self,other):
		return self.get_position() < other.get_position()

	def __le__(self,other):
		return self.get_position() <= other.get_position()

	def __gt__(self,other):
		return self.get_position() > other.get_position()

	def __ge__(self,other):
		return self.get_position() >= other.get_position()

class TaskAlone(object):
	def __init__(self):
		self.tasklists = {}

	def backup(self):
		f = open(comun.BACKUP_FILE,'w')
		f.write(json.dumps(self.tasklists, sort_keys = True, indent = 4))
		f.close()

	def create_tasklist(self,title):
		tasklist = TaskList()
		tasklist['title'] = title
		self.tasklists[tasklist['id']] = tasklist
		return tasklist

	def edit_tasklist(self,tasklist):
		self.tasklists[tasklist['id']] = tasklist
		return tasklist
		
	def remove_tasklist(self,tasklist):
		del self.tasklists[tasklist['id']]
		
	def create_task(self,atasklist,title):
		atask = Task()
		atask['title'] = title
		atask['tasklist_id'] = atasklist['id']
		self.tasklists[atasklist['id']]['tasks'][atask['id']] = atask
		return atask
	
	def edit_task(self,task):
		self.tasklists[task['tasklist_id']]['tasks'][task['id']] = task
		return task

	def remove_task(self,task):
		del self.tasklists[task['tasklist_id']]['tasks'][task['id']]

	def move_tasklists(self,first_tasklist,last_tasklist):
		temporal_position = first_tasklist['position']
		first_tasklist['position'] = last_tasklist['position']
		last_tasklist['position'] = temporal_position
		self.edit_tasklist(first_tasklist)
		self.edit_tasklist(last_tasklist)

	def move_tasklist_first(self,atasklist):
		tasklists = self.get_tasklists()
		if len(tasklists)>0:
			self.move_tasklists(atasklist,tasklists[0])


	def move_tasks(self,first_task,last_task):
		temporal_position = first_task['position']
		first_task['position'] = last_task['position']
		last_task['position'] = temporal_position

	def move_task_first(self,atask,tasklist_id=None):
		tasks = self.get_tasks(tasklist_id)
		if len(tasks)>0:
			self.move_tasks(atask,tasks[0])
			
	def get_tasklists(self):
		return sorted(self.tasklists.values())
		
	def get_tasks(self,tasklist_id = None):
		tasks = []
		if tasklist_id is None:
			for tasklist in self.tasklists.values():
				tasks.extend(tasklist['tasks'].values())
		else:
			if tasklist_id in self.tasklists.keys():
				tasks = self.tasklists[tasklist_id]['tasks'].values()			
		return sorted(tasks)
		
	def clear_completed_tasks(self,tasklist_id = None):
		for task in self.get_tasks(tasklist_id = tasklist_id):
			if task['status'] == 'completed':
				self.remove_task(task)
		
	def restore(self):
		if os.path.exists(comun.BACKUP_FILE):
			f = open(comun.BACKUP_FILE,'r')
			data = f.read()
			f.close()
			midata = json.loads(data)
			self.tasklists = {}
			for tasklist_value in midata.values():
				atasklist = TaskList(tasklist_value)				
				for extasklist in self.tasklists.values():
					if atasklist['position'] == extasklist['position']:
						atasklist.renew_position()
						print(1)
				self.tasklists[atasklist['id']] = atasklist	
		else:
			self.tasklists = {}

class GTAService(GoogleService):
	def __init__(self,token_file):
		GoogleService.__init__(self,auth_url=AUTH_URL,token_url=TOKEN_URL,redirect_uri=REDIRECT_URI,scope=SCOPE,client_id=CLIENT_ID,client_secret=CLIENT_SECRET,token_file=comun.TOKEN_FILE)
		self.tasklists = {}

	def read(self):
		for atasklist in self._get_tasklists().values():
			atasklist['tasks'] = self._get_tasks(atasklist['id'])
			self.tasklists[atasklist['id']] = atasklist

	def backup(self):
		f = open(comun.BACKUP_FILE,'w')
		f.write(json.dumps(self.tasklists, sort_keys = True, indent = 4))
		f.close()

	def restore(self):
		f = open(comun.BACKUP_FILE,'r')
		data = f.read()
		f.close()
		midata = json.loads(data)
		self.tasklists = {}
		for tasklist_value in midata.values():
			atasklist = TaskList(tasklist_value)
			tasks = {}
			for task_value in atasklist['tasks'].values():
				atask = Task(task_value)
				tasks[atask['id']] = atask
			atasklist['tasks'] = tasks
			self.tasklists[atasklist['id']] = atasklist	
		
	def __do_request(self,method,url,addheaders=None,data=None,params=None,first=True):
		headers ={'Authorization':'OAuth %s'%self.access_token}
		if addheaders:
			headers.update(addheaders)
		print(headers)
		if data:
			if params:
				response = self.session.request(method,url,data=data,headers=headers,params=params)		
			else:
				response = self.session.request(method,url,data=data,headers=headers)		
		else:
			if params:
				response = self.session.request(method,url,headers=headers,params=params)
			else:		
				response = self.session.request(method,url,headers=headers)		
		print(response)
		if response.status_code == 200 or response.status_code == 201 or response.status_code == 204:
			return response
		elif (response.status_code == 401 or response.status_code == 403) and first:
			ans = self.do_refresh_authorization()
			print(ans)
			if ans:
				return self.__do_request(method,url,addheaders,data,params,first=False)
		return None

	def _get_tasklists(self):
		tasklists = {}
		params = {'maxResults':1000000}
		response = self.__do_request('GET','https://www.googleapis.com/tasks/v1/users/@me/lists',params=params)		
		if response and response.text:
			try:
				answer = json.loads(response.text)
				if 'items' in answer.keys():
					for item in answer['items']:
						atasklist = TaskList(item)
						tasklists[atasklist['id']] = atasklist
			except:
				pass
		return tasklists

	def _add_tasklist(self,title):
		url = 'https://www.googleapis.com/tasks/v1/users/@me/lists'
		data = {'kind': 'tasks#taskList','title':title}
		body = json.dumps(data).encode('utf-8')
		addheaders={'Content-type':'application/json'}
		response = self.__do_request('POST',url,addheaders=addheaders,data = body)
		if response and response.text:
			try:
				ans = json.loads(response.text)
				print(ans)
				return TaskList(ans)
			except Exception as e:
				print(e)
		return None
	def _edit_tasklist(self,tasklist_id, title):
		params = {'tasklist':tasklist_id}
		url = 'https://www.googleapis.com/tasks/v1/users/@me/lists/%s'%(tasklist_id)
		data = {
		'title':title
		}
		body = json.dumps(data).encode('utf-8')
		addheaders={'Content-type':'application/json'}
		response = self.__do_request('PATCH',url,addheaders=addheaders,params=params,data = body)
		if response and response.text:
			try:
				atasklist = TaskList(json.loads(response.text))
			except Exception as e:
				print(e)
		return None		
	
	def _delete_tasklist(self,tasklist):
		url = 'https://www.googleapis.com/tasks/v1/users/@me/lists/%s'%(tasklist['id'])
		params = {'tasklist':tasklist['id']}
		response = self.__do_request('DELETE',url,params = params)
		if response and response.text:
			try:
				return True
			except Exception as e:
				print(e)
		return False
		
	def _get_tasks(self,tasklist_id = '@default'):
		tasks = {}
		params = {'tasklist':tasklist_id,'maxResults':1000000}
		url =  'https://www.googleapis.com/tasks/v1/lists/%s/tasks'%(tasklist_id)
		response = self.__do_request('GET',url,params=params)		
		if response and response.text:
			try:
				answer = json.loads(response.text)
				if 'items' in answer.keys():
					for item in answer['items']:
						atask = Task(item)
						atask['tasklist_id'] = tasklist_id
						tasks[atask['id']] = atask
			except:
				pass
		return tasks

	def _clear_completed_tasks(self,tasklist_id = '@default'):
		params = {'tasklist':tasklist_id}
		url =  'https://www.googleapis.com/tasks/v1/lists/%s/clear'%(tasklist_id)
		addheaders={'Content-Length':'0'}
		response = self.__do_request('POST',url,params=params,addheaders=addheaders)
		if response is not None:
			try:
				return True
			except Exception as e:
				print(e)
		return False
		
	def _delete_task(self,tasklist_id,task_id):
		params = {'tasklist':tasklist_id,'task':task_id}
		url = 'https://www.googleapis.com/tasks/v1/lists/%s/tasks/%s'%(tasklist_id,task_id)
		response = self.__do_request('DELETE',url,params=params)
		if response and response.text:
			try:
				return True
			except Exception as e:
				print(e)
		return False



	def _edit_task(self,tasklist_id,task_id, title,notes=None, iscompleted=False, due=None, data_completed=None,deleted=False):
		params = {'tasklist':tasklist_id,'task':task_id}
		url = 'https://www.googleapis.com/tasks/v1/lists/%s/tasks/%s'%(tasklist_id,task_id)
		data = {
		'kind': 'tasks#task',
		'title':title,
		'deleted':deleted
		}
		if notes is not None:
			data['notes'] = notes
		if iscompleted:
			data['status'] = 'completed'
			if data_completed is not None:
				data['completed'] = rfc3339.rfc3339(data_completed)
			else:
				data['completed'] = rfc3339.rfc3339(datetime.datetime.now())
		else:
			data['status'] = 'needsAction'
			data['completed'] = None
		if due is not None:
			data['due'] = rfc3339.rfc3339(due)
		body = json.dumps(data).encode('utf-8')
		addheaders={'Content-type':'application/json'}
		response = self.__do_request('PATCH',url,addheaders=addheaders,params=params,data = body)
		if response and response.text:
			try:
				atask = Task(json.loads(response.text))
				atask['tasklist_id'] = tasklist_id
				return atask
			except Exception as e:
				print(e)
		return None		
	def _move_task(self,tasklist_id,task_id,parent_id=None,previous_id=None):
		params = {'tasklist':tasklist_id,'task':task_id}
		if parent_id is not None:
			params['parent'] = parent_id
		if previous_id is not None:
			params['previous'] = previous_id
		addheaders={'Content-Length':'0'}
		url = 'https://www.googleapis.com/tasks/v1/lists/%s/tasks/%s/move'%(tasklist_id,task_id)
		response = self.__do_request('POST',url,params=params,addheaders=addheaders)
		if response and response.text:
			try:
				atask = Task(json.loads(response.text))
				atask['tasklist_id'] = tasklist_id
				return atask
			except Exception as e:
				print(e)
		return None
				
	def _add_task(self,tasklist_id,title,notes=None, iscompleted=False, due=None, data_completed=None,deleted=False):
		params = {'tasklist':tasklist_id}
		url = 'https://www.googleapis.com/tasks/v1/lists/%s/tasks'%(tasklist_id)
		data = {
		'kind': 'tasks#task',
		'title':title,
		'deleted':deleted
		}
		if notes is not None:
			data['notes'] = notes
		if iscompleted:
			data['status'] = 'completed'
			if data_completed is not None:
				data['completed'] = rfc3339.rfc3339(data_completed)
			else:
				data['completed'] = rfc3339.rfc3339(datetime.datetime.now())
		else:
			data['status'] = 'needsAction'
			data['completed'] = None
		if due is not None:
			data['due'] = rfc3339.rfc3339(due)
		body = json.dumps(data).encode('utf-8')
		addheaders={'Content-type':'application/json'}
		response = self.__do_request('POST',url,addheaders=addheaders,params=params,data = body)
		if response and response.text:
			try:
				atask = Task(json.loads(response.text))
				atask['tasklist_id'] = tasklist_id
				return atask
			except Exception as e:
				print(e)
		return None
		
	def get_tasklists(self):
		tasklists = self._get_tasklists()
		return tasklists

	def create_tasklist(self,title):
		return self._add_tasklist(title)

	def update_tasklist(self, tasklist):
		return self._edit_tasklist(tasklist)

	def delete_tasklist(self,tasklist):
		return self._delete_tasklist(tasklist)
		
	def clear_completed_tasks(self,tasklist_id = '@default'):
		return self._clear_completed_tasks(tasklist_id = tasklist_id)
	
	def get_tasks(self, tasklist_id = '@default'):
		tasks = {}
		if tasklist_id is None:
			for atasklist in self._get_tasklists().values():
				for task in self._get_tasks(atasklist['id']).values():
					tasks[task['id']] = task
		else:
			tasks = self._get_tasks(tasklist_id)
		return tasks

	
	def create_task(self, tasklist_id = '@default', title = '', notes=None, iscompleted=False, due=None, data_completed=None,deleted=False):
		atask = self._add_task(tasklist_id,title,notes=notes, iscompleted=iscompleted, due=due, data_completed=data_completed,deleted=deleted)
		return atask

	def move_task(self, task_id, previous_task_id,tasklist_id = '@default'):
		return self._move_task(tasklist_id,task_id,previous_id=previous_task_id) 
		
	def move_task_first(self,task_id, tasklist_id = '@default'):
		return self._move_task(tasklist_id,task_id)

	def edit_tasklist(self, tasklist_id, title):
		return self._edit_tasklist(tasklist_id,title)

	def edit_task(self, task_id, tasklist_id = '@default', title = None, notes = None, iscompleted = False, due = None):
		return self._edit_task(tasklist_id,task_id,title,notes,iscompleted)
	
	def delete_task(self, task_id, tasklist_id = '@default'):
		return self._delete_task(tasklist_id,task_id)

if __name__ == '__main__':	
	ta = TaskAlone()
	ta.restore()
	print(ta.tasklists)
	#tasklist = ta.tasklists['398cecc5-a699-4b4d-94da-5c856244d04c']
	#task = ta.create_task(tasklist,'otra prueba')
	'''
	print(ta.tasklists)
	tasklist = ta.tasklists['398cecc5-a699-4b4d-94da-5c856244d04c']
	tasklist = ta.create_tasklist('lista de prueba')
	print(tasklist)
	task = ta.create_task(tasklist,'prueba')
	print(task)
	print(tasklist)
	print(ta.tasklists)
	
	'''
	'''
	tasklist = ta.create_tasklist('prueba')
	print(tasklist)
	task = ta.create_task(tasklist,'prueba')
	print(task)
	print(tasklist)
	task['title'] = 'La tarea de la lista'
	print(tasklist)
	'''
	ta.backup()
	'''
	
	gta = GTAService(token_file = comun.TOKEN_FILE)
	#gc = GoogleCalendar(token_file = comun.TOKEN_FILE)

	print(gta.do_refresh_authorization())
	if gta.access_token is None or gta.refresh_token is None:
		authorize_url = gta.get_authorize_url()
		print(authorize_url)
		ld = LoginDialog(authorize_url)
		ld.run()
		temporary_token = ld.code
		ld.destroy()
		print(temporary_token)
		print(gta.get_authorization(temporary_token))
	print(gta.get_tasklists())
	#print(gta.create_tasklist('Una lista de ejemplo'))
	#print(gta.get_tasks())
	print'#############################################################'
	print(gta.clear_completed_tasks('@default'))
	print'#############################################################'
	atask = (gta.create_task(tasklist_id='MDU4MDg5OTIxODI5ODgyMTE0MTg6MTA2NTc3MDc0Mzow',title='prueba'))
	print'#############################################################'
	print(atask)
	print'#############################################################'
	gta.move_task_first(atask['id'],atask['tasklist_id'])
	gta.read()
	atask = gta.edit_task(atask['id'],atask['tasklist_id'],title='otra prueba')
	print(atask)
	'''
	'''
	for tasklist in gta.get_tasklists():
		print '########################################################'
		print tasklist
		for task in gta.get_tasks(tasklist_id = tasklist['id']):
			print task
	'''
	
	'''
	for tasklist in gta.get_tasklists():
		print tasklist

	#print gta.create_tasklist('desde ubuntu')
	#print gta.get_tasklist('MDU4MDg5OTIxODI5ODgyMTE0MTg6MDow')
	print gta.get_tasks()
	for task in gta.get_tasks():
		print '%s -> %s'%(task['title'],task['id'])
	#print gta.create_task(title = 'prueba2 desde ubuntu',notes = 'primera prueba')
	gta.move_task_first('MDU4MDg5OTIxODI5ODgyMTE0MTg6MDoy')
	'''
