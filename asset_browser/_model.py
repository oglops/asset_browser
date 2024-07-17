from Qt import QtGui, QtCore

from typing import List
from _asset import AssetType, AssetDef, AssetDataType
from dataclasses import fields
import random

from Qt.QtWidgets import QApplication, QMainWindow, QTableView, QComboBox, QStyledItemDelegate, QVBoxLayout, QWidget, QTableWidgetItem, QTableWidget
from Qt.QtCore import Qt, QModelIndex, QRect, QSize
from Qt.QtWidgets import QStyleOptionComboBox, QStyle

# instead of hardcoding headers, one could extract them into external yaml config
# HEADERS = {
#     "Type": {"visibility": False, "attr":},
#     "Entity": {"type": str},
#     "Version": {"type": int},
# }


class AssetModel(QtCore.QAbstractTableModel):
    def __init__(self, assets: List[AssetDef], parent=None):
        super().__init__(parent)
        self.assets = assets
        self.fields = [ x for x in fields(AssetDef) if x.metadata.get('visible')!=False]
        self.headers = [x.metadata.get('ui_name', x.name) for x in self.fields ]
        self._visible_columns = set(self.headers)
    
    def headerData(self, section, orientation, role):
        # section is the index of the column/row.
        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Horizontal:
                return self.headers[section]

            # if orientation == QtCore.Qt.Vertical:
            #     return str(self._data.index[section])

    def rowCount(self, parent=None):
        return len(self.assets)

    def columnCount(self, parent=None):
        return len(self.headers)

    def data(self, index, role):
        if role == QtCore.Qt.DisplayRole:
            asset = self.assets[index.row()]
            return getattr(asset, self.fields[index.column()].name)

    def setData(self, index, value, role):
        if role == QtCore.Qt.EditRole:
            asset = self.assets[index.row()]
            field = self.fields[index.column()]
            setattr(asset, field.name, value)
            self.dataChanged.emit(index, index, [QtCore.Qt.EditRole])

            # if the field affects other field
            if field.metadata:
                print(f"check field: {field.name} {field.metadata}")
                if affected := field.metadata.get("affect"):
                    print(f"calculate default for affected fields {affected}")
                    # can extract the update logic into abstract methods
                    for affected_field in affected:
                        new_val = random.choice(("lo", "hi"))
                        print(f"new_val= {new_val}")
                        if new_val != getattr(asset, affected_field):
                            setattr(asset, affected_field, new_val)
                            print(f"Updated affected field {affected_field}")
            return True
        return False

    def flags(self, index):
        return (
            QtCore.Qt.ItemIsSelectable
            | QtCore.Qt.ItemIsEditable
            | QtCore.Qt.ItemIsEnabled
        )

    def sort(self, column, order):
        self._sort_column = column
        self._sort_order = order
        self.layoutAboutToBeChanged.emit()
        self.assets = list(sorted(self.assets, key=lambda x: getattr(x, self.fields[column].name), reverse=(order == QtCore.Qt.DescendingOrder)))
        self.layoutChanged.emit()

from Qt.QtWidgets import (
    QStyledItemDelegate,
    QWidget,
    QComboBox,
    QLabel,
    QHBoxLayout,
)


# a way to avoid if/else here is to put this function
# inside each column/property's Delegate class
def makeEditorWidget(_type, asset, parent):
    combobox = QComboBox(parent)
    if _type == AssetDataType.VERSION:
        # get all versions of the asset
        combobox.addItems([str(i) for i in range(20)])

    elif _type == AssetDataType.LOD:
        combobox.addItems(["lo", "hi"])

    return combobox


class AssetDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)

    def createEditor(self, parent, option, index):
        # could add layout and custom widget too
        asset = index.model().assets[index.row()]
        field = index.model().fields[index.column()]
        print("user about to change", field.type)
        editor = makeEditorWidget(field.type, asset, parent)

        return editor

    def setEditorData(self, editor, index):
        asset = index.model().assets[index.row()]
        field = index.model().fields[index.column()]
        # if field.type == AssetDataType.VERSION:
        # print('search for', str(getattr(asset, field.name)))
        index = editor.findText(str(getattr(asset, field.name)))
        if index != -1:
            editor.setCurrentIndex(index)
        else:
            print(f"not found {index}  {asset.version}")

        editor.showPopup()

    def setModelData(self, editor, model, index):
        # asset = model.assets[index.row()]
        # field = index.model().fields[index.column()]
        # # if field.type == AssetDataType.VERSION:
        content = editor.currentText()
        # setattr(asset, field.name, content)
        # print(f"set {field.name} {content}")

        model.setData(index, content, QtCore.Qt.EditRole)

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)
        editor.setGeometry(option.rect)

    def paint(self, painter, option, index):
        super().paint(painter, option, index)
        asset = index.model().assets[index.row()]

        field = index.model().fields[index.column()]

        if field.type in (AssetDataType.LOD ,AssetDataType.VERSION):
            value = index.model().data(index, Qt.DisplayRole)
            combobox_option = QStyleOptionComboBox()
            combobox_option.rect = option.rect
            combobox_option.currentText = str(value)
            combobox_option.state = option.state | QStyle.State_Enabled
            # combobox_option.frame = True
 
            # Draw the combobox
            QApplication.style().drawComplexControl(QStyle.CC_ComboBox, combobox_option, painter)
            QApplication.style().drawControl(QStyle.CE_ComboBoxLabel, combobox_option, painter)

        fields = index.model().fields
        field = fields[index.column()]
        # if getattr(asset, field.name) == field.default
        if not asset.isAttrDirty(field.name):
            return

        polygonTriangle = QtGui.QPolygon()
        polygonTriangle.append(
            QtCore.QPoint(option.rect.right() - 5, option.rect.top())
        )
        polygonTriangle.append(QtCore.QPoint(option.rect.right(), option.rect.top()))
        polygonTriangle.append(
            QtCore.QPoint(option.rect.right(), option.rect.top() + 5)
        )

        painter.save()
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.setBrush(QtGui.QBrush(QtGui.QColor(QtCore.Qt.darkGreen)))
        painter.setPen(QtGui.QPen(QtGui.QColor(QtCore.Qt.darkGreen)))
        painter.drawPolygon(polygonTriangle)
        painter.restore()

# not used right now, one could also define specific delegates for certain columns
# if things get complex and do not wish to have lots of if/else in main delegate
class ComboBoxDelegate(QStyledItemDelegate):
    def __init__(self, items, parent=None):
        super(ComboBoxDelegate, self).__init__(parent)
        self.items = items

    def createEditor(self, parent, option, index):
        editor = QComboBox(parent)
        editor.addItems(self.items)
        return editor

    def setEditorData(self, editor, index):
        value = index.model().data(index, Qt.EditRole)
        editor.setCurrentText(value)

    def setModelData(self, editor, model, index):
        model.setData(index, editor.currentText(), Qt.EditRole)

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)

    def paint(self, painter, option, index):
        value = index.model().data(index, Qt.DisplayRole)

        combobox_option = QStyleOptionComboBox()
        combobox_option.rect = option.rect
        combobox_option.currentText = value
        combobox_option.state = option.state

        # Draw the combobox
        QApplication.style().drawComplexControl(QStyle.CC_ComboBox, combobox_option, painter)
        QApplication.style().drawControl(QStyle.CE_ComboBoxLabel, combobox_option, painter)

    def editorEvent(self, event, model, option, index):
        if event.type() == event.MouseButtonPress:
            if option.rect.contains(event.pos()):
                self.commitData.emit(index)
                self.closeEditor.emit(index, self.NoHint)
                return True
        return super(ComboBoxDelegate, self).editorEvent(event, model, option, index)
