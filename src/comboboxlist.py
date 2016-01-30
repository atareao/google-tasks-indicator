#!/usr/bin/python
# -*- coding: utf-8 -*-
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

class ComboBoxList(Gtk.HBox):
	def __init__(self, window, index=0, values = [], height = 150):
		Gtk.HBox.__init__(self)
		self._window = window
		self.entry = Gtk.Entry()
		self.entry.set_editable(False)
		self.button = Gtk.Button()
		self.button.add(Gtk.Arrow.new(Gtk.ArrowType.DOWN, Gtk.ShadowType.IN))
		self.button.connect('clicked', self.on_button)
		self.pack_start(self.entry, 0, 0, 0)
		self.pack_start(self.button, 0, 0, 0)
		self.index = index
		self.values = values
		self.height = height
				
	def create_window(self):
		self.dialog = Gtk.Dialog(None, None, Gtk.DialogFlags.MODAL)	
		self.dialog.set_decorated(False)
		#
		scrolledwindow = Gtk.ScrolledWindow()
		scrolledwindow.set_can_focus(False) 
		scrolledwindow.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
		scrolledwindow.set_shadow_type(Gtk.ShadowType.ETCHED_OUT)
		self.dialog.vbox.pack_start(scrolledwindow, Gtk.AttachOptions.SHRINK, Gtk.AttachOptions.SHRINK,0)
		#
		self.store = Gtk.ListStore(str)
		for value in self.values:
			self.store.append([value])
		self.tree = Gtk.TreeView(self.store)
		self.tree.set_headers_visible(False)
		self.tree.set_can_focus(False) 
		renderer = Gtk.CellRendererText()
		column = Gtk.TreeViewColumn(title=None,cell_renderer=renderer, text=0)
		self.tree.append_column(column)
		#
		scrolledwindow.add(self.tree)
		self.tree.connect('focus-out-event',self.on_focus_out)
		self.dialog.connect('focus-out-event',self.on_focus_out)
		self.tree.connect('cursor-changed',self.on_cursor_changed)
		self.dialog.show_all()
				
	def set_sensitive(self, is_sensistive):
		self.entry.set_sensitive(is_sensistive)
		self.button.set_sensitive(is_sensistive)

	def set_editable(self, is_editable):
		self.entry.set_editable(is_editable)
		self.button.set_editable(is_editable)

	def set_height(height=150):
		self.height=height
		
	def on_button(self, button):
		win_position = self._window.get_position()
		x_win = win_position[0] + self.entry.get_allocation().x + 3
		y_win = win_position[1] + self.entry.get_allocation().y + 2*self.entry.get_allocation().height + 3
		#
		self.create_window()
		#
		width = self.button.get_allocation().x - self.entry.get_allocation().x
		self.dialog.set_size_request(width,self.height)
		self.dialog.move(x_win, y_win)
		self.dialog.grab_focus()
		self.set_index(self.index)
		self.dialog.run()
		self.dialog.hide()
			
	def on_focus_out(self,widget,event):
		self.dialog.hide()
		
	def set_index(self,index):
		self.index = index
		self.tree.set_cursor(index)
	
	def get_index(self):
		return self.index
	
	def get_selected_value(self):
		return self.entry.get_text()
			
	def on_cursor_changed(self,widget):
		store,iter = self.tree.get_selection().get_selected()
		self.entry.set_text(store.get_value(iter,0))
		self.index = store.get_path(iter)
		self.dialog.hide()
		
