from flask import Flask, render_template, request, session, redirect, url_for, send_from_directory, make_response
from models import db, HeroSection, Product, ContactMessage, Review, User, Highlight
import os
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
from urllib.parse import quote_plus
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
from email_service import send_email

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

UPLOAD_FOLDER = "static/uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///file.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False



db.init_app(app)


@app.route("/")
def hello_world():
    hero = HeroSection.query.first()
    return render_template(
    "home.html",
    hero=hero,
    seo_title="Sehatra - Health & Wellness Products",
    seo_description="Premium skincare, haircare and wellness products.",
    seo_keywords="skincare, haircare, wellness, sehatra"
)



@app.route("/product")
def products():
    category = request.args.get("category", "all")

    query = Product.query

    if category == "all":
        products = query.all()
    elif category in ["face", "hair", "body"]:
        products = query.filter_by(category=category).all()
    elif category == "new":
        one_week_ago = datetime.utcnow() - timedelta(days=7)
        products = query.filter(Product.created_at >= one_week_ago).all()
    else:
        products = []

    return render_template("product.html", products=products, datetime=datetime, timedelta=timedelta)


@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/contact", methods=["GET", "POST"])
def contact_page():
    if request.method == "POST":
        if "user_id" not in session:
            return redirect("/login")

        name = request.form["name"]
        gender = request.form["gender"]
        email = request.form["email"]
        phone = request.form["phone"]
        message = request.form["message"]

        new_msg = ContactMessage(
            name=name,
            gender=gender,
            email=email,
            phone=phone,
            message=message
        )
        db.session.add(new_msg)
        db.session.commit()

        html = f"""
        <h3>New Contact Message</h3>
        <p><b>Name:</b> {name}</p>
        <p><b>Gender:</b> {gender}</p>
        <p><b>Email:</b> {email}</p>
        <p><b>Phone:</b> {phone}</p>
        <p><b>Message:</b><br>{message}</p>
        """

        sent = send_email(
    subject="New Contact Message",
    to_email="admin@email.com",  # apna admin email
    html=html
)
        if not sent:
            return render_template("contact.html", error="Email service busy")

    return render_template("contact.html")




ADMIN_USERNAME = os.getenv("ADMIN_USERNAME")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")

@app.route("/admin_login", methods=["GET", "POST"])
def admin_login():
    error=None
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session["admin"] = True
            return render_template("admin_dashboard.html")
        else:
            error = "Wrong admin credentials, please try again!!"

    return render_template("admin_login.html", error=error)


@app.route("/admin_dashboard")
def admin_dashboard():
    if "admin" not in session:
        return redirect("/admin_login")

    return render_template("admin_dashboard.html")

@app.route("/edit_hero")
def edit_hero():
    if "admin" not in session:
        return redirect("/admin_login")
    
    hero = HeroSection.query.first()
    products = Product.query.all()
    return render_template("admin_edit_hero.html", hero=hero, products=products)


@app.route("/update_hero", methods=["POST"])
def update_hero():
    hero = HeroSection.query.first()
    hero.product_id = request.form.get("product_id")
    db.session.commit()

    # If user uploaded a file
    image_file = request.files.get("image_file")
    if image_file and image_file.filename != "":
        filename = secure_filename(image_file.filename)
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        image_file.save(file_path)
        hero.image_url = "/" + file_path  # Save local file path
    
    # If user entered a URL
    else:
        input_url = request.form.get("image_url")
        if input_url.strip() != "":
            hero.image_url = input_url
    
    # Update text fields
    hero.product_name = request.form.get("product_name")
    hero.product_desc = request.form.get("product_desc")
    hero.offer_text = request.form.get("offer_text")

    db.session.commit()
    return redirect("/")


@app.route("/terms")
def terms():
    return render_template("terms.html")

@app.route("/privacy")
def privacy():
    return render_template("privacy_policy.html")

@app.route("/refund")
def refund():
    return render_template("refund.html")


