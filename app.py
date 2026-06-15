from flask import Flask,flash,render_template,request,jsonify,redirect,url_for,make_response,session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import LoginManager,UserMixin,login_user,current_user,logout_user,login_required 
from flask_migrate import Migrate
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadTimeSignature
from flask_mail import Message,Mail
from redis import Redis
from tensorflow.keras.models import load_model
from PIL import Image
import numpy as np

import os 
from dotenv import load_dotenv

load_dotenv()

lm = LoginManager()

app = Flask(__name__)
app.secret_key = os.getenv('API_KEY')

redis_client = Redis(host='localhost', port=6379, decode_responses=True)

app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///users.db'

s=URLSafeTimedSerializer(app.config['SECRET_KEY'])

db= SQLAlchemy(app)

lm.init_app(app)

model = load_model('model/pneumonia.keras')

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv('USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('PASSWORD')
mail=Mail(app)

migrate = Migrate(app,db)

class User(db.Model,UserMixin):
   id=db.Column(db.Integer,primary_key=True)
   name=db.Column(db.String(100))
   phone=db.Column(db.Integer)
   age=db.Column(db.Integer)
   password=db.Column(db.Integer)
   email=db.Column(db.String(100))
   verified=db.Column(db.Boolean)


@lm.user_loader
def load_user(user_id):
    return User.query.filter_by(id=user_id).first()


@app.route('/verify/<token>')
def verify(token):
    try:
        email=s.loads(token, salt='email-confirm', max_age=1800)
        user=User.query.filter_by(email=email).first()
        user.verified=True
        db.session.commit()
    except SignatureExpired:
        return '<h1>link expired!</h1>',400
    except BadTimeSignature:
        return '<h1>Invalid link</h1>',400
    return '<h1>Email verified!</h1>'

@app.route('/predict',methods=['GET','POST'])
def predict():
    image =Image.open('pn.jpg')
    image = image.resize((224,224))
    image_arr = np.array(image)
    image_arr = np.expand_dims(image_arr, axis=0)
   # print(image_arr)
    pred = model.predict(image_arr)
    print(pred)
    if pred[0][0]>0.5:
        return 'pneumonia'
    else:
        return 'normal'


@app.route('/',methods=['GET','POST'])
def home():
    if request.method == 'POST':
        name = request.form['username']
        age = request.form['age']
        phone = request.form['phone']
        email=request.form['email']
        # response=make_response('Cookie Set')
        # response.set_cookie('username',name)
        # username = request.cookies.get('username')
        password=request.form['password']
        hashed=generate_password_hash(password)
        user1=User(name=name,
                   age=age,
                   phone=phone,
                   password=hashed,
                   email=email,
                   verified=False)
        db.session.add(user1)
        db.session.commit()
        token=s.dumps(email,salt='email-confirm')
        target_url = url_for('verify',token=token,_external=True)
        msg = Message(
        subject="Verify Your Account",
        sender="shoveetsingh2002@gmail.com",
        recipients=[email]
        )
        msg.html = f'<p>Click here to verify: <a href="{target_url}">Link</a></p>'
        mail.send(msg)
    fruit=['apple','banana','coconut','lemon']
    return render_template('home.html',fruit=fruit)


@app.route('/user/<name>')
def user(name):
    return render_template('index.html',user=name)
 
@app.route('/image',methods=['POST'])
def image():
   im = request.files['image']
   if (im):
      return 'image uploaded'
   return 'No img found'

@app.route('/api')
def api():
   data={
       'name':'shoveetsingh2002@gmail.com',
      'role':'Ml enineer'
   }
   #data= jsonify(data)
   session['username']=data.get('name','User not found!')
   session['role']=data.get('role','Unemployed!')
#    session.pop('username',None)
#    session.pop('role',None)
#    return 'cleared'
   user= User.query.filter_by(name=session['username']).first()
   if(user):
     db.session.delete(user)
     db.session.commit()
     print('Deleted user!')
         
   return session['username']+' '+session['role']

@app.route('/users')
def users():
    hits=redis_client.incr('visitor counted')
    if hits==1:
        redis_client.expire('visitor counted',60)
    if hits>5:
        ttl=redis_client.ttl('visitor counted')
        return f'try after {ttl} seconds!'
    query=User.query.all()
    if not query:
        return 'Users not found!!'
   #  q=User.query.first()
   #  q.name='batistawwe2000@gmail.com'
   #  db.session.commit()
    # num_rows_deleted = User.query.delete()
    
    # Commit the session to save changes
    # db.session.commit()
    result=''
    for user in query:
         result +=str(user.id) +str(user.age) + str(user.phone) + user.name + "<br>"
    return result

@app.route('/login',methods=['GET','POST'])
def login():
    # if current_user.is_active:
    #     return 'Nigga'
    if current_user.is_authenticated:
       return f'Welcome back {current_user.name}'
    if request.method == 'POST':
        password=request.form['password']
        name=request.form['name']
        user=User.query.filter_by(name=name).first()
        if user:
            if check_password_hash(user.password,password):
               login_user(user)
               return f'Welcome {name}'
            return 'Not found in db'
    return 'ello guest'

@app.route('/logout')
def logout():
    if current_user.is_active:
        logout_user()
    return 'loed out'
    
#@login_required

if __name__== '__main__':
    with app.app_context():
         db.create_all()
    app.run(debug=True)