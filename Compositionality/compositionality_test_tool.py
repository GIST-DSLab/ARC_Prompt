import sys
import numpy as np
import pandas as pd
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QGridLayout, QPushButton, QLabel, QFrame, QSpacerItem, QSizePolicy,
                             QVBoxLayout, QHBoxLayout, QScrollArea, QProgressBar, QLineEdit, QDialog, QDialogButtonBox, QCheckBox)
from PyQt5.QtGui import QPainter, QBrush, QColor, QPen
from PyQt5.QtCore import Qt, pyqtSignal
import json
import os
from model.tasks.arc import ARCTask

MAXSTEPS = 10

def load_arc_data(file_path):
    with open(file_path, 'r') as f:
        data = json.load(f)
    return data

class UserDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('User ID')
        self.layout = QVBoxLayout()
        self.label = QLabel('Enter your User ID:')
        self.user_id_input = QLineEdit()
        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.user_id_input)
        self.layout.addWidget(self.button_box)
        self.setLayout(self.layout)

    def get_user_id(self):
        return self.user_id_input.text()

class GridWidget(QWidget):
    data_changed = pyqtSignal(np.ndarray)
    position_selected = pyqtSignal(list)
    object_selected = pyqtSignal(str)

    def __init__(self, grid_data, color_palette, editable=True, mode='normal'):
        super().__init__()
        self.grid_data = grid_data
        self.color_palette = color_palette
        self.editable = editable
        self.cell_size = 10 if mode == 'normal' else 20
        self.selected_positions = []
        self.selected_object = None
        self.setMinimumSize(self.grid_data.shape[1] * self.cell_size, 
                            self.grid_data.shape[0] * self.cell_size)
        self.gridChanged = pyqtSignal(np.ndarray)

    def update_grid_size(self, grid_data):
        self.grid_data = grid_data
        self.setMinimumSize(self.grid_data.shape[1] * self.cell_size, 
                            self.grid_data.shape[0] * self.cell_size)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        try:
            if len(self.grid_data.shape) == 3 and self.grid_data.shape[0] == 1:
                self.grid_data = self.grid_data.reshape(self.grid_data.shape[1], self.grid_data.shape[2])

            if not issubclass(self.grid_data.dtype.type, np.integer):
                self.grid_data = self.grid_data.astype(int)

            for i in range(self.grid_data.shape[0]):
                for j in range(self.grid_data.shape[1]):
                    try:
                        color_index = int(self.grid_data[i, j])
                        color = QColor(self.color_palette.colors[color_index])
                        painter.setBrush(QBrush(color))
                        painter.drawRect(j * self.cell_size, i * self.cell_size, self.cell_size, self.cell_size)
                    except IndexError:
                        painter.setBrush(QBrush(QColor("#FFFFFF")))
                        painter.drawRect(j * self.cell_size, i * self.cell_size, self.cell_size, self.cell_size)

            painter.setPen(QPen(QColor("#555555"), 1, Qt.SolidLine))
            for x in range(self.grid_data.shape[1] + 1):
                painter.drawLine(x * self.cell_size, 0, x * self.cell_size, self.grid_data.shape[0] * self.cell_size)
            for y in range(self.grid_data.shape[0] + 1):
                painter.drawLine(0, y * self.cell_size, self.grid_data.shape[1] * self.cell_size, y * self.cell_size)

            for pos in self.selected_positions:
                y, x = pos
                if 0 <= y < self.grid_data.shape[0] and 0 <= x < self.grid_data.shape[1]:
                    painter.setPen(QPen(QColor("#FFFFFF"), 3, Qt.SolidLine))
                    color_index = int(self.grid_data[y, x])
                    color = QColor(self.color_palette.colors[color_index])
                    painter.setBrush(QBrush(color))
                    painter.drawRect(x * self.cell_size, y * self.cell_size, self.cell_size, self.cell_size)

            if self.selected_object:
                painter.setPen(QPen(QColor("#FFFFFF"), 3, Qt.SolidLine))
                obj_coords = self.selected_object
                for y, x in obj_coords:
                    if 0 <= y < self.grid_data.shape[0] and 0 <= x < self.grid_data.shape[1]:
                        color_index = int(self.grid_data[y, x])
                        color = QColor(self.color_palette.colors[color_index])
                        painter.setBrush(QBrush(color))
                        painter.drawRect(x * self.cell_size, y * self.cell_size, self.cell_size, self.cell_size)
        finally:
            painter.end()

    def mousePressEvent(self, event):
        if not self.editable:
            return
        x = event.x() // self.cell_size
        y = event.y() // self.cell_size

        if self.selected_object:
            self.selected_object = None
            self.object_selected.emit(None)

        if 0 <= x < self.grid_data.shape[1] and 0 <= y < self.grid_data.shape[0]:
            if (y, x) in self.selected_positions:
                self.selected_positions.remove((y, x))
            else:
                modifiers = QApplication.keyboardModifiers()
                if modifiers == Qt.ShiftModifier or modifiers == Qt.ControlModifier:
                    self.selected_positions.append((y, x))
                    if len(self.selected_positions) > 2:
                        self.selected_positions.pop(0)
                else:
                    self.selected_positions = [(y, x)]
            self.position_selected.emit(self.selected_positions)
            self.update()

