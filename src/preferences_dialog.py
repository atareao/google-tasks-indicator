#!/usr/bin/python
# -*- utf-8 -*-
#
__author__='atareao'
__date__ ='$19/02/2012$'
#
#
# Copyright (C) 2011,2012 Lorenzo Carbonell
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

from gi.repository import Gtk
import os
import shutil
import locale
import gettext
from configurator import Configuration
from googletasksapi import GTAService
from logindialog import LoginDialog
import comun

locale.setlocale(locale.LC_ALL, '')
gettext.bindtextdomain(comun.APP, comun.LANGDIR)
gettext.textdomain(comun.APP)
_ = gettext.gettext


class Preferences(Gtk.Dialog):
	def __init__(self,tasks=None):
		Gtk.Dialog.__init__(self)
		self.set_title(comun.APPNAME + ' | '+_('Preferences'))
		self.set_modal(True)
		self.add_buttons(Gtk.STOCK_OK, Gtk.ResponseType.ACCEPT,Gtk.STOCK_CANCEL,Gtk.ResponseType.CANCEL)	
		self.set_position(Gtk.WindowPosition.CENTER_ALWAYS)				
		self.set_size_request(400, 170)
		self.set_resizable(False)
		#self.set_icon_from_file(comun.ICON)
		self.connect('destroy', self.close_application)
		#
		vbox0 = Gtk.VBox(spacing = 5)
		vbox0.set_border_width(5)
		self.get_content_area().add(vbox0)
		#
		notebook = Gtk.Notebook()
		vbox0.add(notebook)
		#
		frame2 = Gtk.Frame()
		notebook.append_page(frame2,tab_label = Gtk.Label.new(_('Options')))
		table2 = Gtk.Table(n_rows = 3, n_columns = 2, homogeneous = False)
		table2.set_border_width(5)
		table2.set_col_spacings(5)
		table2.set_row_spacings(5)
		frame2.add(table2)
		#
		label12 = Gtk.Label.new(_('Task List')+':')
		label12.set_alignment(0,.5)
		table2.attach(label12,0,1,0,1, xoptions = Gtk.AttachOptions.FILL, yoptions = Gtk.AttachOptions.SHRINK)
		#
		self.liststore = Gtk.ListStore(str,str)
		self.entry2 = Gtk.ComboBox.new_with_model(model=self.liststore)
		renderer_text = Gtk.CellRendererText()
		self.entry2.pack_start(renderer_text, True)
		self.entry2.add_attribute(renderer_text, "text", 0)
		self.entry2.set_active(0)
		table2.attach(self.entry2,1,2,0,1, xoptions = Gtk.AttachOptions.EXPAND, yoptions = Gtk.AttachOptions.SHRINK)
		#
		label22 = Gtk.Label.new(_('Autostart')+':')
		label22.set_alignment(0,.5)
		table2.attach(label22,0,1,1,2, xoptions = Gtk.AttachOptions.FILL, yoptions = Gtk.AttachOptions.SHRINK)
		#
		self.switch4 = Gtk.Switch()		
		table2.attach(self.switch4,1,2,1,2, xoptions = Gtk.AttachOptions.EXPAND, yoptions = Gtk.AttachOptions.SHRINK)
		#
		label23 = Gtk.Label.new(_('Theme light')+':')
		label23.set_alignment(0,.5)
		table2.attach(label23,0,1,2,3, xoptions = Gtk.AttachOptions.FILL, yoptions = Gtk.AttachOptions.SHRINK)
		#
		self.switch5 = Gtk.Switch()		
		table2.attach(self.switch5,1,2,2,3, xoptions = Gtk.AttachOptions.EXPAND, yoptions = Gtk.AttachOptions.SHRINK)
		#
		frame1 = Gtk.Frame()
		notebook.append_page(frame1,tab_label = Gtk.Label.new(_('Sync options')))
		#
		table1 = Gtk.Table(n_rows = 3, n_columns = 4, homogeneous = False)
		table1.set_border_width(5)
		table1.set_col_spacings(5)
		table1.set_row_spacings(5)
		frame1.add(table1)
		#
		label_so_1 = Gtk.Label.new(_('Tasks local only')+':')
		label_so_1.set_alignment(0,.5)
		table1.attach(label_so_1,0,1,0,1, xoptions = Gtk.AttachOptions.FILL, yoptions = Gtk.AttachOptions.SHRINK)
		#
		self.option_tlo = {}
		self.option_tlo['copy'] = Gtk.RadioButton(group=None,label=_('Copy to external'))
		table1.attach(self.option_tlo['copy'],1,2,0,1, xoptions = Gtk.AttachOptions.FILL, yoptions = Gtk.AttachOptions.SHRINK)
		self.option_tlo['delete'] = Gtk.RadioButton(group=self.option_tlo['copy'],label=_('Delete local'))
		table1.attach(self.option_tlo['delete'],2,3,0,1, xoptions = Gtk.AttachOptions.FILL, yoptions = Gtk.AttachOptions.SHRINK)
		self.option_tlo['none'] = Gtk.RadioButton(group=self.option_tlo['copy'],label=_('Do none'))
		table1.attach(self.option_tlo['none'],3,4,0,1, xoptions = Gtk.AttachOptions.FILL, yoptions = Gtk.AttachOptions.SHRINK)
		#
		label_so_1 = Gtk.Label.new(_('Tasks external only')+':')
		label_so_1.set_alignment(0,.5)
		table1.attach(label_so_1,0,1,1,2, xoptions = Gtk.AttachOptions.FILL, yoptions = Gtk.AttachOptions.SHRINK)
		#
		self.option_teo = {}
		self.option_teo['copy'] = Gtk.RadioButton(group=None,label=_('Copy to local'))
		table1.attach(self.option_teo['copy'],1,2,1,2, xoptions = Gtk.AttachOptions.FILL, yoptions = Gtk.AttachOptions.SHRINK)
		self.option_teo['delete'] = Gtk.RadioButton(group=self.option_teo['copy'],label=_('Delete external'))
		table1.attach(self.option_teo['delete'],2,3,1,2, xoptions = Gtk.AttachOptions.FILL, yoptions = Gtk.AttachOptions.SHRINK)
		self.option_teo['none'] = Gtk.RadioButton(group=self.option_teo['copy'],label=_('Do none'))
		table1.attach(self.option_teo['none'],3,4,1,2, xoptions = Gtk.AttachOptions.FILL, yoptions = Gtk.AttachOptions.SHRINK)
		#
		self.option_tb = {}
		self.option_tb['copy local'] = Gtk.RadioButton(group=None,label=_('Copy to local'))
		table1.attach(self.option_tb['copy local'],1,2,2,3, xoptions = Gtk.AttachOptions.FILL, yoptions = Gtk.AttachOptions.SHRINK)
		self.option_tb['copy external'] = Gtk.RadioButton(group=self.option_tb['copy local'],label=_('Copy to external'))
		table1.attach(self.option_tb['copy external'],2,3,2,3, xoptions = Gtk.AttachOptions.FILL, yoptions = Gtk.AttachOptions.SHRINK)
		self.option_tb['none'] = Gtk.RadioButton(group=self.option_tb['copy local'],label=_('Do none'))
		table1.attach(self.option_tb['none'],3,4,2,3, xoptions = Gtk.AttachOptions.FILL, yoptions = Gtk.AttachOptions.SHRINK)
		#
		label_so_1 = Gtk.Label.new(_('Tasks local and external')+':')
		label_so_1.set_alignment(0,.5)
		table1.attach(label_so_1,0,1,2,3, xoptions = Gtk.AttachOptions.FILL, yoptions = Gtk.AttachOptions.SHRINK)
		
		#
		frame2 = Gtk.Frame()
		notebook.append_page(frame2,tab_label = Gtk.Label.new(_('Login')))
		#
		table2 = Gtk.Table(n_rows = 1, n_columns = 2, homogeneous = False)
		table2.set_border_width(5)
		table2.set_col_spacings(5)
		table2.set_row_spacings(5)
		frame2.add(table2)
		#
		label11 = Gtk.Label.new(_('Allow access to Google Tasks')+':')
		label11.set_alignment(0,.5)
		table2.attach(label11,0,1,0,1, xoptions = Gtk.AttachOptions.FILL, yoptions = Gtk.AttachOptions.SHRINK)
		#
		self.switch1 = Gtk.Switch()
		self.switch1.connect('button-press-event',self.on_switch1_changed)
		self.switch1.connect('activate',self.on_switch1_changed)
		table2.attach(self.switch1,1,2,0,1, xoptions = Gtk.AttachOptions.EXPAND, yoptions = Gtk.AttachOptions.SHRINK)
		#
		self.load_preferences(tasks)
		#
		self.show_all()

	def load_preferences(self,tasks):
		self.switch1.set_active(os.path.exists(comun.TOKEN_FILE))
		configuration = Configuration()
		if os.path.exists(os.path.join(os.getenv("HOME"),".config/autostart/google-tasks-indicator-autostart.desktop")):
			self.switch4.set_active(True)
		if configuration.get('local') == 0:
			self.option_tlo['copy'].set_active(True)
		elif configuration.get('local') == 1:
			self.option_tlo['delete'].set_active(True)
		else:
			self.option_tlo['none'].set_active(True)			
		#
		if configuration.get('external') == 0:
			self.option_teo['copy'].set_active(True)
		elif configuration.get('external') == 1:
			self.option_teo['delete'].set_active(True)
		else:
			self.option_teo['none'].set_active(True)			
		#
		if configuration.get('both') == 0:
			self.option_tb['copy local'].set_active(True)
		elif configuration.get('both') == 1:
			self.option_tb['copy external'].set_active(True)
		else:
			self.option_tb['none'].set_active(True)			
		#
		if configuration.get('theme') == 'light':
			self.switch5.set_active(True)
		else:
			self.switch5.set_active(False)
		tasklist_id = configuration.get('tasklist_id')
		if tasks is not None:
			self.liststore.clear()
			self.liststore.append([_('All'),None])			
			for tasklist in tasks.tasklists.values():
				self.liststore.append([tasklist['title'],tasklist['id']])
			if tasklist_id is None:
				self.entry2.set_active(0)
			else:
				for i,item in enumerate(self.liststore):
					print(tasklist_id,item[1])
					if tasklist_id == item[1]:
						self.entry2.set_active(i)
						break
		
		if os.path.exists(comun.TOKEN_FILE):
			gta = GTAService(token_file = comun.TOKEN_FILE)
						
	def save_preferences(self):
		configuration = Configuration()
		tree_iter = self.entry2.get_active_iter()
		if tree_iter != None:
			model = self.entry2.get_model()
			tasklist_id = model[tree_iter][1]	
			configuration.set('tasklist_id',tasklist_id)
		if self.switch5.get_active():
			configuration.set('theme','light')
		else:
			configuration.set('theme','dark')
		if self.option_tlo['copy'].get_active()==True:
			configuration.set('local',0)
		elif self.option_tlo['delete'].get_active()==True:
			configuration.set('local',1)
		else:
			configuration.set('local',2)
		if self.option_teo['copy'].get_active()==True:
			configuration.set('external',0)
		elif self.option_teo['delete'].get_active()==True:
			configuration.set('external',1)
		else:
			configuration.set('external',2)
		#
		if self.option_tb['copy local'].get_active()==True:
			configuration.set('both',0)
		elif self.option_tb['copy external'].get_active()==True:
			configuration.set('both',1)
		else:
			configuration.set('both',2)
		#
		configuration.save()
		filestart = os.path.join(os.getenv("HOME"),".config/autostart/google-tasks-indicator-autostart.desktop")
		if self.switch4.get_active():
			if not os.path.exists(filestart):
				if not os.path.exists(os.path.dirname(filestart)):
					os.makedirs(os.path.dirname(filestart))
				shutil.copyfile('/usr/share/google-tasks-indicator/google-tasks-indicator-autostart.desktop',filestart)
		else:		
			if os.path.exists(filestart):
				os.remove(filestart)		

	def close_application(self,widget):
		self.ok = False

	def on_switch1_changed(self,widget,data):
		if self.switch1.get_active():
			if os.path.exists(comun.TOKEN_FILE):
				os.remove(comun.TOKEN_FILE)
		else:
			gta = GTAService(token_file = comun.TOKEN_FILE)
			if gta.do_refresh_authorization() is None:
				authorize_url = gta.get_authorize_url()
				ld = LoginDialog(authorize_url)
				ld.run()
				gta.get_authorization(ld.code)
				ld.destroy()				
				if gta.do_refresh_authorization() is None:
					md = Gtk.MessageDialog(	parent = self,
											flags = Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT,
											type = Gtk.MessageType.ERROR,
											buttons = Gtk.ButtonsType.OK_CANCEL,
											message_format = _('You have to authorize Google-Task-Indicator to use it, do you want to authorize?'))
					if md.run() == Gtk.ResponseType.CANCEL:
						exit(3)				
				else:
					if gta.do_refresh_authorization() is None:
						exit(3)
			self.switch1.set_active(True)
			self.liststore.clear()
			self.liststore.append([_('All'),None])
			for tasklist in gta.get_tasklists().values():
				self.liststore.append([tasklist['title'],tasklist['id']])
			self.entry2.set_active(0)	

if __name__ == "__main__":
	p = Preferences()
	if p.run() == Gtk.ResponseType.ACCEPT:
		p.save_preferences()
	p.destroy()
	exit(0)
		
