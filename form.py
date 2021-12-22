#Flask WTForms
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField,RadioField
from wtforms.validators import InputRequired,Email,EqualTo,ValidationError
from flask_wtf.file import FileField, FileRequired, FileAllowed
#CUSTOM VALIDATORS

#Check If username Is Taken Or NOT FUNCTION
def checkUsername(form,field):
    from main import clients
    if (clients.find({'username': field.data})).count() > 0:
        raise ValidationError('Username : '+field.data+' has already been taken.')
        
        
#Check If email Is Taken Or NOT FUNCTION
def checkEmail(form,field):
    from main import clients
    if (clients.find({'email': field.data})).count() > 0:
        raise ValidationError('Email : '+field.data+' has already been taken.')
        
################# CLASS FORMS ###################
class SignupForm(FlaskForm):
    pic = FileField('pic',validators=[FileRequired(), FileAllowed(['jpg','jpeg','png'])])
    upload = SubmitField('upload')
    
    
class AccountSettingsForm(FlaskForm):
    name = StringField('fullname',validators=[InputRequired()] )
    phone = StringField('phone')
    birthday = StringField('birthday')
    email = StringField('email', validators=[InputRequired(), Email(), checkEmail])
    nv_re = StringField('nv_re')
    nv_le = StringField('nv_le')
    fv_re = StringField('fv_re')
    fv_le = StringField('fv_le')
    glasses_type = StringField('glasses_type')
    username = StringField('username', validators=[InputRequired('Username is required.'), checkUsername])
    password = PasswordField('password', validators=[InputRequired('Password is required.')])
    submit = SubmitField('update')
    
class personalInfoForm(FlaskForm):
    name = StringField('fullname',validators=[InputRequired()] )
    password = PasswordField('password', validators=[InputRequired()])
    cpassword = PasswordField('cpassword', validators=[InputRequired(),EqualTo('password')])
    email = StringField('email', validators=[InputRequired(), Email(), checkEmail])
    phone = StringField('phone')
    birthday = StringField('birthday')
    gender = RadioField('gender', choices = ['M', 'F'])
    submit = SubmitField('next')
    
class medicalInfoForm(FlaskForm):
    nv_re = StringField('nv_re')
    nv_le = StringField('nv_le')
    fv_re = StringField('fv_re')
    fv_le = StringField('fv_le')
    glasses_type = StringField('glasses_type')
    always_wear = RadioField('always_wear', choices = ['y', 'n'])
    submit = SubmitField('finish')
    
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
    
