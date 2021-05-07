#!/usr/bin/env python3
# coding=utf-8
# -*- coding: UTF-8 -*-
from flask import Flask, request
import MySQLdb

app = Flask(__name__)

# 建立資料庫連線
#charset='utf8'用於可以輸出中文
conn = MySQLdb.connect(host="127.0.0.1",
	user="Jin",
	passwd="st123456",
	db="test",
	charset='utf8')

#帳號及mysql部分還需修改
@app.route('/')
def signin():
	start = """
	<html>
	<title>選課系統</title>
	<body>
	<h1>登入</h1>
	<form method="post" action="/index">
		<label>帳號：</label>
		<input type="text" name="username"><br><br>
		<label>帳號：</label>
		<input type="password" name="pd"><br><br>
		<input type="submit" value="登入">
	</form>
	</body>
	</html>
	"""
	return start

	
@app.route('/index', methods=['POST'])
def index():
	form = """
	<html>
	<title>選課系統</title>
	<body>
	<h1>選課系統</h1>
	<form method="post" action="/action" >
		<select name="my_head">
			<option>楊</option>
			<option>吳</option>
			<option>劉</option>
		</select>
	<input type="submit" value="送出">
	</form>
	<p><a href="/">重新登入</a></p>
	</body>
	</html> 
	"""
	return form

@app.route('/action', methods=['POST'])
def action():
    # 取得輸入的文字
	my_head = request.form.get("my_head")
    # 欲查詢的 query 指令
	query = "SELECT name,studentid FROM students where name LIKE '%{}%';".format(my_head)
    # 執行查詢
	cursor = conn.cursor()
	cursor.execute(query)

	results = """
	<html>
	<title>選課系統</title>
	<body>
	<form method="post" action="/index" >
	<input type ="button" onclick="history.back()" value="Back to Query Interface"></input><br>
	"""
	#目前找不到正確使用超連結回到上一頁的做法，只好換成按鈕，並使用回到歷史紀錄中的上一頁
    #取得並列出所有查詢結果
	for (description,d2) in cursor.fetchall():
		results += "<p>{}:{}</p>".format(description,d2)
	results+="""
	</body>
	</html>
	"""
	return results