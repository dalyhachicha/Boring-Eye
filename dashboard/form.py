#Flask WTForms
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField,RadioField, IntegerField, FloatField, SelectField
from wtforms.validators import InputRequired,Email,EqualTo,ValidationError
#CUSTOM VALIDATORS

#CHHECK if client id exist if not return False
def checkId(form,field):
    from dashboard.main import clients 
    if str(field.data) == "0":
        return True
    if (clients.find({'_id':field.data})).count() < 1 :
        raise ValidationError('Coudn\'t find '+field.data)
        
def checkProductId(form,field):
    from dashboard.main import products
    if (products.find({'_id': field.data})).count() > 0:
        raise ValidationError('Id : '+field.data+' is taken.')
        
#Check If email Is Taken Or NOT FUNCTION
def checkEmail(form,field):
    from dashboard.main import clients
    if (clients.find({'email': field.data})).count() > 0:
        raise ValidationError('Email : '+field.data+' has already been taken.')
        
def checkPayment(form,field):
    from dashboard.main import payments
    if (payments.find({'_id': field.data})).count() < 1 :
        raise ValidationError('Payment : '+field.data+' Does not exist.')

def checkPaymentInOrders(form,field):
    from dashboard.main import orders
    if (orders.find({'payment_id': field.data})).count() > 0 :
        raise ValidationError('Payment : '+field.data+' Already used in other order.')
    
################# CLASS FORMS ###################

class EditProductForm(FlaskForm):
    product_id = StringField('product_id') 
    name = StringField('name')
    desc = StringField('desc') 
    qte = IntegerField('qte') 
    price = FloatField('price') 
    submit = SubmitField('submit')
class EditOrderForm(FlaskForm):
    order_id = StringField('order_id') 
    status = StringField('status')
    worker_id = StringField('worker_id') 
    id_client = StringField('id_client') 
    payment_id = StringField('payment_id') 
    payment_status = StringField('payment_status')
    submit = SubmitField('submit')
    
    
class SleepForm(FlaskForm):
    password = PasswordField('password', validators=[InputRequired('Password is required.')])
    submit = SubmitField('submit')

class EditProfileForm(FlaskForm):
    _id = StringField('_id',validators=[InputRequired()])
    name = StringField('name',validators=[InputRequired()])
    email = StringField('email')
    phone = StringField('phone',validators=[InputRequired()])
    birthday = StringField('birthday',validators=[InputRequired()])
    gender = RadioField('gender', choices = ['Male', 'Female', 'male', 'female', 'M', 'F', 'm', 'f'])
    address = StringField('address',validators=[InputRequired()])
    password = PasswordField('password', validators=[InputRequired()])
    cpassword = PasswordField('cpassword', validators=[InputRequired(),EqualTo('password')])
    save = SubmitField('save')
    
class SearchClientForm(FlaskForm):
    value = StringField('value',validators=[InputRequired()])
    key = StringField('key')
    search = SubmitField('search')
    
class SearchProductForm(FlaskForm):
    value = StringField('value',validators=[InputRequired()])
    key = StringField('key')
    search = SubmitField('search')
    
class AddClientForm(FlaskForm):
    name = StringField('name',validators=[InputRequired()] )
    password = PasswordField('password', validators=[InputRequired()])
    cpassword = PasswordField('cpassword', validators=[InputRequired(),EqualTo('password')])
    email = StringField('email', validators=[InputRequired(), Email(), checkEmail])
    phone = StringField('phone')
    birthday = StringField('birthday')
    gender = RadioField('gender', choices = ['Male', 'Female', 'male', 'female', 'M', 'F', 'm', 'f'])
    nv_re = StringField('nv_re')
    nv_le = StringField('nv_le')
    fv_re = StringField('fv_re')
    fv_le = StringField('fv_le')
    glasses_type = StringField('glasses_type')
    always_wear = RadioField('always_wear', choices = ['y', 'n'])
    submit = SubmitField('add')
    

class LoginForm(FlaskForm):
    username = StringField('username', validators=[InputRequired('Username is required.')])
    password = PasswordField('password', validators=[InputRequired('Password is required.')])
    submit = SubmitField('login')

class AddProductForm(FlaskForm):
    product_id = StringField('product_id',validators=[InputRequired(), checkProductId])
    name = StringField('name',validators=[InputRequired()] )
    desc = StringField('desc')
    qte = IntegerField('qte', validators=[InputRequired()])
    price = FloatField('price', validators=[InputRequired()])
    submit = SubmitField('add')
    
class AddOrderForm(FlaskForm):
    id_client = StringField('id_client')
    status = StringField('status',validators=[InputRequired()] )
    payment_status = StringField('payment_status',validators=[InputRequired()] )
    payment_id = StringField('payment_id',validators=[checkPayment, checkPaymentInOrders] )
    submit = SubmitField('submit')
    
class PayementForm(FlaskForm):
    amount = FloatField('amount', validators=[InputRequired()])
    client_id = StringField('client_id', validators=[checkId])
    submit = SubmitField('checkout')

class SearchPaymentForm(FlaskForm):
    value = StringField('value',validators=[InputRequired()])
    key = StringField('key')
    search = SubmitField('search')
    
class SearchOrderForm(FlaskForm):
    value = StringField('value',validators=[InputRequired()])
    key = StringField('key')
    search = SubmitField('search')