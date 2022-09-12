#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (C) 2018 Valter Nazianzeno <manipuladordedados at gmail dot com>
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

import os
import datetime
import npyscreen
import configparser
from pdiary.lib import database
from pdiary.lib import utils

__version__ = 1.65

db = None

config = configparser.ConfigParser()
config.optionxform = str
CONFIG_DIR_PATH = os.path.expanduser("~")+"/.config/pdiary/"
DB_FILE = CONFIG_DIR_PATH+"data.db"

# Input data form
class NewEntryForm(npyscreen.ActionForm, npyscreen.SplitForm):
    OK_BUTTON_TEXT = "💾 Save"
    CANCEL_BUTTON_TEXT = "❎ Cancel"
    CANCEL_BUTTON_BR_OFFSET = (2, 17)

    def create(self):
        self.title = self.add(npyscreen.TitleText, name="🆔 Title:")
        self.date = self.add(npyscreen.TitleDateCombo, name="📆 Date:")
        self.text = self.add(npyscreen.MultiLineEdit, slow_scroll=True, rely=7)

    # Clear the fields if the user returns to the main menu
    def clearvalues(self):
        self.title.value = None
        self.date.value = None
        self.text.value = ""

    def on_ok(self):
        if self.title.get_value() == "":
            npyscreen.notify_confirm("The Title Field is empty", "Missing something?", editw=1)
        if len(self.text.get_value_as_list()) == 0:
            npyscreen.notify_confirm("The Page is empty", "Missing something?", editw=1)
        else:
            db.add(self.title.get_value(), self.date.value.strftime("%Y-%m-%d"), self.text.value)
            npyscreen.notify_confirm("✔ Saved successfully!", editw=1)
            self.clearvalues()
            self.parentApp.switchForm("MAINMENU")

    def on_cancel(self):
        exiting = npyscreen.notify_yes_no("Are you sure you want to cancel?"+
                                          " This session will be lost.",
                                          "Quit?", editw=1)
        if exiting:
            self.clearvalues()
            self.parentApp.switchFormPrevious()

# Manage the main menu options
class MenuAction(npyscreen.MultiLineAction):
    def actionHighlighted(self, act_on_this, key_press):
        if act_on_this == "📝 Add entry":
            self.parent.parentApp.switchForm("NEWENTRY")
        if act_on_this == "📚 View previous entries":
            self.parent.parentApp.switchForm("LISTENTRIES")
        if act_on_this == "🔎 Search":
            self.parent.parentApp.switchForm("SEARCHENTRIES")
        if act_on_this == "⚙  Settings":
            self.parent.parentApp.switchForm("CONFIGURATION")
        if act_on_this == "❎ Exit":
            exiting = npyscreen.notify_yes_no("Are you sure you want to quit?", "Quit?", editw=1)
            if exiting:
                npyscreen.notify_confirm("Goodbye!", editw=1)
                exit()
            else:
                pass

# Put the MultiLineAction widget inside a box
class MenuBox(npyscreen.BoxTitle):
    _contained_widget = MenuAction

