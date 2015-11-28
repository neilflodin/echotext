# echotext Version 1.1 by Neil Flodin
# 
# A simply widget that uses predictive text analysis to provide 
# user customized predictive text input, similar to that seen now 
# on many smartphones.
# 
# The text of the MIT license is below.
# 
# 
# Copyright (c) 2015 Neil Flodin <neil@neilflodin.com>
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

# Tkinter library used for GUI
from tkinter import *

# Specifically import these separate tkinter modules
import tkinter.messagebox
import tkinter.commondialog
'''
# These are used to query Princeton's WordNet for parts of speech in order to make more educated guesses
from bs4 import BeautifulSoup
import requests
import urllib
'''
# For easy, good file IO as well as web interfacing (maybe)
import json
import os

# Used to get monitor information when placing the window
import win32con
'''
# Word part of speech tagging, just a great general-usage natural language processor
import nltk
# Load nltk components
try:
    nltk.data.find("taggers/averaged_perceptron_tagger.zip")
except LookupError:
    nltk.download("averaged_perceptron_tagger")
try:
    nltk.data.find("tokenizers/punkt.zip")
except LookupError:
    nltk.download("punkt")
'''

# I <3 multithreading (Used for update_sources_masterobject)
import threading

# Sleep function
import time

# Get file:// URIs
import pathlib

# String splitting
import re

# Keylogging components
import pyHook

# Keyboard entry simulation
import ctypes
import win32api
MAPVK_VK_TO_VSC = 0
MAPVK_VSC_TO_VK = 1
MAPVK_VK_TO_CHAR = 2
MAPVK_VSC_TO_VK_EX = 3
MAPVK_VK_TO_VSC_EX = 4
KLF_ACTIVATE = 1,
KLF_SUBSTITUTE_OK = 2
KLF_REORDER = 8
KLF_REPLACELANG = 0x10
KLF_NOTELLSHELL = 0x80
KLF_SETFORPROCESS = 0x00100
KLF_SHIFTLOCK = 0x10000
KLF_RESET = 0x40000000
SendInput = ctypes.windll.user32.SendInput
PUL = ctypes.POINTER(ctypes.c_ulong)
class KeyBdInput(ctypes.Structure):
    _fields_ = [("wVk", ctypes.c_ushort),
                ("wScan", ctypes.c_ushort),
                ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong),
                ("dwExtraInfo", PUL)]
class HardwareInput(ctypes.Structure):
    _fields_ = [("uMsg", ctypes.c_ulong),
                ("wParamL", ctypes.c_short),
                ("wParamH", ctypes.c_ushort)]
class MouseInput(ctypes.Structure):
    _fields_ = [("dx", ctypes.c_long),
                ("dy", ctypes.c_long),
                ("mouseData", ctypes.c_ulong),
                ("dwFlags", ctypes.c_ulong),
                ("time",ctypes.c_ulong),
                ("dwExtraInfo", PUL)]
class Input_I(ctypes.Union):
    _fields_ = [("ki", KeyBdInput),
                 ("mi", MouseInput),
                 ("hi", HardwareInput)]
class Input(ctypes.Structure):
    _fields_ = [("type", ctypes.c_ulong),
                ("ii", Input_I)]
def PressKey(hexKeyCode):
    extra = ctypes.c_ulong(0)
    ii_ = Input_I()
    ii_.ki = KeyBdInput( 0, win32api.MapVirtualKey(hexKeyCode, MAPVK_VK_TO_VSC),  0x0008, 0, ctypes.pointer(extra) )
    x = Input( ctypes.c_ulong(1), ii_ )
    ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))
    return
def ReleaseKey(hexKeyCode):
    extra = ctypes.c_ulong(0)
    ii_ = Input_I()
    ii_.ki = KeyBdInput( 0, win32api.MapVirtualKey(hexKeyCode, MAPVK_VK_TO_VSC), 0x0008 | win32con.KEYEVENTF_KEYUP, 0, ctypes.pointer(extra) )
    x = Input( ctypes.c_ulong(1), ii_ )
    ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))
    return
def SetKeyStateUp(hexKeyCode):
    if win32api.GetAsyncKeyState(hexKeyCode) != 0:
        ReleaseKey(hexKeyCode)
    return
def SetKeyStateDown(hexKeyCode):
    if win32api.GetAsyncKeyState(hexKeyCode) == 0:
        PressKey(hexKeyCode)
    return

# Create "sources" directory if it doesn't exist
if not os.path.exists("sources"):
    os.makedirs("sources")

# Function to save updated functions on the fly
def save_settings(settingsObj):
    settings_file = open("settings.json", "w")
    settings_file.write(json.dumps(settingsObj))
    settings_file.close()

# Try to load settings file
# If unsuccessful, create one
# Default settings
default_settings = { "keep_window_on_top" : TRUE, "make_window_transparent" : FALSE, "version": "1.1" }
settings = {}
openedFile = {}
fileText = ""
if os.path.isfile(os.path.dirname(os.path.realpath(__file__)) + "/settings.json"):
    openedFile = open("settings.json", "r")
    fileText = openedFile.read()
    # Now try to JSON decode our read file text
    try:
        settings = json.loads(fileText)
    except ValueError:
        settings = default_settings
        save_settings(default_settings)
else:
    openedFile = open("settings.json", "w")
    fileText = json.dumps(default_settings)
    openedFile.write(fileText)
    settings = json.loads(fileText)
openedFile.close()

# Function to save updated sources on the fly
def save_sources(sourcesObj):
    sources_file = open("sources.json", "w")
    sources_file.write(json.dumps(sourcesObj))
    sources_file.close()
    return

# Load the list of sources from sources.json
default_sources = { "version" : "1.1", "sources_list" : [] }
sources_list = {}
openedFile = {}
fileText = ""
if os.path.isfile(os.path.dirname(os.path.realpath(__file__)) + "/sources.json"):
    openedFile = open("sources.json", "r")
    fileText = openedFile.read()
    # Try to decode JSON
    try:
        sources_list = json.loads(fileText)
    except ValueError:
        sources_list = default_sources
        save_sources(default_sources)
else:
    openedFile = open("sources.json", "w")
    fileText = json.dumps(default_sources)
    openedFile.write(fileText)
    sources_list = json.loads(fileText)
openedFile.close()

# Create object that is the combination of all loaded sources
source_master_object = {}

# Figure out window dimensions

window_width = 400
window_height = 200

# Figure out starting x-y position on the screen
window_initial_x_offset = win32api.GetMonitorInfo(win32api.EnumDisplayMonitors()[0][0])["Work"][2] - window_width - 100
window_initial_y_offset = win32api.GetMonitorInfo(win32api.EnumDisplayMonitors()[0][0])["Work"][3] - window_height - 100

