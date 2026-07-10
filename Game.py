import sys
import json
import random
from datetime import datetime

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QGridLayout, QFrame, QStackedWidget, QListWidget,
    QSizePolicy, QDialog, QLineEdit, QMessageBox
)
from PyQt6.QtCore import (
    Qt, QRect, QPropertyAnimation, QParallelAnimationGroup, QEasingCurve, QTimer
)
from PyQt6.QtGui import QFont



def _compress_and_merge_row_with_sources(row_values, row_sources):
    new_vals = []
    new_srcs = []
    score_gain = 0
    k = 0
    while k < len(row_values):
        if k + 1 < len(row_values) and row_values[k] == row_values[k + 1]:
            merged_val = row_values[k] * 2
            merged_srcs = [row_sources[k], row_sources[k + 1]]
            new_vals.append(merged_val)
            new_srcs.append(merged_srcs)
            score_gain += merged_val
            k += 2
        else:
            new_vals.append(row_values[k])
            new_srcs.append([row_sources[k]])
            k += 1
    return new_vals, new_srcs, score_gain


def _simulate_left(grid):
    new_grid = [[0]*4 for _ in range(4)]
    moves = []
    score_gain = 0
    moved = False

    for i in range(4):
        vals = []
        srcs = []
        for j, v in enumerate(grid[i]):
            if v != 0:
                vals.append(v)
                srcs.append((i, j))
        if not vals:
            continue
        new_vals, new_srcs, gain = _compress_and_merge_row_with_sources(vals, srcs)
        score_gain += gain
        for idx, val in enumerate(new_vals):
            new_grid[i][idx] = val
        for k, src_list in enumerate(new_srcs):
            ti, tj = i, k
            for src in src_list:
                moves.append({
                    'from': src,
                    'to': (ti, tj),
                    'value': new_grid[ti][tj],
                    'merged': len(src_list) > 1
                })
    moved = (new_grid != grid)
    return new_grid, moved, score_gain, moves


def _simulate_right(grid):
    reflected = [row[::-1] for row in grid]
    new_ref, moved, score_gain, moves = _simulate_left(reflected)
    new_grid = [row[::-1] for row in new_ref]
    for mv in moves:
        fi, fj = mv['from']
        ti, tj = mv['to']
        mv['from'] = (fi, 3 - fj)
        mv['to'] = (ti, 3 - tj)
        mv['value'] = new_grid[ti][3 - tj]
    return new_grid, moved, score_gain, moves


def _simulate_up(grid):
    trans = [list(row) for row in zip(*grid)]
    new_trans, moved, score_gain, moves = _simulate_left(trans)
    new_grid = [list(row) for row in zip(*new_trans)]
    for mv in moves:
        fi, fj = mv['from']
        ti, tj = mv['to']
        mv['from'] = (fj, fi)
        mv['to'] = (tj, ti)
        mv['value'] = new_grid[tj][ti]
    return new_grid, moved, score_gain, moves


def _simulate_down(grid):
    trans = [list(row) for row in zip(*grid)]
    new_trans, moved, score_gain, moves = _simulate_right(trans)
    new_grid = [list(row) for row in zip(*new_trans)]
    for mv in moves:
        fi, fj = mv['from']
        ti, tj = mv['to']
        mv['from'] = (fj, fi)
        mv['to'] = (tj, ti)
        mv['value'] = new_grid[tj][ti]
    return new_grid, moved, score_gain, moves


def simulate_move_with_moves(grid, direction):
    if direction == 'left':
        return _simulate_left(grid)
    elif direction == 'right':
        return _simulate_right(grid)
    elif direction == 'up':
        return _simulate_up(grid)
    elif direction == 'down':
        return _simulate_down(grid)
    else:
        return grid, False, 0, []



