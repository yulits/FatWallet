import wx
import wx.grid
import wx.adv 
import sqlite3
from wx.lib.pubsub import pub 
import os

imgFolder = os.getcwd() + '\\bmp\\'

def gridData():
    return {'category': (('CategoryId', 'Name', 'ParentId'),
                           {'all':'select * from category',
                            'id':'select max(CategoryId) from category',
                            'filter':'select * from category '},
                           'insert into category values (?, ?, ?)',
                           'update category set Name=?, ParentId=? where CategoryId=?',
                           'delete from category where CategoryId=?'),
            'item': (('Name', 'Category'),
                           {'all':'select i.Name, \
                               (select c.Name from category c where c.CategoryId = i.CategoryId) from item i', 
                               'id': 'select max(ItemId) from item',
                               'filter': 'select i.Name, \
                               (select c.Name from category c where c.CategoryId = i.CategoryId) from item i'
                               },
                           'insert into item values (?, ?, ?)',
                           'update item set Name=?, CategoryId=? where ItemId=?',
                           'delete from item where ItemId=?') ,
            'account': (('AccountId', 'Name', 'CurrencyId'),
                           {'all':'select * from account', 
                            'id':'select max(AccountId) from account', 
                            'filter': 'select * from account '},
                           'insert into account values (?, ?, ?)',
                           'update account set Name=?, CurrencyId=? where AccountId=?',
                           'delete from account where AccountId=?'),
            'currency': (('Short Name', 'Full Name', 'Code'),
                           {'all':'select ShortName, FullName, Code from currency', 
                            'id': 'select max(CurrencyId) from currency',
                            'filter': 'select * from currency '},
                           'insert into currency values (?, ?, ?, ?)',
                           'update item set ShortName=?, FullName=?, Code=? where CurrencyId=?',
                           'delete from currency where CurrencyId=?'),
            'organization': (('OrganizationId', 'Name'),
                           {'all':'select * from organization', 
                            'id':'select max(OrganizationId) from organization',
                            'filter': 'select * from organization '},
                           'insert into organization values (?, ?)',
                           'update organization set Name=? where OrganizationId=?',
                           'delete from organization where OrganizationId=?'), 
            'payment': (('PayDate', 'Account', 'Organization', 'Category', 'Item', 'Price', 'Count', 'Total'), # %H:%M:%S
                           {'all':"select strftime('%m/%d/%Y', PayDate), \
                           (select a.Name from account a where a.AccountId = e.AccountId),\
                           (select o.Name from organization o where o.OrganizationId = e.OrganizationId), \
                           (select c.Name from category c, item i where c.CategoryId = i.CategoryId and i.ItemId = e.ItemId), \
                           (select i.Name from item i where i.ItemId = e.ItemId),\
                           Price, Count, Sum\
                           from payment e", 
                           'id': 'select max(PaymentId) from payment',
                           'filter': 'select * from payment '},
                           'insert into payment values (?, ?, ?, ?, ?, ?, ?, ?)',
                           'update payment set PayDate=?, AccountId=?, ItemId=?, OrganizationId=?, Price=?, Count=?, Sum=? where PaymentId=?',
                           'delete from payment where PaymentId=?'), 
            'income': (('IncomeDate', 'Account', 'Organization', 'Category', 'Item', 'Sum'), # %H:%M:%S
                           {'all':"select strftime('%m/%d/%Y', IncomeDate), \
                           (select a.Name from account a where a.AccountId = e.AccountId),\
                           (select o.Name from organization o where o.OrganizationId = e.OrganizationId), \
                           (select c.Name from category c, item i where c.CategoryId = i.CategoryId and i.ItemId = e.ItemId), \
                           (select i.Name from item i where i.ItemId = e.ItemId),\
                           Sum\
                           from income e", 
                           'id': 'select max(IncomeId) from income',
                           'filter': 'select * from income '},
                           'insert into income values (?, ?, ?, ?, ?, ?)',
                           'update income set IncomeDate=?, AccountId=?, ItemId=?, OrganizationId=?, Sum=? where IncomeId=?'
                           'delete from income where IncomeId=?'), 

            }

def makeChoice(tableName):
    selection = DBData.selectRows(tableName)
    return [item[1] for item in selection if item[1] is not None]  #if item[1] is not None else '' 

