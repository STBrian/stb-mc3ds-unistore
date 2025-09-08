from __future__ import annotations
import json, sys
import tkinter
import tkinter.filedialog
import tkinter.messagebox
import tkinter.ttk
from pathlib import Path
import customtkinter
from PIL import Image
from datetime import datetime, timezone, timedelta
from dateutil import parser
import pytz

UNISTORE_FILENAME = "./stb-mc3ds.unistore"
SPRITESHEET_FILENAME = "./assets/icons/spritesheet.t3s"
ICONS_DIR = Path(SPRITESHEET_FILENAME).parent

SPRITESHEET_CONTENT = []
with open(SPRITESHEET_FILENAME, "r") as f:
    SPRITESHEET_CONTENT = f.readlines()[2:]
for i, element in enumerate(SPRITESHEET_CONTENT):
    SPRITESHEET_CONTENT[i] = element[:-1] if element.endswith("\n") else element

tz_map = {
    "(CST)": timezone(timedelta(hours=-6)),
    "(CDT)": timezone(timedelta(hours=-5)),
    "(UTC)": timezone.utc
}

def parse_date(date_str: str):
    *dt_parts, tz_abbr = date_str.split()
    dt_str = " ".join(dt_parts)
    
    dt = datetime.strptime(dt_str, "%Y-%m-%d at %H:%M")

    if tz_abbr in tz_map:
        dt = dt.replace(tzinfo=tz_map[tz_abbr])
    else:
        raise ValueError(f"Unknown timezone: {tz_abbr}")
    return dt

def getCurrentUTCTime() -> str:
    utc = pytz.utc
    utc_time = datetime.now(utc)
    futc_time = str(utc_time).split(".")[0]
    futc_time = futc_time.split(" ")
    futc_time = f"{futc_time[0]} at {futc_time[1][:-3]} (UTC)"
    return futc_time

class ToolTip:
    def __init__(self, widget, text, delay=1000):
        self.widget = widget
        self.text = text
        self.delay = delay
        self.tip_window = None
        self.after_id = None

        widget.bind("<Enter>", self.schedule_show)
        widget.bind("<Leave>", self.hide)

    def schedule_show(self, event=None):
        self.after_id = self.widget.after(self.delay, self.show)

    def show(self):
        if self.tip_window or not self.text:
            return
        
        x, y, _, cy = self.widget.bbox("insert") or (0,0,0,0)
        x = x + self.widget.winfo_rootx() + 25

        y = y + cy + self.widget.winfo_rooty() + 25

        self.tip_window = tw = customtkinter.CTkToplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")

        label = customtkinter.CTkLabel(tw, text=self.text, corner_radius=0, fg_color="gray20", text_color="white")
        label.pack()
    
    def hide(self, event=None):
        if self.after_id:
            self.widget.after_cancel(self.after_id)
            self.after_id = None
            if self.tip_window:
                self.tip_window.destroy()
                self.tip_window = None

