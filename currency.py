import sys
from pathlib import Path

from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QComboBox,
    QPushButton,
    QLineEdit,
    QListView,
)
from PyQt6.uic import loadUi  # для проверки api
from PyQt6.QtCore import QStringListModel
import json
import requests

import logging
from logging.config import dictConfig

BASE_PATH = (
    Path(sys._MEIPASS) if hasattr(sys, "_MEIPASS") else Path(__file__).parent
)  # путь к currency.py

log_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    "handlers": {
        "rotating_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "DEBUG",
            "formatter": "standard",
            "filename": "app.log",
            "maxBytes": 1024 * 1024 * 1,  # 1 MB, размер одного файла
            "backupCount": 3,  # Сколько файлов
            "encoding": "utf-8",
            "mode": "a",
        },
        "console": {
            "class": "logging.StreamHandler",
            "level": "INFO",
            "formatter": "standard",
            "stream": "ext://sys.stdout",
        },
    },
    "loggers": {
        "": {  # кавычки - применимо ко всем логерам
            "handlers": ["rotating_file", "console"],
            "level": "DEBUG",
            "propagate": False,
        }
    },
    "root": {"handlers": ["console", "rotating_file"], "level": "DEBUG"},
}
dictConfig(log_config)  # загрузка словаря для настройки логеров
logger = logging.getLogger(__name__)


class MyWindow(QMainWindow):  # создание виджетов
    convertPushButton: QPushButton
    sourceLineEdit: QLineEdit
    targetLineEdit: QLineEdit
    sourceCurrencyComboBox: QComboBox
    targetCurrencyComboBox: QComboBox
    historyListView: QListView

    def append_history(self, history_entry: str):
        self.history_model.insertRow(0)  # новый элемент в списке
        index = self.history_model.index(0)  # ссылка на первый элемент в списке
        self.history_model.setData(index, history_entry)
        logger.info(f"{history_entry}")

    def convert(self):
        source_amount = float(
            self.sourceLineEdit.text() or 0
        )  # на случай пустого значения
        target_currency = self.targetCurrencyComboBox.currentText()
        source_currency = self.sourceCurrencyComboBox.currentText()

        if target_currency == source_currency:
            self.targetLineEdit.setText(
                str(source_amount)
            )  # если валюты совпадают, рез-т операции равен исходному
            return  # setText чтобы не сбросилось source_amount

        for currency in self.currency_data:
            if source_currency == currency["Cur_Abbreviation"]:
                source_currency_object = currency

        byn = source_amount * (
            source_currency_object["Cur_OfficialRate"]
            / source_currency_object["Cur_Scale"]
        )

        for currency in self.currency_data:
            if target_currency == currency["Cur_Abbreviation"]:
                target_currency_object = currency

        target_amount = (
            byn / target_currency_object["Cur_OfficialRate"]
        ) * target_currency_object["Cur_Scale"]
        self.targetLineEdit.setText(f"{target_amount:.2f}")  # округление
        self.append_history(
            f"{source_amount:.2f} {source_currency} → {target_amount:.2f} {target_currency}"
        )

    def __init__(self):
        super().__init__()
        r = requests.get("https://api.nbrb.by/exrates/rates?periodicity=0")
        self.currency_data = json.loads(r.content.decode())
        self.currency_data.append(
            {"Cur_Abbreviation": "BYN", "Cur_OfficialRate": 1, "Cur_Scale": 1}
        )  # словарь
        loadUi(BASE_PATH / "currency.ui", self)  # добавление файла к базовой папке

        self.history_model = (
            QStringListModel()
        )  # массив данных, связанный с элементами интерфейса
        self.historyListView.setModel(self.history_model)  # создаем список из строк
        currencies = ["BYN", "USD", "EUR", "RUB", "CNY"]
        for c in self.currency_data:
            currency_name = c["Cur_Abbreviation"]  # ключ аббревиатур к валютам
            if currency_name not in currencies:
                currencies.append(currency_name)

        for currency_name in currencies:
            self.sourceCurrencyComboBox.addItem(
                currency_name
            )  # 20-21 добавляют выпадающий список выбора валют
            self.targetCurrencyComboBox.addItem(currency_name)

        self.centralWidget().layout().setContentsMargins(
            8, 8, 8, 8
        )  # left, top, right, bottom

        self.setWindowTitle("Конвертер валют")

        self.bind_events()

    def bind_events(self):
        self.convertPushButton.clicked.connect(self.convert)


if __name__ == "__main__":
    app = QApplication([])
    window = MyWindow()
    window.show()
    app.exec()
