from PySide6.QtWidgets import (
    QApplication, QMainWindow, QMenu, QListWidgetItem, QInputDialog)
from PySide6.QtCore import Qt, QEvent
from ui_kanban import Ui_MainWindow
from helpers import absPath, existsFile
import csv


class MainWindow(QMainWindow, Ui_MainWindow):
    TAREAS_CSV = "tareas.csv"
    DELIMITADOR_CSV = ","
    
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # Creamos una lista de listas para manejarlas dinámicamente
        self.listas = [self.lista_Pendientes,
                       self.lista_EnProgreso,
                       self.lista_Completadas]

        # Configuración inicial de las listas
        for lista in self.listas:
            lista.clear()
            lista.installEventFilter(self)
            lista.itemDoubleClicked.connect(self.actualizarTarea)
        
        # Cargar tareas desde el archivo CSV al iniciar la aplicación
        if existsFile(absPath(self.TAREAS_CSV)):
            with open(absPath(self.TAREAS_CSV), newline="\n") as csvfile:
                reader = csv.reader(csvfile, delimiter=self.DELIMITADOR_CSV)
                for lista, nombre in reader:
                    item = QListWidgetItem(nombre)
                    item.setTextAlignment(Qt.AlignCenter)
                    self.listas[int(lista)].addItem(item)
                            
    def eventFilter(self, source, event):
        # Manejar eventos de filtro para el menú contextual
        if event.type() == QEvent.ContextMenu:
            menu = QMenu()
            
            item = source.itemAt(event.pos())
            menu.addAction("Borrar tarea", lambda: self.borrarTarea(item))
            menu.addAction("Añadir tarea", self.nuevaTarea)
            if menu.exec(event.globalPos()):
                return True
        return super().eventFilter(source, event)

    def nuevaTarea(self):
        # Añadir una nueva tarea a la lista "Pendientes"
        tarea, _ = QInputDialog.getText(self, "Tarea", "¿Cuál es el pendiente?")
        if tarea:
            item = QListWidgetItem(tarea)
            item.setTextAlignment(Qt.AlignCenter)
            self.lista_Pendientes.addItem(item)
    
    def borrarTarea(self, item):
        # Borrar una tarea de la lista actual
        if isinstance(item, QListWidgetItem):
            item_index = item.listWidget().row(item)
            item.listWidget().takeItem(item_index)
    
    def actualizarTarea(self, item):
        # Mover una tarea a la siguiente lista (Pendientes -> En Progreso -> Completadas)
        lista = item.listWidget()
        item_index = lista.row(item)
        lista.takeItem(item_index)
        if lista == self.lista_Pendientes:
            self.lista_EnProgreso.addItem(item)
        elif lista == self.lista_EnProgreso:
            self.lista_Completadas.addItem(item)

    def closeEvent(self, event):
        # Guardar las tareas en el archivo CSV al cerrar la aplicación
        tareas = []
        for i, lista in enumerate(self.listas):
            for j in range(lista.count()):
                tareas.append([i, lista.item(j).text()])
        with open(absPath(self.TAREAS_CSV), "w", newline="\n") as csvfile:
            writer = csv.writer(csvfile, delimiter=self.DELIMITADOR_CSV)
            writer.writerows(tareas)
        event.accept()


if __name__ == '__main__':
    # Configuración y ejecución de la aplicación
    app = QApplication()
    window = MainWindow()
    window.show()
    app.exec()
