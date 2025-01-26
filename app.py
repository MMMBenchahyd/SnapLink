from flask import Flask ,render_template ,request ,redirect, session, Response, url_for, jsonify
from models.image import Image
from models.User import User
from db import db
from bson import ObjectId
import paypalrestsdk
from flask_mail import Mail, Message
import os
import base64


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

def error_response(message, status_code):
    """
    Returns a JSON error response with the given message and status code.
    """
    return jsonify({"error": message}), status_code


@app.route('/', methods=['GET'])
def index():
    if 'user_id' not in session:
        return redirect('/index')

    user = User.search_id(session['user_id'])
    if not user:
        return redirect('/index')
    # if not user.verified :
    #     return "Please verify your email.", 403
    else:
        images = Image.find_by_user(user.user_id)
    return render_template('gallery.html', images=images, user_is_authenticated=True, n_lgo=False)


@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')

    # check username or email already exists
    if User.find_by_username_or_email(username):
        return jsonify({"message": "Username already exists"}), 400
    if User.find_by_email(email):
        return jsonify({"message": "Email already exists"}), 400

    # create new user
    new_user = User(username=username, email=email)
    new_user.set_password(password)
    new_user.save()

    # send email verification
    token = new_user.generate_verification_token()
    msg = Message('Verify Your Email', sender='snap.link@yandex.com', recipients=[new_user.email])
    link = url_for('verify_email', token=token, _external=True)
    msg.body = f'Click the link to verify your email: {link}'
    mail.send(msg)

    return jsonify({"message": "User registered successfully. Please check your email to verify your account."}), 201


@app.route('/api/login', methods=['GET','POST'])
def login():
    data = request.get_json()
    identifier = data.get('username')
    password = data.get('password')

    user = User.find_by_username_or_email(identifier)
    if user and user.check_password(password):
        session['user_id'] = user.user_id
        return jsonify({"message": "Login successful", "user_id": user.user_id})
    else:
        return error_response("Invalid username/email or password", 401)


@app.route('/api/upload', methods=['POST', 'GET'])
def upload():
    if 'user_id' not in session:
        return error_response("Unauthorized", 401)

    user = User.search_id(session['user_id'])
    if not user:
        return error_response("User not found", 404)

    if request.method == 'POST':
        try:
            name_img = request.form.get('content', '')
            file_to_upload = request.files.get('file')

            if not file_to_upload or not file_to_upload.content_type.startswith('image/'):
                return error_response("Uploaded file is not an image", 400)

            file_data = file_to_upload.read()
            new_img = Image.creating_by_objectid(
                uploaded_by=user.user_id,
                filename=name_img,
                file_content=file_data
            )
            new_img.save()

            return jsonify({"message": "Image uploaded successfully"})
        except Exception as e:
            return error_response(f"Error uploading image: {e}", 500)

    else:
        images = Image.find_by_user(user.user_id)
        return jsonify({"images": [img.to_dict() for img in images]})


@app.route('/api/update/<string:img_id>', methods=['POST', 'GET'])
def update(img_id):
    # print("Session data:", session)  # Check session data
    if 'user_id' not in session:
        return error_response("Unauthorized", 401)

    user = User.search_id(session['user_id'])
    if not user:
        return error_response("User not found", 404)
    # if not user.verified:
    #     return error_response("Please verify your email", 403)

    img_update = Image.find_by_img_id(img_id)
    if not img_update:
        return error_response("Image not found", 404)

    data = request.get_json()
    new_filename = data.get('newname')
    if not new_filename:
        return error_response("New filename is required", 400)

    img_update.filename = new_filename
    img_update.save()

    return jsonify({"message": "Image updated successfully"})


@app.route('/api/delete/<string:id>', methods=['DELETE'])
def delete(id):

    if 'user_id' not in session:
        return {"error": "User not logged in"}, 401

    user = User.search_id(session['user_id'])
    if not user:
        return {"error": "User not found"}, 404

    # if not user.verified:
    #     return {"error": "Please verify your email"}, 403

    try:
        object_id = str(ObjectId(id))
        img_deleting = db.images.find_one({"img_id": object_id})
        if not img_deleting:
            return {"error": "Image not found"}, 404

        # Delete the image
        db.images.delete_one({"img_id": object_id})
        return {"message": "Image deleted successfully"}, 200
    except Exception as e:
        return {"error": f"There was an issue deleting this image: {e}"}, 500


