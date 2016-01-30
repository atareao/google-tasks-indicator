#!/usr/bin/python
# -*- coding: utf-8 -*-
#
__author__='lorenzo.carbonell.cerezo@gmail.com'
__date__ ='$21/02/2012'
#
# Google-Tasks-Indicator
# An indicator for Google Tasks
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
import os
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import GObject
from gi.repository import AppIndicator3 as appindicator
from gi.repository import Gtk
from gi.repository import GdkPixbuf
from gi.repository import Notify

import time
import dbus
import locale
import gettext
import datetime
import webbrowser
import rfc3339
#
import comun
import googletasksapi
from configurator import Configuration
from preferences_dialog import Preferences
from task_dialog import TaskDialog
from tasklist_dialog import TaskListDialog
from show_tasks_dialog import ShowTasksDialog
from show_taskslists_dialog import ShowTasksListsDialog
#

locale.setlocale(locale.LC_ALL, '')
gettext.bindtextdomain(comun.APP, comun.LANGDIR)
gettext.textdomain(comun.APP)
_ = gettext.gettext

def internet_on():
	try:
		response=urllib2.urlopen('http://google.com',timeout=1)
		return True
	except:
		pass
	return False

class MenuNote(Gtk.CheckMenuItem):
	def __init__(self,note):
		Gtk.CheckMenuItem.__init__(self)
		self.note = note
		#self.get_children()[0].set_use_markup(True)
		if 'title' in note.keys() and note['title'] is not None:
			if len(note['title'])>28:
				title = note['title'][0:25]+'...'
			else:
				title = note['title']
		else:
			title = ''
		if 'notes' in note.keys() and note['notes'] is not None:
			self.set_tooltip_text(note['notes'])
		if note['status'] == 'completed':
			self.set_label(title)
			self.set_active(True)
		else:
			self.set_label(title)
			self.set_active(False)
			
	def get_note(self):
		return self.note
		
	def set_note(self,note):
		self.note = note
		if 'status' in note.keys() and note['status'] == 'completed':
			self.set_active(True)
		else:
			self.set_active(False)
		if 'title' in note.keys() and note['title'] is not None:
			if len(note['title'])>28:
				title = note['title'][0:25]+'...'
			else:
				title = note['title']
		else:
			title = ''
		self.set_label(title)
			

def add2menu(menu, text = None, icon = None, conector_event = None, conector_action = None, note = None):
	if note != None:
		menu_item = MenuNote(note)
	else:
		if text != None:
			if icon == None:
				menu_item = Gtk.MenuItem.new_with_label(text)
			else:
				menu_item = Gtk.ImageMenuItem.new_with_label(text)
				image = Gtk.Image.new_from_stock(icon, Gtk.IconSize.MENU)
				menu_item.set_image(image)
				menu_item.set_always_show_image(True)
		else:
			if icon == None:
				menu_item = Gtk.SeparatorMenuItem()
			else:
				menu_item = Gtk.ImageMenuItem.new_from_stock(icon, None)
				menu_item.set_always_show_image(True)
	if conector_event != None and conector_action != None:				
		menu_item.connect(conector_event,conector_action)
	menu_item.show()
	menu.append(menu_item)
	return menu_item

