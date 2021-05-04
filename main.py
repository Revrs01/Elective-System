from flask import Flask, request  # import flask app into program
import mysql.connector

app = Flask(__name__)


@app.route('/')
def index():
    form = """
    <form method="post" action="/action" >
        文字輸出欄位：<input name="my_head">
        <input type="submit" value="送出">
    </form>
    """
    return form


@app.route('/action', methods=['POST'])
def action():
    # 取得輸入的文字
    my_head = request.form.get("my_head")
    # 建立資料庫連線
    conn = mysql.connector.connect(host="127.0.0.1",
                                   user="revrs01",
                                   passwd="1234",
                                   db="test",
                                   auth_plugin='mysql_native_password')
    # 欲查詢的 query 指令
    query = "SELECT Name FROM students where name LIKE '{}%';".format(
        my_head)
    # 執行查詢
    cursor = conn.cursor()
    cursor.execute(query)

    results = """
    <p><a href="/">Back to Query Interface</a></p>
    """
    # 取得並列出所有查詢結果
    for (description,) in cursor.fetchall():
        results += "<p>{}</p>".format(description)
    return results
