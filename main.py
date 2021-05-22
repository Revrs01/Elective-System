#!/usr/bin/env python3
# coding=utf-8
# -*- coding: UTF-8 -*-
from flask import Flask, request
import db_link

def registered_M():#將必修課加入課表中
    query ="insert into registered select distinct student.student_id,course.class_id from student,time,course where course.class = student.class and course.class_id = time.class_id and course.requirements='M';"
    cursor = conn.cursor()
    cursor.execute(query)
    conn.commit()
    
    
def clear_registered():#清除課表中所有內容
    query = "TRUNCATE TABLE registered"
    cursor = conn.cursor()
    cursor.execute(query)
    
    
def register(my_student_id,class_id):#加選課程
    query = "insert into registered VALUES('{}',{})".format(my_student_id, class_id)
    cursor = conn.cursor()
    cursor.execute(query)
    conn.commit()
    count_total_credits(my_student_id)
    
    
def check_register_quota(class_id):#檢查開課人數是否已達上限
    query = "SELECT distinct Open_Quota , Real_Quota FROM course WHERE Class_ID={};".format(class_id)
    cursor = conn.cursor()
    cursor.execute(query)
    fetchresult=cursor.fetchall()
    if(fetchresult[0][0] <= fetchresult[0][1]):#如果實收人數大於等於開放人數回傳TRUE
        return True
    else:
        return False
    
    
def check_register_clash(my_student_id,class_id):#檢查加選後是否衝堂
    query = "select Day,Sessions from registered natural join time where registered.student_id='{}';".format(my_student_id)
    cursor = conn.cursor()
    cursor.execute(query)
    cur_time = cursor.fetchall()
    query = "select Day,Sessions from time where Class_ID={};".format(class_id)
    cursor = conn.cursor()
    cursor.execute(query)
    add_time = cursor.fetchall()
    for (r1,r2) in cur_time:
        if(r1==add_time[0][0] and r2==add_time[0][1]):#如果加選後衝堂回傳TRUE
            return True
    return False


def check_register_name(my_student_id,class_id):#檢查課表中是否有同樣名稱的課
    query = "select distinct Class_Name from registered NATURAL JOIN course where Student_ID='{}';".format(my_student_id)
    cursor = conn.cursor()
    cursor.execute(query)
    cur_class_name = cursor.fetchall()
    query = "select distinct Class_Name from course where Class_ID={};".format(class_id)
    cursor = conn.cursor()
    cursor.execute(query)
    add_class_name = cursor.fetchall()
    for (r1) in cur_class_name:
        if(r1 == add_class_name[0]):#如果有回傳TRUE
            return True
    return False


def check_register_credit(class_id):#檢查已選課程中所有學分數加上加選課程會不會達上限
    query = "SELECT Credits FROM course WHERE Class_ID={}".format(class_id)
    cursor = conn.cursor()
    cursor.execute(query)
    add_credit = cursor.fetchall()
    if(credsum[0][0]+ add_credit[0][0] > 12):
        return True
    else:
        return False
    
    
def count_total_credits(my_student_id):
	global credsum
    #查詢目前課表內學分數
	query = "select sum(course.Credits) from registered natural join course where registered.student_id = '{}';".format(my_student_id)
    # 執行查詢
	cursor = conn.cursor()
	cursor.execute(query)
    #計算課程的學分數
	credsum = cursor.fetchall()


app = Flask(__name__)

conn = db_link.MySQLConnector
clear_registered()      #清除課表中所有內容
registered_M()           #將必修課加入課表中
my_student_id = 'D0XXXXXX'
credsum = 0

# 帳號及mysql部分還需修改
@app.route('/')
def signin():
    start = """
		<html>
		<title>選課系統</title>
		<body>
		<h1>登入</h1>
		<form method="post" name="information" onsubmit="return checkusername();" action="/index">
			<label>帳號：</label>
			<input name="username"><br><br>
			<label>密碼：</label>
			<input type="password" name="pd"><br><br>
			<input type="submit" value="登入">
		</form>
		</body>
		<script>
			function checkusername(){
				if(document.information.username.value==""){
					alert("請輸入學號");
					return false;
				}
			}
		</script>
		</html>
	"""
    return start

