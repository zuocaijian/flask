# -*- coding:utf-8 -*-

"""
author:zcj
create:2017.11.23
fun:
"""

__author__ = 'zcj'

import os

from flask import render_template, g, redirect, url_for, make_response, request, jsonify, session, abort, flash
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


@app.route('/user')
def show_user():
    cur = g.db.execute('SELECT name, password FROM user ORDER BY id DESC')
    users = [dict(name=row[0], password=row[1]) for row in cur.fetchall()]
    return render_template('show_users.html', users=users)


@app.route('/add_user', methods=['POST'])
def add_user():
    if not session.get('logged_in'):
        abort(401)
    g.db.execute('INSERT INTO user (name, password) VALUES (?, ?)', [request.form['name'], request.form['password']])
    g.db.commit()
    flash('New user was successfully posted')
    return redirect(url_for('show_entries'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['name'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('show_user'))
    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_user'))


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
    # result = {}
    # result['code'] = 200
    # result['status'] = 'OK'
    # result['data'] = []
    # files = request.files
    # if files:
    #     for file in files:
    #         if file:
    #             filename = secure_filename(file.filename)
    #             result['data'].append(filename)
    # return make_response(jsonify(result))
    return render_template('upload_file.html')
