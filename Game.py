from queue import Empty
import random
from PyQt6.QtWidgets import QFrame, QGridLayout, QLabel, QMainWindow, QApplication, QVBoxLayout, QWidget
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


        self.setWindowTitle("Моя игра 2048")
        self.setFixedSize(600,700)
        self.setStyleSheet("background-color: rgb(220,220,220);")
        central_window = QWidget()
        self.setCentralWidget(central_window)
        layout = QVBoxLayout()
        central_window.setLayout(layout)
        title = QLabel("2048")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

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
                cell.setStyleSheet(
                    "background-color: rgb(255,248,220)")
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
        for i in range(4):
            for j in range(4):
                digit = self.grid[i][j]
                cell = self.cells[i][j]
                if digit == 0:
                    cell.setText("")
                else:
                    cell.setText(str(digit))

    def move_left(self):
        moved = False
        for i in range(4):  # Проходим по каждой строке
            # Берем строку и убираем нули
            row = []
            for j in range(4):
                if self.grid[i][j] != 0:
                    row.append(self.grid[i][j])
            
            # Сливаем одинаковые числа
            new_row = []
            skip = False
            for j in range(len(row)):
                if skip:
                    skip = False
                    continue
                if j + 1 < len(row) and row[j] == row[j + 1]:
                    new_row.append(row[j] * 2)
                    skip = True
                else:
                    new_row.append(row[j])
            
            # Дополняем нулями до 4 элементов
            while len(new_row) < 4:
                new_row.append(0)
            
            # Проверяем, изменилась ли строка
            if self.grid[i] != new_row:
                moved = True
            self.grid[i] = new_row
        
        return moved
    
    # ==========================================
    # ОБРАБОТКА НАЖАТИЙ КЛАВИШ
    # ==========================================
    def keyPressEvent(self, event):
        key = event.key()
        moved = False
        
        if key == Qt.Key.Key_Left:
            moved = self.move_left()
        elif key == Qt.Key.Key_Right:
            pass
        elif key == Qt.Key.Key_Up:
            # Пока пропускаем (сделаем позже)
            pass
        elif key == Qt.Key.Key_Down:
            # Пока пропускаем (сделаем позже)
            pass
        else:
            super().keyPressEvent(event)
            return
        
        # Если плитки сдвинулись - добавляем новую
        if moved:
            self.add_random_num()
            self.update_game()

def main():
    # Создаем приложение
    app = QApplication(sys.argv)
    
    # Создаем окно
    window = MyWindow()
    window.show()  # Показываем окно
    
    # Запускаем цикл обработки событий
    sys.exit(app.exec())

if __name__ == "__main__":
    main()