class ModalWindow(tkinter.Toplevel):
    def __init__(self, master, title, **kwargs):
        super().__init__(master, **kwargs)
        self.master = master
        self.value = None

        self.title(title)
        self.center(300, 150)
        self.resizable(False, False)

        self.transient(master)
        self.grab_set()
        self.focus_force()

        self.bind("<FocusOut>", lambda e: self.focus_force())
    
    def center(self, width: int, height: int):
        self.update_idletasks()
        
        twidth = self.winfo_screenwidth()
        theight = self.winfo_screenheight()

        x = (twidth // 2) - (width // 2)
        y = (theight // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

class StoreContent:
    def __init__(self, path: Path):
        with open(path, "r", encoding="utf-8") as f:
            json_content = json.loads(f.read())

        if not ("storeInfo" in json_content):
            print("File does not contain 'storeInfo'")
            print("Creating template...")
            json_content["storeInfo"] = {}
            json_content["storeInfo"]["title"] = "dummyTitle"
            json_content["storeInfo"]["author"] = "dummy"
            json_content["storeInfo"]["description"] = "dummyDescription"
            json_content["storeInfo"]["file"] = path.name
            json_content["storeInfo"]["url"] = "dummyUrl.com"
            json_content["storeInfo"]["sheet"] = "dummySheet.t3x"
            json_content["storeInfo"]["sheetURL"] = "dummySheetUrl.com"
            json_content["storeInfo"]["version"] = 3
            json_content["storeInfo"]["revision"] = 1
            print("Check later the file to replace info about unistore")
        if not ("storeContent" in json_content):
            json_content["storeContent"] = []
        else:
            if type(json_content["storeContent"]) != list:
                json_content["storeContent"] = []

        self.storeInfo: dict = json_content["storeInfo"]
        self.storeContent: list[dict] = json_content["storeContent"]

class SelectNewBlockTypeWindow(ModalWindow):
    def __init__(self, master, closeCommand=None):
        super().__init__(master, "Select block type")
        self.master = master
        self.closeCommand = closeCommand
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        mainframe = customtkinter.CTkFrame(self, corner_radius=0)
        mainframe.grid(column=0, row=0, sticky="wnes")

        btnTypes = ["downloadFile", "downloadRelease", "extractFile", "installCia",
                    "bootTitle", "mkdir", "rmdir", "move", "copy", "deleteFile",
                    "promptMessage", "skip", "exit"]
        for i, element in enumerate(btnTypes):
            btn = customtkinter.CTkButton(mainframe, text=element, width=150, command= lambda a=element : self.blockTypeSelection(a))
            btn.grid(column=i % 5, row=i//5, padx=(2, 0), pady=(2, 0))
        
        self.center(610, 92)

        if closeCommand != None:
            self.protocol("WM_DELETE_WINDOW", self.blockTypeSelection)

    def blockTypeSelection(self, type = None):
        self.value = type
        self.destroy()
        if self.closeCommand != None:
            self.closeCommand()

class ScriptViewFrame(customtkinter.CTkFrame):
    def __init__(self, master, elementData: dict, elementName: str, **kwargs):
        super().__init__(master, **kwargs)
        self.columnconfigure(0, weight=1)

        self.elementData = elementData

        self.lastElementName = elementName
        self.elementNameVar = customtkinter.StringVar(self, value=elementName)
        elementNameEntry = customtkinter.CTkEntry(self, textvariable=self.elementNameVar, border_width=0)
        elementNameEntry.grid(column=0, row=0, sticky="we")
        elementNameEntry.bind("<FocusOut>", self.checkNameAndUpdate)

        self.toggleViewBtn = tglBtn = customtkinter.CTkButton(self, text="↓", width=50, fg_color="transparent", corner_radius=0, command=self.toggleView)
        tglBtn.grid(column=1, row=0)
        ToolTip(tglBtn, "Toggle view")

        self.selectBlockWindow = None
        self.scriptBlocksFrame = None
        self.toggle = False
        self.blocks = []

    def checkNameAndUpdate(self, event=None):
        if self.lastElementName != self.elementNameVar.get():
            if self.elementNameVar.get() in self.elementData:
                suffix = 1
                while f"{self.elementNameVar.get()}({suffix})" in self.elementData:
                    suffix += 1
                self.elementNameVar.set(f"{self.elementNameVar.get()}({suffix})")
            self.elementData[self.elementNameVar.get()] = self.elementData[self.lastElementName]
            del self.elementData[self.lastElementName]
            self.lastElementName = self.elementNameVar.get()

    def createBlocksFrame(self):
        if self.scriptBlocksFrame == None:
            self.scriptBlocksFrame = customtkinter.CTkFrame(self)
            self.scriptBlocksFrame.columnconfigure(0, weight=1)
            self.scriptBlocksFrame.grid(column=0, row=1, columnspan=2, sticky="wnes", pady=(2, 0))

    def toggleView(self):
        self.checkNameAndUpdate()
        if self.toggle:
            self.toggleViewBtn.configure(text="↓")
            if self.scriptBlocksFrame != None:
                self.scriptBlocksFrame.destroy()
                self.scriptBlocksFrame = None
        else:
            self.toggleViewBtn.configure(text="↑")
            self.createBlocksFrame()
            self.loadBlocks()
        self.toggle = not self.toggle

    def reloadBlocks(self):
        if self.scriptBlocksFrame != None:
            self.scriptBlocksFrame.destroy()
            self.scriptBlocksFrame = None
            self.createBlocksFrame()
            self.loadBlocks()

    def loadBlocks(self):
        self.blocks.clear()
        if self.scriptBlocksFrame != None:
            for i in range(len(self.elementData[self.lastElementName])):
                addBlockBtn = customtkinter.CTkButton(self.scriptBlocksFrame, text="+", command=lambda a=i : self.addBlockCallback(a), width=20, height=10, corner_radius=360, fg_color="transparent", border_width=0)
                addBlockBtn.grid(column=1, row=i*2)
                ToolTip(addBlockBtn, "Add block")
                block = ScriptBlock(self.scriptBlocksFrame, self.elementData[self.lastElementName], i, self.reloadBlocks)
                block.grid(column=0, row=i*2+1, sticky="wnes", padx=(10, 0))
                self.blocks.append(block)
            i = len(self.elementData[self.lastElementName])
            addBlockBtn = customtkinter.CTkButton(self.scriptBlocksFrame, text="+", command=lambda a=i : self.addBlockCallback(a), width=20, height=10, corner_radius=10, fg_color="transparent", border_width=0)
            addBlockBtn.grid(column=1, row=i*2)
            ToolTip(addBlockBtn, "Add block")

    def addBlockCallback(self, idx: int):
        if self.selectBlockWindow == None:
            self.selectBlockWindow = SelectNewBlockTypeWindow(self, lambda a=idx : self.selectBlockTypeWindowCloseCallback(a))

    def selectBlockTypeWindowCloseCallback(self, idx: int):
        if self.selectBlockWindow != None:
            if self.selectBlockWindow.value != None:
                self.addBlockSelected(self.selectBlockWindow.value, idx)
            self.selectBlockWindow = None

    def addBlockSelected(self, type: str, idx: int):
        newBlock = {"type": type}
        match type:
            case "downloadFile":
                newBlock["file"] = ""
                newBlock["output"] = ""
            case "downloadRelease":
                newBlock["repo"] = ""
                newBlock["file"] = ""
                newBlock["output"] = ""
                newBlock["includePrereleases"] = False # type: ignore
            case "extractFile":
                newBlock["file"] = ""
                newBlock["input"] = ""
                newBlock["output"] = ""
            case "installCia":
                newBlock["file"] = ""
            case "bootTitle":
                newBlock["TitleID"] = ""
                newBlock["NAND"] = False # type: ignore
            case "mkdir":
                newBlock["directory"] = ""
            case "rmdir":
                newBlock["directory"] = ""
                newBlock["required"] = False # type: ignore
            case "move":
                newBlock["old"] = ""
                newBlock["new"] = ""
            case "copy":
                newBlock["source"] = ""
                newBlock["destination"] = ""
            case "deleteFile":
                newBlock["file"] = ""
            case "promptMessage":
                newBlock["message"] = ""
                newBlock["count"] = ""
            case "skip":
                newBlock["count"] = ""
            case "exit":
                pass
            case _:
                raise ValueError(f"Invalid block type {type}")
        self.elementData[self.lastElementName].insert(idx, newBlock)
        self.reloadBlocks()

class ScriptBlock(customtkinter.CTkFrame):
    def __init__(self, master, blocksList: list, key: int, deleteCommand = None, **kwargs):
        super().__init__(master, corner_radius=0, **kwargs)
        self.columnconfigure(1, weight=1)
        self.blocksList = blocksList
        self.key = key
        self.blockData = blockData = blocksList[key]
        self.deleteCommand = deleteCommand

        self.type = type = self.blockData["type"]

        blockLabel = customtkinter.CTkLabel(self, width=100, text=type, fg_color="transparent", anchor="w")
        blockLabel.grid(column=0, row=0, sticky="w", padx=10)

        blockDeleteBtn = customtkinter.CTkButton(self, text="x", command=self.deleteBlock, width=20, height=10, fg_color="transparent", corner_radius=0)
        blockDeleteBtn.grid(column=2, row=0)
        ToolTip(blockDeleteBtn, "Delete block")

        if type == "downloadFile":
            self.stringVar1 = customtkinter.StringVar(self, blockData["file"])
            self.stringVar2 = customtkinter.StringVar(self, blockData["output"])
            self.newStringEntry("file", self.stringVar1, 1)
            self.newStringEntry("output", self.stringVar2, 2)
        elif type == "downloadRelease":
            self.stringVar1 = customtkinter.StringVar(self, blockData["repo"])
            self.stringVar2 = customtkinter.StringVar(self, blockData["file"])
            self.stringVar3 = customtkinter.StringVar(self, blockData["output"])
            self.booleanVar1 = customtkinter.BooleanVar(self, blockData["includePrereleases"])
            self.newStringEntry("repo", self.stringVar1, 1)
            self.newStringEntry("file", self.stringVar2, 2)
            self.newStringEntry("output", self.stringVar3, 3)
            self.newBooleanCheckbox("includePrereleases", self.booleanVar1, 4)
        elif type == "extractFile":
            self.stringVar1 = customtkinter.StringVar(self, blockData["file"])
            self.stringVar2 = customtkinter.StringVar(self, blockData["input"])
            self.stringVar3 = customtkinter.StringVar(self, blockData["output"])
            self.newStringEntry("file", self.stringVar1, 1)
            self.newStringEntry("input", self.stringVar2, 2)
            self.newStringEntry("output", self.stringVar3, 3)
        elif type == "installCia":
            self.stringVar1 = customtkinter.StringVar(self, blockData["file"])
            self.newStringEntry("file", self.stringVar1, 1)
        elif type == "bootTitle":
            self.stringVar1 = customtkinter.StringVar(self, blockData["TitleID"])
            self.booleanVar1 = customtkinter.StringVar(self, blockData["NAND"])
            self.newStringEntry("TitleID", self.stringVar1, 1)
            self.newBooleanCheckbox("NAND", self.booleanVar1, 2)
        elif type == "mkdir":
            self.stringVar1 = customtkinter.StringVar(self, blockData["directory"])
            self.newStringEntry("directory", self.stringVar1, 1)
        elif type == "rmdir":
            self.stringVar1 = customtkinter.StringVar(self, blockData["directory"])
            self.booleanVar1 = customtkinter.BooleanVar(self, blockData["required"])
            self.newStringEntry("directory", self.stringVar1, 1)
            self.newBooleanCheckbox("required", self.booleanVar1, 2)
        elif type == "move":
            self.stringVar1 = customtkinter.StringVar(self, blockData["old"])
            self.stringVar2 = customtkinter.StringVar(self, blockData["new"])
            self.newStringEntry("old", self.stringVar1, 1)
            self.newStringEntry("new", self.stringVar2, 2)
        elif type == "copy":
            self.stringVar1 = customtkinter.StringVar(self, blockData["source"])
            self.stringVar2 = customtkinter.StringVar(self, blockData["destination"])
            self.newStringEntry("source", self.stringVar1, 1)
            self.newStringEntry("destination", self.stringVar2, 2)
        elif type == "deleteFile":
            self.stringVar1 = customtkinter.StringVar(self, blockData["file"])
            self.newStringEntry("file", self.stringVar1, 1)
        elif type == "promptMessage":
            self.stringVar1 = customtkinter.StringVar(self, blockData["message"])
            self.stringVar2 = customtkinter.StringVar(self, blockData["count"])
            self.newStringEntry("message", self.stringVar1, 1)
            self.newStringEntry("count", self.stringVar2, 2)
        elif type == "skip":
            self.stringVar1 = customtkinter.StringVar(self, blockData["count"])
            self.newStringEntry("count", self.stringVar1, 1)
        elif type == "exit":
            pass
        else:
            raise ValueError(f"Invalid block type {type}")
    
    def newStringEntry(self, name, var, r):
        self.newLabel(name, 0, r)
        self.newEntry(var, 1, r)

    def newBooleanCheckbox(self, name, var, r):
        self.newLabel(name, 0, r)
        self.newCheckbox(var, 1, r)

    def newLabel(self, name, c: int, r: int):
        lbl = customtkinter.CTkLabel(self, text=name, width=50, compound="left", anchor="w")
        lbl.grid(column=c, row=r, padx=10, pady=(0, 5), sticky="w")

    def newEntry(self, var, c: int, r: int):
        entry = customtkinter.CTkEntry(self, textvariable=var, border_width=0, corner_radius=0)
        entry.grid(column=c, row=r, sticky="we", padx=(0, 5), pady=(0, 5), columnspan=2)

    def newCheckbox(self, var, c: int, r: int):
        cb = customtkinter.CTkCheckBox(self, text="", variable=var, border_width=1)
        cb.grid(column=c, row=r, sticky="w", pady=(0, 5))

    def deleteBlock(self):
        self.blocksList.pop(self.key)
        if self.deleteCommand != None:
            self.deleteCommand()

class ScriptEditorWindow(tkinter.Toplevel):
    def __init__(self, master, storeData: StoreContent, key: int):
        super().__init__(master)
        self.geometry("600x400")
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        self.storeData = storeData
        self.elementKey = key

        self.mainframe = customtkinter.CTkScrollableFrame(self, corner_radius=0)
        self.mainframe.grid(column=0, row=0, sticky="wnes", padx=0, ipadx=0)
        self.mainframe.columnconfigure(0, weight=1)

        i = 0
        for name, value in storeData.storeContent[key].items():
            if name != "info":
                scriptView = ScriptViewFrame(self.mainframe, storeData.storeContent[key], name)
                scriptView.grid(column=0, row=i, sticky="we", padx=10, pady=(5, 0))
                i += 1
        
        self.bindid = self.bind("<Button-1>", self.on_click, add="+")
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def on_close(self):
        self.unbind("<Button-1>", self.bindid)
        self.destroy()

    def on_click(self, event):
        widget = event.widget
        #print(type(widget))
        if not isinstance(widget, tkinter.Entry):
            self.focus_set()

class EditEntryWindow(tkinter.Toplevel):
    def __init__(self, master, storeData: StoreContent, key: int):
        super().__init__(master)
        self.geometry("450x500")
        self.resizable(False, False)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        self.storeData = storeData
        self.elementIdx = key

        element = storeData.storeContent[key]

        frame = customtkinter.CTkFrame(self, corner_radius=0)
        frame.grid(column=0, row=0, sticky="wnes", padx=0, ipadx=0)
        frame.columnconfigure(1, weight=1)

        row_i = 0
        field = "Title"
        nameLabel = customtkinter.CTkLabel(frame, text=f"{field}: ")
        nameLabel.grid(column=0, row=row_i, sticky="w", pady=(5,0))
        self.nameVar = customtkinter.StringVar(value=element["info"][field.lower()])
        nameEntry = customtkinter.CTkEntry(frame, textvariable=self.nameVar, width=60, border_width=0)
        nameEntry.grid(column=1, row=row_i, sticky="we", pady=(5,0))

        row_i += 1
        field = "Author"
        authorLabel = customtkinter.CTkLabel(frame, text=f"{field}: ")
        authorLabel.grid(column=0, row=row_i, sticky="w", pady=5)
        self.authorVar = customtkinter.StringVar(value=element["info"][field.lower()])
        authorEntry = customtkinter.CTkEntry(frame, textvariable=self.authorVar, width=60, border_width=0)
        authorEntry.grid(column=1, row=row_i, sticky="we", pady=5)

        row_i += 1
        field = "Version"
        versionLabel = customtkinter.CTkLabel(frame, text=f"{field}: ")
        versionLabel.grid(column=0, row=row_i, sticky="w")
        self.versionVar = customtkinter.StringVar(value=element["info"][field.lower()])
        versionEntry = customtkinter.CTkEntry(frame, textvariable=self.versionVar, width=60, border_width=0)
        versionEntry.grid(column=1, row=row_i, sticky="we")

        row_i += 1
        field = "Description"
        descLabel = customtkinter.CTkLabel(frame, text=f"{field}: ")
        descLabel.grid(column=0, row=row_i, sticky="w", pady=5)
        self.descVar = customtkinter.StringVar(value=element["info"][field.lower()])
        descEntry = customtkinter.CTkEntry(frame, textvariable=self.descVar, width=60, border_width=0)
        descEntry.grid(column=1, row=row_i, sticky="we", pady=5)

        row_i += 1
        field = "License"
        licenseLabel = customtkinter.CTkLabel(frame, text=f"{field}: ")
        licenseLabel.grid(column=0, row=row_i, sticky="w")
        self.licenseVar = customtkinter.StringVar(value=element["info"][field.lower()])
        licenseEntry = customtkinter.CTkEntry(frame, textvariable=self.licenseVar, width=60, border_width=0)
        licenseEntry.grid(column=1, row=row_i, sticky="we")

        row_i += 1
        field = "Scripts"
        scriptsLabel = customtkinter.CTkLabel(frame, text=f"{field}: ")
        scriptsLabel.grid(column=0, row=row_i, sticky="w", pady=5)
        self.openScriptEditViewBtn = customtkinter.CTkButton(frame, text="Open Script View", command=self.openScriptEditView)
        self.openScriptEditViewBtn.grid(column=1, row=row_i, sticky="we", pady=5)

        row_i += 1
        frame.rowconfigure(row_i, weight=row_i)
        releaseNotesLabel = customtkinter.CTkLabel(frame, text="Release notes: ")
        releaseNotesLabel.grid(column=0, row=row_i, sticky="w")
        self.releaseNotesEntry = customtkinter.CTkTextbox(frame, width=45, height=15)
        self.releaseNotesEntry.insert(tkinter.END, element["info"]["releasenotes"])
        self.releaseNotesEntry.grid(column=1, row=row_i, sticky="wnes")

        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def on_close(self):
        print("Saving changes")
        self.destroy()

    def openScriptEditView(self):
        ScriptEditorWindow(self, self.storeData, self.elementIdx).focus()

class StoreElementButton(customtkinter.CTkFrame):
    def __init__(self, master: StoreElementsFrame, content: StoreContent, elementIdx: int, **kwargs):
        super().__init__(master, bg_color="transparent", corner_radius=0, **kwargs)
        self.master = master
        btnTitle = content.storeContent[elementIdx]["info"]["title"]
        maxLen = 30 if len(btnTitle) > 30 else len(btnTitle)
        btnImage = Image.open(ICONS_DIR.joinpath(SPRITESHEET_CONTENT[content.storeContent[elementIdx]["info"]["icon_index"]]))
        #btnIcon = ImageTk.PhotoImage(btnImage)
        btnIcon = customtkinter.CTkImage(btnImage, size=(80, 80))

        self.btn = customtkinter.CTkButton(self, height=100, text="", fg_color="transparent", image=btnIcon, corner_radius=0, border_spacing=0, border_width=0, hover=False)
        self.label = customtkinter.CTkLabel(self, height=50, text=btnTitle[:maxLen], wraplength=80)
        self.btn.bind("<Double-Button-1>", self.openEditWindow)
        self.btn.bind("<Enter>", self.on_enter)
        self.btn.bind("<Leave>", self.on_leave)
        self.btn.grid(column=0, row=0, sticky="wnes", padx=0, ipadx=0, pady=0, ipady=0)
        self.label.bind("<Double-Button-1>", self.openEditWindow)
        self.label.bind("<Enter>", self.on_enter)
        self.label.bind("<Leave>", self.on_leave)
        self.label.grid(column=0, row=1, sticky="wnes", padx=0, ipadx=0, pady=0, ipady=0)

        self.content = content
        self.elementIdx = elementIdx

    def on_enter(self, event):
        self.btn.configure(fg_color="#14375e")
        self.label.configure(fg_color="#325882")

    def on_leave(self, event):
        self.btn.configure(fg_color="transparent")
        self.label.configure(fg_color="transparent")

    def openEditWindow(self, event=None):
        self.btn.configure(fg_color="#1b4a80")
        self.label.configure(fg_color="#3B6594")
        EditEntryWindow(None, self.content, self.elementIdx).focus()
        pass

class StoreElementsFrame(customtkinter.CTkScrollableFrame):
    def __init__(self, master: App, content: StoreContent, **kwargs):
        super().__init__(master, **kwargs)
        self.master = master
        self.content = content
        self.columnconfigure((0, 1, 2, 3), weight=1)

        if len(content.storeContent) > 1:
            for i in range(len(content.storeContent) - 1):
                date1 = parse_date(content.storeContent[i]["info"]["last_updated"])
                for j in range(i + 1, len(content.storeContent)):
                    date2 = parse_date(content.storeContent[j]["info"]["last_updated"])
                    if date1 <= date2:
                        date1 = date2
                        aux = content.storeContent[i]
                        content.storeContent[i] = content.storeContent[j]
                        content.storeContent[j] = aux

        for i in range(len(content.storeContent)):
            self.rowconfigure((i // 4), weight=1)
            elementButton = StoreElementButton(self, content, i)
            elementButton.grid(column=(i % 4), row=(i // 4), sticky="wnes", padx=0, ipadx=0, pady=0, ipady=0)

class App(tkinter.Tk):
    def __init__(self):
        super().__init__()

        self.title("Unistore Tool")
        self.geometry('640x400')
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        # -------------------------------
        menubar = tkinter.Menu(self)
        self.config(menu=menubar)

        file_menu = tkinter.Menu(menubar, tearoff=False)
        file_menu.add_command(label="Save", command=self.saveChanges)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.closeApp)

        menubar.add_cascade(label="File", menu=file_menu, underline=0)
        # -------------------------------

        self.unistoreData = StoreContent(Path(UNISTORE_FILENAME))
        self.elementsContainer = StoreElementsFrame(self, self.unistoreData, corner_radius=0)
        self.elementsContainer.grid(column=0, row=0, sticky="wnes")

        self.editEntry = None
        self.lastValue = None
        self.saved = True

    def loadContent(self, fp: Path):
        self.unistoreData = StoreContent(fp)
        sortedElements = []
        indexes = []
        for key, element in enumerate(self.unistoreData.storeContent):
            if len(sortedElements) == 0:
                sortedElements.append(element)
                indexes.append(key)
            else:
                i = 0
                while i < len(sortedElements) and sortedElements[i]["info"]["title"] < element["info"]["title"]:
                    i += 1
                sortedElements.insert(i, element)
                indexes.insert(i, key)

    def saveChanges(self):
        pass

    def closeApp(self, val=None):
        if self.askForChanges():
            sys.exit()
        else:
            pass

    def askForChanges(self):
        if self.saved:
            return True
        else:
            print("Not saved")
            op = tkinter.messagebox.askyesnocancel(title="Unsaved changes", message="There are unsaved changes. Would you like to save them?")
            if op == True:
                self.saveChanges()
                return True
            elif op == False:
                return True
            else:
                return False
            
if __name__ == "__main__":
    app = App()

    app.bind('<Alt-F4>', app.closeApp)
    app.protocol("WM_DELETE_WINDOW", app.closeApp)

    app.mainloop()