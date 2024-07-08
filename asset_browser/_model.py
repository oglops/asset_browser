from PySide6.QtCore import Qt, QAbstractTableModel
from typing import List
from _asset import Asset, AssetType, AssetDef, AssetDataType
from dataclasses import fields

# HEADERS = {
#     "Type": {"visibility": False, "attr":},
#     "Entity": {"type": str},
#     "Version": {"type": int},
# }


class AssetModel(QAbstractTableModel):
    def __init__(self, assets: List[Asset], parent=None):
        super().__init__(parent)
        self.assets = assets
        self.fields = [ x for x in fields(AssetDef) if x.metadata.get('visible')!=False]
        self.headers = [x.metadata.get('ui_name', x.name) for x in self.fields ]
        print('da headers', self.headers)
    
    def headerData(self, section, orientation, role):
        # section is the index of the column/row.
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                print('headaer', section)
                return self.headers[section]

            # if orientation == Qt.Vertical:
            #     return str(self._data.index[section])

    def rowCount(self, parent=None):
        return len(self.assets)

    def columnCount(self, parent=None):
        return len(self.headers)

    def data(self, index, role):
        if role == Qt.DisplayRole:
            asset = self.assets[index.row()]
            return getattr(asset, self.fields[index.column()].name)

    def setData(self, index, value, role):
        if role == Qt.EditRole:
            asset = self.assets[index.row()]
            for key, val in value.items():
                setattr(asset, key, val)
            self.dataChanged.emit(index, index, [Qt.EditRole])
            return True
        return False

    def flags(self, index):
        return Qt.ItemIsEditable | Qt.ItemIsEnabled


from PySide6.QtWidgets import (
    QStyledItemDelegate,
    QWidget,
    QComboBox,
    QLabel,
    QHBoxLayout,
)


def makeEditorWidget( _type, asset, parent):
    if _type == AssetDataType.VERSION:
        # get all versions of the asset
        combobox = QComboBox(parent)
        combobox.addItems([str(i) for i in range(20)])
        return combobox

class AssetDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)

    def createEditor(self, parent, option, index):
        # editor = QWidget(parent)
        # layout = QHBoxLayout(editor)

        asset = index.model().assets[index.row()]
        # for field in fields(asset):  # Skip _type field
        #     if field.type == str:
        #         combo_box = QComboBox(editor)
        #         combo_box.addItems(
        #             ["Option 1", "Option 2", "Option 3"]
        #         )  # Replace with your options
        #         layout.addWidget(combo_box)
        #     else:
        #         label = QLabel(editor)
        #         layout.addWidget(label)
        field = index.model().fields[index.column()]
        print('crap', field.type)
        # layout.addWidget(makeEditorWidget(editor, field.type, asset))
        editor = makeEditorWidget( field.type, asset, parent)

        # editor.setLayout(layout)
        return editor

    def setEditorData(self, editor, index):
        asset = index.model().assets[index.row()]
        field = index.model().fields[index.column()]
        # layout = editor.layout()
        if field.type == AssetDataType.VERSION:
            index = editor.findText(str(asset.version))
            if index!=-1:
                editor.setCurrentIndex(index    )
            else:
                print(f"not found {index}  {asset.version}")
            
            editor.showPopup()
        # for i in range(layout.count()):
        #     widget = layout.itemAt(i).widget()
        #     if isinstance(widget, QComboBox):
        #         widget.setCurrentIndex(asset.version)
            # elif isinstance(widget, QLabel):
            #     widget.setText(asset.name)

    def setModelData(self, editor, model, index):
        layout = editor.layout()
        asset = model.assets[index.row()]
        # for i in range(layout.count()):
        #     widget = layout.itemAt(i).widget()
        #     field_name = fields(asset)[i + 1].name
        #     if isinstance(widget, QComboBox):
        #         setattr(asset, field_name, widget.currentText())
        field = index.model().fields[index.column()]
        if field.type == AssetDataType.VERSION:
            content = editor.currentText()
            setattr(asset, field.name, content)
            print(f'set {field.name} {content}')


        model.setData(index, asset.attributes, Qt.EditRole)

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)
        editor.setGeometry(option.rect)

    def paint(self, painter, option, index):
        super().paint(painter, option, index)
        asset = index.model().assets[index.row()]
        # if not asset.dirty:
        #     return
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


from PySide6 import QtGui, QtCore, QtWidgets

# class StyledItemDelegateTriangle(QtWidgets.QStyledItemDelegate):
#     def __init__(self, parent=None):
#         super(StyledItemDelegateTriangle, self).__init__(parent)

#     def paint(self, painter, option, index):
#         super(StyledItemDelegateTriangle, self).paint(painter, option, index)

#         polygonTriangle = QtGui.QPolygon(3)
#         polygonTriangle.setPoint(0, QtCore.QPoint(option.rect.x()+5, option.rect.y()))
#         polygonTriangle.setPoint(1, QtCore.QPoint(option.rect.x(), option.rect.y()))
#         polygonTriangle.setPoint(2, QtCore.QPoint(option.rect.x(), option.rect.y()+5))

#         painter.save()
#         painter.setRenderHint(painter.Antialiasing)
#         painter.setBrush(QtGui.QBrush(QtGui.QColor(QtCore.Qt.darkGreen))) 
#         painter.setPen(QtGui.QPen(QtGui.QColor(QtCore.Qt.darkGreen)))
#         painter.drawPolygon(polygonTriangle)
#         painter.restore()