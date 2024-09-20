#   Entry point file for the program

#   Imports
import sys
from PyQt6.QtWidgets import QApplication 
from gui import MainWindow

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()           #   IMPORTANT!!!!! Windows are hidden by default.
    app.exec()

if __name__ == '__main__':
    main()
