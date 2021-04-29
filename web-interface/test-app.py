from flask import Flask, render_template, request
from werkzeug.utils import secure_filename

app = Flask(__name__)

@app.route('/')
def hello_world():
    return render_template('home.html')

@app.route('/upload/<int:projectid>')
def upload(projectid=None):
    return render_template('upload.html')


@app.route('/upload_image', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if "fullPath" in request.form:
            print(request.form["fullPath"])
        f = request.files['image']
        f.save('./upload/'+secure_filename(f.filename))
        return 'thanks'
    else:
        return "whoops"