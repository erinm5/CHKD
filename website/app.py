from flask import Flask, render_template, redirect, url_for, request
from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField
from werkzeug.utils import secure_filename
import os
import numpy as np
from wtforms.validators import InputRequired
import socket

video_formats = [".mp4", ".webm"] # hardcoded video formats
image_formats = [".jpg", ".png", "jpeg", ".gif",".bmp"] # hardcoded image formats
audio_formats = [".mp3", ".m4a", ".wav"] # hardcoded audio formats

app = Flask(__name__)
app.config['SECRET_KEY'] = 'nerf'
app.config['UPLOAD_FOLDER'] = 'static'
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024

#checks that a file was acutally uploaded
class UploadFileForm(FlaskForm):
    file = FileField("File", validators=[InputRequired()])
    submit = SubmitField("Upload File")

class Groups():
    def __init__(self, users, id):
        self.users = users
        self.id = id
        self.quest = ""
        self.rules = ""
    def add_quest(self, quest, rules):
        self.quest = quest
        self.rules = rules 

#checks what type of media was uploaded
#returns an int 1-image, 2-video, 3-audio
def mediaType(img_name):
    if any(word in img_name for word in image_formats):
        media_type = 1 # if user input is an image 
    elif any(word in img_name for word in video_formats):
        media_type = 2 # if user input is a video
    elif any(word in img_name for word in audio_formats):
        media_type = 3
    else:
        media_type = 0 # unsupported media format
    return media_type

temp_submissions = []  #temp array to hold media url, and ratings
temp_group = Groups("none", 0)#temp group fo testing


#creates the website on localhost:5000
@app.route('/', methods=['GET',"POST"])

#creates the test home page
@app.route('/home', methods=['GET',"POST"])
def home():
    quest_check = 0 #checks if a quest has been made yet
    if(temp_group.quest != ""):
        quest_check = 1
    if request.method == "POST":
        if(quest_check):
            return redirect(url_for('upload', group = temp_group.id))
        else:
            return redirect(url_for('create'))         
    return render_template('index.html', quest_check = quest_check)


@app.route('/create', methods=['GET', 'Post'])
def create():
    if request.method == "POST":
        # getting input with name = fname in HTML form
        quest = request.form.get("quest")
        # getting input with name = lname in HTML form
        rules = request.form.get("rules")
        # create group object
        temp_group.add_quest(quest, rules) 
        group_id = temp_group.id
        return redirect(url_for('upload', group = group_id))
    return render_template("create.html")


@app.route('/upload/<group>', methods=["GET", "POST"])
def upload(group):
    quest_msg = temp_group.quest
    rules_msg = temp_group.rules
    #get into the root path
    root_path = os.path.dirname(os.path.abspath(__file__))
    #get the folder
    folder =  os.listdir(os.path.join(root_path, 'static'))
    #get the amount of files in the fodler
    folder_len = len(folder) 

    form = UploadFileForm()
    if form.validate_on_submit():
        file = form.file.data # First grab the file
        file.save(os.path.join(os.path.abspath(os.path.dirname(__file__)),app.config['UPLOAD_FOLDER'],secure_filename(str(folder_len) +file.filename))) # Then save the file
        # allocate space in the list
        temp_submissions.append(0)
        
        return redirect(url_for('watch', curr = 0))
    return render_template('upload.html', form=form, quest = quest_msg, rules =rules_msg)
           

#creates webpage to veiw the actual submissions
@app.route('/watch/<curr>', methods=['GET', 'POST'])
def watch(curr):
    curr = int(curr)
    #get into the root path
    root_path = os.path.dirname(os.path.abspath(__file__))
    #get the folder
    folder =  os.listdir(os.path.join(root_path, 'static'))
    folder_len = len(folder) -1 
   
    #get the first file name from the media folder
    img_name = os.listdir(os.path.join(root_path, 'static'))[curr]
    print(img_name)
    print(curr)
    #get the full path of the file
    # full_img_path = os.path.join(os.path.abspath(os.path.dirname(__file__)),app.config['UPLOAD_FOLDER'],secure_filename(img_name)) # Then save the file

    if request.method == "POST":

        button = request.form["submit_button"]
        if(button == "NEXT"):
            if curr == folder_len:
                print(folder_len)
            else:
                curr += 1
        if(button == "PREV"):
            if curr == 0:
                print("No previous files")
            else:
                curr -= 1
        if(button == "NEW"):
            return redirect(url_for('upload', group = temp_group.id))
        if(button == "UP"):
            temp_submissions[curr] += 1
            print("Current vote counter:")
            print(temp_submissions[curr])
            return redirect(url_for('results'))        
        #load next media file
        return redirect(url_for('watch', curr=curr))
    # Load the webpage
    else:
            return  render_template('watch.html', user_input = img_name, media = mediaType(img_name), curr = curr, files = folder_len)
    

 #creates webpage to veiw the actual submissions
 #this is not fully coded yet
@app.route('/results', methods=['GET', 'POST'])
def results():
    winner_index = 0
    #get into the root path
    root_path = os.path.dirname(os.path.abspath(__file__))
    #get the folder
    folder =  os.listdir(os.path.join(root_path, 'static'))
    folder_len = len(folder) -1 
    #get the first file name from the media folder
    img_name = os.listdir(os.path.join(root_path, 'static'))[winner_index]
    print(img_name)
    print(winner_index)
    return  render_template('results.html', user_input = img_name, media = mediaType(img_name), votes = 0)       



if __name__ == '__main__':
    #uncommnet if you want everyone on your network to connect
    #print(socket.gethostbyname(socket.gethostname()))
    #app.run(debug=True, host = "0.0.0.0", port = 25565)
    app.run(debug=True)