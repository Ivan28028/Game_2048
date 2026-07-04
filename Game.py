import random
from PyQt6.QtWidgets import QFrame, QGridLayout, QLabel, QMainWindow, QApplication, QVBoxLayout, QWidget, QHBoxLayout
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
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

        self.setWindowTitle("Моя игра 2048")
        self.setFixedSize(600,700)
        self.setStyleSheet("background-color: rgb(220,220,220);")
        central_window = QWidget()
        self.setCentralWidget(central_window)

  
    
     


        layout = QVBoxLayout()
        central_window.setLayout(layout)


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


        self.add_random_num()
        self.update_game()


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

    def reverse_grid(self):
        new_grid = [[0] * 4 for _ in range(4)]
        for i in range(4):
            for j in range(4):
                new_grid[i][j] = self.grid[j][i]

        self.grid = new_grid
    def load_best_score(self):
        """Загружает лучший счет из файла"""
        try:
            with open("best_score.txt", "r") as f:
                return int(f.read())
        except:
            return 0
    
    def save_best_score(self):
        """Сохраняет лучший счет в файл"""
        with open("best_score.txt", "w") as f:
            f.write(str(self.best_score))
    
    def update_best_score(self):
        """Обновляет лучший счет, если текущий больше"""
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

def main():

    app = QApplication(sys.argv)
    
    window = MyWindow()
    window.show()  
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()

