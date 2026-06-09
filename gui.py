import sys
import json
import uuid
import main

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QHBoxLayout, QToolBar, QMessageBox
)
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QDoubleSpinBox, QPushButton, QFileDialog, QSizePolicy, QDialog, QLineEdit


from PySide6.QtCore import *

from PySide6.QtGui import *

from NodeGraphQt import NodeGraph, BaseNode


# =========================
# NODES
# =========================

class SourceNode(BaseNode):
    __identifier__ = 'Plant'
    NODE_NAME = 'Source'
    node_type = "Source"

    def __init__(self):
        super().__init__()
        self.add_output('Output1')
        self.uid = str(uuid.uuid4())

        self.data = {
            "ore":0,
            "water":0,
            "solids":0
        }


class SeparatorNode(BaseNode):
    __identifier__ = 'Plant'
    NODE_NAME = 'Separator'
    node_type = "Seperator"

    def __init__(self):
        super().__init__()
        #to make sure users can edit
        self.set_port_deletion_allowed(True)

        self.uid = str(uuid.uuid4())
        self.add_input('Input1')
        self.add_output('Output1')
        self.add_output('Output2')

        self.data = {
            "ore":[0.5, 0.5],
            "water":[0.5, 0.5],
            "solids":[0.5, 0.5]
        }

    def add_new_input(self, node_inspector):

        new_num = len(self.inputs())+1

        if new_num >= 4:

            print("Error: Maximum Inputs (3) Exceeded")

            return

        self.add_input(f"Input{new_num}")

        #from here update the screen for no reason

        self.node_inspector.set_node(self)

    def add_new_output(self, node_inspector):

        new_num = len(self.outputs())+1

        #need a maximum # of outputs, lets say 3

        if new_num >= 4:

            print("Error: Maximum Outputs (3) Exceeded")

            return

        self.add_output(f"Output{new_num}")

        #now from here we need to update the data within this

        for each_data in self.data.keys():

            self.data[each_data].append(0.0)

        #now from here we want to regenerate the field of inputs

        node_inspector.set_node(self)

    def remove_first_output(self, node_inspector):

        last_number = len(self.outputs())

        if last_number <= 2:

            print("Error: Cannot Have Less than 2 Outputs")

            return

        self.delete_output(f"Output{last_number}")

        #we have remove the output but not the data from the node
        for each_data in self.data.keys():

            self.data[each_data].pop(last_number-1)

        #now update this all

        node_inspector.set_node(self)

    def remove_first_input(self, node_inspector):

        last_number = len(self.inputs())

        if last_number <= 1:

            print("Error: Cannot Have Less than 1 Inputs")

            return

        self.delete_input(f"Input{last_number}")

        #now just update the node inspector
        node_inspector.set_node(self)


class CollectorNode(BaseNode):
    __identifier__ = 'Plant'
    NODE_NAME = 'Collector'
    node_type = "Collector"

    def __init__(self):
        super().__init__()
        self.uid = str(uuid.uuid4())
        self.add_input('Input1')
        

        self.data = {
            "ore":0,
            "water":0,
            "solids":0
        }

    def add_new_input(self):

        next_num = len(self.inputs())+1
        self.add_input(f"Input{next_num}")

#this is a functoin to clear a layout
def clear_layout(layout):
    if layout is None:
        return

    while layout.count():
        item = layout.takeAt(0)

        if item is None:
            continue

        widget = item.widget()
        child_layout = item.layout()

        if widget is not None:
            widget.setParent(None)
            widget.deleteLater()

        elif child_layout is not None:
            clear_layout(child_layout)

#This is for editing values of the nodes, basically creating a pop up window

