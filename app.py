from flask import Flask ,render_template ,request ,redirect, session, Response, send_file, url_for
from models.image import Image
from models.User import User
from db import db
from bson import ObjectId
import paypalrestsdk
from io import BytesIO
from flask_mail import Mail, Message
import os


app = Flask(__name__)
app.secret_key = os.environ.get('SERCET_KEY')

server_name = os.environ.get('SERVER_NAME_YN')
mail_username = os.environ.get('MAIL_USERNAME_YN')
mail_password = os.environ.get('MAIL_PASSWORD_YN')

app.config['MAIL_SERVER'] = server_name
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = mail_username
app.config['MAIL_PASSWORD'] = mail_password

mail = Mail(app)

paypalrestsdk.configure({
    "mode": "sandbox",
    "client_id": os.environ.get('CLIENT_ID'),
    "client_secret": os.environ.get('CLIENT_SECRET')
})

@app.route('/', methods=['GET'])
def index():
    if 'user_id' not in session:
        return redirect('/index')

    user = User.search_id(session['user_id'])
    if not user:
        return "User not found <a href=\"/login\" style=\"color: hsl(323, 100%, 50%);\">Click here</a>", 404
    if not user.verified :
        return "Please verify your email.", 403
    else:
        images = Image.find_by_user(user.user_id)
        return render_template('gallery.html', images=images, user_is_authenticated=True)

@app.route('/send_verification_email', methods=['GET'])
def send_verification_email():
    if 'user_id' not in session:
        return redirect('/index')

    user = User.search_id(session['user_id'])
    if not user:
        return "User not found  <a href=\"/login\" style=\"color: hsl(323, 100%, 50%);\">Click here</a>", 404

    token = user.generate_verification_token()
    msg = Message('Verify Your Email', sender='snap.link@yandex.com', recipients=[user.email])
    link = url_for('verify_email', token=token, _external=True)
    msg.body = f'Click the link to verify your email: {link}'
    mail.send(msg)

    return "Verification email sent. Check your email"

@app.route('/verify_email/<token>')
def verify_email(token):
    email = User.verify_token(token)
    if email is None:
        return "Invalid or expired token. <a href=\"/login\" style=\"color: hsl(323, 100%, 50%);\">Click here</a>", 400

    user = User.find_by_email(email)
    if user:
        user.verified = True
        db.users.update_one({"user_id": user.user_id}, {"$set": {"verified": True}})
        return "Email verified successfully. <a href=\"/login\" style=\"color: hsl(323, 100%, 50%);\">Click here</a>"
    else:
        return "User not found.", 404

@app.route('/upload', methods=['POST', 'GET'])
def upload():
    if 'user_id' not in session:
        return redirect('/index')

    user = User.search_id(session['user_id'])
    if not user:
        return "User not found  <a href=\"/login\" style=\"color: hsl(323, 100%, 50%);\">Click here</a>", 404

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

            return redirect('/upload')
        except Exception as e:
            return f"Error to adding your image: {e}", 500

    else:
        images = Image.find_by_user(user.user_id)
        return render_template('upload.html', images=images, user_is_authenticated=True)

@app.route('/index')
def home_page():
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']

        if User.find_by_username_or_email(username) or User.find_by_email(email):
            return "Username or email already exists", 400

        new_user = User(username=username, email=email)
        new_user.set_password(password)
        new_user.save()

        #verify_email
        token = new_user.generate_verification_token()
        msg = Message('Verify Your Email', sender='snap.link@yandex.com', recipients=[new_user.email])
        link = url_for('verify_email', token=token, _external=True)
        msg.body = f'Click the link to verify your email: {link}'
        mail.send(msg)
        return redirect('/login')

    return render_template('register.html')

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        user = User.find_by_email(email)
        if user:
            token = user.generate_password_reset_token()
            msg = Message('Reset Your Password', sender='snap.link@yandex.com', recipients=[user.email])
            link = url_for('reset_password', token=token, _external=True)
            msg.body = f'Click the link to reset your password: {link}'
            mail.send(msg)
            return "Password reset email sent."
        else:
            return "Email not found.", 404

    return render_template('forgot_password.html')

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    email = User.verify_password_reset_token(token)
    if email is None:
        return "Invalid or expired token.", 400

    user = User.find_by_email(email)
    if not user:
        return "User not found. <a href=\"/login\" style=\"color: hsl(323, 100%, 50%);\">Click here</a>", 404

    if request.method == 'POST':
        new_password = request.form['new_password']
        user.set_password(new_password)
        db.users.update_one({"user_id": user.user_id}, {"$set": {"password_hash": user.password_hash}})
        return "Password reset successfully."

    return render_template('reset_password.html', token=token)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        identifier = request.form['username']
        password = request.form['password']

        user = User.find_by_username_or_email(identifier)
        if user and user.check_password(password):
            session['user_id'] = user.user_id
            return redirect('/upload')
        else:
            return "Invalid username/email or password", 401

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect('/index')


