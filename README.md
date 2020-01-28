# sessionjsonmodifier
View and modify session jsons

![preview](sessionjson.PNG)

NB: Uses the overwrite button to save

There are two ways of getting firefox to accept your modified session:

1.) Save your modified session somewhere, force quit firefox from task manager/activity monitor/etc., switch out the recovery.jsonlz4 (in your mozilla roaming profiles sessionstore-backups folder, then restart firefox.

2.) Exit firefox normally, look for a sessionstore.jsonlz4 in your mozilla roaming profiles folder, then edit and overwrite that file

Currently allows you to view recently closed tabs in a window but does not allow any alterations to the recently closed tabs. Also does nothing for tab histories.

Uses lz4, PySimpleGUIQt with PySide2, and appdirs for finding the folder where all the mozilla profile information is kept.
