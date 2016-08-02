import wx
import wx.grid
import sqlite3

def gridData():
    return {'category': (('CategoryId', 'Name', 'ParentId'),
                           'select * from category',
                           'insert into category values (?, ?, ?)',
                           'update category set Name=?, ParentId=? where CategoryId=?',
                           'delete from category where CategoryId=?')
              }
class MyFrame(wx.Frame):
    def __init__(self, parent):
        self.title = "Piggy Bank"
        wx.Frame.__init__(self, parent, -1, self.title, size=(800,600))
        self.initStatusBar()
        self.createMenuBar()
        self.createToolBar()
        self.createGrid()
        
    
    def initStatusBar(self):
        self.statusbar = self.CreateStatusBar()
        self.statusbar.SetFieldsCount(3)
        self.statusbar.SetStatusWidths([-1, -2, -3])
        

    def menuData(self):
        return [("&File", (
                ("&New", "New Sketch file", self.OnEvent),
                ("&Open", "Open sketch file", self.OnEvent),
                ("&Save", "Save sketch file", self.OnEvent),
                ("", "", ""),
                ("&Color", (
                    ("&Black", "", self.OnEvent,
                             wx.ITEM_RADIO),
                    ("&Red", "", self.OnEvent,
                             wx.ITEM_RADIO),
                    ("&Green", "", self.OnEvent,
                             wx.ITEM_RADIO),
                    ("&Blue", "", self.OnEvent,
                             wx.ITEM_RADIO),
                    ("&Other...", "", self.OnEvent,
                             wx.ITEM_RADIO))),
                ("", "", ""),
                ("&Quit", "Quit", self.OnCloseWindow))),
                ("&About", (
                ("&Info", "About app", self.OnAbout),
                #("Splash", "Splash window", self.OnSplash)
                ))
                ]
    
    def OnEvent(self, event): pass
    
    def createMenuBar(self):
        menuBar = wx.MenuBar()
        for eachMenuData in self.menuData():
            menuLabel = eachMenuData[0]
            menuItems = eachMenuData[1]
            menuBar.Append(self.createMenu(menuItems), menuLabel)
        self.SetMenuBar(menuBar)
        
    def createMenu(self, menuData):
        menu = wx.Menu()                                                                        
        for eachItem in menuData:                                                               
            if len(eachItem) == 2:                                        # (3) Создание подменю
                label = eachItem[0]
                subMenu = self.createMenu(eachItem[1])
                menu.Append(wx.NewId(), label, subMenu)
            else:
                self.createMenuItem(menu, *eachItem)
        return menu
    
    def createMenuItem(self, menu, label, status, handler, kind=wx.ITEM_NORMAL):
        if not label:
            menu.AppendSeparator()
            return
        menuItem = menu.Append(-1, label, status, kind)                     # (4) Создание элементов меню с типом
        self.Bind(wx.EVT_MENU, handler, menuItem)
        
     
    def OnCloseWindow(self, event):
        self.Destroy()
    
    def createToolBar(self):                                  # (1) Создание панели инструментов
        toolbar = self.CreateToolBar()
        for each in self.toolbarData():
            self.createSimpleTool(toolbar, *each)
        #toolbar.AddSeparator()
        #for each in self.toolbarColorData():
        #    self.createColorTool(toolbar, each)
        toolbar.Realize()
        
    def createSimpleTool(self, toolbar, label, filename, helpStr, handler):    # (3) Создание простых инструментов 
        if not label:
            toolbar.AddSeparator()                                        
            return
                                                             
        bmp = wx.Bitmap(filename, wx.BITMAP_TYPE_PNG)
        toolbar.SetToolBitmapSize((16,15))
        tool = toolbar.AddTool(-1,  label, bmp, helpStr)
        self.Bind(wx.EVT_MENU, handler, tool)
    
    def toolbarData(self):
        return (("Payment", "moneyminus.png", "Add payment",
                     self.OnEvent),
                ("", "", "", ""),
                ("Profit", "moneyplus.png", "Add profit",
                     self.OnEvent),
                ("Planning", "plan.png", "Planning",
                     self.OnEvent))
                                                  
                                                  
    def createColorTool(self, toolbar, color):                # (4) Создание инструментов выбора цвета
        bmp = self.MakeBitmap(color)
        #newId = wx.NewId()
        tool = toolbar.AddRadioTool(-1, '', bmp, shortHelp=color)
        self.Bind(wx.EVT_MENU, self.OnColor, tool)
        
    def MakeBitmap(self, color):                              # (5) Создание сплошного битового изображения
        bmp = wx.Bitmap(50, 50)
        dc = wx.MemoryDC()          
        dc.SelectObject(bmp)        
        dc.SetBackground(wx.Brush(color))
        dc.Clear()
        dc.SelectObject(wx.NullBitmap)
        return bmp
    
    def toolbarColorData(self):
        return ("Black", "Red", "Green", "Blue")
    
    def OnColor(self, event):
        menubar = self.GetMenuBar()
        itemId = event.GetId()
        item = menubar.FindItemById(itemId)
        if not item:                                           # (6) Изменение цвета при щелчке на панели инструментов
            toolbar = self.GetToolBar()
            item = toolbar.FindById(itemId)
            color = item.GetShortHelp()
        else:
            color = item.GetLabel()
        self.sketch.SetColor(color)
    
    def OnOtherColor(self, event):     
        dlg = wx.ColourDialog(self)
        dlg.GetColourData().SetChooseFull(True) # Создание объекта цветовых данных
        if dlg.ShowModal() == wx.ID_OK:
            pass
        dlg.Destroy()
        
        
    def OnAbout(self, event):
        dlg = About(self)
        dlg.ShowModal()
        dlg.Destroy()
        
    
