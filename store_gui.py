import json, sys
import tkinter
import tkinter.filedialog
import tkinter.messagebox
import tkinter.ttk
from pathlib import Path

class App(tkinter.Tk):
    def __init__(self):
        super().__init__()

        self.title("STB MC3DS Unistore Tool")
        self.geometry('640x400')
        self.columnconfigure(0, weight=4)
        self.columnconfigure(2, weight=1)
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
        self.propertiesFrame = tkinter.Frame(self)
        self.propertiesFrame.grid(row=0, column=2, sticky="wnes")
        self.propertiesFrame.columnconfigure(1, weight=1)

        self.tree = tkinter.ttk.Treeview(self, show='tree', selectmode="browse")
        self.tree.bind('<<TreeviewSelect>>', self.itemSelected)
        self.scrollbar = tkinter.Scrollbar(self, orient=tkinter.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.grid(row=0, column=1, sticky="ns")
        self.tree.grid(row=0, column=0, sticky="wesn")

        self.loadContent("./stb-mc3ds.unistore")

        self.lastValue = None
        self.saved = True

    def loadContent(self, fp: str):
        filePath = Path(fp)
        with open(fp, "r", encoding="utf-8") as f:
            json_content = json.loads(f.read())

        if not ("storeInfo" in json_content):
            print("File does not contain 'storeInfo'")
            print("Creating template...")
            json_content["storeInfo"] = {}
            json_content["storeInfo"]["title"] = "dummyTitle"
            json_content["storeInfo"]["author"] = "dummy"
            json_content["storeInfo"]["description"] = "dummyDescription"
            json_content["storeInfo"]["file"] = filePath.name
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
        
        for key, element in enumerate(json_content["storeContent"]):
            self.tree.insert("", "end", text=element["info"]["title"], values=[key])

    def clearTreeview(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
    
    def itemSelected(self, event):
        for selected_item in self.tree.selection():
            item = self.tree.item(selected_item)
            record = item['values']

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