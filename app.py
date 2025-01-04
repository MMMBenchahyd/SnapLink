from flask import Flask ,render_template ,request ,redirect, session, Response
from models.image import Image
from models.User import User
from db import db
from bson import ObjectId


app = Flask(__name__)
app.secret_key = "111"


@app.route('/', methods=['POST', 'GET'])
def index():
    if 'user_id' not in session:
        return redirect('/login')

    user = User.search_id(session['user_id'])
    if not user:
        return "User not found", 404

    if request.method == 'POST':
        try:
            name_img = request.form.get('content', '')
            file_to_uplode = request.files.get('file')

            if not file_to_uplode.content_type.startswith('image/'):
                return "Uploaded file is not an image", 400

            file_data = file_to_uplode.read()
            new_img = Image.creating_by_objectid(
                uploaded_by=user.user_id,
                filename=name_img,
                file_content=file_data
            )
            new_img.save()

            return redirect('/')
        except Exception as e:
            return f"Error to adding your image: {e}", 500

    else:
        images = Image.find_by_user(user.user_id)
        return render_template('index.html', images=images)


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


@app.route('/update/<string:id>', methods=['POST', 'GET'])
def update(id):
    try:
        img_update = Image.find_by_img_id(id)# search image by id
        if not img_update:
            return 'Image not found', 404
    except Exception as e:
        print(f"Error fetching image: {e}")
        return 'There was an issue retrieving this image', 500

    if request.method == 'POST':
        try:
            new_filename = request.form['newname']
            img_update.filename = new_filename
            img_update.save()
            return redirect('/')
        except Exception as e:
            print(f"Error updating image: {e}")
            return 'There was an issue updating this image', 500

    return render_template('update.html', image=img_update)


@app.route('/delete/<string:id>')
def delete(id):
    try:
        object_id = ObjectId(id)
        img_deleting = db.images.find_one({"_id": object_id})
        if not img_deleting:
            return "Image not found.", 404
        # Delete img
        db.images.delete_one({"_id": object_id})
        return redirect('/')
    except Exception as e:
        print(f"Error: {e}")
        return "There was an issue deleting this image.", 500
    

@app.route('/image/<string:img_id>', methods=['GET'])
def get_image(img_id):
    try:
        img = Image.find_by_img_id(img_id)
        if not img or not img.file_content:
            return "Image not found", 404

        return Response(img.file_content, mimetype='image/png')
    except Exception as e:
        return f"Error showing image: {e}", 500


if __name__ == "__main__":
    app.run(debug=True)
