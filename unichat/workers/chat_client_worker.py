from typing import Callable

# external imports
from PySide6.QtCore import QObject, QThread, Qt

# project imports
import unichat.db as db


class ChatClientWorker:
    def __init__(self, worker: QObject, sub_func: Callable = None) -> None:
        """ Chat client worker constructor """
        self.worker = worker
        self.sub_func = sub_func
        self.thread = QThread()

    def execute_worker(self) -> None:
        """ executes QObject worker in a QThread """
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        if self.sub_func:
            self.worker.finished.connect(self.sub_func)
        self.thread.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.quit)
        self.thread.start()

    def execute_async_worker(self) -> None:
        """ executes async QObject worker in a QThread"""
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        if self.sub_func:
            self.worker.msg_receive_signal.connect(
                self.sub_func, Qt.QueuedConnection
            )

        self.thread.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.quit)
        self.thread.start()

    def stop_worker(self) -> None:
        """ stops a QObject worker. manly used by async workers"""
        self.worker.stop()

    def change_target(self, target: db.Contact | None) -> None:
        """ changes the target of the chat client worker. manly used by async workers."""
        self.worker.change_target(target)
