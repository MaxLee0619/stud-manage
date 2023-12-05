from flask import Flask, request, render_template, redirect, url_for
from pymongo import MongoClient
import datetime
from werkzeug.utils import secure_filename
import os

# connect to MongoDB
cluster = MongoClient("mongodb+srv://Max0922:Lmf20031027@cluster0.zd4ije3.mongodb.net/?retryWrites=true&w=majority")
db = cluster["Student"]
admin = db["Admin"]
collection = db["Student"]
taskdb = db["Task"]

app = Flask(__name__, static_url_path='/static')
UPLOAD_FOLDER = "static/images"
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get("username")
        password = request.form.get("password")

        user = admin.find_one({"username": username, "password": password})
        if user:
            return redirect(url_for("index"))
        else:
            return redirect(url_for("login"))
    return render_template("login.html")

@app.route('/index')
def index():
    students = collection.find()
    tasks = taskdb.find()
    return render_template("index.html", students=students, tasks=tasks)

@app.route('/add_student', methods=['GET', 'POST'])
def add_student():
    if request.method == 'POST':
        student_id = request.form.get("student-id")
        name = request.form.get("name")
        age = request.form.get("age")
        gender = request.form.get("gender")
        image = request.files['image'] if 'image' in request.files else None

        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            image.save(image_path)
        else:
            image_path = None  # Set to a default image path or handle accordingly

        active = True
        is_delete = False
        created = datetime.datetime.now()
        created_by = "admin"
        last_updated = datetime.datetime.now()
        updated_by = "admin"

        student_data = {
            "_id": student_id,
            "name": name,
            "age": age,
            "gender": gender,
            "image_path": image_path,  # Store the path to the uploaded image
            "active": active,
            "is_delete": is_delete,
            "created": created,
            "created_by": created_by,
            "last_updated": last_updated,
            "updated_by": updated_by
        }
        collection.insert_one(student_data)
        return redirect(url_for("index"))

    return render_template("add_student.html")

@app.route('/edit_student/<student_id>', methods=['GET', 'POST'])
def edit_student(student_id):
    student = collection.find_one({"_id": student_id})

    if request.method == 'POST':
        if request.method == 'POST':
        # Update the image_path if a new image is uploaded
            if 'image' in request.files:
                image = request.files['image']
                if image and allowed_file(image.filename):
                    filename = secure_filename(image.filename)
                    image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    image.save(image_path)
                    student['image_path'] = image_path

        if request.form.get("name") != "":
            student['name'] = request.form.get("name")
        if request.form.get("age") != "":
            student['age'] = request.form.get("age")
        if request.form.get("gender") != "":
            student['gender'] = request.form.get("gender")
        if request.form.get("active") != "":
            student['active'] = True if request.form.get("active") == "true" else False
        if request.form.get("is_delete") != "":
            student['is_delete'] = True if request.form.get("is_delete") == "true" else False
        student['last_updated'] = datetime.datetime.now()
        student['updated_by'] = "admin"

        collection.update_one({"_id": student_id}, {"$set": student})

        return redirect(url_for("index"))

    return render_template("edit_student.html", student=student)

@app.route('/delete_student/<student_id>', methods=['GET', 'POST'])
def delete_student(student_id):
    collection.delete_one({"_id": student_id})
    return redirect(url_for("index"))

@app.route('/student_detail/<student_id>', methods=['GET', 'POST'])
def student_detail(student_id):
    student = collection.find_one({"_id": student_id})
    tasks_for_student = taskdb.find({"student_id": student_id})
    return render_template("student_detail.html", student=student, tasks=tasks_for_student)

@app.route('/add_task/', methods=['GET', 'POST'])
def add_task():
    # Get the list of student IDs from the database (replace StudentDB with your actual database connection)
    student_ids = collection.find().distinct("_id")

    if request.method == 'POST':
        task_id = request.form.get("task-id")
        task_name = request.form.get("task-name")
        student_id = request.form.get("student-id")
        score = request.form.get("score")
        is_deleted = "No"
        task_created = datetime.datetime.now()
        task_created_by = "admin"
        task_last_updated = datetime.datetime.now()
        task_updated_by = "admin"

        task_data = {
            "_id": task_id,
            "task_name": task_name,
            "score": score,
            "student_id": student_id,
            "is_deleted": is_deleted,
            "task_created": task_created,
            "task_created_by": task_created_by,
            "task_last_updated": task_last_updated,
            "task_updated_by": task_updated_by
        }
        taskdb.insert_one(task_data)
        return redirect(url_for("index"))

    return render_template("add_task.html", student_ids=student_ids)


@app.route('/edit_task/<task_id>', methods=['GET', 'POST'])
def edit_task(task_id):
    task = taskdb.find_one({"_id": task_id})

    if request.method == 'POST':
        if request.form.get("task-name") != "":
            task['task_name'] = request.form.get("task-name")
        if request.form.get("score") != "":
            task['score'] = request.form.get("score")
        task['task_last_updated'] = datetime.datetime.now()
        task['task_updated_by'] = "admin"
        task['is_deleted'] = request.form.get("is_deleted")

        taskdb.update_one({"_id": task_id}, {"$set": task})

        return redirect(url_for("index"))

    return render_template("edit_task.html", task=task)

@app.route('/delete_task/<task_id>', methods=['GET', 'POST'])
def delete_task(task_id):
    taskdb.delete_one({"_id": task_id})
    return redirect(url_for("index"))

if __name__ == '__main__':
    app.run(debug=True)
