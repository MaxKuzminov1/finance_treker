from references.controller import Controller
from main_view import View
from PyQt6.QtWidgets import QApplication, QMessageBox
import sys
import traceback

def main():
    try:
        app = QApplication(sys.argv)

        controller = Controller()

        view = View(controller)
        view.show()

        sys.exit(app.exec())

    except Exception as e:
        print(f"Ошибка при запуске: {e}")
        traceback.print_exc()

        app = QApplication(sys.argv)
        QMessageBox.critical(None, "Ошибка",
                             f"Не удалось запустить программу:\n\n{str(e)}\n\nПроверьте подключение к базе данных")
        sys.exit(1)

if __name__ == "__main__":
    main()