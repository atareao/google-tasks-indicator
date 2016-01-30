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

locale.setlocale(locale.LC_ALL, '')
gettext.bindtextdomain(comun.APP, comun.LANGDIR)
gettext.textdomain(comun.APP)
_ = gettext.gettext
		
class TaskListDialog(Gtk.Dialog):
	def __init__(self, tasklist = None):
		Gtk.Dialog.__init__(self)
		if tasklist == None:
			self.set_title(comun.APPNAME + ' | '+_('Add new tasklist'))
		else:
			self.set_title(comun.APPNAME + ' | '+_('Edit tasklist'))
		self.set_modal(True)
		self.add_buttons(Gtk.STOCK_OK, Gtk.ResponseType.ACCEPT,Gtk.STOCK_CANCEL,Gtk.ResponseType.CANCEL)	
		self.set_size_request(200, 80)
		self.set_resizable(False)
		self.set_icon_from_file(comun.ICON)
		#
		vbox0 = Gtk.VBox(spacing = 5)
		vbox0.set_border_width(5)
		self.get_content_area().add(vbox0)
		#
		table1 = Gtk.Table(n_rows = 1, n_columns = 2, homogeneous = False)
		table1.set_border_width(5)
		table1.set_col_spacings(5)
		table1.set_row_spacings(5)
		vbox0.add(table1)
		#
		label11 = Gtk.Label.new(_('Title')+':')
		label11.set_alignment(0,.5)
		table1.attach(label11,0,1,0,1, xoptions = Gtk.AttachOptions.FILL, yoptions = Gtk.AttachOptions.FILL)
		#
		self.entry1 = Gtk.Entry()
		self.entry1.set_width_chars(60)
		table1.attach(self.entry1,1,2,0,1, xoptions = Gtk.AttachOptions.EXPAND, yoptions = Gtk.AttachOptions.SHRINK)
		#
		if tasklist is not None:
			if 'title' in tasklist.keys():
				self.entry1.set_text(tasklist['title'])
		self.show_all()
		
	
	def get_title(self):
		return self.entry1.get_text()

		
		
if __name__ == "__main__":
	p = TaskListDialog()
	if p.run() == Gtk.ResponseType.ACCEPT:
		p.hide()
		print(p.get_title())
	p.destroy()
	exit(0)
		
