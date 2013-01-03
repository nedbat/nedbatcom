"""
Jot
Ned Batchelder, 3/21/2003
http://www.nedbatchelder.com

Elements are added to an XML file based on a dialog launched from the system tray.
"""

# -- Global configuration -----

# The path to the XML file.
jotfile = 'c:/temp/quick.qx'

# The name of the root element in the XML file.
rootname = 'quickentries'

# The name of each entry in the XML file.
entryname = 'entry'

# A list of dicts defining the attributes for the entries.
attrs = [
    { 'name': 'titleword', 'label': 'Title word:', 'default': 'word',
      'helptext': "A word that will become part of the blog entry title"
      },
    { 'name': 'href', 'label': 'URL:', 'default': 'http://',
      'helptext': "The URL for the entry"
      },
    { 'name': 'text', 'label': 'Link text:', 'default': 'text',
      'helptext': "The text for the link"
      },
    { 'name': 'comment', 'label': 'Comment:', 'default': '',
      'helptext': "Additional commentary for the entry"
      },
]

# -- end configuration -----

from wxPython.wx import *
from wxPython.help import *
from xml.dom.minidom import Document, parse
import path         # http://www.jorendorff.com/articles/python/path
import sys, traceback

# assign ids for the dialog to use.
for a in attrs:
    a['id'] = wxNewId()
    
class JotDialog(wxDialog):
    def __init__(self, dataobj, parent, ID, title,
                 pos=wxDefaultPosition, size=wxDefaultSize,
                 style=wxDEFAULT_DIALOG_STYLE|wxRESIZE_BORDER):

        # Instead of calling wxDialog.__init__ we precreate the dialog
        # so we can set an extra style that must be set before
        # creation, and then we create the GUI dialog using the Create
        # method.
        pre = wxPreDialog()
        pre.SetExtraStyle(wxDIALOG_EX_CONTEXTHELP)
        pre.Create(parent, ID, title, pos, size, style)
        
        # This next step is the most important, it turns this Python
        # object into the real wrapper of the dialog (instead of pre)
        # as far as the wxPython extension is concerned.
        self.this = pre.this

        self.initGui()
        self.dataobj = dataobj        
        self.loadData()

    def initGui(self):
        # Now continue with the normal construction of the dialog
        # contents
        sizer = wxBoxSizer(wxVERTICAL)
        border = 2
        staticArgs = { 'style': wxALIGN_RIGHT, 'size': (60, -1) }
        editArgs = { 'style': wxALIGN_LEFT|wxSIMPLE_BORDER, 'size': (300, -1) }
        
        label = wxStaticText(self, -1, "Jot a quick entry.")
        sizer.Add(label, 0, wxALIGN_CENTRE|wxALL, border)

        for a in attrs:
            box = wxBoxSizer(wxHORIZONTAL)
            label = wxStaticText(self, -1, a['label'], **staticArgs)
            box.Add(label, 0, wxALIGN_CENTER|wxALL, border)

            text = wxTextCtrl(self, a['id'], "", **editArgs)
            text.SetHelpText(a['helptext'])
            box.Add(text, 1, wxALIGN_CENTER|wxALL, border)

            sizer.AddSizer(box, 0, wxGROW|wxALIGN_CENTER_VERTICAL|wxALL, border)

        line = wxStaticLine(self, -1, size=(20,-1), style=wxLI_HORIZONTAL)
        sizer.Add(line, 0, wxGROW|wxALIGN_CENTER_VERTICAL|wxRIGHT|wxTOP, border)

        box = wxBoxSizer(wxHORIZONTAL)

        if wxPlatform != "__WXMSW__":
            btn = wxContextHelpButton(self)
            box.Add(btn, 0, wxALIGN_CENTER|wxALL, border)

        btn = wxButton(self, wxID_OK, "OK")
        btn.SetDefault()
        btn.SetHelpText("The OK button completes the dialog")
        box.Add(btn, 0, wxALIGN_CENTER|wxALL, border)
        EVT_BUTTON(btn, wxID_OK, self.onOkbtnButton)

        btn = wxButton(self, wxID_CANCEL, "Cancel")
        btn.SetHelpText("The Cancel button cancels the dialog.")
        box.Add(btn, 0, wxALIGN_CENTER|wxALL, border)

        sizer.AddSizer(box, 0, wxALIGN_CENTER_VERTICAL|wxALIGN_CENTER|wxALL, border)

        self.SetSizer(sizer)
        self.SetAutoLayout(True)
        sizer.Fit(self)

    def onOkbtnButton(self, event):
        self.saveData()
        self.EndModal(wxID_OK)
        
    def loadData(self):
        for a in attrs:
            self.FindWindowById(a['id']).SetTitle(getattr(self.dataobj, a['name'], ''))

    def saveData(self):            
        for a in attrs:
            setattr(self.dataobj, a['name'], self.FindWindowById(a['id']).GetTitle())

