from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
from os.path import isfile, isdir, join, dirname, basename, abspath
import pathlib

def mkdir(directory):
    print('creating dir "%s"' %directory)
    pathlib.Path(directory).mkdir(parents=True, exist_ok=True)

def save_file(file_path, file):
    file_directory = abspath(join('./upload/', secure_filename(dirname(file_path))))
    file_name = basename(file_path)
    mkdir(file_directory)
    print(file_path)
    print("saving to \"%s\"" %join(file_directory, file_name))
    file.save(join(file_directory, file_name))

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
        f = request.files['image']
        file_path = f.filename
        if "fullPath" in request.form:
            file_path = request.form["fullPath"]
        save_file(file_path, f)
        return 'thanks'
    else:
        return "whoops"