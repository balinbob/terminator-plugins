#!/usr/bin/env python2
# vim: set ts=4 sw=4 et ai si:

import pygtk,gtk
import sys
from sys import argv,exc_info
from glib import get_user_config_dir
import os
from urllib2 import url2pathname
from subprocess import check_output,STDOUT,CalledProcessError
from gtk import gdk

def get_default_screen_metrics(  ):
    scrn = gdk.screen_get_default( )
    h = scrn.get_height( )
    w = scrn.get_width( )
    return (w,h)




class Viewer(gtk.IconView):

    def delete(self,w,e,d=None):
        self.win.destroy( )
        self.destroy( )
        return( )

    def on_ok(self,btn,data=None):
        try:
            self.editor_win.set_image_label(self.image)
        except AttributeError:
            pass
        self.editor_win.update_term(force=True)
        self.win.destroy( )
    
    
    def on_cancel(self,btn,data=None):
        self.editor_win.background_image = self.orig_pic
        self.fn.setitem('background_image',self.orig_pic)
        self.editor_win.do_reconfigure( )
        self.win.destroy( )



    def __init__(self,editor_win,fn):
        self.editor_win = editor_win
        self.fn = fn
        model = gtk.ListStore(gtk.gdk.Pixbuf,str,str)
        gtk.IconView.__init__(self)


        self.orig_pic = fn.getitem('background_image')
        
        
        
        self.noshow = False
        self.set_model(model)
        self.set_pixbuf_column(0)
        self.set_text_column(1)
        self.set_tooltip_column(2)
        self.set_markup_column(-1)
        self.set_item_padding(2)
        self.set_spacing(2)
        self.set_selection_mode(gtk.SELECTION_BROWSE)
#        self.set_column_spacing(2)
#        self.set_row_spacing(2)
            
        self.scrolled_window = gtk.ScrolledWindow( )
        w,h = get_default_screen_metrics(  )
            
        self.scrolled_window.add(self)
        self.vbox = gtk.VBox( )
        self.vpaned = gtk.VPaned( )
        self.expander = gtk.Expander( )
        self.expander.set_label('Open a folder to browse the images inside.')
        self.vbox.pack_start(self.vpaned)
        self.vpaned.pack1(self.expander,True,True)
        self.vpaned.pack2(self.scrolled_window,True,True)
        self.vpaned.set_position(240)
        self.statusbar = gtk.Statusbar( )
        self.fchooser = gtk.FileChooserWidget(gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER)
        self.fchooser.set_size_request(-1,230)
        self.filter = gtk.FileFilter( )
        self.filter.add_mime_type('folder')
        self.fchooser.add_filter(self.filter)
        
        
        
        self.expander.add(self.fchooser)
        self.expander.set_expanded(True)
        self.expander.connect('notify::expanded',self.on_expander)
        self.hbox = gtk.HBox(False)
        self.okbtn = gtk.Button('Ok')
        self.cancelbtn = gtk.Button('Cancel')
        self.recurse_widget = gtk.CheckButton(
                    'Browse two levels\nCan take a few moments',True)
        self.hbox.pack_start(self.recurse_widget)
        self.hbox.pack_start(gtk.VSeparator( ))
        self.hbox.pack_start(self.cancelbtn)
        self.hbox.pack_start(self.okbtn)
        self.okbtn.set_sensitive(False)
        self.vbox.pack_start(self.hbox,False)
        self.vbox.pack_start(self.statusbar,False)
        self.win = gtk.Window(gtk.WINDOW_TOPLEVEL)
        bw=int(w/1.5)
        bh=int(h/2)
        mw=int(w/2.75)
        mh=int(h/1.5)
        self.win.set_size_request(mw,mh) 
        self.win.add(self.vbox)
        self.win.set_transient_for(self.editor_win)
        self.win.set_destroy_with_parent(True)
        self.win.show_all( )
        
	self.connect('item-activated',self.on_item_activated)
	self.connect('selection-changed',self.on_selection_changed)


        self.fchooser.connect('current-folder-changed',self.on_folder_changed)
        
        self.okbtn.connect('clicked',self.on_ok)
        self.cancelbtn.connect('clicked',self.on_cancel)       
        
        self.win.connect('delete-event',self.delete)

