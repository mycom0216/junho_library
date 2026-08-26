import os

from PySide6.QtCore import QFile
from PySide6.QtUiTools import QUiLoader

from PySide6.QtWidgets import (
    QDialog,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QLineEdit
)

import member_data


# =========================================================
# 로그인 성공 클래스
# =========================================================

class LoginSuccess(QMessageBox):

    def __init__(self, parent=None):

        super().__init__(parent)

        self.setWindowTitle(
            "로그인"
        )

        self.setText(
            "로그인되었습니다."
        )

        self.setIcon(
            QMessageBox.Information
        )

        self.setStandardButtons(
            QMessageBox.Ok
        )


# =========================================================
# 아이디 / 비밀번호 오류 클래스
# =========================================================

class LoginError(QMessageBox):

    def __init__(self, parent=None):

        super().__init__(parent)

        self.setWindowTitle(
            "로그인"
        )

        self.setText(
            "아이디 또는 비밀번호가 올바르지 않습니다."
        )

        self.setIcon(
            QMessageBox.Warning
        )

        self.setStandardButtons(
            QMessageBox.Ok
        )


# =========================================================
# 회원정보 없음 클래스
# =========================================================

class MemberNotFound(QMessageBox):

    def __init__(self, parent=None):

        super().__init__(parent)

        self.setWindowTitle(
            "로그인"
        )

        self.setText(
            "회원정보가 없습니다.\n"
            "먼저 회원가입을 해주세요."
        )

        self.setIcon(
            QMessageBox.Warning
        )

        self.setStandardButtons(
            QMessageBox.Ok
        )


# =========================================================
# 로그인 클래스
# =========================================================

class LoginWindow(QDialog):

    def __init__(
        self,
        member=None,
        parent=None
    ):

        super().__init__(parent)

        # 로그인에 "성공"한 회원 정보를 담는 자리.
        # 더 이상 이 값으로 로그인을 검증하지 않고,
        # login() 안에서 매번 user_list.json을 다시 읽어서 검증한다.
        # -> 그래야 프로그램을 재실행해도, 로그아웃 후 다시 로그인해도
        #    가입해둔 계정이 그대로 살아있다.
        self.member = member

        # =================================================
        # login.ui
        # =================================================

        ui_path = os.path.join(
            os.path.dirname(
                os.path.abspath(__file__)
            ),
            "login.ui"
        )

        ui_file = QFile(ui_path)

        if not ui_file.open(
            QFile.ReadOnly
        ):

            QMessageBox.critical(
                self,
                "UI 오류",
                "login.ui 파일을 열 수 없습니다.\n\n"
                + ui_path
            )

            return

        loader = QUiLoader()

        self.ui = loader.load(
            ui_file,
            self
        )

        ui_file.close()

        if self.ui is None:

            QMessageBox.critical(
                self,
                "UI 오류",
                "login.ui를 불러오지 못했습니다."
            )

            return

        # =================================================
        # 입력창
        # =================================================

        self.id_edit = self.ui.findChild(
            QPlainTextEdit,
            "IDTextEdit"
        )

        self.pw_edit = self.ui.findChild(
            QLineEdit,
            "PWTextEdit"
        )

        self.login_button = self.ui.findChild(
            QPushButton,
            "btn_login"
        )

        self.join_button = self.ui.findChild(
            QPushButton,
            "btn_join"
        )

        # =================================================
        # ObjectName 확인
        # =================================================

        missing = []

        if self.id_edit is None:
            missing.append("IDTextEdit")

        if self.pw_edit is None:
            missing.append("PWTextEdit")

        if self.login_button is None:
            missing.append("btn_login")

        if self.join_button is None:
            missing.append("btn_join")

        if missing:

            QMessageBox.critical(
                self,
                "UI 오류",
                "다음 ObjectName을 찾을 수 없습니다.\n\n"
                + "\n".join(missing)
            )

            return

        # =================================================
        # 비밀번호 마스킹
        # =================================================

        self.pw_edit.setEchoMode(
            QLineEdit.Password
        )

        # =================================================
        # 버튼 연결
        # =================================================

        self.login_button.clicked.connect(
            self.login
        )

        self.join_button.clicked.connect(
            self.open_join
        )

    # =====================================================
    # 로그인
    # =====================================================

    def login(self):

        user_id = (
            self.id_edit
            .toPlainText()
            .strip()
        )

        password = (
            self.pw_edit
            .text()
        )

        # =================================================
        # ID 검사
        # =================================================

        if not user_id:

            QMessageBox.warning(
                self,
                "로그인",
                "아이디를 입력해주세요."
            )

            self.id_edit.setFocus()

            return

        # =================================================
        # 비밀번호 검사
        # =================================================

        if not password:

            QMessageBox.warning(
                self,
                "로그인",
                "비밀번호를 입력해주세요."
            )

            self.pw_edit.setFocus()

            return

        # =================================================
        # user_list.json 기준으로 검증
        # (메모리 self.member가 아니라 항상 파일을 다시 읽는다)
        # =================================================

        ok, result = member_data.verify_login(
            user_id,
            password
        )

        # 회원정보 없음 (아이디 자체가 없음)
        if not ok and result == "NO_ID":

            MemberNotFound(
                self
            ).exec()

            return

        # 비밀번호 불일치
        if not ok and result == "WRONG_PASSWORD":

            LoginError(
                self
            ).exec()

            return

        # =================================================
        # 로그인 성공
        # =================================================

        self.member = result  # user_list.json에서 읽어온 회원 dict

        LoginSuccess(
            self
        ).exec()

        self.accept()

    # =====================================================
    # 회원가입
    # =====================================================

    def open_join(self):

        from member_join import JoinWindow

        join_window = JoinWindow(
            self
        )

        result = join_window.exec()

        # =================================================
        # 회원가입 성공
        # =================================================

        if result == QDialog.DialogCode.Accepted:

            new_member = join_window.member

            if new_member:

                # member_data.add_user()가 돌려주는 dict는
                # 닉네임을 "id" 키로 담고 있음
                self.id_edit.setPlainText(
                    new_member.get(
                        "id",
                        ""
                    )
                )

                # 비밀번호는 자동 입력하지 않음
                self.pw_edit.clear()

                self.pw_edit.setFocus()