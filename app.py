from flask import Flask ,render_template ,request ,redirect, session, Response, send_file
from models.image import Image
from models.User import User
from db import db
from bson import ObjectId
import paypalrestsdk
from io import BytesIO


app = Flask(__name__)
app.secret_key = "111"

paypalrestsdk.configure({
    "mode": "sandbox",
    "client_id": "AQorRJu7Scrg_QGT1jcX4JSiWl2-PEH1DPnWpA8C1vNublhXlHsr3GUzIMsEsXS0JzycOTnVtxvenwcL",
    "client_secret": "EKtRS0pNR57bF_d_wiblVJdoo0eJYZdOu5u1tGxOhqP2HvZ2gBxEA0YRVAZ_Ha1ZFbICqyRK8aICEh1b"
})

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
        email = request.form['email']

        if User.find_by_username_or_email(username) or User.find_by_email(email):
            return "Username or email already exists", 400

        new_user = User(username=username, email=email)
        new_user.set_password(password)
        new_user.save()
        return redirect('/login')

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        identifier = request.form['username']
        password = request.form['password']

        user = User.find_by_username_or_email(identifier)
        if user and user.check_password(password):
            session['user_id'] = user.user_id
            return redirect('/')
        else:
            return "Invalid username/email or password", 401

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
        return "Payment successful!"
    else:
        return f"Payment failed: {payment.error}"

@app.route('/payment_cancel')
def payment_cancel():
    return "Payment canceled."


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


if __name__ == "__main__":
    app.run(debug=True)
