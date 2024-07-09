from Qt import QtGui, QtCore

from typing import List
from _asset import Asset, AssetType, AssetDef, AssetDataType
from dataclasses import fields

# instead of hardcoding headers, one could extract them into external yaml config
# HEADERS = {
#     "Type": {"visibility": False, "attr":},
#     "Entity": {"type": str},
#     "Version": {"type": int},
# }

class AssetModel(QtCore.QAbstractTableModel):
    def __init__(self, assets: List[Asset], parent=None):
        super().__init__(parent)
        self.assets = assets
        self.fields = [ x for x in fields(AssetDef) if x.metadata.get('visible')!=False]
        self.headers = [x.metadata.get('ui_name', x.name) for x in self.fields ]
    
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
            for key, val in value.items():
                setattr(asset, key, val)
            self.dataChanged.emit(index, index, [QtCore.Qt.EditRole])
            return True
        return False

    def flags(self, index):
        return QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled


from Qt.QtWidgets import (
    QStyledItemDelegate,
    QWidget,
    QComboBox,
    QLabel,
    QHBoxLayout,
)

# a way to avoid if/else here is to put this function
# inside each column/property's Delegate class
def makeEditorWidget( _type, asset, parent):
    combobox = QComboBox(parent)
    if _type == AssetDataType.VERSION:
        # get all versions of the asset
        combobox.addItems([str(i) for i in range(20)])
        
    elif _type == AssetDataType.LOD:
        combobox.addItems(['lo', 'hi'])

    return combobox


class AssetDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)

    def createEditor(self, parent, option, index):
        # could add layout and custom widget too
        asset = index.model().assets[index.row()]
        field = index.model().fields[index.column()]
        print('user about to change', field.type)
        editor = makeEditorWidget( field.type, asset, parent)

        return editor

    def setEditorData(self, editor, index):
        asset = index.model().assets[index.row()]
        field = index.model().fields[index.column()]
        # if field.type == AssetDataType.VERSION:
        # print('search for', str(getattr(asset, field.name)))
        index = editor.findText(str(getattr(asset, field.name)))
        if index!=-1:
            editor.setCurrentIndex(index)
        else:
            print(f"not found {index}  {asset.version}")
        
        editor.showPopup()

    def setModelData(self, editor, model, index):
        # layout = editor.layout()
        asset = model.assets[index.row()]

        field = index.model().fields[index.column()]
        # if field.type == AssetDataType.VERSION:
        content = editor.currentText()
        setattr(asset, field.name, content)
        print(f'set {field.name} {content}')


        model.setData(index, asset.attributes, QtCore.Qt.EditRole)

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)
        editor.setGeometry(option.rect)

    def paint(self, painter, option, index):
        super().paint(painter, option, index)
        asset = index.model().assets[index.row()]

        fields = index.model().fields
        field = fields[index.column()]
        # if getattr(asset, field.name) == field.default
        if not asset.isAttrDirty(field.name):
            return

        polygonTriangle = QtGui.QPolygon()
        polygonTriangle.append(QtCore.QPoint(option.rect.right()-5, option.rect.top()))
        polygonTriangle.append( QtCore.QPoint(option.rect.right(), option.rect.top()))
        polygonTriangle.append( QtCore.QPoint(option.rect.right(), option.rect.top()+5))

        painter.save()
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.setBrush(QtGui.QBrush(QtGui.QColor(QtCore.Qt.darkGreen))) 
        painter.setPen(QtGui.QPen(QtGui.QColor(QtCore.Qt.darkGreen)))
        painter.drawPolygon(polygonTriangle)
        painter.restore()

