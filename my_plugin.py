#
# vim: set ts=4 sw=4 et ai si:

import gtk
import terminatorlib.plugin as plugin
from terminatorlib.translation import _
from os.path import isfile
AVAILABLE = ['BackgroundZoom']


class BackgroundZoom( plugin.MenuItem ) :
    capabilities = ['terminal_menu']

    def __init__(self):
        plugin.MenuItem.__init__(self)
        self.dynamic = False
        self.terms = { } 
        self.scaling = None

    def callback(self,menuitems,menu,terminal):
        if terminal.config['background_type'] != 'image':
            terminal.vte.set_background_image_file('')

        if terminal.config['background_type'] == 'image' and    \
                            isfile(terminal.config['background_image']):
            
            if self.scaling:
                scaling = self.scaling
            else:
                scaling = 'none'
            submenu = gtk.Menu( )
            submenu_item = gtk.MenuItem('background scaling')
            submenu_item.set_submenu( submenu )
            items=4*[gtk.RadioMenuItem()]
            items[0]=gtk.RadioMenuItem(label='none')
            items[0].connect('toggled',self.zoom,'none')
            items[0].set_active( scaling=='none' )
            submenu.append(items[0])
            scaling_types = ['none','width','height','fit']
            for n,scaling in enumerate(scaling_types[1:]):
                items[n+1]=gtk.RadioMenuItem(group=items[0],label=scaling)    
                items[n+1].connect('toggled',self.zoom,scaling)
                items[n+1].set_active( scaling==self.scaling )
                submenu.append(items[n+1])
            menu.append(submenu_item)
        
        
        if terminal not in self.terms:
            event_id = terminal.connect('size-allocate',self.zoom)
            self.terms.update({terminal:event_id})
            terminal.connect('delete-event',self.disconnect_term)

    def disconnect_term(self,term,event):
        event_id = self.terms.pop(term)
        term.disconnect(event_id)

    def zoom(self,widget,scaling):
        if isinstance(widget,gtk.RadioMenuItem):
            if scaling in ('none','fit','width','height'):
                self.scaling = scaling
            else:
                return True
        else:
            return True
        
        for term in self.terms:
            bg_file = term.config['background_image']
            if not bg_file:
                return True
            term_w,term_h = term.vte.allocation[2],term.vte.allocation[3]
            pb = gtk.gdk.pixbuf_new_from_file(bg_file)
    
            pb_w,pb_h = pb.get_width( ),pb.get_height( )
            
            
            if scaling == 'none':
                pixbuf = gtk.gdk.pixbuf_new_from_file(bg_file)
            elif scaling == 'fit':
                pixbuf = gtk.gdk.pixbuf_new_from_file_at_scale( \
                                    bg_file,term_w,term_h,False)

            if scaling == 'width':
                pixbuf = gtk.gdk.pixbuf_new_from_file_at_scale( \
                            bg_file,term_w,-1,True)
            elif scaling == 'height':
                pixbuf = gtk.gdk.pixbuf_new_from_file_at_scale( \
                            bg_file,-1,term_h,True)


            term.vte.set_background_image( pixbuf )
            
            return True           
            

