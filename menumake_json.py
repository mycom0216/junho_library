import pickle
import os 
import sys
import json

from PySide6.QtWidgets import QApplication
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile
from menu_data import create_menu_data

#=========메뉴데이터 불러오기==========#
menu_data = create_menu_data()


#=====json 파일로 저장=====#
with open(
    "menu.json",
    "w",
    encoding="utf-8"
) as f:
    
    json.dump(
        menu_data,
        f,
        ensure_ascii=False,
        indent=4
    )
    
print("menu.json 파일 생성 완료")

