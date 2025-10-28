import sys
import os
from PyQt5.QtWidgets import QApplication
from ui.main_window import LauncherApp

if __name__ == "__main__":
    app = QApplication(sys.argv)
    launcher = LauncherApp()
    launcher.center_on_screen()
    launcher.show()
    launcher.fade_in()
    sys.exit(app.exec_())
