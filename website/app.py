from flask import Flask, render_template, redirect, url_for, request
from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField, StringField
from wtforms.widgets import TextArea
from werkzeug.utils import secure_filename
from flask_wtf.file import FileField, FileAllowed
import os
from wtforms.validators import InputRequired, DataRequired, Length
import socket

video_formats = [".mp4", ".webm"] # hardcoded video formats
image_formats = [".jpg", ".png", "jpeg", ".gif",".bmp"] # hardcoded image formats
audio_formats = [".mp3", ".m4a", ".wav"] # hardcoded audio formats

#root of the website folder
root_path = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__)
app.config['SECRET_KEY'] = 'nerf'
app.config['MEDIA_FOLDER'] = 'static\media'
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024

#gets quest creation info
class QuestForm(FlaskForm):
    quest = StringField('quest', widget = TextArea(), validators=[DataRequired(), Length(max= 500)])
    rules = StringField('rules', widget = TextArea(), validators=[DataRequired(), Length(max= 500)])

#gets quest submission
class UploadFileForm(FlaskForm):
    file = FileField("File", validators=[InputRequired()])
    submit = SubmitField("Upload File")

#get login info
class LoginForm(FlaskForm):
    name = StringField('name', validators=[DataRequired(), Length(max= 30)])
    password = StringField('password', validators=[DataRequired(), Length(max= 30)])
    login = SubmitField("Login")

#stores group info
class Groups():
    def __init__(self, users, id):
        self.users = users
        self.id = id
        self.quest = ""
        self.rules = ""
    def add_quest(self, quest, rules):
        self.quest = quest
        self.rules = rules 

#mediaType(), given an image name checks what type of media was uploaded
#returns an int 1-image, 2-video, 3-audio
def mediaType(img_name):
    if any(word in img_name for word in image_formats):
        media_type = 1 # image 
    elif any(word in img_name for word in video_formats):
        media_type = 2 # video
    elif any(word in img_name for word in audio_formats):
        media_type = 3 # audio
    else:
        media_type = 0 # unsupported media format
    return media_type

#FAKE DATABSE!
#This is here beacause I havent connected the website to the data base yet
temp_submissions = []  #temp array to hold media url, and ratings
temp_group = Groups("none", 0)#temp group fo testing


#creates the website on localhost:5000
@app.route('/', methods=['GET',"POST"])

#login page
@app.route('/login', methods=['GET',"POST"])
def login():
    form = LoginForm()
    if request.method == "POST":
        user_name = str(form.name.data)
        print("this ran")
        return redirect(url_for('home', user = user_name))
    return(render_template('login.html', form = form))
    
#home page
@app.route('/home/<user>', methods=['GET',"POST"])
def home(user):
    quest_check = 0 #checks if a quest has been made yet
    if(temp_group.quest != ""):
        quest_check = 1
    if request.method == "POST":
        if(quest_check):
            return redirect(url_for('upload', group = temp_group.id))
        else:
            return redirect(url_for('create'))         
    return render_template('index.html', quest_check = quest_check, user = user)


#/create, collects text information to create a task
#returns the upload page after any text is sumbitted
@app.route('/create', methods=['GET', 'Post'])
def create():
    #create the quest
    form = QuestForm()
    if request.method == "POST":
        quest = form.quest.data # First grab the file
        rules = form.rules.data
        temp_group.add_quest(quest, rules)
        return redirect(url_for('upload', group = temp_group.id))
    return render_template("create.html", form = form)

#/upload/<group> uploads files from the websever to the database, given the group number
#returns redirect to watch page to veiw the submissions
@app.route('/upload/<group>', methods=["GET", "POST"])
def upload(group):
    file_num = len(os.listdir(os.path.join(root_path, app.config['MEDIA_FOLDER']))) 
    quest_msg = temp_group.quest
    rules_msg = temp_group.rules
    form = UploadFileForm()
    if form.validate_on_submit():
        file = form.file.data # First grab the file
        #save the file to (file location of root + file in root + file name)
        file.save(os.path.join(os.path.abspath(os.path.dirname(__file__)),app.config['MEDIA_FOLDER'],secure_filename(str(file_num) + file.filename))) # Then save the file
        #update the fake databse
        temp_submissions.append(0)
        return redirect(url_for('watch', curr = 0))
    return render_template('upload.html', form=form, quest = quest_msg, rules =rules_msg)
           

#/watch/<curr> creates webpage to veiw the actual submissions, curr is the submission
#returns the next or previous submission, or redirects to the voting page
@app.route('/watch/<curr>', methods=['GET', 'POST'])
def watch(curr):
    curr = int(curr)
    folder_len = len(os.listdir(os.path.join(root_path, app.config['MEDIA_FOLDER']))) -1
    img_name = 'media/' + os.listdir(os.path.join(root_path, app.config['MEDIA_FOLDER']))[curr]
    #check what button is pressed
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
    

 #/results, webpage to veiw the top upvoted
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
    '''
    #Uncomment if you want everyone on your local network to connect!
    #This will work on eduroam or umbc vistor for a class demostration 
    #your new url will be given in the termianl
    print(socket.gethostbyname(socket.gethostname()))
    app.run(debug=True, host = "0.0.0.0", port = 25565)
    '''
    app.run(debug=True)