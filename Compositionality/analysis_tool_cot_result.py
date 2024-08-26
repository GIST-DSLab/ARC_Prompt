import sys
import os
import gzip
import pickle
import json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QTabWidget, QTextEdit, QTableWidget, \
    QTableWidgetItem, QFileDialog, QHeaderView, QListWidget, QHBoxLayout, QComboBox, QPushButton
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt
from io import BytesIO
from model.tasks.arc import ARCTask  # ARCTask import
import copy

# 컬러맵 설정
cvals = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
colors = ["#000000", "#0074D9", "#FF4136", "#2ECC40", "#FFDC00", "#AAAAAA", "#F012BE", "#FF851B", "#7FDBFF", "#870C25"]
norm = plt.Normalize(min(cvals), max(cvals))
tuples = list(zip(map(norm, cvals), colors))
cmap = matplotlib.colors.LinearSegmentedColormap.from_list("", tuples)


def generate_image(grid):
    rows, cols = np.array(grid).shape
    fig, axs = plt.subplots(1, 1, figsize=(cols * 0.7, rows * 0.7))

    axs.set_xticks(np.arange(cols + 1) - 0.5, minor=True)
    axs.set_yticks(np.arange(rows + 1) - 0.5, minor=True)
    axs.tick_params(which='minor', size=0)
    axs.grid(True, which='minor', color='#555555', linewidth=1)
    axs.set_xticks([]);
    axs.set_yticks([])

    axs.imshow(np.array(grid), cmap=cmap, vmin=0, vmax=9)

    buf = BytesIO()
    plt.tight_layout()
    plt.savefig(buf, format='png')
    plt.close(fig)
    buf.seek(0)

    qimage = QImage.fromData(buf.getvalue())
    return qimage


class JsonViewer(QWidget):
    def __init__(self, json_data):
        super().__init__()
        self.json_data = json_data
        self.task = ARCTask()  # ARCTask 객체 생성
        self.initUI()

    def initUI(self):
        self.setWindowTitle('JSON Viewer')
        layout = QVBoxLayout(self)

        tabs = QTabWidget()
        layout.addWidget(tabs)

        # Problem 탭에 problem 정보와 함께 다른 정보도 포함
        problem_info = {
            'Problem': self.json_data.get('problem', ''),
            'Problem ID': self.json_data.get('problem_id', ''),
            'Correct': str(self.json_data.get('correct', ''))
        }
        problem_content = "\n".join([f"{key}: {value}" for key, value in problem_info.items()])
        tabs.addTab(self.createTextTab('Problem', problem_content), 'Problem')

        # DSL Step (기존 Step)
        tabs.addTab(self.createJsonStepsTab('DSL Steps', self.json_data['json'][0]), 'DSL Steps')

        # Input Grid
        tabs.addTab(self.createImageTab('Input Grid', self.json_data['input_grid'][0]), 'Input Grid')

        # Label Grid
        tabs.addTab(self.createImageTab('Label Grid', self.json_data['label_grid'][0]), 'Label Grid')

        # Prediction Grid (기존 Final Grid)
        tabs.addTab(self.createImageTab('Prediction Grid', self.json_data['final_grid'][0]), 'Prediction Grid')

        self.setLayout(layout)
        self.resize(800, 600)  # PKL File Selector와 동일한 사이즈로 설정

    def createTextTab(self, title, content):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        label = QLabel(title)
        text = QTextEdit()
        text.setReadOnly(True)

        if isinstance(content, list):
            content = "\n".join(content)
        else:
            content = str(content)

        text.setText(content)
        layout.addWidget(label)
        layout.addWidget(text)
        return widget

    def createImageTab(self, title, grid):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        label = QLabel(title)
        image_label = QLabel()

        qimage = generate_image(grid)
        pixmap = QPixmap.fromImage(qimage)
        image_label.setPixmap(pixmap)

        layout.addWidget(label)
        layout.addWidget(image_label)
        return widget

    def createJsonStepsTab(self, title, steps_data):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        label = QLabel(title)
        table = QTableWidget(len(steps_data)+1, 5)  # Object 열을 추가하여 열 수를 5개로 설정
        table.setHorizontalHeaderLabels(['Step', 'DSL', 'Object', 'Grid', 'Description'])

        # 컬럼 길이 조정
        table.setColumnWidth(0, 50)  # Step 컬럼의 길이 줄이기
        table.setColumnWidth(1, 150)  # DSL 컬럼의 길이
        table.setColumnWidth(2, 150)  # Object 컬럼
        table.setColumnWidth(3, 150)  # Grid 컬럼
        table.setColumnWidth(4, 350)  # Description 컬럼의 길이 늘리기

        temp_state = copy.deepcopy(self.json_data['input_grid'][0])
        temp_object = copy.deepcopy(self.json_data['objects'][0])

        grid_image = generate_image(temp_state)
        pixmap = QPixmap.fromImage(grid_image)
        grid_item = QLabel()
        grid_item.setPixmap(pixmap)
        grid_item.setAlignment(Qt.AlignCenter)

        table.setItem(0, 0, QTableWidgetItem(str(0)))
        table.setItem(0, 1, QTableWidgetItem('init'))
        table.setItem(0, 2, QTableWidgetItem(json.dumps(temp_object)))  # Object 정보 추가
        table.setCellWidget(0, 3, grid_item)
        table.setItem(0, 4, QTableWidgetItem('Initial Grid'))
        table.setRowHeight(0, pixmap.height() + 10)

        for i, step in enumerate(steps_data):
            # Step과 DSL, Object, Description 추가
            table.setItem(i+1, 0, QTableWidgetItem(str(step['step'])))
            table.setItem(i+1, 1, QTableWidgetItem(step['dsl']))
            table.setItem(i+1, 2, QTableWidgetItem(json.dumps(temp_object)))  # Object 정보 추가
            table.setItem(i+1, 4, QTableWidgetItem(step['description']))

            # DSL 적용하여 Grid 이미지 생성
            try:
                temp_state, temp_object = self.task.env.step(temp_state, temp_object, step['dsl'], check_mode=True, analysis_mode=True)
                grid_image = generate_image(temp_state)
                pixmap = QPixmap.fromImage(grid_image)
                grid_item = QLabel()
                grid_item.setPixmap(pixmap)
                grid_item.setAlignment(Qt.AlignCenter)
                table.setCellWidget(i+1, 3, grid_item)

                # 이미지 크기에 맞춰 행 높이 조정
                table.setRowHeight(i+1, pixmap.height() + 10)  # 이미지 크기 + 여유 공간
            except Exception as e:
                table.setItem(i+1, 3, QTableWidgetItem(f"Error: {e}"))

        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(label)
        layout.addWidget(table)
        return widget


