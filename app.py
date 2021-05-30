from flask import Flask,render_template,escape,url_for,abort,jsonify,request,flash,redirect
from flask_sqlalchemy import SQLAlchemy
import os
import sys
import click

# WIN = sys.platform.startswith('win')
# if WIN:  # 如果是 Windows 系统，使用三个斜线
#     prefix = 'sqlite:///'
# else:  # 否则使用四个斜线
#     prefix = 'sqlite:////'

app = Flask(__name__)

# app.config['SQLALCHEMY_DATABASE_URI'] = prefix + os.path.join(app.root_path, 'data.db')
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:Ww15888706328@sh-cynosdbmysql-grp-04gwt8ts.sql.tencentcdb.com:29073/base_data'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # 关闭对模型修改的监控
app.config['SECRET_KEY'] = 'dev'

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

@app.route('/', methods=['GET','POST'])
def index():
	if request.method == 'POST':
		title = request.values.get('title')
		year = request.form.get('year')

		if not title or not year or len(year) > 4 or len(title) > 60:
			flash('Invaild input')
			return redirect(url_for('index'))

		movie = Movie(title=title,year=year)
		db.session.add(movie)
		db.session.commit()
		flash('Item created.')
		return redirect(url_for('index'))
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
@app.errorhandler(405)
def page_not_found(error):
	
	return render_template('404.html'), 404

@app.context_processor
def inject_user():
	user = User.query.get(1)
	return dict(user=user)

@app.route('/movie/edit/<int:movie_id>', methods=['GET','POST'])
def edit(movie_id):
	movie = Movie.query.get_or_404(movie_id)

	if request.method == 'POST':
		title = request.form['title']
		year = request.form['year']

		if not title or not year or len(year) != 4 or len(title) > 60:
			flash('Invaild input.')
			return redirect(url_for('edit', movie_id=movie_id))

		movie.title = title
		movie.year = year
		db.session.commit()
		flash('Item update.')
		return redirect(url_for('index'))

	return render_template('edit.html', movie=movie)

@app.route('/movie/delete/<int:movie_id>', methods=['POST'])
def delete(movie_id):
	movie = Movie.query.get_or_404(movie_id)

	db.session.delete(movie)
	db.session.commit()
	flash('Item delete.')

	return redirect(url_for('index'))