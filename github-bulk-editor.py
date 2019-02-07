#!/usr/bin/python3

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
import requests, json


# credentials/headers
cred = ("floe", "api_key_or_password_here") # TODO: fill this in
headers = {"Accept": "application/vnd.github.nightshade-preview+json"}


# TODO if you want to extend this tool, start here
# command title: [ GET url, JSON field to extract from result ]
fetch_cmds = { 
    "Get all repositories": [ "https://api.github.com/user/repos", "full_name"],
    "Get all teams": [ "https://api.github.com/orgs/mmbuw/teams", "slug" ], # TODO: make org name editable
    "Get all members": [ "https://api.github.com/orgs/mmbuw/members", "login" ], # TODO: make org name editable
}

# command title: [ request function, url, parameters ] (will be passed through format(name,id), hence the double braces)
action_cmds = {
    "Transfer repository": [ "github_post", "https://api.github.com/repos/{0}/transfer", '{{ "new_owner": "{0}", "team_ids": [] }}' ],
    "Delete team": [ "github_delete", "https://api.github.com/teams/{1}", "" ],
    "Remove member": [ "github_delete", "https://api.github.com/orgs/mmbuw/members/{0}", "" ], # TODO: fixed org name
}


# fetch all items from url (with pagination)
def github_get_all(url):

    results = []
    link = url

    while link != "":

        r = requests.get(link,auth=cred,headers=headers,allow_redirects=True)
        results.extend(r.json())

        link = ""
        link_header = r.headers.get("Link","")
        links = link_header.split(",")

        for new_link in links:
            if 'rel="next"' in new_link:
                link = new_link.split(";")[0].strip("< >")

    return results

# post a payload to url
def github_post(url,payload):

    r = requests.post(url,auth=cred,headers=headers,data=payload,allow_redirects=True)
    return r

# delete a resource
def github_delete(url,payload):

    r = requests.delete(url,auth=cred,headers=headers,allow_redirects=True)
    return r


class GithubRepoList(Gtk.Window):

    def __init__(self):
        Gtk.Window.__init__(self, title="Github Bulk Editor")
        self.set_icon_name("format-indent-more-symbolic")
        self.set_border_width(10)

        #Setting up the self.grid in which the elements are to be positionned
        self.box= Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.add(self.box)

        # combobox for possible list fetch commands
        self.source = Gtk.ComboBoxText()
        self.source.append_text("[1. Select items to fetch]")
        self.source.set_active(0)
        for cmd in fetch_cmds:
            self.source.append_text(cmd)
        self.source.connect("changed",self.on_source_activate)

        # combobox for possible list fetch commands
        self.action = Gtk.ComboBoxText()
        self.action.append_text("[2. Select action to perform]")
        self.action.set_active(0)
        for cmd in action_cmds:
            self.action.append_text(cmd)

        #Creating the ListStore model
        self.liststore = Gtk.ListStore(bool, str, str, int)

        #creating the treeview, making it use the filter as a model, and adding the columns
        self.treeview = Gtk.TreeView.new_with_model(self.liststore)

        renderer_toggle = Gtk.CellRendererToggle()
        renderer_toggle.connect("toggled",self.on_cell_toggled)
        column_toggle = Gtk.TreeViewColumn("Enable", renderer_toggle, active=0)
        self.treeview.append_column(column_toggle)

        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("Result", renderer, text=1)
        self.treeview.append_column(column)

        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("Item Name", renderer, text=2)
        column.set_sort_column_id(2)
        self.treeview.append_column(column)

        # command bar
        self.command = Gtk.Entry()
        self.command.set_placeholder_text("[3. Enter target API parameter & hit enter]")
        self.command.set_icon_from_icon_name(Gtk.EntryIconPosition.SECONDARY, "emblem-ok-symbolic")
        self.command.connect("activate",self.on_command_activate)

        #setting up the layout, putting the treeview in a scrollwindow, and the buttons in a row
        self.scrollable_treelist = Gtk.ScrolledWindow()
        self.scrollable_treelist.set_vexpand(True)
        self.box.pack_start(self.source,False,True,0)
        self.box.pack_start(self.scrollable_treelist,True,True,0)
        self.box.pack_start(self.action,False,True,0)
        self.box.pack_end(self.command,False,True,0)
        self.scrollable_treelist.add(self.treeview)

        self.show_all()

    def on_cell_toggled(self, widget, path):
        self.liststore[path][0] = not self.liststore[path][0]

    def on_source_activate(self, widget):
        cmd = widget.get_active_text()
        url = fetch_cmds[cmd][0]
        field = fetch_cmds[cmd][1]
        print(cmd,url,field)
        self.liststore.clear()
        for item in github_get_all(url):
            # FIXME: progress indicator doesn't work, main thread is blocked here
            self.liststore.append([False,"",item[field],item["id"]])

    def on_command_activate(self, widget):
        cmd = self.action.get_active_text()
        verb = action_cmds[cmd][0]
        verb = globals()[verb]
        url = action_cmds[cmd][1]
        param = widget.get_text()
        params = action_cmds[cmd][2]
        print(cmd,verb,url,param,params)
        for item in self.liststore:
            if item[0]:
                target = item[2]
                target_id = item[3]
                tmp_params = params.format(param)
                tmp_url = url.format(target,target_id)
                print(verb,tmp_url,tmp_params)
                res = verb(tmp_url,tmp_params)
                item[1] = str(res.status_code)
 
win = GithubRepoList()
win.connect("destroy", Gtk.main_quit)
win.show_all()
Gtk.main()

