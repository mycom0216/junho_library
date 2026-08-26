import os
import re

from PySide6.QtCore import QFile, Qt
from PySide6.QtUiTools import QUiLoader

from PySide6.QtWidgets import (
    QDialog,
    QMessageBox,
    QLineEdit,
    QPushButton,
    QCheckBox,
    QVBoxLayout
)

import member_data


# =========================================================
# 주민등록번호 / 전화번호 마스킹 입력 클래스
# =========================================================

class MaskedLineEdit(QLineEdit):

    def __init__(self, mask_type, parent=None):

        super().__init__(parent)

        self.mask_type = mask_type
        self.real_value = ""

        if mask_type == "jumin":
            self.max_length = 13

        elif mask_type == "phone":
            self.max_length = 11

    # =====================================================
    # 키 입력
    # =====================================================

    def keyPressEvent(self, event):

        key = event.key()
        text = event.text()

        # 숫자 입력
        if text.isdigit():

            if len(self.real_value) >= self.max_length:
                return

            self.real_value += text

            self.update_display()

            return

        # Backspace
        if key == Qt.Key_Backspace:

            if self.real_value:

                self.real_value = (
                    self.real_value[:-1]
                )

                self.update_display()

            return

        # Delete
        if key == Qt.Key_Delete:

            self.real_value = ""

            self.update_display()

            return

        # Ctrl + A
        if (
            key == Qt.Key_A
            and event.modifiers() & Qt.ControlModifier
        ):

            self.real_value = ""

            self.update_display()

            return

        # Ctrl + V
        if (
            key == Qt.Key_V
            and event.modifiers() & Qt.ControlModifier
        ):

            text = self.clipboard().text()

            numbers = ""

            for char in text:

                if char.isdigit():

                    numbers += char

            self.real_value = (
                numbers[:self.max_length]
            )

            self.update_display()

            return

        super().keyPressEvent(event)

    # =====================================================
    # 화면 표시
    # =====================================================

    def update_display(self):

        # 주민등록번호
        if self.mask_type == "jumin":

            if len(self.real_value) <= 6:

                display = self.real_value

            else:

                display = (
                    self.real_value[:6]
                    + "-"
                    + "*"
                    * (
                        len(self.real_value) - 6
                    )
                )

        # 전화번호
        elif self.mask_type == "phone":

            if len(self.real_value) <= 3:

                display = self.real_value

            elif len(self.real_value) <= 7:

                display = (
                    self.real_value[:3]
                    + "-"
                    + "*"
                    * (
                        len(self.real_value) - 3
                    )
                )

            else:

                display = (
                    self.real_value[:3]
                    + "-"
                    + "****"
                    + "-"
                    + "*"
                    * (
                        len(self.real_value) - 7
                    )
                )

        else:

            display = self.real_value

        self.setText(display)

        self.setCursorPosition(
            len(display)
        )

    # =====================================================
    # 실제 값
    # =====================================================

    def get_real_value(self):

        return self.real_value

    # =====================================================
    # 초기화
    # =====================================================

    def clear(self):

        self.real_value = ""

        super().clear()


# =========================================================
# 회원가입 확인 클래스
# =========================================================

class JoinConfirm(QMessageBox):

    def __init__(self, parent=None):

        super().__init__(parent)

        self.setWindowTitle(
            "회원가입"
        )

        self.setText(
            "회원가입 하시겠습니까?"
        )

        self.setIcon(
            QMessageBox.Question
        )

        self.setStandardButtons(
            QMessageBox.Yes
            | QMessageBox.No
        )


# =========================================================
# 회원가입 클래스
# =========================================================