# Initialize window/root object
root = Tk()

# Set the window's icon
root.tk.call("wm", "iconbitmap", root._w, "-default", "icon.ico")

# Set the window's title too
root.wm_title("echotext")

# Set as non-resizable
root.resizable(width = FALSE, height = FALSE)

# Position the window on the screen
root.geometry(str(window_width) + "x" + str(window_height) + "+" + str(window_initial_x_offset) + "+" + str(window_initial_y_offset))

# Keep the window above all others based on setting
if settings["keep_window_on_top"] == TRUE:
    root.wm_attributes("-topmost", "1")

# Set window transparency based on setting
if settings["make_window_transparent"] == TRUE:
    root.wm_attributes("-alpha", 0.7)

# Functions for menu bar buttons
def menu_bar_input_button():
    # Input button pressed
    sources_frame.pack_forget()
    input_frame.pack(fill = BOTH, expand = TRUE)
    return
def menu_bar_sources_button():
    # Sources button pressed
    input_frame.pack_forget()
    sourceframe_background_clicked( None )
    sources_frame.pack(fill = BOTH, expand = TRUE)
    return
def menu_bar_add_source_button():
    global add_source_dialog, source_text_entry_frame, source_text_entry_field_scrollbar, \
            source_text_entry_field, source_meta_entry_frame, source_name_entry_field, source_create_ok_buttton, root

    # "Add Source" button pressed

    # Create a new top-level dialog window
    add_source_dialog = Toplevel()
    add_source_dialog.title("Add Source Text")
    add_source_dialog.resizable(width = FALSE, height = FALSE)
    add_source_dialog.config(background = "black")
    add_source_dialog.geometry("640x480+" + str(int((win32api.GetMonitorInfo(win32api.EnumDisplayMonitors()[0][0])["Work"][2] / 2) \
        - (640 / 2))) + "+" + str(int((win32api.GetMonitorInfo(win32api.EnumDisplayMonitors()[0][0])["Work"][3] / 2) - (480 / 2))))
    
    # Format the grid pattern for the encompassing frames
    add_source_dialog.grid_rowconfigure(0, weight = 4)
    add_source_dialog.grid_rowconfigure(1, weight = 1)
    add_source_dialog.grid_columnconfigure(0, weight = 1)


    # Create the frame that will house the text material entry field
    source_text_entry_frame = Frame(master = add_source_dialog, background = "black")
    source_text_entry_frame.grid(row = 0, column = 0, padx = 6, pady = 3)

    # Create the frame that will house the name entry field and "OK" button
    source_meta_entry_frame = Frame(master = add_source_dialog, background = "black")
    source_meta_entry_frame.grid(row = 1, column = 0, padx = 6, pady = 3)

    # Create the vertical scrollbar that goes in that text field
    source_text_entry_field_scrollbar = Scrollbar(master = source_text_entry_frame)
    source_text_entry_field_scrollbar.pack(side = RIGHT, fill = Y)

    # Create the text entry field for entering raw text data
    source_text_entry_field = Text(master = source_text_entry_frame)
    source_text_entry_field.config(wrap = WORD, font = "Arial 12")
    source_text_entry_field.insert(CURRENT, "Enter your human-readable text here.")
    source_text_entry_field.pack(side = LEFT, expand = TRUE)

    # "Attach" the text field and scrollbar to each other
    source_text_entry_field_scrollbar.config( command = source_text_entry_field.yview )
    source_text_entry_field.config( yscrollcommand = source_text_entry_field_scrollbar.set )

    # Format the grid pattern for the meta entry fields
    source_meta_entry_frame.grid_rowconfigure(0, weight = 1)
    source_meta_entry_frame.grid_columnconfigure(0, weight = 3)
    source_meta_entry_frame.grid_columnconfigure(1, weight = 1)

    # Create the reference name entry box below the text entry one
    source_name_entry_field = Entry(master = source_meta_entry_frame, width = 24)
    source_name_entry_field.insert(INSERT, "Source name")
    source_name_entry_field.grid(row = 0, column = 0, padx = 6, pady = 3, sticky = N+S+E+W)

    # Create the button that will finish the reference creation process
    source_create_ok_buttton = Button(master = source_meta_entry_frame, text = "Create Source", command = source_create_ok_clicked)
    source_create_ok_buttton.grid(row = 0, column = 1, padx = 6, pady = 3, sticky = N+S+E+W)

    add_source_dialog.wm_transient(master = root)
    add_source_dialog.focus_set()
    add_source_dialog.grab_set()
    return
def menu_bar_about_button():
    tkinter.messagebox.showinfo("About", "\"EchoText\" version one point one\n\nechotext is released under the MIT license\n\
        https://opensource.org/licenses/MIT\n\nDeveloped by Neil Flodin <neil@neilflodin.com>")
    return

