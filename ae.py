#!/usr/bin/env python2
# vim: set ts=4 sw=4 et ai si:
#
#    Bob's Terminator Customization Plugins
#    Copyright (C) 2015  balinbob@gmail.com
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, version 2 only.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  
#    USA

import gtk
import terminatorlib.plugin as plugin
from terminatorlib.translation import _
from os.path import isfile
from glib import timeout_add_seconds
import vte
from terminatorlib.config import Config
config = Config( )
base = config.base
profile = config.get_profile( )
idx = 0
import sys
import gobject
from gobject import GObject
sys.path.append('.')
from setter import Viewer
import os


class Fn( ):
    def __init__( self,profile,term=None ):
        self.profile = profile

    def setprofile(self,profile):
        self.profile = profile

    def getitem(self,item):
        return base.get_item(item,self.profile)

    def setitem(self,item,val):
        base.set_item(item,val,self.profile)

    def colorobj(self,str):
        return gtk.gdk.Color( normalize \
                ( self.getitem(str)))

    def colorstr(self,widget):
        return normalize(widget.get_color( ))

    def colorobj_from_widget(self,widget):
        return widget.get_color( )




class OrigState(dict):
    def __init__(self,profile):
        dict.__init__(self)
        self.profile = profile

    def keylist(self):
        return [ 'foreground_color',
                 'background_color',
                 'palette',
                 'background_type',
                 'background_darkness',
                 'background_image',
                 'show_titlebar',
                 'scrollbar_position',
                 'use_system_font',
                 'font'
               ]

    def read(self):
        fn = Fn( self.profile )
        for key in self.keylist( ):
            self[key] = fn.getitem(key)

    def restore(self):
        fn = Fn( self.profile )
        for key in self.keys( ):
            fn.setitem(key,self.get(key))

class State(dict):
    def __init__(self,profile):
        dict.__init__(self)
        self.profile = profile
    
    def set_profile(self,profile):
        self.profile = profile

    def get_profile(self):
        return self.profile


    def keylist(self):
        return [ 'foreground_color',
                 'background_color',
                 'palette',
                 'background_type',
                 'background_darkness',
                 'background_image',
                 'show_titlebar',
                 'font',
                 'use_system_font',
                 'scrollbar_position'
               ]
    
    def read(self):
        fn = Fn(self.profile)
        for key in self.keylist( ):
            self[key] = fn.getitem(key)
            print 'key:',key,'  ',self.get(key)

    def restore(self):
        fn = Fn(self.profile)
        
        for key in self.keylist( ):
            fn.setitem(key,self.get(key))






class ColorBtns(object):
    def __init__(self,parent):
        titles = ['Black','Red','Green','Yellow','Blue','Magenta','Cyan','White']
        titles.extend( ['Light '+title for title in titles[:8] ] )
        title_iter = iter( titles )

        self.colorbtns = [gtk.ColorButton( ) for n in range(16)]
        mc = MkC( )


class Completer(gtk.EntryCompletion):
    def __init__(self):
        gtk.EntryCompletion.__init__(self)
        self.entry = gtk.Entry( )
        self.entry.set_completion(self)
        self.liststore = gtk.ListStore(str)
        self.set_model(self.liststore)
        self.set_text_column(0)

    def set_data(self,list=[]):
        self.liststore.clear( )
        for profile in list:
            self.liststore.append([profile])



class MkC(object):
    def __init__(self):
        self.i=iter(['0']*8+['1']*8)
        self.j=iter(['30','31','32','33','34','35','36','37']*2)
    def say(self):
        while True:
            try:
                return "%s;%s" % (self.i.next( ),self.j.next( ))
            except StopIteration:
                return ""


AVAILABLE=['AppearanceEditor']

class AppearanceEditor( plugin.MenuItem ):
    capabilities = ['terminal_menu']
    
    def __init__(self):
        pass

    def edit(self,item,term):
        editor = EditorWin( term )
        editor.connect('destroy',lambda w:term.reconfigure( ))
        editor.set_transient_for(term.parent)
        editor.show_all( )

    def callback(self,menuitems,menu,terminal):
        item = gtk.MenuItem('Appearance')
        menu.append(item)
        item.connect('activate',self.edit,terminal)




