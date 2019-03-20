# -*- coding:utf-8 -*-
from web.router import app
app.config['JSON_AS_ASCII'] = False
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