#     def OnSplash(self, event):
#         bitmap = wx.Bitmap('cat.png', wx.BITMAP_TYPE_PNG)
#         wx.adv.SplashScreen(bitmap, wx.adv.SPLASH_CENTRE_ON_PARENT|wx.adv.SPLASH_TIMEOUT, 6000, self, -1, style=wx.NO_BORDER)
    def createGrid(self):
        #controlPanel = ControlPanel(self, -1)
        mainSizer = wx.GridBagSizer(hgap=2, vgap=2)
        #gridSizer = wx.BoxSizer(wx.HORIZONTAL)
        actionSizer = wx.BoxSizer(wx.VERTICAL)
        buttons = (("plus.png", self.OnClickPlus), 
                   ("minus.png", self.OnClickMinus), 
                   ('delete.png', self.OnClickDelete))
        for but in buttons:
            bmp = wx.Bitmap(but[0], wx.BITMAP_TYPE_PNG)
            self.button = wx.BitmapButton(self, -1, bmp, pos=(150, 20), style=0)
            self.Bind(wx.EVT_BUTTON, but[1], self.button)
            actionSizer.Add(self.button)
        
        mainSizer.Add(actionSizer, pos=(0,0))    
        grid = MyGrid(self)
       # self.Bind(wx.EVT_MO, self.OnColor, tool)
        
    #    grid.SetColLabelSize(100)
        mainSizer.Add(grid, pos=(0,1), flag=wx.EXPAND)
        tableName = 'category'
        table = MyTable(tableName)
        for idx, col in enumerate(gridData()[tableName][0]):
            table.SetColLabelValue(idx, col)
        grid.SetTable(table, True)
        
        button = wx.Button(self)
        mainSizer.Add(button, pos=(1,0), span=(1,2), flag=wx.EXPAND)
        
        mainSizer.AddGrowableRow(1)
        mainSizer.AddGrowableCol(1)
        self.SetSizer(mainSizer)
    
        
        
    def OnClickPlus(self, event):
        pass
    
    def OnClickMinus(self, event):
        pass
    
    def OnClickDelete(self, event):
        pass
    
def popupMenuData():
    return ('Add item', 'Rename item', 'Remove item', 'Sort children')

class MyPopupMenu(wx.Menu):
    def __init__(self, parent):
        wx.Menu.__init__(self, -1)
        self.parent = parent
        for text in popupMenuData():
            item = self.Append(-1, text)
            self.Bind(wx.EVT_MENU, self.OnPopupItemSelected, item)
        self.parent.Bind(wx.EVT_CONTEXT_MENU, self.OnShowPopup)


    def OnShowPopup(self, event):
        pos = event.GetPosition()
        pos = self.parent.ScreenToClient(pos)
        self.parent.PopupMenu(self, pos)

    def OnPopupItemSelected(self, event):
        item = self.FindItemById(event.GetId())
        self.selection = self.parent.data.selectRows()
        #looking for ID for new row 
        if len(self.selection) != 0:
            maxId = max(row[0] for row in self.selection)
        else: maxId = 0 
        print(len(self.selection), maxId)
        parentId = self.parent.FindIdByItem(item)
        self.parent.data.insertRow((maxId+1, 'test', parentId))
        self.parent.data.commit()

