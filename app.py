from flask import Flask, render_template, g, redirect, request
import sqlite3
import os
import logging
import sys
import uuid
from flask_login import UserMixin, LoginManager, login_required, login_user, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime

DATABASE = "flaskmemo.db"
app = Flask(__name__)
app.secret_key = os.urandom(24)

ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif'}
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024  # 2MB

ALLOWED_PREFECTURES = [
    '北海道', '青森県', '岩手県', '宮城県', '秋田県', '山形県', '福島県',
    '茨城県', '栃木県', '群馬県', '埼玉県', '千葉県', '東京都', '神奈川県',
    '新潟県', '富山県', '石川県', '福井県', '山梨県', '長野県',
    '岐阜県', '静岡県', '愛知県', '三重県',
    '滋賀県', '京都府', '大阪府', '兵庫県', '奈良県', '和歌山県',
    '鳥取県', '島根県', '岡山県', '広島県', '山口県',
    '徳島県', '香川県', '愛媛県', '高知県',
    '福岡県', '佐賀県', '長崎県', '熊本県', '大分県', '宮崎県', '鹿児島県', '沖縄県'
]

ALLOWED_FACILITY_TYPES = ['動物園', '水族館', 'その他']

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def valid_date(date_str):
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except (ValueError, TypeError):
        return False

logging.basicConfig(
    level=logging.INFO,
    stream=sys.stderr
)

login_manager = LoginManager()
login_manager.init_app(app)

class User(UserMixin):
    def __init__(self, user_id):
        self.id = user_id


@login_manager.user_loader
def load_user(user_id):
    db = get_db()
    user_data = db.execute(
        "select user_id from user where user_id=?",
        [user_id]
    ).fetchone()

    if user_data is None:
        return None

    return User(user_id)


@login_manager.unauthorized_handler
def unauthorized():
    return redirect('/login')


@app.route("/logout", methods=['POST'])
def logout():
    logout_user()
    return redirect('/login')


@app.route("/signup", methods=['GET', 'POST'])
def signup():
    error_message = ''
    user_id = ''

    if request.method == 'POST':
        user_id = request.form.get('user_id', '').strip()
        password = request.form.get('password', '')

        if not user_id:
            error_message = 'ユーザIDを入力してください'
            return render_template('signup.html', error_message=error_message, user_id=user_id)

        if not password:
            error_message = 'パスワードを入力してください'
            return render_template('signup.html', error_message=error_message, user_id=user_id)

        pass_hash = generate_password_hash(password)
        db = get_db()
        user_check = db.execute(
            "select user_id from user where user_id=?",
            [user_id]
        ).fetchone()

        if not user_check:
            db.execute(
                "insert into user (user_id, password) values(?, ?)",
                [user_id, pass_hash]
            )
            db.commit()
            return redirect('/login')
        else:
            error_message = '入力されたユーザIDはすでに登録されています'

    return render_template('signup.html', error_message=error_message, user_id=user_id)


@app.route("/login", methods=['GET', 'POST'])
def login():
    error_message = ''
    user_id = ''

    if request.method == 'POST':
        user_id = request.form.get('user_id', '').strip()
        password = request.form.get('password', '')

        if not user_id:
            error_message = 'ユーザIDを入力してください'
            return render_template('login.html', user_id=user_id, error_message=error_message)

        if not password:
            error_message = 'パスワードを入力してください'
            return render_template('login.html', user_id=user_id, error_message=error_message)

        user_data = get_db().execute(
            "select password from user where user_id=?",
            [user_id]
        ).fetchone()

        if user_data is not None and check_password_hash(user_data["password"], password):
            user = User(user_id)
            login_user(user)
            return redirect('/')

        error_message = '入力されたユーザIDもしくはパスワードが誤っています'

    return render_template('login.html', user_id=user_id, error_message=error_message)


