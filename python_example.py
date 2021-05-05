#!/usr/bin/env python3
# coding=utf-8
# -*- coding: UTF-8 -*-
from flask import Flask, request    # AAAA
import MySQLdb

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
    #charset='utf8'用於可以輸出中文
    conn = MySQLdb.connect(host="127.0.0.1",
                           user="Jin",
                           passwd="st123456",
                           db="test",
                           charset='utf8')
    # 欲查詢的 query 指令
    query = "SELECT name,studentid FROM students where studentid LIKE '%{}%';".format(my_head)
    # 執行查詢
    cursor = conn.cursor()
    cursor.execute(query)

    results = """
    <p><a href="/">Back to Query Interface</a></p>
    """
    # 取得並列出所有查詢結果
    for (description,d2 ) in cursor.fetchall():
        results += "<p>{}:{}</p>".format(description,d2)
    return results


    #...........................................