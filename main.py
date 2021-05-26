#!/usr/bin/env python3
# coding=utf-8
# -*- coding: UTF-8 -*-
from flask import Flask, request
import db_link


def registered_M():  # 將必修課加入課表中
    query = "INSERT INTO registered SELECT DISTINCT student.student_id,course.class_id FROM student,time,course WHERE course.class = student.class AND course.class_id = time.class_id AND course.requirements='M';"
    cursor = conn.cursor()
    cursor.execute(query)
    conn.commit()


def clear_registered():  # 清除課表中所有內容
    query = "TRUNCATE TABLE registered"
    cursor = conn.cursor()
    cursor.execute(query)


def register(my_student_id, class_id):  # 加選課程
    query = "insert into registered VALUES('{}',{})".format(my_student_id, class_id)
    cursor = conn.cursor()
    cursor.execute(query)
    conn.commit()
    count_total_credits(my_student_id)
    cursor.execute("update course set real_quota = real_quota+1 where class_ID = '{}';".format(class_id))
    conn.commit()


def check_register_quota(class_id):  # 檢查開課人數是否已達上限
    query = "SELECT DISTINCT Open_Quota , Real_Quota FROM course WHERE Class_ID={};".format(class_id)
    cursor = conn.cursor()
    cursor.execute(query)
    fetchresult = cursor.fetchall()
    if (fetchresult[0][0] <= fetchresult[0][1]):  # 如果實收人數大於等於開放人數回傳TRUE
        return True
    else:
        return False


def check_register_clash(my_student_id, class_id):  # 檢查加選後是否衝堂
    query = "SELECT Day,Sessions FROM registered NATURAL JOIN time WHERE registered.student_id='{}';".format(
        my_student_id)
    cursor = conn.cursor()
    cursor.execute(query)
    cur_time = cursor.fetchall()
    query = "SELECT Day,Sessions FROM time WHERE Class_ID={};".format(class_id)
    cursor = conn.cursor()
    cursor.execute(query)
    add_time = cursor.fetchall()
    for (r1, r2) in cur_time:
        if (r1 == add_time[0][0] and r2 == add_time[0][1]):  # 如果加選後衝堂回傳TRUE
            return True
    return False


def check_register_name(my_student_id, class_id):  # 檢查課表中是否有同樣名稱的課
    query = "SELECT DISTINCT Class_Name FROM registered NATURAL JOIN course where Student_ID='{}';".format(
        my_student_id)
    cursor = conn.cursor()
    cursor.execute(query)
    cur_class_name = cursor.fetchall()
    query = "select distinct Class_Name from course where Class_ID={};".format(class_id)
    cursor = conn.cursor()
    cursor.execute(query)
    add_class_name = cursor.fetchall()
    for (r1) in cur_class_name:
        if (r1 == add_class_name[0]):  # 如果有回傳TRUE
            return True
    return False


def check_register_credit(class_id):  # 檢查已選課程中所有學分數加上加選課程會不會達上限
    query = "SELECT Credits FROM course WHERE Class_ID={}".format(class_id)
    cursor = conn.cursor()
    cursor.execute(query)
    add_credit = cursor.fetchall()
    if (credsum[0][0] + add_credit[0][0] > 30):
        return True
    else:
        return False


def count_total_credits(my_student_id):
    global credsum
    # 查詢目前課表內學分數
    query = "SELECT sum(Credits) FROM (SELECT distinct Class_id,Credits FROM registered NATURAL JOIN course WHERE registered.student_id = '{}')AS a;".format(
        my_student_id)
    # 執行查詢
    cursor = conn.cursor()
    cursor.execute(query)
    # 計算課程的學分數
    credsum = cursor.fetchall()


def concern(my_student_id, class_id):  # 關注課程
    query = "insert into concerned VALUES('{}',{})".format(my_student_id, class_id)
    cursor = conn.cursor()
    cursor.execute(query)
    conn.commit()


def init_flag():
    global flag_action,flag_index,flag_redirect

    flag_index = True
    flag_action = True
    flag_redirect = True


def del_concern(my_student_id, class_id):  # 退關注
    query = "DELETE FROM concerned WHERE Student_ID='{}' AND Class_id = {};".format(my_student_id, class_id)
    cursor = conn.cursor()
    cursor.execute(query)
    conn.commit()


app = Flask(__name__)