@app.route("/")
@login_required
def top():
    db = get_db()

    memo_list = db.execute(
        """
        select id, facility_type, facility_name, prefecture, visit_date, favorite_animal, memo, photo_path
        from memo
        where user_id=?
        order by id desc
        limit 5
        """,
        [current_user.id]
    ).fetchall()

    prefecture_list = db.execute(
        """
        select prefecture, count(*) as count
        from memo
        where user_id=?
        group by prefecture
        order by prefecture
        """,
        [current_user.id]
    ).fetchall()

    achieved_count = len(prefecture_list)
    achievement_rate = round((achieved_count / 47) * 100, 1) if achieved_count > 0 else 0
    unvisited_count = 47 - achieved_count

    wish_list = db.execute(
        """
        select id, zoo_name, prefecture, memo, created_at
        from wish
        where user_id=?
        order by id desc
        limit 3
        """,
        [current_user.id]
    ).fetchall()

    hour = datetime.now().hour
    if 5 <= hour < 12:
        greeting = "おはようございます"
    elif 12 <= hour < 18:
        greeting = "こんにちは"
    else:
        greeting = "こんばんは"

    user_data = db.execute(
        """
        select name
        from user
        where user_id=?
        """,
        [current_user.id]
    ).fetchone()

    display_name = user_data["name"] if user_data and user_data["name"] else current_user.id

    return render_template(
        'index.html',
        memo_list=memo_list,
        prefecture_list=prefecture_list,
        achieved_count=achieved_count,
        achievement_rate=achievement_rate,
        unvisited_count=unvisited_count,
        wish_list=wish_list,
        greeting=greeting,
        display_name=display_name
    )


@app.route("/favorites")
@login_required
def favorites():
    favorite_list = get_db().execute(
        """
        select id, facility_type, facility_name, prefecture, visit_date, favorite_animal, memo, photo_path
        from memo
        where user_id=? and favorite_animal is not null and favorite_animal != ''
        order by id desc
        """,
        [current_user.id]
    ).fetchall()

    return render_template("favorites.html", favorite_list=favorite_list)


@app.route("/prefecture_detail")
@login_required
def prefecture_detail():
    prefecture_name = request.args.get('name')

    memo_list = get_db().execute(
        """
        select id, facility_type, facility_name, prefecture, visit_date, favorite_animal, memo, photo_path
        from memo
        where user_id=? and prefecture=?
        order by id desc
        """,
        [current_user.id, prefecture_name]
    ).fetchall()

    return render_template('prefecture_detail.html', prefecture_name=prefecture_name, memo_list=memo_list)


@app.route("/prefecture")
@login_required
def prefecture():
    sort = request.args.get('sort', 'name')
    db = get_db()

    if sort == 'count_desc':
        prefecture_list = db.execute(
            """
            select prefecture, count(*) as count
            from memo
            where user_id=?
            group by prefecture
            order by count(*) desc, prefecture asc
            """,
            [current_user.id]
        ).fetchall()
    elif sort == 'count_asc':
        prefecture_list = db.execute(
            """
            select prefecture, count(*) as count
            from memo
            where user_id=?
            group by prefecture
            order by count(*) asc, prefecture asc
            """,
            [current_user.id]
        ).fetchall()
    else:
        prefecture_list = db.execute(
            """
            select prefecture, count(*) as count
            from memo
            where user_id=?
            group by prefecture
            order by prefecture asc
            """,
            [current_user.id]
        ).fetchall()

    achieved_count = len(prefecture_list)
    achievement_rate = round((achieved_count / 47) * 100, 1) if achieved_count > 0 else 0

    return render_template(
        'prefecture.html',
        prefecture_list=prefecture_list,
        achieved_count=achieved_count,
        achievement_rate=achievement_rate,
        sort=sort
    )


@app.route("/wish/regist", methods=["GET", "POST"])
@login_required
def wish_regist():
    if request.method == "POST":
        zoo_name = request.form.get("zoo_name")
        prefecture = request.form.get("prefecture")
        memo = request.form.get("memo")
        db = get_db()
        db.execute(
            "insert into wish (user_id, zoo_name, prefecture, memo) values (?, ?, ?, ?)",
            [current_user.id, zoo_name, prefecture, memo]
        )
        db.commit()
        return redirect("/")

    return render_template("wish_regist.html")