@app.route('/index', methods=['POST'])
def index():
	global my_student_id,credsum

	cn={'一':1,'二':2,'三':3,'四':4,'五':5,'六':6,'七':7} #用字典將星期數從中文數字轉為阿拉伯數字    
	my_student_id=request.form.get("username")
	
    #呼叫計算學分數函式
	count_total_credits(my_student_id)
	   
	#選課清單
	form = """
		<html>
		<title>選課系統</title>
		<body>
		<h1>選課系統</h1>
		<form method="post" action="/action" >
			<select name="my_class">
					<option value="">請選擇</option>
				<optgroup label="企管系">
					<option>企管一甲</option>
					<option>企管一乙</option>
					<option>企管二甲</option>
					<option>企管二乙</option>
					<option>企管三甲</option>
					<option>企管三乙</option>
					<option>企管四甲</option>
					<option>企管四乙</option>
					<option>企管碩一</option>
				</optgroup>
				<optgroup label="通識課">
					<option>人文</option>
					<option>自然</option>
					<option>社會</option>
					<option>統合</option>
				</optgroup>
				<optgroup label="資訊系">
					<option>資訊一甲</option>
					<option>資訊一乙</option>
					<option>資訊一丙</option>
					<option>資訊二甲</option>
					<option>資訊二乙</option>
					<option>資訊二丙</option>
					<option>資訊二丁</option>
					<option>資訊三甲</option>
					<option>資訊三乙</option>
					<option>資訊三丙</option>
					<option>資訊三丁</option>
					<option>資訊碩一</option>
					<option>資訊碩二</option>
				</optgroup>
				<optgroup label="其他">
					<option>電腦系統學程資訊三</option>
					<option>軟體工程學程資訊三</option>
					<option>網路與資安學程資訊三</option>
					<option>資訊跨領域學程資訊三</option>
				</optgroup>
			</select>
			<select name="my_department">
				<option value="">請選擇</option>
				<option>企業管理學系</option>
				<option>通識</option>
				<option>資訊工程學系</option>
			</select>
			<input name="my_name">
			<input type="submit" value="送出">
		</form>
		<p><a href="/">重新登入</a></p>
		<label>使用者：{}</label><br>
		<label>總學分：{}</label>
	""".format(my_student_id,credsum[0][0])

	#使用者的必修課表
	form+="""
		<table border="2" width="25%">
			<tr>
				<th align='center' valign="middle"></th>
				<th align='center' valign="middle">Mon</th>
				<th align='center' valign="middle">Tue</th>
				<th align='center' valign="middle">Wed</th>
				<th align='center' valign="middle">Thu</th>
				<th align='center' valign="middle">Fri</th>
				<th align='center' valign="middle">Sat</th>
				<th align='center' valign="middle">Sun</th>
			</tr>
	"""
    #找出使用者的必修課的學號、課程代碼、課程名稱、星期數、節次，主要用來查詢課程的時間
	query = "select registered.student_id,registered.class_id,course.class_name,time.day,time.sessions,course.credits from course,time,registered where course.class_id=time.class_id and registered.class_id=course.class_id and registered.student_id = '{}';".format(my_student_id)
	cursor = conn.cursor()
	cursor.execute(query)
	fetchresult=cursor.fetchall()
    
	#比對星期數和節次將課程名稱填進去課表
	for i in range(1,15):
		form+="<tr>"
		form+="<th align='center' valign='middle'>{}</th>".format(i)
		for j in range(1,8):
			for (r1,r2,r3,r4,r5,r6) in fetchresult:
				if i==r5 and j==cn[r4]:
					form+="<td align='center' valign='middle'>{}</th>".format(r3)
					break;
			else:
				form+="<td align='center' valign='middle'> </th>"
		form+="</tr>"

	form+="</table>"

	form+="""
		</body>
		</html> 
	"""

	return form