class NodeInspector(QWidget):
    def __init__(self, window):
        super().__init__()

        self.main_window = window

        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignTop)
        self.setFixedWidth(300)
        self.setLayout(self.layout)

        self.node = None

    # -------------------------
    # SET CURRENT NODE
    # -------------------------
    def set_node(self, node):

        self.node = node

        

        # clear UI safely
        clear_layout(self.layout)

        # -------------------------
        # blank state
        # -------------------------
        if node is None:
            self.layout.addWidget(QLabel("No node selected"))
            return

        # -------------------------
        # safe name handling
        # -------------------------
        name = getattr(node, "name", None)
        if callable(name):
            name = name()

        if not name:
            name = "Unnamed Node"

        

        name_label = QLabel(str(name))
        name_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        name_label.setFixedHeight(25)
        name_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.layout.addWidget(name_label)

        # -------------------------
        # safe data handling
        # -------------------------
        data = getattr(node, "data", None)
        if data is None:
            data = {}
            node.data = data

        # -------------------------
        # build UI
        # -------------------------


        num_outputs = 0 #this is in the case of editing a seperator

        #this will change depending on a seperator, source or collector

        if self.node.node_type == "Collector":
            for key, value in data.items():



                row = QHBoxLayout()

                label = QLabel(str(key))
                label.setFixedWidth(120)
                row.addWidget(label)

                # numeric
                if isinstance(value, (int, float)):

                    editor = QDoubleSpinBox()
                    editor.setRange(0, 1e9)
                    editor.setDecimals(2)
                    editor.setValue(float(value))

                    editor.valueChanged.connect(
                        lambda v, k=key: self._update_node(k, v)
                    )

                # text
                else:
                    editor = QLineEdit(str(value))

                    editor.textChanged.connect(
                        lambda v, k=key: self._update_node(k, v)
                    )

                row.addWidget(editor)

                
                self.layout.addLayout(row)

            #now we have some util buttons we want to display in a row
            editor_row = QHBoxLayout()


            #now create the buttons and link them to functions
            add_input_button = QPushButton("Add Input")

            add_input_button.clicked.connect(node.add_new_input)
            
            remove_input_button = QPushButton("Remove Input")

            remove_input_button.clicked.connect(node.remove_first_input)

            #now add the buttons to the layout and then the layout the bigger layout

            editor_row.addWidget(add_input_button)
            editor_row.addWidget(remove_input_button)

            self.layout.addLayout(editor_row)

        elif self.node.node_type == "Seperator":



            for key, value in data.items():

                #from here we want to determine if there is two or three outputs

                num_outputs = len(value)

                row = QHBoxLayout()

                label = QLabel(str(key))
                label.setFixedWidth(120)
                row.addWidget(label)

                # numeric
                if isinstance(value[0], (int, float)):

                    editor = QDoubleSpinBox()
                    editor.setRange(0, 1)
                    editor.setValue(float(value[0]))

                    editor.valueChanged.connect(
                        lambda v, k=key: self._update_seperator(k, 0, v)
                    )

                    editor2 = QDoubleSpinBox()
                    editor2.setRange(0, 1)
                    editor2.setValue(float(value[1]))

                    editor2.valueChanged.connect(
                        lambda v, k=key:self._update_seperator(k, 1, v)
                    )

                    #now in the case where there is 3 outputs
                    #we are going to want one more column of inputs
                    if num_outputs == 3:

                        editor3 = QDoubleSpinBox()
                        editor3.setRange(0, 1)
                        editor3.setValue(float(value[2]))

                        editor3.valueChanged.connect(
                            lambda v, k=key:self._update_seperator(k, 2, v)
                        )

                # text
                else:
                    editor = QLineEdit(str(value))

                    editor.textChanged.connect(
                        lambda v, k=key: self._update_node(k, v)
                    )

                row.addWidget(editor)
                row.addWidget(editor2)

                if num_outputs == 3:

                    row.addWidget(editor3)

                
                self.layout.addLayout(row)

            add_row = QHBoxLayout()

            #here creates two buttons for adding inputs and outputs

            input_button = QPushButton("Add Input")

            input_button.clicked.connect(lambda: node.add_new_input(self))

            output_button = QPushButton("Add Output")
            
            output_button.clicked.connect(lambda: node.add_new_output(self)) #need to pass this so that when we add an output it will update itself
            

            #add the buttons to the row/layout
            add_row.addWidget(input_button)
            add_row.addWidget(output_button)

            self.layout.addLayout(add_row)

            #now from here we want to make options to remove inputs and outputs

            remove_row = QHBoxLayout()

            remove_input_button = QPushButton("Remove Input")

            remove_input_button.clicked.connect(lambda: node.remove_first_input(self)) #when we click it remove the most recently added input

            remove_output_button = QPushButton("Remove Output")

            remove_output_button.clicked.connect(lambda: node.remove_first_output(self)) #when we clikc it remov ethe most recently added output

            remove_row.addWidget(remove_input_button)
            remove_row.addWidget(remove_output_button)

            self.layout.addLayout(remove_row)


            

        elif self.node.node_type == "Source":
            for key, value in data.items():



                row = QHBoxLayout()

                label = QLabel(str(key))
                label.setFixedWidth(120)
                row.addWidget(label)

                # numeric
                if isinstance(value, (int, float)):

                    editor = QDoubleSpinBox()
                    editor.setRange(0, 1e9)
                    editor.setDecimals(2)
                    editor.setValue(float(value))

                    editor.valueChanged.connect(
                        lambda v, k=key: self._update_node(k, v)
                    )

                # text
                else:
                    editor = QLineEdit(str(value))

                    editor.textChanged.connect(
                        lambda v, k=key: self._update_node(k, v)
                    )

                row.addWidget(editor)

                
                self.layout.addLayout(row)

            
        else:

            print("Error: unknown node type")

            return

    def _update_node(self, key, value):
        if self.node is not None:
            self.node.data[key] = value


    #this function is for when data is edited in the gui and now that needs to be reflected in the objects data
    def _update_seperator(self, key, pos, value):

        if self.node is not None:

            self.node.data[key][pos] = value

    


