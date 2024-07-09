#!/usr/bin/env python
import os
import sys
from Qt import QtWidgets, QtCompat, QtCore
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


from _model import AssetModel, AssetDelegate

from _asset import AssetDef, AssetType


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

        # Set the custom delegate
        self.delegate = AssetDelegate()
        self.tableView.setItemDelegate(self.delegate)

        self.tableView.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)

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