@app.route('/action', methods=['POST'])
def action():
    global credsum
    # 取得輸入的文字
    my_class = request.form.get("my_class")
    my_department = request.form.get("my_department")
    my_class_name = request.form.get("my_name")
    # 欲查詢的 query 指令

    query = "SELECT * FROM course where class_name LIKE '%{}%' and class LIKE '%{}%' and department LIKE '%{}%';".format(my_class_name, my_class, my_department)

    # 執行查詢
    cursor = conn.cursor()
    cursor.execute(query)

    results = """
		<!DOCTYPE html>
		<html>
		<title>選課系統</title>
		<body>
		<form method="post" action="/action" >
		<input type ="button" onclick="history.back()" value="Back to Query Interface"></input><br>
		</form>
        <form method="post" action="/register_class">
		<table border="1" style="width:100%">
			<tr>
				<th align='center' valign="middle">開課班級</th>
				<th align='center' valign="middle">課程名稱</th>
				<th align='center' valign="middle">課程代碼</th>
				<th align='center' valign="middle">學分</th>
				<th align='center' valign="middle">必選修</th>
				<th align='center' valign="middle">系所</th>
				<th align='center' valign="middle">實收名額/開放名額</th>
				<th align='center' valign="middle">教師</th>
				<th align='center' valign="middle">加選</th>
			</tr>
	"""
    # 目前找不到正確使用超連結回到上一頁的做法，只好換成按鈕，並使用回到歷史紀錄中的上一頁
    # 取得並列出所有查詢結果
    for (d1, d2, d3, d4, d5, d6, d7, d8, d9) in cursor.fetchall():
        results += """
			<tr>
				<td align='center' valign="middle">{}</td>
				<td align='center' valign="middle">{}</td>
				<td align='center' valign="middle">{}</td>
				<td align='center' valign="middle">{}</td>
				<td align='center' valign="middle">{}</td>
				<td align='center' valign="middle">{}</td>
				<td align='center' valign="middle">{}/{}</td>
				<td align='center' valign="middle">{}</td>
				<td align='center' valign="middle"><button name="my_class_id" value={} onclick="/register_class">加選</button></td>
			</tr>
		""".format(d1, d2, d3, d4, d5, d6, d8, d7, d9, d3)

    results += """
		</table>
		</body>
		</html>
	"""
    return results
@app.route('/register_class', methods=['GET', 'POST'])
def register_class():
    #my_student_id = request.form.get("username")
    class_id = request.form.get("my_class_id")
    if(check_register_quota(class_id)):
        view = """
        <html>
        <body>
        <h1>加選失敗，人數已滿</h1>
        <input type ="button" onclick="history.back()" value="Back to Query Interface"></input><br>
        </body>
        </html>
    """
    elif(check_register_clash(my_student_id,class_id)):
        view = """
        <html>
        <body>
        <h1>加選失敗，課程衝堂</h1>
        <input type ="button" onclick="history.back()" value="Back to Query Interface"></input><br>
        </body>
        </html>
    """
    elif(check_register_name(my_student_id,class_id)):
        view = """
        <html>
        <body>
        <h1>加選失敗，已有相同課程在課表中</h1>
        <input type ="button" onclick="history.back()" value="Back to Query Interface"></input><br>
        </body>
        </html>
    """
    elif(check_register_credit(class_id)):
        view = """
        <html>
        <body>
        <h1>加選失敗，學分已達上限</h1>
        <input type ="button" onclick="history.back()" value="Back to Query Interface"></input><br>
        </body>
        </html>
    """
    else:
        register(my_student_id,class_id)
        view = """
        <html>
        <body>
        <h1>加選成功</h1>
        <input type ="button" onclick="history.back()" value="Back to Query Interface"></input><br>
        </body>
        </html>
    """
        
    return view