# Handler functions from the "Add Source" dialog
def source_create_ok_clicked():
    global add_source_dialog, source_text_entry_frame, source_text_entry_field_scrollbar, \
            source_text_entry_field, source_meta_entry_frame, source_name_entry_field, source_create_ok_buttton

    # Trim the whitespace off of the entered name
    source_name_entry_field_newname = source_name_entry_field.get().strip()
    source_name_entry_field.delete(0, END)
    source_name_entry_field.insert(0, source_name_entry_field_newname)

    # Check if source name exceeds maximum length
    if len( source_name_entry_field_newname ) > 24:
        tkinter.messagebox.showerror("Name Too Long", "The name you entered for the new source is over 24 characters long. Shorten it before you continue.")
        return

    # Check if source name matches an already created name
    for source_item in sources_list["sources_list"]:
        if source_item["source_name"] == source_name_entry_field_newname:
            tkinter.messagebox.showerror("Name Already Used", "There is already a source that has that same name. Please enter another one.")
            return

    # Check to make sure name is legit for Windows
    for character in source_name_entry_field_newname:
        if character == '\\' or character == '/' or character == ':' or character == '*' or character == '?' or \
        character == '"' or character == '<' or character == '>' or character == '|':
            # Can't use the name
            tkinter.messagebox.showerror("Name Invalid", "Source names cannot contain any of the following characters:\n\\/:*?\"<>|\nPlease enter another source name.")
            return

    # Create a loading screen while the data is added to databases
    loading_dialog = Toplevel()
    loading_dialog.title("Please wait...")
    loading_dialog.resizable(width = FALSE, height = FALSE)
    loading_dialog.config(background = "black")
    loading_dialog.wm_attributes("-disabled", "1")
    loading_dialog.geometry("300x200+" + str(int((win32api.GetMonitorInfo(win32api.EnumDisplayMonitors()[0][0])["Work"][2] / 2) \
        - (300 / 2))) + "+" + str(int((win32api.GetMonitorInfo(win32api.EnumDisplayMonitors()[0][0])["Work"][3] / 2) - (200 / 2))))

    loading_dialog_label = Label(loading_dialog, text = "Adding and sorting text into personal database...\nPlease wait...", justify = CENTER, background = "black", foreground = "white")
    loading_dialog_label.place(relx = 0.5, rely = 0.5, anchor = CENTER)

    loading_dialog.wm_transient(master = root)
    loading_dialog.focus_set()
    loading_dialog.grab_set()

    # Split raw text into sentences
    raw_text = source_text_entry_field.get("1.0", END)
    split_sentence_list = re.split("[;,.!?:]\s*", raw_text)
    empty_sentences_removed_list = []
    for chunk in split_sentence_list:
        # If, after removing the sentence's whitespace, the sentence is not empty, add it to empty_sentences_removed_list
        if chunk.strip() != "":
            # Add stripped sentence to new array
            empty_sentences_removed_list.append(chunk.strip())

    # Now we have an array of every individual sentence

    new_source_json_data = { "version" : "1.1", "top_word_list" : {} }

    # Do following for every sentence that will be parsed
    for sentence_index in range(0, len( empty_sentences_removed_list )):
        # Split the sentence into individual words by removing spaces
        current_sentence_split = empty_sentences_removed_list[sentence_index].split()
        # Do following for every word in the current sentence being parsed
        for word_index in range(0, len( current_sentence_split )):
            # If a top_word_list word entry doesn't already exist for the current word being parsed, create one
            if current_sentence_split[ word_index ] in new_source_json_data["top_word_list"]:
                # Increase top-level total_frequency by one
                new_source_json_data["top_word_list"][current_sentence_split[ word_index ]]["total_frequency"] += 1
            else:
                new_source_json_data["top_word_list"][current_sentence_split[ word_index ]] = { "subsequent_words" : [], "total_frequency" : 1 }
                
            # If the word_index isn't 0, that means the current word has a word before it
            # We can add this word as a "subsequent_word"
            if word_index > 0:
                new_subsequent = True
                for subseq_listitem_index in range(0, len( new_source_json_data["top_word_list"][current_sentence_split[ word_index - 1 ]]["subsequent_words"] )):
                    if new_source_json_data["top_word_list"][current_sentence_split[ word_index - 1 ]]["subsequent_words"][subseq_listitem_index]["word_name"] == current_sentence_split[word_index]:
                        new_source_json_data["top_word_list"][current_sentence_split[ word_index - 1 ]]["subsequent_words"][subseq_listitem_index]["subseq_frequency"] += 1
                        new_subsequent = False
                        break
                # New subseq
                if new_subsequent == True:
                    new_source_json_data["top_word_list"][current_sentence_split[ word_index - 1 ]]["subsequent_words"].append( \
                        { "word_name" : current_sentence_split[word_index], "subseq_frequency" : 1 })

    # Add this new source to sources_list and save that file
    sources_list["sources_list"].append({ "source_name" : source_name_entry_field_newname, "source_selected" : 1 })
    save_sources(sources_list)

    # Save tje new source JSON data as a JSON file
    new_source_file = open("sources/" + source_name_entry_field_newname + ".json", "w")
    new_source_file.write(json.dumps(new_source_json_data))
    new_source_file.close()

    # Return to the main window
    loading_dialog.destroy()
    add_source_dialog.destroy()
    update_sources()

    return

# Add the menu for switching between views
menu_bar = Menu(root)
menu_bar.add_command(label = "Input", command = menu_bar_input_button)
menu_bar.add_command(label = "Sources", command = menu_bar_sources_button)
menu_bar.add_command(label = "Add Source", command = menu_bar_add_source_button)
menu_bar.add_command(label = "About", command = menu_bar_about_button)
root.config(menu = menu_bar)

# Create the frame object for the keyboard input view
input_frame = Frame(master = root, background = "black", padx = 3, pady = 3)
input_frame.pack(fill = BOTH, expand = TRUE)

# Define the function called when a keyboard input button is pressed
keyEntryEnabled = True
def enterTextFromSuggestion( index ):
    global keyEntryEnabled, current_word, previous_word
    if index < len( suggestions ):
        keyEntryEnabled = False
        # Get the remainder of the word to be entered
        wordToEnter = suggestions[ index ]
        restOfCurrentWord = wordToEnter[ len( current_word ) : ]
        # Lift up the keys that were pressed in order to activate this function
        SetKeyStateUp(ord( str( index + 1 )[0] ))
        # Lift up the keys that can affect keyboard input so that the simulated input isn't messed up
        SetKeyStateUp(win32con.VK_LSHIFT)
        SetKeyStateUp(win32con.VK_RSHIFT)
        SetKeyStateUp(win32con.VK_LCONTROL)
        SetKeyStateUp(win32con.VK_RCONTROL)
        SetKeyStateUp(win32con.VK_LMENU)
        SetKeyStateUp(win32con.VK_RMENU)
        # For each character in the text to be entered, get its modifier
        # Convert modifier to hex string, and query that string for keys to be held down and the 
        # key to be typed in
        for char in restOfCurrentWord:
            keyScanEx = win32api.VkKeyScanEx(char, 0)
            keyModifier = [keyScanEx >> i & 0xff for i in (8,0)][0]
            keyVKCode = [keyScanEx >> i & 0xff for i in (8,0)][1]
            if keyModifier != -1:
                # Key entered is able to be entered with the keyboard
                if keyModifier == 1:
                    # Shift key must be pressed down when typing the letter
                    SetKeyStateUp(keyVKCode)
                    SetKeyStateUp(win32con.VK_LSHIFT)
                    SetKeyStateDown(win32con.VK_LSHIFT)
                    SetKeyStateDown(keyVKCode)
                    SetKeyStateUp(keyVKCode)
                    SetKeyStateUp(win32con.VK_LSHIFT)
                elif keyModifier == 2:
                    SetKeyStateUp(keyVKCode)
                    SetKeyStateUp(win32con.VK_LCONTROL)
                    SetKeyStateDown(win32con.VK_LCONTROL)
                    SetKeyStateDown(keyVKCode)
                    SetKeyStateUp(keyVKCode)
                    SetKeyStateUp(win32con.VK_LCONTROL)
                elif keyModifier == 4:
                    SetKeyStateUp(keyVKCode)
                    SetKeyStateUp(win32con.VK_LMENU)
                    SetKeyStateDown(win32con.VK_LMENU)
                    SetKeyStateDown(keyVKCode)
                    SetKeyStateUp(keyVKCode)
                    SetKeyStateUp(win32con.VK_LMENU)
                else:
                    SetKeyStateUp(keyVKCode)
                    SetKeyStateDown(keyVKCode)
                    SetKeyStateUp(keyVKCode)
        # Add a space after the word
        SetKeyStateUp(win32con.VK_SPACE)
        SetKeyStateDown(win32con.VK_SPACE)
        SetKeyStateUp(win32con.VK_SPACE)
        previous_word = wordToEnter
        current_word = ""
        update_suggestions()
        # Allow again for natural key pressed
        keyEntryEnabled = True
    return
    
