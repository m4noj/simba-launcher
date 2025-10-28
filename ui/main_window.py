import os, json
from PyQt5.QtWidgets import (QWidget, QListWidget, QTextEdit, QSplitter, QVBoxLayout, QLineEdit, QListWidget, QListWidgetItem, QDesktopWidget, QGraphicsDropShadowEffect, QDialog, QLabel, QPushButton)
from PyQt5.QtGui import QFont, QPalette, QColor
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QFontMetrics
from core.indexer import build_index
from core.search import search_files
from core.launcher import open_file
from core.config import load_config

class LauncherApp(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("SmartLauncher (Beta)")
        self.setFixedSize(600, 400)

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.inner = QWidget()
        inner_layout = QVBoxLayout()
        inner_layout.setContentsMargins(15, 15, 15, 15)
        inner_layout.setSpacing(10)

        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Type to search...")
        self.search_box.setFont(QFont("Helvetica", 14))
        self.search_box.textChanged.connect(self.on_text_changed)
        self.search_box.returnPressed.connect(self.on_enter_pressed)

        self.result_list = QListWidget()
        self.result_list.setFont(QFont("Fira Code", 12))
        self.result_list.itemActivated.connect(self.on_item_activated)
     
        inner_layout.addWidget(self.search_box)
        inner_layout.addWidget(self.result_list)
        self.inner.setLayout(inner_layout)

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(30)
        shadow.setOffset(0, 8)  # drop below
        shadow.setColor(QColor(0, 0, 0, 180))  # translucent black
        self.inner.setGraphicsEffect(shadow)

        self.inner.setStyleSheet("""
            QWidget {
                background-color: #2e2e2e;
                border-radius: 12px;
            }
            QLineEdit {
                background-color: #3a3a3a;
                border: 1px solid #555;
                border-radius: 6px;
                padding: 6px;
                color: white;
                selection-background-color: #0078d7;
            }
            QListWidget {
                background-color: #2e2e2e;
                border: none;
                color: white;
                border-radius: 6px;
            }
            QListWidget::item {
                padding: 6px 8px;
            }
            QListWidget::item:hover {
                background-color: #404040;
            }
            QListWidget::item:selected {
                background-color: #0078d7;
                color: #ffffff;
            }
            /* Hide horizontal scrollbar completely */
            QListWidget QScrollBar:horizontal {
                height: 0px;
            }

            
            /* Scrollbar styling */
            QScrollBar:vertical {
                border: none;
                background: #2e2e2e;
                width: 6px;
                margin: 2px;
            }
            QScrollBar::handle:vertical {
                background: #555;
                border-radius: 3px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: #888;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0;
            }
        """)

        layout.addWidget(self.inner)
        self.setLayout(layout)

        config = load_config()
        self.max_results = config["max_results"]
        self.index = build_index(config["search_paths"])
        self.search_box.installEventFilter(self)

        self.setWindowOpacity(0.0)
        self.fade_anim = QPropertyAnimation(self, b"windowOpacity")
        self.fade_anim.setDuration(400)
        self.fade_anim.setStartValue(0.0)
        self.fade_anim.setEndValue(1.0)
        self.fade_anim.setEasingCurve(QEasingCurve.InOutQuad)

    def center_on_screen(self):
        """Center window like Albert."""
        screen = QDesktopWidget().availableGeometry().center()
        frame = self.frameGeometry()
        frame.moveCenter(screen)
        self.move(frame.topLeft())

    def fade_in(self):
        self.fade_anim.start()


    def on_text_changed(self, text):
        self.result_list.clear()
        
        if not text.strip():
            return

        # Dictionary mode
        if text.startswith("w:") or text.startswith("w>"):
            from core.dictionary import lookup_word
            query = text[2:].strip()
            results = lookup_word(query)

            self.result_list.clear()
            for entry in results:
                definition = entry["definition"]
                POS_MAP = {"n": "noun","v": "verb","a": "adjective","s": "adjective","r": "adverb"}
                pos = POS_MAP.get(entry["pos"], "")
                preview = definition[:80] + ("…" if len(definition) > 80 else "")
                item = QListWidgetItem(f"{query} ({pos}) — {preview}")
                item.setToolTip(definition)
                # attach full data
                item.setData(Qt.UserRole, (query, pos, definition))
                self.result_list.addItem(item)
            return


        metrics = QFontMetrics(self.result_list.font())
        max_width = self.result_list.viewport().width() - 10

        try:
            results = search_files(text, self.index)
            for res in results[: self.max_results]:
                display_text = metrics.elidedText(res["path"], Qt.ElideMiddle, max_width)
                item = QListWidgetItem(display_text)
                item.setToolTip(res["path"])  # full path
                self.result_list.addItem(item)
        except Exception as e:
            print("Search error:", e)

        if self.result_list.count() > 0:
            self.result_list.setCurrentRow(0)

    def on_item_activated(self, item):
        open_file(item.text())

    def on_enter_pressed(self):
        item = self.result_list.currentItem()
        if item:
            self.on_item_activated(item)

    def eventFilter(self, obj, event):
        if obj is self.search_box and event.type() == event.KeyPress:
            if event.key() == Qt.Key_Down:
                row = self.result_list.currentRow()
                if row < self.result_list.count() - 1:
                    self.result_list.setCurrentRow(row + 1)
                return True
            elif event.key() == Qt.Key_Up:
                row = self.result_list.currentRow()
                if row > 0:
                    self.result_list.setCurrentRow(row - 1)
                return True
        return super().eventFilter(obj, event)


    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.hide()  # hide instead of closing

        elif event.key() == Qt.Key_Return and event.modifiers() == Qt.ControlModifier:
            item = self.result_list.currentItem()
            if item:
                path = item.toolTip()
                folder = os.path.dirname(path)
                os.system(f'xdg-open "{folder}"')

        elif event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            current = self.result_list.currentItem()
            if current:
                data = current.data(Qt.UserRole)
                if data:  # only for dictionary items
                    word, pos, definition = data
                    self.show_detail_popup(word, pos, definition)

        else:
            super().keyPressEvent(event)