@app.route("/add_product", methods=["GET", "POST"])
def add_product():
    if request.method == "GET":
        return render_template("admin_product.html")

    name = request.form["name"]
    category = request.form["category"]
    price = request.form["price"]
    description = request.form.get("description")
    details = request.form.get("details")
    # refund_policy = request.form.get("refund_policy")
    # shipping_info = request.form.get("shipping_info")



    image_url = None

    # 1️⃣ If admin uploaded a file
    file = request.files.get("image_file")
    if file and file.filename != "":
        filename = secure_filename(file.filename)

        # path = static/uploads/filename.jpg
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename).replace("\\", "/")

        # Ensure folder exists
        if not os.path.exists(app.config["UPLOAD_FOLDER"]):
            os.makedirs(app.config["UPLOAD_FOLDER"])

        file.save(file_path)

        # for displaying in HTML we need a / prefix
        image_url = "/" + file_path

    # 2️⃣ If admin pasted a URL
    if not image_url:
        image_url = request.form["image_url"]

    # Save to DB
    product = Product(
        name=name,
        category=category,
        price=price,
        image_url=image_url,
        description=description,
        details=details,
        # refund_policy=refund_policy,
        # shipping_info=shipping_info
    )
    db.session.add(product)
    db.session.commit()

    return redirect("/manage_products")



@app.route("/manage_products")
def manage_products():
    products = Product.query.all()
    return render_template("manage_products.html", products=products)


@app.route("/delete_product/<int:id>")
def delete_product(id):
    product = Product.query.get(id)
    if product:
        db.session.delete(product)
        db.session.commit()
    return redirect("/manage_products")


@app.route("/edit_product/<int:id>", methods=["GET", "POST"])
def edit_product(id):
    product = Product.query.get(id)

    if request.method == "GET":
        return render_template("edit_product.html", product=product)

    product.name = request.form["name"]
    product.category = request.form["category"]
    product.price = request.form["price"]
    product.description = request.form["description"]
    product.details = request.form["details"]
    # product.refund_policy = request.form["refund_policy"]
    # product.shipping_info = request.form["shipping_info"]


    # File Upload
    file = request.files.get("image_file")
    if file and file.filename != "":
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename).replace("\\", "/")
        file.save(file_path)
        product.image_url = "/" + file_path
    else:
        product.image_url = request.form["image_url"]

    db.session.commit()
    return redirect("/manage_products")


@app.route("/contact_messages")
def contact_messages():
    if "admin" not in session:
        return redirect("/admin_login")

    messages = ContactMessage.query.order_by(ContactMessage.created_at.desc()).all()
    return render_template("contact_messages.html", messages=messages)


@app.route("/search")
def search_page():
    products = Product.query.all()   # sab products dikhane hain pahle
    return render_template("search.html", products=products)


@app.route("/product/<int:product_id>")
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)

    # WhatsApp link (default quantity 1, baad me JS se change karenge)
    base_number = "919970839647"  # +91 ke saath
    default_msg = f"Hi, I want to buy '{product.name}' (ID: {product.id}). Price: ₹{product.price}. Quantity: 1"
    wa_link = "https://wa.me/" + base_number + "?text=" + quote_plus(default_msg)

    share_url = request.url  # current page ka URL

    # reviews hum STEP 3 me add karenge, abhi empty list bhej do
    reviews = Review.query.filter_by(product_id=product.id)\
                      .order_by(Review.created_at.desc())\
                      .all()


    return render_template(
    "product_detail.html",
    product=product,
    seo_title=product.name,
    seo_description=product.description,
    reviews=reviews,
    seo_keywords=f"{product.category}, sehatra {product.name}"
)


@app.route("/product/<int:product_id>/review", methods=["POST"])
def add_review(product_id):
    product = Product.query.get_or_404(product_id)
    name = request.form["name"]
    rating = int(request.form["rating"])
    comment = request.form.get("comment", "")

    new_review = Review(
        product_id=product.id,
        name=name,
        rating=rating,
        comment=comment
    )
    db.session.add(new_review)
    db.session.commit()

    return redirect(url_for("product_detail", product_id=product.id))


