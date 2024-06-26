from flask import Flask, render_template, redirect, request, flash, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import threading
import webview

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['SECRET_KEY'] = '62c916ce4320e85984d0db65'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)







class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    password = db.Column(db.String(50))
    authorized = db.Column(db.Boolean, default=0)

    def __repr__(self):
        return f"User: {self.name}, Password: {self.password}, Authorized: {self.authorized}"

class Tasks(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task = db.Column(db.String(150))
    for_day = db.Column(db.Integer)
    for_user = db.Column(db.Integer)

    def __repr__(self):
        return f"Task: {self.task}"

def create_db():
    with app.app_context():
        db.create_all()
        db.reflect()
    print("db created and reflected")

create_db()







@app.route('/login', methods = ['GET', 'POST'])
def login():
    if request.method == "POST":
        user = Users.query.filter_by(name = request.form.get("username")).first()
        if user.password == request.form.get("password"):
            user.authorized = 1
            db.session.commit()
            flash("You succesfully signed in!", "success")
            return redirect('tasks/0')
        else:
            flash("Incorrect username or password", "error")
    return render_template("login.html")

@app.route('/signup', methods = ['GET', 'POST'])
def signup():
    if request.method == "POST":
        user = Users(
                name = request.form.get("username"),
                password = request.form.get("password"),
                authorized = True
            )
        print("User succesfully created")
        db.session.add(user)
        db.session.commit()
        flash("You succesfully signed up!", "success")
        return redirect('tasks/0')
    else:
        return render_template("signup.html")

@app.route('/tasks/<int:id>', methods = ['GET', 'POST'])
def tasks(id):
    authorized_user = Users.query.filter_by(authorized=1).first()
    if request.method == "POST":
        add_task_name = request.form.get("add_task-name")
        task_to_add = Tasks(task=add_task_name, for_day=id, for_user=authorized_user.id)
        db.session.add(task_to_add)
        db.session.commit()
    date = datetime.now()
    days = ['Today']
    for day in range(6):
        date += timedelta(days=1)
        days.append(date.strftime("%d.%m"))
    days_num = range(len(days))
    tasks = Tasks.query.filter(Tasks.for_day==id, Users.authorized==1, Tasks.for_user==authorized_user.id).all()
    tasks_num = range(len(tasks))
    return render_template("tasks.html", tasks=tasks, tasks_num=tasks_num, days=days, days_num=days_num, id=id)

@app.route('/delete/<int:for_day>/<int:id>')
def delete(for_day, id):
    task_to_delete = Tasks.query.get(id)
    db.session.delete(task_to_delete)
    db.session.commit()
    return redirect(url_for("tasks", id=for_day))

@app.route('/logout')
def logout():
    user = Users.query.filter(Users.authorized==1).first()
    user.authorized = 0
    db.session.commit()
    return redirect(url_for("login"))







def run_flask_app():
    app.run(debug=True, threaded=True, use_reloader=False)

if __name__ == '__main__':
    t = threading.Thread(target=run_flask_app)
    t.daemon = True
    t.start()

    webview.create_window('Flask App Window', 'login', width=1500, height=800, min_size=(1000, 800), resizable=True)
    webview.start(http_server=True, http_port=5000)
