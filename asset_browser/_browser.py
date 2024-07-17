#!/usr/bin/env python
import os
import sys
from Qt import QtWidgets, QtCompat, QtCore, QtGui
from dataclasses import fields
from typing import List

uiFile = os.path.join(os.path.dirname(__file__), "test.ui")
print(f"uiFile = {uiFile}")

try:
    import maya.OpenMayaUI as apiUI

    def getMayaWindow():
        ptr = apiUI.MQtUtil.mainWindow()
        return QtCompat.wrapInstance(int(ptr), QtWidgets.QMainWindow)

except:
    pass


from _model import AssetModel, AssetDelegate, ComboBoxDelegate

from _asset import AssetDef, AssetType
from functools import partial

class PersistentMenu(QtWidgets.QMenu):
    def mouseReleaseEvent(self, event):
        action = self.activeAction()

        if action and action.isEnabled():
            if not action.isCheckable():
                super(PersistentMenu, self).mouseReleaseEvent(event)
                return

            action.setEnabled(False)
            super(PersistentMenu, self).mouseReleaseEvent(event)
            action.setEnabled(True)
            action.trigger()
        else:
            super(PersistentMenu, self).mouseReleaseEvent(event)

class CustomTableView(QtWidgets.QTableView):
    def __init__(self, *args, **kwargs):
        super(CustomTableView, self).__init__(**kwargs)

        header = self.horizontalHeader()
        header.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        header.customContextMenuRequested.connect(self.build_menu)

        self.setSortingEnabled(True)

    def build_menu(self, pos):

        menu = PersistentMenu()

        action = QtWidgets.QWidgetAction(menu)

        for i, header in enumerate(self.model().headers):
            action = menu.addAction(header)
            if i==0: 
                action.setEnabled(False)
            action.setCheckable(True)
            action.setChecked(header in self.model()._visible_columns)
            action.triggered[bool].connect(partial(self.__updateColumnVis, header))
        
        menu.addSeparator()    
        clearAction = menu.addAction("Use Default")
        clearAction.triggered.connect(
                partial(self.__defaultColumns)
            )
    
        menu.setStyleSheet("""
            QMenu::item:disabled {
                background: lightgray;
                color: gray;
            }
        """)
        menu.exec_(self.horizontalHeader().viewport().mapToGlobal(pos))

    def __updateColumnVis(self, header, vis):
        if not vis:
            self.model()._visible_columns.remove(header)
        else:
            self.model()._visible_columns.add(header)
        
        index = self.model().headers.index(header)
        self.setColumnHidden(index, not vis)
        # print(f"set col {index} {not vis} {self.model().headers}")

    def __defaultColumns(self):
        for i,field in enumerate(self.model().fields):
            if not field.metadata:
                self.setColumnHidden(False)
                continue

            if visible:= field.metadata.get('visible'):
                self.setColumnHidden(i, not visible)
            else:
                self.setColumnHidden(i, False)

        self.model()._visible_columns = set(self.model().headers)

class MyWindow(QtWidgets.QDialog):

    def __init__(self, parent=None):
        super(MyWindow, self).__init__(parent)
        QtCompat.loadUi(uiFile, self)
        self.setWindowTitle("test")

        import random, names

        self.assets = [
            AssetDef(
                _type=random.choice(list(AssetType)),
                version=random.randint(1, 20),
                entity=names.get_first_name(),
                lod = random.choice(('lo','hi'))
            )
            for i in range(10)
        ]

        # Create the model and set it to the list view
        self.model = AssetModel(self.assets)
        self.tableView.setModel(self.model)
        print(self.tableView)

        # Set the custom delegate
        self.delegate = AssetDelegate()
        self.tableView.setItemDelegate(self.delegate)

        self.tableView.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.tableView.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.tableView.setShowGrid(False)

        self.resize(330, 420)
        self.show()

        self.resetBtn.clicked.connect(self._resetChanges)
        self.modifiedBtn.clicked.connect(self._modified)

    def _resetChanges(self):
        refresh = False
        for asset in self.assets:
            if asset.dirty:
                asset.reset()
                refresh = True
        if refresh:
            top_left = self.model.index(0, 0)
            bottom_right = self.model.index(self.model.rowCount() - 1, self.model.columnCount() - 1)
            self.tableView.dataChanged(top_left, bottom_right)

    def _modified(self):

        for asset in self.assets:
            if not asset.dirty:
                continue
            print(f" {asset.entity} --> {asset.dirtyAttrs}")

def main():
    qApp = QtWidgets.QApplication.instance()
    if qApp and qApp.applicationName().startswith("Maya"):
        global win
        try:
            win.close()
        except:
            pass
        win = MyWindow(getMayaWindow())
    else:
        QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_ShareOpenGLContexts)
        app = QtWidgets.QApplication(sys.argv)
        win = MyWindow()
        sys.exit(app.exec())


if __name__ == "__main__":
    main()