def normalize(clr):
    clr = str(clr)
    if len(clr) == 4: return '#'+''.join([clr[1]*2,clr[2]*2,clr[3]*2])
    if len(clr) == 7: return clr
    return clr[:3]+clr[5:7]+clr[9:11]




class EditorWin(gtk.Window):
    
    base = None
    profile = None
    getitem = None
    setitem = None
    getcolor = None
    
    def on_btn_cancel( self, button ):
        self.origstate.restore( )
        fn = Fn(self.get_current_profile( ))
        self.background_image = fn.getitem('background_image')
        self.term.reconfigure( )
        self.destroy( )

    def on_btn_ok( self, btn ):
        self.update_term(force=True)
        self.destroy( )
    
    def on_apply(self,btn):
        self.update_term(force=True)
 

    
    def on_save(self,widget=None):
#        start_profile = self.get_current_profile( )
        entry_text = self.entry.get_text( )
        if entry_text:
            print 'on save'
            state = State(self.get_current_profile( ))
            state.read( )
            if entry_text not in self.get_profiles( ):
                self.term.config.add_profile(entry_text)
            self.term.config.set_profile(entry_text)
            state.set_profile(entry_text)            
            state.restore( )
            self.term.config.save( )
#            self.origstate.restore( )
            self.term.reconfigure( )


    def on_entry( self, entry ):
        self.on_save( )
    
    def on_entry_changed( self, entry ):
        if entry.get_text_length( ):
            self.btn_save.set_sensitive(True)
            self.btn_save.set_label('Save')
            if entry.get_text( ) not in self.get_profiles( ):
                self.btn_save.set_label('Save As')
        else:
            self.btn_save.set_sensitive(False)

    def get_profiles(self):
        profiles = self.term.config.list_profiles( ) 
        return profiles

    def set_profile(self,profile):
        self.term.config.set_profile(profile)
        self.combo.set_active(self.get_profiles( ).index(profile))

    def make_combo(self,combo):
        for profile in combo.get_model( ):
            combo.remove(profile)
        profiles = self.get_profiles( )
        for profile in profiles:
            combo.append_text(profile)
        combo.set_active(profiles.index(self.get_current_profile( )))
    
    
    def normalize(self,clr):
        clr = str(clr)
        if len(clr) == 4: return '#'+''.join([clr[1]*2,clr[2]*2,clr[3]*2])
        if len(clr) == 7: return clr
        return clr[:3]+clr[5:7]+clr[9:11]



    def on_combo(self,combo,term):
        profile = combo.get_active_text( )
        fn = Fn( profile )
        colors = iter( [gtk.gdk.Color(item) for item in \
                fn.getitem('palette').split(':') ] )
        self.btn_fore.set_color( fn.colorobj('foreground_color') )
        [btn.set_color(colors.next( )) for btn in self.colorbtns]
        self.update_term( )

    def do_reconfigure(self):
        self.term.reconfigure( )


    def update_term(self,force=False):
        if self.checkbutton.get_active( ) or force:
            pass
        else:
            return
        
        fn = Fn(self.get_current_profile( ))
        fn.setitem('foreground_color',fn.colorstr(self.btn_fore))
        fn.setitem('background_color',fn.colorstr(self.btn_back))
    
        fn.setitem('background_type',self.bg_type)
        if self.bg_type == 'solid':
            fn.setitem('background_type','solid')
        else:
            fn.setitem('background_darkness',float(self.wrange.get_value( )))
        self.wrange.set_sensitive(self.bg_type!='solid')

        self.palette = ':'.join([fn.colorstr(btn) for btn in self.colorbtns])
        fn.setitem('palette',self.palette)
        self.do_reconfigure( )


    def on_slider_value_changed(self,wrange):
        self.update_term( )


    def on_checkbutton( self, btn ):
        if btn.get_active( ):
            self.do_reconfigure( )
        self.btn_apply.set_sensitive(not btn.get_active( ))


    def get_current_profile( self ):
        return self.term.config.get_profile( )

    
    def get_bg_type(self):
        return self.term.config.base.get_item('background_type',self.profile)


    def set_bg_type(self,widget=None):
        fn = Fn(self.get_current_profile( )) 
        self.bg_type = self.bg_type_combo.get_active_text( )
        self.background_image = fn.getitem('background_image')
        self.image_widget.set_sensitive(self.bg_type == 'image')
        self.wrange.set_sensitive( self.bg_type!='solid' )
        fn.setitem('background_type',self.bg_type)
        
        self.set_image_label(fn.getitem('background_image') or '')
        self.update_term( )


    def on_font_btn(self,fontbutton,data=None):
        fn = Fn(self.get_current_profile( ))
        current_font = fn.getitem('font')
        self.font_dialog = gtk.FontSelectionDialog('Pick a Font')
        self.font_dialog.set_font_name(current_font)
        self.font_dialog.get_font_selection( ).set_font_name(current_font)
        
    def on_font_set(self,font_btn):
        fn = Fn(self.get_current_profile( ))
        font_btn.set_use_font(True)
        font_btn.set_use_size(True)
        new_font_name = font_btn.get_font_name( )
        fn.setitem('font',new_font_name)
        self.term.reconfigure( )
        self.font_dialog.destroy( )
    
        
    def scrollbar_left(self,widget):
        fn = Fn(self.get_current_profile( ))
        fn.setitem('scrollbar_position','left')
        if self.checkbutton.get_active( ):
            self.do_reconfigure( )

    def scrollbar_right(self,widget):
        fn = Fn(self.get_current_profile( ))
        fn.setitem('scrollbar_position','right')
        if self.checkbutton.get_active( ):
            self.do_reconfigure( )

    def scrollbar_hidden(self,widget):
        fn = Fn(self.get_current_profile( ))
        fn.setitem('scrollbar_position','hidden')
        if self.checkbutton.get_active( ):
            self.do_reconfigure( )

    def systemfont(self,widget):
        fn = Fn(self.get_current_profile( ))
        fn.setitem('use_system_font',widget.get_active( ))
        if self.checkbutton.get_active( ):
            self.do_reconfigure( )

    def titlebar(self,widget):
        fn = Fn(self.get_current_profile( ))
        fn.setitem('show_titlebar',widget.get_active( ))
        if self.checkbutton.get_active( ):
            self.do_reconfigure( )
    
    def bgscrolls(self,widget):
        fn = Fn(self.get_current_profile( ))
        fn.setitem('scroll_background',widget.get_active( ))
        if self.checkbutton.get_active( ):
            self.do_reconfigure( )

    def put(self,bar,widgets,widths):
        for widget in widgets:
            widget.set_size_request(widths.next( ),-1)
            bar.pack_start(widget)
        

    def setter_win(self,btn,event,data=None):
        fn = Fn(self.get_current_profile( ))
        self.setter = Viewer(self,fn)
        self.background_image = fn.getitem('background_image')
        self.set_image_label(self.background_image)


    def set_image_label(self,text=None):
        if not text:
            fn = Fn(self.get_current_profile( ))
            text = fn.getitem('background_image') or ''
        fname = os.path.basename(text)
        if len(fname) > 22:
            fname = fname[:14] + '...' + fname[-10:]
        self.image_widget.set_label(fname)
        self.image_widget.set_tooltip_text(text)

    def __init__(self, term):
        item = None
        gtk.Window.__init__(self)
        self.set_type_hint(gtk.gdk.WINDOW_TYPE_HINT_DIALOG)
        self.term = term
        self.base = term.config.base
        self.profile = term.config.get_profile( )

        fn = Fn( self.profile )
        self.background_image = fn.getitem('background_image') or None	   
        print 'read in background_image as', self.background_image
