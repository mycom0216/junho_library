import os
import sys
import json

from PySide6.QtWidgets import (
    QApplication,
    QMessageBox,
    QLineEdit,
    QTableWidget,
    QTableWidgetItem
)
from PySide6.QtCore import QFile
from PySide6.QtUiTools import QUiLoader
from login import LoginWindow
import member_data
from admin_setup import AdminSetupDialog

# =========================================================
# 도서관 메인 클래스
# =========================================================

class Library:

    def __init__(self, window):

        self.window = window
        
        self.current_member = None

        # =================================================
        # 책 목록
        # =================================================

        self.books = []


        self.book_table = self.window.findChild(
            QTableWidget,
            "book_table"
        )


        # JSON 파일 불러오기
        self.load_books()
        
        
        #============== 도서 테이블 ===========#
        

        self.load_books() ### json 파일 불러오기

        # =================================================
        # 버튼
        # =================================================
        
        

        self.btn_login = self.window.findChild(
            object,
            "btn_login"
        )

        self.btn_member_info = self.window.findChild(
            object,
            "btn_member_info"
        )

        self.btn_book_search = self.window.findChild(
            object,
            "btn_book_search"
        )

        self.btn_rental_update = self.window.findChild(
            object,
            "btn_rental_update"
        )

        self.btn_book_return = self.window.findChild(
            object,
            "btn_book_return"
        )

        self.btn_book_manage = self.window.findChild(
            object,
            "btn_book_manage"
        )

        self.btn_member_manage = self.window.findChild(
            object,
            "btn_member_manage"
        )

        # =================================================
        # 회원등급 표시
        # =================================================

        self.grade_edit = self.window.findChild(
            QLineEdit,
            "lineEdit_3"
        )

        # =================================================
        # 초기 상태
        # =================================================

        if self.btn_member_info is not None:
            self.btn_member_info.setEnabled(False)

        if self.grade_edit is not None:
            self.grade_edit.clear()

        # =================================================
        # 로그인 버튼
        # =================================================

        if self.btn_login is not None:
            self.btn_login.clicked.connect(
                self.open_login
            )

        # =================================================
        # 회원정보 버튼
        # =================================================

        if self.btn_member_info is not None:
            self.btn_member_info.clicked.connect(
                self.open_member_info
            )


        # =================================================
        # 도서 관리 / 회원 관리 버튼
        # =================================================

        if self.btn_book_manage is not None:
            self.btn_book_manage.clicked.connect(
                self.open_book_manage
            )

        if self.btn_member_manage is not None:
            self.btn_member_manage.clicked.connect(
                self.open_member_manage
            )

        # =====================================================
    # 도서 관리 (관리자: 삭제 가능 / 사서: 삭제 불가)
    # =====================================================

    def open_book_manage(self):

        if self.current_member is None:
            return

        member_class = self.current_member.get(
            "class",
            ""
        )

        allow_delete = (
            member_class == "관리자"
        )

        QMessageBox.information(
            self.window,
            "도서 관리",
            "도서 관리 화면은 아직 준비 중입니다.\n"
            + ("(삭제 권한 있음)" if allow_delete else "(삭제 권한 없음)")
        )

    # =====================================================
    # 회원 관리 (관리자 전용 - 사서 등록 포함)
    # =====================================================

    def open_member_manage(self):

        if self.current_member is None:
            return

        member_class = self.current_member.get(
            "class",
            ""
        )

        if member_class != "관리자":

            QMessageBox.warning(
                self.window,
                "회원 관리",
                "관리자만 접근할 수 있습니다."
            )

            return

        from admin_main import AdminMain

        self.admin_window = AdminMain(
            admin_member=self.current_member,
            parent=self.window
        )

        self.admin_window.show()


    # =====================================================
    # book_list.json 불러오기
    # =====================================================

        # =====================================================
    # book_list.json 불러오기
    # =====================================================

    def load_books(self):

        json_path = os.path.join(
            os.path.dirname(
                os.path.abspath(__file__)
            ),
            "book_list.json"
        )

        print("JSON 경로:", json_path)

        if not os.path.exists(json_path):

            QMessageBox.warning(
                self.window,
                "도서 목록",
                "book_list.json 파일을 찾을 수 없습니다."
            )

            return

        try:

            with open(
                json_path,
                "r",
                encoding="utf-8"
            ) as file:

                self.books = json.load(file)

            print("도서 목록 불러오기 성공")
            print(self.books)

            # JSON 데이터를 화면에 출력
            self.show_books()

        except Exception as e:

            QMessageBox.critical(
                self.window,
                "도서 목록 오류",
                f"book_list.json을 불러오지 못했습니다.\n\n{e}"
            )

            self.books = []

    # =====================================================
    # 도서 목록 화면에 표시
    # =====================================================

    def show_books(self):

        if self.book_table is None:

            print("book_table을 찾을 수 없습니다.")

            return

        # 테이블 초기화
        self.book_table.clear()

        # 책 개수만큼 행 생성
        self.book_table.setRowCount(
            len(self.books)
        )

        # 4개의 열
        self.book_table.setColumnCount(4)

        # 열 제목
        self.book_table.setHorizontalHeaderLabels([
            "도서번호",
            "책 제목",
            "저자",
            "대여상태"
        ])

        # JSON 데이터 출력
        for row, book in enumerate(self.books):

            self.book_table.setItem(
                row,
                0,
                QTableWidgetItem(
                    str(book.get("book_id", ""))
                )
            )

            self.book_table.setItem(
                row,
                1,
                QTableWidgetItem(
                    str(book.get("title", ""))
                )
            )

            self.book_table.setItem(
                row,
                2,
                QTableWidgetItem(
                    str(book.get("author", ""))
                )
            )

            self.book_table.setItem(
                row,
                3,
                QTableWidgetItem(
                    str(book.get("status", "대여가능"))
                )
            )

        # 열 크기 자동 조절
        # self.book_table.resizeColumnsToContents()
        # # 테이블 전체 너비에 맞게 마지막 열까지 표시
        # self.book_table.horizontalHeader().setStretchLastSection(True)
            # 열 크기 설정
        self.book_table.setColumnWidth(0, 70)
        self.book_table.setColumnWidth(1, 450)
        self.book_table.setColumnWidth(2, 150)
        self.book_table.setColumnWidth(3, 100)

    # =====================================================
    # 로그인 창
    # =====================================================

    def open_login(self):

        # 이미 로그인 상태라면 로그아웃
        if self.current_member is not None:

            self.logout()

            return

        # 로그인 창
        login_window = LoginWindow(
            self.window
        )

        result = login_window.exec()

        # 로그인 성공
        if result == login_window.DialogCode.Accepted:

            self.current_member = login_window.member

            # 회원정보 버튼 활성화
            if self.btn_member_info is not None:

                self.btn_member_info.setEnabled(
                    True
                )

            # 로그인 → 로그아웃
            if self.btn_login is not None:

                self.btn_login.setText(
                    "로그아웃"
                )

            # 회원등급 표시
            #
            # member_data.py(user_list.json)에는 "grade"라는 키가
            # 없고 "class"(권한: 관리자/사서/일반사용자)와
            # "rating"(화면표시 등급: 일반회원/우수회원/VIP)이
            # 따로 저장된다. 관리자/사서는 class를 그대로,
            # 일반사용자는 rating을 표시한다.

            member_class = self.current_member.get(
                "class",
                "일반사용자"
            )

            if member_class in (
                "관리자",
                "사서"
            ):

                grade = member_class

            else:

                grade = self.current_member.get(
                    "rating",
                    "일반회원"
                )

            if self.grade_edit is not None:

                self.grade_edit.setText(
                    grade
                )
                
                  # 권한 설정
                if grade == "관리자":

                    self.btn_book_manage.setEnabled(True)
                    self.btn_member_manage.setEnabled(True)

                elif grade == "사서":

                    self.btn_book_manage.setEnabled(True)
                    self.btn_member_manage.setEnabled(True)

                else:

                    self.btn_book_manage.setEnabled(False)
                    self.btn_member_manage.setEnabled(False)

    # =====================================================
    # 로그아웃
    # =====================================================

    def logout(self):

        self.current_member = None

        # 회원정보 버튼 비활성화
        if self.btn_member_info is not None:

            self.btn_member_info.setEnabled(
                False
            )

        # 로그인 버튼 복구
        if self.btn_login is not None:

            self.btn_login.setText(
                "로그인"
            )

        # 회원등급 제거
        if self.grade_edit is not None:

            self.grade_edit.clear()

        QMessageBox.information(
            self.window,
            "로그아웃",
            "로그아웃되었습니다."
        )

    # =====================================================
    # 회원정보
    # =====================================================

    def open_member_info(self):

        if self.current_member is None:
            return

        from member_info import MemberInfoWindow

        member_window = MemberInfoWindow(
            self.current_member,
            self.window
        )

        member_window.exec()