# Adjust input_frame grid pattern
input_frame.grid_rowconfigure(0, minsize = 30, weight = 1)
input_frame.grid_rowconfigure(1, minsize = 30, weight = 1)
input_frame.grid_rowconfigure(2, minsize = 30, weight = 1)
input_frame.grid_rowconfigure(3, minsize = 30, weight = 1)
input_frame.grid_rowconfigure(4, minsize = 30, weight = 1)
input_frame.grid_columnconfigure(0, minsize = 48, weight = 1)
input_frame.grid_columnconfigure(1, minsize = 300, weight = 6)
 
# Create each label for the other key information top to bottom
keyInfoLabelList = []
keyInfoLabelList.append( Label( input_frame, text = "Alt + 1", background = "black", foreground = "white" ) )
keyInfoLabelList[0].grid(row = 0, column = 0, sticky = W)
keyInfoLabelList.append( Label( input_frame, text = "Alt + 2", background = "black", foreground = "white" ) )
keyInfoLabelList[1].grid(row = 1, column = 0, sticky = W)
keyInfoLabelList.append( Label( input_frame, text = "Alt + 3", background = "black", foreground = "white" ) )
keyInfoLabelList[2].grid(row = 2, column = 0, sticky = W)
keyInfoLabelList.append( Label( input_frame, text = "Alt + 4", background = "black", foreground = "white" ) )
keyInfoLabelList[3].grid(row = 3, column = 0, sticky = W)
keyInfoLabelList.append( Label( input_frame, text = "Alt + 5", background = "black", foreground = "white" ) )
keyInfoLabelList[4].grid(row = 4, column = 0, sticky = W)

# Create each button that will occupy the keyboard input frame
def keyInputButtonPressed( index ):
    keyEntryEnabled = False
    SetKeyStateUp(win32con.VK_TAB)
    SetKeyStateUp(win32con.VK_LMENU)
    SetKeyStateDown(win32con.VK_LMENU)
    SetKeyStateDown(win32con.VK_TAB)
    SetKeyStateUp(win32con.VK_TAB)
    SetKeyStateUp(win32con.VK_LMENU)
    keyEntryEnabled = True
    enterTextFromSuggestion( index )
    return
keyInputButtonList = []
keyInputButtonList.append(Button(input_frame, text = "", borderwidth = 3, command = lambda: keyInputButtonPressed( 0 ) ))
keyInputButtonList[0].grid( row = 0, column = 1, padx = 3, pady = 3, sticky = E+W )
keyInputButtonList.append(Button(input_frame, text = "", borderwidth = 3, command = lambda: keyInputButtonPressed( 1 ) ))
keyInputButtonList[1].grid( row = 1, column = 1, padx = 3, pady = 3, sticky = E+W )
keyInputButtonList.append(Button(input_frame, text = "", borderwidth = 3, command = lambda: keyInputButtonPressed( 2 ) ))
keyInputButtonList[2].grid( row = 2, column = 1, padx = 3, pady = 3, sticky = E+W )
keyInputButtonList.append(Button(input_frame, text = "", borderwidth = 3, command = lambda: keyInputButtonPressed( 3 ) ))
keyInputButtonList[3].grid( row = 3, column = 1, padx = 3, pady = 3, sticky = E+W )
keyInputButtonList.append(Button(input_frame, text = "", borderwidth = 3, command = lambda: keyInputButtonPressed( 4 ) ))
keyInputButtonList[4].grid( row = 4, column = 1, padx = 3, pady = 3, sticky = E+W )

# Create the frame object for the sources view
sources_frame = Frame(master = root, background = "black")
sources_frame.grid_rowconfigure(0, weight = 4)
sources_frame.grid_rowconfigure(1, weight = 1)
sources_frame.grid_columnconfigure(0, weight = 1)

# Create the frame for the bottom part of the UI
sources_bottom_ui_frame = Frame(master = sources_frame, background = "black")
sources_bottom_ui_frame.grid(row = 1, column = 0, sticky = N+S+W+E)
sources_bottom_ui_frame.grid_columnconfigure(0, weight = 1)
sources_bottom_ui_frame.grid_columnconfigure(1, weight = 1)

# Create the sources display buttons frame below the display
sources_display_buttons_frame = Frame(master = sources_bottom_ui_frame, background = "black")
sources_display_buttons_frame.grid(row = 0, column = 0)
sources_display_buttons_frame.grid_columnconfigure(0, minsize = 75, weight = 1)
sources_display_buttons_frame.grid_columnconfigure(1, minsize = 75, weight = 1)

# Callback function for rename source button
newNameDialog = None
newNameDialogText = None
newNameDialogButton = None
def rename_source_button_inner_clicked():
    global newNameDialog, newNameDialogText, newNameDialogButton
    newName = newNameDialogText.get().strip()
    if newName != None:
            if len( newName ) <= 24:
                for source_item in sources_list["sources_list"]:
                    if source_item["source_name"] == newName:
                        newNameDialogText.selection_range( 0, END )
                        tkinter.messagebox.showerror("Name Already Used", "There is already a source that has that same name. Please enter another one.")
                        return
                for character in newName:
                    if character == '\\' or character == '/' or character == ':' or character == '*' or character == '?' or character == '"' or character == '<' or character == '>' or character == '|':
                        newNameDialogText.selection_range( 0, END )
                        tkinter.messagebox.showerror("Name Invalid", "Source names cannot contain any of the following characters:\n\\/:*?\"<>|\nPlease enter another source name.")
                        return
                # Name is OK
                os.rename( "sources/" + sources_list["sources_list"][source_element_selected_index]["source_name"] + ".json", "sources/" + newName + ".json" )
                sources_list["sources_list"][source_element_selected_index]["source_name"] = newName
                save_sources( sources_list )
                update_sources()
                tkinter.messagebox.showinfo("Source Renamed", "The source has been renamed to \"" + newName + "\".")
                newNameDialog.destroy()
                return
            else:
                newNameDialogText.selection_range( 0, END )
                tkinter.messagebox.showerror("Name Too Long", "The new name is over 24 characters long. Shorten it before you continue.")
                return
    return
