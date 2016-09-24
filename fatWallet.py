import wx
import wx.grid
import wx.adv 
import sqlite3
from wx.lib.pubsub import pub 
import os
from datetime import datetime
from wx.lib.masked import NumCtrl 
import wx.lib.agw.piectrl as PC

imgFolder = os.getcwd() + '\\img\\'

gridLabelColor = wx.Colour(154,207,227) #'#4f3856'
gridCellColor = wx.Colour(228,232,233)

def gridData():
    return {'category': (('CategoryId', 'Name', 'ParentId'),
                           {'all':'select CategoryId, Name, ParentId from category order by 2',
                            'id':'select max(CategoryId) from category',
                            'filter':'select CategoryId, Name from category '},
                           'insert into category values (?, ?, ?)',
                           'update category set Name=?, ParentId=? where CategoryId=?',
                           'delete from category where CategoryId=?'),
            'item': (('Name', 'Category'),
                           {'all':'select i.ItemId, i.Name, \
                               (select c.Name from category c where c.CategoryId = i.CategoryId) from item i order by 2', 
                               'id': 'select max(ItemId) from item',
                               'filter': 'select i.ItemId, i.Name, \
                               (select c.Name from category c where c.CategoryId = i.CategoryId) from item i',
                               'recursive': 'with recursive tree as ( \
                                                select CategoryId from category\
                                                where CategoryId = ? \
                                                union all \
                                                select category.CategoryId \
                                                from category \
                                                join tree on category.ParentId = tree.CategoryId\
                                                )\
                                            select i.ItemId, i.Name, \
                               (select c.Name from category c where c.CategoryId = i.CategoryId) from item i \
                                            where i.CategoryId in tree'
                               },
                           'insert into item values (?, ?, ?)',
                           'update item set Name=?, CategoryId=? where ItemId=?',
                           'delete from item where ItemId=?') ,
            'account': (('Name', 'Currency'),
                           {'all':'select AccountId, Name, \
                               (select c.ShortName from currency c where c.CurrencyId=a.CurrencyId) from account a order by 2', 
                            'id':'select max(AccountId) from account ', 
                            'filter': 'select AccountId, Name, \
                               (select c.ShortName from currency c where c.CurrencyId=a.CurrencyId) from account a '},
                           'insert into account values (?, ?, ?)',
                           'update account set Name=?, CurrencyId=? where AccountId=?',
                           'delete from account where AccountId=?'),
            'currency': (('Short Name', 'Full Name', 'Code'),
                           {'all':'select CurrencyId, ShortName, FullName, Code from currency order by 2', 
                            'id': 'select max(CurrencyId) from currency',
                            'filter': 'select * from currency '},
                           'insert into currency values (?, ?, ?, ?)',
                           'update currency set ShortName=?, FullName=?, Code=? where CurrencyId=?',
                           'delete from currency where CurrencyId=?'),
            'organization': (('Name',),
                           {'all':'select OrganizationId, Name from organization order by 2', 
                            'id':'select max(OrganizationId) from organization',
                            'filter': 'select OrganizationId, Name from organization '},
                           'insert into organization values (?, ?)',
                           'update organization set Name=? where OrganizationId=?',
                           'delete from organization where OrganizationId=?'), 
            'payment': (('PayDate', 'Account', 'Organization', 'Category', 'Item', 'Price', 'Count', 'Total'), # %H:%M:%S
                           {'all':"select e.PaymentId, strftime('%d.%m.%Y', PayDate), \
                           (select a.Name from account a where a.AccountId = e.AccountId),\
                           (select o.Name from organization o where o.OrganizationId = e.OrganizationId), \
                           (select c.Name from category c, item i where c.CategoryId = i.CategoryId and i.ItemId = e.ItemId), \
                           (select i.Name from item i where i.ItemId = e.ItemId),\
                           Price, Count, Total\
                           from payment e order by 2", 
                           'id': 'select max(PaymentId) from payment',
                           'filter': "select e.PaymentId, strftime('%d.%m.%Y', PayDate), \
                           (select a.Name from account a where a.AccountId = e.AccountId),\
                           (select o.Name from organization o where o.OrganizationId = e.OrganizationId), \
                           (select c.Name from category c, item i where c.CategoryId = i.CategoryId and i.ItemId = e.ItemId), \
                           (select i.Name from item i where i.ItemId = e.ItemId),\
                           Price, Count, Total from payment e "},
                           'insert into payment values (?, ?, ?, ?, ?, ?, ?, ?)',
                           'update payment set PayDate=?, AccountId=?, ItemId=?, Price=?, Count=?, Total=?, OrganizationId=? where PaymentId=?',
                           'delete from payment where PaymentId=?'), 
            'income': (('IncomeDate', 'Account', 'Organization', 'Category', 'Item', 'Amount'), # %H:%M:%S
                           {'all':"select IncomeId, strftime('%d.%m.%Y', IncomeDate), \
                           (select a.Name from account a where a.AccountId = e.AccountId),\
                           (select o.Name from organization o where o.OrganizationId = e.OrganizationId), \
                           (select c.Name from category c, item i where c.CategoryId = i.CategoryId and i.ItemId = e.ItemId), \
                           (select i.Name from item i where i.ItemId = e.ItemId),\
                           Amount from income e order by 2", 
                           'id': 'select max(IncomeId) from income',
                           'filter': "select IncomeId, strftime('%d.%m.%Y', IncomeDate), \
                           (select a.Name from account a where a.AccountId = e.AccountId),\
                           (select o.Name from organization o where o.OrganizationId = e.OrganizationId), \
                           (select c.Name from category c, item i where c.CategoryId = i.CategoryId and i.ItemId = e.ItemId), \
                           (select i.Name from item i where i.ItemId = e.ItemId),\
                           Amount from income e "},
                           'insert into income values (?, ?, ?, ?, ?, ?)',
                           'update income set IncomeDate=?, AccountId=?, ItemId=?, OrganizationId=?, Amount=? where IncomeId=?'
                           'delete from income where IncomeId=?'), 

            }

def makeChoice(tableName):
    selection = DBData.selectRows(tableName)
    return [(item[0], item[1]) for item in selection if item[1] is not None]  #if item[1] is not None else '' 