# Main menu class
class MainMenuForm(npyscreen.FormBaseNewWithMenus):
    # Hide the ok button
    OK_BUTTON_TEXT = None
    MENU_KEY = "^H"

    def create(self):
        y, x = self.useable_space()
        # max_y, max_x = self.curses_pad.getmaxyx() also work
        menu_itens = ["📝 Add entry",
                      "📚 View previous entries",
                      "🔎 Search",
                      "⚙  Settings",
                      "❎ Exit"]
        self.display()
        self.add(npyscreen.MultiLineEdit, editable=False,
                 value="╔═╗┌┬┐┬┌─┐┬─┐┬ ┬\n╠═╝ │││├─┤├┬┘└┬┘\n╩  ─┴┘┴┴ ┴┴└─ ┴",
                 rely=(y-18) // 2, relx=(x-17) // 2)
        # Subtracting the size of the screen with the size of the widgets and
        # dividing the result for two centralizes the widget on the screen.
        self.add(MenuBox, name="Menu", slow_scroll=True, values=menu_itens,
                 relx=(x-33) // 2, rely=(y-8) // 2, max_height=8, max_width=33)
        self.menu = self.new_menu(name="Help", shortcut="^H")
        self.menu.addItem("⁈ About", self.aboutMessage )

    def aboutMessage(self):
        npyscreen.notify_confirm("\t\tPdiary 1.65\n\nhttps://github.com/manipu"\
        "ladordedados/pdiary\n\nCopyright (C) 2022 Valter Nazianzeno\n\nThis"\
        " program comes with ABSOLUTELY NO WARRANTY.See the GNU General "\
        "Public License for more details.", "About Pdiary", editw=1)

# Manages the selection of items in the entry list
class ListAction(npyscreen.MultiLineAction):
    def actionHighlighted(self, act_on_this, key_press):
        self.parent.parentApp.getForm("VIEWENTRIES").value = db.list_entries().index(act_on_this)
        self.parent.parentApp.switchForm("VIEWENTRIES")

# List all entries
class ListEntriesForm(npyscreen.ActionFormMinimal, npyscreen.SplitForm):
    OK_BUTTON_TEXT = "⬅ Back"
    MAIN_WIDGET_CLASS = ListAction

    def create(self):
        self.title = self.add(npyscreen.TitleFixedText, name="📆 Date", editable=False)
        self.date = self.add(npyscreen. TitleFixedText, name="🆔 Title", relx=17,
                             rely=2, editable=False)
        self.text = self.add(ListAction, slow_scroll=True, rely=4)

    def on_ok(self):
        self.parentApp.setNextForm("MAINMENU")

    def beforeEditing(self):
        self.text.values = db.list_entries()

class ViewEntriesForm(npyscreen.FormBaseNewWithMenus, npyscreen.SplitForm):
    def create(self):
        self.value = None
        self.title = self.add(npyscreen.TitleFixedText, name="🆔 Title:", editable=False)
        self.date = self.add(npyscreen.TitleFixedText, name="📆 Date:", rely=3, editable=False)
        self.text = self.add(npyscreen.Pager, autowrap=False, scroll_exit=True,
                             rely=7, editable=True)
        self.menu = self.new_menu(name="", shortcut="m")
        self.menu.addItem("⬅ Back", self.on_ok)
        self.menu.addItem("↗ Export as Plain Text", self.to_plain_text)
        self.menu.addItem("📝 Edit", self.edit_form)
        self.menu.addItem("🗑 Delete", self.del_entry)

    def del_entry(self):
        delete = npyscreen.notify_yes_no("Are you sure you want to delete this entry?",
                                         "Delete?", editw=1)
        if delete:
            db.remove(self.value)
            npyscreen.notify_confirm("Entry was deleted successfully!", editw=1)
            self.parentApp.switchForm("LISTENTRIES")

    def to_plain_text(self):
        utils.WriteFile.toText(self,
                               db.view(self.value)[1],
                               db.view(self.value)[2],
                               db.view(self.value)[3])
        msg = "Saved as {}".format(config.get("DEFAULT", "Export_Folder")+
                                            db.view(self.value)[2]+" - "+db.view(self.value)[1]+".txt")
        npyscreen.notify_confirm(msg, editw=1)

    def edit_form(self):
        self.parentApp.getForm("EDITENTRY").value = self.value
        self.parentApp.switchForm("EDITENTRY")

    def on_ok(self):
        self.parentApp.switchForm("LISTENTRIES")

    def beforeEditing(self):
        self.title.value = db.view(self.value)[1]
        self.date.value = db.view(self.value)[2]
        self.text.values = db.view(self.value)[3].split("\n")

# Edit content
class EditEntryForm(npyscreen.ActionForm, npyscreen.SplitForm):
    OK_BUTTON_TEXT = "🔄 Update"
    CANCEL_BUTTON_TEXT = "❎ Cancel"
    CANCEL_BUTTON_BR_OFFSET = (2, 17)

    def create(self):
        self.title = self.add(npyscreen.TitleText, name="🆔 Title:")
        self.date = self.add(npyscreen.TitleDateCombo, name="📆 Date:")
        self.text = self.add(npyscreen.MultiLineEdit, slow_scroll=True, rely=7)

    def beforeEditing(self):
        self.title.value = db.view(self.value)[1]
        self.date.value = datetime.datetime.strptime(db.view(self.value)[2], "%Y-%m-%d")
        self.text.value = db.view(self.value)[3]

    def on_ok(self):
        if self.title.get_value() == "":
            npyscreen.notify_confirm("The Title Field is empty", "Missing something?", editw=1)
            self.parentApp.setNextForm("MAINMENU")
        if len(self.text.get_value_as_list()) == 0:
            npyscreen.notify_confirm("The Page is empty", "Missing something?", editw=1)
        else:
            db.edit(self.value, self.title.get_value(),
                    self.date.value.strftime("%Y-%m-%d"), self.text.value)
            npyscreen.notify_confirm("The entry was successfully updated!", editw=1)
            self.parentApp.switchForm("MAINMENU")

    def on_cancel(self):
        exiting = npyscreen.notify_yes_no("Are you sure you want to cancel?"+
                                          " This session will be lost.", "Quit?", editw=1)
        if exiting:
            self.parentApp.switchFormPrevious()

class ListAction2(npyscreen.MultiLineAction):
    def actionHighlighted(self, act_on_this, key_press):
        self.parent.parentApp.getForm("VIEWENTRIES").value = db.list_entries().index(act_on_this)
        self.parent.parentApp.getForm("SEARCHENTRIES").clear()
        self.parent.parentApp.switchForm("VIEWENTRIES")

# Text search
class SearchEntriesForm(npyscreen.ActionForm, npyscreen.SplitForm):
    OK_BUTTON_TEXT = "🔎 Search"
    CANCEL_BUTTON_TEXT = "❎ Cancel"
    CANCEL_BUTTON_BR_OFFSET = (2, 23)
    MAIN_WIDGET_CLASS = ListAction2

    def create(self):
        self.search_bar = self.add(npyscreen.TitleText, name = "Search:" )
        self.search_list = self.add(ListAction2, slow_scroll=True, rely=4)

    def on_ok(self):
        def check_ifexists(self, term):
            if db.resultado(term):
                npyscreen.notify_confirm("Found {0} entries.".format(str(len(
                                    db.list_searched_entries(str(self.search_bar.value))))), editw=1)
            else:
                npyscreen.notify_confirm("Nothing was found in the database.", editw=1)

        if not self.search_bar.value:
            npyscreen.notify_confirm("You need to write something.", editw=1)
        if len(self.search_bar.value) != 0:
            check_ifexists(self, str(self.search_bar.value))
            self.search_list.values = db.list_searched_entries(str(self.search_bar.value))

    def on_cancel(self):
        exiting = npyscreen.notify_yes_no("Are you sure you want to cancel?", "Quit?", editw=1)
        self.clear()
        if exiting:
            self.parentApp.switchFormPrevious()

    def clear(self):
        self.search_bar.value = None
        self.search_list.values = ""

# Settings form
class ConfigurationForm(npyscreen.ActionForm):
    OK_BUTTON_TEXT = "✅ Save"
    CANCEL_BUTTON_TEXT = "❎ Cancel"
    CANCEL_BUTTON_BR_OFFSET = (2, 16)

    def create(self):
        config = configparser.ConfigParser()
        config.optionxform = str
        config.read(CONFIG_DIR_PATH+"pdiary.conf")
        self.tOptions = ["PdiaryTheme", "DefaultTheme", "ElegantTheme", "ColorfulTheme",
            "BlackOnWhiteTheme", "TransparentThemeDarkText", "TransparentThemeLightText"]

        if not os.path.exists(CONFIG_DIR_PATH):
            self.theme_select = self.add(npyscreen.TitleSelectOne, max_height=8, value=self.tOptions.index(
                            "PdiaryTheme"), name="Theme:", values = self.tOptions, scroll_exit=True)
            self.export_folder = self.add(npyscreen.TitleFilenameCombo, name="Export Folder:",
                                            select_dir=True, value=utils.USER_HOME+"/")
        else:
            self.theme_select = self.add(npyscreen.TitleSelectOne, max_height=8, value=self.tOptions.index(
                            config.get("DEFAULT", "Theme")), name="Theme:", values = self.tOptions, scroll_exit=True)
            self.export_folder = self.add(npyscreen.TitleFilenameCombo, name="Export Folder:",
                                            select_dir=True, value=config.get("DEFAULT", "Export_Folder"))

    def on_ok(self):
        config.set("DEFAULT", "Export_Folder", self.export_folder.value)
        config.set("DEFAULT", "Theme", str(self.tOptions[self.theme_select.value[0]]))
        with open(CONFIG_DIR_PATH+"pdiary.conf", "w") as configfile:
            config.write(configfile)
        npyscreen.notify_confirm("Configurations Saved!\nIf you changed the theme you need to restart "\
                                                "the application to the new settings take effect!", editw=1)
        self.parentApp.switchFormPrevious()

    def on_cancel(self):
        self.parentApp.switchFormPrevious()

class PasswordBox(npyscreen.BoxTitle):
    _contained_widget = npyscreen.TitlePassword
    _contained_widget.name = "🔒 Password:"

# Password option
class PasswordForm(npyscreen.ActionFormMinimal):
    OK_BUTTON_TEXT = "🔓 Enter"
    OK_BUTTON_BR_OFFSET = (2, 10)

    def create(self):
        y, x = self.useable_space()
        # Message for the first run
        if not os.path.isfile(database.DB_FILE):
            self.passbox = self.add(PasswordBox, name="Create a password for your diary 🔐",
                                    relx=(x-50) // 2, rely=(y-6) // 2, max_height=6, max_width=50)
        self.passbox = self.add(PasswordBox, name="Please enter the password 🛡",
                                relx=(x-50) // 2, rely=(y-6) // 2, max_height=6, max_width=50)
        self.add(npyscreen.MultiLineEdit, editable=False,
                 value="╔═╗┌┬┐┬┌─┐┬─┐┬ ┬\n╠═╝ │││├─┤├┬┘└┬┘\n╩  ─┴┘┴┴ ┴┴└─ ┴",
                 rely=(y-18) // 2, relx=(x-17) // 2)

    def on_ok(self):
        if not self.passbox.value:
            npyscreen.notify_confirm("A password is required for access into the diary.", editw=1)
        elif len(self.passbox.value) < 8:
            npyscreen.notify_confirm("The password must be at least 8 characters.", editw=1)
            self.passbox.value = None
        else:
            try:
                from peewee import DatabaseError
                global db
                db = database.dbManager(password=self.passbox.value)
                self.parentApp.switchForm("MAINMENU")
            except DatabaseError:
                npyscreen.notify_confirm("Password is incorrect. Please try again.", editw=1)
                self.passbox.value = None

class FirstRunMessage(npyscreen.MultiLineEdit):
    pass

class FirstRunBox(npyscreen.BoxTitle):
    _contained_widget = FirstRunMessage

# First run form
class FirstRunForm(npyscreen.ActionForm):
    OK_BUTTON_TEXT = "✅ Continue"
    CANCEL_BUTTON_TEXT = "❎ Cancel"
    CANCEL_BUTTON_BR_OFFSET = (2, 21)

    def create(self):
        y, x = self.useable_space()
        self.messagebox = self.add(FirstRunBox, value="This is the first time you are running"\
        " pdiary.\nSome configurations are need.\nYou can change then later on the settings menu.", editable=False,
                contained_widget_arguments={'color': "WARNING"},
                rely=1, relx=(x-51) // 2, max_height=5, max_width=51)
        self.enablepass = self.add(npyscreen.TitleSelectOne, value=[1,], name="Password",
                values=["No","Yes"], scroll_exit=True, rely=9, max_height=5)
        self.exportdir = self.add(npyscreen.TitleFilenameCombo, name="Export Folder:",
        value=utils.USER_HOME, rely=14, select_dir=True, editable=False)

    def on_ok(self):
        if os.path.exists(self.exportdir.get_value()) and os.path.isdir(self.exportdir.get_value()):
            os.mkdir(CONFIG_DIR_PATH)
            config["DEFAULT"]["Password"] = str(self.enablepass.get_value()[0] == True)
            config["DEFAULT"]["Export_Folder"] = utils.USER_HOME+"/"
            config["DEFAULT"]["Theme"] = "PdiaryTheme"
            with open(CONFIG_DIR_PATH+"pdiary.conf", "w") as configfile:
                config.write(configfile)
            if self.enablepass.get_value()[0] == True:
                self.parentApp.switchForm("PASSWORD")
            else:
                global db
                db = database.dbManager(password=None)
                self.parentApp.switchForm("MAINMENU")
        else:
            npyscreen.notify_confirm("Invalid Directory.", editw=1)

    def on_cancel(self):
        exiting = npyscreen.notify_yes_no("Are you sure you want to cancel?",
                                          "Quit?", editw=1)
        if exiting:
            npyscreen.notify_confirm("Goodbye!", editw=1)
            exit()
        else:
            pass

class PdiaryTheme(npyscreen.ThemeManager):
    default_colors = {
        "DEFAULT"     : "RED_BLACK",
        "FORMDEFAULT" : "WHITE_BLACK",
        "NO_EDIT"     : "BLUE_BLACK",
        "STANDOUT"    : "CYAN_BLACK",
        "CURSOR"      : "WHITE_BLACK",
        "CURSOR_INVERSE": "BLACK_WHITE",
        "LABEL"       : "BLUE_BLACK",
        "LABELBOLD"   : "YELLOW_BLACK",
        "CONTROL"     : "GREEN_BLACK",
        "WARNING"     : "RED_BLACK",
        "CRITICAL"    : "BLACK_RED",
        "GOOD"        : "GREEN_BLACK",
        "GOODHL"      : "GREEN_BLACK",
        "VERYGOOD"    : "BLACK_GREEN",
        "CAUTION"     : "YELLOW_BLACK",
        "CAUTIONHL"   : "BLACK_YELLOW",
    }

# Register all forms and start then
class App(npyscreen.StandardApp):
    def onStart(self):
        # Make it easy to store and call the themes
        sThemes =           {"PdiaryTheme": PdiaryTheme,
                            "DefaultTheme": npyscreen.Themes.DefaultTheme,
                            "ElegantTheme": npyscreen.Themes.ElegantTheme,
                            "ColorfulTheme": npyscreen.Themes.ColorfulTheme,
                            "BlackOnWhiteTheme": npyscreen.Themes.BlackOnWhiteTheme,
                            "TransparentThemeDarkText": npyscreen.Themes.TransparentThemeDarkText,
                            "TransparentThemeLightText": npyscreen.Themes.TransparentThemeLightText}
        # Detect if the configuration directory exists, if not, show the first run screen
        if not os.path.exists(CONFIG_DIR_PATH):
            # Set the theme. DefaultTheme is used by default
            npyscreen.setTheme(sThemes["PdiaryTheme"])
            self.addForm("MAIN", FirstRunForm, name="Welcome to Pdiary")
        else:
            config.read(CONFIG_DIR_PATH+"pdiary.conf")
            # If the password option is habilited shows the password screen at startup
            npyscreen.setTheme(sThemes[str(config.get("DEFAULT", "Theme"))])
            if config.getboolean("DEFAULT", "Password") == True:
                self.addForm("MAIN", PasswordForm, name="Welcome to Pdiary")
            # If the password protection is turned off, go right into the main menu screen
            else:
                global db
                db = database.dbManager(password=None)
                self.addForm("MAIN", MainMenuForm, name="Welcome to Pdiary")

        self.addForm("PASSWORD", PasswordForm, name="Welcome to Pdiary")
        self.addForm("MAINMENU", MainMenuForm, name="Welcome to Pdiary")
        self.addForm("NEWENTRY", NewEntryForm, name="New Entry", draw_line_at=5)
        self.addForm("LISTENTRIES", ListEntriesForm, name="View Last Entries", draw_line_at=3)
        self.addForm("VIEWENTRIES", ViewEntriesForm, name="View Entry", draw_line_at=5)
        self.addForm("SEARCHENTRIES", SearchEntriesForm, name="Search Entries", draw_line_at=3)
        self.addForm("EDITENTRY", EditEntryForm, name="Edit Entry", draw_line_at=5)
        self.addForm("CONFIGURATION", ConfigurationForm, name="Settings")