def rename_source_button_clicked():
    global newNameDialog, newNameDialogText, newNameDialogButton, root, sources_list
    if source_element_selected_index != None:
        newNameDialog = Toplevel()
        newNameDialog.title( "Rename Source" )
        newNameDialog.resizable( width = FALSE, height = FALSE )
        newNameDialog.config( background = "black" )
        newNameDialog.geometry("200x50+" + str(int((win32api.GetMonitorInfo(win32api.EnumDisplayMonitors()[0][0])["Work"][2] / 2) \
            - (200 / 2))) + "+" + str(int((win32api.GetMonitorInfo(win32api.EnumDisplayMonitors()[0][0])["Work"][3] / 2) - (50 / 2))))
        # Create the text entry field
        newNameDialogText = Entry( master = newNameDialog, width = 24 )
        newNameDialogText.insert( INSERT, sources_list["sources_list"][source_element_selected_index]["source_name"] )
        newNameDialogText.pack( side = TOP, fill = X, padx = 4, pady = 3 )
        # Create the button
        newNameDialogButton = Button( master = newNameDialog, text = "Rename Source", command = rename_source_button_inner_clicked )
        newNameDialogButton.pack( side = BOTTOM, fill = BOTH, padx = 4, pady = 3 )
        newNameDialog.wm_transient( master = root )
        newNameDialog.focus_set()
        newNameDialog.grab_set()
    return

# Callback function for delete source button
def delete_source_button_clicked():
    if source_element_selected_index != None:
        deletedSourceName = sources_list["sources_list"][source_element_selected_index]["source_name"]
        if tkinter.messagebox.askokcancel( "Delete Source", "This will permanently delete the source \"" + deletedSourceName + "\". Are you sure you want to continue?" ):
            # Delete the source
            os.remove( "sources/" + deletedSourceName + ".json" )
            sources_list["sources_list"].pop( source_element_selected_index )
            save_sources( sources_list )
            update_sources()
            tkinter.messagebox.showinfo("Source Deleted", "The source \"" + deletedSourceName + "\"has been deleted.")
    return

# Create the rename button for the sources display frame above
rename_source_button = Button(sources_display_buttons_frame, text = "Rename", borderwidth = 3, command = rename_source_button_clicked)
rename_source_button.grid(row = 0, column = 0, sticky = N+S+W+E)

# Create the delete button for the sources display frame above
delete_source_button = Button(sources_display_buttons_frame, text = "Delete", borderwidth = 3, command = delete_source_button_clicked)
delete_source_button.grid(row = 0, column = 1, sticky = N+S+W+E)

# Create the global settings frame below the display
global_settings_frame = Frame(master = sources_bottom_ui_frame, background = "black")
global_settings_frame.grid(row = 0, column = 1, sticky = N+S+E)

# Create the "keep window on top" label
keep_window_on_top_label = Label(global_settings_frame, text = "Keep this window on top?", background = "black", foreground = "white")
keep_window_on_top_label.grid(row = 0, column = 0, sticky = N+S+E)

# Create the "make this window transparent" label
make_window_transparent_label = Label(global_settings_frame, text = "Make this window transparent?", background = "black", foreground = "white")
make_window_transparent_label.grid(row = 1, column = 0, sticky = N+S+E)

# Callback functions if one of the checkbuttons is toggled
def keep_window_on_top_checkbutton_toggled():
    root.wm_attributes("-topmost", keep_window_on_top_checkbutton_selected.get())
    settings["keep_window_on_top"] = keep_window_on_top_checkbutton_selected.get()
    save_settings(settings)
    return
def make_window_transparent_checkbutton_toggled():
    if make_window_transparent_checkbutton_selected.get():
        root.wm_attributes("-alpha", 0.7)
    else:
        root.wm_attributes("-alpha", 1.0)
    settings["make_window_transparent"] = make_window_transparent_checkbutton_selected.get()
    save_settings(settings)
    return

# Create the "keep window on top" checkbutton
keep_window_on_top_checkbutton_selected = IntVar()
keep_window_on_top_checkbutton = Checkbutton(global_settings_frame, background = "black", \
    foreground = "black", highlightbackground = "black", activebackground = "black", activeforeground = "black", \
    variable = keep_window_on_top_checkbutton_selected, command = keep_window_on_top_checkbutton_toggled)
if settings["keep_window_on_top"]:
    keep_window_on_top_checkbutton.select()
else:
    keep_window_on_top_checkbutton.deselect()
keep_window_on_top_checkbutton.grid(row = 0, column = 1, sticky = N+S+E)

# Create the "make this window transparent" checkbutton
make_window_transparent_checkbutton_selected = IntVar()
make_window_transparent_checkbutton = Checkbutton(global_settings_frame, background = "black", \
    foreground = "black", highlightbackground = "black", activebackground = "black", activeforeground = "black", \
    variable = make_window_transparent_checkbutton_selected, command = make_window_transparent_checkbutton_toggled)
if settings["make_window_transparent"]:
    make_window_transparent_checkbutton.select()
else:
    make_window_transparent_checkbutton.deselect()
make_window_transparent_checkbutton.grid(row = 1, column = 1, sticky = N+S+E)

# Keyboard input
# Store the previous entered word in order to help prediction results
previous_word = "" # <---- Can be empty
current_word = ""
left_alt_down = False
right_alt_down = False
def on_keyboard_down_event( event ):
    global current_word, previous_word, left_alt_down, right_alt_down, keyEntryEnabled
    if keyEntryEnabled:
        if event.Key == "Lmenu":
            left_alt_down = True
        elif event.Key == "Rmenu":
            right_alt_down = True
        elif event.Key == "Space":
            # Space
            previous_word = current_word.strip()
            current_word = ""
            update_suggestions()
        elif event.Key == "Back":
            # Back
            # Remove the end character from current_word
            if len(current_word) > 0:
                current_word = current_word[:len(current_word) - 1]
                update_suggestions()
        else:
            if event.Ascii >= 33 and event.Ascii <= 254 and event.Ascii != 127 \
                and left_alt_down == False and right_alt_down == False:
                # If the letter entered is a "sentence ender", clear previous_word so that 
                # suggestions are refreshed from the top level
                if event.Ascii == '.' or event.Ascii == '?' or event.Ascii == '!':
                    previous_word = ""
                    current_word = ""
                else:
                    # Append the ASCII version of the key to the end of current_word
                    current_word = current_word + str(chr(event.Ascii))
                    update_suggestions()
    return True
