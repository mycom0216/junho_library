import os

from PySide6.QtCore import QFile
from PySide6.QtUiTools import QUiLoader

from PySide6.QtWidgets import (
    QDialog,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QVBoxLayout
)

import member_data


# =========================================================
# 회원정보 클래스
# =========================================================

class MemberInfoWindow(QDialog):

    def __init__(
        self,
        member=None,
        parent=None
    ):

        super().__init__(parent)

        # =================================================
        # 로그인한 회원정보
        #
        # login.py에서 넘겨준 member dict를 그대로 쓰지 않고,
        # member_data.json을 다시 조회해서 최신 정보로 갱신한다.
        # (다른 곳에서 정보가 수정됐을 수도 있으므로)
        # =================================================

        self.member = member

        if self.member:

            fresh = member_data.find_user_by_id(
                self.member.get("id", "")
            )

            if fresh is not None:

                self.member = fresh

        # =================================================
        # member_info.ui 경로
        # =================================================

        ui_path = os.path.join(
            os.path.dirname(
                os.path.abspath(__file__)
            ),
            "member_info.ui"
        )

        # =================================================
        # UI 파일 확인
        # =================================================

        if not os.path.exists(ui_path):

            QMessageBox.critical(
                self,
                "UI 오류",
                "member_info.ui 파일을 찾을 수 없습니다."
            )

            return

        # =================================================
        # UI 파일 열기
        # =================================================

        ui_file = QFile(ui_path)

        if not ui_file.open(
            QFile.ReadOnly
        ):

            QMessageBox.critical(
                self,
                "UI 오류",
                "member_info.ui 파일을 열 수 없습니다."
            )

            return

        # =================================================
        # QUiLoader
        # =================================================

        loader = QUiLoader()

        self.ui = loader.load(
            ui_file
        )

        ui_file.close()

        # =================================================
        # UI 로딩 확인
        # =================================================

        if self.ui is None:

            QMessageBox.critical(
                self,
                "UI 오류",
                "member_info.ui를 불러오지 못했습니다."
            )

            return

        # =================================================
        # Dialog 크기
        # =================================================

        self.setFixedSize(
            self.ui.size()
        )

        # =================================================
        # UI를 Dialog 안에 배치
        # =================================================

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
        # 회원정보 위젯
        #
        # 실제 member_info.ui의 ObjectName과
        # 정확하게 일치시킵니다.
        # =================================================

        # 이름
        self.name_edit = self.ui.findChild(
            QPlainTextEdit,
            "plainTextEdit"
        )

        # 주민등록번호
        self.jumin_edit = self.ui.findChild(
            QPlainTextEdit,
            "plainTextEdit_2"
        )

        # 전화번호
        self.phone_edit = self.ui.findChild(
            QPlainTextEdit,
            "plainTextEdit_3"
        )

        # 성별
        self.gender_edit = self.ui.findChild(
            QPlainTextEdit,
            "plainTextEdit_4"
        )

        # 이메일
        self.email_edit = self.ui.findChild(
            QPlainTextEdit,
            "plainTextEdit_5"
        )

        # 닉네임
        self.nickname_edit = self.ui.findChild(
            QPlainTextEdit,
            "plainTextEdit_6"
        )

        # 회원등급
        self.grade_edit = self.ui.findChild(
            QPlainTextEdit,
            "plainTextEdit_7"
        )

        # 확인 버튼
        self.btn_check = self.ui.findChild(
            QPushButton,
            "btn_check"
        )

        # =================================================
        # ObjectName 확인
        # =================================================

        missing = []

        if self.name_edit is None:
            missing.append("plainTextEdit")

        if self.jumin_edit is None:
            missing.append("plainTextEdit_2")

        if self.phone_edit is None:
            missing.append("plainTextEdit_3")

        if self.gender_edit is None:
            missing.append("plainTextEdit_4")

        if self.email_edit is None:
            missing.append("plainTextEdit_5")

        if self.nickname_edit is None:
            missing.append("plainTextEdit_6")

        if self.grade_edit is None:
            missing.append("plainTextEdit_7")

        if self.btn_check is None:
            missing.append("btn_check")

        # =================================================
        # 위젯을 찾지 못했을 경우
        # =================================================

        if missing:

            QMessageBox.critical(
                self,
                "UI 오류",
                "다음 ObjectName을 찾을 수 없습니다.\n\n"
                + "\n".join(missing)
            )

            return

        # =================================================
        # 회원정보 표시
        # =================================================

        self.show_member_info()

        # =================================================
        # 확인 버튼
        # =================================================

        self.btn_check.clicked.connect(
            self.accept
        )

    # =====================================================
    # QPlainTextEdit에 텍스트 표시
    # =====================================================

    def set_value(
        self,
        widget,
        value
    ):

        widget.setPlainText(
            str(value)
        )

    # =====================================================
    # 회원정보 표시
    #
    # member_data.py(user_list.json)에 저장된 실제 키 이름 기준:
    #   name, resident, phone_number, gender(male/female),
    #   e_mail, id, class, rating
    # =====================================================

    def show_member_info(self):

        if self.member is None:

            return

        # =================================================
        # 이름
        # =================================================

        name = self.member.get(
            "name",
            ""
        )

        self.set_value(
            self.name_edit,
            name
        )

        # =================================================
        # 주민등록번호
        #
        # 저장된 값 (member_data.py 기준, 하이픈 없음):
        #
        # 9001011234567
        #
        # 화면:
        #
        # 900101-*******
        # =================================================

        jumin = self.member.get(
            "resident",
            ""
        )

        jumin = jumin.replace(
            "-",
            ""
        )

        if len(jumin) == 13:

            masked_jumin = (
                jumin[:6]
                + "-"
                + "*******"
            )

        else:

            masked_jumin = jumin

        self.set_value(
            self.jumin_edit,
            masked_jumin
        )

        # =================================================
        # 전화번호
        #
        # 저장 (member_data.py 기준, 하이픈 없음):
        #
        # 01012345678
        #
        # 화면:
        #
        # 010-****-****
        # =================================================

        phone = self.member.get(
            "phone_number",
            ""
        )

        phone = phone.replace(
            "-",
            ""
        )

        if len(phone) == 11:

            masked_phone = (
                phone[:3]
                + "-"
                + "****"
                + "-"
                + "****"
            )

        else:

            masked_phone = phone

        self.set_value(
            self.phone_edit,
            masked_phone
        )

        # =================================================
        # 성별
        #
        # 저장 (member_data.py 기준): "male" / "female"
        # 화면 표시: "남성" / "여성"
        # =================================================

        gender_raw = self.member.get(
            "gender",
            ""
        )

        gender_display = {
            "male": "남성",
            "female": "여성"
        }.get(
            gender_raw,
            gender_raw
        )

        self.set_value(
            self.gender_edit,
            gender_display
        )

        # =================================================
        # 이메일
        # =================================================

        email = self.member.get(
            "e_mail",
            ""
        )

        self.set_value(
            self.email_edit,
            email
        )

        # =================================================
        # 닉네임(로그인 ID)
        # =================================================

        nickname = self.member.get(
            "id",
            ""
        )

        self.set_value(
            self.nickname_edit,
            nickname
        )

        # =================================================
        # 회원등급
        #
        # class가 "관리자"/"사서"면 그대로 표시,
        # 그 외(일반사용자)는 rating(일반회원/우수회원/VIP)을 표시
        # =================================================

        member_class = self.member.get(
            "class",
            "일반사용자"
        )

        if member_class in (
            "관리자",
            "사서"
        ):

            grade = member_class

        else:

            grade = self.member.get(
                "rating",
                "일반회원"
            )

        self.set_value(
            self.grade_edit,
            grade
        )