def dialogData():  
    """
        Structure: 
        { dialog name: ((what kind of element to add, label, style, proportion, flags))
        }
    """
    return {'StaticText': (
                        ((wx.StaticText, 'Date', 0, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER|wx.TOP|wx.LEFT|wx.BOTTOM), 
                            (wx.adv.DatePickerCtrl, wx.DateTime().Now(), wx.adv.DP_DROPDOWN, 0, wx.ALIGN_LEFT|wx.EXPAND|wx.ALL, 'date'), 
                            (wx.StaticText, 'Account', 0, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER|wx.TOP|wx.LEFT|wx.BOTTOM), 
                            (wx.ComboBox, 'Select account...', wx.CB_DROPDOWN, 1, wx.ALIGN_LEFT|wx.EXPAND|wx.ALL,  'account', makeChoice('account'))
                            ), 
                        ((wx.StaticText, 'Organization', 0, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER|wx.TOP|wx.LEFT|wx.BOTTOM), 
                            (wx.ComboBox, 'Select organization...', wx.CB_DROPDOWN, 1, wx.ALIGN_LEFT|wx.EXPAND|wx.ALL, 'organization', makeChoice('organization'))
                            ),
                        ((wx.StaticText, 'Category', 0, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER|wx.TOP|wx.LEFT|wx.BOTTOM), 
                            (wx.ComboBox, 'Select category...', wx.CB_DROPDOWN, 1, wx.ALIGN_LEFT|wx.EXPAND|wx.ALL, 'category', makeChoice('category'))
                            ),
                        ((wx.StaticText, 'Item', 0, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER|wx.TOP|wx.LEFT|wx.BOTTOM), 
                            (wx.ComboBox, 'Select item...', wx.CB_DROPDOWN, 1, wx.ALIGN_LEFT|wx.EXPAND|wx.ALL, 'item', makeChoice('item'))
                            ),
                        ((wx.StaticText, 'Price', 0, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER|wx.TOP|wx.LEFT|wx.BOTTOM), 
                            (wx.TextCtrl, '', 0, 0, wx.ALIGN_LEFT|wx.EXPAND|wx.ALL, 'price'), 
                            (wx.StaticText, 'Count', 0, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER|wx.TOP|wx.LEFT|wx.BOTTOM), 
                            (wx.TextCtrl, '', 0, 0, wx.ALIGN_LEFT|wx.EXPAND|wx.ALL, 'count')
                            ),
                        ((wx.StaticText, 'Total', 0, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER|wx.TOP|wx.LEFT|wx.BOTTOM), 
                            (wx.TextCtrl, '', 0, 0, wx.ALIGN_LEFT|wx.EXPAND|wx.ALL, 'total')
                            ),    
                        ((wx.Button, 'Ok', 0, 0, wx.ALIGN_LEFT|wx.ALL, 'ok'), 
                         (wx.Button, 'Cancel', 0, 0, wx.ALIGN_LEFT|wx.ALL, 'cancel'))
                        ),
            'currency': (
                        ((wx.StaticText, 'Full Name', 0, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER|wx.TOP|wx.LEFT|wx.BOTTOM), 
                            (wx.TextCtrl, '', 0, 0, wx.ALIGN_LEFT|wx.EXPAND|wx.ALL, 'fullname')
                            ),
                        ((wx.StaticText, 'Short name', 0, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER|wx.TOP|wx.LEFT|wx.BOTTOM), 
                            (wx.TextCtrl, '', 0, 0, wx.ALIGN_LEFT|wx.EXPAND|wx.ALL, 'shortname')
                            ),
                        ((wx.StaticText, 'Code', 0, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER|wx.TOP|wx.LEFT|wx.BOTTOM), 
                            (wx.TextCtrl, '', 0, 0, wx.ALIGN_LEFT|wx.EXPAND|wx.ALL, 'code')
                            ),    
                        ((wx.Button, 'Ok', 0, 0, wx.ALIGN_LEFT|wx.ALL, 'ok'), 
                         (wx.Button, 'Cancel', 0, 0, wx.ALIGN_LEFT|wx.ALL, 'cancel'))
                        ),
            'account': (
                        ((wx.StaticText, 'Name', 0, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER|wx.TOP|wx.LEFT|wx.BOTTOM), 
                            (wx.TextCtrl, '', 0, 0, wx.ALIGN_LEFT|wx.EXPAND|wx.ALL)
                            ),
                        ((wx.StaticText, 'Currency', 0, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER|wx.TOP|wx.LEFT|wx.BOTTOM), 
                            (wx.ComboBox, 'Select currency...', wx.CB_DROPDOWN, 1, wx.ALIGN_LEFT|wx.EXPAND|wx.ALL,  'currency', makeChoice('account'))
                            ),
                        ((wx.Button, 'Ok', 0, 0, wx.ALIGN_LEFT|wx.ALL, 'ok'), 
                         (wx.Button, 'Cancel', 0, 0, wx.ALIGN_LEFT|wx.ALL, 'cancel'))
                        ),
            'item': (
                        ((wx.StaticText, 'Name', 0, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER|wx.TOP|wx.LEFT|wx.BOTTOM), 
                            (wx.TextCtrl, '', 0, 0, wx.ALIGN_LEFT|wx.EXPAND|wx.ALL)
                            ),
                        ((wx.StaticText, 'Currency', 0, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER|wx.TOP|wx.LEFT|wx.BOTTOM), 
                            (wx.ComboBox, 'Select currency...', wx.CB_DROPDOWN, 1, wx.ALIGN_LEFT|wx.EXPAND|wx.ALL,  'currency', makeChoice('account'))
                            ),
                        ((wx.Button, 'Ok', 0, 0, wx.ALIGN_LEFT|wx.ALL, 'ok'), 
                         (wx.Button, 'Cancel', 0, 0, wx.ALIGN_LEFT|wx.ALL, 'cancel'))
                        ),
            'category': (
                        ((wx.StaticText, 'Name', 0, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER|wx.TOP|wx.LEFT|wx.BOTTOM), 
                            (wx.TextCtrl, '', 0, 0, wx.ALIGN_LEFT|wx.EXPAND|wx.ALL)
                            ),
                        ((wx.StaticText, 'Currency', 0, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER|wx.TOP|wx.LEFT|wx.BOTTOM), 
                            (wx.ComboBox, 'Select currency...', wx.CB_DROPDOWN, 1, wx.ALIGN_LEFT|wx.EXPAND|wx.ALL,  'currency', makeChoice('account'))
                            ),
                        ((wx.Button, 'Ok', 0, 0, wx.ALIGN_LEFT|wx.ALL, 'ok'), 
                         (wx.Button, 'Cancel', 0, 0, wx.ALIGN_LEFT|wx.ALL, 'cancel'))
                        )
            } 
    
