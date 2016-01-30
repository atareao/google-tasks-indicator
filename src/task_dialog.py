#!/usr/bin/python
# -*- coding: iso-8859-15 -*-
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
import locale
import gettext
import comun
import datetime
from comboboxcalendar import ComboBoxCalendar
import rfc3339

locale.setlocale(locale.LC_ALL, '')
gettext.bindtextdomain(comun.APP, comun.LANGDIR)
gettext.textdomain(comun.APP)
_ = gettext.gettext
		
class TaskDialog(Gtk.Dialog):
	def __init__(self, task = None,tasks = None):		
		Gtk.Dialog.__init__(self)
		if task == None:
			self.set_title(comun.APPNAME + ' | '+_('Add new task'))
		else:
			self.set_title(comun.APPNAME + ' | '+_('Edit task'))
		self.set_modal(True)
		self.add_buttons(Gtk.STOCK_OK, Gtk.ResponseType.ACCEPT,Gtk.STOCK_CANCEL,Gtk.ResponseType.CANCEL)	
		self.set_size_request(250, 160)
		self.set_resizable(False)
		self.set_icon_from_file(comun.ICON)
		self.connect('destroy', self.close_application)
		#
		vbox0 = Gtk.VBox(spacing = 5)
		vbox0.set_border_width(5)
		self.get_content_area().add(vbox0)
		#
		table1 = Gtk.Table(n_rows = 5, n_columns = 2, homogeneous = False)
		table1.set_border_width(5)
		table1.set_col_spacings(5)
		table1.set_row_spacings(5)
		vbox0.add(table1)
		#
		label10 = Gtk.Label.new(_('Task List')+':')
		label10.set_alignment(0,.5)
		table1.attach(label10,0,1,0,1, xoptions = Gtk.AttachOptions.FILL, yoptions = Gtk.AttachOptions.FILL)
		#
		self.liststore = Gtk.ListStore(str,str)
		self.entry0 = Gtk.ComboBox.new_with_model(model=self.liststore)
		renderer_text = Gtk.CellRendererText()
		self.entry0.pack_start(renderer_text, True)
		self.entry0.add_attribute(renderer_text, "text", 0)
		self.entry0.set_active(0)
		table1.attach(self.entry0,1,2,0,1, xoptions = Gtk.AttachOptions.EXPAND, yoptions = Gtk.AttachOptions.SHRINK)
		#
		label11 = Gtk.Label.new(_('Title')+':')
		label11.set_alignment(0,.5)
		table1.attach(label11,0,1,1,2, xoptions = Gtk.AttachOptions.FILL, yoptions = Gtk.AttachOptions.FILL)
		#
		label12 = Gtk.Label.new(_('Notes')+':')
		label12.set_alignment(0,0)
		table1.attach(label12,0,1,2,3, xoptions = Gtk.AttachOptions.FILL, yoptions = Gtk.AttachOptions.FILL)
		#
		label13 = Gtk.Label.new(_('Completed')+':')
		label13.set_alignment(0,.5)
		table1.attach(label13,0,1,3,4, xoptions = Gtk.AttachOptions.FILL, yoptions = Gtk.AttachOptions.SHRINK)
		#
		label14 = Gtk.Label.new(_('Date due')+':')
		label14.set_alignment(0,0)
		table1.attach(label14,0,1,4,5, xoptions = Gtk.AttachOptions.FILL, yoptions = Gtk.AttachOptions.SHRINK)
		#
		self.entry1 = Gtk.Entry()
		self.entry1.set_width_chars(60)
		table1.attach(self.entry1,1,2,1,2, xoptions = Gtk.AttachOptions.EXPAND, yoptions = Gtk.AttachOptions.SHRINK)
		#
		scrolledwindow2 = Gtk.ScrolledWindow()
		scrolledwindow2.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
		scrolledwindow2.set_shadow_type(Gtk.ShadowType.ETCHED_OUT)
		table1.attach(scrolledwindow2,1,2,2,3, xoptions = Gtk.AttachOptions.FILL, yoptions = Gtk.AttachOptions.FILL)
		self.entry2 = Gtk.TextView()
		self.entry2.set_wrap_mode(Gtk.WrapMode.WORD)
		scrolledwindow2.set_size_request(350,150)
		scrolledwindow2.add(self.entry2)
		#
		self.entry3 = Gtk.Switch()
		table1.attach(self.entry3,1,2,3,4, xoptions = Gtk.AttachOptions.SHRINK, yoptions = Gtk.AttachOptions.SHRINK)
		#
		hbox = Gtk.HBox()
		table1.attach(hbox,1,2,4,5, xoptions = Gtk.AttachOptions.SHRINK, yoptions = Gtk.AttachOptions.SHRINK)
		self.entry4 = Gtk.CheckButton()
		self.entry4.connect('toggled', self.toggle_clicked )
		hbox.pack_start(self.entry4,0,0,0)
		self.entry5 = ComboBoxCalendar(self)
		self.entry5.set_sensitive(False)
		hbox.pack_start(self.entry5,0,0,0)
		#table1.attach(self.entry4,1,2,3,4, xoptions = Gtk.AttachOptions.SHRINK, yoptions = Gtk.AttachOptions.SHRINK)
		#
		if tasks is not None:
			for tasklist in sorted(tasks.tasklists.values()):
				self.liststore.append([tasklist['title'],tasklist['id']])						
		if task is not None:
			for i,item in enumerate(self.liststore):
				if task['tasklist_id'] == item[1]:
					self.entry0.set_active(i)					
					break			
			self.entry0.set_active(False)
			if 'title' in task.keys():
				self.entry1.set_text(task['title'])
			if 'notes' in task.keys() and task['notes'] is not None:
				self.entry2.get_buffer().set_text(task['notes'])
			if 'status' in task.keys():
				self.entry3.set_active(task['status'] == 'completed')
			if 'due' in task.keys() and task['due'] is not None:
				self.entry4.set_active(True)
				self.entry5.set_date(rfc3339.parse_datetime(task['due']))
			else:
				self.entry4.set_active(False)
		else:
			self.entry0.set_active(0)
		self.show_all()
		
	def toggle_clicked(self,widget):
		self.entry5.set_sensitive(self.entry4.get_active())
		
	def close_application(self,widget):
		self.ok = False
	
	def get_tasklist_id(self):
		tree_iter = self.entry0.get_active_iter()
		model = self.entry0.get_model()
		return model[tree_iter][1]	

	def get_title(self):
		return self.entry1.get_text()
		
	def get_notes(self):
		tbuffer =self.entry2.get_buffer()
		inicio = tbuffer.get_start_iter()
		fin = tbuffer.get_end_iter()
		return tbuffer.get_text(inicio,fin,True)

	def is_completed(self):
		return self.entry3.get_active()

	def get_due_date(self):
		if self.entry4.get_active():
			return self.entry5.get_date()
		return None

		
		
if __name__ == "__main__":
	p = TaskDialog()
	p.entry5.set_date('2012-03-09T00:00:00.000Z')
	if p.run() == Gtk.ResponseType.ACCEPT:
		p.hide()
		print(p.get_due_date())
	p.destroy()
	exit(0)
		
