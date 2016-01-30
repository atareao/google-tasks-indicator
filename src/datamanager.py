#!/usr/bin/python
# -*- coding: utf-8 -*-
#
__author__='atareao'
__date__ ='$19/02/2012'
#
#
# Copyright (C) 2012 Lorenzo Carbonell
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

import codecs
import os
import json
import comun
import uuid

DATA = {
		'tasklists':[],
		'tasks':[]
		}

TASKLIST = {'id':'',
			'kind':'tasks#taskList',
			'title':'',
			'updated':'',
			'selfLink':'',
			'on-google':False,
			}

TASK = 	   {'id':'',
			'tasklist_id':'',
			'kind':'tasks#task',
			'title':'',
			'notes':'',
			'position':'',
			'status':'needsAction',
			'updated':'',
			'on-google':False,
			'etag':'',
			'selfLink':''
}
class Task(object):
	def __init__(self,tasklist_id):
		self.task = TASK.copy()
		self.task['id'] = str(uuid.uuid1())
		task['tasklist_id'] = tasklist_id
		
	def __eq__(self,other):
		return (self.task['id'] == other.task['id'])

class TaskList(object):
	def __init__(self):
		self.tasklist = TASKLIST.copy()
		self.tasklist['id'] = str(uuid.uuid1())
		
	def __eq__(self,other):
		return (self.tasklist['id'] == other.tasklist['id'])

class DataManager(object):
	def __init__(self):
		self.data = DATA.copy()
		self.read()
	
	def create_tasklist(self):
		self.data['tasklists'].append(tasklist)
		return tasklist
	
	def create_task(self,tasklist):
		task = TASK.copy()
		task['id'] = str(uuid.uuid1())
		task['tasklist-id'] = tasklist['id']
		self.data['tasks'].append(task)

	def get_tasklists(self):
		return self.data['tasklists']

	def get_tasks(self):
		return self.data['tasks']


	def get_tasklist(self,tasklist_id):
		for tasklist in self.data['tasklists']:
			if tasklist['id'] == tasklist_id:
				return tasklist
		return None

	def remove_tasklist(self,tasklist_id):
		tasklist = self.get_tasklist(tasklist_id)
		if tasklist:
			self.data['tasklists'].remove(tasklist)
			
	def get_task(self,task_id):
		for task in self.data['tasks']:
			if task['id'] == task_id:
				return task
		return None

	def remove_task(self,task_id):
		task = self.get_task(task_id)
		if task:
			self.data['task'].remove(task)

			
	def read(self):		
		if os.path.exists(comun.DATA_FILE):
			try:
				f=codecs.open(comun.DATA_FILE,'r','utf-8')
				print 'Read'
			except IOError, e:
				print 'An error:%s'%e
				self.save()
				f=codecs.open(comun.DATA_FILE,'r','utf-8')
				print 'Read'
			values_read = f.read()
			f.close()
			try:
				self.data = json.loads(values_read)
			except ValueError,e:
				print 'An error:%s'%e
				self.save()
				self.read()

	def save(self):
		if not os.path.exists(comun.CONFIG_APP_DIR):
			os.makedirs(comun.CONFIG_APP_DIR)
		f=codecs.open(comun.DATA_FILE,'w','utf-8')
		f.write(json.dumps(self.data))
		f.close()
		print 'Saved'
      
if __name__=='__main__':
	'''
	datamanager = DataManager()
	#tasklist = datamanager.create_tasklist('Lista de prueba')
	#task = datamanager.create_task('Tarea de prueba',tasklist)
	#datamanager.save()	
	print datamanager.data
	'''
	print TaskList().tasklist['id']