def dialogData():  
    """
        Structure: 
        { dialog name: ((what kind of element to add, label, style, proportion, flags, name, choice))
        }
    """
    return {'payment': (
                        ((wx.StaticText, 'Date', 0, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER|wx.TOP|wx.LEFT|wx.BOTTOM), 
                            (wx.adv.DatePickerCtrl, wx.DateTime().Now(), wx.adv.DP_DEFAULT|wx.adv.DP_SHOWCENTURY|wx.adv.DP_DROPDOWN, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 'datectrl'), 
                            (wx.StaticText, 'Account', 0, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER|wx.TOP|wx.LEFT|wx.BOTTOM), 
                            (wx.ComboBox, 'Select account...', wx.CB_DROPDOWN, 1, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT|wx.ALL,  'account', NotEmptyValidator(), makeChoice('account')),
                            (wx.BitmapButton, 'dict.png', 0, 0, wx.ALIGN_LEFT|wx.TOP|wx.BOTTOM|wx.RIGHT, 'accdict')
                            ), 
                        ((wx.StaticText, 'Organization', 0, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER|wx.TOP|wx.LEFT|wx.BOTTOM), 
                            (wx.ComboBox, 'Select organization...', wx.CB_DROPDOWN, 1, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT|wx.ALL, 'organization', NotEmptyValidator(), makeChoice('organization')),
                            (wx.BitmapButton, 'dict.png', 0, 0, wx.ALIGN_LEFT|wx.TOP|wx.BOTTOM|wx.RIGHT, 'orgdict')
                            ),
                        ((wx.StaticText, 'Category', 0, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER|wx.TOP|wx.LEFT|wx.BOTTOM), 
                            (wx.ComboBox, 'Select category...', wx.CB_DROPDOWN, 1, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 'categoryitem', wx.DefaultValidator, makeChoice('category')),
                            (wx.BitmapButton, 'dict.png', 0, 0, wx.ALIGN_LEFT|wx.TOP|wx.BOTTOM|wx.RIGHT, 'catdict')
                            ),
                        ((wx.StaticText, 'Item', 0, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER|wx.TOP|wx.LEFT|wx.BOTTOM), 
                            (wx.ComboBox, 'Select item...', wx.CB_DROPDOWN, 1, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 'item', NotEmptyValidator(), makeChoice('item')),
                            (wx.BitmapButton, 'dict.png', 0, 0, wx.ALIGN_LEFT|wx.TOP|wx.BOTTOM|wx.RIGHT, 'itemdict')
                            ),
                        ((wx.StaticText, 'Price', 0, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER|wx.TOP|wx.LEFT|wx.BOTTOM), 
                            (NumCtrl, 0, 0, 0, wx.ALIGN_LEFT|wx.EXPAND|wx.ALL, 'price', wx.DefaultValidator), 
                            (wx.StaticText, 'Count', 0, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER|wx.TOP|wx.LEFT|wx.BOTTOM), 
                            (NumCtrl, 0, 0, 0, wx.ALIGN_LEFT|wx.EXPAND|wx.ALL, 'count', wx.DefaultValidator)
                            ),
                        ((wx.StaticText, 'Total', 0, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER|wx.TOP|wx.LEFT|wx.BOTTOM), 
                            (NumCtrl, 0, 0, 0, wx.ALIGN_LEFT|wx.EXPAND|wx.ALL, 'total', NotZeroValidator())
                            ),    
                        ((wx.Button, 'Ok', wx.ID_OK, 0, wx.ALIGN_LEFT|wx.ALL, 'ok'), 
                         (wx.Button, 'Cancel', wx.ID_CANCEL, 0, wx.ALIGN_LEFT|wx.ALL, 'cancel'))
                        ),
            'currency': (
                        ((wx.StaticText, 'Full Name', 0, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER|wx.TOP|wx.LEFT|wx.BOTTOM), 
                            (wx.TextCtrl, '', 0, 0, wx.ALIGN_LEFT|wx.EXPAND|wx.ALL, 'fullname', wx.DefaultValidator)
                            ),
                        ((wx.StaticText, 'Short name', 0, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER|wx.TOP|wx.LEFT|wx.BOTTOM), 
                            (wx.TextCtrl, '', 0, 0, wx.ALIGN_LEFT|wx.EXPAND|wx.ALL, 'shortname', NotEmptyValidator())
                            ),
                        ((wx.StaticText, 'Code', 0, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER|wx.TOP|wx.LEFT|wx.BOTTOM), 
                            (wx.TextCtrl, '', 0, 0, wx.ALIGN_LEFT|wx.EXPAND|wx.ALL, 'code', wx.DefaultValidator)
                            ),    
                        ((wx.Button, 'Ok', wx.ID_OK, 0, wx.ALIGN_LEFT|wx.ALL, 'ok'), 
                         (wx.Button, 'Cancel', wx.ID_CANCEL, 0, wx.ALIGN_LEFT|wx.ALL, 'cancel'))
                        ),
            'account': (
                        ((wx.StaticText, 'Name', 0, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER|wx.TOP|wx.LEFT|wx.BOTTOM), 
                            (wx.TextCtrl, '', 0, 1, wx.ALIGN_LEFT|wx.EXPAND|wx.ALL, 'account', NotEmptyValidator())
                            ),
                        ((wx.StaticText, 'Currency', 0, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER|wx.TOP|wx.LEFT|wx.BOTTOM), 
                            (wx.ComboBox, 'Select currency...', wx.CB_DROPDOWN, 1, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT|wx.ALL,  'currency', NotEmptyValidator(), makeChoice('currency')),
                            (wx.BitmapButton, 'dict.png', 0, 0, wx.ALIGN_LEFT|wx.TOP|wx.BOTTOM|wx.RIGHT, 'curdict')
                            ),
                        ((wx.Button, 'Ok', wx.ID_OK, 0, wx.ALIGN_LEFT|wx.ALL, 'ok'), 
                         (wx.Button, 'Cancel', wx.ID_CANCEL, 0, wx.ALIGN_LEFT|wx.ALL, 'cancel'))
                        ),
            'item': (
                        ((wx.StaticText, 'Name', 0, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER|wx.TOP|wx.LEFT|wx.BOTTOM), 
                            (wx.TextCtrl, '', 0, 0, wx.ALIGN_LEFT|wx.EXPAND|wx.ALL, 'item', NotEmptyValidator())
                            ),
                        ((wx.StaticText, 'Category', 0, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER|wx.TOP|wx.LEFT|wx.BOTTOM), 
                            (wx.ComboBox, 'Select category...', wx.CB_DROPDOWN, 1, wx.ALIGN_LEFT|wx.EXPAND|wx.ALL,  'category', NotEmptyValidator(), makeChoice('category')),
                            (wx.BitmapButton, 'dict.png', 0, 0, wx.ALIGN_LEFT|wx.TOP|wx.BOTTOM|wx.RIGHT, 'catdict')
                            ),
                        ((wx.Button, 'Ok', wx.ID_OK, 0, wx.ALIGN_LEFT|wx.ALL, 'ok'), 
                         (wx.Button, 'Cancel', wx.ID_CANCEL, 0, wx.ALIGN_LEFT|wx.ALL, 'cancel'))
                        ),
            'category': (
                        ((wx.StaticText, 'Name', 0, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER|wx.TOP|wx.LEFT|wx.BOTTOM), 
                            (wx.TextCtrl, '', 0, 0, wx.ALIGN_LEFT|wx.EXPAND|wx.ALL, 'category', NotEmptyValidator())
                            ),
                        ((wx.Button, 'Ok', wx.ID_OK, 0, wx.ALIGN_LEFT|wx.ALL, 'ok'), 
                         (wx.Button, 'Cancel', wx.ID_CANCEL, 0, wx.ALIGN_LEFT|wx.ALL, 'cancel'))
                        ),
            'organization': (
                        ((wx.StaticText, 'Name', 0, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER|wx.TOP|wx.LEFT|wx.BOTTOM), 
                            (wx.TextCtrl, '', 0, 0, wx.ALIGN_LEFT|wx.EXPAND|wx.ALL, 'organization', NotEmptyValidator())
                            ),
                        ((wx.Button, 'Ok', wx.ID_OK, 0, wx.ALIGN_LEFT|wx.ALL, 'ok'), 
                         (wx.Button, 'Cancel', wx.ID_CANCEL, 0, wx.ALIGN_LEFT|wx.ALL, 'cancel'))
                        ),
            'income': (
                        ((wx.StaticText, 'Date', 0, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER|wx.TOP|wx.LEFT|wx.BOTTOM), 
                            (wx.adv.DatePickerCtrl, wx.DateTime().Now(), wx.adv.DP_DROPDOWN, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 'datectrl'), 
                            (wx.StaticText, 'Account', 0, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER|wx.TOP|wx.LEFT|wx.BOTTOM), 
                            (wx.ComboBox, 'Select account...', wx.CB_DROPDOWN, 1, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT|wx.ALL,  'account', NotEmptyValidator(), makeChoice('account')),
                            (wx.BitmapButton, 'dict.png', 0, 0, wx.ALIGN_LEFT|wx.TOP|wx.BOTTOM|wx.RIGHT, 'accdict')
                            ), 
                        ((wx.StaticText, 'Organization', 0, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER|wx.TOP|wx.LEFT|wx.BOTTOM), 
                            (wx.ComboBox, 'Select organization...', wx.CB_DROPDOWN, 1, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT|wx.ALL, 'organization', NotEmptyValidator(), makeChoice('organization')),
                            (wx.BitmapButton, 'dict.png', 0, 0, wx.ALIGN_LEFT|wx.TOP|wx.BOTTOM|wx.RIGHT, 'orgdict')
                            ),
                        ((wx.StaticText, 'Category', 0, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER|wx.TOP|wx.LEFT|wx.BOTTOM), 
                            (wx.ComboBox, 'Select category...', wx.CB_DROPDOWN, 1, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 'categoryitem', NotEmptyValidator(), makeChoice('category')),
                            (wx.BitmapButton, 'dict.png', 0, 0, wx.ALIGN_LEFT|wx.TOP|wx.BOTTOM|wx.RIGHT, 'catdict')
                            ),
                        ((wx.StaticText, 'Item', 0, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER|wx.TOP|wx.LEFT|wx.BOTTOM), 
                            (wx.ComboBox, 'Select item...', wx.CB_DROPDOWN, 1, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 'item', NotEmptyValidator(), makeChoice('item')),
                            (wx.BitmapButton, 'dict.png', 0, 0, wx.ALIGN_LEFT|wx.TOP|wx.BOTTOM|wx.RIGHT, 'itemdict')
                            ),
                        ((wx.StaticText, 'Amount', 0, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER|wx.TOP|wx.LEFT|wx.BOTTOM), 
                            (wx.TextCtrl, '', 0, 0, wx.ALIGN_LEFT|wx.EXPAND|wx.ALL, 'amount', NotEmptyValidator())
                            ),    
                        ((wx.Button, 'Ok', wx.ID_OK, 0, wx.ALIGN_LEFT|wx.ALL, 'ok'), 
                         (wx.Button, 'Cancel', wx.ID_CANCEL, 0, wx.ALIGN_LEFT|wx.ALL, 'cancel'))
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
#                             (wx.ComboBox, 'Select account...', wx.CB_DROPDOWN, 1, wx.ALIGN_LEFT|wx.EXPAND|wx.ALL,  'account', NotEmptyValidator(), makeChoice('account'))
#                             ), 
#                         ((wx.StaticText, 'Organization', 0, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER|wx.TOP|wx.LEFT|wx.BOTTOM), 
#                             (wx.ComboBox, 'Select organization...', wx.CB_DROPDOWN, 1, wx.ALIGN_LEFT|wx.EXPAND|wx.ALL, 'organization', NotEmptyValidator(), makeChoice('organization'))
#                             ),
#                         ((wx.StaticText, 'Category', 0, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER|wx.TOP|wx.LEFT|wx.BOTTOM), 
#                             (wx.ComboBox, 'Select category...', wx.CB_DROPDOWN, 1, wx.ALIGN_LEFT|wx.EXPAND|wx.ALL, 'category', NotEmptyValidator(), makeChoice('category'))
#                             ),
#                         ((wx.StaticText, 'Item', 0, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER|wx.TOP|wx.LEFT|wx.BOTTOM), 
#                             (wx.ComboBox, 'Select item...', wx.CB_DROPDOWN, 1, wx.ALIGN_LEFT|wx.EXPAND|wx.ALL, 'item', NotEmptyValidator(), makeChoice('item'))
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
#                             (wx.ComboBox, 'Select currency...', wx.CB_DROPDOWN, 1, wx.ALIGN_LEFT|wx.EXPAND|wx.ALL,  'currency', NotEmptyValidator(), makeChoice('account'))
#                             ),
#                         ((wx.Button, 'Ok', 0, 0, wx.ALIGN_LEFT|wx.ALL, 'ok'), 
#                          (wx.Button, 'Cancel', 0, 0, wx.ALIGN_LEFT|wx.ALL, 'cancel'))
#                         ),
#             'item': (
#                         ((wx.StaticText, 'Name', 0, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER|wx.TOP|wx.LEFT|wx.BOTTOM), 
#                             (wx.TextCtrl, '', 0, 0, wx.ALIGN_LEFT|wx.EXPAND|wx.ALL)
#                             ),
#                         ((wx.StaticText, 'Currency', 0, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER|wx.TOP|wx.LEFT|wx.BOTTOM), 
#                             (wx.ComboBox, 'Select currency...', wx.CB_DROPDOWN, 1, wx.ALIGN_LEFT|wx.EXPAND|wx.ALL,  'currency', NotEmptyValidator(), makeChoice('account'))
#                             ),
#                         ((wx.Button, 'Ok', 0, 0, wx.ALIGN_LEFT|wx.ALL, 'ok'), 
#                          (wx.Button, 'Cancel', 0, 0, wx.ALIGN_LEFT|wx.ALL, 'cancel'))
#                         ),
#             'category': (
#                         ((wx.StaticText, 'Name', 0, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER|wx.TOP|wx.LEFT|wx.BOTTOM), 
#                             (wx.TextCtrl, '', 0, 0, wx.ALIGN_LEFT|wx.EXPAND|wx.ALL)
#                             ),
#                         ((wx.StaticText, 'Currency', 0, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER|wx.TOP|wx.LEFT|wx.BOTTOM), 
#                             (wx.ComboBox, 'Select currency...', wx.CB_DROPDOWN, 1, wx.ALIGN_LEFT|wx.EXPAND|wx.ALL,  'currency', NotEmptyValidator(), makeChoice('account'))
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
                ("Income", imgFolder+"incomes.png", "Add income", self.OnEvent),
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
#         mainSizer = wx.GridBagSizer(hgap=2, vgap=2)
#         
#         grid = MyGrid(self, 'payment', gridPopupMenuData('payment'))
#         grid.SetLabelBackgroundColour(gridLabelColor)
#         grid.SetDefaultCellBackgroundColour(gridCellColor)
#         mainSizer.Add(grid, pos=(0,1), flag=wx.EXPAND)
#         
#         button = wx.Button(self)
#         mainSizer.Add(button, pos=(1,0),  flag=wx.EXPAND)
#         
#         mainSizer.AddGrowableRow(1)
#         mainSizer.AddGrowableCol(1)
#         self.SetSizer(mainSizer)
        
        
        myPie = PC.PieCtrl(self, -1, pos=(0,100), size=wx.Size(300,540))
        myPie.SetAngle(0.3)
#         mypie.SetBackColour('red')
        myPie.SetShowEdges(False)
        myPie.SetHeight(30)
        myPieLeg = myPie.GetLegend()
#         myPieLeg.SetBackColour('green')
#         myPieLeg.SetLabelColour('purple')
        myPieLeg.SetTransparent(True)
#         myPieLeg.SetPosition((0,500))
#         myPieLeg.SetLabelFont(wx.Font(wx.FontInfo(10).Bold() ))
        
        
        part = PC.PiePart(300, wx.Colour(200, 50, 50), "Label 1")
        myPie._series.append(part)
        
        part = PC.PiePart(300, wx.Colour(200, 200, 50), "Label 2")
        myPie._series.append(part)
        
        part = PC.PiePart(300, wx.Colour(200, 200, 200), "Label 3")
        myPie._series.append(part)
        
        mainSizer = wx.BoxSizer(wx.HORIZONTAL)
        mainSizer.Add(myPie, 0, wx.EXPAND|wx.ALL, 5)
        self.SetSizer(mainSizer)
    

def treePopupMenuData(tableName):
    return ('Add %s' % tableName, 'Rename %s' % tableName, 'Remove %s' % tableName, 'Sort children')

def gridPopupMenuData(tableName):
    return {1:'Add %s' % tableName, 2:'Edit %s' % tableName, 3:'Delete %s' % tableName}

class CategoryDialog(wx.Dialog):
    #----------------------------------------------------------------------
    def __init__(self):
        wx.Dialog.__init__(self, None, wx.ID_ANY, "Categories and items", style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER, size=(700,500))
        self.panel = wx.Panel(self)
        catLabel = wx.StaticText(self.panel, -1, 'Categories')
        self.tableName = 'category'
        self.selection = DBData.selectRows(self.tableName) 
        
        self.createTree()
        self.treePopupMenu = self.createPopupMenu(treePopupMenuData)
        
        
        
        itemLabel = wx.StaticText(self.panel, -1, 'Items')
#         gridPanel = wx.Panel(self.panel, style=wx.SUNKEN_BORDER)
        self.itemGrid = MyGrid(self.panel, 'item', gridPopupMenuData('item'))
        self.itemGrid.SetLabelBackgroundColour(gridLabelColor)
        self.itemGrid.SetDefaultCellBackgroundColour(gridCellColor)
        self.itemGrid.SetCellHighlightPenWidth(0) 
        self.itemGrid.Fit()
        
        closeBtn = wx.Button(self.panel, label="Close")
        closeBtn.Bind(wx.EVT_BUTTON, self.onSendAndClose)

        buts = ActionButtons(self.panel, self.tableName, self.itemGrid)
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
        itemSizer.Add(self.itemGrid, 1, wx.ALL|wx.EXPAND, 10)
        itemSizer.Add(closeBtn, 0, wx.ALL|wx.RIGHT, 10)
        mainSizer.Add(itemSizer, 1, wx.EXPAND)
        mainSizer.Add(buts.actionSizer, 0, wx.ALL, 10)
        
        self.panel.SetSizer(mainSizer)
    
    def createTree(self):
        self.tree = wx.TreeCtrl(self.panel, -1, size=(250,200), style=wx.TR_DEFAULT_STYLE | wx.TR_EDIT_LABELS)
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
            item = popupmenu.Append(-1, text)
            self.Bind(wx.EVT_MENU, self.OnPopupItemSelected, item)
        return popupmenu
        
    def OnShowPopup(self, event):
        pos = event.GetPosition()
        self.pos = self.tree.ScreenToClient(pos)
        self.tree.PopupMenu(self.treePopupMenu, self.pos)
    
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
#             print(selItem)
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
#         print('OnSelectChange')
        self.tree.SetItemText(self.root, 'All categories')
        self.itemGrid.ClearGrid()
        treeItem = event.GetItem()
#         print('treeItem', self.tree.GetItemText(treeItem))
#         if self.tree.GetItemData(treeItem) is not None: # if a tree item doesn't have DB ID, than it's a new one and no need to select anything
        if treeItem == self.root:
            self.itemGrid.table.data = DBData.selectRows('item')
            self.itemGrid.selectionFlag = 'all'
            self.itemGrid.selectionArgs = ''
        else:
            if treeItem is not None and self.tree.GetItemData(treeItem) is not None:  # if a tree item doesn't have DB ID, than it's a new one and no need to select anything
                catItemId = self.tree.GetItemData(treeItem)
                
#                 self.itemGrid.table.selection = self.data.selectRows('item', cond='filter', CategoryId=catItemId)
                self.itemGrid.table.data = DBData.selectRows('item', 'recursive', (str(catItemId),))
            self.itemGrid.selectionFlag = 'recursive'
            self.itemGrid.selectionArgs = (str(catItemId),)
        self.itemGrid.Reset()
#         self.itemGrid.Refresh()
            
    def OnEndLabelEdit(self, event):
        treeItem = event.GetItem()
        print('treeItem', treeItem)
        label = ''
        if len(event.GetLabel().strip()) != 0: 
            label = event.GetLabel().strip() 
        elif len(self.tree.GetItemText(treeItem).strip()) != 0:
            label = self.tree.GetItemText(treeItem).strip()
        if label != '': 
            if self.tree.GetItemData(treeItem) is None: # if an item doesn't have DB ID, than it's a new one       
                # add item
                #if event.GetId() > 0:
    #             popupMenuText = self.popupmenu.FindItemById(event.GetId()).GetText()
    #             print('popupText:', popupMenuText)
                
                
    #             if popupMenuText == 'Add category':
                maxId = DBData.getMaxID(self.tableName) 
                
                parentItemData = self.tree.GetItemData(self.tree.GetItemParent(treeItem))
                if parentItemData == 'root':
                    parentId = None
                else: parentId = parentItemData
                DBData.insertRow(self.tableName, (maxId+1, label, parentId))
                DBData.commit()
                self.OnSelChanged(event)
            elif self.tree.GetItemData(treeItem) != 'root':
                categoryId = self.tree.GetItemData(treeItem)
                parentItemData = self.tree.GetItemData(self.tree.GetItemParent(treeItem))
                if parentItemData == 'root':
                    parentId = None
                else: parentId = parentItemData
                
                DBData.updateRow(self.tableName, (label, parentId, categoryId))
                DBData.commit()
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
    def __init__(self, parent, tableName, grid):
        self.tableName = tableName
        self.grid = grid
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
        self.grid.OpenDialog(1)
    
    def OnEditClick(self, event):
        if self.grid.GetNumberRows() > 0:
            self.grid.OpenDialog(2)
    
    def OnDeleteClick(self, event):
        if self.grid.GetNumberRows() > 0:
            self.grid.OpenDialog(3)
    
class MyDialog(wx.Dialog):
    #----------------------------------------------------------------------
    def __init__(self, table):
        wx.Dialog.__init__(self, None, wx.ID_ANY, table, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER, size=(700,500))
        mainPanel = wx.Panel(self)
#         curLabel = wx.StaticText(self.panel, -1, table)
        self.tableName = table.lower()
        self.data = DBData
        self.selection = self.data.selectRows(self.tableName) 
        
#         curPanel = wx.Panel(mainPanel, style=wx.SUNKEN_BORDER)
#         curPanel.SetBackgroundColour('red')
        self.curGrid = MyGrid(mainPanel, self.tableName, gridPopupMenuData(self.tableName))
        
        self.curGrid.SetLabelBackgroundColour(gridLabelColor)
        self.curGrid.SetDefaultCellBackgroundColour(gridCellColor)
        self.curGrid.SetCellHighlightPenWidth(0) 
#         self.curGrid.Fit()
        
        closeBtn = wx.Button(mainPanel, label="Close")
        closeBtn.Bind(wx.EVT_BUTTON, self.onClose)

        buts = ActionButtons(mainPanel, self.tableName, self.curGrid)
        
        mainSizer = wx.BoxSizer(wx.HORIZONTAL)
        curSizer = wx.BoxSizer(wx.VERTICAL)
#         curSizer.Add(curLabel, 0, wx.LEFT|wx.TOP|wx.RIGHT, 10)
        curSizer.Add(self.curGrid, 1, wx.ALL|wx.EXPAND, 10)
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
        
       # gridPanel = wx.Panel(mainPanel, style=wx.SUNKEN_BORDER)
        self.grid = MyGrid(mainPanel, self.tableName, gridPopupMenuData(self.tableName))
        self.grid.SetLabelBackgroundColour(gridLabelColor)
        self.grid.SetDefaultCellBackgroundColour(gridCellColor)
        self.grid.SetCellHighlightPenWidth(0)  
#         self.grid.Fit()
        
        closeBtn = wx.Button(mainPanel, label="Close")
        self.Bind(wx.EVT_BUTTON, self.onClose, closeBtn)
        
        buts = ActionButtons(mainPanel, self.tableName, self.grid)
          
        self.Bind(wx.EVT_CLOSE, self.onClose)

        mainSizer = wx.BoxSizer(wx.HORIZONTAL)
        gridSizer = wx.BoxSizer(wx.VERTICAL)
        gridSizer.Add(self.grid, 1, wx.ALL|wx.EXPAND, 10)
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
        self.SetRowLabelSize(1)
        self.tableName = tableName
        self.table = MyTable(self.tableName)
        self.selectionFlag = 'all'
        self.selectionArgs = ''
        
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
        self.Bind(wx.grid.EVT_GRID_CELL_LEFT_DCLICK, self.OnCellLeftDClick)
        
    def OnCellRightClick(self, event):
        popupMenu = wx.Menu()
        for key in self.popupMenuData:
            popupMenu.Append(key, self.popupMenuData[key])
            self.Bind(wx.EVT_MENU, self.OnPopupItemSelected, id=key)
#         self.Bind(wx.EVT_CONTEXT_MENU, self.OnShowPopup)
        self.PopupMenu(popupMenu) 
        popupMenu.Destroy()  
        event.Skip()
    
    def OnCellLeftDClick(self, event):
        self.OpenDialog(2)
        event.Skip()
           
    def CalcPosition(self, point): 
        x, y = self.CalcUnscrolledPosition(point)
        self.curRow, self.curCol = self.XYToCell(x, y)
    
    def OnRightDown(self, event):
        self.CalcPosition(event.GetPosition())
        self.SelectRow(self.curRow)
        event.Skip()
        
    def OnLeftDown(self, event):
        self.CalcPosition(event.GetPosition())
        self.SelectRow(self.curRow)
        event.Skip()
        
#     b = wx.Button(self, 10, "Default Button", (20, 20))
#         self.Bind(wx.EVT_BUTTON, lambda event: self.OnClick(event, 'somevalue'), b)
# def OnClick(self, event, somearg):
#         self.log.write("Click! (%d)\n" % event.GetId())
        
#     def createPopupMenu(self):
#         
#         
#         return popupmenu
        
#         print('OnShowPopup')
#         pos = event.GetPosition()
#         self.pos = self.ScreenToClient(pos)
#         self.PopupMenu(self.gridPopupMenu, self.pos)
#         print(self.pos, self.myGrid.XYToCell(x, y))
    
#     def append(self, event):
#         self.table.AppendRow(row)
#         self.Reset()
    def OpenDialog(self, key):
        def getValues(dialog):
            if self.tableName == 'currency':
                for widget in dialog.widgetList:
                    name = widget.GetName()
                    if name == 'fullname':
                        fullName = widget.GetValue()
                    if name == 'shortname':    
                        shortName = widget.GetValue()
                    if name == 'code':    
                        code = widget.GetValue()
                cols = (shortName, fullName, code)
            elif self.tableName == 'account':
                for widget in dialog.widgetList:
                    name = widget.GetName()
                    if name == 'account':
                        accName = widget.GetValue().strip()
                    if name == 'currency':    
                        currencyId = widget.GetClientData(widget.FindString(widget.GetValue()))
                cols = (accName, currencyId)
            elif self.tableName == 'organization':
                for widget in dialog.widgetList:
                    name = widget.GetName()
                    if name == 'organization':
                        orgName = widget.GetValue().strip()
                cols = (orgName,)
            elif self.tableName == 'item':
                for widget in dialog.widgetList:
                    name = widget.GetName()
                    if name == 'item':
                        itemName = widget.GetValue().strip()
                    if name == 'category':    
                        categoryId = widget.GetClientData(widget.FindString(widget.GetValue()))
                cols = (itemName, categoryId)
            elif self.tableName == 'payment':
                for widget in dialog.widgetList:
                    name = widget.GetName()
                    if name == 'datectrl':
                        pickleDate = widget.GetValue()
                        month = pickleDate.GetMonth() + 1
                        day = pickleDate.GetDay()
                        year = pickleDate.GetYear()
                        payDate = datetime(year, month, day)
                    if name == 'account':
                        accountId = widget.GetClientData(widget.FindString(widget.GetValue().strip()))
                    if name == 'organization':    
                        organizationId = widget.GetClientData(widget.FindString(widget.GetValue().strip()))
#                     if name == 'category':  
#                         categoryId = widget.GetClientData(widget.FindString(value))
                    if name == 'item':
                        itemId = widget.GetClientData(widget.FindString(widget.GetValue().strip()))
                    if name == 'price':
                        price = widget.GetValue()
                    if name == 'count':
                        count = widget.GetValue()
                    if name == 'total':
                        total = widget.GetValue()
                cols = (payDate, accountId, itemId,  price, count, total, organizationId)
            elif self.tableName == 'income':
                for widget in dialog.widgetList:
                    name = widget.GetName()
                    if name == 'datectrl':
                        pickleDate = widget.GetValue()
                        month = pickleDate.GetMonth() + 1
                        day = pickleDate.GetDay()
                        year = pickleDate.GetYear()
                        payDate = datetime(year, month, day)
                    if name == 'account':
                        accountId = widget.GetClientData(widget.FindString(widget.GetValue().strip()))
                    if name == 'organization':    
                        organizationId = widget.GetClientData(widget.FindString(widget.GetValue().strip()))
#                     if name == 'category':  
#                         categoryId = widget.GetClientData(widget.FindString(value))
                    if name == 'item':
                        itemId = widget.GetClientData(widget.FindString(widget.GetValue().strip()))
                    if name == 'amount':
                        amount = widget.GetValue()
                cols = (payDate, accountId, organizationId, itemId, amount)
            return cols
                            
        def addData():
            args={}
            if self.tableName == 'item':
                print('self.selectionArgs',self.selectionArgs)
                if len(self.selectionArgs) > 0:
                    catId = self.selectionArgs[0]
                    rows = DBData.selectRows('category', 'filter', ' where CategoryId=%s' % catId)
                    row = rows[0]
                    print('row', row)
                    args = {'category': row[1]}
            addDialog = ActionDialog(self.tableName, args)
            result = addDialog.ShowModal()
            if result == wx.ID_OK:
                maxId = DBData.getMaxID(self.tableName)
                cols = (maxId+1,) + getValues(addDialog)
                self.table.AppendRow(cols)
            addDialog.Destroy()            
        
        def editData():
            dataId = self.table.GetRowLabelValue(self.curRow)
            args = {}
            if self.tableName == 'currency':
                rows = DBData.selectRows(self.tableName, 'filter', ' where CurrencyId=%s' % dataId)
                row = rows[0]
                args = {'shortname': row[1], 'fullname': row[2], 'code': row[3]}
            elif self.tableName == 'account':
                rows = DBData.selectRows(self.tableName, 'filter', ' where AccountId=%s' % dataId)
                row = rows[0]
                args = {'account': row[1], 'currency': row[2]}
            elif self.tableName == 'organization':
                rows = DBData.selectRows(self.tableName, 'filter', ' where OrganizationId=%s' % dataId)
                row = rows[0]
                args = {'organization': row[1]}
            elif self.tableName == 'item':
                rows = DBData.selectRows(self.tableName, 'filter', ' where ItemId=%s' % dataId)
                row = rows[0]
                args = {'item': row[1], 'category': row[2]}
            elif self.tableName == 'payment':
                rows = DBData.selectRows(self.tableName, 'filter', ' where PaymentId=%s' % dataId)
                row = rows[0]
                args = {'datectrl': row[1], 'account': row[2], 'organization': row[3], 'categoryitem': row[4], 'item': row[5], 'price': str(row[6]), 'count': str(row[7]), 'total': str(row[8])}
            elif self.tableName == 'income':
                rows = DBData.selectRows(self.tableName, 'filter', ' where IncomeId=%s' % dataId)
                row = rows[0]
                args = {'datectrl': row[1], 'account': row[2], 'organization': row[3], 'categoryitem': row[4], 'item': row[5], 'amount': str(row[6])}
                    
            editDialog = ActionDialog(self.tableName, args)
            result = editDialog.ShowModal()
            if result == wx.ID_OK:
                cols = getValues(editDialog) + (dataId,) 
                self.table.UpdateRow(cols)
            editDialog.Destroy()  

        if key == 1:
            addData()
        elif key == 2:
            editData()
        elif key == 3:
            self.table.DeleteRow(self.table.GetRowLabelValue(self.curRow))
            self.SelectRow(self.curRow)
        
        self.table.data = DBData.selectRows(self.tableName, self.selectionFlag, self.selectionArgs)
        self.Reset()
    
    def OnPopupItemSelected(self, event):
        #key definites punkt of menu was selected
        key = event.GetId()
        self.OpenDialog(key)
        
        
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
    
#     def GetNumberCols(self, tableName):
#         dataTable = gridData()[tableName]
#         self.cols = dataTable[0]
#         return len(self.cols)
    
    def GetNumberRows(self, tableName):
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
        if flag == 'recursive':
            self.cursor.execute(query, args)
        else:
            query = query + args
            self.cursor.execute(query)
        
        rows = self.cursor.fetchall()
        self.nrows = len(rows) 
        return rows
    
    def getMaxID(self, tableName):
        return self.selectRows(tableName, 'id')[0][0]
    
    def insertRow(self, tableName, cols):
        dataTable = gridData()[tableName]
#         print('cols', cols)
        self.cursor.execute(dataTable[2], cols)
        
    def updateRow(self, tableName, cols):
        dataTable = gridData()[tableName]
#         print('update', dataTable[3], cols)
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
#         self.data = DBData
#         self.selection = self.data.selectRows(self.tableName) 
        self.data = DBData.selectRows(self.tableName) 
        self.nrows = len(self.data)
        self.ncols = self.GetNumberCols()        
    
    def GetNumberRows(self):
        return len(self.data)
    
    def GetNumberCols(self):
        dataTable = gridData()[self.tableName]
        self.cols = dataTable[0]
        return len(self.cols)
#         return self.data.GetNumberCols(self.tableName)
    
    def IsEmptyCell(self, row, col):
        if self.GetNumberRows() > 0:
            return self.data[row][col] is not None
        else: return True
    
    def GetValue(self, row, col):
        value = None
        if self.GetNumberRows() > 0: 
            value = str(self.data[row][col+1])
        
        if value is None:
            return ''
        else:
            return value

    def SetValue(self, row, col, value):
#         self.data[row][col] = value
        self.data[row][col] = value
        
    def GetColLabelValue(self, col):
        self.GetNumberCols()
        return self.cols[col]
    
    def GetRowLabelValue(self, row):
        return str(self.data[row][0])
    
    def DeleteRows(self, rows):
        """
        rows -> delete the rows from the dataset
        rows hold the row indices
        """
        deleteCount = 0
        rows = rows[:]
        rows.sort()
 
        for i in rows:
            self.data.pop(i-deleteCount)
            # we need to advance the delete count
            # to make sure we delete the right rows
            deleteCount += 1
    
    def UpdateRow(self, cols):
        DBData.updateRow(self.tableName, cols)
        DBData.commit()
            
    def DeleteRow(self, id):
        DBData.deleteRow(self.tableName, id)
        DBData.commit()
            
    def AppendRow(self, cols):
        DBData.insertRow(self.tableName, cols)
        DBData.commit()
       # self.selection = self.data.selectRows(self.tableName) 

    def ResetView(self, grid):
        """
        (Grid) -> Reset the grid view.   Call this to
        update the grid if rows and columns have been added or deleted
        """
        grid.BeginBatch()
#         print('self.nrows, self.GetNumberRows()',self.nrows, self.GetNumberRows())
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
    
    def UpdateValues(self, grid):
        """Update all displayed values"""
        # This sends an event to the grid table to update all of the values
        msg = wx.grid.GridTableMessage(self, wx.grid.GRIDTABLE_REQUEST_VIEW_GET_VALUES)
        grid.ProcessTableMessage(msg)


class ActionDialog(wx.Dialog):
    def __init__(self, tableName, args={}):
        wx.Dialog.__init__(self, None, -1, tableName, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER, size=(400,500))
        self.widgetList = []
        self.tableName = tableName
        self.args = args
        def createCtrl(el):
            if el[0] == wx.Button:
                ctrl = el[0](self, el[2], name=el[5]) # creates an instance of one of controls
            elif el[0] == wx.ComboBox:
                ctrl = el[0](self, -1, el[1], style=el[2], name=el[5], validator=el[6])
                # fills combobox list
                self.cbFilling(ctrl, el[7])
                if self.args is not None and self.args.get(el[5]) is not None:
                    ctrl.SetValue(self.args.get(el[5]))  #if dialog is opened for edit we take values from grid
                    ctrl.SetSelection(ctrl.FindString(ctrl.GetValue()))
            elif el[0] == wx.TextCtrl: 
                ctrl = wx.TextCtrl(self, -1, el[1], name=el[5], validator=el[6])
                if self.args is not None and self.args.get(el[5]) is not None: 
                    ctrl.SetValue(self.args.get(el[5]))
            elif el[0] == wx.BitmapButton:
                img = wx.Bitmap(imgFolder + el[1], wx.BITMAP_TYPE_PNG)
                ctrl = el[0](self, -1, img, style=el[2], name=el[5])
                self.Bind(wx.EVT_BUTTON, self.OnClickButton, ctrl)
            elif el[0] == wx.adv.DatePickerCtrl:
                ctrl = el[0](self, -1, el[1], style=el[2])
                if self.args is not None and self.args.get(el[5]) is not None:
                    str = self.args.get(el[5])
                    day, month, year =  str.split('.')
                    ctrl.SetValue(datetime(day=1, month=int(month), year=int(year)))
            elif el[0]  == NumCtrl:
                ctrl = NumCtrl(
                         self, -1,
                         value = 0,
                         pos = wx.DefaultPosition,
                         size = wx.DefaultSize,
                         style = wx.TE_PROCESS_ENTER,
                         validator = el[6],
                         name = el[5],
                         integerWidth = 10,
                         fractionWidth = 2,
                         allowNone = False,
                         allowNegative = False)
                ctrl.SetValue(self.args.get(el[5], '0'))
                ctrl.Bind(wx.EVT_KILL_FOCUS, self.OnChangeNum)
            else: 
                ctrl = el[0](self, -1, el[1], style=el[2])
            return ctrl

        sizerV = wx.BoxSizer(wx.VERTICAL)
        ctrlElements = dialogData()[self.tableName]
        for element in ctrlElements:
            if type(element[0]) == tuple: 
                sizerH = wx.BoxSizer(wx.HORIZONTAL)
                for el in element:
                    ctrl = createCtrl(el)
#                     print('ctrl', ctrl)
                    self.widgetList.append(ctrl)
                    if type(ctrl) == wx.ComboBox:
                        ctrl.Bind(wx.EVT_TEXT, self.OnCBText)
                        ctrl.Bind(wx.EVT_COMBOBOX_CLOSEUP, self.OnCBCloseUp)
                        ctrl.Bind(wx.EVT_COMBOBOX_DROPDOWN, self.OnCBDropDown)
                        objName = ctrl.GetName()
                        if objName == 'currency':
#                             if args is not None: ctrl.SetValue(args.get(el[5])) 
                            self.cbCurrency = ctrl
                        elif objName == 'account':
                            self.cbAccount = ctrl
                        elif objName == 'organization':
                            self.cbOrganization = ctrl
                        elif objName == 'categoryitem':
                            self.cbCategory = ctrl
                            self.Bind(wx.EVT_COMBOBOX, self.OnCBSelect, self.cbCategory)
                        elif objName == 'item':
                            self.cbItem = ctrl
                    elif type(ctrl) == NumCtrl:
                        objName = ctrl.GetName()
                        if objName == 'price':
                            self.price = ctrl
                        elif objName == 'count':
                            self.count = ctrl
                        elif objName == 'total':
                            self.total = ctrl
                      
                    sizerH.Add(ctrl, el[3], el[4], 10)
                sizerV.Add(sizerH, 0, wx.EXPAND)
            else:
                ctrl = createCtrl(element) # creates an instance of one of controls 
                self.widgetList.append(ctrl)
                sizerV.Add(ctrl, element[3], element[4], 10)
        self.SetSizer(sizerV)
        sizerV.Fit(self)
        self.popuped = False
    
    def cbFilling(self, cb, selection):
        def restoreSelectionById(dataId):
            for i in range(cb.GetCount()):
                if cb.GetClientData(i) == dataId:
                    return i 
                    break
            return -1
        if cb.GetSelection() != wx.NOT_FOUND:
            dataId = cb.GetClientData() #saves Id to restore later 
        else: dataId = None
        cb.Clear()
        i = 0
        for item in selection: 
            cb.Append(item[1])
            cb.SetClientData(i, item[0])
            i = i + 1
        n = restoreSelectionById(dataId)
        if n != -1:
            cb.SetSelection(restoreSelectionById(dataId))
            
    def OnChangeNum(self, event):
        numField = event.GetEventObject()
        if numField == self.price:
            if self.count.GetValue() != 0:
                self.total.SetValue(self.price.GetValue() * self.count.GetValue())
        if numField == self.count:
            if self.price.GetValue() != 0:
                self.total.SetValue(self.price.GetValue() * self.count.GetValue())
        if numField == self.total:
            if self.count.GetValue() != 0 and self.price.GetValue() != 0:
                self.count.SetValue(self.total.GetValue()/self.price.GetValue())
        event.Skip()
                

    def OnCBSelect(self, event):
        
        elId = self.cbCategory.GetClientData(self.cbCategory.GetSelection())
        selection = DBData.selectRows('item', "filter", " where CategoryID = %s" % elId)
        self.cbFilling(self.cbItem, selection)
#         self.cbItem.SetSelection(self.cbItem.FindString(itemValue))
            
    def OnCBText(self, event):
        if not self.popuped:
            event.GetEventObject().Popup()
        
    def OnCBCloseUp(self, event):
        self.popuped = False
        if len(event.GetEventObject().GetValue().strip()) == 0:
            selection = DBData.selectRows('item', "all")
            self.cbFilling(self.cbItem, selection)
                    
    def OnCBDropDown(self, event):
        self.popuped = True
        cb = event.GetEventObject()
        if cb.GetName() == 'item': 
            self.OnCBSelect(event)
        

    def OnClickButton(self, event):
        but = event.GetEventObject().GetName()

        if but == 'curdict':
            curDialog = CurrencyDialog()
            curDialog.ShowModal()
            curDialog.Destroy()
            selection = DBData.selectRows('currency', "all")
            self.cbFilling(self.cbCurrency, selection)
        elif but == 'accdict':
            accDialog = AccountDialog()
            accDialog.ShowModal()
            accDialog.Destroy()
            selection = DBData.selectRows('account', "all")
            self.cbFilling(self.cbAccount, selection)
        elif but == 'catdict':
            catDialog = CategoryDialog()
            catDialog.ShowModal()
            catDialog.Destroy()
            selection = DBData.selectRows('category', "all")
            self.cbFilling(self.cbCategory, selection)
        elif but == 'orgdict':
            orgDialog = OrgDialog()
            orgDialog.ShowModal()
            orgDialog.Destroy()
            selection = DBData.selectRows('organization', "all")
            self.cbFilling(self.cbOrganization, selection)
        elif but == 'itemdict':
            catDialog = CategoryDialog()
            catDialog.ShowModal()
            catDialog.Destroy()
            selection = DBData.selectRows('item', "all")
            self.cbFilling(self.cbOrganization, selection)
            
class NotEmptyValidator(wx.Validator):
    def __init__(self):
        wx.Validator.__init__(self)

    def Clone(self):
        return NotEmptyValidator()

    def Validate(self, widgetParent):
        widget = self.GetWindow()
        text = widget.GetValue().strip()

        if len(text) == 0:
            wx.MessageBox("The field '%s' can't be empty" % widget.GetName(), "Error")
            widget.SetBackgroundColour("pink")
            widget.SetFocus()
            widget.Refresh()
            return False
        elif type(widget) == wx.ComboBox and widget.FindString(text) is wx.NOT_FOUND:
            wx.MessageBox("There is no '%s' in %s dictionary" % (text, widget.GetName()), "Error")
            widget.SetBackgroundColour("pink")
            widget.SetFocus()
            widget.Refresh()
            return False
        else:
            widget.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOW))
            widget.Refresh()
            return True

    def TransferToWindow(self):
        return True

    def TransferFromWindow(self):
        return True

class NotZeroValidator(wx.Validator):
    def __init__(self):
        wx.Validator.__init__(self)

    def Clone(self):
        return NotZeroValidator()

    def Validate(self, widgetParent):
        widget = self.GetWindow()
        value = widget.GetValue()

        if value == 0:
            wx.MessageBox("The field '%s' must be > 0" % widget.GetName(), "Error")
            widget.SetBackgroundColour("pink")
            widget.SetFocus()
            widget.Refresh()
            return False
        else:
            widget.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOW))
            widget.Refresh()
            return True

    def TransferToWindow(self):
        return True

    def TransferFromWindow(self):
        return True

             
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