class JotFrame(wxFrame):
    def __init__(self, jotapp, parent, id, title):
        wxFrame.__init__(self, parent, -1, title, size = (800, 600),
                         style=wxDEFAULT_FRAME_STYLE|wxNO_FULL_REPAINT_ON_RESIZE)

        self.jotapp = jotapp
        icon = wxIcon('jot.ico', wxBITMAP_TYPE_ICO)
        self.SetIcon(icon)
        
        if wxPlatform == '__WXMSW__':
            # setup a taskbar icon, and catch some events from it
            self.tbicon = wxTaskBarIcon()
            self.tbicon.SetIcon(icon, "Jot")
            EVT_TASKBAR_LEFT_DCLICK(self.tbicon, self.OnTaskBarActivate)
            EVT_TASKBAR_RIGHT_UP(self.tbicon, self.OnTaskBarMenu)
            EVT_MENU(self.tbicon, self.idMenuNewEntry, self.OnTaskBarActivate)
            EVT_MENU(self.tbicon, self.idMenuClose, self.OnTaskBarClose)
        EVT_ICONIZE(self, self.OnIconify)
        return

    def OnIconify(self, evt):
        self.Hide()
        return

    def OnTaskBarActivate(self, evt):
        self.jotapp.onNewEntry()
        return

    def OnCloseWindow(self, event):
        if hasattr(self, "tbicon"):
            del self.tbicon
        self.Destroy()

    idMenuNewEntry = wxNewId()
    idMenuClose = wxNewId()

    def OnTaskBarMenu(self, evt):
        menu = wxMenu()
        menu.Append(self.idMenuNewEntry, "Jot an entry")
        menu.Append(self.idMenuClose, "Close")
        self.tbicon.PopupMenu(menu)
        menu.Destroy()

    def OnTaskBarClose(self, evt):
        self.Close()

        # because of the way wxTaskBarIcon.PopupMenu is implemented we have to
        # prod the main idle handler a bit to get the window to actually close
        wxGetApp().ProcessIdle()

class QuickEntry:
    pass

class JotApp(wxApp):
    def OnInit(self):
        frame = JotFrame(self, None, -1, "Jot")
        return True

    def onNewEntry(self):
        qentry = QuickEntry()
        for a in attrs:
            setattr(qentry, a['name'], a['default'])

        dlg = JotDialog(qentry, None, -1, "Jot")
        dlg.CenterOnScreen()
        try:
            val = dlg.ShowModal()
        finally:
            dlg.Destroy()
        if val == wxID_OK:
            self.writeEntry(qentry)
           
        return True

    def writeEntry(self, qentry):
        qxPath = path.path(jotfile)
        if qxPath.exists():
            qxDoc = parse(jotfile)
        else:
            qxDoc = Document()
            qxDoc.appendChild(qxDoc.createElement(rootname))

        newElt = qxDoc.createElement(entryname)
        for a in attrs:
            newElt.setAttribute(a['name'], getattr(qentry, a['name']))
                                
        qxDoc.documentElement.appendChild(newElt)

        open(jotfile, 'w').write(qxDoc.toxml())

if __name__ == '__main__':
    try:
        app = JotApp()
        app.MainLoop()
    except:
        wxMessageBox(''.join(traceback.format_exception(*sys.exc_info())))
