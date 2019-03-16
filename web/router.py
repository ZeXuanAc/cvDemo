# -*- coding:utf-8 -*-
from werkzeug.utils import secure_filename
from flask import Flask, render_template, jsonify, request
import time
import os
from detect.detect_api import detect, array_get
from detect.face_detect import FaceDetect
from detect import detect_path

WEB_PATH = os.path.dirname(os.path.realpath(__file__))

app = Flask(__name__, template_folder='./templates')
UPLOAD_FOLDER = 'upload'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
basedir = os.path.abspath(os.path.dirname(__file__))
ALLOWED_EXTENSIONS = set(['txt', 'png', 'jpg', 'xls', 'JPG', 'PNG', 'xlsx', 'gif', 'GIF'])


# 用于判断文件后缀
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


# 用于测试上传，稍后用到
@app.route('/')
def upload_test():
    return render_template('index.html')


# 用于测试上传，稍后用到
@app.route('/array')
def array_test():
    aaa = array_get()
    return jsonify(aaa)


# 上传文件
@app.route('/api/upload', methods=['POST'])
def api_upload():
    print(basedir)
    file_dir = os.path.join(basedir, app.config['UPLOAD_FOLDER'])
    if not os.path.exists(file_dir):
        os.makedirs(file_dir)
    f = request.files['myfile']  # 从表单的file字段获取文件，myfile为该表单的name值
    if f and allowed_file(f.filename):  # 判断是否是允许上传的文件类型
        fname = secure_filename(f.filename)
        print(fname)
        ext = fname.rsplit('.', 1)[1]  # 获取文件后缀
        unix_time = int(time.time())
        new_filename = str(unix_time) + '.' + ext  # 修改了上传的文件名
        f.save(os.path.join(file_dir, new_filename))  # 保存文件到upload目录
        # token = base64.b64encode(new_filename)
        # print(token)
        faceDetect = FaceDetect(os.path.join(WEB_PATH, 'upload'), os.path.join(WEB_PATH, 'upload_flip'), "C:\\Users\\viruser.v-desktop\\Desktop\\123")
        faces = faceDetect.detectImg(new_filename)
        # detect(new_filename)
        return jsonify(faces)
    else:
        return jsonify({"errno": 1001, "errmsg": "上传失败"})