# =========================
# MAIN WINDOW
# =========================

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Plant++ (Prototype)")
        self.resize(1600, 900)

        # -------------------------
        # GRAPH
        # -------------------------
        self.graph = NodeGraph()

        #now we want to register an event filter for dealing with clicks
        self.graph.widget.installEventFilter(self)

        self.graph.register_node(SourceNode)
        self.graph.register_node(SeparatorNode)
        self.graph.register_node(CollectorNode)

        # -------------------------
        # CENTRAL WIDGET
        # -------------------------
        central = QWidget()
        self.setCentralWidget(central)

        layout = QHBoxLayout()
        central.setLayout(layout)

        layout.addWidget(self.graph.widget, stretch=1)
        self.graph.node_selected.connect(self.on_node_selected)
        self.inspector = NodeInspector(self)
        layout.addWidget(self.inspector, stretch=0)

        # -------------------------
        # UI SETUP
        # -------------------------
        self.create_menu_bar()
        #self.create_toolbar()

        self.click_mode = None


        #the next variable stores the last action of the user so that they can easily repeat it
        self.last_action = None

        shortcut = QShortcut(QKeySequence("F4"), self)
        shortcut.activated.connect(self.repeat_last_action)

        # demo nodes
        #self.build_demo()



    # =========================
    # MENU BAR
    # =========================
    def create_menu_bar(self):
        menu = self.menuBar()

        # FILE
        file_menu = menu.addMenu("File")

        export_action = QAction("Export System", self)
        export_action.triggered.connect(self.export_graph)

        file_menu.addAction(export_action)

        import_action = QAction("Import System", self)
        import_action.triggered.connect(self.import_from_json)

        file_menu.addAction(import_action)

        exit_action = QAction("Exit", self)

        exit_action.triggered.connect(self.confirm_exit)

        file_menu.addAction(exit_action)

        # EDIT
        edit_menu = menu.addMenu("Edit")

        add_menu = edit_menu.addMenu("Add")

        add_separator_action = QAction("Separator", self)

        add_separator_action.triggered.connect(self.add_separator)

        add_source_action = QAction("Source", self)

        add_source_action.triggered.connect(self.add_source)

        add_collector_action = QAction("Collector", self)

        add_collector_action.triggered.connect(self.add_collector)

        add_menu.addAction(add_source_action)
        add_menu.addAction(add_separator_action)
        add_menu.addAction(add_collector_action)

        remove_action = QAction("Remove", self)

        remove_action.triggered.connect(self.enable_remove_mode)

        
        edit_menu.addAction(remove_action)

        # SIMULATE
        sim_menu = menu.addMenu("Simulate")

        run_action = QAction("Run Simulation", self)

        run_action.triggered.connect(self.open_two_file_dialog)

        sim_menu.addAction(run_action)

        # HELP
        help_menu = menu.addMenu("Help")
        help_menu.addAction(QAction("Help", self))

    # =========================
    # TOOLBAR
    # =========================
    def create_toolbar(self):
        toolbar = QToolBar("Main Toolbar")
        self.addToolBar(toolbar)

        toolbar.addAction("Add Node")
        toolbar.addAction("Remove")
        toolbar.addAction("Run")



    # =========================
    # DEMO GRAPH
    # =========================
    def build_demo(self):
        src = self.graph.create_node('Plant.SourceNode', name='Ore Source')
        sep = self.graph.create_node('Plant.SeparatorNode', name='PSC1')
        col = self.graph.create_node('Plant.CollectorNode', name='Ore Col')

        src.set_pos(-200, 0)
        sep.set_pos(0, 0)
        col.set_pos(200, 0)

        src.output(0).connect_to(sep.input(0))
        sep.output(0).connect_to(col.input(0))

    #this event filter just makes it so if you press the remove button
    #you can press anywhere in empty space to disable the removing
    def eventFilter(self, obj, event):

        if obj == self.graph.widget and event.type() == QEvent.MouseButtonPress:

            # Item under the mouse.
            item = self.graph.viewer().itemAt(event.pos())

            # If we're in remove mode and clicked empty space, cancel remove mode.
            if self.click_mode == "remove" and item is None:
                self.click_mode = None
                print("Remove mode cancelled.")
                return True  # event handled

        # Let Qt process everything else normally.
        return super().eventFilter(obj, event)

    # =========================
    # ADD SEPARATOR
    # =========================
    def add_separator(self):

        
        new_sep = self.graph.create_node('Plant.SeparatorNode', name='New Seperator')
        # Get the center of the viewport (in widget coordinates).
        view_center = self.graph.viewer().viewport().rect().center()

        # Convert that point to scene coordinates.
        scene_center = self.graph.viewer().mapToScene(view_center)
       

        # Place it at the center of the visible area.
        new_sep.set_pos(scene_center.x(), scene_center.y())

        self.last_action = self.add_separator
        #new_sep.set_pos(0, 0)

    # =========================
    # ADD SOURCE
    # =========================

    def add_source(self):

        new_src = self.graph.create_node('Plant.SourceNode', name="New Source")


        # Get the center of the viewport (in widget coordinates).
        view_center = self.graph.viewer().viewport().rect().center()

        # Convert that point to scene coordinates.
        scene_center = self.graph.viewer().mapToScene(view_center)

        # Place it at the center of the visible area.
        new_src.set_pos(scene_center.x(), scene_center.y())

        self.last_action = self.add_source
    # =========================
    # ADD COLLECTOR
    # =========================

    def add_collector(self):

        new_col = self.graph.create_node('Plant.CollectorNode', name="New Collector")

        view_center = self.graph.viewer().viewport().rect().center()

        scene_center=self.graph.viewer().mapToScene(view_center)

        new_col.set_pos(scene_center.x(), scene_center.y())

        self.last_action = self.add_collector



    #Function to set it so the next node clicked gets removed
    def enable_remove_mode(self):

        self.click_mode = "remove"

    #function to enable a shortcut for repeating the last action

    def repeat_last_action(self):

        if self.last_action is not None:
            self.last_action()

        else:

            print("Warning: No previous action to complete")



    # =========================
    # EXPORT FUNCTION
    # =========================
    def export_graph(self):
        nodes = []

        for node in self.graph.all_nodes():
            print(node.pos())

            node_data = {
                "name": node.name(),
                "type": node.type_,
                "data": getattr(node, "data", {}),
                "pos": (node.pos()[0], node.pos()[1]),
                "inputs": [],
                "outputs": []
            }

            print(node_data)

            print(node.inputs())

            print(node.outputs())

            # inputs
            for inp in node.inputs().keys():
                node_data["inputs"].append(node.inputs()[inp].name())

            # outputs
            for out in node.outputs().keys():
                node_data["outputs"].append(node.outputs()[out].name())

            nodes.append(node_data)

        #now do the connections:
        edges = []

        for node in self.graph.all_nodes():

            for out_port in node.outputs().keys():

                temp_port = node.outputs()[out_port]


                connected_ports = node.outputs()[out_port].connected_ports()

                for in_port in connected_ports:
                    edges.append({
                        "from": f"{node.name()}:{temp_port.name()}",
                        "to": f"{in_port.node().name()}:{in_port.name()}"
                    })

        filepath, _ = QFileDialog.getSaveFileName(
            self,
            "Export Graph",
            "",
            "JSON Files (*.json)"
        )

        if not filepath:
            return  # user cancelled

        data = {
            "nodes": nodes,
            "edges": edges
        }

        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)

        print(f"Exported to {filepath}")



    def import_from_json(self):
        filepath, _ = QFileDialog.getOpenFileName(
            self,
            "Import Graph",
            "",
            "JSON Files (*.json)"
        )

        if not filepath:
            return

        with open(filepath, "r") as f:
            data = json.load(f)

        nodes = data["nodes"]
        edges = data["edges"]

        # -------------------------
        # CLEAR GRAPH
        # -------------------------
        self.graph.clear_session()

        # -------------------------
        # CREATE NODE MAP
        # -------------------------
        node_map = {}

        # -------------------------
        # 1. REBUILD NODES
        # -------------------------
        for n in nodes:
            node = self.graph.create_node(n["type"], name=n["name"])

            # restore data
            node.data = n.get("data", {})

            # restore position
            x, y = n.get("pos", [0, 0])
            node.set_pos(x, y)

            # store by NAME (your format uses names, not UUIDs)
            node_map[n["name"]] = node

        # -------------------------
        # 2. REBUILD EDGES
        # -------------------------
        for e in edges:
            from_node_name, from_port = e["from"].split(":")
            to_node_name, to_port = e["to"].split(":")

            out_node = node_map[from_node_name]
            in_node = node_map[to_node_name]

            out_port = self._find_port_by_name(out_node.outputs(), from_port)
            in_port = self._find_port_by_name(in_node.inputs(), to_port)

            if out_port and in_port:
                out_port.connect_to(in_port)

        print(f"Imported graph: {filepath}")

    #this is a helper function for the import function above
    def _find_port_by_name(self, ports_dict, name):
        for port in ports_dict.values():
            if port.name() == name:
                return port
        return None

    def on_node_selected(self, node):
        """
        Called whenever the user clicks/selects a node.
        """

        # If we're in remove mode, delete the clicked node.
        if self.click_mode == "remove":
            print(f"Removing node: {node.name()}")
            self.graph.delete_nodes([node])

            # Exit remove mode after deleting one node.
            self.click_mode = None

            # Clear the inspector.
            self.inspector.set_node(None)

            self.last_action = self.on_node_selected
            return

        self.inspector.set_node(node)

    #a function to set the mode of the next click
    def set_mode(self, mode):

        self.click_mode = mode


    # =========================
    # ON CLOSE FUNCTION
    # =========================
    #basically just checks with the user thaty actually want to close
    def closeEvent(self, event):
        reply = QMessageBox.question(
            self,
            "Confirm Exit",
            "Are you sure you want to close the application?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

    def confirm_exit(self):

        reply = QMessageBox.question(
            self,
            "Confirm Exit",
            "Are you sure you want to close the application?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.close()

    #this next function handles selecting the system and testcases when you want to run the simulation
    def open_two_file_dialog(self):
        """
        Opens a dialog that allows the user to select two files.
        When the Run button is pressed, the selected file paths are
        printed to the console. Replace the print statements with
        your own processing function later.
        """

        dialog = QDialog(self)
        dialog.setWindowTitle("Select Input Files")
        dialog.setFixedWidth(600)

        layout = QVBoxLayout(dialog)

        # -------------------------
        # File 1
        # -------------------------
        layout.addWidget(QLabel("System Input File:"))

        file1_row = QHBoxLayout()

        file1_edit = QLineEdit()
        file1_edit.setReadOnly(True)

        file1_browse = QPushButton("Browse")

        def browse_file1():
            filename, _ = QFileDialog.getOpenFileName(
                self,
                "Select System Input File",
                "",
                "All Files (*)"
            )
            if filename:
                file1_edit.setText(filename)

        file1_browse.clicked.connect(browse_file1)

        file1_row.addWidget(file1_edit)
        file1_row.addWidget(file1_browse)

        layout.addLayout(file1_row)

        # -------------------------
        # File 2
        # -------------------------
        layout.addWidget(QLabel("Testcase Input File:"))

        file2_row = QHBoxLayout()

        file2_edit = QLineEdit()
        file2_edit.setReadOnly(True)

        file2_browse = QPushButton("Browse")

        def browse_file2():
            filename, _ = QFileDialog.getOpenFileName(
                self,
                "Select Testcase Input File",
                "",
                "All Files (*)"
            )
            if filename:
                file2_edit.setText(filename)

        file2_browse.clicked.connect(browse_file2)

        file2_row.addWidget(file2_edit)
        file2_row.addWidget(file2_browse)

        layout.addLayout(file2_row)

        # -------------------------
        # Run button
        # -------------------------
        run_button = QPushButton("Run")

        def run_function():
            file1 = file1_edit.text()
            file2 = file2_edit.text()

            print("System Solver")
            print("System Input:", file1)
            print("Testcase Input:", file2)

            dialog.accept()

            main.main(file1, file2)


            

        run_button.clicked.connect(run_function)
        layout.addWidget(run_button)

        # Show the dialog
        dialog.exec()






# =========================
# RUN APP
# =========================

if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()



    sys.exit(app.exec())