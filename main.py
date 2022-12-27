from flask import Flask, render_template, request, redirect, url_for, session, abort
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shop.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    img = db.Column(db.Text, nullable=False)
    isActive = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f'Запись: {self.title}'


@app.route('/')
@app.route('/index')
def index():
    return render_template("index.html")


@app.route('/product')
def product():
    items = Item.query.order_by(Item.price).all()
    return render_template("product.html", data = items)


@app.route('/product/<int:id>')
def product_detail(id):
    item = Item.query.get(id)
    return render_template("product_detail.html", item = item)


@app.route('/product/<int:id>/del')
def product_delete(id):
    if 'userlogged' not in session:
        abort(401)
    if session['userlogged'] != '1':
        abort(401)
    item = Item.query.get_or_404(id)

    try:
        db.session.delete(item)
        db.session.commit()
        return redirect('/product')
    except:
        return "Получилась ошибка при удалении"


@app.route('/about')
def about():
    return render_template("about.html")


@app.route('/help')
def help():
    return render_template("help.html")

@app.route('/create', methods=['POST', 'GET'])
def create():
    if 'userlogged' not in session:
        abort(401)
    if 'userlogged' in session and session['userlogged'] != "1":
        abort(401)
    if request.method == "POST":
        title = request.form['title']
        price = request.form['price']
        img = request.form['img']

        item = Item(title=title, price=price, img = img)

        try:
            db.session.add(item)
            db.session.commit()
            return redirect('/product')
        except:
            return "Получилась ошибка"
    else:
        return render_template("create.html")


@app.route('/login', methods=['POST', 'GET'])
def login():
    if 'userlogged' in session:
        return redirect(url_for('profile', username=session['userlogged']))
    elif request.method == "POST":
        session['userlogged'] = request.form['username']
        session['userlogged_psw'] = request.form['psw']
        return redirect(url_for('profile', username=session['userlogged']))
    return render_template('login.html')


@app.route('/login/<username>')
def profile(username):
    if 'userlogged' not in session or session['userlogged'] != username:
        abort(401)
    if session['userlogged'] == '1' and session['userlogged_psw'] == '2':
        return render_template('loginadm.html')
    else:
        return render_template('loginuser.html', username=username)

@app.route('/login/<username>/exit')
def exit(username):
    session.clear()
    return redirect(url_for('login'))


if __name__ == "__main__":
    app.run(debug=True)