class MyDialog(wx.Dialog):
    def __init__(self, ):
        wx.Dialog.__init__(self, None, -1, "Test", size=(400,500))
        catLabel = wx.StaticText(self, -1, 'Select category:')
        self.tableName = 'category'
        self.data = Data(self.tableName)
        self.selection = self.data.selectRows() 
        
        self.tree = wx.TreeCtrl(self, -1, size=(400,200), style=wx.TR_DEFAULT_STYLE | wx.TR_EDIT_LABELS)
        self.root = self.tree.AddRoot("All categories")
        self.AddTreeNodes(self.root, None)
        self.tree.Expand(self.root)
        
        self.createPopupMenu()
        
  #      button = wx.Button(self, -1, "Which item is selected?")
#         self.Bind(wx.EVT_BUTTON, self.OnClickButton, button)
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(catLabel, 0, wx.LEFT|wx.TOP|wx.RIGHT, 10)
        sizer.Add(self.tree, 0, wx.LEFT|wx.TOP|wx.RIGHT, 10)
 #       sizer.Add(button, 0, wx.LEFT|wx.TOP|wx.RIGHT, 10)
        self.SetSizer(sizer)
        
    def AddTreeNodes(self, parentItem, pId):
        self.treeItems = {}
        for item in [row for row in self.selection if row[2] == pId]:
            newItem = self.tree.AppendItem(parentItem, item[1])
            self.tree.SetItemData(newItem, item[0])  # Added ID category to the appropriate item 
            self.AddTreeNodes(newItem, item[0])
    
    def createPopupMenu(self):
        self.popupmenu = wx.Menu()
        for text in popupMenuData():
            item = self.popupmenu.Append(-1, text)
            self.Bind(wx.EVT_MENU, self.OnPopupItemSelected, item)
        self.tree.Bind(wx.EVT_CONTEXT_MENU, self.OnShowPopup)
        self.tree.Bind(wx.EVT_TREE_END_LABEL_EDIT, self.OnEndLabelEdit)
        
    def OnShowPopup(self, event):
        pos = event.GetPosition()
        self.pos = self.tree.ScreenToClient(pos)
        print('OnShowPopup', event.GetId())
        self.tree.PopupMenu(self.popupmenu, self.pos)
        
    def OnPopupItemSelected(self, event):
        itemText = self.popupmenu.FindItemById(event.GetId()).GetText()
        selItem, flag = self.tree.HitTest(self.pos)
        if itemText == 'Add category':
            newItem = self.tree.AppendItem(selItem, '')
            self.tree.SelectItem(newItem)
            self.tree.EditLabel(newItem)
        elif itemText == 'Edit category':
            self.tree.SelectItem(selItem)
            self.tree.EditLabel(selItem)
        elif itemText == 'Remove category':
            self.DeleteItem()
        elif itemText == 'Sort children': 
            self.SortItems()
        #self.tree.Expand(self.parentItem)
        
    def OnEndLabelEdit(self, event):
        itemText = self.popupmenu.FindItemById(event.GetId()).GetText()
        if itemText == 'Add category':
            self.selection = self.data.selectRows()
            #looking for ID for new row 
            if len(self.selection) != 0:
                maxId = max(row[0] for row in self.selection)
            else: maxId = 0 
            parentId = self.tree.GetItemData(self.tree.GetItemParent(self.tree.GetSelection()))
    #         self.parentItem = None
            self.data.insertRow((maxId+1, event.GetLabel(), parentId))
            self.data.commit()
        elif itemText == 'Edit category':
            self.data.updateRow((maxId+1, event.GetLabel(), parentId))
            self.data.commit()
        event.Skip()
    
    def DeleteItem(self):
        item = self.tree.GetSelection()
        if item:
            self.tree.DeleteChildren(item)
        self.tree.Delete(item)
        
        #I have to add an exception !!!!!
        
        #Removing from DB
        self.selection = self.data.selectRows()