class ColorPalette(QWidget):
    color_selected = pyqtSignal(int)

    def __init__(self, colors):
        super().__init__()
        self.colors = colors
        self.selected_color = -1
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout(self)
        self.color_buttons = []
        grid_layout = QGridLayout()
        for i, color in enumerate(self.colors):
            button = QPushButton()
            button.setStyleSheet(f"background-color: {color}")
            button.clicked.connect(lambda ch, col=i: self.select_color(col))
            self.color_buttons.append(button)
            grid_layout.addWidget(button, 0, i)
        self.selected_color_label = QLabel("Selected Color: ")
        self.selected_color_display = QLabel()
        self.selected_color_display.setFixedHeight(30)
        layout.addLayout(grid_layout)
        layout.addWidget(self.selected_color_label)
        layout.addWidget(self.selected_color_display)
        self.setLayout(layout)

    def select_color(self, color_index):
        self.selected_color = color_index
        self.color_selected.emit(self.selected_color)
        self.update_selected_color_label()

    def update_selected_color_label(self):
        if self.selected_color == -1:
            self.selected_color_label.setText("Selected Color: ")
            self.selected_color_display.setStyleSheet("background-color: none")
        else:
            selected_color = self.colors[self.selected_color]
            self.selected_color_label.setText(f"Selected Color: {selected_color}")
            self.selected_color_display.setStyleSheet(f"background-color: {selected_color}")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.data = None
        self.user_id = None
        self.problem_index = 0
        self.current_problem = None
        self.example_widgets = []
        self.temp_state = None
        self.objects = {}
        self.selected_object = None
        self.selected_positions = []
        self.arc_task = ARCTask()
        self.selected_color = -1
        self.steps = 0
        self.dsl = []  # To store the list of used functions
        self.exercise_problem_index = 0  # Index for exercise problems
        self.main_problem_index = 0  # Index for main problems
        self.current_test_type = None  # To store the current test type (exercise or main)

        self.user_dialog = UserDialog()
        if self.user_dialog.exec_() == QDialog.Accepted:
            self.user_id = self.user_dialog.get_user_id()
            self.show_test_selection()
        else:
            sys.exit()

    def show_test_selection(self):
        self.setWindowTitle('Test Selection')
        self.setGeometry(300, 300, 400, 200)

        layout = QVBoxLayout()
        widget = QWidget(self)
        self.setCentralWidget(widget)
        widget.setLayout(layout)

        exercise_test_button = QPushButton('Exercise Test', self)
        exercise_test_button.clicked.connect(self.load_exercise_test)

        main_test_button = QPushButton('Main Test', self)
        main_test_button.clicked.connect(self.load_main_test)

        layout.addWidget(QLabel(f'Welcome, {self.user_id}'))
        layout.addWidget(exercise_test_button)
        layout.addWidget(main_test_button)

        self.show()

    def load_exercise_test(self):
        self.data = load_arc_data('data/exercise_arc.json')
        self.current_test_type = 'exercise'
        self.problem_index = self.exercise_problem_index
        self.initUI()

    def load_main_test(self):
        self.data = load_arc_data('data/arc.json')
        self.current_test_type = 'main'
        self.problem_index = self.main_problem_index
        self.initUI()

    def initUI(self):
        self.setWindowTitle('ARC Test Tool')
        self.setGeometry(300, 300, 2600, 1800)
        colors = ["#000000", "#0074D9", "#FF4136", "#2ECC40", "#FFDC00", "#AAAAAA", "#F012BE", "#FF851B", "#7FDBFF", "#870C25"]
        self.color_palette = ColorPalette(colors)
        self.color_palette.color_selected.connect(self.update_selected_color)

        main_layout = QVBoxLayout()
        widget = QWidget(self)
        self.setCentralWidget(widget)
        widget.setLayout(main_layout)

        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximum(len(self.data))
        self.progress_bar.setValue(self.problem_index + 1)
        self.progress_bar.setFormat('%v / %m')
        main_layout.addWidget(self.progress_bar)

        content_layout = QHBoxLayout()
        main_layout.addLayout(content_layout)

        self.example_scroll_area = QScrollArea()
        self.example_scroll_area.setWidgetResizable(True)
        self.example_scroll_widget = QWidget()
        self.example_layout = QVBoxLayout(self.example_scroll_widget)
        self.example_scroll_area.setWidget(self.example_scroll_widget)

        self.test_scroll_area = QScrollArea()
        self.test_scroll_area.setWidgetResizable(True)
        self.test_scroll_widget = QWidget()
        self.test_layout = QVBoxLayout(self.test_scroll_widget)
        self.test_scroll_area.setWidget(self.test_scroll_widget)

        self.input_widget = GridWidget(np.zeros((10, 10)), self.color_palette, editable=False, mode='test')
        self.output_widget = GridWidget(np.zeros((10, 10)), self.color_palette, editable=True, mode='test')
        self.output_widget.data_changed.connect(self.update_temp_state)
        self.output_widget.position_selected.connect(self.store_selected_positions)

        self.test_layout.addWidget(QLabel('Test Input'))
        self.test_layout.addWidget(self.center_widget(self.input_widget))
        self.test_layout.addWidget(QLabel('Your Solution (Test output)'))
        self.test_layout.addWidget(self.center_widget(self.output_widget))

        # Checkboxes 추가
        checkbox_layout = QHBoxLayout()
        self.mistake_checkbox = QCheckBox('Mistake')
        self.object_incompleteness_checkbox = QCheckBox('Object Incompleteness')
        self.dsl_incompleteness_checkbox = QCheckBox('DSL Incompleteness')

        # 스타일 시트로 글씨 크기 조정 및 굵게 설정
        checkbox_style = "font-size: 24px;"
        self.mistake_checkbox.setStyleSheet(checkbox_style)
        self.object_incompleteness_checkbox.setStyleSheet(checkbox_style)
        self.dsl_incompleteness_checkbox.setStyleSheet(checkbox_style)

        # 동일한 간격으로 체크박스 배치
        checkbox_layout.addWidget(self.mistake_checkbox)
        checkbox_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        checkbox_layout.addWidget(self.object_incompleteness_checkbox)
        checkbox_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        checkbox_layout.addWidget(self.dsl_incompleteness_checkbox)
        self.test_layout.addLayout(checkbox_layout)

        self.step_label = QLabel(f'Step: {self.steps}')
        self.step_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        self.test_layout.addWidget(self.step_label)

        self.test_layout.addWidget(self.color_palette)

        self.add_transformation_buttons()

        self.object_scroll_area = QScrollArea()
        self.object_scroll_area.setWidgetResizable(True)
        self.object_scroll_widget = QWidget()
        self.object_layout = QVBoxLayout(self.object_scroll_widget)
        self.object_scroll_area.setWidget(self.object_scroll_widget)

        self.object_widgets = {}

        content_layout.addWidget(self.example_scroll_area)
        content_layout.addWidget(self.test_scroll_area)
        content_layout.addWidget(self.object_scroll_area)

        self.load_problem()
        self.show()

    def center_widget(self, widget):
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.addStretch()
        layout.addWidget(widget, 0, Qt.AlignCenter)
        layout.addStretch()
        return container

    def update_selected_color(self, color_index):
        self.selected_color = color_index
        self.color_palette.update_selected_color_label()

    def store_selected_positions(self, positions):
        if self.selected_object:
            self.selected_object = None
            self.output_widget.selected_object = None
            self.output_widget.update()
        self.selected_positions = positions

    def select_object(self, obj_name):
        if self.selected_positions:
            self.selected_positions = []
            self.output_widget.selected_positions = self.selected_positions
            self.output_widget.position_selected.connect(self.store_selected_positions) 

        if self.selected_object == obj_name:
            self.selected_object = None
            self.output_widget.selected_object = None
        else:
            self.selected_object = obj_name
            self.output_widget.selected_object = self.objects[obj_name]
        self.display_object_on_output_widget()

    def display_object_on_output_widget(self):
        self.output_widget.selected_object = self.objects.get(self.selected_object, None)
        self.output_widget.update()

    def add_transformation_buttons(self):
        transformation_layout = QGridLayout()
        buttons = [
            ('Rotate Left', self.rotate_left),
            ('Rotate Right', self.rotate_right),
            ('Flip Vertical', self.flip_vertical),
            ('Flip Horizontal', self.flip_horizontal),
            ('Move Right', self.move_right),
            ('Move Left', self.move_left),
            ('Move Up', self.move_up),
            ('Move Down', self.move_down),
            ('Rotate Right Obj', self.rotate_right_obj),
            ('Rotate Left Obj', self.rotate_left_obj),
            ('Flip Vertical Obj', self.vertical_flip_obj),
            ('Flip Horizontal Obj', self.horizontal_flip_obj),
            ('X Line', self.x_line),
            ('Horizontal Line', self.horizontal_line),
            ('Vertical Line', self.vertical_line),
            ('Diagonal Line', self.diagonal_line),
            ('Object Color', self.obj_color),
            ('Pixel Color', self.pixel_color),
            ('Complete', self.complete)
        ]
        row, col = 0, 0
        for label, function in buttons:
            button = QPushButton(label, self)
            if label == 'Complete':
                button.setStyleSheet("background-color: red; color: white; font-weight: bold;")
            button.clicked.connect(self.create_step_increment_function(function, function.__name__))
            transformation_layout.addWidget(button, row, col)
            col += 1
            if col == 5:
                col = 0
                row += 1
        self.test_layout.addLayout(transformation_layout)

    def create_step_increment_function(self, func, func_name):
        def wrapper():
            if func != self.complete:  # complete 함수가 호출된 후에는 steps를 증가시키지 않도록 함
                func()
                self.steps += 1
                self.step_label.setText(f'Step: {self.steps}')
                self.dsl.append(func_name)  # Record the used function
                if self.steps >= MAXSTEPS:
                    self.load_next_problem()
            else:
                self.dsl.append(func_name)
                self.steps += 1
                func()
        return wrapper

    def change_color(self, color_index):
        if self.selected_positions and len(self.selected_positions) < 2:
            y, x = self.selected_positions[-1]
            self.temp_state[y, x] = color_index
            self.output_widget.update_grid_size(self.temp_state)
            self.output_widget.update()

    def pixel_color(self):
        if self.selected_color == -1:
            return
        if self.temp_state is not None and self.selected_positions and len(self.selected_positions) == 1:
            y, x = self.selected_positions[-1]
            self.temp_state[y, x] = self.selected_color
            self.output_widget.update_grid_size(self.temp_state)
            self.output_widget.update()
            self.output_widget.selected_positions = self.selected_positions
            self.output_widget.update()

    def remove_overlapping_positions(self, special_mode=False):
        if self.selected_object is None and not special_mode:
            return

        if special_mode:
            pass
        else:
            for obj_name, coordinates in self.objects.items():
                if obj_name != self.selected_object:
                    new_coords = []
                    for coord in coordinates:
                        if self.temp_state[coord[0], coord[1]] != self.color_palette.colors.index("#000000") and coord in self.objects[self.selected_object]:
                            continue
                        new_coords.append(coord)
                    self.objects[obj_name] = new_coords

    def rotate_left(self):
        if self.temp_state is not None:
            self.temp_state, self.objects = self.arc_task.env.step(self.temp_state, self.objects, 'rotate_left_state(temp_state)')
            # self.remove_overlapping_positions()
            self.update_display_objects()
            self.display_object_on_output_widget()
            self.output_widget.update_grid_size(self.temp_state)
            self.output_widget.update()

    def rotate_right(self):
        if self.temp_state is not None:
            self.temp_state, self.objects = self.arc_task.env.step(self.temp_state, self.objects, 'rotate_right_state(temp_state)')
            # self.remove_overlapping_positions()
            self.update_display_objects()
            self.display_object_on_output_widget()
            self.output_widget.update_grid_size(self.temp_state)
            self.output_widget.update()

    def flip_vertical(self):
        if self.temp_state is not None:
            self.temp_state, self.objects = self.arc_task.env.step(self.temp_state, self.objects, 'vertical_flip(temp_state)')
            # self.remove_overlapping_positions()
            self.update_display_objects()
            self.display_object_on_output_widget()
            self.output_widget.update_grid_size(self.temp_state)
            self.output_widget.update()

    def flip_horizontal(self):
        if self.temp_state is not None:
            self.temp_state, self.objects = self.arc_task.env.step(self.temp_state, self.objects, 'horizontal_flip(temp_state)')
            # self.remove_overlapping_positions()
            self.update_display_objects()
            self.display_object_on_output_widget()
            self.output_widget.update_grid_size(self.temp_state)
            self.output_widget.update()

    def move_right(self):
        if self.temp_state is not None and self.selected_object:
            self.temp_state, self.objects = self.arc_task.env.step(self.temp_state, self.objects, f'move_right(self.temp_state, {self.selected_object})')
            # self.remove_overlapping_positions()
            self.update_display_objects()
            self.display_object_on_output_widget()
            self.output_widget.update_grid_size(self.temp_state)
            self.output_widget.update()

    def move_left(self):
        if self.temp_state is not None and self.selected_object:
            self.temp_state, self.objects = self.arc_task.env.step(self.temp_state, self.objects, f'move_left(self.temp_state, {self.selected_object})')
            # self.remove_overlapping_positions()
            self.update_display_objects()
            self.display_object_on_output_widget()
            self.output_widget.update_grid_size(self.temp_state)
            self.output_widget.update()

    def move_up(self):
        if self.temp_state is not None and self.selected_object:
            self.temp_state, self.objects = self.arc_task.env.step(self.temp_state, self.objects, f'move_up(self.temp_state, {self.selected_object})')
            # self.remove_overlapping_positions()
            self.update_display_objects()
            self.display_object_on_output_widget()
            self.output_widget.update_grid_size(self.temp_state)
            self.output_widget.update()

    def move_down(self):
        if self.temp_state is not None and self.selected_object:
            self.temp_state, self.objects = self.arc_task.env.step(self.temp_state, self.objects, f'move_down(self.temp_state, {self.selected_object})')
            # self.remove_overlapping_positions()
            self.update_display_objects()
            self.display_object_on_output_widget()
            self.output_widget.update_grid_size(self.temp_state)
            self.output_widget.update()

    def rotate_right_obj(self):
        if self.temp_state is not None and self.selected_object:
            self.temp_state, self.objects = self.arc_task.env.step(self.temp_state, self.objects, f'rotate_right_obj(self.temp_state, {self.selected_object})')
            # self.remove_overlapping_positions()
            self.update_display_objects()
            self.display_object_on_output_widget()
            self.output_widget.update_grid_size(self.temp_state)
            self.output_widget.update()

    def rotate_left_obj(self):
        if self.temp_state is not None and self.selected_object:
            self.temp_state, self.objects = self.arc_task.env.step(self.temp_state, self.objects, f'rotate_left_obj(self.temp_state, {self.selected_object})')
            # self.remove_overlapping_positions()
            self.update_display_objects()
            self.display_object_on_output_widget()
            self.output_widget.update_grid_size(self.temp_state)
            self.output_widget.update()

    def vertical_flip_obj(self):
        if self.temp_state is not None and self.selected_object:
            self.temp_state, self.objects = self.arc_task.env.step(self.temp_state, self.objects, f'vertical_flip_obj(self.temp_state, {self.selected_object})')
            # self.remove_overlapping_positions()
            self.update_display_objects()
            self.display_object_on_output_widget()
            self.output_widget.update_grid_size(self.temp_state)
            self.output_widget.update()

    def horizontal_flip_obj(self):
        if self.temp_state is not None and self.selected_object:
            self.temp_state, self.objects = self.arc_task.env.step(self.temp_state, self.objects, f'horizontal_flip_obj(self.temp_state, {self.selected_object})')
            # self.remove_overlapping_positions()
            self.update_display_objects()
            self.display_object_on_output_widget()
            self.output_widget.update_grid_size(self.temp_state)
            self.output_widget.update()

    def x_line(self):
        if self.selected_color == -1:
            return
        if self.temp_state is not None and self.selected_positions and len(self.selected_positions) == 1:
            y, x = self.selected_positions[-1]
            self.temp_state, self.objects = self.arc_task.env.step(self.temp_state, self.objects, f'X_line(self.temp_state, {y}, {x}, {self.selected_color})')
            # self.remove_overlapping_positions(special_mode=True)
            self.update_display_objects()
            self.display_object_on_output_widget()
            self.output_widget.update_grid_size(self.temp_state)
            self.output_widget.update()

    def horizontal_line(self):
        if self.selected_color == -1:
            return
        if self.temp_state is not None and len(self.selected_positions) == 2:
            y1, x1 = self.selected_positions[0]
            y2, x2 = self.selected_positions[1]
            self.temp_state, self.objects = self.arc_task.env.step(self.temp_state, self.objects, f'horizontal_line(self.temp_state, {y1}, {x1}, {y2}, {x2}, {self.selected_color})')
            # self.remove_overlapping_positions(special_mode=True)
            self.update_display_objects()
            self.display_object_on_output_widget()
            self.output_widget.update_grid_size(self.temp_state)
            self.output_widget.update()

    def vertical_line(self):
        if self.selected_color == -1:
            return
        if self.temp_state is not None and len(self.selected_positions) == 2:
            y1, x1 = self.selected_positions[0]
            y2, x2 = self.selected_positions[1]
            self.temp_state, self.objects = self.arc_task.env.step(self.temp_state, self.objects, f'vertical_line(self.temp_state, {y1}, {x1}, {y2}, {x2}, {self.selected_color})')
            # self.remove_overlapping_positions(special_mode=True)
            self.update_display_objects()
            self.display_object_on_output_widget()
            self.output_widget.update_grid_size(self.temp_state)
            self.output_widget.update()

    def diagonal_line(self):
        if self.selected_color == -1:
            return
        if self.temp_state is not None and len(self.selected_positions) == 2:
            y1, x1 = self.selected_positions[0]
            y2, x2 = self.selected_positions[1]
            self.temp_state, self.objects = self.arc_task.env.step(self.temp_state, self.objects, f'diagonal_line(self.temp_state, {y1}, {x1}, {y2}, {x2}, {self.selected_color})')
            # self.remove_overlapping_positions(special_mode=True)
            self.update_display_objects()
            self.display_object_on_output_widget()
            self.output_widget.update_grid_size(self.temp_state)
            self.output_widget.update()

    def obj_color(self):
        if self.selected_color == -1:
            return
        if self.temp_state is not None and self.selected_object:
            self.temp_state, self.objects = self.arc_task.env.step(self.temp_state, self.objects, f'obj_color(self.temp_state, {self.selected_object}, {self.selected_color})')
            # self.remove_overlapping_positions()
            self.update_display_objects()
            self.display_object_on_output_widget()
            self.output_widget.update_grid_size(self.temp_state)
            self.output_widget.update()

    def complete(self):
        if self.temp_state is not None:
            self.temp_state, self.objects = self.arc_task.env.step(self.temp_state, self.objects, 'complete(self.temp_state)')
            # self.remove_overlapping_positions()
            self.update_display_objects()
            self.display_object_on_output_widget()
            self.output_widget.update_grid_size(self.temp_state)
            self.output_widget.update()

            self.steps = 0  # Add this line to reset steps
            self.step_label.setText(f'Step: {self.steps}')  # Update the step label

            if self.problem_index + 1 >= len(self.data):  # 마지막 문제인 경우
                self.log_data() 
                self.show_test_selection()  # 이전 Main Test와 Exercise Test 보여주는 부분으로 돌아감
            else:
                self.load_next_problem()

    def log_data(self):
        correct_output = self.current_problem['test'][0]['output']
        user_output = self.temp_state.tolist()
        correct = (user_output == correct_output)
        log_entry = {
            'user_id': self.user_id,
            'test_type': self.current_test_type,
            'problem': self.problem_index,
            'dsl': self.dsl,
            'steps': self.steps,
            'correct': correct,
            'output': user_output,
            'mistake': self.mistake_checkbox.isChecked(),
            'object_incompleteness': self.object_incompleteness_checkbox.isChecked(),
            'dsl_incompleteness': self.dsl_incompleteness_checkbox.isChecked()
        }
        df = pd.DataFrame([log_entry])
        if not os.path.isfile('result/human_log.csv'):
            df.to_csv('result/human_log.csv', mode='w', header=True, index=False)
        else:
            df.to_csv('result/human_log.csv', mode='a', header=False, index=False)
        self.dsl = []  # Reset the dsl list for the next problem

    def load_problem(self):
        if self.problem_index >= len(self.data):
            print("No more problems to load")
            return
        self.current_problem = self.data[self.problem_index]
        self.progress_bar.setValue(self.problem_index + 1)
        self.progress_bar.setFormat(f'{self.problem_index + 1} / {len(self.data)}')

        self.selected_object = None
        self.selected_positions = []
        self.input_widget.selected_positions = []
        self.output_widget.selected_positions = []
        self.input_widget.selected_object = None
        self.output_widget.selected_object = None
        self.steps = 0
        self.step_label.setText(f'Step: {self.steps}')
        self.update_display()

        self.reset_checkboxes() 
        self.reset_selected_color()  # Reset selected color when loading a new problem

    def reset_selected_color(self):
        self.selected_color = -1
        self.color_palette.selected_color = -1
        self.color_palette.update_selected_color_label()

    def load_next_problem(self):
        self.log_data()  # Log the data before moving to the next problem

        # Update the correct index based on the current test type
        if self.current_test_type == 'exercise':
            self.exercise_problem_index += 1
            self.problem_index = self.exercise_problem_index
        elif self.current_test_type == 'main':
            self.main_problem_index += 1
            self.problem_index = self.main_problem_index

        self.load_problem()
    
    def reset_checkboxes(self):
        self.mistake_checkbox.setChecked(False)
        self.object_incompleteness_checkbox.setChecked(False)
        self.dsl_incompleteness_checkbox.setChecked(False)

    def update_display(self):
        while self.example_layout.count():
            layout_item = self.example_layout.takeAt(0)
            if layout_item.widget():
                layout_item.widget().deleteLater()
            elif layout_item.layout():
                self.clear_layout(layout_item.layout())

        problem_data = self.current_problem
        ex_in = [example['input'] for example in problem_data['train']]
        ex_out = [example['output'] for example in problem_data['train']]
        tt_in = [example['input'] for example in problem_data['test']]
        tt_out = [example['output'] for example in problem_data['test']]
        self.objects = problem_data['test'][0]['objects']

        for i in range(len(ex_in)):
            input_grid = np.array(ex_in[i]) if not isinstance(ex_in[i], np.ndarray) else ex_in[i]
            output_grid = np.array(ex_out[i]) if not isinstance(ex_out[i], np.ndarray) else ex_out[i]

            example_layout = QHBoxLayout()

            input_container = QWidget()
            input_layout = QVBoxLayout(input_container)
            input_layout.addWidget(QLabel(f'Example {i+1}: Input'), 0, Qt.AlignCenter)
            input_layout.addWidget(self.center_widget(GridWidget(input_grid, self.color_palette, editable=False)))

            output_container = QWidget()
            output_layout = QVBoxLayout(output_container)
            output_layout.addWidget(QLabel(f'Example {i+1}: Output'), 0, Qt.AlignCenter)
            output_layout.addWidget(self.center_widget(GridWidget(output_grid, self.color_palette, editable=False)))

            example_layout.addWidget(input_container)
            example_layout.addWidget(output_container)

            self.example_layout.addLayout(example_layout)

            if i < len(ex_in) - 1:
                separator = QFrame()
                separator.setFrameShape(QFrame.HLine)
                separator.setFrameShadow(QFrame.Sunken)
                self.example_layout.addWidget(separator)

        if tt_in:
            self.temp_state = np.array(tt_in[0]) if not isinstance(tt_in[0], np.ndarray) else tt_in[0]
            self.input_widget.update_grid_size(np.array(tt_in[0]) if not isinstance(tt_in[0], np.ndarray) else tt_in[0])
            self.output_widget.update_grid_size(np.array(tt_in[0]) if not isinstance(tt_in[0], np.ndarray) else tt_in[0])
            self.input_widget.update()
            self.output_widget.update()

        self.update_display_objects()

    def update_display_objects(self):
        while self.object_layout.count():
            layout_item = self.object_layout.takeAt(0)
            widget = layout_item.widget()
            if widget:
                widget.deleteLater()
            elif layout_item.layout():
                self.clear_layout(layout_item.layout())

        self.object_widgets.clear()

        for obj_name, coordinates in self.objects.items():
            obj_layout = QVBoxLayout()
            obj_button = QPushButton(obj_name)
            obj_button.setStyleSheet("""
                QPushButton {
                    border: 2px solid black;
                    background-color: #FFA500;
                    color: black;
                    font-weight: bold;
                    padding: 10px;
                    text-align: center;
                }
                QPushButton:hover {
                    background-color: #FFB732;
                }
            """)
            obj_button.clicked.connect(lambda checked, name=obj_name: self.select_object(name))
            obj_layout.addWidget(obj_button)

            obj_grid = np.zeros_like(self.input_widget.grid_data)
            for y, x in coordinates:
                obj_grid[y, x] = self.temp_state[y, x]

            obj_widget = self.center_widget(GridWidget(obj_grid, self.color_palette, editable=False))
            obj_layout.addWidget(obj_widget)

            self.object_layout.addLayout(obj_layout)
            self.object_widgets[obj_name] = obj_widget

    def clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
            elif item.layout():
                self.clear_layout(item.layout())

    def update_temp_state(self, data):
        self.temp_state = data
        print("temp_state updated:", self.temp_state)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    sys.exit(app.exec_())
