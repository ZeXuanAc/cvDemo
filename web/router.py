# -*- coding:utf-8 -*-
from werkzeug.utils import secure_filename
from flask import Flask, render_template, jsonify, request
import time
import os
from detect.face_detect import FaceDetect
import base64
from configs import LOGGER
import json

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
    face_detect = FaceDetect(os.path.join(WEB_PATH, 'upload'), os.path.join(WEB_PATH, 'upload_flip'),
                             os.path.join(basedir, 'static', 'result'))
    if request.files:
        f = request.files['nettyFile'] if 'nettyFile' in request.files.keys() else None
        if f and allowed_file(f.filename):  # 判断是否是允许上传的文件类型
            f_name = secure_filename(f.filename)
            ext = f_name.rsplit('.', 1)  # 获取文件后缀
            unix_time = int(time.time())
            new_filename = ext[0] + '_' + str(unix_time) + '.' + ext[1]  # 修改了上传的文件名
            f.save(os.path.join(file_dir, new_filename))  # 保存文件到upload目录
            faces = face_detect.detectImg(new_filename)
            return jsonify(faces)
        else:
            return jsonify({"error_code": -2, "error_msg": "上传失败"})
    file_base64 = None
    # 保存文件扩展名 用户userid fileKey userip device
    log_dict = {}
    if request.form:
        for key in request.form.keys():
            if key == 'nettyFile':
                # 文件base64解码并且保存 其他参数日志打印
                f = request.form.get(key)
                file_base64 = base64.b64decode(f)
            else:
                log_dict[key] = request.form.get(key)
    # 从表单的file字段获取文件，myfile为该表单的name值
    LOGGER.info(log_dict)
    if file_base64 is not None:
        file_name = log_dict['fileKey'] + '_' + str(int(time.time())) + '.' + log_dict['fileType']
        with open(os.path.join(file_dir, file_name), 'wb') as f:
            f.write(file_base64)
            f.close()
        faces = face_detect.detectImg(file_name)
        z = log_dict.copy()
        z.update(faces)
        LOGGER.info("result:" + json.dumps(z))
        return jsonify(faces)
    else:
        return jsonify({"error_code": -1, "error_msg": "未获取到文件"})