#        self.orig_pic = self.background_image
        self.orig_state = OrigState( self.profile )
        self.orig_state.read( )

        self.bg_types = ('solid','transparent','image')
        self.connect('delete-event',lambda w,e:self.destroy( ))
        self.profiles=self.get_profiles( )


        titles = ['Black','Red','Green','Yellow','Blue','Magenta','Cyan','White']
        titles.extend( ['Light '+title for title in titles[:8] ] )
        title_iter = iter( titles )

        self.combo = gtk.combo_box_new_text( )
        
        profile_comp = Completer( )
        profile_comp.set_data(self.get_profiles( ))
        profile_comp.get_entry( ).connect('changed',self.on_entry_changed)

        
        self.bars = [gtk.HBox( ),
                        gtk.HBox( ),
                        gtk.HBox( ),
                        gtk.HBox( ),
                        gtk.VBox( ),
                        gtk.HBox( ),
                        gtk.HBox( )
                    ]

        
        bar = [ gtk.CheckButton('Auto'),
                gtk.Button('Apply'),
                profile_comp.get_entry( ),
                gtk.Button('Save'),
                gtk.Button("Cancel"),
                gtk.Button("Ok") ]
        
        self.checkbutton    = bar[0]
        self.btn_apply      = bar[1]
        self.entry          = bar[2]
        self.btn_save       = bar[3]
        self.btn_cancel     = bar[4]
        self.btn_ok         = bar[5]

        w=iter([50,50,70,50,50,50])
        self.put(self.bars[0],bar,w)

        bar[0].set_tooltip_text("Auto-Update: Otherwise use the 'Apply' button")
        bar[1].set_tooltip_text("Apply changes")
        bar[2].set_tooltip_text("Profile name for Save/Save As")
        bar[3].set_tooltip_text("Save the current profile settings")
        bar[4].set_tooltip_text("Undo changes and exit")
        bar[5].set_tooltip_text("Exit and Keep changes for this terminal instance")
 
        self.checkbutton.set_active(True)
        self.checkbutton.connect(   'toggled', self.on_checkbutton )
        self.btn_save.connect(      'clicked',  self.on_save )
        self.btn_apply.connect(     'clicked',  self.on_apply )
        self.btn_apply.set_sensitive( False )
        self.btn_save.set_sensitive( False )
        self.entry.set_text(self.profile)
        self.entry.connect( 'activate',self.on_entry )
        self.entry.connect( 'changed', self.on_entry_changed )
        self.btn_cancel.connect( 'clicked',   self.on_btn_cancel )
        self.btn_ok.connect(     'clicked',   self.on_btn_ok )


        self.palette = fn.getitem('palette')

        colors = iter( [gtk.gdk.Color(item) for item in self.palette.split(':') ] )
        

        bar = [gtk.Label('use palette from profile: '),
               self.combo,
               gtk.Label('fore- ground: '),
               gtk.ColorButton( ),
               gtk.Label('back- ground: '),
                gtk.ColorButton( )
              ] 
        
        self.label0   = bar[0]
        self.label1   = bar[2]
        self.btn_fore = bar[3]
        self.label2   = bar[4]
        self.btn_back = bar[5]
        self.label0.set_line_wrap(True)
        self.label1.set_line_wrap(True)
        self.label2.set_line_wrap(True)
        self.label0.set_padding(4,0)
        self.label1.set_padding(4,0)
        self.label2.set_padding(4,0)
        self.btn_fore.set_title('foreground')
        self.btn_fore.set_color(fn.colorobj('foreground_color'))
        self.btn_fore.connect('color-set', self.update_term)
        
        self.btn_back.set_title('background')
        self.btn_back.set_color(fn.colorobj('background_color'))
        self.btn_back.connect('color-set',self.update_term)

        w=iter([100,160,70,100,70,100])
        self.put(self.bars[1],bar,w)

        self.make_combo(self.combo)
        self.combo.connect('changed',self.on_combo,term)

        
        clrb = ColorBtns(self)


        self.colorbtns = [gtk.ColorButton( ) for n in range(16)]
        mc = MkC( )
        for n,btn in enumerate( self.colorbtns ):
            btn.set_property( 'name', n )
            btn.set_title( title_iter.next( ) )
            btn.connect( 'color-set', self.update_term )
            btn.set_has_tooltip(True)    
            btn.set_tooltip_text(str(mc.say( )))
            btn.set_color(colors.next( ))

            if n < 8:
                self.bars[2].pack_start(btn,expand=True,fill=True)
            else:
                self.bars[3].pack_start(btn,expand=True,fill=True)
        
        self.vbox=gtk.VBox(homogeneous=False,spacing=0)

        adj=gtk.Adjustment(0,0,1.00,.05)
        slider=gtk.HScale(adj)
        self.wrange=slider
        slider.set_digits(2)
        slider.set_increments(.05,.05)
        slider.set_value(fn.getitem('background_darkness'))
        slider.set_sensitive(fn.getitem('background_type')!='solid')
        slider.connect('value-changed',self.on_slider_value_changed)
        
        self.bars[4].pack_start(slider)


        self.bg_type_combo = gtk.combo_box_new_text( )
        for bg_type in self.bg_types:
            self.bg_type_combo.append_text(bg_type)
        bg_type = self.get_bg_type( ) or 'solid'
        self.bg_type = bg_type
        self.bg_type_combo.set_active(self.bg_types.index(bg_type))
        self.bg_type_combo.connect('changed',self.set_bg_type )
        print 'background_type is ',self.bg_type



        self.image_widget = gtk.Button( )
        self.set_image_label(fn.getitem('background_image') or '')
        self.image_widget.set_sensitive(bg_type=='image')
        self.image_widget.connect('button-release-event',self.setter_win,self.event)

	
	