#         self.parentItem = None
        self.data.deleteRow(cols)
        self.data.commit()
            
    def SortItems(self):
        item = self.tree.GetSelection()
        if item:
            self.tree.SortChildren(item)
        
class MyGrid(wx.grid.Grid):
    def __init__(self, parent):
        wx.grid.Grid.__init__(self, parent, -1)
        self.SetRowLabelSize(0)
        
        #gridSizer.Add(grid)
        
        self.Bind(wx.grid.EVT_GRID_CELL_LEFT_CLICK, self.OnCellLeftClick)
        self.Bind(wx.grid.EVT_GRID_LABEL_LEFT_CLICK, self.OnLabelLeftClick)
        self.Bind(wx.grid.EVT_GRID_CELL_LEFT_DCLICK, self.OnLabelLeftDClick)
     
    def OnCellLeftClick(self, event):
        self.ClearSelection()
        row = event.GetRow()
        self.SelectRow(row)
        
    def OnLabelLeftClick(self, event):
        pass
    
    def OnLabelLeftDClick(self, event):
        dlg = MyDialog()
        dlg.ShowModal()
        dlg.Destroy()
    
class Data():
    def __init__(self, tableName):
        self.con = sqlite3.connect('data/fatwallet.db')
        self.cursor = self.con.cursor()
        self.tableName = tableName
        self.dataTable = gridData()[self.tableName]
        self.cols = self.dataTable[0]
        self.ncols = len(self.cols)
        self.nrows = 0
    
    def selectRows(self):
        self.cursor.execute(self.dataTable[1])
        rows = self.cursor.fetchall()
        self.nrows = len(rows) 
        return rows
    
    def insertRow(self, cols):
        self.cursor.execute(self.dataTable[2], cols)
        
    def updateRow(self, cols):
        self.cursor.execute(self.dataTable[3], cols)
        
    def deleteRow(self, cols):
        self.cursor.execute(self.dataTable[4], cols[0])
            
    def commit(self):
        self.con.commit()
        
class MyTable(wx.grid.GridTableBase):
    def __init__(self, tableName):
        wx.grid.GridTableBase.__init__(self)
        self.tableName = tableName
        self.data = Data(self.tableName)
        self.selection = self.data.selectRows() 
        self.nrows = len(self.selection)
        self.ncols = len(self.selection[0])
        
    
    def GetNumberRows(self):
        return self.data.nrows
    
    def GetNumberCols(self):
        return self.data.ncols
    
    def IsEmptyCell(self, row, col):
        #return self.data[row][col] is not None
        return self.selection[row][col] is not None
    
    def GetValue(self, row, col):
#         value = self.data[row][col]
        value = str(self.selection[row][col])
        if value is not None:
            return value
        else:
            return ''

    def SetValue(self, row, col, value):
#         self.data[row][col] = value
        self.selection[row][col] = value
        
    def GetColLabelValue(self, col):
        return self.data.cols[col]
        
        
class About(wx.Dialog):
    text = '''
        <html>
        <body bgcolor="#ACAA60">
        <center><table bgcolor="#455481" width="100%" cellspacing="0"
        cellpadding="0" border="1">
        <tr>
             <td align="center"><h1>FatWallet!</h1></td>
        </tr>
        </table>
        </center>
        <p><b>FatWallet</b> will help you to save money
        </p>
        <p><b>SuperDoodle</b> and <b>wxPython</b> are brought to you by
        <b>Robin Dunn</b> and <b>Total Control Software</b>, Copyright
        &copy; 1997-2006.</p>
        </body>
        </html>
        '''
    
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, 'About Sketch', size=(440, 400) )
        html = wx.html.HtmlWindow(self)
        html.SetPage(self.text)
        button = wx.Button(self, wx.ID_OK, "Okay")
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(html, 1, wx.EXPAND|wx.ALL, 5)
        sizer.Add(button, 0, wx.ALIGN_CENTER|wx.ALL, 5)
        self.SetSizer(sizer)
        self.Layout()
    
           
if __name__ == '__main__':
    app = wx.App()
    frame = MyFrame(None)
    frame.Show(True)
    #app.SetTopWindow(frame)
    app.MainLoop()