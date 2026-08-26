from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QMessageBox
)

import member_data


# =========================================================
# 관리자 초기 설정 창
#
# 프로그램을 맨 처음 실행했을 때(=user_list.json에 관리자
# 계정이 하나도 없을 때) main.py에서 이 창을 띄운다.
# 여기서 입력한 비밀번호로 member_data.create_admin()이
# 호출되어 관리자 계정(id="admin")이 저장된다.
# =========================================================
class AdminSetupDialog(QDialog):

    def __init__(self, parent=None):

        super().__init__(parent)

        self.setWindowTitle(
            "관리자 계정 초기 설정"
        )

        # setModal(True): 이 창이 떠 있는 동안에는
        # 뒤에 있는 다른 창(main.ui)을 조작할 수 없게 막는다.
        # 관리자 계정을 만들기 전까지는 프로그램을 정상적으로
        # 쓸 수 없어야 하므로 모달로 띄운다.
        self.setModal(True)

        layout = QVBoxLayout(self)

        # =================================================
        # 안내 문구
        # =================================================

        layout.addWidget(
            QLabel(
                "관리자 계정이 존재하지 않습니다.\n"
                "최초 실행이므로 관리자 비밀번호를 설정해주세요.\n"
                "(관리자 아이디는 'admin'으로 고정됩니다)"
            )
        )

        # =================================================
        # 비밀번호 입력
        # =================================================

        self.pw_edit = QLineEdit()

        # 입력값을 ●●●로 가려서 보여준다 (로그인창과 동일한 방식)
        self.pw_edit.setEchoMode(
            QLineEdit.Password
        )

        self.pw_edit.setPlaceholderText(
            "비밀번호"
        )

        layout.addWidget(
            self.pw_edit
        )

        # =================================================
        # 비밀번호 확인 입력
        # =================================================

        self.pw_confirm_edit = QLineEdit()

        self.pw_confirm_edit.setEchoMode(
            QLineEdit.Password
        )

        self.pw_confirm_edit.setPlaceholderText(
            "비밀번호 확인"
        )

        layout.addWidget(
            self.pw_confirm_edit
        )

        # =================================================
        # 설정 완료 버튼
        # =================================================

        confirm_button = QPushButton(
            "설정 완료"
        )

        confirm_button.clicked.connect(
            self.confirm
        )

        layout.addWidget(
            confirm_button
        )

    # =====================================================
    # 설정 완료 버튼 클릭 시 실행
    # =====================================================

    def confirm(self):

        password = self.pw_edit.text()
        password_confirm = self.pw_confirm_edit.text()

        # 비밀번호를 아예 입력 안 한 경우
        if not password:

            QMessageBox.warning(
                self,
                "관리자 설정",
                "비밀번호를 입력해주세요."
            )

            return

        # 비밀번호와 비밀번호 확인이 다른 경우
        if password != password_confirm:

            QMessageBox.warning(
                self,
                "관리자 설정",
                "비밀번호가 일치하지 않습니다."
            )

            return

        # =================================================
        # member_data.py의 create_admin() 호출
        #
        # 이 함수가 user_list.json에 다음과 같은 계정을 추가한다:
        #   {"id": "admin", "class": "관리자",
        #    "rating": "관리자", "password": password, ...}
        # =================================================

        member_data.create_admin(
            password
        )

        QMessageBox.information(
            self,
            "관리자 설정",
            "관리자 계정이 생성되었습니다."
        )

        # accept()를 호출해야 setup_dialog.exec()가 끝나고
        # main.py의 다음 코드(Library 실행)로 넘어간다.
        self.accept()