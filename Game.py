from PyQt6.QtWidgets import QFrame, QGridLayout, QLabel, QMainWindow, QApplication, QVBoxLayout, QWidget
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont



import sys
class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Моя игра 2048")
        self.setFixedSize(500,600)
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
            padding: 10px;
        """)
       
        field.setFixedSize(400, 400)  
        grid = QGridLayout()
        grid.setSpacing(10)  
        field.setLayout(grid)
     
        for i in range(4):
            for j in range(4):
                cell = QLabel()
                cell.setStyleSheet(
                    "background-color: rgb(255,248,220)")
                grid.addWidget(cell,i,j)
        
        layout.addWidget(field)


#need to delete
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

