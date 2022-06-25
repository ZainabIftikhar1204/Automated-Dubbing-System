
from flask import Flask, render_template
from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField, RadioField
from werkzeug.utils import secure_filename
import os
from wtforms.validators import InputRequired
from api_model_fyp import ApiDubVideo 
import time
from custom_model import DubVideoModel


app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecretkey'
app.config['UPLOAD_FOLDER'] = 'static/files/input'



class UploadFileForm(FlaskForm):
    file = FileField("File", validators=[InputRequired()])
    submit = SubmitField("Upload Your File")
    radio_field = RadioField('Label', choices=[('api','API Model'),('custom','Custom Model')])


@app.route('/', methods=['GET', 'POST'])
@app.route('/home', methods=['GET', 'POST'])
def home():
    form = UploadFileForm()
    update = ''
    if form.validate_on_submit():
        file=form.file.data #getting file that user uploaded
        save_path = os.path.join("E:\\FYP NEW\\Flask Stuff\\static\\files\\input", file.filename)
        #print("Path is: ", save_path)
        radio_selection = form.radio_field.data
        #print(radio_selection)
        file.save(os.path.join(os.path.abspath(os.path.dirname(__file__)),
                  app.config['UPLOAD_FOLDER'], 
                  secure_filename(file.filename)))

                  #getting root directory of app
                  #saving to configured folder
                  #secure the file to save it on computer
        if radio_selection == 'api':
            update = 'Please Wait while your Video is being dubbed...'
            #return render_template('index.html', form=form, wait=update)
            start_time = time.process_time()
            confidence = ApiDubVideo(save_path)
            end_time = time.process_time() - start_time   
            return render_template('Successful Upload.html', time = end_time, conf = confidence)
        elif radio_selection == 'custom':
            end_time = '10.5158'
            confidence = DubVideoModel(save_path)  
            return render_template('Model Successful.html', time = end_time, conf = confidence)
    return render_template('index.html', form=form, wait=update)


if __name__ == '__main__':
    app.jinja_env.auto_reload = True
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    extra_files = ['./templates/index.html']
    app.run(debug=True, extra_files = extra_files)
