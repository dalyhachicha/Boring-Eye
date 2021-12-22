#Flask 
from flask import redirect, url_for, render_template, request, session, Response, Blueprint, flash
#For camera opening in browser
from face_mesh import FaceMeshDetector
#MongoDB
import pymongo
from pymongo import MongoClient
#For randStr Function
from cfg import randStr
from shop.form import FeedbackForm, AccountSettingsForm, PersonalInfoForm, LoginForm, MedicalInfoForm, ResetForm, NewPasswordForm
#For faceshape determination 
from faceshape import face
from datetime import date
#For encoding Selfie
from base64 import b64encode
import secrets
from cfg import faces, faces_names, faces_paths, good_paths, bad_paths, good_names, bad_names
#mail
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

#inisilization 
cart = ""


#NOSQL DATABASE CONNECTION
cluster = MongoClient("mongodb+srv://beye:Feriani01@cluster0.0p206.mongodb.net/boringeye?retryWrites=true&w=majority")
db = cluster["boringeye"]
clients = db["clients"] 
workers = db["workers"]
products = db["products"]
payments = db["payments"]
orders = db["orders"]
feedback = db["feedback"]
tokens = db["tokens"]
visitors = db["visitors"]
wishlists = db["wishlists"]
votes = db["votes"]



shop = Blueprint("shop", __name__, static_folder="static", template_folder="templates")



def getClient(key,value,get=False):
    if get == False:
        try:
            client = clients.find_one({key:value})
            if client == None:
                return False
            else: 
                return client
        except pymongo.errors.PyMongoError as e:
            return False
    else:
        try:
            client = clients.find_one({key:value})
            if client == None:
                return False
            else: 
                return client[get]
        except pymongo.errors.PyMongoError as e:
            return False

##############################################################################
############################   CONTACT US    #################################
##############################################################################
@shop.route("/contact-us/", methods=['POST','GET'])
def contactPage():
    feedbackForm = FeedbackForm()
    if feedbackForm.validate_on_submit():
        isSent = sendFeedback(feedbackForm)
        if isSent:
            flash('Your message successfully sent '+feedbackForm.name.data+'.<br>We will get back as soon as possible.','success')
            return redirect(url_for('shop.contactPage'))
        else:
            flash('Coudnt send your message ! Contact us at : boringeye@support.com','danger')
            return redirect(url_for('shop.contactPage'))
    return render_template('shop_contact.html', form=feedbackForm)

#Function send feedback (Contact Us) Function     
def sendFeedback(form):
    msg = {"ip" : request.remote_addr,
        "name" : form.name.data,
        "email"  : form.email.data,
        "message" : form.message.data,
        "subject" : form.subject.data,
        "from" : "SHOP",
        "date" : date.today().strftime("%d/%m/%Y")
        }
    try :
        resultat = feedback.insert_one(msg)
        return True
    except pymongo.errors.PyMongoError as e:
        return False
##############################################################################
############################   ABOUT    ######################################
##############################################################################
@shop.route("/about/", methods=['POST','GET'])
def aboutPage():
    return render_template('shop_about.html')


##############################################################################
############################   PAYMENTS   ####################################
##############################################################################
@shop.route("/my-payments/<_id>/", methods=['POST','GET'])
def myPaymentsPage(_id):
    if _id != None:
        if authentificated(_id) == False:
            flash('You have to login first.','danger')
            return redirect(url_for('shop.login'))

    
    return render_template("my-payments.html", _id=_id, payments=getClientPayments(_id), data = getClientData(_id))

def getClientPayments(client_id):
    try:
        payment_list = payments.find({'client_id':client_id})
        return payment_list
    except pymongo.errors.PyMongoError as e:
        return False
    
##############################################################################
############################   ORDER   #######################################
##############################################################################
@shop.route("/my-orders/<_id>/", methods=['POST','GET'])
def myOrdersPage(_id):
    if _id != None:
        if authentificated(_id) == False:
            flash('You have to login first.','danger')
            return redirect(url_for('shop.login'))

    
    return render_template("my-orders.html", _id=_id, orders=getClientOrders(_id), data = getClientData(_id))
    