def on_keyboard_up_event( event ):
    global left_alt_down, right_alt_down, keyEntryEnabled
    if keyEntryEnabled:
        if event.Key == "Lmenu":
            left_alt_down = False
        elif event.Key == "Rmenu":
            right_alt_down = False
        elif event.Ascii >= 49 and event.Ascii <= 53:
            # It's one of the 1-5 numeric keys; test for alt key to maybe enter predicted text
            if left_alt_down == True:
                # Act as though one of the 5 buttons was pressed
                SetKeyStateUp(win32con.VK_LMENU)
                enterTextFromSuggestion( int( chr( event.Ascii ) ) - 1 ) # Minus one because 1 maps to 0, 2 maps to 1, etc. for this function
                SetKeyStateDown(win32con.VK_LMENU)
            elif right_alt_down == True:
                # Act as though one of the 5 buttons was pressed
                SetKeyStateUp(win32con.VK_RMENU)
                enterTextFromSuggestion( int( chr( event.Ascii ) ) - 1 ) # Minus one because 1 maps to 0, 2 maps to 1, etc. for this function
                SetKeyStateDown(win32con.VK_RMENU)
    return True

# Functions usefol when updating and sorting word suggestions
def get_master_word_list_sorted_by_total_frequency():
    source_master_list = []
    for master_word_key in source_master_object:
        source_master_list.append( { "name" : master_word_key, \
            "subsequent_words" : source_master_object[master_word_key]["subsequent_words"], \
             "total_frequency" : source_master_object[master_word_key]["total_frequency"] } )
    source_master_list.sort( key = lambda word : word[ "total_frequency" ], reverse = True )
    return source_master_list
def get_master_word_list_sorted_by_total_frequency_sans_removed_words( removed_words_list ):
    source_master_list = []
    for master_word_key in source_master_object:
        source_master_list.append( { "name" : master_word_key, \
            "subsequent_words" : source_master_object[master_word_key]["subsequent_words"], \
             "total_frequency" : source_master_object[master_word_key]["total_frequency"] } )
    source_master_list.sort( key = lambda word : word[ "total_frequency" ], reverse = True )
    return [ item for item in source_master_list if not item["name"] in removed_words_list ]

suggestions = []

def update_suggestions():
    global source_master_object, current_word, previous_word, suggestions

    # Get the top five suggestions based on previous_word and what's currently in current_word
    del suggestions[:]
    suggestions = []

    # Test if we can use previous_word for predictions
    if previous_word in source_master_object:
        # Word is in source_master_object so we can look at subsequent words
        # First, get subsequent_words whose first letters match current_word, rank those by subseq_frequency, then 
        # second, rank remaining subsequent_words by subseq_frequency and add those to the rank.
        # Finally, if those words don't fill the 5 recommendation bars, rank the top list similarly to below
        prev_word_subsequent_words = source_master_object[ previous_word ][ "subsequent_words" ]
        # Divide subsequent_words into two further arrays: one that contains words with beginning characters 
        # that match those entered in current_word, and an array of those words which don't match.
        # The first array is where the initial predictions will come from, and then the second array (Both sorted 
        # by "frequency" variable) and then the global words object with these words taken out, sorted 
        # by "total_frequency"
        removed_words = []
        prev_word_subsequent_words_matching = []
        for listitem in prev_word_subsequent_words:
            if listitem["word_name"].lower().find( current_word.lower() ) == 0:
                removed_words.append( listitem["word_name"] )
                prev_word_subsequent_words_matching.append( listitem )

        # Sort each array by subseq_frequency
        prev_word_subsequent_words_matching.sort( key = lambda word : word[ "subseq_frequency" ], reverse = True )

        # Populate suggestions array with matching words
        for listitem in prev_word_subsequent_words_matching:
            suggestions.insert( len( suggestions ), listitem["word_name"] )

        # If still not full, populate suggestions with words matching current_word from toplevel 
        # without including removed_words. This list is sorted by frequency.


        toplevel_matching_words_sans_removed_words = []
        if len( suggestions ) < 5:
            for word in source_master_object:
                # First test to make sure the word hasn't already been removed from "suggestables"...
                if not word in removed_words:
                    # Test to see if the word could possibly overlap with current_word
                    if word.lower().find( current_word.lower() ) == 0:
                        removed_words.append( word )
                        toplevel_matching_words_sans_removed_words.append( word )

        # Sort the matching toplevel words by frequency in source_master_object
        toplevel_matching_words_sans_removed_words.sort( key = lambda word : source_master_object[ word ][ "total_frequency" ], reverse = True )

        for word_index in range( 0, len( toplevel_matching_words_sans_removed_words ) ):
            suggestions.insert( len( suggestions ), toplevel_matching_words_sans_removed_words[ word_index ] )

        # If suggestions STILL isn't full, populate it with words from the toplevel list
        # sorted by total frequency
        if len( suggestions ) < 5:
            for listitem in get_master_word_list_sorted_by_total_frequency_sans_removed_words( removed_words ):
                if not len( suggestions ) < 5:
                    break
                suggestions.insert( len( suggestions ), listitem["name"] )

    else:
        # Just get source_master_object words whose first letters match current_word, rank these by total_frequency, 
        # and append to the end of those the remaining words sorted by frequency

        name_frequency_pairs = []
        removed_words = []

        for word in source_master_object:
            # Check if current_word matches first letters of this word
            if word.lower().find( current_word.lower() ) == 0:
                name_frequency_pairs.append( { "name" : word, "frequency" : source_master_object[ word ][ "total_frequency" ] } )
                # Add this matching word to "removed_words"
                removed_words.append( word )
        
        # Sort name_frequency_pairs
        name_frequency_pairs.sort( key = lambda word : word[ "frequency" ], reverse = True )

        # Copy values from name_frequency_pairs to suggestions
        for pair_index in range( 0, len( name_frequency_pairs ) ):
            suggestions.insert( pair_index, name_frequency_pairs[ pair_index ][ "name" ] )

        # Fill the rest of the remaining suggestions array with words from master list 
        # sorted by total_frequency
        if len( suggestions ) < 5:
            for listitem in get_master_word_list_sorted_by_total_frequency_sans_removed_words( removed_words ):
                if not len( suggestions ) < 5:
                    break
                suggestions.insert( len( suggestions ), listitem["name"] )

    # Update label values based on suggestions
    for label_index in range( 0, 5 ):
        if label_index < len( suggestions ):
            keyInputButtonList[ label_index ].config( text = suggestions[ label_index ] )
        else:
             keyInputButtonList[ label_index ].config( text = "" )

    return

