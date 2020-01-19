from flask import Flask
from config import Config
from flask_bootstrap import Bootstrap
import psycopg2


app = Flask(__name__)
app.config.from_object(Config)
conn = psycopg2.connect(dbname='d55phjpp7el6ol', user='xefhnkrqillfyn', password='1db4836e42b33efc28281222afd035a86e5aa977697b7a15624a1cf9d8813f06', host='ec2-54-217-225-16.eu-west-1.compute.amazonaws.com')
bootstrap = Bootstrap(app)


from my_app import routes