conn = db_link.MySQLConnector
clear_registered()  # 清除課表中所有內容
registered_M()  # 將必修課加入課表中
my_student_id = 'D0XXXXXX'
flag_index = True
flag_action = True
flag_redirect = True
credsum = 0
my_student_name = 'XXX'
my_student_class = 'XXXX'


# 帳號及mysql部分還需修改
@app.route('/')
def signin():
    init_flag()
    start = """
        <html>
        <title>選課系統</title>
        <body>
        <h1>登入</h1>
        <form method="post" name="information" onsubmit="return checkusername();" action="/index">
            <label>學號：</label>
            <input name="username"><br><br>
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


@app.route('/index', methods=['GET', 'POST'])
def index():
    global my_student_id, flag_index, my_student_name, my_student_class
    cn = {'一': 1, '二': 2, '三': 3, '四': 4, '五': 5, '六': 6, '七': 7}  # 用字典將星期數從中文數字轉為阿拉伯數字
    if (flag_index):
        my_student_id = request.form.get("username")
        flag_index = False

    # 呼叫計算學分數函式
    count_total_credits(my_student_id)
    global my_class,my_department,my_class_name,flag_action
    # 取得輸入的文字
    if(flag_action or request.form.get("my_class")=='' or request.form.get("my_department") == '' or request.form.get("my_name") == ''):
        my_class = request.form.get("my_class")
        my_department = request.form.get("my_department")
        my_class_name = request.form.get("my_name")
        flag_action = False
    else:
        my_class = my_class
        my_department = my_department
        my_class_name = my_class_name

    if(flag_redirect):
        query="SELECT student_name,class FROM student WHERE student_id='{}'".format(my_student_id)
        cursor = conn.cursor()
        cursor.execute(query)
        infres=cursor.fetchall()
        my_student_name=infres[0][0]
        my_student_class=infres[0][1]

    # 取消關注清單
    form = """
        <html>
        <title>選課系統</title>
        <body>
        <h1>選課系統</h1>
        <form method="post" action="/index" >
        <label>系所：</label>
            <select name="my_department">
                <option value="">全部</option>
                <option>企業管理學系</option>
                <option>通識</option>
                <option>資訊工程學系</option>
            </select>
        <label>班級：</label>
            <select name="my_class">
                    <option value="">全部</option>
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
        <label>課程名稱：</label>
            <input name="my_name">
            <button name="搜尋">搜尋</button><br>
        </form>
        <p><a href="/">重新登入</a></p>
        <label>班級：{}</label><br>
        <label>使用者：{}</label><br>
        <label>學號：{}</label><br>
        <label>總學分：{}</label>
        <form method="post" action="/action">
            <button name="去選課">去選課!</button><br>
        </form>
    """.format(my_student_class, my_student_name, my_student_id, credsum[0][0])

    #關注清單
    query = "SELECT DISTINCT * FROM concerned NATURAL JOIN course WHERE concerned.student_id='{}' GROUP BY class_id;".format(my_student_id)

    # 執行查詢
    cursor = conn.cursor()
    cursor.execute(query)
    concern_list_result=cursor.fetchall()

    form += """
        <h1>取消關注清單</h1>
        <button onclick="hideandshow(coninf)">收起取消關注清單</button>
        <div id="concern_table">
        <table border="1" style="width:100%">
            <tr>
                <th align='center' valign="middle">取消關注</th>
                <th align='center' valign="middle">開課班級</th>
                <th align='center' valign="middle">課程名稱</th>
                <th align='center' valign="middle">時間</th>
                <th align='center' valign="middle">課程代碼</th>
                <th align='center' valign="middle">學分</th>
                <th align='center' valign="middle">必選修</th>
                <th align='center' valign="middle">系所</th>
                <th align='center' valign="middle">實收名額/開放名額</th>
                <th align='center' valign="middle">教師</th>
            </tr>
    """
    # 取得並列出所有查詢結果
    for (d1, d2, d3, d4, d5, d6, d7, d8, d9, d10) in concern_list_result:
        class_time=""
        query="SELECT * FROM time WHERE class_id='{}'".format(d1)
        cursor = conn.cursor()
        cursor.execute(query)
        for (t1,t2,t3) in cursor.fetchall():
            class_time+=" ({}) ".format(t2)
            class_time+=str(t3)
        form += """
            <tr>
            <form method="post" action="/quit_concern">
                <td align='center' valign="middle"><button name="my_class_id" value={} onclick="/quit_concern">取消關注</button></td>
            </form>
                <td align='center' valign="middle">{}</td>
                <td align='center' valign="middle">{}</td>
                <td align='center' valign="middle">{}</td>
                <td align='center' valign="middle">{}</td>
                <td align='center' valign="middle">{}</td>
                <td align='center' valign="middle">{}</td>
                <td align='center' valign="middle">{}</td>
                <td align='center' valign="middle">{}/{}</td>
                <td align='center' valign="middle">{}</td>
            </tr>
        """.format(d1, d3, d4, class_time, d1, d5, d6, d7, d9, d8, d10)

    form += """
        </table>
        </div>
    """

    #關注清單
    query = "SELECT * FROM course where class_name LIKE '%{}%' and class LIKE '%{}%' AND department LIKE '%{}%' and Class_ID not in (SELECT Class_id FROM registered WHERE Student_ID = '{}') and Class_ID not in (SELECT Class_id FROM concerned WHERE Student_ID = '{}')".format(my_class_name, my_class, my_department, my_student_id, my_student_id)

    # 執行查詢
    cursor = conn.cursor()
    cursor.execute(query)
    register_list_result=cursor.fetchall()

    form += """
        <h1>關注清單</h1>
        <button onclick="hideandshow(reinf)">收起關注清單</button>
        <div id="registered_table">
        <table border="1" style="width:100%">
            <tr>
                <th align='center' valign="middle">關注</th>
                <th align='center' valign="middle">開課班級</th>
                <th align='center' valign="middle">課程名稱</th>
                <th align='center' valign="middle">時間</th>
                <th align='center' valign="middle">課程代碼</th>
                <th align='center' valign="middle">學分</th>
                <th align='center' valign="middle">必選修</th>
                <th align='center' valign="middle">系所</th>
                <th align='center' valign="middle">實收名額/開放名額</th>
                <th align='center' valign="middle">教師</th>
            </tr>
    """
    # 取得並列出所有查詢結果
    for (d1, d2, d3, d4, d5, d6, d7, d8, d9) in register_list_result:
        class_time=""
        query="SELECT * FROM time WHERE class_id='{}'".format(d3)
        cursor = conn.cursor()
        cursor.execute(query)
        for (t1,t2,t3) in cursor.fetchall():
            class_time+=" ({}) ".format(t2)
            class_time+=str(t3)
        form += """
            <tr>
            <form method="post" action="/concern">
                <td align='center' valign="middle"><button name="my_class_id" value={} onclick="/concern">關注</button></td>
            </form>
                <td align='center' valign="middle">{}</td>
                <td align='center' valign="middle">{}</td>
                <td align='center' valign="middle">{}</td>
                <td align='center' valign="middle">{}</td>
                <td align='center' valign="middle">{}</td>
                <td align='center' valign="middle">{}</td>
                <td align='center' valign="middle">{}</td>
                <td align='center' valign="middle">{}/{}</td>
                <td align='center' valign="middle">{}</td>
            </tr>
        """.format(d3, d1, d2,class_time, d3, d4, d5, d6, d8, d7, d9)

    form += """
        </table>
        </div>
    """

    # 使用者的關注課表
    form += """
        <h1>關注課表</h1>
        <button onclick="hideandshow(concernedinf)">收起關注課表</button>
        <div id="concerned_table">
        <table border="2">
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
    # 找出使用者的必修課的學號、課程代碼、課程名稱、星期數、節次，主要用來查詢課程的時間
    query = "SELECT DISTINCT concerned.student_id,concerned.class_id,course.class_name,time.day,time.sessions,course.credits FROM course,time,concerned WHERE course.class_id=time.class_id AND concerned.class_id=course.class_id AND concerned.student_id = '{}';".format(
        my_student_id)
    cursor = conn.cursor()
    cursor.execute(query)
    fetchresult = cursor.fetchall()
    classcounter = 0

    # 比對星期數和節次將課程名稱填進去課表
    for i in range(1, 15):
        form += "<tr>"
        form += "<th align='center' valign='middle'>{}</th>".format(i)
        for j in range(1, 8):
            classcounter = 0
            form += "<td align='center' valign='middle'>"
            for (r1, r2, r3, r4, r5, r6) in fetchresult:
                if i == r5 and j == cn[r4]:
                    if classcounter == 0:
                        form += "{}".format(r3)
                        classcounter += 1
                    else:
                        form += "<br>{}".format(r3)
                        classcounter += 1
            form += "</td>"
        form += "</tr>"

    form += """
        </table>
        </div>
    """

    form += """
        </body>
        <script>
            var reinf=document.getElementById("registered_table");
            var coninf=document.getElementById("concern_table");
            var concernedinf=document.getElementById("concerned_table");
            function hideandshow(inf){
                if(inf.style.display==="none"){
                    inf.style.display="block";
                }
                else{
                    inf.style.display="none";
                }
            }
        </script>
        </html> 
    """

    return form


