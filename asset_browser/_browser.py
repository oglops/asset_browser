#!/usr/bin/env python
import os
import sys
from Qt import QtWidgets, QtCompat
from dataclasses import fields
from typing import List

uiFile = os.path.join(os.path.dirname(__file__), "test.ui")

try:
    import maya.OpenMayaUI as apiUI

    def getMayaWindow():
        ptr = apiUI.MQtUtil.mainWindow()
        return QtCompat.wrapInstance(long(ptr), QtWidgets.QMainWindow)

except:
    pass

from _asset import Asset

from _model import AssetModel, AssetDelegate

from _asset import Asset, AssetType


class MyWindow(QtWidgets.QDialog):

    def __init__(self, parent=None):
        super(MyWindow, self).__init__(parent)
        uiFile = "test.ui"
        QtCompat.loadUi(uiFile, self)
        # self.ui.show()
        self.setWindowTitle("test")

        # Create some Char instances
        # chars = [
        #     Asset(_type=AssetType.CHARACTER, version=13, entity="han", lod="lo"),
        #     Asset(_type=AssetType.PROP, version=3, entity="phone", lod="hi"),
        # ]

        import random, names

        self.assets = [
            Asset(
                _type=random.choice(list(AssetType)),
                version=random.randint(1, 20),
                entity=names.get_first_name(),
                lod = random.choice(('lo','hi'))
            )
            for i in range(20)
        ]

        # Create the model and set it to the list view
        self.model = AssetModel(self.assets)
        # self.list_view = self.findChild(QtWidgets.QListView, "listView")
        self.tableView.setModel(self.model)

        # Set the custom delegate
        self.delegate = AssetDelegate()
        self.tableView.setItemDelegate(self.delegate)

        # from _model import StyledItemDelegateTriangle
        # d = StyledItemDelegateTriangle()
        # self.tableView.setItemDelegate(d)

        # self.ui.resize(500, 300)
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
        app = QtWidgets.QApplication(sys.argv)
        win = MyWindow()
        sys.exit(app.exec())


if __name__ == "__main__":
    main()
