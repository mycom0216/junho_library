import os
import sys
import json

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QMessageBox,
    QLineEdit,
    QTableWidget,
    QPushButton,
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

        # =================================================
        # book_table 확인
        # =================================================

        if self.book_table is None:

            print("book_table을 찾을 수 없습니다.")

            return

        # =================================================
        # 테이블 초기화
        # =================================================

        self.book_table.clear()

        # 왼쪽 1, 2, 3, 4... 행 번호 제거
        self.book_table.verticalHeader().setVisible(False)

        # =================================================
        # 행 개수 설정
        # =================================================

        self.book_table.setRowCount(
            len(self.books)
        )

        # =================================================
        # 열 개수 설정
        #
        # 0 : 제목
        # 1 : 저자
        # 2 : 발행처
        # 3 : 주제
        # 4 : 대상
        # 5 : 대여여부
        # 6 : 대여 버튼
        # =================================================

        self.book_table.setColumnCount(7)

        # =================================================
        # 열 제목
        # =================================================

        self.book_table.setHorizontalHeaderLabels([
            "제목",
            "저자",
            "발행처",
            "주제",
            "대상",
            "대여여부",
            "대여"
        ])

        # =================================================
        # JSON 데이터를 한 권씩 테이블에 출력
        # =================================================

        for row, book in enumerate(self.books):

            # -------------------------------------------------
            # 제목
            # -------------------------------------------------

            self.book_table.setItem(
                row,
                0,
                QTableWidgetItem(
                    str(
                        book.get(
                            "title",
                            ""
                        )
                    )
                )
            )

            # -------------------------------------------------
            # 저자
            # -------------------------------------------------

            self.book_table.setItem(
                row,
                1,
                QTableWidgetItem(
                    str(
                        book.get(
                            "author",
                            ""
                        )
                    )
                )
            )

            # -------------------------------------------------
            # 발행처
            # -------------------------------------------------

            self.book_table.setItem(
                row,
                2,
                QTableWidgetItem(
                    str(
                        book.get(
                            "publisher",
                            ""
                        )
                    )
                )
            )

            # -------------------------------------------------
            # 주제
            # -------------------------------------------------

            self.book_table.setItem(
                row,
                3,
                QTableWidgetItem(
                    str(
                        book.get(
                            "subject",
                            ""
                        )
                    )
                )
            )

            # -------------------------------------------------
            # 대상
            # -------------------------------------------------

            self.book_table.setItem(
                row,
                4,
                QTableWidgetItem(
                    str(
                        book.get(
                            "target",
                            ""
                        )
                    )
                )
            )

            # -------------------------------------------------
            # 대여여부
            # -------------------------------------------------

            rental = str(
                book.get(
                    "rental",
                    "1"
                )
            )

            # rental == 1 → 대여가능
            # rental == 0 → 대여중

            if rental == "1":

                rental_text = "대여가능"

            else:

                rental_text = "대여중"

            self.book_table.setItem(
                row,
                5,
                QTableWidgetItem(
                    rental_text
                )
            )

            # -------------------------------------------------
            # 대여 버튼
            # -------------------------------------------------

            rental_button = QPushButton(
                "대여"
            )

            # 현재 행 번호를 기억
            rental_button.clicked.connect(
                lambda checked=False, r=row:
                self.rental_book(r)
            )

            # 이미 대여중이면 버튼 비활성화
            if rental != "1":

                rental_button.setEnabled(
                    False
                )

            # 7번째 열에 대여 버튼 추가
            self.book_table.setCellWidget(
                row,
                6,
                rental_button
            )

        # =================================================
        # 열 너비 설정
        #
        # 중요:
        # 이 부분은 for문 바깥에 있어야 함
        # =================================================

        self.book_table.setColumnWidth(
            0,
            300
        )

        self.book_table.setColumnWidth(
            1,
            150
        )

        self.book_table.setColumnWidth(
            2,
            150
        )

        self.book_table.setColumnWidth(
            3,
            120
        )

        self.book_table.setColumnWidth(
            4,
            100
        )

        self.book_table.setColumnWidth(
            5,
            100
        )

        self.book_table.setColumnWidth(
            6,
            80
        )

   
        # =====================================================
    # 도서 대여
    # =====================================================

    def rental_book(self, row):

        # 현재 도서
        book = self.books[row]

        # 이미 대여중인지 확인
        if str(book.get("rental", "1")) != "1":

            QMessageBox.warning(
                self.window,
                "대여 불가",
                "이미 대여 중인 도서입니다."
            )

            return

        # =================================================
        # 대여 확인 창
        # =================================================

        dialog = QMessageBox()

        dialog.setWindowTitle(
            "도서 대여"
        )

        dialog.setText(
            "대여하시겠습니까?"
        )

        # 확인 / 취소 버튼
        ok_button = dialog.addButton(
            "확인",
            QMessageBox.AcceptRole
        )

        dialog.addButton(
            "취소",
            QMessageBox.RejectRole
        )

        # =================================================
        # 메인 창 가운데에 배치
        # =================================================

        dialog.adjustSize()

        main_rect = self.window.frameGeometry()

        dialog_rect = dialog.frameGeometry()

        dialog.move(
            main_rect.center() -
            dialog_rect.center()
        )

        # 창 실행
        dialog.exec()

        # =================================================
        # 확인을 누른 경우
        # =================================================

        if dialog.clickedButton() == ok_button:

            # JSON 대여 상태 변경
            book["rental"] = "0"

            # 화면 대여여부 변경
            status_item = self.book_table.item(
                row,
                5
            )

            if status_item is not None:

                status_item.setText(
                    "대여중"
                )

            # 대여 버튼 비활성화
            rental_button = self.book_table.cellWidget(
                row,
                6
            )

            if rental_button is not None:

                rental_button.setEnabled(
                    False
                )

            # JSON 저장
            self.save_books()

                      # =================================================
            # 대여 완료 메시지
            # =================================================

            complete_dialog = QMessageBox()

            complete_dialog.setWindowTitle(
                "대여 완료"
            )

            complete_dialog.setText(
                "도서가 대여되었습니다."
            )

            complete_dialog.setStandardButtons(
                QMessageBox.StandardButton.Ok
            )

            # OK 버튼 글자 변경
            complete_dialog.button(
                QMessageBox.StandardButton.Ok
            ).setText("확인")

            # =================================================
            # 메인 창 가운데에 배치
            # =================================================

            complete_dialog.adjustSize()

            main_rect = self.window.frameGeometry()

            dialog_rect = complete_dialog.frameGeometry()

            complete_dialog.move(
                main_rect.center()
                - dialog_rect.center()
            )

            # 완료 창 표시
            complete_dialog.exec()
    
        # =====================================================
    # book_list.json 저장
    # =====================================================

    def save_books(self):

        json_path = os.path.join(
            os.path.dirname(
                os.path.abspath(__file__)
            ),
            "book_list.json"
        )

        try:

            with open(
                json_path,
                "w",
                
                encoding="utf-8"
            ) as file:

                json.dump(
                    self.books,
                    file,
                    ensure_ascii=False,
                    indent=4
                )

            print("도서 목록 저장 성공")

        except Exception as e:

            QMessageBox.critical(
                self.window,
                "도서 목록 오류",
                f"도서 목록을 저장하지 못했습니다.\n\n{e}"
            )
        
        

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