@app.route("/<int:id>/edit", methods=['GET', 'POST'])
@login_required
def edit(id):
    db = get_db()
    post = db.execute(
        """
        select id, facility_type, facility_name, prefecture, visit_date, favorite_animal, memo, photo_path
        from memo
        where id=? and user_id=?
        """,
        [id, current_user.id]
    ).fetchone()

    if post is None:
        return redirect('/')

    if request.method == 'POST':
        facility_type = request.form.get('facility_type', '').strip()
        facility_name = request.form.get('facility_name', '').strip()
        prefecture = request.form.get('prefecture', '').strip()
        visit_date = request.form.get('visit_date', '').strip()
        favorite_animal = request.form.get('favorite_animal', '').strip()
        memo = request.form.get('memo', '').strip()
        photo = request.files.get('photo')
        photo_path = post['photo_path']

        if not facility_type or facility_type not in ALLOWED_FACILITY_TYPES:
            return render_template('edit.html', post=post, error_message='施設種別を正しく選択してください')

        if not facility_name:
            return render_template('edit.html', post=post, error_message='施設名を入力してください')

        if not prefecture or prefecture not in ALLOWED_PREFECTURES:
            return render_template('edit.html', post=post, error_message='都道府県を正しく選択してください')

        if not valid_date(visit_date):
            return render_template('edit.html', post=post, error_message='訪問日の形式が正しくありません')

        if photo and photo.filename != '':
            if not allowed_file(photo.filename):
                return render_template('edit.html', post=post, error_message='画像は jpg, jpeg, png, gif のみです')

            filename = secure_filename(photo.filename)
            upload_dir = os.path.join(app.root_path, 'static', 'uploads')
            os.makedirs(upload_dir, exist_ok=True)
            ext = filename.rsplit('.', 1)[1].lower()
            unique_name = f"{uuid.uuid4()}.{ext}"
            save_path = os.path.join(upload_dir, unique_name)
            photo.save(save_path)
            photo_path = '/static/uploads/' + unique_name

        db.execute(
            """
            update memo
            set facility_type=?, facility_name=?, prefecture=?, visit_date=?, favorite_animal=?, memo=?, photo_path=?
            where id=? and user_id=?
            """,
            [facility_type, facility_name, prefecture, visit_date, favorite_animal, memo, photo_path, id, current_user.id]
        )
        db.commit()
        return redirect('/')

    return render_template('edit.html', post=post)


@app.route("/<int:id>/delete", methods=['POST'])
@login_required
def delete(id):
    db = get_db()
    db.execute(
        "delete from memo where id=? and user_id=?",
        [id, current_user.id]
    )
    db.commit()
    return redirect('/')


@app.route("/wish")
@login_required
def wish():
    wish_list = get_db().execute(
        """
        select id, zoo_name, prefecture, memo, created_at
        from wish
        where user_id=?
        order by id desc
        """,
        [current_user.id]
    ).fetchall()

    return render_template("wish.html", wish_list=wish_list)


@app.route("/wish/<int:id>/delete", methods=["POST"])
@login_required
def wish_delete(id):
    db = get_db()
    db.execute(
        "delete from wish where id=? and user_id=?",
        [id, current_user.id]
    )
    db.commit()
    return redirect("/")


@app.route("/user")
@login_required
def user_page():
    db = get_db()

    user_data = db.execute(
        """
        select user_id, name, profile_memo, created_at
        from user
        where user_id=?
        """,
        [current_user.id]
    ).fetchone()

    memo_count = db.execute(
        """
        select count(*) as count
        from memo
        where user_id=?
        """,
        [current_user.id]
    ).fetchone()["count"]

    wish_count = db.execute(
        """
        select count(*) as count
        from wish
        where user_id=?
        """,
        [current_user.id]
    ).fetchone()["count"]

    favorite_count = db.execute(
        """
        select count(*) as count
        from memo
        where user_id=? and favorite_animal is not null and favorite_animal != ''
        """,
        [current_user.id]
    ).fetchone()["count"]

    prefecture_list = db.execute(
        """
        select prefecture, count(*) as count
        from memo
        where user_id=?
        group by prefecture
        """,
        [current_user.id]
    ).fetchall()

    achieved_count = len(prefecture_list)
    achievement_rate = round((achieved_count / 47) * 100, 1) if achieved_count > 0 else 0

    return render_template(
        "user.html",
        user_name=user_data["name"] if user_data and user_data["name"] else current_user.id,
        user_id=user_data["user_id"] if user_data else current_user.id,
        created_at=user_data["created_at"] if user_data else "",
        profile_memo=user_data["profile_memo"] if user_data and user_data["profile_memo"] else "",
        memo_count=memo_count,
        wish_count=wish_count,
        favorite_count=favorite_count,
        achieved_count=achieved_count,
        achievement_rate=achievement_rate
    )


