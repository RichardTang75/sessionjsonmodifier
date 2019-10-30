import PySimpleGUIQt as sg
from pathlib import Path
import os
import lz4.block
import json
from appdirs import *
import time


def get_dir():
    moz_dir = user_data_dir(roaming=True)
    if (os.path.exists(os.path.join(moz_dir + os.sep + "Firefox"))):
        moz_dir = os.path.join(moz_dir + os.sep + "Firefox")
    elif (os.path.exists(os.path.join(moz_dir + os.sep + "Mozilla" + os.sep + "Firefox"))):
        moz_dir = os.path.join(moz_dir + os.sep + "Mozilla" + os.sep + "Firefox")
    moz_dir = os.path.join(moz_dir + os.sep + "Profiles")
    moz_dir_paths = [os.path.join(moz_dir, f) for f in os.listdir(moz_dir) if os.path.isdir(os.path.join(moz_dir, f))]
    last_mod = max(moz_dir_paths, key=os.path.getmtime)
    return last_mod


def get_session():
    json_path = os.path.join(get_dir() + os.sep + "sessionstore-backups" + os.sep + "recovery.jsonlz4")
    return json_path


def get_bookmarks():
    bookmark_dir = os.path.join(get_dir() + os.sep + "bookmarkbackups")
    bookmark_dir_paths = [os.path.join(bookmark_dir, f) for f in os.listdir(bookmark_dir)]
    last_mod = max(bookmark_dir_paths, key=os.path.getmtime)
    return last_mod


def get_title(entry):
    if "title" in entry:
        title = entry["title"]
    else:
        title = entry["url"]
    return title


def decompress(path):
    with open(path, 'rb') as file:
        watup = file.read(8)
        if (watup == b'mozLz40\x00'):
            print(watup)
            decomp_json = lz4.block.decompress(file.read()).decode('utf-8')
        elif (watup == b'{"window'):
            decomp_json = watup + file.read()
        else:
            print("Unrecognized file")
        loaded = json.loads(decomp_json)
    return loaded


print(get_bookmarks())
loaded = decompress(get_session())
# with open("sweet.json", 'w', encoding='utf-8') as file:
#    file.write(loaded.encode('utf-8'))
#    json.dump(loaded, file, ensure_ascii=False)
#print("dump done")


def dump_json(path, in_json):
    with open(path, 'wb') as file:
        # file.write(json.dumps(in_json))
        comp_json = lz4.block.compress(json.dumps(in_json).encode('utf-8'))
        comp_json = b"mozLz40\0" + comp_json
        file.write(comp_json)
    print("dump done")


def pull_tab_info(tab, win_name, window_tabs, window_tabs_urls, tab_history, tab_history_urls, tab_cnt, closed=False):
    current_entries = tab["entries"]
    if len(current_entries) > 0:
        active_entry = current_entries[tab["index"]-1]
        title = get_title(active_entry)
        url = active_entry["url"]
        if closed:
            tab_name = str(tab_cnt) + " Closed Tab: " + title
            url_name = str(tab_cnt) + " Closed Tab: " + url
        else:
            tab_name = str(tab_cnt) + " " + title
            url_name = str(tab_cnt) + " " + url
    else:
        tab_name = str(tab_cnt) + tab["userTypedValue"]
        url_name = str(tab_cnt) + tab["userTypedValue"]
    window_tabs[win_name] += [tab_name]
    window_tabs_urls[win_name] += [url_name]
    tab_history[tab_name] = [get_title(entry) for entry in current_entries]
    tab_history_urls[url_name] = [entry["url"] for entry in current_entries]


def get_index(tab_name):
    return int(tab_name[:tab_name.index(" ")])