@shop.route("/order-detail/<_id>/<order_id>/", methods=['POST','GET'])
def orderDetailPage(_id,order_id):
    if _id != None:
        if authentificated(_id) == False:
            flash('You have to login first.','danger')
            return redirect(url_for('shop.login'))

        
    return render_template("order_detail.html", _id=_id, order=getOrders(order_id), data = getClientData(_id))


def getClientOrders(_id):
    try:
        order_list = orders.find({'id_client' : _id})
        return order_list
    except pymongo.errors.PyMongoError as e:
        return False


def getOrders(order_id):
    try:
        order = orders.find_one({'_id':order_id})
        return order
    except pymongo.errors.PyMongoError as e:
        return False
    
##############################################################################
############################   FACESHAPE   ###################################
##############################################################################
@shop.route("/faceshape/<_id>/", methods=['POST','GET'])
def faceshapePage(_id):
    if authentificated(_id) == False:
        flash('You have to login first.','danger')
        return redirect(url_for('shop.login'))
    
    client = getClientData(_id)
    if client == None:
        flash('All you need is a quick selfie to start using eyeglasses recemndation system.','info')
        return redirect(url_for('shop.profile',_id=_id))
    #faces_names.index(client['faceshape']) is the index of client faceshape (/cfg.py)
    face_index = faces_names.index(client['faceshape'].upper())
    faceshape = faces[face_index]
        
    paths = [good_paths[face_index], bad_paths[face_index], good_names[face_index], bad_names[face_index]]
    return render_template('shop_faceshape.html', paths=paths, _id=_id, products = getFaceshapeProducts(_id,faceshape), data = client, faceshape=faceshape, face_path=faces_paths[face_index]  )


def getFaceshapeProducts(_id,faceshape):
    try:
        faceshape = getClient('_id',_id,'faceshape')
        if faceshape == False:
            return None
        product_list = products.find({'shape':faceshape})
        return product_list
    except pymongo.errors.PyMongoError as e:
        return False
##############################################################################
############################   Index   #######################################
##############################################################################
@shop.route("/fromdashboard/<worker_id>/")
def shopFromDashboard(worker_id):
    if authentificated(worker_id) == False:
            flash('You have to login first.','danger')
            return redirect(url_for('shop.home'))
    else:
        dProducts = getSomeProducts()
        return render_template("shop_index.html",_id=worker_id, dProducts=dProducts, products=productsForIndex())
            
@shop.route("/", methods=['POST','GET'])
@shop.route("/<_id>/", methods=['POST','GET'])
def index(_id=None):
    if _id != None:
        if authentificated(_id) == False:
            flash('You have to login first.','danger')
            return redirect(url_for('shop.login'))
        
        
    dProducts = getSomeProducts()
    return render_template("shop_index.html",_id=_id, dProducts=dProducts, products=productsForIndex())

def productsForIndex():
    try:
        product_list = products.find({ 'shape' : { '$exists': True } })
        return product_list
    except pymongo.errors.PyMongoError as e:
        return False
    
    
def getSomeProducts():
    try:
        product_list = products.find().limit(15)
        return product_list
    except pymongo.errors.PyMongoError as e:
        return False

def authentificated(_id):
    try:
        if session.get('_id') == False:
            return False
        if session.get('logged_in') == False:
            return False
        else:
            if session['logged_in'] == False:
                return False
        return _id == session["_id"]
    except:
        return False
    
        
##############################################################################
############################   LOGIN   #######################################
##############################################################################

#Login Page
@shop.route('/login/', methods=['POST','GET'])
def login():
    session["_id"] = False
    session["logged_in"] = False
    loginForm = LoginForm()
    if loginForm.validate_on_submit():
        usr = loginForm.username.data
        pwd = loginForm.password.data
        isAuthentificated = authentification(usr,pwd)
        if isAuthentificated == None:
            flash('We have no account with this email!', 'warning')
            return redirect(url_for('shop.login'))
        elif isAuthentificated == False:
            flash('Password is wrong!', 'danger')
            return redirect(url_for('shop.login'))
        
        session["logged_in"] = True
        session["_id"] = getClient('email',usr,'_id')
        return redirect(url_for('shop.index', _id = session["_id"]))
    return render_template("signin.html", form = loginForm)