# def dialogData():  
#     """
#         Structure: 
#         { dialog name: ((what kind of element to add, label, style, proportion, flags))
#         }
#     """
#     return {'payment': (
#                         ((wx.StaticText, 'Date', 0, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER|wx.TOP|wx.LEFT|wx.BOTTOM), 
#                             (wx.adv.DatePickerCtrl, wx.DateTime().Now(), wx.adv.DP_DROPDOWN, 0, wx.ALIGN_LEFT|wx.EXPAND|wx.ALL), 
#                             (wx.StaticText, 'Account', 0, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER|wx.TOP|wx.LEFT|wx.BOTTOM), 
#                             (wx.ComboBox, 'Select account...', wx.CB_DROPDOWN, 1, wx.ALIGN_LEFT|wx.EXPAND|wx.ALL,  'account', makeChoice('account'))
#                             ), 
#                         ((wx.StaticText, 'Organization', 0, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER|wx.TOP|wx.LEFT|wx.BOTTOM), 
#                             (wx.ComboBox, 'Select organization...', wx.CB_DROPDOWN, 1, wx.ALIGN_LEFT|wx.EXPAND|wx.ALL, 'organization', makeChoice('organization'))
#                             ),
#                         ((wx.StaticText, 'Category', 0, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER|wx.TOP|wx.LEFT|wx.BOTTOM), 
#                             (wx.ComboBox, 'Select category...', wx.CB_DROPDOWN, 1, wx.ALIGN_LEFT|wx.EXPAND|wx.ALL, 'category', makeChoice('category'))
#                             ),
#                         ((wx.StaticText, 'Item', 0, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER|wx.TOP|wx.LEFT|wx.BOTTOM), 
#                             (wx.ComboBox, 'Select item...', wx.CB_DROPDOWN, 1, wx.ALIGN_LEFT|wx.EXPAND|wx.ALL, 'item', makeChoice('item'))
#                             ),
#                         ((wx.StaticText, 'Price', 0, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER|wx.TOP|wx.LEFT|wx.BOTTOM), 
#                             (wx.TextCtrl, '', 0, 0, wx.ALIGN_LEFT|wx.EXPAND|wx.ALL), 
#                             (wx.StaticText, 'Count', 0, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER|wx.TOP|wx.LEFT|wx.BOTTOM), 
#                             (wx.TextCtrl, '', 0, 0, wx.ALIGN_LEFT|wx.EXPAND|wx.ALL)
#                             ),
#                         ((wx.StaticText, 'Total', 0, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER|wx.TOP|wx.LEFT|wx.BOTTOM), 
#                             (wx.TextCtrl, '', 0, 0, wx.ALIGN_LEFT|wx.EXPAND|wx.ALL)
#                             ),    
#                         ((wx.Button, 'Ok', 0, 0, wx.ALIGN_LEFT|wx.ALL, 'ok'), 
#                          (wx.Button, 'Cancel', 0, 0, wx.ALIGN_LEFT|wx.ALL, 'cancel'))
#                         ),
#             'currency': (
#                         ((wx.StaticText, 'Full Name', 0, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER|wx.TOP|wx.LEFT|wx.BOTTOM), 
#                             (wx.TextCtrl, '', 0, 0, wx.ALIGN_LEFT|wx.EXPAND|wx.ALL)
#                             ),
#                         ((wx.StaticText, 'Short name', 0, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER|wx.TOP|wx.LEFT|wx.BOTTOM), 
#                             (wx.TextCtrl, '', 0, 0, wx.ALIGN_LEFT|wx.EXPAND|wx.ALL)
#                             ),
#                         ((wx.StaticText, 'Code', 0, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER|wx.TOP|wx.LEFT|wx.BOTTOM), 
#                             (wx.TextCtrl, '', 0, 0, wx.ALIGN_LEFT|wx.EXPAND|wx.ALL)
#                             ),    
#                         ((wx.Button, 'Ok', 0, 0, wx.ALIGN_LEFT|wx.ALL, 'ok'), 
#                          (wx.Button, 'Cancel', 0, 0, wx.ALIGN_LEFT|wx.ALL, 'cancel'))
#                         ),
#             'account': (
#                         ((wx.StaticText, 'Name', 0, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER|wx.TOP|wx.LEFT|wx.BOTTOM), 
#                             (wx.TextCtrl, '', 0, 0, wx.ALIGN_LEFT|wx.EXPAND|wx.ALL)
#                             ),
#                         ((wx.StaticText, 'Currency', 0, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER|wx.TOP|wx.LEFT|wx.BOTTOM), 
#                             (wx.ComboBox, 'Select currency...', wx.CB_DROPDOWN, 1, wx.ALIGN_LEFT|wx.EXPAND|wx.ALL,  'currency', makeChoice('account'))
#                             ),
#                         ((wx.Button, 'Ok', 0, 0, wx.ALIGN_LEFT|wx.ALL, 'ok'), 
#                          (wx.Button, 'Cancel', 0, 0, wx.ALIGN_LEFT|wx.ALL, 'cancel'))
#                         ),
#             'item': (
#                         ((wx.StaticText, 'Name', 0, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER|wx.TOP|wx.LEFT|wx.BOTTOM), 
#                             (wx.TextCtrl, '', 0, 0, wx.ALIGN_LEFT|wx.EXPAND|wx.ALL)
#                             ),
#                         ((wx.StaticText, 'Currency', 0, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER|wx.TOP|wx.LEFT|wx.BOTTOM), 
#                             (wx.ComboBox, 'Select currency...', wx.CB_DROPDOWN, 1, wx.ALIGN_LEFT|wx.EXPAND|wx.ALL,  'currency', makeChoice('account'))
#                             ),
#                         ((wx.Button, 'Ok', 0, 0, wx.ALIGN_LEFT|wx.ALL, 'ok'), 
#                          (wx.Button, 'Cancel', 0, 0, wx.ALIGN_LEFT|wx.ALL, 'cancel'))
#                         ),
#             'category': (
#                         ((wx.StaticText, 'Name', 0, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER|wx.TOP|wx.LEFT|wx.BOTTOM), 
#                             (wx.TextCtrl, '', 0, 0, wx.ALIGN_LEFT|wx.EXPAND|wx.ALL)
#                             ),
#                         ((wx.StaticText, 'Currency', 0, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER|wx.TOP|wx.LEFT|wx.BOTTOM), 
#                             (wx.ComboBox, 'Select currency...', wx.CB_DROPDOWN, 1, wx.ALIGN_LEFT|wx.EXPAND|wx.ALL,  'currency', makeChoice('account'))
#                             ),
#                         ((wx.Button, 'Ok', 0, 0, wx.ALIGN_LEFT|wx.ALL, 'ok'), 
#                          (wx.Button, 'Cancel', 0, 0, wx.ALIGN_LEFT|wx.ALL, 'cancel'))
#                         )
#             } 

