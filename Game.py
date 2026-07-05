import random
from PyQt6.QtWidgets import QFrame, QGridLayout, QLabel, QMainWindow, QApplication, QVBoxLayout, QWidget, QHBoxLayout, QDialog, QPushButton, QStackedWidget
from PyQt6.QtCore import Qt
from random import choice, random



import sys
class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.grid = [[0, 0, 0, 0],
                     [0, 0, 0, 0],
                     [0, 0, 0, 0],
                     [0, 0, 0, 0]]

        self.score = 0;
        self.best_score = self.load_best_score()
        self.game_over = False

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
        
        menu_widget.setLayout(menu_layout)
        self.stacked_widget.addWidget(menu_widget)  
        
   
        game_widget = QWidget()
        layout = QVBoxLayout()
        game_widget.setLayout(layout)
        
        
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
        
      
        self.stacked_widget.setCurrentIndex(0)  

        self.add_random_num()
        self.add_random_num()
        self.update_game()

    def start_game(self):
        """Переключает на игровой экран"""
        self.stacked_widget.setCurrentIndex(1) 

    def add_random_num(self):
        empty_cells = []
        for i in range(4):
            for j in range(4):
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

        for i in range(4):
            for j in range(4):
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
      
        for i in range(4):
            for j in range(4):
                if self.grid[i][j] == 0:
                    return False
        return True

    def can_merge(self):
      
        for i in range(4):
            for j in range(4):

                if j < 3 and self.grid[i][j] == self.grid[i][j + 1]:
                    return True
               
                if i < 3 and self.grid[i][j] == self.grid[i + 1][j]:
                    return True
        return False

    def check_game_over(self):
    
        if self.is_board_full() and not self.can_merge():
            self.game_over = True
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

        self.grid = [[0, 0, 0, 0] for _ in range(4)]
        self.score = 0
        self.game_over = False
        self.add_random_num()
        self.add_random_num()
        self.update_game()

    def reverse_grid(self):
        new_grid = [[0] * 4 for _ in range(4)]
        for i in range(4):
            for j in range(4):
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



    def move_left(self):
        moved = False
        for i in range(4):  
           
            row = []
            for j in range(4):
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
            
            
            while len(new_row) < 4:
                new_row.append(0)
            
    
            if self.grid[i] != new_row:
                moved = True
            self.grid[i] = new_row
        
        return moved
    def move_right(self):
        for i in range(4):
            self.grid[i] = self.grid[i][::-1]

        moved = self.move_left()

        for i in range(4):
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

