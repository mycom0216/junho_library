import os

from PySide6.QtCore import QFile
from PySide6.QtUiTools import QUiLoader

from PySide6.QtWidgets import (
    QDialog,
    QWidget,
    QMessageBox,
    QPushButton,
    QVBoxLayout
)


# =========================================================
# 관리자 메인 화면 클래스
#
# main.py의 open_member_manage()에서, 로그인한 회원의
# class가 "관리자"일 때만 이 창을 띄운다.
# =========================================================
class AdminMain(QWidget):

    def __init__(
        self,
        admin_member=None,
        parent=None
    ):

        super().__init__(parent)

        # 로그인된 관리자 회원 정보 (member_data 딕셔너리)
        self.admin_member = admin_member

        # =================================================
        # admin_main.ui 로드
        # =================================================

        ui_path = os.path.join(
            os.path.dirname(
                os.path.abspath(__file__)
            ),
            "admin_main.ui"
        )

        ui_file = QFile(ui_path)

        if not ui_file.open(
            QFile.ReadOnly
        ):

            QMessageBox.critical(
                self,
                "UI 오류",
                "admin_main.ui 파일을 열 수 없습니다.\n\n"
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
                "admin_main.ui를 불러오지 못했습니다."
            )

            return

        self.setFixedSize(
            self.ui.size()
        )

        layout = QVBoxLayout(
            self
        )

        layout.setContentsMargins(
            0,
            0,
            0,
            0
        )

        layout.addWidget(
            self.ui
        )

        self.setWindowTitle(
            "관리자 화면"
        )

        # =================================================
        # 버튼 찾기
        # =================================================

        self.btn_add_librarian = self.ui.findChild(
            QPushButton,
            "btn_add_librarian"
        )

        self.btn_manage_members = self.ui.findChild(
            QPushButton,
            "btn_manage_members"
        )

        self.btn_manage_books = self.ui.findChild(
            QPushButton,
            "btn_manage_books"
        )

        self.btn_rental_status = self.ui.findChild(
            QPushButton,
            "btn_rental_status"
        )

        self.btn_logout = self.ui.findChild(
            QPushButton,
            "btn_logout"
        )

        # =================================================
        # ObjectName 확인
        # =================================================

        missing = []

        widgets = {
            "btn_add_librarian": self.btn_add_librarian,
            "btn_manage_members": self.btn_manage_members,
            "btn_manage_books": self.btn_manage_books,
            "btn_rental_status": self.btn_rental_status,
            "btn_logout": self.btn_logout
        }

        for name, widget in widgets.items():

            if widget is None:

                missing.append(name)

        if missing:

            QMessageBox.critical(
                self,
                "UI 오류",
                "다음 ObjectName을 찾을 수 없습니다.\n\n"
                + "\n".join(missing)
            )

            return

        # =================================================
        # 버튼 연결
        # =================================================

        self.btn_add_librarian.clicked.connect(
            self.open_librarian_join
        )

        self.btn_manage_members.clicked.connect(
            self.open_manage_members
        )

        self.btn_manage_books.clicked.connect(
            self.open_manage_books
        )

        self.btn_rental_status.clicked.connect(
            self.open_rental_status
        )

        self.btn_logout.clicked.connect(
            self.logout
        )

    # =====================================================
    # 사서 등록
    #
    # member_join.py의 JoinWindow를 mode="librarian"으로 열면,
    # 똑같은 입력폼(member_join.ui)을 그대로 재사용하면서
    # 저장할 때만 member_data.add_librarian()을 호출하게 된다.
    # =====================================================

    def open_librarian_join(self):

        from member_join import JoinWindow

        join_window = JoinWindow(
            mode="librarian",
            parent=self
        )

        result = join_window.exec()

        if result == QDialog.DialogCode.Accepted:

            new_librarian = join_window.member

            if new_librarian:

                QMessageBox.information(
                    self,
                    "사서 등록",
                    f"'{new_librarian.get('id', '')}' "
                    "사서 계정이 등록되었습니다."
                )

    # =====================================================
    # 회원 관리 (추후 구현)
    # =====================================================

    def open_manage_members(self):

        QMessageBox.information(
            self,
            "회원 관리",
            "회원 관리 화면은 아직 준비 중입니다."
        )

    # =====================================================
    # 도서 관리 (추후 구현)
    # =====================================================

    def open_manage_books(self):

        QMessageBox.information(
            self,
            "도서 관리",
            "도서 관리 화면은 아직 준비 중입니다."
        )

    # =====================================================
    # 회원 대여현황 조회/수정 (추후 구현)
    # =====================================================

    def open_rental_status(self):

        QMessageBox.information(
            self,
            "대여현황",
            "대여현황 조회/수정 화면은 아직 준비 중입니다."
        )

    # =====================================================
    # 로그아웃 (창 닫기)
    # =====================================================

    def logout(self):

        self.close()