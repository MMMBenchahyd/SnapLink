from flask import Flask ,render_template ,request ,redirect, session
from models.image import Image
from models.User import User


app = Flask(__name__)
app.secret_key = "111"


@app.route('/', methods=['POST', 'GET'])
def index():
    if 'user_id' not in session:
        return redirect('/login')
    else:
        user = User.search_id(session['user_id'])
        return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if User.find_by_username(username):
            return "Username already exists", 400


        new_user = User(username=username)
        new_user.set_password(password)
        new_user.save()

        return redirect('/login')

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.find_by_username(username)
        if user and user.check_password(password):
            # userid storing.
            session['user_id'] = user.user_id
            return redirect('/')
        else:
            return "Invalid username or password", 401

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect('/login')


if __name__ == "__main__":
    app.run(debug=True)
