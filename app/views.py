# -*- coding:utf-8 -*-

"""
author:zcj
create:2017.11.23
fun:
"""

__author__ = 'zcj'

import os

from flask import render_template, g, redirect, url_for, make_response, request, jsonify
from werkzeug.utils import secure_filename

from app import app
from app import model


@app.before_request
def before_request():
    if not hasattr(g, 'db'):
        g.db = model.connect()


@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'db'):
        g.db.close()


@app.errorhandler(404)
def url_not_found(e):
    return render_template('result.html', title='错误', result='无此页面')


@app.route('/')
def index():
    return render_template('index.html', title='欢迎来到文件管理首页')


@app.route('/<file>')
def static_file(file):
    base_dir = os.path.dirname(__file__)
    try:
        with open(os.path.join(base_dir, file)) as f:
            resp = make_response(open(os.path.join(base_dir, file)).read())
            if file.endswith('json'):
                resp.headers['Content-type'] = 'application/json;charset=UTF-8'
            elif file.endswith('html'):
                resp.headers['Content-type'] = 'text/html;charset=UTF-8'
            return resp
    except IOError:
        return render_template('result.html', title='错误', result='文件未找到')


@app.route('/file_list')
def file_list():
    cursor = g.db.cursor()
    cursor.execute('SELECT * FROM files')
    files = cursor.fetchall()
    return render_template('file_list.html', title='所有文件列表', files=files)


@app.route('/download/<filename>')
def down_file(filename):
    base_dir = os.path.dirname(__file__)
    path = os.path.join(base_dir, 'static/files/', filename)
    try:
        with open(path) as f:
            return redirect(url_for('static', filename='files/' + filename))
    except IOError:
        return render_template('result.html', title='错误', result='文件下载地址错误')


@app.route('/upload')
def upload_file():
    result = {}
    result['code'] = 200
    result['status'] = 'OK'
    result['data'] = []
    files = request.files
    if files:
        for file in files:
            if file:
                filename = secure_filename(file.filename)
                result['data'].append(filename)
    return make_response(jsonify(result))