class MainFrame(wx.Frame):
    def __init__(self, parent):
        self.title = "FatWallet"
        wx.Frame.__init__(self, parent, -1, self.title, size=(800,600))
        self.Centre()
        self.initStatusBar()
        self.createMenuBar()
        self.createToolBar()
        self.createGrid()
        pub.subscribe(self.myListener, "mainListener")
    
    def initStatusBar(self):
        self.statusbar = self.CreateStatusBar()
        self.statusbar.SetFieldsCount(3)
        self.statusbar.SetStatusWidths([-1, -2, -3])
        

    def menuData(self):
        return [("&File", 
                    (
                     ("", "", ""),
                     ("&Quit", "Quit", self.OnCloseWindow)
                    )
                 ),
                ("&Dictionary", 
                    (
                     ("&Account", "Accounts list", self.OnAccountList),
                     ("&Currency", "Currency list", self.OnCurrencyList),
                     ("Category and &items", "Category and items list", self.OnCategoryList),
                     ("&Organizations", "C", self.OnOrganizationList),
                     ("", "", "")
                    )
                ),
                ("&Actions", 
                    (
                     ("&Payment", "Payment list", self.OnPaymentList),
                     ("&Incomes", "Incomes list", self.OnIncomeList)
                    )
                ),
                ("&About", (
                ("&Info", "About app", self.OnAbout),
                #("Splash", "Splash window", self.OnSplash)
                ))
                ]
    
    def OnAccountList(self, event):
        accountDialog = AccountDialog()
        accountDialog.ShowModal()
        accountDialog.Destroy()
    
    def OnCurrencyList(self, event):
        curDialog = CurrencyDialog()
        curDialog.ShowModal()
        curDialog.Destroy()
        
    def OnCategoryList(self, event):
        catDialog = CategoryDialog()
        catDialog.ShowModal()
        catDialog.Destroy()
        
    def OnOrganizationList(self, event):
        orgDialog = OrgDialog()
        orgDialog.ShowModal()
        orgDialog.Destroy()
        
    def OnPaymentList(self, event):
        try:
            if self.payFrame.IsShown():
                self.payFrame.Iconize(False)
            else: self.payFrame.Show()
        except AttributeError: # if a PaymentFrame instance does not exist create it 
            self.payFrame = PaymentFrame(self, 'Payment')
            self.payFrame.Show()
            
    def OnIncomeList(self, event):
        try:
            if self.incomeFrame.IsShown():
                self.incomeFrame.Iconize(False)
            else: self.incomeFrame.Show()
        except AttributeError: # if a PaymentFrame instance does not exist create it 
            self.incomeFrame = IncomeFrame(self, 'Income')
            self.incomeFrame.Show()
    
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
        return (("Payment", imgFolder+"payments.png", "Add payment", self.OnEvent),
                ("", "", "", ""),
                ("Profit", imgFolder+"incomes.png", "Add income", self.OnEvent),
                ("", "", "", ""),
                ("Planning", imgFolder+"plan.png", "Planning", self.OnEvent))
        
    def OnEvent(self, e):
        pass
                                                  
                                                  
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
        
    def myListener(self, message, arg2=None):
        """
        Listener function
        """
        print("Received the following message: " + message)
        if arg2:
            print("Received another arguments: " + str(arg2))
 
#     def OnSplash(self, event):
#         bitmap = wx.Bitmap('cat.png', wx.BITMAP_TYPE_PNG)
#         wx.adv.SplashScreen(bitmap, wx.adv.SPLASH_CENTRE_ON_PARENT|wx.adv.SPLASH_TIMEOUT, 6000, self, -1, style=wx.NO_BORDER)
    def createGrid(self):
        #controlPanel = ControlPanel(self, -1)
        mainSizer = wx.GridBagSizer(hgap=2, vgap=2)
        #gridSizer = wx.BoxSizer(wx.HORIZONTAL)
        
        grid = MyGrid(self, 'payment', gridPopupMenuData('payment'))
       # self.Bind(wx.EVT_MO, self.OnColor, tool)
        
    #    grid.SetColLabelSize(100)
        mainSizer.Add(grid, pos=(0,1), flag=wx.EXPAND)
        
        button = wx.Button(self)
#         mainSizer.Add(button, pos=(1,0), span=(1,2), flag=wx.EXPAND)
        mainSizer.Add(button, pos=(1,0),  flag=wx.EXPAND)
        
        mainSizer.AddGrowableRow(1)
        mainSizer.AddGrowableCol(1)
        self.SetSizer(mainSizer)
    
        
        
#     def OnClickPlus(self, event):
#         pass
#     
#     def OnClickMinus(self, event):
#         pass
#     
#     def OnClickDelete(self, event):
#         pass
    


# class MyPopupMenu(wx.Menu):
#     def __init__(self, parent):
#         wx.Menu.__init__(self, -1)
#         self.parent = parent
#         for text in popupMenuData():
#             item = self.Append(-1, text)
#             self.Bind(wx.EVT_MENU, self.OnPopupItemSelected, item)
#         self.parent.Bind(wx.EVT_CONTEXT_MENU, self.OnShowPopup)
# 
# 
#     def OnShowPopup(self, event):
#         pos = event.GetPosition()
#         pos = self.parent.ScreenToClient(pos)
#         self.parent.PopupMenu(self, pos)
# 
#     def OnPopupItemSelected(self, event):
#         item = self.FindItemById(event.GetId())
#         self.selection = self.parent.data.selectRows()
#         #looking for ID for new row 
#         if len(self.selection) != 0:
#             maxId = max(row[0] for row in self.selection)
#         else: maxId = 0 
#         parentId = self.parent.FindIdByItem(item)
#         self.parent.data.insertRow((maxId+1, 'test', parentId))
#         self.parent.data.commit()

def treePopupMenuData(tableName):
    return ('Add %s' % tableName, 'Rename %s' % tableName, 'Remove %s' % tableName, 'Sort children')

def gridPopupMenuData(tableName):
    return ('Add %s' % tableName, 'Edit %s' % tableName, 'Delete %s' % tableName)

class CategoryDialog(wx.Dialog):
    #----------------------------------------------------------------------
    def __init__(self):
        wx.Dialog.__init__(self, None, wx.ID_ANY, "Categories and items", style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER, size=(700,500))
        self.panel = wx.Panel(self)
        catLabel = wx.StaticText(self.panel, -1, 'Categories')
        self.tableName = 'category'
        self.data = DBData
        self.selection = self.data.selectRows(self.tableName) 
        
        self.createTree()
        self.treePopupMenu = self.createPopupMenu(treePopupMenuData)
        
        
        
        itemLabel = wx.StaticText(self.panel, -1, 'Items')
        gridPanel = wx.Panel(self.panel, style=wx.SUNKEN_BORDER)
        self.itemGrid = MyGrid(gridPanel, 'item', gridPopupMenuData('item'))
        self.itemGrid.Fit()
        
        closeBtn = wx.Button(self.panel, label="Close")
        closeBtn.Bind(wx.EVT_BUTTON, self.onSendAndClose)

        buts = ActionButtons(self.panel, self.tableName)
        buts.actionSizer.InsertSpacer(0, 25)
        
        mainSizer = wx.BoxSizer(wx.HORIZONTAL)
        catSizer = wx.BoxSizer(wx.VERTICAL)
        catSizer.Add(catLabel, 0, wx.LEFT|wx.TOP|wx.RIGHT, 10)
        catSizer.Add(self.tree, 1, wx.ALL|wx.EXPAND, 10)
 #       sizer.Add(button, 0, wx.LEFT|wx.TOP|wx.RIGHT, 10)
        mainSizer.Add(catSizer, 1, wx.EXPAND)
        itemSizer = wx.BoxSizer(wx.VERTICAL)
        itemSizer.Add(itemLabel, 0, wx.LEFT|wx.TOP|wx.RIGHT, 10)
        #itemSizer.Add(self.grid, 1, wx.ALL|wx.EXPAND, 10)
        itemSizer.Add(gridPanel, 1, wx.ALL|wx.EXPAND, 10)
        itemSizer.Add(closeBtn, 0, wx.ALL|wx.RIGHT, 10)
        mainSizer.Add(itemSizer, 1, wx.EXPAND)
        mainSizer.Add(buts.actionSizer, 0, wx.ALL, 10)
        
        self.panel.SetSizer(mainSizer)
    
    def createTree(self):
        self.tree = wx.TreeCtrl(self.panel, -1, size=(400,200), style=wx.TR_DEFAULT_STYLE | wx.TR_EDIT_LABELS)
        self.root = self.tree.AddRoot("All categories")
        self.addTreeNodes(self.root, None)
        self.tree.SetItemData(self.root, 'root')
        self.tree.SelectItem(self.root)
        self.tree.Expand(self.root)
        self.tree.Bind(wx.EVT_CONTEXT_MENU, self.OnShowPopup)
        self.tree.Bind(wx.EVT_TREE_END_LABEL_EDIT, self.OnEndLabelEdit)