class FileSelector(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('PKL File Selector')
        main_layout = QVBoxLayout(self)

        # Directory 선택 및 필터링 옵션 레이아웃
        dir_layout = QHBoxLayout()

        self.directoryLabel = QLabel('No directory selected')
        self.selectDirButton = QPushButton('Select Directory')
        self.selectDirButton.clicked.connect(self.select_directory)

        self.filterBox = QComboBox()
        self.filterBox.addItem("All")
        self.filterBox.addItem("True")
        self.filterBox.addItem("False")
        self.filterBox.currentIndexChanged.connect(self.apply_filter)

        dir_layout.addWidget(self.directoryLabel)
        dir_layout.addWidget(self.selectDirButton)
        dir_layout.addWidget(self.filterBox)

        # 파일 목록 및 내용 표시 레이아웃
        self.fileListWidget = QTableWidget()
        self.fileListWidget.setColumnCount(2)
        self.fileListWidget.setHorizontalHeaderLabels(['File Name', 'Correct'])
        self.fileListWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.fileListWidget.itemClicked.connect(self.load_selected_pkl)

        main_layout.addLayout(dir_layout)
        main_layout.addWidget(self.fileListWidget)

        self.setLayout(main_layout)
        self.resize(800, 600)

    def select_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Directory")
        if directory:
            self.scan_directory_for_pkl(directory)
            self.directoryLabel.setText(f'Selected Directory: {directory}')
            self.directory = directory

    def scan_directory_for_pkl(self, directory):
        self.fileListWidget.setRowCount(0)
        self.pkl_files = []
        self.correct_values = []

        for pkl_file in os.listdir(directory):
            if pkl_file.endswith('.pkl'):
                file_path = os.path.join(directory, pkl_file)
                try:
                    with gzip.open(file_path, 'rb') as f:
                        json_data = pickle.load(f)
                        correct_value = json_data.get('correct', [None])[0]  # 'correct' 값을 가져옴
                        self.pkl_files.append((pkl_file, correct_value))
                except (OSError, pickle.UnpicklingError) as e:
                    print(f"Failed to load {pkl_file}: {e}")

        self.display_pkl_files()

    def display_pkl_files(self):
        filter_option = self.filterBox.currentText()
        filtered_files = [item for item in self.pkl_files if filter_option == "All" or str(item[1]) == filter_option]

        self.fileListWidget.setRowCount(len(filtered_files))
        for row, (file_name, correct_value) in enumerate(filtered_files):
            self.fileListWidget.setItem(row, 0, QTableWidgetItem(file_name))
            self.fileListWidget.setItem(row, 1, QTableWidgetItem(str(correct_value)))

    def apply_filter(self):
        self.display_pkl_files()

    def load_selected_pkl(self, item):
        row = item.row()
        file_name = self.fileListWidget.item(row, 0).text()
        file_path = os.path.join(self.directory, file_name)

        with gzip.open(file_path, 'rb') as f:
            json_data = pickle.load(f)

        self.json_viewer = JsonViewer(json_data)
        self.json_viewer.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    file_selector = FileSelector()
    file_selector.show()
    sys.exit(app.exec_())
