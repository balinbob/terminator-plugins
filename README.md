#terminator-plugins

Two related plugins for the Terminator terminal emulator:
File #1 is "my_plugin.py" (name to be changed eventually)
Probable name "BackgroundZoom", this is a submenu to the
terminator pop-up context, which provides for easily 
resizing a background image so that it better fits the
size of the terminal.  There are a four methods: "None",
"Width", "Height", and "Fit".  When the window is resized
by the user, the background image is automatically resized
the first time the pop-up menu is displayed.

Right-clicking to open the pop-up menu also dismisses any
"phantom-image" which appears upon switching to a solid
or transparent background.

Files #2 & #3 are "ae.py" and "setter.py".  setter.py
is simply a module, it is not a self-contained plugin.
These two show up in the plugins menu as 
"AppearanceEditor", which provides for a pop-up dialog
for changing characteristics of the vte object in real-
time.  Ex: Adusting background transparency or darkness
is reflected in the terminal as it happens.   There are
quite a few features to this one.