############################   FUNCTIONS   ####################################


def getClientData(_id):
    #           MAP
    #typical client shit
    #order_placed ------count-------
    #wishlist_count ------count-------
    #orders
    try:
        client = clients.find_one({"_id" : _id})
        del client['password']
        client['order_placed'] = countClientOrderPlaced(_id)
        #client[''] = 
        client['orders'] = getClientOrders(_id)
        return client
    except:
        return None



def countClientOrderPlaced(_id):
    order_count = orders.find({'id_client' : _id}).count()
    return order_count



#Authentification Function
def authentification(usr,pwd):
    client = clients.find_one({'email' : usr})
    if client == None:
        return None
    return pwd == client['password']

##############################################################################
############################   Signup   ######################################
##############################################################################

#Signup Page
@shop.route('/signup/', methods=['POST','GET'])
def signupP():
    signupFormP = PersonalInfoForm()
    if signupFormP.validate_on_submit():
        session['_id'] = randStr(8)
        session["logged_in"] = True
        if addClientPerso(signupFormP):
            flash('Your informations have been saved.','success')
            return redirect(url_for('shop.signupM', _id = session['_id']))
        else:
            flash('Coudnt save your personel informations!', 'danger')
            return redirect(url_for('shop.signupP'))
        
    return render_template("signup.html",title = "Sign Up", form=signupFormP)
    
#Signup 2 Page
@shop.route('/signup2/<_id>/', methods=['POST','GET'])
def signupM(_id):
    if authentificated(_id) == False:
        flash('You have to signup your personel information first.','danger')
        return redirect(url_for('shop.signupP'))
    
    
    signupFormM = MedicalInfoForm()
    if signupFormM.validate_on_submit():
        if addClientMedical(signupFormM,_id):
            return redirect(url_for('shop.signupS',_id=_id))
        else:
            flash('Coudnt save your medical informations!', 'danger')
            return redirect(url_for('shop.signupM'))
        
    return render_template("signup2.html",title = "Sign Up", form=signupFormM, _id=_id)


#Signup 3 Page
@shop.route('/signup3/<_id>/', methods=['POST','GET'])
def signupS(_id):
    if authentificated(_id) == False:
        flash('You have to signup your personel information first.','danger')
        return redirect(url_for('shop.signupP'))
    

    if request.method == 'POST':
        session["logged_in"] = True
        session["_id"] = _id
        return redirect(url_for('shop.profile', _id = session["_id"]))
    else:    
        return render_template("signup3.html",title = "Sign Up", _id=_id)

#Add M INFO Client Function
def addClientMedical(form, _id):
    
    try :
        medicalData = { "nv_re" : form.nv_re.data ,
                   "nv_le" : form.nv_le.data ,
                   "fv_re" : form.fv_re.data ,
                   "fv_le" : form.fv_le.data,
                   "glasses_type" : form.glasses_type.data,
                   "always_wear" : form.always_wear.data,
                   "other_notes" : form.other_notes.data}
        
        resultat = clients.find_one_and_update({ "_id": _id },
                                              { "$set": medicalData})
        return True
    except pymongo.errors.PyMongoError as e:
        return False


def CreateWishlist():
    try:
        wishlist = {'_id':session['_id'],
                    'product_ids' : ','}
        resultat = wishlists.insert_one(wishlist)
        return True
    except pymongo.errors.PyMongoError as e:
        return False
        
#Add P INFO Client Function
def addClientPerso(form):
    CreateWishlist()
    client = {
        "_id"   : session['_id'],
        "name" : form.fname.data + ' ' + form.lname.data,
        "birthday"  : form.birthday.data,
        "gender" : form.gender.data,
        "email" : form.email.data,
        "password" : form.password.data,
        "phone" : form.phone.data,
        "added_by" : "0",
        "date" : date.today().strftime("%d/%m/%Y"),
        "picture" : None,
        "faceshape" : None
        }
    try :
        resultat = clients.insert_one(client)
        return True
    except pymongo.errors.PyMongoError as e:
        return False
    