class GoogleTasksIndicator():
	def __init__(self):
		if dbus.SessionBus().request_name("es.atareao.google-tasks-indicator") != dbus.bus.REQUEST_NAME_REPLY_PRIMARY_OWNER:
			print("application already running")
			exit(0)
		self.indicator = appindicator.Indicator.new('Google-Tasks-Indicator', 'Google-Tasks-Indicator', appindicator.IndicatorCategory.APPLICATION_STATUS)
		self.notification = Notify.Notification.new('','', None)
		self.tasks = googletasksapi.TaskAlone()
		self.tasks.restore()
		if self.tasks.tasklists == {}:
			tld = TaskListDialog()
			if tld.run() == Gtk.ResponseType.ACCEPT:
				tld.hide()
				self.tasks.create_tasklist(tld.get_title())
			tld.destroy()
		self.read_preferences()
		self.set_menu()
		self.menu_update()
		
	def on_destroy(self):
		self.tasks.backup()
		
	def sync(self,widget):
		gta = googletasksapi.GTAService(token_file = comun.TOKEN_FILE)
		error = True
		while(error):
			if gta.do_refresh_authorization() is None:
				p = Preferences(self.tasks)
				if p.run() == Gtk.ResponseType.ACCEPT:
					p.save_preferences()
				p.destroy()
				gta = googletasksapi.GTAService(token_file = comun.TOKEN_FILE)
				if (not os.path.exists(comun.TOKEN_FILE)) or (gta.do_refresh_authorization() is None):
					md = Gtk.MessageDialog(	parent = None,
											flags = Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT,
											type = Gtk.MessageType.ERROR,
											buttons = Gtk.ButtonsType.OK_CANCEL,
											message_format = _('You have to authorize Google-Tasks-Indicator to manage your Google Calendar.\n Do you want to authorize?'))
					if md.run() == Gtk.ResponseType.CANCEL:
						md.destroy()
						return
					md.destroy()
				else:
					gta = googletasksapi.GTAService(token_file = comun.TOKEN_FILE)
					if gta.do_refresh_authorization() is None:
						error = False
			else:
				error = False
		## Options
		configuration = Configuration()
		option_local = configuration.get('local')
		option_external = configuration.get('external')
		option_both = configuration.get('both')
		##
		google_tasklists = gta.get_tasklists()
		
		## From Local to Google ##
		google_task_lists_ids = []
		for gtl in google_tasklists.values():
			google_task_lists_ids.append(gtl['id'])			
		for tasklist in self.tasks.tasklists.values():
			if tasklist['id'] not in google_task_lists_ids: # Tasklist only local
				if option_local == 0: # Copy to external
					new_tasklist = gta.create_tasklist(tasklist['title'])
					if new_tasklist is not None:
						for task in tasklist['tasks'].values():
							if 'due' in task.keys() and task['due'] is not None:
								due = rfc3339.parse_datetime(str(task['due']))
							else:
								due = None
							new_task = gta.create_task( tasklist_id = new_tasklist['id'], title = task['title'], notes=task['notes'], iscompleted=task.get_completed(),due=due,data_completed=task['completed'])
							new_tasklist['tasks'][new_task['id']] = new_task
						self.tasks.remove_tasklist(tasklist)
						self.tasks.tasklists[new_tasklist['id']] = new_tasklist
				elif option_local == 1: # delete local
					self.tasks.remove_tasklist(tasklist)
			else: # Tasklist local and external;
				if option_both == 0: # Copy to local
					gtl = google_tasklists[tasklist['id']]
					tasklist['title'] = gtl['title']
				elif option_both == 1: # Copy to external
					if gtl['title'] != tasklist['title']:
						gta.edit_tasklist(tasklist['id'],tasklist['title'])
				########################################################
				## Working with tasks
				localtasks = tasklist['tasks']
				googletasks = gta.get_tasks(tasklist_id=tasklist['id'])
				### From Local to Google
				print(localtasks)
				for task in localtasks.values():
					if task['id'] not in googletasks.keys():
						# Task only local
						if option_local == 0:
							# Copy to external
							new_task = gta.create_task( tasklist_id = task['tasklist_id'], title = task['title'], notes=task['notes'], iscompleted=task.get_completed(),due=task['due'],data_completed=task['completed'])
							if new_task is not None:
								self.tasks.remove_task(task)
								self.tasks.tasklists[task['tasklist_id']]['tasks'][new_task['id']] = new_task
						elif option_local == 1:
							# Delete local
							self.tasks.remove_task(task)
					else:
						#Task local and external
						if option_both == 0:
							# Copy to local
							self.tasks.tasklists[task['tasklist_id']]['tasks'][task['id']] = googletasks[task['id']]
						elif option_both ==1:
							# Copy to external
							task_id = task['id']
							tasklist_id = task['tasklist_id']
							title = task['title']
							notes = task['notes']
							iscompleted = (task['status']=='completed')
							due = task['due']
							gta.edit_task(task_id, tasklist_id , title = title, notes = notes, iscompleted = iscompleted, due = due)
				### From Google to Local
				for task in googletasks.values():
					if task['id'] not in localtasks.keys():
						#Task only external
						if option_external == 0:
							# Copy to local
							self.tasks.tasklists[task['tasklist_id']]['tasks'][task['id']] = googletasks[task['id']]
						elif option_external == 1:
							# Delete external
							gta.delete_task(task['id'], task['tasklist_id'])
				########################################################
		## From Google to Local ##
		alone_task_lists_ids = []
		for atl in self.tasks.tasklists.values():
			alone_task_lists_ids.append(atl['id'])			
		for tasklist in google_tasklists.values():
			if tasklist['id'] not in alone_task_lists_ids: # Tasklist only Google
				if option_external == 0: # Copy to local
					new_tasklist = tasklist
					new_tasklist['tasks'] = gta.get_tasks(tasklist_id = tasklist['id'])
					self.tasks.tasklists[new_tasklist['id']] = new_tasklist	
				elif option_external == 1: # Delete external
					gta.delete_tasklist(tasklist)
		self.tasks.backup()
		self.menu_update()
			
	def read_preferences(self):
		error = True
		while error:
			try:
				configuration = Configuration()
				self.tasklist_id = configuration.get('tasklist_id')
				self.theme = configuration.get('theme')
				error = False
			except Exception as e:
				print(e)
				error = True
				p = Preferences()
				if p.run() == Gtk.ResponseType.ACCEPT:
					p.save_preferences()
				else:
					exit(1)
				p.destroy()

	def set_menu(self,check=False):
		#
		normal_icon = os.path.join(comun.ICONDIR,'google-tasks-indicator-%s-normal.svg'%(self.theme))
		starred_icon = os.path.join(comun.ICONDIR,'google-tasks-indicator-%s-starred.svg'%(self.theme))
		#
		self.indicator.set_icon(normal_icon)
		self.indicator.set_attention_icon(starred_icon)		
		#
		menu = Gtk.Menu()
		#
		self.indicator.set_status(appindicator.IndicatorStatus.ACTIVE)
		self.menu_tasks = []
		for i in range(0,10):
			menu_note = add2menu(menu, text = '', conector_event = 'activate',conector_action = self.menu_check_item, note = googletasksapi.Task())
			menu_note.set_visible(False)
			self.menu_tasks.append(menu_note)
			#self.menu_tasks.append(add2menu(menu, text = note['title'], conector_event = 'activate',conector_action = self.menu_check_item, note = note))
		add2menu(menu)
		add2menu(menu, text = _('Add new task'), conector_event = 'activate',conector_action = self.menu_add_new_task)			
		add2menu(menu, text = _('Add new task list'), conector_event = 'activate',conector_action = self.menu_add_new_tasklist)
		add2menu(menu, text = _('Manage tasklists'), conector_event = 'activate',conector_action = self.menu_manage_tasklists)
		add2menu(menu)
		add2menu(menu, text = _('Refresh'), conector_event = 'activate',conector_action = self.menu_refresh)			
		add2menu(menu, text = _('Clear completed tasks'), conector_event = 'activate',conector_action = self.menu_clear_completed_tasks)			
		add2menu(menu, text = _('Show all tasks'), conector_event = 'activate',conector_action = self.menu_show_tasks)
		add2menu(menu, text = _('Synchronize with Google'), conector_event = 'activate',conector_action = self.sync)
		add2menu(menu)
		add2menu(menu)
		add2menu(menu, text = _('Preferences'), conector_event = 'activate',conector_action = self.menu_preferences_response)
		add2menu(menu)
		menu_help = add2menu(menu, text =_('Help'))
		menu_help.set_submenu(self.get_help_menu())
		add2menu(menu)
		add2menu(menu, text = _('Exit'), conector_event = 'activate',conector_action = self.menu_exit_response)
		menu.show()
		self.indicator.set_menu(menu)
		

	def get_help_menu(self):
		help_menu =Gtk.Menu()
		#		
		add2menu(help_menu,text = _('Web...'),conector_event = 'activate',conector_action = lambda x: webbrowser.open('https://launchpad.net/google-tasks-indicator'))
		add2menu(help_menu,text = _('Get help online...'),conector_event = 'activate',conector_action = lambda x: webbrowser.open('https://answers.launchpad.net/google-tasks-indicator'))
		add2menu(help_menu,text = _('Translate this application...'),conector_event = 'activate',conector_action = lambda x: webbrowser.open('https://translations.launchpad.net/google-tasks-indicator'))
		add2menu(help_menu,text = _('Report a bug...'),conector_event = 'activate',conector_action = lambda x: webbrowser.open('https://bugs.launchpad.net/google-tasks-indicator'))
		add2menu(help_menu)
		self.menu_about = add2menu(help_menu,text = _('About'),conector_event = 'activate',conector_action = self.menu_about_response)
		#
		help_menu.show()
		#
		return help_menu

	def menu_preferences_response(self,widget):
		widget.set_sensitive(False)
		p = Preferences(self.tasks)
		if p.run() == Gtk.ResponseType.ACCEPT:
			p.save_preferences()
		p.destroy()
		self.read_preferences()
		self.menu_update()
		widget.set_sensitive(True)
	
	def menu_edit_note(self,widget):
		widget.set_sensitive(False)
		note = widget.note
		annd = NoteDialog(note = note)
		if annd.run() == Gtk.ResponseType.ACCEPT:
			atasklist = self.tasks.tasklists[annd.get_tasklist_id()]
			note = self.tasks.create_task(self,atasklist,title)
			note['notes'] = annd.get_notes()
			note.set_completed(annd.is_completed())
			due = annd.get_due_date()
			if due is not None:
				note.set_due(due)			
			self.menu_update()
		annd.destroy()
		widget.set_active(widget.get_note()['status'] == 'completed')
		widget.set_sensitive(True)	
			
	def menu_check_item(self,widget):
		completed = not widget.get_active()
		atask = widget.get_note()
		if 'notes' in atask.keys():
			notes = atask['notes']
		else:
			notes = ''
		atask.set_completed(iscompleted = not completed)
		#self.tasks.tasklists[atask['tasklist_id']]['tasks']
		widget.set_note(atask)
		widget.set_active(atask['status'] == 'completed')
	def menu_manage_tasklists(self,widget):
		widget.set_sensitive(False)
		stld = ShowTasksListsDialog(self.tasks)
		stld.run()
		stld.destroy()
		self.menu_update()
		widget.set_sensitive(True)
	def menu_add_new_tasklist(self,widget):
		widget.set_sensitive(False)
		tld = TaskListDialog()
		if tld.run() == Gtk.ResponseType.ACCEPT:
			tld.hide()
			self.tasks.create_tasklist(tld.get_title())
		tld.destroy()
		self.menu_update()
		widget.set_sensitive(True)
				
	def menu_add_new_task(self,widget):
		widget.set_sensitive(False)
		annd = TaskDialog(tasks=self.tasks)
		if annd.run() == Gtk.ResponseType.ACCEPT:
			annd.hide()			
			tasklist = self.tasks.tasklists[annd.get_tasklist_id()]
			atask = self.tasks.create_task(tasklist,annd.get_title())
			atask['notes'] = annd.get_notes()
			atask.set_completed(annd.is_completed())
			due = annd.get_due_date()
			if due is not None:
				atask.set_due(due)						
		annd.destroy()
		self.menu_update()
		widget.set_sensitive(True)
		
	def menu_update(self):
		number_of_tasks = len(self.tasks.get_tasks(tasklist_id = self.tasklist_id)[:10])
		if number_of_tasks < 10:
			for index,note in enumerate(self.tasks.get_tasks(tasklist_id = self.tasklist_id)[:number_of_tasks]):
				self.menu_tasks[index].set_note(note)
				self.menu_tasks[index].set_visible(True)
			for index in range(number_of_tasks,10):
				self.menu_tasks[index].set_visible(False)
		else:
			for index,note in enumerate(self.tasks.get_tasks(tasklist_id = self.tasklist_id)[:10]):
				self.menu_tasks[index].set_note(note)
				self.menu_tasks[index].set_visible(True)
			
	def menu_clear_completed_tasks(self,widget):
		widget.set_sensitive(False)
		self.tasks.clear_completed_tasks(tasklist_id = self.tasklist_id)		
		self.menu_update()
		widget.set_sensitive(True)
		
	def menu_refresh(self,widget):
		widget.set_sensitive(False)
		self.menu_update()
		widget.set_sensitive(True)
		
	def menu_show_tasks(self,widget):
		widget.set_sensitive(False)
		snd = ShowTasksDialog(self.tasks, self.tasklist_id)
		snd.run()
		snd.destroy()
		self.menu_update()
		widget.set_sensitive(True)

	def menu_exit_response(self,widget):
		self.tasks.backup()
		exit(0)

	def menu_about_response(self,widget):
		widget.set_sensitive(False)
		ad=Gtk.AboutDialog()
		ad.set_name(comun.APPNAME)
		ad.set_version(comun.VERSION)
		ad.set_copyright('Copyrignt (c) 2012\nLorenzo Carbonell')
		ad.set_comments(_('An indicator for Google Tasks'))
		ad.set_license(''+
		'This program is free software: you can redistribute it and/or modify it\n'+
		'under the terms of the GNU General Public License as published by the\n'+
		'Free Software Foundation, either version 3 of the License, or (at your option)\n'+
		'any later version.\n\n'+
		'This program is distributed in the hope that it will be useful, but\n'+
		'WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY\n'+
		'or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for\n'+
		'more details.\n\n'+
		'You should have received a copy of the GNU General Public License along with\n'+
		'this program.  If not, see <http://www.gnu.org/licenses/>.')
		ad.set_website('http://www.atareao.es')
		ad.set_website_label('http://www.atareao.es')
		ad.set_authors(['Lorenzo Carbonell <lorenzo.carbonell.cerezo@gmail.com>'])
		ad.set_documenters(['Lorenzo Carbonell <lorenzo.carbonell.cerezo@gmail.com>'])
		ad.set_logo(GdkPixbuf.Pixbuf.new_from_file(comun.ICON))
		ad.set_program_name(comun.APPNAME)
		ad.run()
		ad.destroy()
		widget.set_sensitive(True)

if __name__ == "__main__":
	Notify.init("google-tasks-indicator")
	gti=GoogleTasksIndicator()
	Gtk.main()
	print('eo')