# Store the source element activated checkbox values
source_element_activated_variablelist = []

# Initialize the variable for sources_info_display_frame
sources_info_display_frame = None

# Variable that defines which item in the source list is selected
source_element_selected_index = None

# Initialize the lists that hold each label/checkbutton widget combo from the source list display
source_elements_label_widget_list = []
source_elements_checkbutton_widget_list = []

# Function for when a source element checkbox is toggled
def source_element_checkbutton_toggled():
    global source_element_selected_index, source_elements_checkbutton_widget_list, source_element_activated_variablelist
    for source_index3 in range( 0, len( sources_list["sources_list"] )):
        sources_list[ "sources_list" ][ source_index3 ][ "source_selected" ] = source_element_activated_variablelist[ source_index3 ].get()
    save_sources( sources_list )
    update_source_masterobject()
    return

# Function callback for source element label clicked by mouse
def source_element_label_widget_clicked( event ):
    global source_element_selected_index, source_elements_label_widget_list, source_elements_checkbutton_widget_list
    for source_index2 in range( 0, len( sources_list["sources_list"] )):
        if source_elements_label_widget_list[ source_index2 ] == event.widget:
            source_elements_label_widget_list[ source_index2 ].config( background = "blue", foreground = "white" )
            source_elements_checkbutton_widget_list[ source_index2 ].config( background = "blue", activebackground = "blue", highlightbackground = "blue" )
            source_element_selected_index = source_index2
        else:
            source_elements_label_widget_list[ source_index2 ].config( background = "white", foreground = "black" )
            source_elements_checkbutton_widget_list[ source_index2 ].config( background = "white", activebackground = "white", highlightbackground = "white" )

def source_info_element_content_frame_configure( canvas, window, scrollbar ):
    canvas.configure( scrollregion = canvas.bbox("all") )
    canvas.itemconfig( window, width = canvas.winfo_width() - scrollbar.winfo_width() - 10 )

update_sources_masterobject_window = None
update_sources_masterobject_window_label = None
update_source_masterobject_worker_thread_return_value = True

def update_source_masterobject_worker_thread():
    global source_master_object, update_source_masterobject_worker_thread_return_value

    source_master_object.clear()

    activated_sources_json_data = []
    for source in sources_list[ "sources_list" ]:
        if source[ "source_selected" ] == 1:
            # Add this source's JSON contents to activated_sources_json_data
            openedFile = {}
            fileText = ""
            if os.path.isfile(os.path.dirname(os.path.realpath(__file__)) + "/sources/" + source[ "source_name" ] + ".json"):
                openedFile = open("sources/" + source[ "source_name" ] + ".json", "r")
                fileText = openedFile.read()
                openedFile.close()
                # Now try to JSON decode our read file text
                try:
                    activated_sources_json_data.append(json.loads(fileText))
                except ValueError:
                    tkinter.messagebox.showerror("JSON Decode Error", "Couldn't decode JSON from source file \"sources/" + source[ "source_name" ] + ".json\". Unable to properly build master object.")
                    update_source_masterobject_worker_thread_return_value = False
                # JSON loaded successfully
            else:
                tkinter.messagebox.showerror("File Load Error", "Couldn't load source file \"sources/" + source[ "source_name" ] + ".json\". Unable to properly build master object.")
                update_source_masterobject_worker_thread_return_value = False
    # All source data to be used is now loaded into the list activated_sources_json_data

    # Now assemble each separate source file into one masterobject
    for activated_source in activated_sources_json_data:
        for word in activated_source[ "top_word_list" ]:
            if word in source_master_object:
                # Word already exists in source_master_object
                # Add this word's total_frequency to master object
                source_master_object[ word ][ "total_frequency" ] += activated_source[ "top_word_list" ][ word ][ "total_frequency" ]
                # Merge the subsequent_words from this with master object's
                for subsequent_word_index in range( 0, len( activated_source[ "top_word_list" ][ word ][ "subsequent_words" ] ) ):
                    subseq_exists_in_master = False
                    for mastersource_subsequent_word_index in range( 0, len( source_master_object[ word ][ "subsequent_words" ] ) ):
                        # Check if subsequent word already exists in master object
                        if activated_source[ "top_word_list" ][ word ][ "subsequent_words" ][ subsequent_word_index ][ "word_name" ] == \
                            source_master_object[ word ][ "subsequent_words" ][ mastersource_subsequent_word_index ][ "word_name" ]:
                            # Already exists in master object, so just frequency to master
                            source_master_object[ word ][ "subsequent_words" ][ mastersource_subsequent_word_index ][ "subseq_frequency" ] += \
                                activated_source[ "top_word_list" ][ word ][ "subsequent_words" ][ subsequent_word_index ][ "subseq_frequency" ]
                            subseq_exists_in_master = True
                    if subseq_exists_in_master == False:
                        # Is new subsequent word, so just copy contents of current one to master
                        source_master_object[ word ][ "subsequent_words" ].append( activated_source[ "top_word_list" ][ word ][ "subsequent_words" ][ subsequent_word_index ] )
            else:
                # New word not in master object
                # Create new entry and copy over the contents from this source
                source_master_object[ word ] = activated_source[ "top_word_list" ][ word ]
    if update_sources_masterobject_window != None:
        update_sources_masterobject_window.destroy()
    update_source_masterobject_worker_thread_return_value = True
    update_suggestions()
    root.focus_force()
    return

def update_source_masterobject():
    global source_master_object, update_sources_masterobject_window, \
    update_sources_masterobject_window_label, update_source_masterobject_worker_thread_return_value

    update_source_masterobject_worker_thread_return_value = True

    update_sources_masterobject_window = Toplevel()
    update_sources_masterobject_window.title("Updating Compound Sourcefile Data")
    update_sources_masterobject_window.resizable(width = FALSE, height = FALSE)
    update_sources_masterobject_window.config(background = "black")
    update_sources_masterobject_window.wm_attributes("-disabled", "1")
    update_sources_masterobject_window.geometry("300x50+" + str(int((win32api.GetMonitorInfo(win32api.EnumDisplayMonitors()[0][0])["Work"][2] / 2) \
        - (300 / 2))) + "+" + str(int((win32api.GetMonitorInfo(win32api.EnumDisplayMonitors()[0][0])["Work"][3] / 2) - (50 / 2))))

    update_sources_masterobject_window_label = Label(update_sources_masterobject_window, text = "Updating combined sourcefile data...\nPlease wait...", justify = CENTER, background = "black", foreground = "white")
    update_sources_masterobject_window_label.place(relx = 0.5, rely = 0.5, anchor = CENTER)

    update_sources_masterobject_window.wm_transient(master = root)
    update_sources_masterobject_window.protocol('WM_DELETE_WINDOW', None)
    update_sources_masterobject_window.focus_set()
    update_sources_masterobject_window.grab_set()

    worker_thread = threading.Thread( target = update_source_masterobject_worker_thread )
    worker_thread.daemon = True
    worker_thread.start()

    return update_source_masterobject_worker_thread_return_value