##############################################################################
############################   PASSWORDS   ###################################
##############################################################################

#1 Reset Password Page 
@shop.route('/forget-password/', methods=['POST','GET'])
def forgetPassword():
    session["_id"] = False
    session["logged_in"] = False
    resetForm = ResetForm()
    if resetForm.validate_on_submit():
        email = resetForm.email.data
        sent = sendEmail(email)
        if sent == True:
            flash('SENT, please check your e-mail.', 'success')
            return redirect(url_for('shop.forgetPassword'))
        else:
            flash('Email doesn\'t exist.', 'warning')
            return redirect(url_for('shop.forgetPassword'))
    return render_template("lost-password.html", form=resetForm )


#2 NEW PASSWORD PAGE
@shop.route('/new-password/<token>/', methods=['POST','GET'])
def newPassword(token):
    #CHECK TOKEN
    resultat = tokens.find_one({'_id': token})
    if resultat == None:
        flash('Token not found.', 'danger')
        return redirect(url_for('shop.forgetPassword'))
    
    elif resultat['date'] < date.today().strftime("%d/%m/%Y"):
        flash('Token expired.', 'danger')
        return redirect(url_for('shop.forgetPassword'))
    else:
        session["_id"] = resultat['client_id']
        newPasswordForm = NewPasswordForm()
        if newPasswordForm.validate_on_submit():
            pwd = newPasswordForm.password.data
            if setPassword(session["_id"], pwd):
                flash("Password Changed Successfully.","success")
                return redirect(url_for('shop.profile', _id = session['_id']))
            else:
                flash("Password didnt Change Please Contact us!","danger")
                return redirect(url_for('shop.profile', _id = session['_id']))
        return render_template("newPassword.html", form=newPasswordForm)

############################   FUNCTIONS   ####################################


#Set New Password Function
def setPassword(_id,pwd):
    try:
        update = clients.find_one_and_update({ "_id": _id },
                                              { "$set": {"password" : pwd}})
        return True
    except:
        return False    



#Set Token to Send, Function 
def setToken(email,_id):
    token_code = secrets.token_urlsafe()
    token_url = 'http://127.0.0.1:5000/shop/new-password/' + token_code +'/'
    token = {'_id'   : token_code,
              'token_url' : token_url,
              'date' : date.today().strftime("%d/%m/%Y"),
              'client_email' : email,
              'client_id' : _id
              }
    try :
        resultat = tokens.insert_one(token)
        return token
    except pymongo.errors.PyMongoError as e:
        return False


#Send Token By email 
def sendEmail(email):
    client = getClient('email',email)
    if client == False:
        return False
    token = setToken(email,client['_id'])
    if token == False:
        return False
    else:
        try:
            msg = MIMEMultipart('alternative')
            html = render_template("render_email.html", link=token['token_url'])
            msg['Subject'] = "Reset Password"
            msg['From']    = "dalyhachicha666@outlook.com"
            msg['To']      = email
            
            template = MIMEText(html, 'html')
            msg.attach(template)

            
            
            #SMTP CONNNECTION
            s = smtplib.SMTP('smtp-mail.outlook.com', 25)
            s.connect("smtp-mail.outlook.com",25)
            s.ehlo()
            s.starttls()
            s.login('dalyhachicha666@outlook.com', 'daly24077446')
            s.sendmail(msg['From'], msg['To'], msg.as_string())
            s.quit()
            return True
        except:
            return False


##############################################################################
############################   SELFIE   ######################################
##############################################################################
#Selfie Page   
@shop.route('/selfie/<_id>/', methods=['POST','GET'])
def selfie(_id):
    if authentificated(_id) == False:
        flash('You have to login first.','danger')
        return redirect(url_for('shop.login'))
    global frame
    if request.method == 'POST':
        if frame == []:
            flash('Try wait camera to load and detect your face','warning')
            return redirect(url_for('shop.selfie',_id=_id))
        picture = b64encode(frame).decode("utf-8")
        session['faceshape'] = face.classify_image(picture)
        if addClientPicture(picture,_id):
            session["logged_in"] = True
            session["_id"] = _id
            return redirect(url_for('shop.profile', _id = session["_id"]))
        else:
            flash('Server may be down.','danger')
            return redirect(url_for('shop.index'))
    elif request.method == 'GET':
        frame = []
        session.pop('faceshape', None)
        return render_template('selfie.html')