#         self.tree.Bind(wx.EVT_TREE_BEGIN_LABEL_EDIT, self.OnBeginLabelEdit)
        self.Bind(wx.EVT_TREE_SEL_CHANGED, self.OnSelChanged, self.tree)
            
    def addTreeNodes(self, parentItem, pId):
        self.treeItems = {}
        for item in [row for row in self.selection if row[2] == pId]:
            newItem = self.tree.AppendItem(parentItem, item[1])
            self.tree.SetItemData(newItem, item[0])  # Added ID category to the appropriate item 
            self.addTreeNodes(newItem, item[0])
            
    
    
       # self.Bind(wx.EVT_MO, self.OnColor, tool)
        
    #    grid.SetColLabelSize(100)
        
    def createPopupMenu(self, PopupMenuData):
        popupmenu = wx.Menu()
        for text in PopupMenuData(self.tableName):
#             print(text)
            item = popupmenu.Append(-1, text)
            self.Bind(wx.EVT_MENU, self.OnPopupItemSelected, item)
        return popupmenu
        
    def OnShowPopup(self, event):
        pos = event.GetPosition()
        self.pos = self.tree.ScreenToClient(pos)
        self.tree.PopupMenu(self.treePopupMenu, self.pos)
#         
#     def OnShowPopup2(self, event):
#         pos = event.GetPosition()
#         print('pos:', pos)
#         self.pos = self.grid.ScreenToClient(pos)
#         self.grid.PopupMenu(self.gridPopupMenu2, self.pos)
#         
#     def OnShowPopup3(self, event):
#         pos = event.GetPosition()
#         self.pos = self.gridPanel.ScreenToClient(pos)
#         self.gridPanel.PopupMenu(self.gridPopupMenu, self.pos)
#     
    
    def OnPopupItemSelected(self, event):
        itemText = self.treePopupMenu.FindItemById(event.GetId()).GetText()
        selItem, flag = self.tree.HitTest(self.pos)
        self.tree.SelectItem(selItem)
        #self.OnSelChanged(event)
        if itemText == 'Add category':
            newItem = self.tree.AppendItem(selItem, '')
            self.tree.SelectItem(newItem)
            self.tree.EditLabel(newItem)
        elif itemText == 'Rename category':
            print(selItem)
            self.tree.EditLabel(selItem)
        elif itemText == 'Remove category':
            self.DeleteItem()
#         elif itemText == 'Sort children': 
#             self.SortItems()
        #self.tree.Expand(self.parentItem)
    
#     def OnRightClick(self, event):
#         selItem, flag = self.tree.HitTest(self.pos)
#         self.tree.SelectItem(selItem)
#         self.OnSelChanged(event)
#         event.Skip()
        
    def OnSelChanged(self, event):
        self.tree.SetItemText(self.root, 'All categories')
        self.itemGrid.ClearGrid()
        treeItem = event.GetItem()
#         if self.tree.GetItemData(treeItem) is not None: # if a tree item doesn't have DB ID, than it's a new one and no need to select anything
        if treeItem == self.root:
            print('Yes, I"m root!')
            self.itemGrid.table.selection = self.data.selectRows('item')
        else:
            if treeItem is not None and self.tree.GetItemData(treeItem) is not None:  # if a tree item doesn't have DB ID, than it's a new one and no need to select anything
                catItemId = self.tree.GetItemData(treeItem)
#                 self.itemGrid.table.selection = self.data.selectRows('item', cond='filter', CategoryId=catItemId)
                self.itemGrid.table.selection = self.data.selectRows('item', 'filter', ' where CategoryId = %s' % (catItemId))
#                 self.itemGrid.table.nrows = len(self.itemGrid.table.selection)
            
    def OnEndLabelEdit(self, event):
#         print('OnEndLabelEdit')
        treeItem = event.GetItem()
        if event.GetLabel().strip() != '': 
            if self.tree.GetItemData(treeItem) is None: # if an item doesn't have DB ID, than it's a new one       
                # add item
                #if event.GetId() > 0:
    #             popupMenuText = self.popupmenu.FindItemById(event.GetId()).GetText()
    #             print('popupText:', popupMenuText)
                
                
    #             if popupMenuText == 'Add category':
                maxId = self.data.getMaxID(self.tableName) 
                
                parentItemData = self.tree.GetItemData(self.tree.GetItemParent(treeItem))
                if parentItemData == 'root':
                    parentId = None
                else: parentId = parentItemData
                
                print('Add category', maxId+1,  event.GetLabel(), parentId)
                
                self.data.insertRow(self.tableName, (maxId+1, event.GetLabel(), parentId))
                self.data.commit()
                
                
            elif self.tree.GetItemData(treeItem) != 'root':
                categoryId = self.tree.GetItemData(treeItem)
                parentItemData = self.tree.GetItemData(self.tree.GetItemParent(treeItem))
                if parentItemData == 'root':
                    parentId = None
                else: parentId = parentItemData
                
                print('Rename category', event.GetLabel(), parentId, categoryId)
                
                self.data.updateRow(self.tableName, (event.GetLabel(), parentId, categoryId))
                self.data.commit()
        else: 
            self.tree.Delete(treeItem)