@app.route("/add_review/<int:pid>", methods=["POST"])
def add_user_review(pid):
    if "user_id" not in session:
        return redirect("/login")


    user = User.query.get(session["user_id"])
    product = Product.query.get_or_404(pid)

    if user.is_blocked:
        return render_template("product_detail.html", product=product, alert_type="error", alert_msg="Dear User,\nYour account has been restricted due to repeated posting of spam or irrelevant content in the product review section.\nReviews are meant to help customers make informed decisions, and maintaining their authenticity is important to us.\nIf you believe this action was taken in error, you may contact our support team for review.\n- Team Sehatra")

    rating = request.form["rating"]
    review_text = request.form["review"]

    new_review = Review(
        user_id=user.id,
        product_id=pid,
        rating=rating,
        review_text=review_text
    )

    db.session.add(new_review)
    db.session.commit()

    return redirect(f"/product/{pid}")


@app.route("/delete_review/<int:id>")
def delete_review(id):
    if "admin" not in session:
        return redirect("/admin_login")

    r = Review.query.get(id)
    db.session.delete(r)
    db.session.commit()
    return redirect("/admin_reviews")


@app.route("/block_user/<int:uid>")
def block_user(uid):
    if "admin" not in session:
        return redirect("/admin_login")

    user = User.query.get(uid)
    user.is_blocked = True
    db.session.commit()
    return redirect("/admin_reviews")



@app.route("/unblock_user/<int:uid>")
def unblock_user(uid):
    if "admin" not in session:
        return redirect("/admin_login")

    user = User.query.get(uid)
    if user:
        user.is_blocked = False
        db.session.commit()

    return redirect("/blocked_users")


@app.route("/reply_review/<int:id>", methods=["POST"])
def reply_review(id):
    if "admin" not in session:
        return redirect("/admin_login")

    reply_text = request.form["reply"]
    review = Review.query.get(id)

    review.admin_reply = reply_text
    db.session.commit()

    return redirect("/admin_reviews")



@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "GET":
        return render_template("signup.html")

    name = request.form["name"]
    email = request.form["email"]
    phone = request.form["phone"]
    password = request.form["password"]

    if User.query.filter_by(email=email).first():
        return render_template("signup.html", error="Email already registered")

    if User.query.filter_by(phone=phone).first():
        return render_template("signup.html", error="Phone already registered")

    token = str(uuid.uuid4())

    user = User(
        name=name,
        email=email,
        phone=phone,
        password=generate_password_hash(password),
        verification_token=token,
        is_verified=False
    )

    db.session.add(user)
    db.session.commit()

    verify_link = request.host_url.rstrip("/") + "/verify/" + token

    html = f"""
    <h3>Verify Your Email</h3>
    <p>Click below to verify your account:</p>
    <a href="{verify_link}"
       style="padding:10px 15px;background:#ae3a00;color:white;
              text-decoration:none;border-radius:5px;">
       Verify Email
    </a>
    """

    sent = send_email(
    subject="Verify your email",
    to_email=email,
    html=html
)
    if not sent:
        return render_template("signup.html", error="Email service busy, try again")





@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    email = request.form["email"]
    password = request.form["password"]

    user = User.query.filter_by(email=email).first()

    if not user:
        return render_template("login.html", alert_type="error", alert_msg="User does not exist!")

    if not user.is_verified:
        return render_template(
            "login.html",
            alert_type="warning",
            alert_msg="Please verify your email first!",
            email=email
    )


    if not check_password_hash(user.password, password):
        return render_template("login.html", alert_type="error", alert_msg="Incorrect password!")

    # SUCCESS
    session["user_id"] = user.id
    session["user_name"] = user.name
    session["user_email"] = user.email
    session["user_phone"] = user.phone

    return redirect("/")




@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")



