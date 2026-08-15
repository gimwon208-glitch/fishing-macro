import sys
import time
import platform
import subprocess
import threading

import pyautogui
import pyperclip
from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QMessageBox,
    QSpinBox,
)

APP_TITLE = "방구석 낚시꾼 자동 매크로"
DEFAULT_ROOM = "낚시방"
DEFAULT_BOT = "방구석낚시꾼"
DEFAULT_COMMAND = "낚시"
DEFAULT_INTERVAL = 4

pyautogui.PAUSE = 0.15
pyautogui.FAILSAFE = True


class Signals(QObject):
    status = Signal(str)
    stopped = Signal()
    error = Signal(str)


class FishingMacro:
    def __init__(self, signals):
        self.signals = signals
        self.running = False

    def stop(self):
        self.running = False
        self.signals.status.emit("중지 중...")

    def paste_text(self, text):
        pyperclip.copy(text)
        if platform.system() == "Darwin":
            pyautogui.hotkey("command", "v")
        else:
            pyautogui.hotkey("ctrl", "v")

    def activate_kakao(self):
        if platform.system() != "Darwin":
            raise RuntimeError("이 빌드는 macOS 카카오톡용입니다.")

        # KakaoTalk을 앞으로 가져온다.
        result = subprocess.run(
            ["osascript", "-e", 'tell application "KakaoTalk" to activate'],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            raise RuntimeError(
                "KakaoTalk을 활성화하지 못했습니다.\n"
                "Mac에 카카오톡이 설치되어 있고 실행 가능한지 확인하세요."
            )
        time.sleep(1.5)

    def send_once(self, bot_name, command):
        # 사용자가 미리 열어 둔 채팅방의 입력창에 명령을 보낸다.
        # 이 방식이 Mac 카카오톡 버전 차이에 가장 덜 민감하다.

        # 기존 입력 내용이 있다면 정리
        pyautogui.hotkey("command", "a")
        pyautogui.press("backspace")
        time.sleep(0.2)

        # @멘션 이름 입력
        self.paste_text("@" + bot_name)
        time.sleep(1.0)

        # 카카오톡 멘션 자동완성의 첫 항목 선택
        pyautogui.press("down")
        time.sleep(0.2)
        pyautogui.press("enter")
        time.sleep(0.5)

        # 명령어 입력 후 전송
        self.paste_text(" " + command)
        time.sleep(0.3)
        pyautogui.press("enter")

    def interruptible_wait(self, seconds):
        elapsed = 0.0
        while elapsed < seconds:
            if not self.running:
                return False
            time.sleep(0.2)
            elapsed += 0.2
        return True

    def run(self, room_name, bot_name, command, interval):
        self.running = True
        try:
            self.signals.status.emit("카카오톡을 활성화하는 중...")
            self.activate_kakao()

            # room_name은 안전 확인 및 상태표시용.
            # 채팅방 자동검색은 카카오톡 버전마다 단축키/UI가 달라
            # 사용자가 해당 방을 미리 열어두는 방식을 사용한다.
            self.signals.status.emit(
                f"'{room_name}' 채팅방을 미리 열어둔 상태인지 확인하세요. 3초 후 시작"
            )
            if not self.interruptible_wait(3):
                return

            count = 0
            while self.running:
                count += 1
                self.signals.status.emit(f"낚시 실행 중 ({count}회)")
                self.send_once(bot_name, command)

                if not self.running:
                    break

                remaining = interval
                while remaining > 0 and self.running:
                    self.signals.status.emit(f"다음 실행까지 {remaining}초")
                    if not self.interruptible_wait(1):
                        break
                    remaining -= 1

        except pyautogui.FailSafeException:
            self.signals.error.emit(
                "긴급 정지되었습니다.\n마우스를 화면 왼쪽 위 모서리로 옮기면 자동 정지합니다."
            )
        except Exception as exc:
            self.signals.error.emit(str(exc))
        finally:
            self.running = False
            self.signals.stopped.emit()


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_TITLE)
        self.resize(460, 420)

        self.signals = Signals()
        self.macro = FishingMacro(self.signals)

        self._build_ui()

        self.signals.status.connect(self.set_status)
        self.signals.stopped.connect(self.on_stopped)
        self.signals.error.connect(self.show_error)

    def _build_ui(self):
        main = QVBoxLayout()

        title = QLabel("🎣 방구석 낚시꾼 자동 실행기")
        title.setStyleSheet("font-size: 22px; font-weight: bold; padding: 10px;")
        subtitle = QLabel("Mac 카카오톡 멘션 연동 매크로")
        subtitle.setStyleSheet("font-size: 13px; color: #777; padding-bottom: 12px;")

        main.addWidget(title)
        main.addWidget(subtitle)

        form = QFormLayout()

        self.room_input = QLineEdit(DEFAULT_ROOM)
        self.bot_input = QLineEdit(DEFAULT_BOT)
        self.command_input = QLineEdit(DEFAULT_COMMAND)
        self.interval_input = QSpinBox()
        self.interval_input.setRange(1, 3600)
        self.interval_input.setValue(DEFAULT_INTERVAL)
        self.interval_input.setSuffix(" 초")

        form.addRow("채팅방 이름", self.room_input)
        form.addRow("멘션 봇(@)", self.bot_input)
        form.addRow("전송 명령어", self.command_input)
        form.addRow("실행 간격", self.interval_input)
        main.addLayout(form)

        note = QLabel(
            "※ 시작 전에 Mac 카카오톡에서 원하는 채팅방을 직접 열어두세요.\n"
            "※ 처음 실행 시 macOS '손쉬운 사용' 권한 허용이 필요할 수 있습니다."
        )
        note.setWordWrap(True)
        note.setStyleSheet("font-size: 12px; color: #666; padding: 10px 0;")
        main.addWidget(note)

        self.status_label = QLabel("상태: 대기 중")
        self.status_label.setWordWrap(True)
        self.status_label.setStyleSheet(
            "padding: 14px; font-size: 14px; background: #f2f2f2; margin-top: 8px;"
        )
        main.addWidget(self.status_label)
        main.addStretch()

        buttons = QHBoxLayout()
        self.start_button = QPushButton("낚시 시작")
        self.stop_button = QPushButton("중지")
        self.start_button.setMinimumHeight(48)
        self.stop_button.setMinimumHeight(48)
        self.start_button.setStyleSheet(
            "QPushButton { font-size: 16px; font-weight: bold; }"
        )
        self.stop_button.setEnabled(False)

        self.start_button.clicked.connect(self.start_macro)
        self.stop_button.clicked.connect(self.stop_macro)

        buttons.addWidget(self.start_button, 2)
        buttons.addWidget(self.stop_button, 1)
        main.addLayout(buttons)

        self.setLayout(main)

    def set_status(self, text):
        self.status_label.setText("상태: " + text)

    def start_macro(self):
        room = self.room_input.text().strip()
        bot = self.bot_input.text().strip().lstrip("@")
        command = self.command_input.text().strip()
        interval = self.interval_input.value()

        if not room or not bot or not command:
            QMessageBox.warning(self, "확인", "채팅방/봇/명령어를 모두 입력하세요.")
            return

        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.room_input.setEnabled(False)
        self.bot_input.setEnabled(False)
        self.command_input.setEnabled(False)
        self.interval_input.setEnabled(False)

        threading.Thread(
            target=self.macro.run,
            args=(room, bot, command, interval),
            daemon=True,
        ).start()

    def stop_macro(self):
        self.macro.stop()
        self.stop_button.setEnabled(False)

    def on_stopped(self):
        self.set_status("대기 중")
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.room_input.setEnabled(True)
        self.bot_input.setEnabled(True)
        self.command_input.setEnabled(True)
        self.interval_input.setEnabled(True)

    def show_error(self, message):
        QMessageBox.critical(self, "오류", message)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