#             dlg = wx.MessageDialog(None, 'Название не может быть пустым', 'New Message', wx.OK)
#             res = dlg.ShowModal()
#             dlg.Destroy()   
        event.Skip()
    
    def DeleteItem(self):
        item = self.tree.GetSelection()
        if item:
            self.tree.DeleteChildren(item)
        
        id = self.tree.GetItemData(item)
        self.tree.Delete(item)        
        #I have to add an exception !!!!!
        
        #Removing from DB
       
        self.selection = self.data.selectRows(self.tableName)
        self.data.deleteRow(self.tableName, id)
        self.data.commit()
            
    def SortItems(self):
        item = self.root
        if item:
            self.tree.SortChildren(item)
 
    #----------------------------------------------------------------------
    def onSendAndClose(self, event):
        """
        Send a message and close frame
        """
        #msg = self.msgTxt.GetValue()
        #pub.sendMessage("mainListener", message='test1')
        #pub.sendMessage("mainListener", message="test2", arg2="2nd argument!")
        self.Close()

class ActionButtons:
    def __init__(self, parent, tableName):
        self.tableName = tableName
        self.actionSizer = wx.BoxSizer(wx.VERTICAL)

        buttons = ((imgFolder+"new.png", self.OnNewClick, 'add'), 
                   (imgFolder+"edit.png", self.OnEditClick, 'edit'), 
                   (imgFolder+'delete.png', self.OnDeleteClick, 'delete'))
        for but in buttons:
            img = wx.Image(but[0]).Scale(48, 48, wx.IMAGE_QUALITY_HIGH)
            self.button = wx.BitmapButton(parent, -1, img.ConvertToBitmap())
            self.button.SetToolTip(wx.ToolTip("Click here to %s" % but[2]))
            self.button.Bind(wx.EVT_BUTTON, but[1])
            self.actionSizer.Add(self.button)
            
    def OnNewClick(self, event):
        pass
    
    def OnEditClick(self, event):
        pass
    
    def OnDeleteClick(self, event):
        pass
    
class MyDialog(wx.Dialog):
    #----------------------------------------------------------------------
    def __init__(self, table):
        wx.Dialog.__init__(self, None, wx.ID_ANY, table, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER, size=(700,500))
        mainPanel = wx.Panel(self)
#         curLabel = wx.StaticText(self.panel, -1, table)
        self.tableName = table.lower()
        self.data = DBData
        self.selection = self.data.selectRows(self.tableName) 
        
        curPanel = wx.Panel(mainPanel, style=wx.SUNKEN_BORDER)
        self.curGrid = MyGrid(curPanel, self.tableName, gridPopupMenuData(self.tableName))
        
        self.curGrid.Fit()
        
        closeBtn = wx.Button(mainPanel, label="Close")
        closeBtn.Bind(wx.EVT_BUTTON, self.onClose)

        buts = ActionButtons(mainPanel, self.tableName)
        
        mainSizer = wx.BoxSizer(wx.HORIZONTAL)
        curSizer = wx.BoxSizer(wx.VERTICAL)
#         curSizer.Add(curLabel, 0, wx.LEFT|wx.TOP|wx.RIGHT, 10)
        curSizer.Add(curPanel, 1, wx.ALL|wx.EXPAND, 10)
        curSizer.Add(closeBtn, 0, wx.ALL|wx.RIGHT, 10)
        
        mainSizer.Add(curSizer, 1, wx.EXPAND)
        mainSizer.Add(buts.actionSizer, 0, wx.ALL, 10)
        mainPanel.SetSizer(mainSizer) 
        
    #----------------------------------------------------------------------
    
        
    def onClose(self, event):
        """
        Send a message and close frame
        """
        #msg = self.msgTxt.GetValue()
        #pub.sendMessage("mainListener", message='test1')
        #pub.sendMessage("mainListener", message="test2", arg2="2nd argument!")
#         self.ToggleWindowStyle(wx.STAY_ON_TOP)
        self.Close() 


        
class AccountDialog(MyDialog):
    #----------------------------------------------------------------------
    def __init__(self):
        MyDialog.__init__(self, "Account")
        
        
class CurrencyDialog(MyDialog):
    #----------------------------------------------------------------------
    def __init__(self):
        MyDialog.__init__(self, "Currency")
        
class OrgDialog(MyDialog):
    #----------------------------------------------------------------------
    def __init__(self):
        MyDialog.__init__(self, "Organization")
               
    #----------------------------------------------------------------------
class MyFrame(wx.Frame):
    def __init__(self, parent, table, gridPopupMenuData):
        wx.Frame.__init__(self, parent, wx.ID_ANY, title=table, size=(700,500))
        self.CentreOnParent()
        mainPanel = wx.Panel(self)
        self.tableName = table.lower()
        self.data = DBData
        self.selection = self.data.selectRows(self.tableName) 
        
        gridPanel = wx.Panel(mainPanel, style=wx.SUNKEN_BORDER)
        self.grid = MyGrid(gridPanel, self.tableName, gridPopupMenuData(self.tableName))
        
        self.grid.Fit()
        
        closeBtn = wx.Button(mainPanel, label="Close")
        self.Bind(wx.EVT_BUTTON, self.onClose, closeBtn)
        
        buts = ActionButtons(mainPanel)
          
        self.Bind(wx.EVT_CLOSE, self.onClose)

        mainSizer = wx.BoxSizer(wx.HORIZONTAL)
        gridSizer = wx.BoxSizer(wx.VERTICAL)
        gridSizer.Add(gridPanel, 1, wx.ALL|wx.EXPAND, 10)
        gridSizer.Add(closeBtn, 0, wx.ALL|wx.RIGHT, 10)
        mainSizer.Add(gridSizer, 1, wx.EXPAND)
        mainSizer.Add(buts.actionSizer, 0, wx.ALL, 10)  
        mainPanel.SetSizer(mainSizer)
          
       
    #----------------------------------------------------------------------
    def onClose(self, event):
        """
        Send a message and close frame
        """
        #msg = self.msgTxt.GetValue()
        #pub.sendMessage("mainListener", message='test1')
        #pub.sendMessage("mainListener", message="test2", arg2="2nd argument!")
#         self.ToggleWindowStyle(wx.STAY_ON_TOP)
        self.Hide()    
    #----------------------------------------------------------------------
class PaymentFrame(MyFrame):
    def __init__(self, parent, table):
        MyFrame.__init__(self, parent, table, gridPopupMenuData)
        
        
class IncomeFrame(MyFrame):
    def __init__(self, parent, table):
        MyFrame.__init__(self, parent, table, gridPopupMenuData)
    
        
class MyGrid(wx.grid.Grid):
    def __init__(self, parent, tableName, popupMenuData):
        wx.grid.Grid.__init__(self, parent, -1)
        self.popupMenuData = popupMenuData
        self.SetRowLabelSize(0)
        self.tableName = tableName
        self.table = MyTable(self.tableName)
        
        for idx, col in enumerate(gridData()[self.tableName][0]):
            self.table.SetColLabelValue(idx, col)
        self.SetTable(self.table, True)
        