@app.route('/update/<string:id>', methods=['POST', 'GET'])
def update(id):
    if 'user_id' not in session:
        return redirect('/index')

    user = User.search_id(session['user_id'])
    if not user:
        return "User not found  <a href=\"/login\" style=\"color: hsl(323, 100%, 50%);\">Click here</a>", 404
    if not user.verified :
        return "Please verify your email.", 403
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


@app.route('/delete/<string:id>', methods=['GET'])
def delete(id):
    if 'user_id' not in session:
        return redirect('/index')

    user = User.search_id(session['user_id'])
    if not user:
        return "User not found  <a href=\"/login\" style=\"color: hsl(323, 100%, 50%);\">Click here</a>", 404
    if not user.verified :
        return "Please verify your email.", 403
    try:
        object_id = str(ObjectId(id))
        img_deleting = db.images.find_one({"img_id": object_id})
        if not img_deleting:
            return "Image not found.", 404
        # Delete img
        db.images.delete_one({"img_id": object_id})
        return redirect('/')
    except Exception as e:
        print(f"Error: {e}")
        return "There was an issue deleting this image.", 500
    

@app.route('/image/<string:img_id>', methods=['GET'])
def get_image(img_id):
    try:
        img = Image.find_by_img_id(img_id)
        if not img or not img.file_content:
            return "Image not found <a href=\"/login\" style=\"color: hsl(323, 100%, 50%);\">Click here</a>", 404

        return Response(img.file_content, mimetype='image/png')
    except Exception as e:
        return f"Error showing image: {e}", 500

@app.route('/pay', methods=['GET', 'POST'])
def pay():
    payment = paypalrestsdk.Payment({
        "intent": "sale",
        "payer": {
            "payment_method": "paypal"
        },
        "redirect_urls": {
            "return_url": url_for('payment_success', _external=True),
            "cancel_url": url_for('payment_cancel', _external=True)
        },
        "application_context": {
            "brand_name": "SnapLink",
        },
        "transactions": [{
            "item_list": {
                "items": [{
                    "name": "donate",
                    "price": "0.99",
                    "currency": "USD",
                    "quantity": 1
                }]
            },
            "amount": {
                "total": "0.99",
                "currency": "USD"
            },
            "description": "Thanks for donating."
        }]
    })

    if payment.create():
        for link in payment.links:
            if link.rel == "approval_url":
                return redirect(link.href)
    else:
        return f"Error: {payment.error}"

@app.route('/payment_success')
def payment_success():
    payment_id = request.args.get('paymentId')
    payer_id = request.args.get('PayerID')

    if not payment_id or not payer_id:
        return "no donating done !!!"

    payment = paypalrestsdk.Payment.find(payment_id)

    if payment.execute({"payer_id": payer_id}):
        return render_template('payment_success.html')
    else:
        return f"Payment failed: {payment.error}"

@app.route('/payment_cancel')
def payment_cancel():
    return  render_template('payment_cancel.html')


@app.route('/retrieve/<string:img_id>')
def retrieve(img_id):
    try:
        img = Image.find_by_img_id(img_id)

        if not img or not img.file_content:
            return "Image not found.", 404

        return send_file(
            BytesIO(img.file_content),
            as_attachment=True,
            download_name=f"{img.filename.split('.')[0]}.png"
        )
    except Exception as e:
        return f"Error retrieving image: {e}", 500
@app.route('/contact')
def contact():
    return  render_template('contact.html')

@app.route('/about')
def about():
    return  render_template('about.html')

@app.route('/terms')
def terms():
    return  render_template('terms.html')
@app.route('/privacy')
def privacy():
    return  render_template('privacy.html')

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
