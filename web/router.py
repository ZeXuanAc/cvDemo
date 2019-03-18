# -*- coding:utf-8 -*-
from werkzeug.utils import secure_filename
from flask import Flask, render_template, jsonify, request
import time
import os
from detect.face_detect import FaceDetect

WEB_PATH = os.path.dirname(os.path.realpath(__file__))

app = Flask(__name__, template_folder='./templates', static_folder="./static", static_url_path="/image")
UPLOAD_FOLDER = 'upload'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
basedir = os.path.abspath(os.path.dirname(__file__))
ALLOWED_EXTENSIONS = {'png', 'jpg', 'JPG', 'PNG'}


# 用于判断文件后缀
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


# 用于测试上传，稍后用到
@app.route('/')
def upload_test():
    return render_template('index.html')


# 上传文件
@app.route('/api/upload', methods=['POST'])
def api_upload():
    file_dir = os.path.join(basedir, app.config['UPLOAD_FOLDER'])
    if not os.path.exists(file_dir):
        os.makedirs(file_dir)
    f = request.files['myfile']  # 从表单的file字段获取文件，myfile为该表单的name值
    if f and allowed_file(f.filename):  # 判断是否是允许上传的文件类型
        fname = secure_filename(f.filename)
        ext = fname.rsplit('.', 1)  # 获取文件后缀
        unix_time = int(time.time())
        new_filename = ext[0] + '_' + str(unix_time) + '.' + ext[1]  # 修改了上传的文件名
        f.save(os.path.join(file_dir, new_filename))  # 保存文件到upload目录
        faceDetect = FaceDetect(os.path.join(WEB_PATH, 'upload'), os.path.join(WEB_PATH, 'upload_flip'),
                                os.path.join(basedir, 'static', 'result'))
        faces = faceDetect.detectImg(new_filename)
        # detect(new_filename)
        return jsonify(faces)
    else:
        return jsonify({"errno": 1001, "errmsg": "上传失败"})
