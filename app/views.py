# -*- coding:utf-8 -*-

"""
author:zcj
create:2017.11.23
fun:
"""

__author__ = 'zcj'

import os

from flask import render_template, g, redirect, url_for, make_response, request, session, abort, flash
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
    return render_template('upload_file.html')


@app.route('/upload_process', methods=['POST'])
def process_upload():
    # 获取版本号和版本名
    v_code = request.form['v_code']
    v_name = request.form['v_name']
    print('the version code is %s, and version name is %s' % (v_code, v_name))
    base_dir = os.path.dirname(__file__)
    # 1、获取所有文件名及路径
    files = request.files.to_dict()
    if files:
        for k, v in files.items():
            file = v
            if file:
                filename = secure_filename(file.filename)
                path = os.path.join(base_dir, 'static', 'files', filename)
                print('the filename is %s, and the save path will be %s' % (filename, path))
                # todo 查询数据库，如果已经有了，则不需要在保存和插入到数据库
                # 2、保存文件
                file.save(path)
                # 3、插入数据库
                g.db.execute(
                    'INSERT INTO files (filename, path, size, url, version_code, version_name) VALUES (?,?,?,?,?,?)',
                    [filename, path, os.path.getsize(path), path, v_code, v_name])
    # 4、查询数据库，并返回页面
    cursor = g.db.execute('SELECT * FROM files')
    g.db.commit()
    file_list = cursor.fetchall()
    return render_template('file_list.html', tile='所有文件列表', files=file_list)