#	self.set_bg_type(None,bg_type)
	

        bar = [ gtk.FontButton( ),
                gtk.Label('background- type: '),
                self.bg_type_combo,
                self.image_widget
              ]

        w = iter([160,70,80,190])

        bar[1].set_line_wrap(True)

        self.put(self.bars[5],bar,w)

        self.font_btn = bar[0]
    
        self.font_btn.set_font_name(fn.getitem('font'))
        self.font_btn.connect('clicked',self.on_font_btn)
        self.font_btn.connect('font-set',self.on_font_set)

        radio0 = gtk.RadioButton( None, 'Left' )
        radio1 = gtk.RadioButton( radio0, 'Right')
        radio2 = gtk.RadioButton( radio0, 'Hidden')

        bar = [ gtk.CheckButton( 'System Font' ),
                gtk.CheckButton( 'Show Titlebar' ),
                gtk.CheckButton( 'BG Scrolls' ),
                radio0,
                radio1,
                radio2
              ]
        w = iter([80,80,80,10,10,10])
        self.put(self.bars[6],bar,w)

        bar[0].set_active(fn.getitem('use_system_font'))
        bar[1].set_active(fn.getitem('show_titlebar'))
        bar[2].set_active(fn.getitem('scroll_background'))
        scrollbar = fn.getitem('scrollbar_position')
        if scrollbar == "left":
            bar[3].set_active(True)
        elif scrollbar == "right":
            bar[4].set_active(True)
        else:
            bar[5].set_active(True)
        
        bar[0].connect('toggled',self.systemfont)
        bar[1].connect('toggled',self.titlebar)
        bar[2].connect('toggled',self.bgscrolls)
        bar[3].connect('toggled',self.scrollbar_left)
        bar[4].connect('toggled',self.scrollbar_right)
        bar[5].connect('toggled',self.scrollbar_hidden)
        for b in self.bars: 
            self.vbox.pack_start(b)
        

        self.origstate = OrigState(self.get_current_profile( ))
        self.origstate.read( )
        self.add( self.vbox )
        self.set_title('Terminator: Editing %s' % self.get_current_profile( ))
        
        
        print self.background_image, ' is self.background_image'
        
        self.show_all( )

       