@app.route("/verify/<token>")
def verify_email(token):
    user = User.query.filter_by(verification_token=token).first()

    if not user:
        return render_template("verify_failed.html")

    user.is_verified = True
    user.verification_token = None
    db.session.commit()

    return render_template("verify_success.html")



@app.route("/forgot_password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "GET":
        return render_template("forgot.html")

    email = request.form["email"]
    user = User.query.filter_by(email=email).first()

    if not user:
        return render_template("forgot.html", error="Email not registered!")

    token = str(uuid.uuid4())
    user.reset_token = token
    user.reset_token_expiry = datetime.utcnow() + timedelta(minutes=30)
    db.session.commit()

    reset_link = request.host_url.rstrip("/") + "/reset_password/" + token

    html = f"""
    <h3>Password Reset</h3>
    <p>Click below to reset your password:</p>
    <a href="{reset_link}"
       style="padding:10px 15px;background:#ae3a00;color:white;
              text-decoration:none;border-radius:5px;">
       Reset Password
    </a>
    <p><small>Valid for 30 minutes</small></p>
    """

    sent = send_email(
    subject="Reset Password",
    to_email=email,
    html=f"<a href='{reset_link}'>Reset</a>"
)


    if not sent:
        return render_template(
            "forgot.html",
            error="Email service busy. Please try again later."
        )

    return render_template(
        "forgot.html",
        success="Password reset link sent! Check inbox/spam."
    )





@app.route("/reset_password/<token>", methods=["GET", "POST"])
def reset_password(token):
    user = User.query.filter_by(reset_token=token).first()

    if not user:
        return "Invalid reset link!"

    # Check expiry
    if user.reset_token_expiry < datetime.utcnow():
        return "Reset link expired! Please try again."

    if request.method == "POST":
        new_pass = request.form["password"]
        user.password = generate_password_hash(new_pass)
        user.reset_token = None
        user.reset_token_expiry = None

        db.session.commit()
        return render_template("reset_success.html")

    return render_template("reset.html", token=token)




@app.route("/admin_reviews")
def admin_reviews():
    if "admin" not in session:
        return redirect("/admin_login")

    reviews = Review.query.order_by(Review.created_at.desc()).all()
    return render_template("admin_reviews.html", reviews=reviews)


@app.route("/blocked_users")
def blocked_users():
    if "admin" not in session:
        return redirect("/admin_login")

    users = User.query.filter_by(is_blocked=True).all()

    return render_template("blocked_users.html", users=users)


@app.route("/profile")
def profile():
    if "user_id" not in session:
        return redirect("/login")

    user = User.query.get(session["user_id"])
    return render_template("profile.html", user=user)


@app.route("/profile/edit", methods=["GET", "POST"])
def edit_profile():
    if "user_id" not in session:
        return redirect("/login")

    user = User.query.get(session["user_id"])

    if request.method == "POST":
        user.name = request.form["name"]
        user.phone = request.form["phone"]

        # PROFILE PHOTO UPDATE
        file = request.files.get("profile_pic")
        if file and file.filename != "":
            filename = secure_filename(file.filename)
            path = "static/profile/" + filename

            # ensure folder exists
            os.makedirs("static/profile", exist_ok=True)

            file.save(path)
            user.profile_pic = "/" + path

            # Update session pic
            session["profile_pic"] = user.profile_pic

        # UPDATE PASSWORD (only if entered)
        new_pass = request.form.get("password", "").strip()
        if new_pass:
            user.password = generate_password_hash(new_pass)

        db.session.commit()
        return redirect("/")

    # Make sure profile pic in session for navbar
    if user.profile_pic:
        session["profile_pic"] = user.profile_pic

    return render_template("edit_profile.html", user=user)


@app.route("/sitemap.xml", methods=["GET"])
def sitemap():
    pages = []

    # STATIC PAGES
    static_urls = [
        ("/", "daily"),
        ("/product", "daily"),
        ("/about", "monthly"),
        ("/contact", "monthly"),
    ]

    for url, freq in static_urls:
        pages.append({
            "loc": request.host_url.strip("/") + url,
            "changefreq": freq,
            "priority": "0.8"
        })

    # DYNAMIC PRODUCT PAGES
    products = Product.query.all()
    for p in products:
        pages.append({
            "loc": request.host_url.strip("/") + f"/product/{p.id}",
            "changefreq": "weekly",
            "priority": "0.9"
        })

    # Render XML Manually
    sitemap_xml = render_template("sitemap_template.xml", pages=pages)
    response = make_response(sitemap_xml)
    response.headers["Content-Type"] = "application/xml"

    return response



@app.route('/robots.txt')
def robots():
    return send_from_directory('static', 'robots.txt')


# main.py

@app.route("/add-highlight", methods=["GET", "POST"])
def admin_add_highlight():
    if not session.get("admin"):
        return redirect("/admin_login")

    if request.method == "POST":
        video = request.files["video"]

        if not video:
            return "No video selected"

        filename = secure_filename(video.filename)
        path = os.path.join("static/uploads", filename)
        video.save(path)

        new_highlight = Highlight(video_file=filename)
        db.session.add(new_highlight)
        db.session.commit()

        return redirect("/manage-highlights")

    return render_template("admin_add_highlight.html")


@app.route("/manage-highlights")
def manage_highlights():
    if not session.get("admin"):
        return redirect("/admin_login")

    highlights = Highlight.query.order_by(Highlight.created_at.desc()).all()
    return render_template("manage_highlights.html", highlights=highlights)


@app.route("/admin/delete-highlight/<int:id>")
def delete_highlight(id):
    if not session.get("admin"):
        return redirect("/admin_login")

    highlight = Highlight.query.get_or_404(id)

    # delete file
    file_path = os.path.join("static/uploads", highlight.video_file)
    if os.path.exists(file_path):
        os.remove(file_path)

    db.session.delete(highlight)
    db.session.commit()

    return redirect("/manage-highlights")



@app.route("/highlight")
def highlight():
    highlights = Highlight.query.order_by(Highlight.created_at.desc()).all()
    return render_template("highlight.html", highlights=highlights)


@app.route("/resend-verification", methods=["POST"])
def resend_verification():
    email = request.form["email"]

    user = User.query.filter_by(email=email).first()
    if not user:
        return render_template(
            "login.html",
            alert_type="error",
            alert_msg="User not found!"
        )

    if user.is_verified:
        return redirect("/login")

    # New token
    token = str(uuid.uuid4())
    user.verification_token = token
    db.session.commit()

    verify_link = request.host_url.rstrip("/") + "/verify/" + token

    html = f"""
    <h3>Email Verification</h3>
    <p>Click below to verify your account:</p>
    <a href="{verify_link}"
       style="padding:10px 15px;background:#ae3a00;color:white;
              text-decoration:none;border-radius:5px;">
       Verify Email
    </a>
    """

    sent = send_email(
    subject="Verify Your Email - Sehatra",
    to_email=email,
    html=html
)


    if not sent:
        return render_template(
            "login.html",
            alert_type="error",
            alert_msg="Email service busy. Try again later."
        )

    return render_template(
        "login.html",
        alert_type="success",
        alert_msg="Verification email sent again! Check inbox/spam."
    )








with app.app_context():

        # Database tables create karo
        db.create_all()

        # Default hero section insert agar empty ho
        if HeroSection.query.first() is None:
            default_hero = HeroSection(
                image_url="https://static.wixstatic.com/media/c837a6_ce2611b99f714d55ac39dd982c0e2dc3~mv2.jpg/v1/crop/x_0,y_514,w_2688,h_1278/fill/w_1818,h_864,fp_0.50_0.50,q_85,usm_0.66_1.00_0.01,enc_avif,quality_auto/fold3_banner.jpg",
                product_name="Product name",
                product_desc="Product description",
                offer_text="free shipping on orders over $50"
            )
            db.session.add(default_hero)
            db.session.commit()


if __name__ == "__main__":
    app.run(debug=True)