"""
member_data.py
- 회원 계정을 user_list.json 파일에 저장/조회하는 모듈
- 프로그램을 껐다 켜도(로그아웃 후 재실행해도) 계정이 유지되도록,
  메모리(dict/list)가 아니라 항상 파일을 읽고/쓰는 방식으로 동작한다.

JSON 필드 구성 (회원 1명당):
    user_number   : int   - 자동 채번
    name          : str
    resident      : str   - 주민등록번호 (13자리, 하이픈 없이 저장)
    phone_number  : str   - 전화번호 (하이픈 없이 저장)
    gender        : str   - "male" / "female"
    e_mail        : str
    id            : str   - 로그인 아이디(닉네임)
    password      : str
    class         : str   - "관리자" / "사서" / "일반사용자"
    rating        : str   - "관리자" / "사서" / "일반회원" / "우수회원" / "VIP"
    total_rental  : int
    rental        : list
"""

import json
import os

USER_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "user_list.json"
)


def load_users():
    """user_list.json을 읽어 회원 리스트를 반환한다. 파일이 없거나 손상되었으면 빈 리스트."""
    if not os.path.exists(USER_FILE):
        return []

    try:
        with open(USER_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return []


def save_users(users):
    """회원 리스트 전체를 user_list.json에 덮어써서 저장한다."""
    with open(USER_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=2)


def get_next_user_number(users):
    """
    현재 회원 리스트 기준으로 다음 user_number를 계산한다.
    user_number가 문자열("1")로 저장돼 있거나 아예 없는 데이터가
    섞여 있어도 오류 없이 처리한다.
    """
    numbers = []

    for u in users:
        raw = u.get("user_number", 0)
        try:
            numbers.append(int(raw))
        except (TypeError, ValueError):
            continue

    if not numbers:
        return 1

    return max(numbers) + 1


def find_user_by_id(login_id):
    """로그인 아이디로 회원 1명을 찾는다. 없으면 None."""
    users = load_users()
    for u in users:
        if u["id"] == login_id:
            return u
    return None


def is_id_taken(login_id):
    """해당 아이디가 이미 가입되어 있는지 여부."""
    return find_user_by_id(login_id) is not None


def add_user(member: dict):
    """
    회원가입 시 호출.
    member = {
        "name", "resident", "phone_number",
        "gender" ("male"/"female"), "e_mail",
        "id", "password"
    }
    user_number / class / rating / total_rental / rental 은 여기서 기본값으로 채운 뒤
    파일에 append 저장하고, 저장된 최종 dict를 반환한다.
    """
    users = load_users()

    new_user = {
        "user_number": get_next_user_number(users),
        "name": member["name"],
        "resident": member["resident"],
        "phone_number": member["phone_number"],
        "gender": member["gender"],
        "e_mail": member["e_mail"],
        "id": member["id"],
        "password": member["password"],
        "class": "일반사용자",
        "rating": "일반회원",
        "total_rental": 0,
        "rental": 0
    }

    users.append(new_user)
    save_users(users)

    return new_user


def update_user(login_id, **fields):
    """회원정보 수정(예: 등급 변경, 대여 목록 갱신 등)에 사용."""
    users = load_users()

    for u in users:
        if u["id"] == login_id:
            u.update(fields)
            save_users(users)
            return u

    return None


def delete_user(login_id):
    """회원 탈퇴/삭제(관리자 기능)에 사용."""
    users = load_users()
    new_users = [u for u in users if u["id"] != login_id]

    if len(new_users) == len(users):
        return False  # 삭제할 대상이 없었음

    save_users(new_users)
    return True


def verify_login(login_id, password):
    """
    로그인 검증.
    반환값:
        (True, user_dict)          - 로그인 성공
        (False, "NO_ID")           - 아이디가 존재하지 않음
        (False, "WRONG_PASSWORD")  - 비밀번호 불일치
    """
    user = find_user_by_id(login_id)

    if user is None:
        return False, "NO_ID"

    if user["password"] != password:
        return False, "WRONG_PASSWORD"

    return True, user

# =========================================================
# 관리자 계정 존재 여부 확인
#
# 프로그램을 맨 처음 실행했는지 판단하는 용도로 쓴다.
# main.py에서 프로그램 시작 시 이 함수를 호출해서,
# False가 나오면(=관리자가 아직 한 명도 없으면)
# AdminSetupDialog를 띄워 최초 1회 관리자 계정을 만들게 한다.
# =========================================================
def has_admin():
    """
    user_list.json 안에 class가 "관리자"인 계정이
    하나라도 있으면 True, 없으면 False를 반환한다.
    """

    users = load_users()

    # any()는 리스트 안에 조건을 만족하는 요소가
    # 하나라도 있으면 True를 즉시 반환하는 내장 함수.
    # 회원이 수천 명이어도 관리자를 찾는 순간 바로 멈추므로
    # for문을 직접 돌리는 것보다 효율적이다.
    return any(
        u.get("class") == "관리자"
        for u in users
    )


# =========================================================
# 관리자 계정 생성 (최초 실행 시 딱 1번만 호출됨)
#
# 회원가입(add_user)이나 사서등록(add_librarian)과 달리,
# 관리자는 이름/주민번호/이메일 같은 개인정보를 입력받지 않는다.
# - 애초에 관리자는 "실존 인물"이 아니라 프로그램을 관리하는
#   계정 하나만 필요하기 때문에 최소한의 정보만 저장한다.
# - 아이디도 매번 새로 입력받을 필요 없이 "admin"으로 고정해서,
#   나중에 로그인할 때 아이디를 헷갈릴 일이 없게 만들었다.
# =========================================================
def create_admin(password: str):
    """
    관리자 계정을 새로 만들어 user_list.json에 저장한다.

    매개변수:
        password (str) - AdminSetupDialog에서 사용자가 직접
                          입력한 관리자 비밀번호

    반환값:
        새로 생성되어 저장된 관리자 정보 dict
    """

    # 1) 현재 저장된 회원 목록을 통째로 불러온다.
    #    (파일 맨 위에서 이미 있는 load_users() 재사용)
    users = load_users()

    # 2) 관리자 계정의 뼈대(dict)를 만든다.
    #    - user_number는 get_next_user_number()로 자동 채번
    #      (기존 add_user()에서 하던 방식과 완전히 동일)
    #    - name/resident/phone_number/gender/e_mail은
    #      관리자에게 필요 없으므로 전부 빈 문자열로 둔다.
    #    - id는 "admin"으로 고정
    #    - class="관리자", rating="관리자"로 고정
    #      (member_data.py 상단 주석에 정의된 필드 규칙을 그대로 따름)
    #    - total_rental=0, rental=[] : 관리자는 대여 기능을
    #      쓰지 않지만, 다른 회원 dict와 구조를 통일시켜서
    #      나중에 코드에서 "이 필드가 없어서 에러"가 나는 걸 방지
    new_admin = {
        "user_number": get_next_user_number(users),
        "name": "관리자",
        "resident": "",
        "phone_number": "",
        "gender": "",
        "e_mail": "",
        "id": "admin",
        "password": password,
        "class": "관리자",
        "rating": "관리자",
        "total_rental": 0,
        "rental": 0
    }

    # 3) 리스트 맨 뒤에 추가하고
    users.append(new_admin)

    # 4) 파일에 통째로 다시 저장한다.
    #    (기존 save_users()를 그대로 재사용 - 새 함수를 만들 필요 없음)
    save_users(users)

    # 5) 호출한 쪽(admin_setup.py)에서 필요할 수도 있으니
    #    생성된 최종 dict를 돌려준다.
    return new_admin