# =========================================================
# 프로그램 실행 클래스
# =========================================================

class LibraryApplication:

    def __init__(self):

        # QApplication 생성
        self.app = QApplication(sys.argv)

        # =================================================
        # main.ui 경로
        # =================================================

        ui_path = os.path.join(
            os.path.dirname(
                os.path.abspath(__file__)
            ),
            "main.ui"
        )

        print("UI 경로:", ui_path)

        # =================================================
        # main.ui 열기
        # =================================================

        ui_file = QFile(ui_path)

        if not ui_file.open(QFile.ReadOnly):

            QMessageBox.critical(
                None,
                "UI 오류",
                "main.ui 파일을 열 수 없습니다.\n\n"
                + ui_path
            )

            self.window = None
            return

        # =================================================
        # UI 로드
        # =================================================

        loader = QUiLoader()

        self.window = loader.load(ui_file)

        ui_file.close()
        
     

        if self.window is None:

            QMessageBox.critical(
                None,
                "UI 오류",
                "main.ui를 불러오지 못했습니다."
            )

            return

        print("main.ui 로드 성공")

        # =================================================
        # 최초 실행 시 관리자 계정 생성
        #
        # user_list.json에 class="관리자"인 계정이 하나도 없으면
        # (=프로그램을 처음 실행하는 상황이면) 관리자 초기 비밀번호를
        # 입력받는 창을 먼저 띄운다. 이 창에서 confirm()이 호출되면
        # member_data.create_admin()이 user_list.json에 관리자
        # 계정을 저장한다.
        # =================================================

        if not member_data.has_admin():

            setup_dialog = AdminSetupDialog(
                self.window
            )

            setup_dialog.exec()


        # =================================================
        # Library 실행
        # =================================================

        self.library = Library(self.window)

        print("Library 생성 성공")

    # =====================================================
    # 프로그램 실행
    # =====================================================

    def run(self):

        if self.window is None:
            return 1

        self.window.show()

        print("프로그램 실행")

        return self.app.exec()


# =========================================================
# 프로그램 시작점
# =========================================================

if __name__ == "__main__":

    print("main.py 실행 시작")

    application = LibraryApplication()

    sys.exit(
        application.run()
    )