class JoinWindow(QDialog):

    def __init__(self, parent=None):

        super().__init__(parent)

        self.member = None

        # =================================================
        # UI 경로
        # =================================================

        ui_path = os.path.join(
            os.path.dirname(
                os.path.abspath(__file__)
            ),
            "member_join.ui"
        )

        ui_file = QFile(ui_path)

        if not ui_file.open(
            QFile.ReadOnly
        ):

            QMessageBox.critical(
                self,
                "UI 오류",
                "member_join.ui 파일을 열 수 없습니다.\n\n"
                + ui_path
            )

            return

        loader = QUiLoader()

        self.ui = loader.load(
            ui_file
        )

        ui_file.close()

        if self.ui is None:

            QMessageBox.critical(
                self,
                "UI 오류",
                "member_join.ui를 불러오지 못했습니다."
            )

            return

        # =================================================
        # UI 크기
        # =================================================

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

        # =================================================
        # 입력창
        # =================================================

        self.name_edit = self.ui.findChild(
            QLineEdit,
            "name_edit"
        )

        self.jumin_edit = self.ui.findChild(
            QLineEdit,
            "jumin_edit"
        )

        self.phone_edit = self.ui.findChild(
            QLineEdit,
            "phone_edit"
        )

        self.email_edit = self.ui.findChild(
            QLineEdit,
            "email_edit"
        )

        self.nickname_edit = self.ui.findChild(
            QLineEdit,
            "nickname_edit"
        )

        self.password_edit = self.ui.findChild(
            QLineEdit,
            "password_edit"
        )

        self.password_confirm_edit = self.ui.findChild(
            QLineEdit,
            "password_confirm_edit"
        )

        # =================================================
        # 성별
        # =================================================

        self.male_checkbox = self.ui.findChild(
            QCheckBox,
            "man_checkbox"
        )

        self.female_checkbox = self.ui.findChild(
            QCheckBox,
            "woman_checkbox"
        )

        # =================================================
        # 버튼
        # =================================================

        self.btn_check = self.ui.findChild(
            QPushButton,
            "btn_check"
        )

        self.btn_cancel = self.ui.findChild(
            QPushButton,
            "btn_cancel"
        )

        # =================================================
        # ObjectName 확인
        # =================================================

        missing = []

        widgets = {
            "name_edit": self.name_edit,
            "jumin_edit": self.jumin_edit,
            "phone_edit": self.phone_edit,
            "email_edit": self.email_edit,
            "nickname_edit": self.nickname_edit,
            "password_edit": self.password_edit,
            "password_confirm_edit":
                self.password_confirm_edit,
            "man_checkbox": self.male_checkbox,
            "woman_checkbox": self.female_checkbox,
            "btn_check": self.btn_check,
            "btn_cancel": self.btn_cancel
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
        # 비밀번호 마스킹
        # =================================================

        self.password_edit.setEchoMode(
            QLineEdit.Password
        )

        self.password_confirm_edit.setEchoMode(
            QLineEdit.Password
        )

        # =================================================
        # 주민번호 / 전화번호 입력창 교체
        # =================================================

        self.replace_masked_edit(
            self.jumin_edit,
            "jumin"
        )

        self.replace_masked_edit(
            self.phone_edit,
            "phone"
        )

        # =================================================
        # 버튼 연결
        # =================================================

        self.btn_check.clicked.connect(
            self.check_join
        )

        self.btn_cancel.clicked.connect(
            self.reject
        )

        self.male_checkbox.toggled.connect(
            self.gender_changed
        )

        self.female_checkbox.toggled.connect(
            self.gender_changed
        )

    # =====================================================
    # 마스킹 입력창 교체
    # =====================================================

    def replace_masked_edit(
        self,
        old_edit,
        mask_type
    ):

        parent = old_edit.parentWidget()

        geometry = old_edit.geometry()

        old_edit.hide()

        new_edit = MaskedLineEdit(
            mask_type,
            parent
        )

        new_edit.setGeometry(
            geometry
        )

        new_edit.setStyleSheet(
            old_edit.styleSheet()
        )

        if mask_type == "jumin":

            new_edit.setPlaceholderText(
                "000000-*******"
            )

        elif mask_type == "phone":

            new_edit.setPlaceholderText(
                "010-****-****"
            )

        new_edit.show()

        if mask_type == "jumin":

            self.jumin_edit = new_edit

        elif mask_type == "phone":

            self.phone_edit = new_edit

    # =====================================================
    # 성별 선택
    # =====================================================

    def gender_changed(self, checked):

        if not checked:
            return

        sender = self.sender()

        if sender == self.male_checkbox:

            self.female_checkbox.setChecked(
                False
            )

        elif sender == self.female_checkbox:

            self.male_checkbox.setChecked(
                False
            )

    # =====================================================
    # 회원가입 검사
    # =====================================================

    def check_join(self):

        name = self.name_edit.text().strip()

        jumin = (
            self.jumin_edit
            .get_real_value()
        )

        phone = (
            self.phone_edit
            .get_real_value()
        )

        email = self.email_edit.text().strip()

        nickname = (
            self.nickname_edit
            .text()
            .strip()
        )

        password = self.password_edit.text()

        password_confirm = (
            self.password_confirm_edit
            .text()
        )

        # =================================================
        # 성별
        # =================================================

        if self.male_checkbox.isChecked():

            gender = "male"

        elif self.female_checkbox.isChecked():

            gender = "female"

        else:

            gender = ""

        # =================================================
        # 이름
        # =================================================

        if not name:

            QMessageBox.warning(
                self,
                "회원가입",
                "이름을 입력해주세요."
            )

            self.name_edit.setFocus()

            return

        # =================================================
        # 주민등록번호
        # =================================================

        if not self.validate_jumin(jumin):

            QMessageBox.warning(
                self,
                "회원가입",
                "올바른 주민등록번호를 입력해주세요."
            )

            self.jumin_edit.setFocus()

            return

        # =================================================
        # 전화번호
        # =================================================

        if not self.validate_phone(phone):

            QMessageBox.warning(
                self,
                "회원가입",
                "전화번호를 올바르게 입력해주세요.\n"
                "예: 010-1234-5678"
            )

            self.phone_edit.setFocus()

            return

        # =================================================
        # 성별
        # =================================================

        if not gender:

            QMessageBox.warning(
                self,
                "회원가입",
                "성별을 선택해주세요."
            )

            return

        # =================================================
        # 이메일
        # =================================================

        email_pattern = (
            r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
        )

        if not re.match(
            email_pattern,
            email
        ):

            QMessageBox.warning(
                self,
                "회원가입",
                "이메일을 올바르게 입력해주세요."
            )

            self.email_edit.setFocus()

            return

        # =================================================
        # ID (닉네임)
        # =================================================

        if not nickname:

            QMessageBox.warning(
                self,
                "회원가입",
                "닉네임(ID)을 입력해주세요."
            )

            self.nickname_edit.setFocus()

            return

        # ID 중복 검사 - user_list.json 기준
        if member_data.is_id_taken(nickname):

            QMessageBox.warning(
                self,
                "회원가입",
                "이미 사용 중인 닉네임(ID)입니다."
            )

            self.nickname_edit.setFocus()

            return

        # =================================================
        # 비밀번호
        # =================================================

        if not password:

            QMessageBox.warning(
                self,
                "회원가입",
                "비밀번호를 입력해주세요."
            )

            self.password_edit.setFocus()

            return

        # =================================================
        # 비밀번호 확인
        # =================================================

        if not password_confirm:

            QMessageBox.warning(
                self,
                "회원가입",
                "비밀번호 확인을 입력해주세요."
            )

            self.password_confirm_edit.setFocus()

            return

        # =================================================
        # 비밀번호 일치
        # =================================================

        if password != password_confirm:

            QMessageBox.warning(
                self,
                "비밀번호 오류",
                "비밀번호가 틀립니다."
            )

            self.password_confirm_edit.clear()

            self.password_confirm_edit.setFocus()

            return

        # =================================================
        # 회원가입 확인
        # =================================================

        confirm = JoinConfirm(
            self
        )

        result = confirm.exec()

        if result != QMessageBox.Yes:

            return

        # =================================================
        # 회원정보 생성 + user_list.json 저장
        # =================================================

        new_member = {
            "name": name,
            "resident": jumin,
            "phone_number": phone,
            "gender": gender,
            "e_mail": email,
            "id": nickname,
            "password": password
        }

        # member_data.add_user()가 user_number/class/rating/
        # total_rental/rental 기본값을 채워 user_list.json에
        # append 저장하고, 저장된 최종 dict를 돌려준다.
        self.member = member_data.add_user(new_member)

        # =================================================
        # 완료
        # =================================================

        QMessageBox.information(
            self,
            "회원가입",
            "회원가입이 완료되었습니다."
        )

        self.accept()

    # =====================================================
    # 주민등록번호 검증
    # =====================================================

    def validate_jumin(self, jumin):

        if not re.fullmatch(
            r"\d{13}",
            jumin
        ):

            return False

        # 성별/발급지역 구분번호
        if jumin[6] not in "12345678":

            return False

        # 검증번호
        weights = [
            2, 3, 4, 5, 6, 7,
            8, 9, 2, 3, 4, 5
        ]

        total = 0

        for i in range(12):

            total += (
                int(jumin[i])
                * weights[i]
            )

        check = (
            11 - (total % 11)
        ) % 10

        return (
            check == int(jumin[12])
        )

    # =====================================================
    # 전화번호 검증
    # =====================================================

    def validate_phone(self, phone):

        return bool(
            re.fullmatch(
                r"010\d{8}",
                phone
            )
        )