class sessionInfo:
    def __init__(self, in_json):
        if in_json == None:
            self.window_listbox = []
        else:
            self.held_json = in_json
            self.window_listbox = []
            win_cnt = 0
            self.window_tabs = dict()
            self.window_tabs_urls = dict()
            self.tabs_history = dict()
            self.tabs_history_urls = dict()
            for window in in_json["windows"]:
                win_name = "Window " + str(win_cnt)
                win_cnt += 1
                tabs = window["tabs"]
                self.window_listbox += [win_name]
                self.window_tabs[win_name] = []
                self.window_tabs_urls[win_name] = []
                tab_cnt = 0
                for tab in tabs:
                    # if (tab_cnt > 455 and tab_cnt < 460):
                    #     print(tab)
                    tab_cnt += 1
                    pull_tab_info(tab, win_name, self.window_tabs, self.window_tabs_urls,
                                  self.tabs_history, self.tabs_history_urls, tab_cnt)
                closedtabs = window["_closedTabs"]
                for closed in closedtabs:
                    equiv_tab = closed["state"]
                    tab_cnt += 1
                    pull_tab_info(equiv_tab, win_name, self.window_tabs, self.window_tabs_urls,
                                  self.tabs_history, self.tabs_history_urls, tab_cnt, True)
# print(listbox_items)
# print(os.getenv('APPDATA'))


LISTBOX_SMALL = 3
LISTBOX_BIG = 5

first_session = sessionInfo(loaded)
second_session = sessionInfo(None)
layout = [[sg.Text('Session to add from')],
          [sg.In(default_text=get_session(), size=(80, 1), key='Session2'),
           sg.FileBrowse(), sg.Button('Choose', key="Choose Second")],

          [sg.Listbox(values=[], size=(30, LISTBOX_SMALL), select_mode=sg.LISTBOX_SELECT_MODE_EXTENDED, key='_WIN2', enable_events=True),
           sg.Listbox(values=[], size=(60, LISTBOX_SMALL), select_mode=sg.LISTBOX_SELECT_MODE_EXTENDED, key='_TAB2', enable_events=True),
           sg.Listbox(values=[], size=(30, LISTBOX_SMALL), select_mode=sg.LISTBOX_SELECT_MODE_EXTENDED, key='_HIS2', enable_events=True)],

          [sg.Button('Add Window(s)'), sg.Button(
              'Add Tab(s)'), sg.Button('Add History')],


          [sg.Text('Session to add to')],
          [sg.In(default_text=get_session(), size=(80, 1), key='Session1'),
           sg.FileBrowse(), sg.Button('Choose')],

          [sg.Listbox(values=first_session.window_listbox, size=(30, LISTBOX_BIG), select_mode=sg.LISTBOX_SELECT_MODE_EXTENDED, key='_WIN', enable_events=True),
           sg.Listbox(values=[], size=(60, LISTBOX_BIG), select_mode=sg.LISTBOX_SELECT_MODE_EXTENDED, key='_TAB', enable_events=True),
           sg.Listbox(values=[], size=(30, LISTBOX_BIG), select_mode=sg.LISTBOX_SELECT_MODE_EXTENDED, key='_HIS', enable_events=True)],

          [sg.Button('Delete Window(s)'), sg.Button(
              'Delete Tab(s)'), sg.Button('Delete History')],


          [sg.Text('Search for tab urls'), sg.In(size=(80, 1), key='In Search'), sg.Button('Search')],
          [sg.Listbox(values=[], size=(120, LISTBOX_BIG), select_mode=sg.LISTBOX_SELECT_MODE_EXTENDED, key='_SEARCH', enable_events=True)],
          [sg.Button('Delete selected searched')],

          [sg.Text('Save to')],
          [sg.In(default_text=get_session(), size=(80, 1), key='Session Write'), sg.FileBrowse(), sg.Button('Overwrite')],
          [sg.Button('Show Title'), sg.Button('Hide/Show URL'), sg.Button('Exit')]]

window = sg.Window('Window Title', layout)


current_window = None
current_window_index = None
current_tab = None
current_tab_index = None
use_urls = False


def get_listbox_values(listbox_source, values):
    if len(values) == 0:
        return []
    else:
        return listbox_source[values[0]]

def get_search(search_key, current_window, urls, titles):
    matched_urls = []
    matched_titles = []
    if search_key != '' and current_window != None:
            for url in urls:
                if search_key in url:
                    matched_urls += [url]
                    url_index = urls.index(url)
                    matched_titles += [titles[url_index]]
    return (matched_urls, matched_titles)