#         self.gridPopupMenu = self.createPopupMenu(popupMenuData)
        
#         self.Bind(wx.EVT_CONTEXT_MENU, self.OnShowPopup)
        self.Bind(wx.grid.EVT_GRID_CELL_LEFT_CLICK, self.OnCellLeftClick)
        self.Bind(wx.grid.EVT_GRID_CELL_RIGHT_CLICK, self.OnCellRightClick)
        self.GetGridWindow().Bind(wx.EVT_RIGHT_DOWN, self.OnRightDown)
        self.GetGridWindow().Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown)
        self.Bind(wx.grid.EVT_GRID_LABEL_LEFT_CLICK, self.OnLabelLeftClick)
        
    def OnCellRightClick(self, event):
        
        self.popupMenu = self.createPopupMenu(self.popupMenuData) 
        self.Bind(wx.EVT_CONTEXT_MENU, self.OnShowPopup)
        self.PopupMenu(self.popupMenu) 
        self.popupMenu.Destroy()  
        event.Skip()
    
    def OnRightDown(self, event):
        x, y = self.CalcUnscrolledPosition(event.GetPosition())
        row, col = self.XYToCell(x, y)
        event.Skip()
        
    def OnLeftDown(self, event):
        x, y = self.CalcUnscrolledPosition(event.GetPosition())
        row, col = self.XYToCell(x, y)   
#     b = wx.Button(self, 10, "Default Button", (20, 20))
#         self.Bind(wx.EVT_BUTTON, lambda event: self.OnClick(event, 'somevalue'), b)
# def OnClick(self, event, somearg):
#         self.log.write("Click! (%d)\n" % event.GetId())
        
    def createPopupMenu(self, popupMenuData):
        
        popupmenu = wx.Menu()
        for text in popupMenuData:
            item = popupmenu.Append(-1, text)
            self.Bind(wx.EVT_MENU, self.OnPopupItemSelected, item)
        return popupmenu
        
    def OnShowPopup(self, event):
        pass
#         print('OnShowPopup')
#         pos = event.GetPosition()
#         self.pos = self.ScreenToClient(pos)
#         self.PopupMenu(self.gridPopupMenu, self.pos)
#         print(self.pos, self.myGrid.XYToCell(x, y))
    
    def OnPopupItemSelected(self, event):
        itemText = self.popupMenu.FindItemById(event.GetId()).GetText()
        action = itemText.split()
        if action[0] == 'Add':
            addDialog = ActionDialog(action[1])
            result = addDialog.ShowModal()
            if result == wx.ID_OK:
                if self.tableName == 'currency':
                    
                    for widget in addDialog.widgetList:
                        name = widget.GetName()
                        if name == 'fullname':
                            fullName = widget.GetValue()
                        if name == 'shortname':    
                            shortName = widget.GetValue()
                        if name == 'code':    
                            code = widget.GetValue()
                    
                    maxId = DBData.getMaxID(self.tableName)
                    

                    DBData.insertRow(self.tableName, (maxId+1, fullName, shortName, code))
                    DBData.commit()
            
            addDialog.Destroy()     
        elif action[0] == 'Edit':
            pass
        elif action[0] == 'Delete':
            pass
        
        self.table.selection = self.table.data.selectRows(self.tableName)
#         self.table.nrows = len(self.table.selection)
        self.Reset()
        
    def OnCellLeftClick(self, event):
        self.ClearSelection()
        row = event.GetRow()
        self.SelectRow(row)
        
    def OnLabelLeftClick(self, event):
        pass

    def delete(self):
        if self.table.GetNumberRows() > 0:
            rows = list(range(self.GetNumberRows()))
            self.table.DeleteRows(rows)
            self.Reset()

    def Reset(self):
        """reset the view based on the data in the table.  Call
        this when rows are added or destroyed"""
        self.table.ResetView(self)
#     def OnLabelLeftDClick(self, event):
#         dlg = MyDialog()
#         dlg.ShowModal()
#         dlg.Destroy()
    
class Data():
    def __init__(self):
        self.con = sqlite3.connect('data/fatwallet.db')
        self.cursor = self.con.cursor()
#         self.tableName = tableName
#         self.dataTable = gridData()[self.tableName]
        self.cols = []
#         self.ncols = len(self.cols)
        self.ncols = 0
        self.nrows = 0
    
    def GetColNumber(self, tableName):
        dataTable = gridData()[tableName]
        self.cols = dataTable[0]
        return len(self.cols)
    
    def GetRowNumber(self, tableName):
        self.selectRows(tableName)
        return self.nrows
    
#     def selectRows(self, tableName, cond='all', **args): 
    def selectRows(self, tableName, flag='all', args=''): 
        '''
        Selects rows from table, cond detects what part of selection we need
        '''
        dataTable = gridData()[tableName]
        query = dataTable[1][flag]
        #print(self.dataTable[1]['all'])
        query = query + args
        print(query)
#             for key in args:
#                 if cond == 'filter':
#                     if args[key] is not None:
#                         query = query + ' ' + key + '=' + str(args[key])
#                     else:
#                         query = query + ' ' + key + ' is null'
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        self.nrows = len(rows) 
        return rows
    
    def getMaxID(self, tableName):
        return self.selectRows(tableName, 'id')[0][0]
    
    def insertRow(self, tableName, cols):
        dataTable = gridData()[tableName]
        self.cursor.execute(dataTable[2], cols)
        
    def updateRow(self, tableName, cols):
        dataTable = gridData()[tableName]
        self.cursor.execute(dataTable[3], cols)
        
    def deleteRow(self, tableName, id):
        dataTable = gridData()[tableName]
        self.cursor.execute(dataTable[4], (id,))
            
    def commit(self):
        self.con.commit()
        
class MyTable(wx.grid.GridTableBase):
    def __init__(self, tableName):
        wx.grid.GridTableBase.__init__(self)
        self.tableName = tableName
        self.data = DBData
        self.selection = self.data.selectRows(self.tableName) 
        self.nrows = self.data.GetRowNumber(self.tableName)
        self.ncols = self.data.GetColNumber(self.tableName)        
    
    def GetNumberRows(self):
        return self.data.GetRowNumber(self.tableName)
    
    def GetNumberCols(self):
        return self.data.GetColNumber(self.tableName)
    
    def IsEmptyCell(self, row, col):
        if self.GetNumberRows() > 0:
            return self.selection[row][col] is not None
        else: return True
    
    def GetValue(self, row, col):
        value = None
        if self.GetNumberRows() > 0: 
            value = str(self.selection[row][col])
        
        if value is None:
            return ''
        else:
            return value

    def SetValue(self, row, col, value):