@app.route('/api/retrieve/<string:img_id>', methods=['GET'])
def retrieve(img_id):
    try:
        img = Image.find_by_img_id(img_id)

        if not img or not img.file_content:
            return {"error": "Image not found"}, 404

        # Convert image content to base64 for JSON transmission
        image_base64 = base64.b64encode(img.file_content).decode('utf-8')

        return {
            "filename": img.filename,
            "content_type": "image/png",
            "image_data": image_base64
        }, 200
    except Exception as e:
        return {"error": f"There was an issue retrieving this image: {e}"}, 500


@app.route('/index', methods=['GET'])
def home_page():

    if 'user_id' not in session:
        return render_template('index.html', user_is_authenticated=False, n_lgo=False)

    user = User.search_id(session['user_id'])
    if not user:
        return render_template('index.html', user_is_authenticated=False, n_lgo=False)

    return render_template('index.html', user_is_authenticated=True, n_lgo=False)


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect('/index')


@app.route('/image/<string:img_id>', methods=['GET'])
def get_image(img_id):
    try:
        img = Image.find_by_img_id(img_id)
        if not img or not img.file_content:
            return "Image not found <a href=\"/login\" style=\"color: hsl(323, 100%, 50%);\">Click here</a>", 404

        return Response(img.file_content, mimetype='image/png')
    except Exception as e:
        return f"Error showing image: {e}", 500


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


@app.route('/verify_email/<token>')
def verify_email(token):
    email = User.verify_token(token)
    if email is None:
        return "Invalid or expired token. <a href=\"/index\" style=\"color: hsl(323, 100%, 50%);\">Click here</a>", 400

    user = User.find_by_email(email)
    if user:
        user.verified = True
        db.users.update_one({"user_id": user.user_id}, {"$set": {"verified": True}})
        return "Email verified successfully. <a href=\"/index\" style=\"color: hsl(323, 100%, 50%);\">Click here</a>"
    else:
        return "User not found.", 404


@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    email = User.verify_password_reset_token(token)
    if email is None:
        return "Invalid or expired token.", 400

    user = User.find_by_email(email)
    if not user:
        return "User not found. <a href=\"/index\" style=\"color: hsl(323, 100%, 50%);\">Click here</a>", 404

    if request.method == 'POST':
        new_password = request.form['new_password']
        user.set_password(new_password)
        db.users.update_one({"user_id": user.user_id}, {"$set": {"password_hash": user.password_hash}})
        return "Password reset successfully. <a href=\"/index\" style=\"color: hsl(323, 100%, 50%);\">Click here</a>"

    return render_template('reset_password.html', token=token)


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


@app.route('/contact')
def contact():
    if 'user_id' not in session:
        return render_template('contact.html', user_is_authenticated=False, n_lgo=False)

    user = User.search_id(session['user_id'])
    if not user:
        return render_template('contact.html', user_is_authenticated=False, n_lgo=False)
    return  render_template('contact.html', user_is_authenticated=True, n_lgo=True)


@app.route('/about')
def about():
    if 'user_id' not in session:
        return render_template('about.html', user_is_authenticated=False, n_lgo=False)

    user = User.search_id(session['user_id'])
    if not user:
        return render_template('about.html', user_is_authenticated=False, n_lgo=False)
    return  render_template('about.html', user_is_authenticated=True, n_lgo=True)


@app.route('/terms')
def terms():
    if 'user_id' not in session:
        return render_template('terms.html', user_is_authenticated=False, n_lgo=False)

    user = User.search_id(session['user_id'])
    if not user:
        return render_template('terms.html', user_is_authenticated=False, n_lgo=False)
    return  render_template('terms.html', user_is_authenticated=True, n_lgo=True)


@app.route('/privacy')
def privacy():
    if 'user_id' not in session:
        return render_template('privacy.html', user_is_authenticated=False, n_lgo=False)

    user = User.search_id(session['user_id'])
    if not user:
        return render_template('privacy.html', user_is_authenticated=False, n_lgo=False)
    return  render_template('privacy.html', user_is_authenticated=True, n_lgo=True)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