class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.grid = [[0]*4 for _ in range(4)]
        self.score = 0
        self.best_score = self.load_best_score()
        self.game_over = False
        self.all_records = self.load_records()
        self.animating = False
        self._active_animations = []
        self.tile_widgets = {}

        self.setWindowTitle("Игра 2048 (с анимацией)")
        self.setMinimumSize(420, 520)
        self.setStyleSheet("background-color: #dcdcdc;")
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        self.init_menu()
        self.init_game_widget()
        self.init_records_widget()

        self.stacked_widget.setCurrentIndex(0)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    
    def init_menu(self):
        menu_widget = QWidget()
        menu_layout = QVBoxLayout()
        menu_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        menu_layout.setSpacing(30)

        title = QLabel("2048")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 72px; font-weight: bold; color: #776e65;")
        menu_layout.addWidget(title)

        start_btn = QPushButton("Начать игру")
        start_btn.setStyleSheet("""
            QPushButton {
                background-color: #8f7a66;
                color: #ffffff;
                font-size: 24px;
                font-weight: bold;
                padding: 20px 60px;
                border-radius: 15px;
                border: none;
                min-width: 250px;
            }
            QPushButton:hover { background-color: #9f8a76; }
        """)
        start_btn.clicked.connect(self.start_game)
        menu_layout.addWidget(start_btn)

        records_btn = QPushButton("Рекорды")
        records_btn.setStyleSheet(start_btn.styleSheet())
        records_btn.clicked.connect(self.open_records)
        menu_layout.addWidget(records_btn)

        menu_widget.setLayout(menu_layout)
        self.stacked_widget.addWidget(menu_widget)

    def init_game_widget(self):
        game_widget = QWidget()
        layout = QVBoxLayout()
        game_widget.setLayout(layout)

        top_layout = QHBoxLayout()
        home_btn = QPushButton("🏠")
        home_btn.setFixedSize(40, 40)
        home_btn.setStyleSheet("""
            QPushButton {
                background-color: #8f7a66;
                color: #ffffff;
                font-size: 16px;
                border-radius: 20px;
                border: none;
            }
            QPushButton:hover { background-color: #9f8a76; }
        """)
        home_btn.clicked.connect(self.home)
        top_layout.addWidget(home_btn)
        top_layout.addStretch()
        layout.addLayout(top_layout)

        self.scores_container = QWidget()
        self.scores_container.setStyleSheet("""
            background-color: #faf8ef;
            border-radius: 10px;
            padding: 8px 20px;
        """)
        self.scores_container.setMaximumWidth(350)
        self.scores_container.setMinimumWidth(200)
        self.scores_container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        scores_layout = QHBoxLayout()
        scores_layout.setSpacing(40)
        scores_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.scores_container.setLayout(scores_layout)

        score_block = QWidget()
        score_block_layout = QVBoxLayout()
        score_block_layout.setSpacing(2)
        score_block_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        score_block.setLayout(score_block_layout)

        self.score_label = QLabel("SCORE")
        self.score_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.score_label.setStyleSheet("font-size: 12px; font-weight: bold; color: #776e65; letter-spacing: 1px;")
        score_block_layout.addWidget(self.score_label)

        self.score_line = QLabel("0")
        self.score_line.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.score_line.setStyleSheet("font-size: 24px; font-weight: bold; color: #776e65;")
        score_block_layout.addWidget(self.score_line)

        best_block = QWidget()
        best_block_layout = QVBoxLayout()
        best_block_layout.setSpacing(2)
        best_block_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        best_block.setLayout(best_block_layout)

        self.best_label = QLabel("BEST")
        self.best_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.best_label.setStyleSheet("font-size: 12px; font-weight: bold; color: #776e65; letter-spacing: 1px;")
        best_block_layout.addWidget(self.best_label)

        self.best_score_line = QLabel(str(self.best_score))
        self.best_score_line.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.best_score_line.setStyleSheet("font-size: 24px; font-weight: bold; color: #776e65;")
        best_block_layout.addWidget(self.best_score_line)

        scores_layout.addWidget(score_block)
        scores_layout.addWidget(best_block)

        scores_wrapper = QHBoxLayout()
        scores_wrapper.addStretch()
        scores_wrapper.addWidget(self.scores_container)
        scores_wrapper.addStretch()
        layout.addLayout(scores_wrapper)

        field_container = QWidget()
        field_container_layout = QVBoxLayout()
        field_container_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        field_container.setLayout(field_container_layout)

        field = QFrame()
        field.setStyleSheet("background-color: #bbada0; border-radius: 10px;")
        field.setMaximumSize(500, 500)
        field.setMinimumSize(200, 200)
        field.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        grid = QGridLayout()
        grid.setSpacing(6)
        grid.setContentsMargins(6, 6, 6, 6)
        field.setLayout(grid)

        self.field = field
        self.grid_layout = grid

        self.cells = []
        for i in range(4):
            row = []
            for j in range(4):
                cell = QLabel()
                cell.setAlignment(Qt.AlignmentFlag.AlignCenter)
                cell.setStyleSheet("background-color: #fff8dc; font-size:30px; border-radius: 5px;")
                grid.addWidget(cell, i, j)
                row.append(cell)
            self.cells.append(row)

        field_container_layout.addWidget(field)
        layout.addWidget(field_container, stretch=1)

        self.overlay = QWidget(self.field)
        self.overlay.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.overlay.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.overlay.setStyleSheet("background: transparent;")
        self.overlay.setGeometry(self.field.rect())
        self.overlay.raise_()
        self.overlay.show()

        self.stacked_widget.addWidget(game_widget)

    def init_records_widget(self):
        records_widget = QWidget()
        records_layout = QVBoxLayout()
        records_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        records_layout.setSpacing(20)

        records_label = QLabel("Рекорды")
        records_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        records_label.setStyleSheet("font-size: 36px; font-weight: bold; color: #776e65;")
        records_layout.addWidget(records_label)

        self.records_list = QListWidget()
        self.records_list.setStyleSheet("""
            QListWidget {
                background-color: #faf8ef;
                border-radius: 10px;
                padding: 10px;
                font-size: 16px;
                color: #776e65;
                min-height: 300px;
                max-width: 400px;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #e0d6c8;
            }
            QListWidget::item:selected {
                background-color: #bbada0;
                color: #ffffff;
            }
        """)
        self.records_list.itemClicked.connect(self.on_record_selected)
        records_layout.addWidget(self.records_list)

        self.delete_btn = QPushButton("🗑 Удалить рекорд")
        self.delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: #ffffff;
                font-size: 16px;
                font-weight: bold;
                padding: 10px 30px;
                border-radius: 8px;
                border: none;
                min-width: 200px;
            }
            QPushButton:hover { background-color: #c0392b; }
            QPushButton:disabled { background-color: #95a5a6; }
        """)
        self.delete_btn.clicked.connect(self.delete_selected_record)
        self.delete_btn.setEnabled(False)
        records_layout.addWidget(self.delete_btn)

        back_btn = QPushButton("Назад")
        back_btn.setStyleSheet("""
            QPushButton {
                background-color: #8f7a66;
                color: #ffffff;
                font-size: 18px;
                padding: 10px 40px;
                border-radius: 10px;
                border: none;
            }
            QPushButton:hover { background-color: #9f8a76; }
        """)
        back_btn.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        records_layout.addWidget(back_btn)

        records_widget.setLayout(records_layout)
        self.stacked_widget.addWidget(records_widget)

    def load_best_score(self):
        try:
            with open("best_score.txt", "r") as f:
                return int(f.read())
        except:
            return 0

    def save_best_score(self):
        with open("best_score.txt", "w") as f:
            f.write(str(self.best_score))

    def update_best_score(self):
        if self.score > self.best_score:
            self.best_score = self.score
            self.best_score_line.setText(str(self.best_score))
            self.save_best_score()

    def load_records(self):
        try:
            with open("records.json", "r") as f:
                return json.load(f)
        except:
            return []

    def save_records(self):
        with open("records.json", "w") as f:
            json.dump(self.all_records, f)

    def update_records_list(self):
        self.records_list.clear()
        if not self.all_records:
            self.records_list.addItem("Нет рекордов")
            return
        for i, record in enumerate(self.all_records, 1):
            name = record.get('name', 'Игрок')
            text = f"{i}. {name} - {record['score']} очков  ({record['date']})"
            self.records_list.addItem(text)
        self.delete_btn.setEnabled(False)

    def on_record_selected(self, item):
        self.delete_btn.setEnabled(True)
        self.selected_record_index = self.records_list.currentRow()

    def delete_selected_record(self):
        if not hasattr(self, 'selected_record_index') or self.selected_record_index is None:
            return
        index = self.selected_record_index
        if 0 <= index < len(self.all_records):
            reply = QMessageBox.question(
                self,
                "Подтверждение удаления",
                f"Вы уверены, что хотите удалить этот рекорд?\n\n{self.records_list.currentItem().text()}",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                del self.all_records[index]
                self.save_records()
                self.update_records_list()
                self.delete_btn.setEnabled(False)
                self.selected_record_index = None

    def add_random_num(self, animate=True):
        if self.game_over:
            return
        empty = [(i, j) for i in range(4) for j in range(4) if self.grid[i][j] == 0]
        if not empty:
            return
        i, j = random.choice(empty)
        self.grid[i][j] = 2 if random.random() < 0.9 else 4
        if animate:
            self.create_tile_widget(i, j, self.grid[i][j], appear=True)

    def update_game(self):
        for i in range(4):
            for j in range(4):
                self.cells[i][j].setText("")
                self.cells[i][j].setStyleSheet("background-color: #fff8ec; border-radius: 5px;")

        existing = set(self.tile_widgets.keys())
        desired = set((i, j) for i in range(4) for j in range(4) if self.grid[i][j] != 0)
        for pos in list(existing - desired):
            info = self.tile_widgets.pop(pos, None)
            if info and info.get('widget'):
                info['widget'].deleteLater()

        for pos in list(desired - existing):
            i, j = pos
            self.create_tile_widget(i, j, self.grid[i][j], appear=False)

        for (i, j), info in self.tile_widgets.items():
            w = info['widget']
            val = self.grid[i][j]
            w.setText(str(val))
            font_size = self._compute_font_size(i, j)
            w.setStyleSheet(self._style_for_value(val, font_size))
            rect = self.cells[i][j].geometry()
            w.setGeometry(rect)

        self.score_line.setText(str(self.score))
        self.update_best_score()
        self.update_cell_sizes()

    def is_board_full(self):
        return all(self.grid[i][j] != 0 for i in range(4) for j in range(4))

    def can_merge(self):
        for i in range(4):
            for j in range(4):
                if j < 3 and self.grid[i][j] == self.grid[i][j+1]:
                    return True
                if i < 3 and self.grid[i][j] == self.grid[i+1][j]:
                    return True
        return False

    def check_game_over(self):
        if self.is_board_full() and not self.can_merge():
            self.game_over = True
            if self.score > 0:
                self.show_save_record_dialog()
            else:
                self.save_record_without_name()
            self.show_game_over_message()
            return True
        return False

   
    def show_save_record_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Новый рекорд!")
        dialog.setFixedSize(350, 250)
        dialog.setStyleSheet("background-color: #faf8ef;")
        dialog.setModal(True)

        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(25, 25, 25, 25)

        score_label = QLabel(f"Ваш счет: {self.score} очков")
        score_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        score_label.setStyleSheet("font-size: 22px; font-weight: bold; color: #776e65;")
        layout.addWidget(score_label)

        name_label = QLabel("Введите ваше имя:")
        name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        name_label.setStyleSheet("font-size: 16px; color: #776e65;")
        layout.addWidget(name_label)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Введите имя...")
        self.name_input.setStyleSheet("""
            QLineEdit {
                background-color: #ffffff;
                border: 2px solid #bbada0;
                border-radius: 8px;
                padding: 10px;
                font-size: 16px;
                color: #776e65;
            }
            QLineEdit:focus { border-color: #8f7a66; }
        """)
        layout.addWidget(self.name_input)

        buttons_layout = QHBoxLayout()
        save_btn = QPushButton("💾 Сохранить")
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #8f7a66;
                color: #ffffff;
                font-size: 16px;
                font-weight: bold;
                padding: 8px 25px;
                border-radius: 8px;
                border: none;
                min-width: 100px;
            }
            QPushButton:hover { background-color: #9f8a76; }
        """)
        save_btn.clicked.connect(lambda: self.save_record_with_name(dialog))
        buttons_layout.addWidget(save_btn)

        skip_btn = QPushButton("Пропустить")
        skip_btn.setStyleSheet("""
            QPushButton {
                background-color: #bbada0;
                color: #ffffff;
                font-size: 16px;
                padding: 8px 25px;
                border-radius: 8px;
                border: none;
                min-width: 100px;
            }
            QPushButton:hover { background-color: #cbbdb0; }
        """)
        skip_btn.clicked.connect(lambda: (dialog.reject(), self.save_record_without_name()))
        buttons_layout.addWidget(skip_btn)

        layout.addLayout(buttons_layout)
        dialog.setLayout(layout)
        self.name_input.setFocus()
        dialog.exec()

    def save_record_with_name(self, dialog):
        player_name = self.name_input.text().strip()
        if not player_name:
            player_name = "Игрок"
        record = {
            "score": self.score,
            "date": datetime.now().strftime("%d.%m.%Y %H:%M"),
            "name": player_name
        }
        self.all_records.append(record)
        self.all_records.sort(key=lambda x: x["score"], reverse=True)
        if len(self.all_records) > 20:
            self.all_records = self.all_records[:20]
        self.save_records()
        self.update_records_list()
        dialog.accept()

    def save_record_without_name(self):
        if self.score > 0:
            record = {
                "score": self.score,
                "date": datetime.now().strftime("%d.%m.%Y %H:%M"),
                "name": "Игрок"
            }
            self.all_records.append(record)
            self.all_records.sort(key=lambda x: x["score"], reverse=True)
            if len(self.all_records) > 20:
                self.all_records = self.all_records[:20]
            self.save_records()
            self.update_records_list()

    def show_game_over_message(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Игра окончена!")
        dialog.setFixedSize(500, 350)
        dialog.setStyleSheet("background-color: #faf8ef;")

        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(30, 30, 30, 30)

        title = QLabel("ИГРА ОКОНЧЕНА!")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 32px; font-weight: bold; color: #776e65; padding: 20px;")
        layout.addWidget(title)

        score = QLabel(f"Вы набрали: {self.score} очков")
        score.setAlignment(Qt.AlignmentFlag.AlignCenter)
        score.setStyleSheet("font-size: 24px; color: #776e65; padding: 10px;")
        layout.addWidget(score)

        question = QLabel("Хотите начать заново?")
        question.setAlignment(Qt.AlignmentFlag.AlignCenter)
        question.setStyleSheet("font-size: 20px; color: #776e65; padding: 20px;")
        layout.addWidget(question)

        buttons = QHBoxLayout()
        btn_yes = QPushButton("Да")
        btn_yes.setStyleSheet("""
            QPushButton {
                background-color: #8f7a66;
                color: #ffffff;
                font-size: 18px;
                padding: 12px 40px;
                border-radius: 8px;
                border: none;
                min-width: 120px;
            }
            QPushButton:hover { background-color: #9f8a76; }
        """)
        btn_yes.clicked.connect(lambda: (dialog.accept(), self.reset_game()))

        btn_no = QPushButton("Нет")
        btn_no.setStyleSheet("""
            QPushButton {
                background-color: #bbada0;
                color: #ffffff;
                font-size: 18px;
                padding: 12px 40px;
                border-radius: 8px;
                border: none;
                min-width: 120px;
            }
            QPushButton:hover { background-color: #cbbdb0; }
        """)
        btn_no.clicked.connect(lambda: (dialog.reject(), self.close()))

        buttons.addWidget(btn_yes)
        buttons.addWidget(btn_no)
        layout.addLayout(buttons)

        dialog.setLayout(layout)
        dialog.exec()

    def reset_game(self):
        for info in list(self.tile_widgets.values()):
            if info.get('widget'):
                info['widget'].deleteLater()
        self.tile_widgets.clear()

        self.grid = [[0]*4 for _ in range(4)]
        self.score = 0
        self.game_over = False
        self.add_random_num(animate=False)
        self.add_random_num(animate=False)
        self.update_game()
        self.setFocus()

    
    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_cell_sizes()
        self.update_score_sizes()

        if hasattr(self, 'field') and self.field:
            self.field.layout().activate()
            self.field.update()

        if hasattr(self, 'overlay') and self.overlay:
            self.overlay.setGeometry(self.field.rect())
            for (i, j), info in self.tile_widgets.items():
                rect = self.cells[i][j].geometry()
                w = info.get('widget')
                if w:
                    w.setGeometry(rect)
                    val = self.grid[i][j]
                    font_size = self._compute_font_size(i, j)
                    w.setStyleSheet(self._style_for_value(val, font_size))

    def update_score_sizes(self):
        if not hasattr(self, 'scores_container'):
            return
        window_width = self.width()
        if window_width >= 800:
            label_size, value_size, spacing = 14, 28, 50
        elif window_width >= 600:
            label_size, value_size, spacing = 13, 26, 45
        elif window_width >= 500:
            label_size, value_size, spacing = 12, 24, 40
        else:
            label_size, value_size, spacing = 11, 20, 30

        if self.scores_container:
            layout = self.scores_container.layout()
            if layout:
                layout.setSpacing(spacing)

        self.score_label.setStyleSheet(f"font-size: {label_size}px; font-weight: bold; color: #776e65; letter-spacing: 1px;")
        self.best_label.setStyleSheet(f"font-size: {label_size}px; font-weight: bold; color: #776e65; letter-spacing: 1px;")
        self.score_line.setStyleSheet(f"font-size: {value_size}px; font-weight: bold; color: #776e65;")
        self.best_score_line.setStyleSheet(f"font-size: {value_size}px; font-weight: bold; color: #776e65;")

    def update_cell_sizes(self):
        if not hasattr(self, 'field') or not self.field:
            return
        field_size = self.field.size()
        width = field_size.width()
        height = field_size.height()
        spacing = 6
        margin = 6
        total_spacing = (4 - 1) * spacing
        cell_size = min(width, height) - margin * 2 - total_spacing
        cell_size = cell_size // 4
        if cell_size < 20:
            cell_size = 20

        for i in range(4):
            for j in range(4):
                self.cells[i][j].setFixedSize(cell_size, cell_size)
                self.cells[i][j].setStyleSheet("background-color: #fff8ec; border-radius: 5px;")

        for (i, j), info in self.tile_widgets.items():
            rect = self.cells[i][j].geometry()
            w = info.get('widget')
            if w:
                w.setGeometry(rect)
                val = self.grid[i][j]
                font_size = self._compute_font_size(i, j)
                w.setStyleSheet(self._style_for_value(val, font_size))

    def _compute_font_size(self, i, j):
        rect = self.cells[i][j].geometry()
        cell_size = min(rect.width(), rect.height()) if rect.width() > 0 and rect.height() > 0 else 60
        return max(14, min(30, cell_size // 2))

    def _style_for_value(self, v, font_size):
        colors = {
            0: "#cdc1b4",
            2: "#eee4da", 4: "#ede0c8",
            8: "#f2b179", 16: "#f59563",
            32: "#f67c5f", 64: "#f65e3b",
            128: "#edcf72", 256: "#edcc61",
            512: "#edc850", 1024: "#edc53f",
            2048: "#edc22e",
        }
        color = 'white' if v >= 8 else 'black'
        return (f"background-color: {colors.get(v, '#cdc1b4')};"
                f"font-size: {font_size}px; font-weight: bold; color: {color}; border-radius: 5px;")

    def create_tile_widget(self, i, j, value, appear=False):
        if (i, j) in self.tile_widgets:
            info = self.tile_widgets[(i, j)]
            w = info['widget']
            info['value'] = value
            w.setText(str(value))
            font_size = self._compute_font_size(i, j)
            w.setStyleSheet(self._style_for_value(value, font_size))
            return w

        w = QLabel(self.overlay)
        w.setAlignment(Qt.AlignmentFlag.AlignCenter)
        w.setText(str(value))
        font_size = self._compute_font_size(i, j)
        w.setStyleSheet(self._style_for_value(value, font_size))
        font = QFont()
        font.setBold(True)
        font.setPointSize(int(max(10, font_size * 0.6)))
        w.setFont(font)

        rect = self.cells[i][j].geometry()
        w.setGeometry(rect)
        w.show()
        w.raise_()
        self.tile_widgets[(i, j)] = {'widget': w, 'value': value}

        if appear:
            small = QRect(rect.x() + rect.width()//2, rect.y() + rect.height()//2, 0, 0)
            anim = QPropertyAnimation(w, b"geometry", self)
            anim.setDuration(140)
            anim.setStartValue(small)
            anim.setEndValue(rect)
            anim.setEasingCurve(QEasingCurve.Type.OutBack)
            self._active_animations.append(anim)
            anim.finished.connect(lambda a=anim: self._safe_remove_animation(a))
            anim.start()
        return w

    def _safe_remove_animation(self, anim):
        try:
            self._active_animations.remove(anim)
        except Exception:
            pass

    
    def animate_moves(self, old_grid, new_grid, moves, duration=160):
        if not moves:
            return

        self.animating = True
        self.overlay.setGeometry(self.field.rect())

        group = QParallelAnimationGroup(self)
        self._active_animations.append(group)

        clones_info = []

        for mv in moves:
            si, sj = mv['from']
            ti, tj = mv['to']
            src_pos = (si, sj)
            tgt_pos = (ti, tj)

            orig_info = self.tile_widgets.pop(src_pos, None)
            orig_widget = orig_info['widget'] if orig_info else None
            if orig_widget:
                orig_widget.hide()

            clone = QLabel(self.overlay)
            clone.setAlignment(Qt.AlignmentFlag.AlignCenter)
            clone_value = old_grid[si][sj] if old_grid[si][sj] != 0 else mv.get('value', '')
            clone.setText(str(clone_value))

            if orig_info and 'font_size' in orig_info:
                font_size = orig_info['font_size']
            else:
                font_size = self._compute_font_size(si, sj)
            clone.setStyleSheet(self._style_for_value(clone_value, font_size))
            font = QFont()
            font.setBold(True)
            font.setPointSize(int(max(10, font_size * 0.6)))
            clone.setFont(font)

            start_rect = self._to_int_rect(self.cells[si][sj].geometry())
            end_rect = self._to_int_rect(self.cells[ti][tj].geometry())
            clone.setGeometry(start_rect)
            clone.show()
            clone.raise_()

            anim = QPropertyAnimation(clone, b"geometry", self)
            anim.setDuration(int(duration))
            anim.setStartValue(start_rect)
            anim.setEndValue(end_rect)
            anim.setEasingCurve(QEasingCurve.Type.InOutCubic)
            group.addAnimation(anim)

            clones_info.append((src_pos, tgt_pos, clone, orig_widget, font_size))

        def on_moves_finished():
            try:
                self._active_animations.remove(group)
            except Exception:
                pass

            by_target = {}
            for src_pos, tgt_pos, clone, orig_widget, font_size in clones_info:
                by_target.setdefault(tgt_pos, []).append((src_pos, clone, orig_widget, font_size))

            new_tile_widgets = {}

            for tgt_pos, clone_list in by_target.items():
                ti, tj = tgt_pos
                keeper_src, keeper_clone, keeper_orig, keeper_font = clone_list[0]
                new_value = new_grid[ti][tj]
                keeper_clone.setText(str(new_value))
                font_size = self._compute_font_size(ti, tj)
                keeper_clone.setStyleSheet(self._style_for_value(new_value, font_size))
                keeper_clone.setGeometry(self.cells[ti][tj].geometry())
                new_tile_widgets[tgt_pos] = {'widget': keeper_clone, 'value': new_value}

                for other_src, other_clone, other_orig, other_font in clone_list[1:]:
                    other_clone.deleteLater()
                    if other_orig is not None:
                        other_orig.deleteLater()

                if keeper_orig is not None:
                    keeper_orig.deleteLater()

            
            moved_sources = {src for src, _, _, _, _ in clones_info}
            
            for pos, info in list(self.tile_widgets.items()):
                if pos not in moved_sources and self.grid[pos[0]][pos[1]] != 0:
                    i, j = pos
                    w = info['widget']
                    font_size = self._compute_font_size(i, j)
                    w.setText(str(new_grid[i][j]))
                    w.setStyleSheet(self._style_for_value(new_grid[i][j], font_size))
                    w.setGeometry(self.cells[i][j].geometry())
                    new_tile_widgets[pos] = {'widget': w, 'value': new_grid[i][j]}
                else:
          
                    if info.get('widget') and info['widget'] not in [clone for _, _, clone, _, _ in clones_info]:
                        info['widget'].deleteLater()

            self.tile_widgets = new_tile_widgets

        
            merged_targets = list(set([tuple(mv['to']) for mv in moves if mv.get('merged')]))
            pulse_labels = []
            for (ti, tj) in merged_targets:
                val = new_grid[ti][tj]
                pulse = QLabel(self.overlay)
                pulse.setAlignment(Qt.AlignmentFlag.AlignCenter)
                pulse.setText(str(val))
                font_size = self._compute_font_size(ti, tj)
                pulse.setStyleSheet(self._style_for_value(val, font_size))
                font = QFont()
                font.setBold(True)
                font.setPointSize(int(max(10, font_size * 0.6)))
                pulse.setFont(font)

                rect = self._to_int_rect(self.cells[ti][tj].geometry())
                pulse.setGeometry(rect)
                pulse.show()
                pulse.raise_()
                pulse_labels.append(pulse)

                grow = QPropertyAnimation(pulse, b"geometry", self)
                grow.setDuration(100)
                bigger = QRect(int(rect.x() - rect.width()*0.08), int(rect.y() - rect.height()*0.08),
                               int(rect.width()*1.16), int(rect.height()*1.16))
                grow.setStartValue(rect)
                grow.setEndValue(bigger)
                grow.setEasingCurve(QEasingCurve.Type.OutCubic)

                shrink = QPropertyAnimation(pulse, b"geometry", self)
                shrink.setDuration(100)
                shrink.setStartValue(bigger)
                shrink.setEndValue(rect)
                shrink.setEasingCurve(QEasingCurve.Type.InCubic)

                def start_shrink(s=shrink):
                    s.start()
                grow.finished.connect(start_shrink)
                grow.start()

            def cleanup_pulses():
                for p in pulse_labels:
                    p.deleteLater()
                self.animating = False

            QTimer.singleShot(240, cleanup_pulses)

        group.finished.connect(on_moves_finished)
        group.start()

    @staticmethod
    def _to_int_rect(rect):
        return QRect(int(rect.x()), int(rect.y()), int(rect.width()), int(rect.height()))

 
    def keyPressEvent(self, event):
        if self.stacked_widget.currentIndex() != 1:
            return
        if self.game_over or self.animating:
            return

        key = event.key()
        direction = None
        if key == Qt.Key.Key_Left:
            direction = 'left'
        elif key == Qt.Key.Key_Right:
            direction = 'right'
        elif key == Qt.Key.Key_Up:
            direction = 'up'
        elif key == Qt.Key.Key_Down:
            direction = 'down'
        else:
            return

        old_grid = [row[:] for row in self.grid]
        new_grid, moved, score_gain, moves = simulate_move_with_moves(old_grid, direction)
        if not moved:
            return

        self.animate_moves(old_grid, new_grid, moves, duration=160)

        def commit_when_done():
            if self.animating:
                QTimer.singleShot(30, commit_when_done)
            else:
                self.grid = new_grid
                self.score += score_gain
                self.add_random_num(animate=True)
                self.update_game()
                self.check_game_over()
        QTimer.singleShot(30, commit_when_done)

    
    def home(self):
        self.stacked_widget.setCurrentIndex(0)

    def start_game(self):
        self.reset_game()
        self.stacked_widget.setCurrentIndex(1)
        QApplication.processEvents()
        self.update_cell_sizes()
        self.update_score_sizes()

    def open_records(self):
        self.update_records_list()
        self.stacked_widget.setCurrentIndex(2)

    def save_record(self, score):
        if score > 0:
            record = {
                "score": score,
                "date": datetime.now().strftime("%d.%m.%Y %H:%M"),
                "name": "Игрок"
            }
            self.all_records.append(record)
            self.all_records.sort(key=lambda x: x["score"], reverse=True)
            if len(self.all_records) > 20:
                self.all_records = self.all_records[:20]
            self.save_records()
            self.update_records_list()



def main():
    app = QApplication(sys.argv)
    w = MyWindow()
    w.show()
    w.stacked_widget.setCurrentIndex(0)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()