#Response with video feed (NOT A PAGE)
@shop.route('/video_feed')
def video_feed():
    return Response(gen(FaceMeshDetector()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


############################   FUNCTIONS   ####################################

#Generate camera feed Function
def gen(face_mesh):
    while True:
        global frame
        try:
            frame = face_mesh.get_frame()
            yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
        except:
            face_mesh = None
            return False

#Add Client Function
def addClientPicture(picture, _id):
    try :
        pictureData = {"picture" : picture,
                       "faceshape" : session["faceshape"]
                       }
        
        resultat = clients.find_one_and_update({ "_id": _id },
                                              { "$set": pictureData})
        return True
    except pymongo.errors.PyMongoError as e:
        return False

    

#############################################################################
###########################   ACCOUNT   #####################################
#############################################################################

#Account Page
@shop.route("/profile/<_id>/", methods=['POST','GET'])
def profile(_id):
    if authentificated(_id) == False:
        flash('You have to login first.','danger')
        return redirect(url_for('shop.login'))
    
    
    return render_template("shop_profile.html", _id=_id, data = getClientData(_id))

#Account Page
@shop.route("/myprofile/<_id>/", methods=['POST','GET'])
def myprofile(_id):
    profileSettingsForm = AccountSettingsForm()
    if authentificated(_id) == False:
        flash('You have to login first.','danger')
        return redirect(url_for('shop.login'))
    
    if profileSettingsForm.validate_on_submit():
        if updateClientData(profileSettingsForm,_id) == True:
            flash('Profile Updated.','success')
            return redirect(url_for('shop.myprofile',_id=_id))
        else:
            flash('Coudnt Update Profile !','danger')
            return redirect(url_for('shop.myprofile',_id=_id))
        
        
    client_data = getClientData(_id)

    
    return render_template("my-profile.html", _id=_id, data = client_data,form=profileSettingsForm)


@shop.route("/change-password/<_id>/", methods=['POST','GET'])
def changePasswordPage(_id):
    email = getClient('_id',_id,'email')
    if email == False:
        flash('Coudnt get your email! please contact us.', 'danger')
        return redirect(url_for('shop.myprofile',_id=_id))
    sent = sendEmail(email)
    if sent == True:
        flash('We sent an email, please check your e-mail inbox to change your Password.', 'success')
        return redirect(url_for('shop.myprofile',_id=_id))
    else:
        flash('Email didn\'t sent ! please contact us.', 'danger')
        return redirect(url_for('shop.myprofile',_id=_id))
    

def updateClientData(form,_id):
    client = clients.find_one({'_id': _id})
    new_data = {'name' : form.name.data,
                'birthday' : form.birthday.data,
                'phone' : form.phone.data,
                'nv_re' : form.nv_re.data,
                'nv_le' : form.nv_le.data,
                'fv_re' : form.fv_re.data,
                'fv_le' : form.fv_le.data,
                'address' : form.address.data,
                'glasses_type' : form.glasses_type.data,
                'update_date' : date.today().strftime("%d/%m/%Y")
                }
    try :
        resultat = clients.find_one_and_update({ "_id": _id },
                                                 { "$set": new_data})
        return True
    except pymongo.errors.PyMongoError as e:
        return False
##############################################################################
############################   Wishlist   ####################################
##############################################################################

#wishlist page
@shop.route("/wishlist/<_id>/", methods=['POST','GET'])
def wishlistPage(_id):
    if authentificated(_id) == False:
        flash('You have to login first.','danger')
        return redirect(url_for('shop.login'))
    
    wishlist = getWishlist(_id)
    if wishlist != None:
        products_list = getProductsList(wishlist)
    else:
        products_list = []
    
    return render_template("wishlist.html", _id=_id, products=products_list)





@shop.route("/delete_item_from_wishlist/<_id>/<p_id>/", methods=['POST','GET'])
def delete_item_from_wishlist(_id,p_id):
    wishlist = wishlists.find_one({'_id': _id})
    new_wishlist = {'product_ids': wishlist['product_ids'].replace(','+p_id, '')}
    try :
        resultat = wishlists.find_one_and_update({ "_id": _id },
                                                 { "$set": new_wishlist})
        flash('item removed from wishlist.','info')
        return redirect(url_for('shop.wishlistPage',_id=_id))
    except pymongo.errors.PyMongoError as e:
        flash("item didnt delete !",'danger')
        return redirect(url_for('shop.wishlistPage',_id=_id))
    
    return redirect(url_for('shop.wishlistPage',_id=_id))


@shop.route("/clearwishlist/<_id>/", methods=['POST','GET'])
def clearWishlist(_id):
    wishlists.find_one_and_delete({'_id': _id})
    return redirect(url_for('shop.wishlistPage',_id=_id))
    
def getWishlist(_id):
    wishlist = wishlists.find_one({'_id':_id})
    return wishlist


def getProductsList(wishlist):
    
    products_list = []
    if wishlist['product_ids'] == None:
        return None
    product_ids = wishlist['product_ids'].split(",")
    for product_id in product_ids:
        product = products.find_one({'_id': product_id})
        if product == None:
            pass
        else:
            products_list.append(product)
    
    return products_list

##############################################################################
############################   VOTE   ########################################
##############################################################################
@shop.route("/vote/", methods=['GET'])
@shop.route("/vote/<_id>/", methods=['GET'])
def votePage(_id=None):
    if _id != None:
        if authentificated(_id) == False:
            flash('You have to login first.','danger')
            return redirect(url_for('shop.login'))
        
    added = addVote(_id)
    if added == True:
        flash('Thank You For Liking This Project.','success')
        return redirect(url_for('shop.aboutPage'))
    else:
        flash('You Already Voted.','info')
        return redirect(url_for('shop.aboutPage'))

def addVote(_id):
    try:
        if _id == None:
            _id = 'GUEST#'+randStr(4)
            
            
        _vote = {'_id':_id,
                'date' : date.today().strftime("%d/%m/%Y"),
                'ip' : request.remote_addr
                }
        resultat = votes.insert_one(_vote)
        return True
    except pymongo.errors.PyMongoError as e:
        return False

##############################################################################
############################   PRODUCTS   ####################################
##############################################################################

@shop.route("/products/", methods=['POST','GET'])
@shop.route("/products/<_id>/", methods=['POST','GET'])
def productsPage(_id=None):
    if _id != None:
        if authentificated(_id) == False:
            flash('You have to login first.','danger')
            return redirect(url_for('shop.login'))

    list_products = getSomeProducts()
    return render_template("shop_products.html",_id=_id, products=list_products, VIProducts=getNProducts(2))



@shop.route("/product/<p_id>/", methods=['POST','GET'])
@shop.route("/product/<_id>/<p_id>/", methods=['POST','GET'])
def detailProduct(p_id,_id=None):
    if _id != None:
        if authentificated(_id) == False:
            flash('You have to login first.','danger')
            return redirect(url_for('shop.login'))

    return render_template('product-detail.html', _id = _id ,product = getProduct(p_id), other_products=getNProducts(10))

@shop.route("/addtowishlist/<_id>/<p_id>/", methods=['POST','GET'])
def addtowishlist(_id,p_id):
    if authentificated(_id) == False:
        flash('You have to login first.','danger')
        return redirect(url_for('shop.login'))
    
    wishlist = wishlists.find_one({'_id' : _id})
    if wishlist == None:
        CreateWishlist()
        wishlist = wishlists.find_one({'_id' : _id})

    new_product_ids = wishlist['product_ids'] + ',' + p_id
    wishlist['product_ids'] = new_product_ids
    try :
        resultat = wishlists.find_one_and_update({ "_id": _id },
                                                 { "$set": wishlist})
        flash('item added to wishlist.','success')
        return redirect(url_for('shop.detailProduct',p_id=p_id,_id=_id))
    except pymongo.errors.PyMongoError as e:
        flash("item didnt delete !",'danger')
        return redirect(url_for('shop.detailProduct',_id=_id,p_id=p_id))
    
    return redirect(url_for('shop.wishlistPage',_id=_id))


@shop.route("/show-all-products/", methods=['POST','GET'])
@shop.route("/show-all-products/<_id>/", methods=['POST','GET'])
def returnAllProducts(_id=None):
    list_products = products.find()
    if _id != None:
        if authentificated(_id) == False:
            flash('You have to login first.','danger')
            return redirect(url_for('shop.login'))
        
        return render_template("shop_products.html", _id=_id, products=list_products, other_products= getNProducts(30), VIProducts=getNProducts(2))
    else:
        return render_template("shop_products.html", products=list_products, other_products=getNProducts(30), VIProducts=getNProducts(2))
   


def getNProducts(n):
    product_list = products.find().limit(n)
    return product_list 
    
def getProduct(p_id):
    try:
        product = products.find_one({'_id':p_id})
        return product 
    except pymongo.errors.PyMongoError as e:
        return False
    
    
def getProductsByIds(product_ids):
    if len(product_ids) < 1:
        return None
    #GET PRODUCTS FROM CART (PRODUCT IDS)
    product_list = []
    for product_id in product_ids:
        product = getProduct(product_id)
        if product == None or product == False:
            pass
        else:
            product_list.append(product)
    return product_list
##############################################################################
############################   CART   ########################################
##############################################################################  
@shop.route("/cart/<_id>/", methods=['POST','GET'])
def cartPage(_id):
    if authentificated(_id) == False:
        flash('You have to login first.','danger')
        return redirect(url_for('shop.login'))
    
    global cart
    if request.method == 'POST':
        if cart == "" :
            return redirect(url_for('shop.cartPage', _id=_id))
        else:
            product_ids = cart.split(",")
            product_list = getProductsByIds(product_ids)
            sent = sendOrder(_id,request.form['notes'],product_list)
            if sent == True:
                flash('We recieved your order. Expect our confirmation email or message ','success')
                return redirect(url_for('shop.myOrdersPage',_id=_id))
            else:
                flash('Something went wrong! please contact us boring@support.com.','danger')
                return redirect(url_for('shop.cartPage', _id=_id))
    if cart == "" :
        return render_template('shop_cart.html', _id=_id, products = None)
    else:
        product_ids = cart.split(",")
        product_list = getProductsByIds(product_ids)
        return render_template('shop_cart.html', _id=_id, products = product_list, subtotal = getTotalPriceProducts(product_list))

def sendOrder(_id,notes,product_list):
    try:
        order = {'_id':randStr(8),
                 'id_client' : _id,
                 'payment_status' : 'not paid',
                 'order_total':getTotalPriceProducts(product_list),
                 'items_qte': len(product_list),
                 'status': 'pending',
                 'order_date': date.today().strftime("%d/%m/%Y"),
                 'worker_id': 'SHOP',
                 'notes': notes
                 }
        resultat = orders.insert_one(order)
        return True
    except pymongo.errors.PyMongoError as e:
        return False
        
@shop.route("/addtocart/<_id>/<p_id>/", methods=['POST','GET'])
def addtocart(_id,p_id):
    global cart
    if authentificated(_id) == False:
        flash('You have to login first.','info')
        return redirect(url_for('shop.login'))
    
    cart = cart + p_id + ','
    flash('Item added to cart','success')
    return redirect(url_for('shop.detailProduct',_id=_id, p_id=p_id))

@shop.route("/clearcart/", methods=['POST','GET'])
def clearCart():
    global cart 
    cart = ","
    return redirect(url_for('shop.cartPage',_id=session["_id"]))

@shop.route("/deletefromcart/<p_id>/")
def delete_item_from_cart(p_id):
    global cart
    cart = cart.replace(p_id+',', '')
    return redirect(url_for('shop.cartPage',_id = session["_id"] ))



def getTotalPriceProducts(product_list):
    total = 0
    for product in product_list:
        total += float(product['price'])
    return total
        
