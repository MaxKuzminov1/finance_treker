from references.controller import Controller
from main_view import View
from PyQt6.QtWidgets import QApplication, QMessageBox
import sys
import traceback


def main():
    try:
        app = QApplication(sys.argv)
        app.setStyle("Fusion")  # Базовый стиль для более чистого рендеринга виджетов

        controller = Controller()

        view = View(controller)
        view.show()

        sys.exit(app.exec())

    except Exception as e:
        print(f"Ошибка при запуске: {e}")
        traceback.print_exc()

        # Если инстанс приложения еще не создан или упал, создаем резервный для алерта
        if not QApplication.instance():
            app = QApplication(sys.argv)

        QMessageBox.critical(None, "Ошибка",
                             f"Не удалось запустить программу:\n\n{str(e)}\n\nПроверьте подключение к базе данных")
        sys.exit(1)


if __name__ == "__main__":
    main()