def sourceframe_background_clicked(event):
    global source_element_selected_index, source_elements_label_widget_list, source_elements_checkbutton_widget_list
    source_element_selected_index = None
    for source_index2 in range( 0, len( sources_list["sources_list"] )):
        source_elements_label_widget_list[ source_index2 ].config( background = "white", foreground = "black" )
        source_elements_checkbutton_widget_list[ source_index2 ].config( background = "white", activebackground = "white", highlightbackground = "white" )
    return

def update_sources():
    # Two major things that are supposed to happen here:
    # First, the sources info panel gets updated with source names
    # Second, the convergent source object that predictions come from is remade with currently activated sources
    # This function assumes that sources_list is updated and each name in that file will link to a source file

    global sources_list, sources_info_display_frame, source_element_activated_variablelist, \
        source_element_selected_index, source_elements_label_widget_list, source_elements_checkbutton_widget_list
    source_element_selected_index = None

    # Empty the variable lists

    del source_element_activated_variablelist[:]
    del source_elements_label_widget_list[:]
    del source_elements_checkbutton_widget_list[:]

    # Create the sources informational display frame for the sources view
    if sources_info_display_frame != None:
        if sources_info_display_frame.winfo_exists():
            sources_info_display_frame.destroy()

    sources_info_display_frame = Frame(master = sources_frame, background = "gray", borderwidth = 2, relief = FLAT)
    sources_info_display_frame.grid(row = 0, column = 0, sticky = N+S+E+W)
    sources_info_display_frame.grid_rowconfigure(0, weight = 1)
    sources_info_display_frame.grid_rowconfigure(1, weight = 9)
    sources_info_display_frame.grid_columnconfigure(0, weight = 4)
    sources_info_display_frame.grid_columnconfigure(1, weight = 1)

    # First, update the frame
    source_info_name_label = Label(sources_info_display_frame, text = "Source Name", font = ("Helvetica", 10), background = "gray", padx = 4, pady = 4, foreground = "white")
    source_info_name_label.grid(row = 0, column = 0, sticky = N+S+W)
    source_info_activated_label = Label(sources_info_display_frame, text = "Activated?", font = ("Helvetica", 10), background = "gray", anchor = W, padx = 4, pady = 4, foreground = "white")
    source_info_activated_label.grid(row = 0, column = 1, sticky = N+S+W)

    # Frame for actual source elements
    source_info_elements_frame = Frame(master = sources_info_display_frame, background = "white")
    source_info_elements_frame.grid(row = 1, column = 0, columnspan = 2, padx = 4, pady = 2, sticky = N+S+E+W)

    # Canvas element content frame container
    source_info_elements_canvas = Canvas(master = source_info_elements_frame, height = 85, borderwidth = 0, background = "white")
    source_info_elements_canvas.pack(side = LEFT, fill = BOTH, expand = TRUE)

    # Scrollbar for actual source elements
    source_info_elements_scrollbar = Scrollbar( master = source_info_elements_frame, orient = "vertical", command = source_info_elements_canvas.yview )
    source_info_elements_scrollbar.pack(side = RIGHT, fill = Y)
    source_info_elements_canvas.configure( yscrollcommand = source_info_elements_scrollbar.set )

    # Frame for actual element info content
    # Render with a white background if no elements currently exist so that a black dot doesn't appear in the container frame's top-left corner
    if len( sources_list["sources_list"] ) > 0:
        source_info_element_content_frame = Frame(master = source_info_elements_canvas, background = "black")
    else:
        source_info_element_content_frame = Frame(master = source_info_elements_canvas, background = "white")
    source_info_element_content_frame.grid_columnconfigure(0, weight = 5)
    source_info_element_content_frame.grid_columnconfigure(1, weight = 1)

    source_info_elements_canvas_window = source_info_elements_canvas.create_window( (0, 0), window = source_info_element_content_frame, anchor = NW )
    source_info_element_content_frame.bind( "<Configure>", lambda event, canvas = source_info_elements_canvas, \
        window = source_info_elements_canvas_window, scrollbar = source_info_elements_scrollbar: source_info_element_content_frame_configure( canvas, window, scrollbar ) )
    source_info_elements_canvas.bind( "<Button-1>", sourceframe_background_clicked )

    for source_index in range( 0, len( sources_list["sources_list"] )):
        # First, populate the info frame with each source

        source_elements_label_widget_list.insert( source_index,  Label(source_info_element_content_frame, text = sources_list["sources_list"][source_index]["source_name"], anchor = W, background = "white", foreground = "black"))
        source_elements_label_widget_list[ source_index ].grid(row = source_index, column = 0, padx = 1, pady = 1, sticky = N+S+E+W)
        source_elements_label_widget_list[ source_index ].bind( "<Button-1>", lambda event : source_element_label_widget_clicked( event ) )

        source_element_activated_variablelist.insert( source_index, IntVar() )

        source_elements_checkbutton_widget_list.insert( source_index, Checkbutton( source_info_element_content_frame, background = "white", \
            foreground = "black", highlightbackground = "white", activebackground = "white", \
            variable = source_element_activated_variablelist[source_index], anchor = CENTER, command = source_element_checkbutton_toggled ) )
        if sources_list["sources_list"][source_index]["source_selected"] == 1:
            source_elements_checkbutton_widget_list[ source_index ].select()
        else:
            source_elements_checkbutton_widget_list[ source_index ].deselect()
        source_elements_checkbutton_widget_list[ source_index ].grid(row = source_index, column = 1, padx = 1, pady = 1, sticky = N+S+E+W)

    update_source_masterobject()

    return

# Keylogging components
hook_manager = pyHook.HookManager()
hook_manager.SubscribeKeyDown(on_keyboard_down_event)
hook_manager.SubscribeKeyUp(on_keyboard_up_event)
# Attach hook_manager to the physical keyboard
hook_manager.HookKeyboard()

update_sources()
root.mainloop()