@app.route('/action', methods=['GET', 'POST'])
def action():
    global my_class,my_department,my_class_name,flag_action
    cn = {'一': 1, '二': 2, '三': 3, '四': 4, '五': 5, '六': 6, '七': 7}  # 用字典將星期數從中文數字轉為阿拉伯數字

    # 取得輸入的文字
    if (flag_action or request.form.get("my_class") == '' or request.form.get(
            "my_department") == '' or request.form.get("my_name") == ''):
        my_class = request.form.get("my_class")
        my_department = request.form.get("my_department")
        my_class_name = request.form.get("my_name")
        flag_action = False
    else:
        my_class = my_class
        my_department = my_department
        my_class_name = my_class_name
    # 欲查詢的 query 指令

    count_total_credits(my_student_id)

    query = "SELECT DISTINCT * from registered NATURAL JOIN course WHERE registered.student_id='{}';".format(
        my_student_id)

    # 執行查詢
    cursor = conn.cursor()
    cursor.execute(query)
    withdraw_list_result = cursor.fetchall()

    # 目前找不到正確使用超連結回到上一頁的做法，只好換成按鈕，並使用回到歷史紀錄中的上一頁
    # 退選清單
    results = """
        <!DOCTYPE html>
        <html>
        <title>選課系統</title>
        <body>
        <label>班級：{}</label><br>
        <label>使用者：{}</label><br>
        <label>學號：{}</label><br>
        <label>總學分：{}</label>
        <form method="post" action="/index">
            <button name="返回搜尋">返回搜尋</button>
        </form>
    """.format(my_student_class, my_student_name, my_student_id, credsum[0][0])

    results += """
        <h1>退選清單</h1>
        <button onclick="hideandshow(wdinf)">收起退選清單</button>
        <div id="withdraw_table">
        <form name="unregister" method="post" action="withdraw_class">
            <input type="hidden" name="class_id">
        </form>
        <script>
            function submit_unregister(class_id, requirements) {
                var is_submit = true;
                if (requirements == 'M') {
                    is_submit = confirm("這是必修，確定要退？");
                }
                if (is_submit) {
                    var theForm = document.forms["unregister"]
                    theForm.class_id.value = class_id;
                    theForm.submit();
                }
            }
        </script>

        <table border="1" style="width:100%">
            <tr>
                <th align='center' valign="middle">開課班級</th>
                <th align='center' valign="middle">課程名稱</th>
                <th align='center' valign="middle">時間</th>
                <th align='center' valign="middle">課程代碼</th>
                <th align='center' valign="middle">學分</th>
                <th align='center' valign="middle">必選修</th>
                <th align='center' valign="middle">系所</th>
                <th align='center' valign="middle">實收名額/開放名額</th>
                <th align='center' valign="middle">教師</th>
                <th align='center' valign="middle">退選</th>
            </tr>
    """

    class_time = ""

    for (d1, d2, d3, d4, d5, d6, d7, d8, d9, d10) in withdraw_list_result:
        class_time = ""
        query = "SELECT * FROM time WHERE class_id='{}'".format(d1)
        cursor = conn.cursor()
        cursor.execute(query)
        for (t1, t2, t3) in cursor.fetchall():
            class_time += " ({}) ".format(t2)
            class_time += str(t3)
        results += """
            <tr>
                <td align='center' valign="middle">{}</td>
                <td align='center' valign="middle">{}</td>
                <td align='center' valign="middle">{}</td>
                <td align='center' valign="middle">{}</td>
                <td align='center' valign="middle">{}</td>
                <td align='center' valign="middle">{}</td>
                <td align='center' valign="middle">{}</td>
                <td align='center' valign="middle">{}/{}</td>
                <td align='center' valign="middle">{}</td>
                <td align='center' valign="middle"><button name="my_class_id" value={} onclick="submit_unregister({},'{}')">退選</button></td>
            </tr>
        """.format(d3, d4, class_time, d1, d5, d6, d7, d9, d8, d10, d1, d1, d6)

    results += """
        </table>
        </div>
    """

    query = "SELECT DISTINCT * FROM concerned NATURAL JOIN course WHERE concerned.student_id='{}' GROUP BY class_id;".format(my_student_id)

    # 執行查詢
    cursor = conn.cursor()
    cursor.execute(query)
    concern_list_result = cursor.fetchall()

    results += """
        <h1>加選清單</h1>
        <button onclick="hideandshow(coninf)">收起加選清單</button>
        <div id="concern_table">
        <table border="1" style="width:100%">
            <tr>
                <th align='center' valign="middle">開課班級</th>
                <th align='center' valign="middle">課程名稱</th>
                <th align='center' valign="middle">時間</th>
                <th align='center' valign="middle">課程代碼</th>
                <th align='center' valign="middle">學分</th>
                <th align='center' valign="middle">必選修</th>
                <th align='center' valign="middle">系所</th>
                <th align='center' valign="middle">實收名額/開放名額</th>
                <th align='center' valign="middle">教師</th>
                <th align='center' valign="middle">加選</th>
            </tr>
    """
    # 取得並列出所有查詢結果
    for (d1, d2, d3, d4, d5, d6, d7, d8, d9, d10) in concern_list_result:
        class_time = ""
        query = "SELECT * FROM time WHERE class_id='{}'".format(d1)
        cursor = conn.cursor()
        cursor.execute(query)
        for (t1, t2, t3) in cursor.fetchall():
            class_time += " ({}) ".format(t2)
            class_time += str(t3)
        results += """
            <tr>
                <td align='center' valign="middle">{}</td>
                <td align='center' valign="middle">{}</td>
                <td align='center' valign="middle">{}</td>
                <td align='center' valign="middle">{}</td>
                <td align='center' valign="middle">{}</td>
                <td align='center' valign="middle">{}</td>
                <td align='center' valign="middle">{}</td>
                <td align='center' valign="middle">{}/{}</td>
                <td align='center' valign="middle">{}</td>
            <form method="post" action="/register_class">
                <td align='center' valign="middle"><button name="my_class_id" value={} onclick="/register_class">加選</button></td>
            </form>
            </tr>
        """.format(d3, d4, class_time, d1, d5, d6, d7, d9, d8, d10, d1)

    results += """
        </table>
        </div>
    """

    # 使用者的必修課表
    results += """      
        <h1>已選課表</h1>
        <button onclick="hideandshow(registeredinf)">收起已選課表</button>
        <div id="registered_table">
        <table border="2">

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
    # 找出使用者的必修課的學號、課程代碼、課程名稱、星期數、節次，主要用來查詢課程的時間
    query = "SELECT DISTINCT registered.student_id,registered.class_id,course.class_name,time.day,time.sessions,course.credits FROM course,time,registered WHERE course.class_id=time.class_id AND registered.class_id=course.class_id AND registered.student_id = '{}';".format(
        my_student_id)
    cursor = conn.cursor()
    cursor.execute(query)
    fetchresult = cursor.fetchall()
    classcounter = 0


    # 比對星期數和節次將課程名稱填進去課表
    for i in range(1, 15):
        results += "<tr>"
        results += "<th align='center' valign='middle'>{}</th>".format(i)
        for j in range(1, 8):
            classcounter = 0
            results += "<td align='center' valign='middle'>"
            for (r1, r2, r3, r4, r5, r6) in fetchresult:
                if i == r5 and j == cn[r4]:
                    if classcounter == 0:
                        results += "{}".format(r3)
                        classcounter += 1
                    else:
                        results += "<br>{}".format(r3)
                        classcounter += 1
            results += "</td>"
        results += "</tr>"

    results += "</table></div><br>"

    results += """
        <script>
            var registeredinf=document.getElementById("registered_table");
            var wdinf=document.getElementById("withdraw_table");
            var coninf=document.getElementById("concern_table");
            function hideandshow(inf){
                if(inf.style.display==="none"){
                    inf.style.display="block";
                }
                else{
                    inf.style.display="none";
                }
            }
        </script>
        </body>
        </html>
    """
    return results


@app.route('/register_class', methods=['GET', 'POST'])
def register_class():
    class_id = request.form.get("my_class_id")
    if (check_register_quota(class_id)):
        rview = """
        <html>
        <title>選課系統</title>
        <body>
        <h1>加選失敗，人數已滿</h1>
        <form method="post" action="/action">
            <button name="返回課程清單">返回課程清單</button><br>
        </form>
        </body>
        </html>
    """
    elif (check_register_clash(my_student_id, class_id)):
        rview = """
        <html>
        <title>選課系統</title>
        <body>
        <h1>加選失敗，課程衝堂</h1>
        <form method="post" action="/action">
            <button name="返回課程清單">返回課程清單</button><br>
        </form>
        </body>
        </html>
    """
    elif (check_register_name(my_student_id, class_id)):
        rview = """
        <html>
        <title>選課系統</title>
        <body>
        <h1>加選失敗，已有相同課程在課表中</h1>
        <form method="post" action="/action">
            <button name="返回課程清單">返回課程清單</button><br>
        </form>
        </body>
        </html>
    """
    elif (check_register_credit(class_id)):
        rview = """
        <html>
        <title>選課系統</title>
        <body>
        <h1>加選失敗，學分已達上限</h1>
        <form method="post" action="/action">
            <button name="返回課程清單">返回課程清單</button><br>
        </form>
        </body>
        </html>
    """
    else:
        register(my_student_id, class_id)
        rview = """
        <html>
        <title>選課系統</title>
        <body>
        <h1>加選成功</h1>
        <form method="post" action="/action">
            <button name="返回課程清單">返回課程清單</button><br>
        </form>
        </body>
        </html>
    """
    return rview


@app.route('/withdraw_class', methods=['GET', 'POST'])
def withdraw_class():
    get_class_id = request.form.get("class_id")
    query = "select class_id from registered where class_id = '{}' and student_ID = '{}'".format(get_class_id,
                                                                                                 my_student_id)
    cursor = conn.cursor()
    cursor.execute(query)

    my_class_id = cursor.fetchall()[0][0]

    query_sum_of_class_credits = "select credits from course join registered on course.class_ID = registered.class_ID where student_ID = '{}' and registered.class_ID = '{}' group by credits".format(
        my_student_id, my_class_id)
    cursor.execute(query_sum_of_class_credits)
    my_class_credits = cursor.fetchall()[0][0]

    query_sum_my_credits = "select sum(credits) from course join registered on course.class_ID = registered.Class_ID where Student_ID = '{}';".format(
        my_student_id)
    cursor.execute(query_sum_my_credits)
    my_class_credits_sum = cursor.fetchall()[0][0]
    if my_class_id and int(my_class_credits_sum) - int(my_class_credits) >= 9:

        cursor.execute(
            "delete from registered where student_ID = '{}' and class_ID = '{}'".format(my_student_id, my_class_id))
        conn.commit()
        cursor.execute("update course set real_quota = real_quota-1 where class_ID = '{}';".format(get_class_id))
        conn.commit()
        success_view = """
                    <html>
                    <title>選課系統</title>
                    <body>
                    <form method="post" action="/action">
                        <button name="返回課程清單">返回課程清單</button><br>
                    </form>
                    <script>
                        alert('退選成功')
                    </script>
                    </body>
                    </html>
                """

        return success_view
    else:
        failed_view = """
                    <html>
                    <title>選課系統</title>
                    <body>
                    <form method="post" action="/action">
                        <button name="返回課程清單">返回課程清單</button><br>
                    </form>
                    <script>
                        alert('退選失敗')
                    </script>                 
                    </body>
                    </html>
                """
        return failed_view


@app.route('/concern', methods=['GET', 'POST'])
def concern_class():
    class_id = request.form.get("my_class_id")
    concern(my_student_id, class_id)
    view = """
        <html>
        <title>選課系統</title>
        <body>
        <h1>關注成功</h1>
        <form method="post" action="/index">
            <button name="返回搜尋">返回搜尋</button><br>
        </form>
        </body>
        </html>
    """
    return view


@app.route('/quit_concern', methods=['GET', 'POST'])
def quit_concern():
    class_id = request.form.get("my_class_id")
    del_concern(my_student_id, class_id)
    view = """
        <html>
        <title>選課系統</title>
        <body>
        <h1>取消關注成功</h1>
        <form method="post" action="/index">
            <button name="返回搜尋">返回搜尋</button><br>
        </form>
        </body>
        </html>
    """
    return view