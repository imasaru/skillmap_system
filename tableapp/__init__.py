from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object('tableapp.config')
app.secret_key = 'secretsecret'  # ここで secret_key を設定

db = SQLAlchemy(app)
from .models import skillmap  # 追加

import tableapp.views