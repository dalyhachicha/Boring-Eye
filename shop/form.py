#Flask WTForms
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired,Email,EqualTo,ValidationError
import datetime

#CUSTOM VALIDATORS     

#Check if birthday is good or not  
def checkBday(form,field):
    if field.data == "":
        return True
    day,month,year = field.data.split('/')
    try :
        datetime.datetime(int(year), int(month),int(day))
    except ValueError :
        raise ValidationError('Birthday : '+field.data+' is not Valid.')  
   
    
#Check If email Is Taken Or NOT FUNCTION
def checkEmail(form,field):
    from main import clients
    if (clients.find({'email': field.data})).count() > 0:
        raise ValidationError('Email : '+field.data+' has already been taken.')  


class FeedbackForm(FlaskForm):
    name = StringField('name',validators=[] )
    email = StringField('email',validators=[] )
    subject = StringField('subject',validators=[] )
    message = StringField('message',validators=[] )
    submit = SubmitField('send')
    
    
class PersonalInfoForm(FlaskForm):
    fname = StringField('fname',validators=[InputRequired()] )
    lname = StringField('lname',validators=[InputRequired()] )
    password = PasswordField('password', validators=[InputRequired()])
    cpassword = PasswordField('cpassword', validators=[InputRequired(),EqualTo('password')])
    email = StringField('email', validators=[InputRequired(), Email(), checkEmail])
    phone = StringField('phone')
    birthday = StringField('birthday', validators=[checkBday])
    gender = StringField('gender')
    address = StringField('address')
    submit = SubmitField('next')
    
    
class MedicalInfoForm(FlaskForm):
    nv_re = StringField('nv_re')
    nv_le = StringField('nv_le')
    fv_re = StringField('fv_re')
    fv_le = StringField('fv_le')
    glasses_type = StringField('glasses_type')
    other_notes = StringField('other_notes')
    always_wear = StringField('always_wear')
    submit = SubmitField('next')
       
class LoginForm(FlaskForm):
    username = StringField('email', validators=[InputRequired('Email is required.'), Email()])
    password = PasswordField('password', validators=[InputRequired('Password is required.')])
    submit = SubmitField('login')
    
    


class ResetForm(FlaskForm):
    email = StringField('email', validators=[InputRequired(), Email()])
    submit = SubmitField('reset')

    
class NewPasswordForm(FlaskForm):
    password = PasswordField('password', validators=[InputRequired()])
    cpassword = PasswordField('cpassword', validators=[InputRequired()])    
    submit = SubmitField('reset')
    
class AccountSettingsForm(FlaskForm):
    name = StringField('name',validators=[InputRequired()] )
    phone = StringField('phone')
    birthday = StringField('birthday',  validators=[checkBday])
    nv_re = StringField('nv_re')
    nv_le = StringField('nv_le')
    fv_re = StringField('fv_re')
    fv_le = StringField('fv_le')
    faceshape = StringField('faceshape')
    glasses_type = StringField('glasses_type')
    address = StringField('address')
    submit = SubmitField('update')

############################################################


        
    
    




    