while True:                 # Event Loop
    event, values = window.Read()
    if event is None or event == 'Exit':
        break

    if event == '_WIN':
        if (use_urls):
            window.Element('_TAB').Update(values=get_listbox_values(first_session.window_tabs_urls, values['_WIN']), set_to_index=0)
        else:
            window.Element('_TAB').Update(values=get_listbox_values(first_session.window_tabs, values['_WIN']), set_to_index=0)
        if len(values['_WIN']) > 0:
            current_window = values['_WIN'][0]
            current_window_index = first_session.window_listbox.index(current_window)
    elif event == '_TAB':
        if (use_urls):
            window.Element('_HIS').Update(values=get_listbox_values(first_session.tabs_history_urls, values['_TAB']))
        else:
            window.Element('_HIS').Update(values=get_listbox_values(first_session.tabs_history, values['_TAB']))
        if len(values['_TAB']) > 0:
            current_tab = values['_TAB'][0]
            if use_urls:
                current_tab_index = first_session.window_tabs_urls[current_window].index(current_tab)
            else:
                current_tab_index = first_session.window_tabs[current_window].index(current_tab)
    elif event == 'Choose':
        if values['Session1'] != '':
            decompressed = decompress(values['Session1'])
            first_session = sessionInfo(decompressed)
            window.Element('_WIN').Update(values=first_session.window_listbox, set_to_index=0)



    elif event == 'Delete Window(s)':
        # I can't believe they don't give me this either
        indices_to_delete = []
        for to_delete in values['_WIN']:
            indices_to_delete += [first_session.window_listbox.index(to_delete)]
        indices_to_delete.sort(reverse=True)
        for index_to_delete in indices_to_delete:
            first_session.held_json["windows"].pop(index_to_delete)
        first_session = sessionInfo(first_session.held_json)
        window.Element('_WIN').Update(values=first_session.window_listbox, set_to_index=0)
    elif event == 'Delete Tab(s)':
        try:
            print(len(first_session.window_tabs_urls[current_window]))
            window_index = first_session.window_listbox.index(current_window)
            indices_to_delete = []
            for tab_name in values['_TAB']:
                indices_to_delete += [get_index(tab_name)]
            indices_to_delete.sort(reverse=True)
            print(len(indices_to_delete))
            for index_to_delete in indices_to_delete:
                first_session.held_json["windows"][window_index]["tabs"].pop(index_to_delete-1)
            first_session = sessionInfo(first_session.held_json)
            print(len(first_session.window_tabs_urls[current_window]))
            if use_urls:
                window.Element('_TAB').Update(values=first_session.window_tabs_urls[values['_WIN'][0]], set_to_index=indices_to_delete[0])
            else:
                window.Element('_TAB').Update(values=first_session.window_tabs[values['_WIN'][0]], set_to_index=indices_to_delete[0])
        except:
            print("wassup")
    elif event == 'Delete History':
        print(5)


    elif event == '_WIN2':
        window.Element('_TAB2').Update(
            values=second_session.window_tabs[values['_WIN2'][0]], set_to_index=0)
    elif event == '_TAB2':
        window.Element('_HIS2').Update(
            values=second_session.tabs_history[values['_TAB2'][0]])
    elif event == 'Choose Second':
        if values['Session2'] != '':
            decompressed = decompress(values['Session2'])
            second_session = sessionInfo(decompressed)
            window.Element('_WIN2').Update(
                values=second_session.window_listbox, set_to_index=0)
    
    
    elif event == 'Add Window(s)':
        indices_to_add = []
        for to_add in values['_WIN2']:
            indices_to_add += [second_session.window_listbox.index(to_add)]
        for index_to_add in indices_to_add:
            first_session.held_json["windows"] += [second_session.held_json["windows"][index_to_add]]
        first_session = sessionInfo(first_session.held_json)
        window.Element('_WIN').Update(values=first_session.window_listbox, set_to_index=0)
    elif event == 'Add Tab(s)':
         indices_to_add = []
        # for to_add in values['_TAB2']:
        #     indices_to_add += [second_session.tabs_history.index(to_add)]
        # for index_to_add in indices_to_add:
        #     first_session.held_json[current_window_index] += [second_session.held_json["windows"][index_to_add]]
        # first_session = sessionInfo(first_session.held_json)
        # window.Element('_WIN').Update(values=first_session.window_listbox, set_to_index=0)
    elif event == 'Add History':
        print(5)



    # make option to view titles instead
    elif event == 'Search':
        (matched_urls, matched_titles) = get_search(values['In Search'], current_window, 
                        first_session.window_tabs_urls[current_window], first_session.window_tabs[current_window])
        if (use_urls):
            window.Element('_SEARCH').Update(values=matched_urls)
        else:
            window.Element('_SEARCH').Update(values=matched_titles)

    elif event == '_SEARCH':
        if len(values['_SEARCH']) > 0:
            first_item = values['_SEARCH'][0]
            if use_urls:
                important_index = first_session.window_tabs_urls[current_window].index(first_item)
            else:
                important_index = first_session.window_tabs[current_window].index(first_item)
            window.Element('_TAB').Update(set_to_index=important_index)

    elif event == 'Delete selected searched':
        try:
            indices_to_delete = []
            print(len(first_session.window_tabs[current_window]))
            for tab_name in values['_SEARCH']:
                indices_to_delete += [get_index(tab_name)]
            indices_to_delete.sort(reverse=True)
            for index_to_delete in indices_to_delete:
                first_session.held_json["windows"][current_window_index]["tabs"].pop(index_to_delete-1)
            print(len(indices_to_delete))
            first_session = sessionInfo(first_session.held_json)
            if use_urls:
                window.Element('_TAB').Update(values=first_session.window_tabs_urls[values['_WIN'][0]])
            else:
                window.Element('_TAB').Update(values=first_session.window_tabs[values['_WIN'][0]])
            matched_urls = []
            matched_titles = []

            #modify the search function if this becomes too slow
            count = 0
            for url in matched_urls:
                url_index = first_session.window_tabs_urls[current_window].index(url)
                if url_index < indices_to_delete[-1]:
                    count += 1
                    
            if values['In Search'] != '' and current_window != None:
                for url in first_session.window_tabs_urls[current_window]:
                    if values['In Search'] in url:
                        matched_urls += [url]
                        url_index = first_session.window_tabs_urls[current_window].index(url)
                        matched_titles += [first_session.window_tabs[current_window][url_index]]
                        if url_index < indices_to_delete[-1]:
                            count += 1
            print(len(first_session.window_tabs[current_window]))
            if (use_urls):
                window.Element('_SEARCH').Update(values=matched_urls, set_to_index=count)
            else:
                window.Element('_SEARCH').Update(values=matched_titles, set_to_index=count)
            
        except:
            print("wassup")
    elif event == 'Hide/Show URL':
        if (use_urls):
            use_urls = False
            window.Element('_TAB').Update(values=get_listbox_values(first_session.window_tabs, values['_WIN']), set_to_index=current_tab_index)
            equiv_title = first_session.window_tabs[current_window][current_tab_index]
            window.Element('_HIS').Update(values=first_session.tabs_history[equiv_title])
        else:
            use_urls = True
            window.Element('_TAB').Update(values=get_listbox_values(first_session.window_tabs_urls, values['_WIN']), set_to_index=current_tab_index)
            equiv_url = first_session.window_tabs_urls[current_window][current_tab_index]
            window.Element('_HIS').Update(values=first_session.tabs_history_urls[equiv_url])

    elif event == 'Overwrite':
        dump_json(values['Session Write'], first_session.held_json)
    else:
        print(event, values)
    time.sleep(.1)


window.Close()
# sg.ChangeLookAndFeel('BlueMono')

# Column layout
# col = [[sg.Text('col Row 1', text_color='white', background_color='blue')],
#        [sg.Text('col Row 2', text_color='white', background_color='blue'), sg.Input('col input 1')],
#        [sg.Text('col Row 3', text_color='white', background_color='blue'), sg.Input('col input 2')]]

# layout = [[sg.Listbox(values=('Listbox Item 1', 'Listbox Item 2', 'Listbox Item 3'), select_mode=sg.LISTBOX_SELECT_MODE_MULTIPLE, size=(20,3)), sg.Column(col, background_color='blue')],
#            [sg.Input('Last input')],
#            [sg.OK()]]

# Display the Window and get values

#event, values = sg.Window('Compact 1-line Window with column', layout).Read()

#sg.Popup(event, values, line_width=200)
