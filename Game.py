import random
from PyQt6.QtWidgets import QFrame, QGridLayout, QLabel, QMainWindow, QApplication, QVBoxLayout, QWidget, QHBoxLayout, QDialog, QPushButton, QStackedWidget, QListWidget, QComboBox
from PyQt6.QtCore import Qt
from random import choice, random
import json  
from datetime import datetime 
import sys

class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        
        self.grid_size = 4
        
        self.grid = [[0, 0, 0, 0],
                     [0, 0, 0, 0],
                     [0, 0, 0, 0],
                     [0, 0, 0, 0]]

        self.score = 0;
        self.best_score = self.load_best_score()
        self.game_over = False
        self.all_records = self.load_records()

        self.setWindowTitle("Игра 2048")
        self.setFixedSize(600,700)
        self.setStyleSheet("background-color: rgb(220,220,220);")
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)
        
       
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
                color: white;
                font-size: 24px;
                font-weight: bold;
                padding: 20px 60px;
                border-radius: 15px;
                border: none;
                min-width: 250px;
            }
            QPushButton:hover {
                background-color: #9f8a76;
            }
        """)
        start_btn.clicked.connect(self.start_game)
        menu_layout.addWidget(start_btn)

        setting_btn = QPushButton("Настройки")
        setting_btn.setStyleSheet("""
            QPushButton {
                background-color: #8f7a66;
                color: white;
                font-size: 24px;
                font-weight: bold;
                padding: 20px 60px;
                border-radius: 15px;
                border: none;
                min-width: 250px;
            }
            QPushButton:hover {
                background-color: #9f8a76;
            }
        """)
        setting_btn.clicked.connect(self.open_settings)
        menu_layout.addWidget(setting_btn)

        records_btn = QPushButton("Рекорды")
        records_btn.setStyleSheet("""
            QPushButton {
                background-color: #8f7a66;
                color: white;
                font-size: 24px;
                font-weight: bold;
                padding: 20px 60px;
                border-radius: 15px;
                border: none;
                min-width: 250px;
            }
            QPushButton:hover {
                background-color: #9f8a76;
            }
        """)
        records_btn.clicked.connect(self.open_records)
        menu_layout.addWidget(records_btn)

        
        menu_widget.setLayout(menu_layout)
        self.stacked_widget.addWidget(menu_widget)  
        
   
        game_widget = QWidget()
        layout = QVBoxLayout()
        game_widget.setLayout(layout)
        
        home_btn = QPushButton("🏠︎")
        home_btn.setFixedSize(50,50)
        home_btn.setStyleSheet("""
            background-color: #8f7a66;
            color:black
            """)
        home_btn.clicked.connect(self.home)
        layout.addWidget(home_btn)
        
        title_layout = QHBoxLayout()
   
        title_score = QLabel("Score")
        title_score.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_score.setStyleSheet("font-size: 48px; font-weight: bold; color: #776e65;")
        title_layout.addWidget(title_score)

        title_best_score = QLabel("Best score")
        title_best_score.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_best_score.setStyleSheet("font-size: 48px; font-weight: bold; color: #776e65;")
        title_layout.addWidget(title_best_score)
  
        layout.addLayout(title_layout)

        score_layout = QHBoxLayout()

        self.score_line = QLabel("0")
        self.score_line.setStyleSheet("font-size: 48px; font-weight: bold; color: #776e65;")
        self.score_line.setAlignment(Qt.AlignmentFlag.AlignCenter)
        score_layout.addWidget(self.score_line)

        self.best_score_line = QLabel(str(self.best_score))
        self.best_score_line.setStyleSheet("font-size: 48px; font-weight: bold; color: #776e65;")
        self.best_score_line.setAlignment(Qt.AlignmentFlag.AlignCenter)
        score_layout.addWidget(self.best_score_line)

        layout.addLayout(score_layout)

        field = QFrame()
        field.setStyleSheet("""
            background-color: #bbada0;
            border-radius: 10px;
            padding: 5px;
        """)
       
        field.setFixedSize(500, 500)  
        grid = QGridLayout()
        grid.setSpacing(10)  
        field.setLayout(grid)
     
        self.cells = []
        for i in range(4):
            row = []
            for j in range(4):
                cell = QLabel()
                cell.setAlignment(Qt.AlignmentFlag.AlignCenter)
                cell.setStyleSheet(
                    "background-color: rgb(255,248,220);"
                    "font-size:30px;"
                    )
                grid.addWidget(cell,i,j)
                row.append(cell)
            self.cells.append(row)
        
        layout.addWidget(field, alignment=Qt.AlignmentFlag.AlignCenter)
        
        self.stacked_widget.addWidget(game_widget)  
        

      
        settings_widget = QWidget()
        settings_layout = QVBoxLayout()
        settings_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        settings_layout.setSpacing(20)
        
        settings_label = QLabel("Настройки")
        settings_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        settings_label.setStyleSheet("font-size: 36px; font-weight: bold; color: #776e65;")
        settings_layout.addWidget(settings_label)
        
 
        size_label = QLabel("Размер поля:")
        size_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        size_label.setStyleSheet("font-size: 20px; color: #776e65;")
        settings_layout.addWidget(size_label)
        
        self.size_combo = QComboBox()
        self.size_combo.addItems(["3x3", "4x4", "5x5", "6x6", "7x7", "8x8"])
        self.size_combo.setCurrentText("4x4")
        self.size_combo.setStyleSheet("""
            QComboBox {
                background-color: #faf8ef;
                color: #776e65;
                font-size: 20px;
                padding: 10px;
                border-radius: 10px;
                border: 2px solid #bbada0;
                min-width: 150px;
            }
            QComboBox:hover {
                border-color: #8f7a66;
            }
        """)
        self.size_combo.currentTextChanged.connect(self.change_grid_size)
        settings_layout.addWidget(self.size_combo)
        
        back_btn_settings = QPushButton("Назад")
        back_btn_settings.setStyleSheet("""
            QPushButton {
                background-color: #8f7a66;
                color: white;
                font-size: 18px;
                padding: 10px 40px;
                border-radius: 10px;
                border: none;
            }
            QPushButton:hover {
                background-color: #9f8a76;
            }
        """)
        back_btn_settings.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        settings_layout.addWidget(back_btn_settings)
        
        settings_widget.setLayout(settings_layout)
        self.stacked_widget.addWidget(settings_widget) 


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
        """)
        records_layout.addWidget(self.records_list)
        
        
        back_btn = QPushButton("Назад")
        back_btn.setStyleSheet("""
            QPushButton {
                background-color: #8f7a66;
                color: white;
                font-size: 18px;
                padding: 10px 40px;
                border-radius: 10px;
                border: none;
            }
            QPushButton:hover {
                background-color: #9f8a76;
            }
        """)
        back_btn.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        records_layout.addWidget(back_btn)
        records_widget.setLayout(records_layout)
        self.stacked_widget.addWidget(records_widget)  


        self.stacked_widget.setCurrentIndex(0)  
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        self.add_random_num()
        self.add_random_num()
        self.update_game()

        self.update_records_list()


    def change_grid_size(self, size_text):

        new_size = int(size_text[0])
        if new_size != self.grid_size:
            self.grid_size = new_size

            self.create_new_grid()
            self.reset_game()


    def create_new_grid(self):
        self.grid = [[0] * self.grid_size for _ in range(self.grid_size)]
        self.cells = []
        
        game_widget = self.stacked_widget.widget(1)
        layout = game_widget.layout()
        

        for i in range(layout.count() - 1, -1, -1):
            item = layout.itemAt(i)
            if item and isinstance(item.widget(), QFrame):
                widget = item.widget()
                if widget.styleSheet().strip().startswith("background-color: #bbada0"):
                    widget.deleteLater()
                    break
        
       
        field = QFrame()
        field.setStyleSheet("""
            background-color: #bbada0;
            border-radius: 10px;
            padding: 5px;
        """)
        field.setFixedSize(500, 500)
        
        grid = QGridLayout()
        grid.setSpacing(10)
        field.setLayout(grid)
        
        for i in range(self.grid_size):
            row = []
            for j in range(self.grid_size):
                cell = QLabel()
                cell.setAlignment(Qt.AlignmentFlag.AlignCenter)
                cell.setStyleSheet(
                    "background-color: rgb(255,248,220);"
                    "font-size:30px;"
                )
                grid.addWidget(cell, i, j)
                row.append(cell)
            self.cells.append(row)
        
        layout.addWidget(field, alignment=Qt.AlignmentFlag.AlignCenter)

    def home(self):
        self.stacked_widget.setCurrentIndex(0)
        self.reset_game()
        
    def start_game(self):
        self.stacked_widget.setCurrentIndex(1) 
        
    def open_settings(self):
        self.stacked_widget.setCurrentIndex(2)
        
    def open_records(self):
        self.update_records_list()
        self.stacked_widget.setCurrentIndex(3)

    def add_random_num(self):
        empty_cells = []
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                if(self.grid[i][j] == 0):
                    empty_cells.append((i,j))
        if empty_cells:
            i, j = choice(empty_cells)
            self.grid[i][j] = 2 if random() < 0.9 else 4
            
    def update_game(self):
        colors = {
            0: "#cdc1b4",       
            2: "#eee4da", 4: "#ede0c8",
            8: "#f2b179", 16: "#f59563",
            32: "#f67c5f", 64: "#f65e3b",
            128: "#edcf72", 256: "#edcc61",
            512: "#edc850", 1024: "#edc53f",
            2048: "#edc22e", 4096: "#60d392",
        }

        for i in range(self.grid_size):
            for j in range(self.grid_size):
                digit = self.grid[i][j]
                cell = self.cells[i][j]
                if digit == 0:
                    cell.setText("")
                    cell.setStyleSheet(
                        f"background-color: {colors[0]}"
                        )
                else:
                    cell.setText(str(digit))
                    cell.setStyleSheet(
                        f""" background-color: {colors.get(digit, "#cdc1b4")};
                             font-size: 30px;
                             color:black"""
                        )
        self.score_line.setText(str(self.score))
        self.update_best_score()
        
    def is_board_full(self):
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                if self.grid[i][j] == 0:
                    return False
        return True

    def can_merge(self):
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                if j < self.grid_size - 1 and self.grid[i][j] == self.grid[i][j + 1]:
                    return True
                if i < self.grid_size - 1 and self.grid[i][j] == self.grid[i + 1][j]:
                    return True
        return False

    def check_game_over(self):
        if self.is_board_full() and not self.can_merge():
            self.game_over = True
            self.save_record(self.score)
            self.show_game_over_message()
            return True
        return False

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
        title.setStyleSheet("""
            font-size: 32px;
            font-weight: bold;
            color: #776e65;
            padding: 20px;
        """)
        layout.addWidget(title)
    
        score = QLabel(f"Вы набрали: {self.score} очков")
        score.setAlignment(Qt.AlignmentFlag.AlignCenter)
        score.setStyleSheet("""
            font-size: 24px;
            color: #776e65;
            padding: 10px;
        """)
        layout.addWidget(score)
    
    
        question = QLabel("Хотите начать заново?")
        question.setAlignment(Qt.AlignmentFlag.AlignCenter)
        question.setStyleSheet("""
            font-size: 20px;
            color: #776e65;
            padding: 20px;
        """)
        layout.addWidget(question)
   
        buttons = QHBoxLayout()
        buttons.setSpacing(20)
    
        btn_yes = QPushButton("Да")
        btn_yes.setStyleSheet("""
            QPushButton {
                background-color: #8f7a66;
                color: white;
                font-size: 18px;
                padding: 12px 40px;
                border-radius: 8px;
                border: none;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #9f8a76;
            }
        """)
        btn_yes.clicked.connect(lambda: (dialog.accept(), self.reset_game()))
    
        btn_no = QPushButton("Нет")
        btn_no.setStyleSheet("""
            QPushButton {
                background-color: #bbada0;
                color: white;
                font-size: 18px;
                padding: 12px 40px;
                border-radius: 8px;
                border: none;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #cbbdb0;
            }
        """)
        btn_no.clicked.connect(lambda: (dialog.reject(), self.close()))
    
        buttons.addWidget(btn_yes)
        buttons.addWidget(btn_no)
        layout.addLayout(buttons)
    
        dialog.setLayout(layout)
        dialog.exec()

    def reset_game(self):
        self.grid = [[0] * self.grid_size for _ in range(self.grid_size)]
        self.score = 0
        self.game_over = False
        self.add_random_num()
        self.add_random_num()
        self.update_game()

    def reverse_grid(self):
        new_grid = [[0] * self.grid_size for _ in range(self.grid_size)]
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                new_grid[i][j] = self.grid[j][i]
        self.grid = new_grid
        
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
    
    def save_record(self, score):
        
        if score > 0:
            record = {
                "score": score,
                "date": datetime.now().strftime("%d.%m.%Y %H:%M"),
                "size": f"{self.grid_size}x{self.grid_size}"  
            }
            self.all_records.append(record)
            self.all_records.sort(key=lambda x: x["score"], reverse=True)
            if len(self.all_records) > 20:
                self.all_records = self.all_records[:20]
            self.save_records()
            self.update_records_list()
    
    def update_records_list(self):
        
        self.records_list.clear()
        
        if not self.all_records:
            self.records_list.addItem("Нет рекордов")
            return
        
        for i, record in enumerate(self.all_records, 1):
            size_info = f" [{record.get('size', '4x4')}]" if 'size' in record else ""
            text = f"{i}. {record['score']} очков{size_info}  ({record['date']})"
            self.records_list.addItem(text)

    def move_left(self):
        moved = False
        for i in range(self.grid_size):  
            row = []
            for j in range(self.grid_size):
                if self.grid[i][j] != 0:
                    row.append(self.grid[i][j])
         
            new_row = []
            skip = False
            for j in range(len(row)):
                if skip:
                    skip = False
                    continue
                if j + 1 < len(row) and row[j] == row[j + 1]:
                    new_row.append(row[j] * 2)
                    self.score += row[j] * 2
                    skip = True
                else:
                    new_row.append(row[j])
            
            while len(new_row) < self.grid_size:
                new_row.append(0)
    
            if self.grid[i] != new_row:
                moved = True
            self.grid[i] = new_row
        
        return moved
        
    def move_right(self):
        for i in range(self.grid_size):
            self.grid[i] = self.grid[i][::-1]

        moved = self.move_left()

        for i in range(self.grid_size):
            self.grid[i] = self.grid[i][::-1]

        return moved
        
    def move_up(self):
        self.reverse_grid()
        moved = self.move_left()
        self.reverse_grid()
        return moved
        
    def move_down(self):
        self.reverse_grid()
        moved = self.move_right()
        self.reverse_grid()
        return moved

    def keyPressEvent(self, event):
        if self.stacked_widget.currentIndex() != 1:
            return
            
        if self.game_over:
            return
            
        key = event.key()
        moved = False
        
        if key == Qt.Key.Key_Left:
            moved = self.move_left()
        elif key == Qt.Key.Key_Right:
            moved = self.move_right()
        elif key == Qt.Key.Key_Up:
            moved = self.move_up()
        elif key == Qt.Key.Key_Down:
            moved = self.move_down()
        else:
            super().keyPressEvent(event)
            return
        
        if moved:
            self.add_random_num()
            self.update_game()
            self.check_game_over()

def main():
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()  
    sys.exit(app.exec())

if __name__ == "__main__":
    main()