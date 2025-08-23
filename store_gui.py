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

class ScriptViewFrame(customtkinter.CTkFrame):
    def __init__(self, master, elementData: dict, elementName: str, **kwargs):
        super().__init__(master, **kwargs)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        self.elementData = elementData

        self.elementNameVar = customtkinter.StringVar(self, value=elementName)
        self.elementNameLabel = customtkinter.CTkEntry(self, textvariable=self.elementNameVar)
        self.elementNameLabel.grid(column=0, row=0, sticky="we")

        toggleViewBtn = customtkinter.CTkButton(self, text="Toggle View", width=100, fg_color="transparent", corner_radius=0)
        toggleViewBtn.grid(column=1, row=0)

class ScriptEditorWindow(tkinter.Toplevel):
    def __init__(self, master, storeData: StoreContent, key: int):
        super().__init__(master)
        self.geometry("450x400")
        self.resizable(False, False)
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
                scriptView.grid(column=0, row=i, sticky="we")
                i += 1

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
        self.master = master
        super().__init__(master, bg_color="transparent", corner_radius=0, **kwargs)
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

    def openEditWindow(self, event):
        self.btn.configure(fg_color="#1b4a80")
        self.label.configure(fg_color="#3B6594")
        EditEntryWindow(self, self.content, self.elementIdx).focus()
        pass

class StoreElementsFrame(customtkinter.CTkScrollableFrame):
    def __init__(self, master: App, content: StoreContent, **kwargs):
        self.master = master
        super().__init__(master, **kwargs)
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