#        self.fchooser.set_current_folder(os.path.expanduser('~'))
        self.recurse_widget.connect('toggled',self.check_recurse)



    def on_expander(self,expander,data=None):
        if expander.get_expanded( ):
            self.fchooser.set_size_request(-1,400)
            self.vpaned.set_position(-1)
            self.vpaned.queue_resize( )
        if not expander.get_expanded( ):
            self.fchooser.set_size_request(-1,40)
            expander.set_size_request(-1,40)
            self.scrolled_window.queue_resize( )
            expander.queue_draw( )
            expander.queue_resize( )
            self.vpaned.set_position(40)
            self.vpaned.queue_resize( )
            expander.check_resize( )

    
    def scale_pb(self,ow,oh):
        if ow>oh:
            nw=125
            r=float(ow)/float(nw)
            nh=float(oh)/float(r)
        else:
            nh=125
            r=float(oh)/float(nh)
            nw=float(ow)/float(r)
        return (nw,nh)


    def on_size_prepared(self,pbloader,w,h,data=None):
        minwidth = 200 
        if w<minwidth:
            self.noshow = True
            return
        else:
            self.noshow = False
            (w,h) = self.scale_pb(w,h)
            pbloader.set_size(int(w),int(h))


    def on_area_prepared(self,pbloader):
        self.pb = pbloader.get_pixbuf( )

    def load_pixbuf(self,pname):
        pbloader = gtk.gdk.PixbufLoader( )
        try:
            f = open(pname)
            buf = f.read( )
            f.close( )
        except IOError:
            return
        pbloader.connect('size-prepared',self.on_size_prepared)
        pbloader.connect('area-prepared',self.on_area_prepared)
        try:
            pbloader.write( buf )
            pbloader.close( )
        except:
            pass

    
    def on_selection_changed(self,iconview):
        self.okbtn.set_sensitive(False)
        if len (self.get_selected_items( )):
            path = self.get_selected_items( )[0]
            self.image = self.master_list[path[0]]
            self.okbtn.set_sensitive(self.image != None)
            self.fn.setitem('background_image',self.image)
            
            cid = self.statusbar.get_context_id('pathname')
            self.statusbar.pop(cid)
            self.statusbar.push(cid,self.image)
            
            if self.editor_win.checkbutton.get_active( ):
                self.editor_win.background_image = self.image
                self.editor_win.image_widget.set_label(self.image)
                self.editor_win.do_reconfigure( )

    def on_item_activated(self,iconview,path,data=None):
        self.on_selection_changed(iconview)
        self.on_ok(gtk.Button( ))
   

    def check_recurse(self,cbtn,data=None):
        self.on_folder_changed(self.fchooser)
    
    def on_folder_changed(self,fchooser,data=None):
        url = fchooser.get_current_folder_uri( )
        if not url: 
            return
        pname = url2pathname(url)[7:]
        model = self.get_model( )
        model.clear( )
        self.master_list = [ ]
        self.depth = len( pname.split(os.path.sep) )
        if self.recurse_widget.get_active( ):
            self.recurse = 1
        else:
            self.recurse = 0
        
        self.my_walker(pname,model)
        self.okbtn.set_sensitive(False)
        

   
    def my_walker(self,dirname,model):
        if not os.access(dirname,os.X_OK): return
        pic_types = ('.png','.jpg','.jpeg','.jpe','.xpm')
        itr = None
        cid = self.statusbar.get_context_id('filecount')    
        self.statusbar.pop(cid)

        


        pics = [fname for fname in os.listdir(dirname) if \
                os.path.splitext(fname)[1].lower( ) in pic_types]
        dirs = [fname for fname in os.listdir(dirname) if \
                os.path.isdir(os.path.join(dirname,fname))]
        for fname in pics:
            pname = os.path.join(dirname,fname)
            self.load_pixbuf(pname)
            if self.noshow:
                continue
            self.master_list.append(pname)
           
            if len(fname) > 32:
                fname = fname[:32] + '...'
            itr=model.append([self.pb,fname,pname])
             
        cid = self.statusbar.get_context_id('filecount')
        self.statusbar.pop(cid)
        self.statusbar.push(cid,str(len(self.master_list)))

        if len(dirs) < 1: return

        if 0 < self.recurse < 2:
            self.recurse += 1
#           self.recurse_widget.set_label('please wait!')
        else:
#            self.recurse_widget.set_label('Search two levels')
            return

        for dname in dirs:
            pname = os.path.join(dirname,dname)
            self.my_walker(pname,model)

def main(args):
    iconview = Viewer(args)


if __name__=='__main__':
    main(argv)

