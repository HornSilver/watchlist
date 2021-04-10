from flask import Flask,render_template
from flask import escape,url_for,abort,jsonify
from flask_sqlalchemy import SQLAlchemy
import os
import sys
import click

WIN = sys.platform.startswith('win')
if WIN:  # 如果是 Windows 系统，使用三个斜线
    prefix = 'sqlite:///'
else:  # 否则使用四个斜线
    prefix = 'sqlite:////'

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = prefix + os.path.join(app.root_path, 'data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # 关闭对模型修改的监控

db = SQLAlchemy(app)

class User(db.Model):  # 表名将会是 user（自动生成，小写处理）
    id = db.Column(db.Integer, primary_key=True)  # 主键
    name = db.Column(db.String(20))  # 名字

class Movie(db.Model):  # 表名将会是 movie
    id = db.Column(db.Integer, primary_key=True)  # 主键
    title = db.Column(db.String(60))  # 电影标题
    year = db.Column(db.String(4))  # 电影年份

@app.cli.command()
@click.option('--drop', is_flag=True, help='Create after drop')
def initdb(drop):
	if drop:
		db.drop_all()
	db.create_all()
	click.echo('Initizlized database.')

@app.cli.command()
def forge():

	db.create_all()

	name = 'Horn Silver'
	movies = [
				{'title': 'My Neighbor Totoro', 'year': '1988'},
			    {'title': 'Dead Poets Society', 'year': '1989'},
			    {'title': 'A Perfect World', 'year': '1993'},
			    {'title': 'Leon', 'year': '1994'},
			    {'title': 'Mahjong', 'year': '1996'},
			    {'title': 'Swallowtail Butterfly', 'year': '1996'},
			    {'title': 'King of Comedy', 'year': '1999'},
			    {'title': 'Devils on the Doorstep', 'year': '1999'},
			    {'title': 'WALL-E', 'year': '2008'},
			    {'title': 'The Pork of Music', 'year': '2012'},
			]


	user = User(name=name)
	db.session.add(user)

	for movie in movies:
		m = Movie(title=movie['title'],year=movie['year'])
		db.session.add(m)
	db.session.commit()
	click.echo("Done!")

@app.route('/')
def index():
	moviedata = Movie.query.all()
	return render_template('index.html',movies=moviedata)

@app.route('/home')
def hello():
	return '<h1>Hello Totoro!</h1><img src="http://helloflask.com/totoro.gif">'

@app.route('/user/<name>')
def user_page(name):
	return 'User: %s ' % escape(name)

@app.route('/test')
def test_url_for():

	abort(404)
	return 12

@app.errorhandler(404)
def page_not_found(error):
	
	return render_template('404.html'), 404

@app.context_processor
def inject_user():
	user = User.query.get(2)
	return dict(user=user)