@app.route("/user/update_name", methods=["POST"])
@login_required
def update_name():
    name = request.form.get("name", "").strip()

    if not name:
        return redirect("/user")

    db = get_db()
    db.execute(
        "update user set name=? where user_id=?",
        [name, current_user.id]
    )
    db.commit()
    return redirect("/user")


@app.route("/user/update_user_id", methods=["POST"])
@login_required
def update_user_id():
    new_user_id = request.form.get("user_id", "").strip()
    old_user_id = current_user.id

    if not new_user_id:
        return redirect("/user")

    db = get_db()
    check = db.execute(
        "select user_id from user where user_id=?",
        [new_user_id]
    ).fetchone()

    if check is None:
        db.execute(
            "update user set user_id=? where user_id=?",
            [new_user_id, old_user_id]
        )
        db.execute(
            "update memo set user_id=? where user_id=?",
            [new_user_id, old_user_id]
        )
        db.execute(
            "update wish set user_id=? where user_id=?",
            [new_user_id, old_user_id]
        )
        db.commit()
        login_user(User(new_user_id))

    return redirect("/user")


@app.route("/user/update_password", methods=["POST"])
@login_required
def update_password():
    current_password = request.form.get("current_password", "")
    new_password = request.form.get("new_password", "")

    if not current_password or not new_password:
        return redirect("/user")

    db = get_db()
    user_data = db.execute(
        "select password from user where user_id=?",
        [current_user.id]
    ).fetchone()

    if user_data is not None and check_password_hash(user_data["password"], current_password):
        new_hash = generate_password_hash(new_password)
        db.execute(
            "update user set password=? where user_id=?",
            [new_hash, current_user.id]
        )
        db.commit()

    return redirect("/user")


@app.route("/user/update_memo", methods=["POST"])
@login_required
def update_profile_memo():
    profile_memo = request.form.get("profile_memo")
    db = get_db()
    db.execute(
        "update user set profile_memo=? where user_id=?",
        [profile_memo, current_user.id]
    )
    db.commit()
    return redirect("/user")


@app.route("/regist", methods=["GET", "POST"])
@login_required
def regist():
    error_message = ''

    if request.method == "POST":
        facility_type = request.form.get("facility_type", "").strip()
        facility_name = request.form.get("facility_name", "").strip()
        prefecture = request.form.get("prefecture", "").strip()
        visit_date = request.form.get("visit_date", "").strip()
        favorite_animal = request.form.get("favorite_animal", "").strip()
        memo = request.form.get("memo", "").strip()
        photo = request.files.get("photo")
        photo_path = None

        if not facility_type or facility_type not in ALLOWED_FACILITY_TYPES:
            error_message = "施設種別を正しく選択してください"
            return render_template("regist.html", error_message=error_message)

        if not facility_name:
            error_message = "施設名を入力してください"
            return render_template("regist.html", error_message=error_message)

        if not prefecture or prefecture not in ALLOWED_PREFECTURES:
            error_message = "都道府県を正しく選択してください"
            return render_template("regist.html", error_message=error_message)

        if not valid_date(visit_date):
            error_message = "訪問日の形式が正しくありません"
            return render_template("regist.html", error_message=error_message)

        if photo and photo.filename != "":
            if not allowed_file(photo.filename):
                return render_template("regist.html", error_message="画像は jpg, jpeg, png, gif のみです")

            filename = secure_filename(photo.filename)
            ext = filename.rsplit('.', 1)[1].lower()
            upload_dir = os.path.join(app.root_path, "static", "uploads")
            os.makedirs(upload_dir, exist_ok=True)
            unique_name = f"{uuid.uuid4()}.{ext}"
            save_path = os.path.join(upload_dir, unique_name)
            photo.save(save_path)
            photo_path = "/static/uploads/" + unique_name

        db = get_db()
        db.execute(
            """
            insert into memo
            (user_id, facility_type, facility_name, prefecture, visit_date, favorite_animal, memo, photo_path)
            values (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [current_user.id, facility_type, facility_name, prefecture, visit_date, favorite_animal, memo, photo_path]
        )
        db.commit()
        return redirect("/")

    return render_template("regist.html", error_message=error_message)


def connect_db():
    rv = sqlite3.connect(DATABASE)
    rv.row_factory = sqlite3.Row
    return rv


def get_db():
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db


@app.teardown_appcontext
def close_db(exception):
    db = g.pop('sqlite_db', None)
    if db is not None:
        db.close()


if __name__ == "__main__":
    app.run()
