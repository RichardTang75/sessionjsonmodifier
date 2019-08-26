# sessionjsonmodifier
view and modify session jsons


In progress, currently allows for 
searching of tabs to delete
deleting windows 
deleting tabs
adding windows from one session to another

Can switch from title to URL. Avoid doing this as it's a bit buggy. Click on selected window/tab/history or search button again before modifying for best results.

Unlikely to be expanded upon, it already hits all of my needs.

Uses lz4, PySimpleGUIQt with PySide2, and appdirs for finding the folder where all the mozilla profile information is kept.