#         self.data[row][col] = value
        self.selection[row][col] = value
        
    def GetColLabelValue(self, col):
        self.data.GetColNumber(self.tableName)
        return self.data.cols[col]
    
    def DeleteRows(self, rows):
        """
        rows -> delete the rows from the dataset
        rows hold the row indices
        """
        deleteCount = 0
        rows = rows[:]
        rows.sort()
 
        for i in rows:
            self.selection.pop(i-deleteCount)
            # we need to advance the delete count
            # to make sure we delete the right rows
            deleteCount += 1
       
    def ResetView(self, grid):
        """
        (Grid) -> Reset the grid view.   Call this to
        update the grid if rows and columns have been added or deleted
        """
        print('ResetView called', self.nrows)
        grid.BeginBatch()
 
        for current, new, delmsg, addmsg in [
            (self.nrows, self.GetNumberRows(), wx.grid.GRIDTABLE_NOTIFY_ROWS_DELETED, wx.grid.GRIDTABLE_NOTIFY_ROWS_APPENDED),
            (self.ncols, self.GetNumberCols(), wx.grid.GRIDTABLE_NOTIFY_COLS_DELETED, wx.grid.GRIDTABLE_NOTIFY_COLS_APPENDED),
        ]:
            if new < current:
                msg = wx.grid.GridTableMessage(self,delmsg,new,current-new)
                grid.ProcessTableMessage(msg)
            elif new > current:
                msg = wx.grid.GridTableMessage(self,addmsg,new-current)
                grid.ProcessTableMessage(msg)
                self.UpdateValues(grid)
 
        grid.EndBatch()

        self.nrows = self.GetNumberRows()
        self.ncols = self.GetNumberCols()     
        
        grid.AdjustScrollbars()
        grid.ForceRefresh()

class ActionDialog(wx.Dialog):
    def __init__(self, tableName):
        wx.Dialog.__init__(self, None, -1, "Test", style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER, size=(400,500))
        self.widgetList = []
#         self.data = DBData()
#         StatTxtStyle = wx.ALIGN_RIGHT|wx.ALIGN_CENTER|wx.TOP|wx.LEFT|wx.BOTTOM
#         if tableName == 'currency':
#             sizerV = wx.BoxSizer(wx.VERTICAL)
#             self.fullName = wx.StaticText(self, -1, 'Full Name', 0, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER|wx.TOP|wx.LEFT|wx.BOTTOM), 
#                             (wx.TextCtrl, '', 0, 0, wx.ALIGN_LEFT|wx.EXPAND|wx.ALL)
#                             ),
#                         ((wx.StaticText, 'Short name', 0, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER|wx.TOP|wx.LEFT|wx.BOTTOM), 
#                             (wx.TextCtrl, '', 0, 0, wx.ALIGN_LEFT|wx.EXPAND|wx.ALL)
#                             ),
#                         ((wx.StaticText, 'Code', 0, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER|wx.TOP|wx.LEFT|wx.BOTTOM), 
#                             (wx.TextCtrl, '', 0, 0, wx.ALIGN_LEFT|wx.EXPAND|wx.ALL)
#                             ),    
#                         ((wx.Button, 'Ok', 0, 0, wx.ALIGN_LEFT|wx.ALL, 'ok'), 
#                          (wx.Button, 'Cancel', 0, 0, wx.ALIGN_LEFT|wx.ALL, 'cancel'))
#             self.SetSizer(sizerV)
#             sizerV.Fit(self)
#         elif tableName == 'account':
#             pass
#         elif tableName == 'organization':
#             pass
#         elif tableName == 'item':
#             pass
#         elif tableName == 'payment':
#             pass
#         elif tableName == 'income':
#             pass
        
        
        def createCtrl(el):
            if el[0] == wx.ComboBox:
                ctrl = el[0](self, -1, el[1], choices=el[6], style=el[2], name=el[5]) # creates an instance of one of controls
            elif el[0] == wx.Button or el[0] == wx.TextCtrl: 
                ctrl = el[0](self, -1, el[1], style=el[2], name=el[5])
            else:
                ctrl = el[0](self, -1, el[1], style=el[2])
            return ctrl
                    
        sizerV = wx.BoxSizer(wx.VERTICAL)
        
        ctrlElements = dialogData()[tableName]
        for element in ctrlElements:
            if type(element[0]) == tuple: 
                sizerH = wx.BoxSizer(wx.HORIZONTAL)
                for el in element:
                    ctrl = createCtrl(el)
                    self.widgetList.append(ctrl)
                    if el[0] == wx.ComboBox:
                        objName = ctrl.GetName()
                        if objName == 'account':
                            self.cbAccount = ctrl
                        if objName == 'organization':
                            self.cbOrganization = ctrl
                        if objName == 'category':
                            self.cbCategory = ctrl
                            print('self.cbCategory:', self.cbCategory)
                            self.Bind(wx.EVT_COMBOBOX, lambda event: self.OnCBSelect(event, 'category'), self.cbCategory)
                        if objName == 'item':
                            self.cbItem = ctrl
                            
                    if el[0] == wx.Button:
                        self.Bind(wx.EVT_BUTTON, self.OnClickButton, ctrl)  
                    sizerH.Add(ctrl, el[3], el[4], 10)
                sizerV.Add(sizerH, 0, wx.EXPAND)
            else:
                ctrl = createCtrl(element) # creates an instance of one of controls 
                self.widgetList.append(ctrl)
                sizerV.Add(ctrl, element[3], element[4], 10)
        self.SetSizer(sizerV)
        sizerV.Fit(self)
        
    def OnClickButton(self, event):
        but = event.GetEventObject().GetName()
        code = wx.ID_CANCEL
        if but == 'ok':
            code = wx.ID_OK

        self.EndModal(code)
        
    def OnCBSelect(self, event, tableName):
        object = event.GetEventObject()
        objectText = object.GetString(object.GetSelection())
        if tableName == 'category':
            selection = DBData.selectRows('item', " where CategoryID = (select CategoryId from category where Name='%s')" % objectText)
            self.cbItem.Clear()
            self.cbItem.Append([item[1] for item in selection if item[1] is not None])
         
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
    
DBData = Data()
           
if __name__ == '__main__':
    app = wx.App()
    frame = MainFrame(None)
    frame.Show(True)
    #app.SetTopWindow(frame)
    app.MainLoop()