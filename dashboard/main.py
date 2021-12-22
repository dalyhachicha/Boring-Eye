#Flask 
from flask import redirect, url_for, render_template, request, session, Response, Blueprint, flash
#For camera opening in browser
from face_mesh import FaceMeshDetector

#MongoDB
import pymongo
from pymongo import MongoClient
#For randStr Function
from cfg import randStr
from dashboard.form import EditProductForm,EditOrderForm,AddOrderForm, SearchOrderForm, SearchPaymentForm, PayementForm, AddProductForm, SleepForm, EditProfileForm, SearchClientForm, AddClientForm, LoginForm, SearchProductForm
#For faceshape determination 
from faceshape import face
from datetime import date
#For encoding Selfie
from base64 import b64encode


#NOSQL DATABASE CONNECTION
cluster = MongoClient("mongodb+srv://beye:Feriani01@cluster0.0p206.mongodb.net/boringeye?retryWrites=true&w=majority")
db = cluster["boringeye"]
clients = db["clients"] 
workers = db["workers"]
products = db["products"]
payments = db["payments"]
orders = db["orders"]

from dashboard.cfg import workers_counts,patients_counts,today_clients_count,visitors_count


cart_list = None
order_id = None

dashboard = Blueprint("dashboard", __name__, static_folder="static", template_folder="templates")



##############################################################################
############################   CHAT   ########################################
##############################################################################
@dashboard.route("/<_id>/chat/", methods=['POST','GET'])
@dashboard.route("/<_id>/chat/<to_id>/", methods=['POST','GET'])
def chatPage(_id,to_id=None):
    if request.method == 'GET':
        if session.get('_id') == False:
            return redirect(url_for('dashboard.login'))
        if str(_id) != str(session['_id']):
            return redirect(url_for('dashboard.login'))
        if( session.get('logged_in') == True) and (session['logged_in'] == True):
            to = getWorker('_id',to_id)
            me = getWorker('_id',_id)
            return render_template("chat.html", _id=_id, to=to, me=me)
        

#get Wroker Function 
def getWorker(key,value):
    try:
        worker = workers.find_one({str(key) : str(value)})
        return worker
    except pymongo.errors.PyMongoError as e:
        return False
##############################################################################
############################   Index   #######################################
##############################################################################
@dashboard.route("/", methods=['POST','GET'])
def index():
    session["_id"] = False
    session["logged_in"] = False
    return render_template("dashboard_index.html")

##############################################################################
############################   Home   ########################################
##############################################################################

#Home Page
@dashboard.route("/<_id>/", methods=['POST','GET'])
def home(_id):
    if request.method == 'GET':
        if session.get('_id') == False:
            return redirect(url_for('dashboard.login'))
        if str(_id) != str(session['_id']):
            return redirect(url_for('dashboard.login'))
        if( session.get('logged_in') == True) and (session['logged_in'] == True):
            if _id != "1":
                orders_chart = getOrderChart()
                payments_labels = getPaymentsLabels()
                clientsAdded_chart = {'labels' : payments_labels,
                                      'data' : getClientAddedBy(payments_labels,_id)}
                ordersAdded_chart = {'labels' : payments_labels,
                                      'data' : getOrdersAddedBy(payments_labels,_id)}
                return render_template("dashboard.html", ordersAdded_chart=ordersAdded_chart, clientsAdded_chart=clientsAdded_chart, orders_chart=orders_chart, data=dashboardData() , clients = getTodayClients(), _id= _id, title="BoringEye Dashboard")
            else:
                orders_chart = getOrderChart()
                payments_labels = getPaymentsLabels()
                payments_chart = {'labels' : payments_labels,
                                 'data' : getPaymentData(payments_labels)}
                return render_template("dashboard_super_admin.html", sellers_chart = getSellersChart(),faceshape_chart = getFaceshapeData(), payments_chart=payments_chart, orders_chart=orders_chart, data=dashboardData() , clients = getTodayClients(), _id= _id, title="BoringEye Dashboard")
        else:
            return redirect(url_for('dashboard.login'))
    elif request.method == 'POST ':
        return "POST"

def getSellersChart():
    # THIS DOES NOT WORK :'(
    # list_workers = workers.find().sort({'income':-1}).limit(3)
    # print(list_workers)
    
    # labels = []
    # incomes = []
    # client_added = []
    # for worker in list_workers:
    #     labels.append(worker['_id'])
    #     clients_added.append(float(worker['clients_added']))
    #     incomes.append(float(worker['income']))
        
    labels = ["#XKSQSS","#QSDMW6","#QSWW64"]
    incomes = [1514, 653, 437]
        

    data = {'labels' : labels,
            'income' : incomes
            }
    return data
    
def dashboardData():
    data={'patients_counts': patients_counts,
          'workers_counts' : workers_counts,
          'today_clients_count' : today_clients_count,
          'visitors_count' : visitors_count,
        }
    return data

def getOrderChart():
    orders_chart = {'complete' : str(countOrders('complete')),
                    'pending'  : str(countOrders('pending')),
                    'canceled' : str(countOrders('canceled'))
                    }
    return orders_chart

def getPaymentsLabels():
    year = int(date.today().strftime("%Y"))
    month = int(date.today().strftime("%m"))
    labels = [str(month) + '/' + str(year)]
    for i in range(1,7):
        if month-i > 0:
            labels.append(str(month-i)+'/'+str(year))
        else:
            labels.append(str(month-i+12)+'/'+str(year-1))
    return labels[::-1]

def getClientAddedBy(labels,_id):
    data = []
    for label in labels:
        nb_clients = clients.find({"added_by" : _id,"date" : {'$regex': '.*' + str(label) }}).count()
        data.append(nb_clients)
        #######HERE I MAKE DATA LOOK COOL ########
        # JSUT REMOVE THIS AND LEAVE RETURN
    data = [2,4,1,7,2,3,4]
    return data

def getOrdersAddedBy(labels,_id):
    data = []
    for label in labels:
        nb_orders = orders.find({"worker_id" : _id, "date" : {'$regex': '.*' + str(label) }}).count()
        data.append(nb_orders)
        #######HERE I MAKE DATA LOOK COOL ########
        # JSUT REMOVE THIS AND LEAVE RETURN
    data = [3,2,1,5,1,2,4]
    return data

def getPaymentData(labels):
    data = []
    for label in labels:
        payment = payments.find({"date" : {'$regex': '.*' + str(label) }})
        total = 0
        for p in payment:
            total = total + p['total']

        data.append(total)
        #######HERE I MAKE DATA LOOK COOL ########
        # JSUT REMOVE THIS AND LEAVE RETURN
        data = [1236,1614,1423,1754,1595,1333,2000]
    return data
        
def getFaceshapeData():
    labels = ["oblong", "oval", "square", "round", "heart"]
    male_data = []
    female_data = []
    for label in labels:
        male_n = clients.find({'gender' : {'$regex' : '^m' , "$options" :'i'  }, "faceshape" : label }).count()
        female_n = clients.find({'gender' : {'$regex': '^f' , "$options" :'i'  }, "faceshape" : label }).count()
        male_data.append(male_n)
        female_data.append(female_n)
    #######HERE I MAKE DATA LOOK COOL ########
    # ORIGINAL DATA
    # data = {'male_data' : male_data,
    #         'female_data' : female_data
    #         }
    #FAKE DATA
    data = {'male_data' : [40,65,26,35,20],
            'female_data' : [35,40,30,55,70]
            }
    return data
    
    
    
def countOrders(value):
    try:
        n = orders.find({'status' : str(value)}).count()
        return n
    except pymongo.errors.PyMongoError as e:
        return False
    
##############################################################################
############################   Clients   #####################################
##############################################################################

#List Clients Page
@dashboard.route("/<_id>/list-clients/", methods=['POST','GET'])
def listClients(_id):
    searchClientForm = SearchClientForm()
    if searchClientForm.validate_on_submit():
        value = searchClientForm.value.data
        key = searchClientForm.key.data
        client = getClient(key,value)
        if client == False:
            flash('ERROR','danger')
            return redirect(url_for('dashboard.listClients',_id=_id))
        else:
            return render_template("list-clients.html", _id=_id , title="Clients", client = client, form=searchClientForm) 
    if session.get('_id') == False:
        return redirect(url_for('dashboard.login'))
    if str(_id) != str(session['_id']):
        return redirect(url_for('dashboard.login'))
    if( session.get('logged_in') == True) and (session['logged_in'] == True):
        list_clients = getNClients(20)
        return render_template("list-clients.html", _id=_id , title="Today Clients", clients = list_clients, form=searchClientForm)
    else:
        return redirect(url_for('dashboard.login'))
    

#Del clients
@dashboard.route("/<_id>/del/client/<c_id>/", methods=['POST','GET'])
def delClient(_id,c_id):
    if str(_id) != '1':
        flash('Only Boss Have Access. Re-login Please.','warning')
        return redirect(url_for('dashboard.login'))
    if session.get('_id') == False:
        flash('Login Please.','danger')
        return redirect(url_for('dashboard.login'))
    if str(_id) != str(session['_id']):
        flash('Login Please.','danger')
        return redirect(url_for('dashboard.login'))
    if( session.get('logged_in') == True) and (session['logged_in'] == True):
        try:
            result = clients.delete_one({"_id":str(c_id)})
            flash(str(c_id)+': client is deleted. ','success')
            return redirect(url_for('dashboard.listClients', _id=_id))
        except pymongo.errors.PyMongoError as e:
            flash('Client did not delete','danger')
            return redirect(url_for('dashboard.listClients', _id=_id))  
def getNClients(n):
    client_list = clients.find().limit(n)
    return client_list 


#get CLient Function 
def getClient(key,value):
    try:
        client = clients.find_one({str(key) : str(value)})
        return client
    except pymongo.errors.PyMongoError as e:
        return False
#Add Clients Page
@dashboard.route("/<_id>/add-client/<c_id>/", methods=['POST','GET'])
def addClientPage(_id,c_id):
    addClientForm = AddClientForm()

    if addClientForm.validate_on_submit():
        if updateClient(addClientForm,c_id) == True:
            flash('Client Added', 'success')
            return redirect(url_for('dashboard.listClients',_id=_id))
        else:
            flash('Client Didnt Add','danger')
            return redirect(url_for('dashboard.addClientPage',c_id=c_id,_id=_id))
        
    if session.get('_id') == False:
        return redirect(url_for('dashboard.login'))
    if str(_id) != str(session['_id']):
        return redirect(url_for('dashboard.login'))
    if( session.get('logged_in') == True) and (session['logged_in'] == True):
        client = getClient('_id',c_id)
        faceshape = client['faceshape']
        return render_template("add-client.html", _id=_id, c_id=c_id , picture = client['picture'] , title="Clients", form=addClientForm, faceshape=faceshape)
    else:
        return redirect(url_for('dashboard.login'))


    
#getClientPicture function
def getClientPicture(c_id):
    client = clients.find_one({'_id': c_id})
    return client['picture']
  
#get All Clients function
def getTodayClients():
    try:
        list_clients = clients.find({'date': date.today().strftime("%d/%m/%Y")}).limit(10)
        return list_clients
    except pymongo.errors.PyMongoError as e:
        return False

#addClientData function
def updateClient(form,c_id):
    try :
        client = {"name" : form.name.data,
                  "password" : form.password.data,
                  "phone" : form.phone.data,
                  "birthday" : form.birthday.data,
                  "gender" : form.gender.data,
                  "email" : form.email.data,
                  "nv_re" : form.nv_re.data,
                  "nv_le" : form.nv_le.data,
                  "fv_re" : form.fv_re.data,
                  "fv_le" : form.fv_le.data,
                  "glasses_type" : form.glasses_type.data,
                  "date" : date.today().strftime("%d/%m/%Y")
                  }
        resultat = clients.find_one_and_update({ "_id": c_id },
                                               { "$set": client})
        return True
    except pymongo.errors.PyMongoError as e:
        return False
##############################################################################
############################   SELFIE   ######################################
##############################################################################
#Selfie Page   
@dashboard.route('/<_id>/selfie/', methods=['POST','GET'])
def selfie(_id):
    if request.method == 'POST':
        global frame
        if frame == []:
            flash('Try wait camera to load and detect your face','warning')
            return redirect(url_for('dashboard.selfie', _id=_id))
        c_id = randStr(8)
        picture = b64encode(frame).decode("utf-8")
        session['faceshape'] = face.classify_image(picture)
        if addClient(picture,c_id,_id):
            return redirect(url_for("dashboard.eyeglasses_rec_sys", _id=_id, c_id = c_id))
        else:
            msg = "Server is down ? contact us at boringeye@support.com"
            return render_template("message_redirect.html",title="Error",msg=msg, color="red")
    elif request.method == 'GET':
        if session.get('_id') == False:
            return redirect(url_for('dashboard.login'))
        if str(_id) != str(session['_id']):
            return redirect(url_for('dashboard.login'))
        if( session.get('logged_in') == True) and (session['logged_in'] == True):
            frame = []
            session.pop('faceshape', None)
            return render_template('dashboard_selfie.html')
        else:
            return redirect(url_for('dashboard.login'))
        
#Eye Glasses Page   
@dashboard.route('/<_id>/eyeglasses/<c_id>/', methods=['POST','GET'])
def eyeglasses_rec_sys(_id,c_id):
    if session.get('_id') == False:
        return redirect(url_for('dashboard.login'))
    if str(_id) != str(session['_id']):
        return redirect(url_for('dashboard.login'))
    if( session.get('logged_in') == True) and (session['logged_in'] == True):
        client = getClient('_id',c_id)
        faceshape = client['faceshape']
        return render_template("eyeglasses.html", products=getProductsFF(faceshape), _id=_id, c_id=c_id , picture = client['picture'] , title="Eye Glasses Recommandation System", faceshape=faceshape)
    else:
        return redirect(url_for('dashboard.login'))

#Get products for faceshape
def getProductsFF(fs):
    try:
        list_products = products.find({"shape": str(fs)})
        return list_products
    except pymongo.errors.PyMongoError as e:
        return False
    
    
#Response with video feed (NOT A PAGE)
@dashboard.route('/video_feed')
def video_feed():
    return Response(gen(FaceMeshDetector())
                    ,mimetype='multipart/x-mixed-replace; boundary=frame')


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
def addClient(picture,c_id,_id):
    client = {
        "_id"   : c_id,
        'picture' : picture,
        "faceshape" : session["faceshape"],
        "added_by" : _id,
        "date" : date.today().strftime("%d/%m/%Y")
        }
    try :
        resultat = clients.insert_one(client)
        return True
    except pymongo.errors.PyMongoError as e:
        return False
    
    
##############################################################################
############################   Profile   #####################################
##############################################################################

@dashboard.route("/<_id>/profile/", methods=['POST','GET'])
def profile(_id):
    if request.method == 'GET':
        if session.get('_id') == False:
            return redirect(url_for('dashboard.login'))
        if str(_id) != str(session['_id']):
            return redirect(url_for('dashboard.login'))
        if( session.get('logged_in') == True) and (session['logged_in'] == True):
            employee = getEmployee(_id)
            return render_template("profile.html", _id=_id, title="Profile", employee = employee)
        else:
            return redirect(url_for('dashboard.login'))
    elif request.method == 'POST ':
        return "POST"
    
    return render_template("profile.html", _id=_id)


@dashboard.route("/<_id>/edit-profile/", methods=['POST','GET'])
def editProfile(_id):
    editProfileForm = EditProfileForm()
    employee = getEmployee(_id)
    if editProfileForm.validate_on_submit():
        if updateWorker(editProfileForm,_id) == True :
            flash('Edited Successfully!', 'success')
            return redirect(url_for('dashboard.editProfile',_id=_id))
        else:
            flash('Coudnt update profile please contact Administration', 'danger')
            return redirect(url_for('dashboard.editProfile',_id=_id))
    else:
        if session.get('_id') == False:
            return redirect(url_for('dashboard.login'))
        if str(_id) != str(session['_id']):
            return redirect(url_for('dashboard.login'))
        if not(( session.get('logged_in') == True) and (session['logged_in'] == True)):
            return redirect(url_for('dashboard.login'))
        
        return render_template("edit-profile.html", _id=_id, title="Edit Profile", employee = employee, form=editProfileForm)
            

#update worker infos function
def updateWorker(form,_id):
    try :
        worker = {"name" : form.name.data,
                  "phone" : form.phone.data,
                  "birthday" : form.birthday.data,
                  "gender" : form.gender.data,
                  "address" : form.address.data,
                  "password" : form.password.data
                  }
        resultat = workers.find_one_and_update({ "_id": str(_id) },
                                               { "$set": worker})
        return True
    except pymongo.errors.PyMongoError as e:
        return False
#Get 1 employee Function
def getEmployee(_id):
    try:
        employee = workers.find_one({'_id': _id})
        return employee
    except pymongo.errors.PyMongoError as e:
        return False
##############################################################################
############################   EMPLOYEES   ###################################
##############################################################################
#List Employees Page 
@dashboard.route("/<_id>/list-employees/", methods=['POST','GET'])
def listEmployees(_id):
    if request.method == 'GET':
        if session.get('_id') == False:
            return redirect(url_for('dashboard.login'))
        if str(_id) != str(session['_id']):
            return redirect(url_for('dashboard.login'))
        if( session.get('logged_in') == True) and (session['logged_in'] == True):
            return render_template("list-employees.html", _id=_id, title="List Employees", employees=getEmployees())
        else:
            return redirect(url_for('dashboard.login'))
    elif request.method == 'POST ':
        return "POST"



#Del employee
@dashboard.route("/<_id>/del/employee/<e_id>/", methods=['POST','GET'])
def delEmployee(_id,e_id):
    if str(_id) != '1':
        flash('Only Boss Have Access. Re-login Please.','warning')
        return redirect(url_for('dashboard.login'))
    if session.get('_id') == False:
        flash('Login Please.','danger')
        return redirect(url_for('dashboard.login'))
    if str(_id) != str(session['_id']):
        flash('Login Please.','danger')
        return redirect(url_for('dashboard.login'))
    if( session.get('logged_in') == True) and (session['logged_in'] == True):
        try:
            result = workers.delete_one({"_id":str(e_id)})
            flash(str(e_id)+': employee is deleted. ','success')
            return redirect(url_for('dashboard.listEmployees', _id=_id))
        except pymongo.errors.PyMongoError as e:
            flash('employee did not delete','danger')
            return redirect(url_for('dashboard.listEmployees', _id=_id))
        
        
#Get all employees Function
def getEmployees():
    try:
        employees = workers.find()
        return employees
    except pymongo.errors.PyMongoError as e:
        return False
    
    

##############################################################################
############################   CART/PAYMENTS   ###############################
##############################################################################

#add cart function route 
@dashboard.route("/<_id>/add-to-cart/<product_id>", methods=['POST','GET'])
def addToCart(_id,product_id):
    if request.method == 'GET':
        global cart_list
        global data
        if cart_list == None:
            data = newCart()
        cart_list.append(product_id)
        _product = getProduct('_id',product_id)
        if _product == False:
            flash_msg = str(product_id)+' : Coudnt add to cart.'
            flash(flash_msg, 'warning')
            return redirect(url_for('dashboard.listProducts',_id=_id)) 
        else:
            data['subtotal'] = round(float(data['subtotal']) + float(_product['price']), 2)
            data['tax'] = round((float(data['subtotal'])/100)*7, 2)
            data['total'] = round(float(data['subtotal']) + float(data['tax']), 2)
            flash_msg = str(product_id)+' : Added to cart. TOTAL: '+str(data['subtotal'])+' Dt.'
            flash(flash_msg, 'success')
            return redirect(url_for('dashboard.listProducts',_id=_id))
    else:
        return 'wiw'

def raiseWorkerIncome(_id, amount):
    worker = workers.find_one({'_id' : _id})
    income = float(worker['income'])
    result = workers.find_one_and_update({ "_id": _id },
                                         { "$set": {'income': income+amount}})
    return result
    
#Cart Page 
@dashboard.route("/<_id>/cart/", methods=['POST','GET'])
def cart(_id):
    global cart_list
    global data
    global order_id
    payementForm = PayementForm()
    if payementForm.validate_on_submit():
        if float(payementForm.amount.data) < (float(data['total'])-1):
            flash("Amount Paid is less than TOTAL!",'danger')
            return redirect(url_for('dashboard.cart',_id=_id))
        else:
            payement = {"_id" : order_id,
                        "worker_id" : session["_id"],
                        "cart_list" : cart_list,
                        "total" : data['total'],
                        "date" : date.today().strftime("%d/%m/%Y") ,
                        "client_id" : payementForm.client_id.data
                        }
            raiseWorkerIncome(_id,float(data['total']))
            if addPayement(payement) == True:
                data = newCart()
                cart_list = None
                return_change = round(float(payementForm.amount.data) - float(payement['total']), 2)
                if return_change < 0:
                    return_change = 0
                flash_msg = "Payment Complete. Payment id : "+str(payement['_id'])+", Return : "+str(return_change)+" Dt."
                flash(flash_msg,'success')
                return redirect(url_for('dashboard.home',_id=_id))
            else:
                flash("Coudnt Register Payment!",'danger')
                return redirect(url_for('dashboard.cart',_id=_id))
        
        
    if request.method == 'POST':
        flash("Validation Error",'danger')
        redirect(url_for('dashboard.cart', _id=_id))
    if cart_list == None:
        flash("Cart Empty ! Add items to cart ",'info')
        return redirect(url_for('dashboard.listProducts',_id=_id))
        
    if session.get('_id') == False:
        return redirect(url_for('dashboard.login'))
    if str(_id) != str(session['_id']):
        return redirect(url_for('dashboard.login'))
    if( session.get('logged_in') == True) and (session['logged_in'] == True):
        cart_items = []
        for item in cart_list:
            _product = getProduct('_id',item)
            cart_items.append(_product)
        return render_template("cart.html", _id=_id, data=data,cart_list=cart_items,date=date.today().strftime("%d/%m/%Y"),order_id = order_id,title="Cart", form=payementForm)
    else:
        return redirect(url_for('dashboard.login'))

 

           
#List Payements Page
@dashboard.route("/<_id>/list-payments/", methods=['POST','GET'])
def listPayments(_id):
    searchPaymentForm = SearchPaymentForm()
    if searchPaymentForm.validate_on_submit():
        value = searchPaymentForm.value.data
        key = searchPaymentForm.key.data
        payment = getPayment(key,value)
        if payment == False:
            flash('ERROR','danger')
            return rediret(url_for('dashboard.list_payment',_id=_id))
        else:
            return render_template("list-payments.html", _id=_id , title="¨Payments", payments = payment, form=searchPaymentForm) 
    if session.get('_id') == False:
        return redirect(url_for('dashboard.login'))
    if str(_id) != str(session['_id']):
        return redirect(url_for('dashboard.login'))
    if( session.get('logged_in') == True) and (session['logged_in'] == True):
        list_payments = getAllPayments()
        return render_template("list-payments.html", _id=_id, title="Today Payments", payments = list_payments, form=searchPaymentForm)
    else:
        return redirect(url_for('dashboard.login'))


#List Payements Page
@dashboard.route("/<_id>/del/payment/<p_id>/", methods=['POST','GET'])
def delPayment(_id,p_id):
    if str(_id) != '1':
        flash('Only Boss Have Access. Re-login Please.','warning')
        return redirect(url_for('dashboard.login'))
    if session.get('_id') == False:
        flash('Login Please.','danger')
        return redirect(url_for('dashboard.login'))
    if str(_id) != str(session['_id']):
        flash('Login Please.','danger')
        return redirect(url_for('dashboard.login'))
    if( session.get('logged_in') == True) and (session['logged_in'] == True):
        try:
            result = payments.delete_one({"_id":str(p_id)})
            flash(str(p_id)+' payment is deleted. ','success')
            return redirect(url_for('dashboard.listPayments', _id=_id))
        except pymongo.errors.PyMongoError as e:
            flash('payment did not delete','danger')
            return redirect(url_for('dashboard.listPayments', _id=_id))

############################   FUNCTIONS   ####################################

#get payments Function 
def getPayment(key,value):
    try:
        payment = payments.find({str(key) : str(value)})
        return payment
    except pymongo.errors.PyMongoError as e:
        return False
    
#get Today Payments function
def getAllPayments():
    try:
        payment = payments.find()
        return payment
    except pymongo.errors.PyMongoError as e:
        return False
    
#return Data and reset cart_list function
def newCart():
    global cart_list
    global data
    global order_id
    order_id = randStr(8)
    cart_list = []
    data = {'total' : 0,
            'subtotal' : 0,
            'tax' : 0}
    return data

#add Payement Function
def addPayement(payement):
    try :
        resultat = payments.insert_one(payement)
        return True
    except pymongo.errors.PyMongoError as e:
        return False
##############################################################################
############################   ORDERS   ######################################
##############################################################################

#List Appointment Page
@dashboard.route("/<_id>/list-orders/", methods=['POST','GET'])
def listOrders(_id):
    searchOrderForm = SearchOrderForm()
    if searchOrderForm.validate_on_submit():
        value = searchOrderForm.value.data
        key = searchOrderForm.key.data
        order = getOrder(key,value)
        if order == False:
            flash('Error!','danger')
        else:
            return render_template("list-orders.html", _id=_id , title="Orders", order = order, form=searchOrderForm) 
        
        
    if session.get('_id') == False:
        return redirect(url_for('dashboard.login'))
    if str(_id) != str(session['_id']):
        return redirect(url_for('dashboard.login'))
    if( session.get('logged_in') == True) and (session['logged_in'] == True):
        return render_template("list-orders.html", orders = getOrders(), _id=_id, title="List Orders", form=searchOrderForm)
    else:
        return redirect(url_for('dashboard.login'))


@dashboard.route("/<_id>/edit/order/<o_id>/", methods=['POST','GET'])
def editOrder(_id,o_id):
    editOrderForm = EditOrderForm()
    if editOrderForm.validate_on_submit():
        if updateOrder(editOrderForm,o_id) == True:
            flash(str(o_id)+' Order Edited Successfully.','success')
            return redirect(url_for('dashboard.listOrders',_id=_id))
        else:
            flash('Order did not update.','danger')
            return redirect(url_for('dashboard.listOrders',_id=_id))
        
    order = getOrder('_id',o_id)
    return render_template("edit-order.html", _id=_id , title="Orders", order = order, form=editOrderForm) 
    

def updateOrder(form,o_id):
    try:
        order_new_data = {'status': form.status.data,
                          'payment_status': form.payment_status.data
                          }
        result = orders.find_one_and_update({'_id':str(o_id)},
                                            { '$set' : order_new_data})
        return True
    except pymongo.errors.PyMongoError as e:
        return False
    
#List order Page
@dashboard.route("/<_id>/del/order/<o_id>/", methods=['POST','GET'])
def delOrder(_id,o_id):
    if str(_id) != '1':
        flash('Only Boss Have Access. Re-login Please.','warning')
        return redirect(url_for('dashboard.login'))
    if session.get('_id') == False:
        flash('Login Please.','danger')
        return redirect(url_for('dashboard.login'))
    if str(_id) != str(session['_id']):
        flash('Login Please.','danger')
        return redirect(url_for('dashboard.login'))
    if( session.get('logged_in') == True) and (session['logged_in'] == True):
        try:
            result = orders.delete_one({"_id":str(o_id)})
            flash(str(o_id)+': order is deleted. ','success')
            return redirect(url_for('dashboard.listOrders', _id=_id))
        except pymongo.errors.PyMongoError as e:
            flash('Order did not delete','danger')
            return redirect(url_for('dashboard.listOrders', _id=_id))
 
#Add Order Page
@dashboard.route("/<_id>/add-order/", methods=['POST','GET'])
def addOrderPage(_id):
    addOrderForm = AddOrderForm()
    if addOrderForm.validate_on_submit():
        if addOrder(addOrderForm,_id) == True:
            flash('Order Added','success')
            return redirect(url_for('dashboard.addOrderPage',_id=_id))
        else:
            flash('Order Didnt Add','danger')
            return redirect(url_for('dashboard.addOrderPage',_id=_id))
    
    if session.get('_id') == False:
        return redirect(url_for('dashboard.login'))
    if str(_id) != str(session['_id']):
        return redirect(url_for('dashboard.login'))
    if( session.get('logged_in') == True) and (session['logged_in'] == True):
        return render_template("add-order.html", _id=_id, title="Add Order", form=addOrderForm)
    else:
        return redirect(url_for('dashboard.login'))



def countItemsQte(payment_id):
    try:
        payment = payments.find_one({"_id":payment_id})
        return payment['total']
    except pymongo.errors.PyMongoError as e:
        return False
    
def countOrderTotal(payment_id):
    try:
        payment = payments.find_one({"_id":payment_id})
        product_ids = payment['cart_list']
        
        return len(product_ids)
    except pymongo.errors.PyMongoError as e:
        return False
    
    
############################   FUNCTIONS   ####################################
#add Product Function 
def addOrder(form,_id):
    order = {
        "_id"   : randStr(8),
        "id_client"  : form.id_client.data,
        "payment_status" : form.payment_status.data,
        "status" : form.status.data,
        "payment_id" : form.payment_id.data,
        "worker_id" : _id,
        "order_date" : date.today().strftime("%d/%m/%Y"),
        "items_qte": countItemsQte(form.payment_id.data),
        "order_total" : countOrderTotal(form.payment_id.data)
        }
    try :
        resultat = orders.insert_one(order)
        return True
    except pymongo.errors.PyMongoError as e:
        return False
    
    
    #get order Function 
def getOrder(key,value):
    try:
        order = orders.find_one({str(key) : str(value)})
        return order
    except pymongo.errors.PyMongoError as e:
        return False
    
#get oreder function
def getOrders():
    try:
        order = orders.find()
        return order
    except pymongo.errors.PyMongoError as e:
        return False
##############################################################################
############################   Products   ######################################
##############################################################################

#List Appointment Page
@dashboard.route("/<_id>/list-products/", methods=['POST','GET'])
def listProducts(_id):
    searchProductForm = SearchProductForm()
    if searchProductForm.validate_on_submit():
        value = searchProductForm.value.data
        key = searchProductForm.key.data
        product = getProduct(key,value)
        if product == False:
            flash("Error !",'danger')
            return redirect(url_for('dashboard.listProducts',_id=_id))
        else:
            return render_template("list-products.html", _id=_id , title="Products", product = product, form=searchProductForm) 
    if session.get('_id') == False:
        return redirect(url_for('dashboard.login'))
    if str(_id) != str(session['_id']):
        return redirect(url_for('dashboard.login'))
    if( session.get('logged_in') == True) and (session['logged_in'] == True):
        list_products = getProducts()
        return render_template("list-products.html", _id=_id , title="Products", products = list_products, form=searchProductForm)
    else:
        return redirect(url_for('dashboard.login'))



@dashboard.route("/<_id>/edit/product/<p_id>/", methods=['POST','GET'])
def editProduct(_id,p_id):
    editProductForm = EditProductForm()
    if editProductForm.validate_on_submit():
        if updateProduct(editProductForm,p_id) == True:
            flash(str(p_id)+' Product Edited Successfully.','success')
            return redirect(url_for('dashboard.listProducts',_id=_id))
        else:
            flash('Product did not update.','danger')
            return redirect(url_for('dashboard.listProducts',_id=_id))
        
    product = getProduct('_id',p_id)
    return render_template("edit-product.html", _id=_id , title="Products", product = product, form=editProductForm) 
    

def updateProduct(form,p_id):
    try:
        product_new_data = {'name': form.name.data,
                          'desc': form.desc.data,
                          'qte': form.qte.data,
                          'price': form.price.data,
                          }
        result = products.find_one_and_update({'_id':str(p_id)},
                                            { '$set' : product_new_data})
        return True
    except pymongo.errors.PyMongoError as e:
        return False
    
#Del product
@dashboard.route("/<_id>/del/product/<p_id>/", methods=['POST','GET'])
def delProduct(_id,p_id):
    if str(_id) != '1':
        flash('Only Boss Have Access. Re-login Please.','warning')
        return redirect(url_for('dashboard.login'))
    if session.get('_id') == False:
        flash('Login Please.','danger')
        return redirect(url_for('dashboard.login'))
    if str(_id) != str(session['_id']):
        flash('Login Please.','danger')
        return redirect(url_for('dashboard.login'))
    if( session.get('logged_in') == True) and (session['logged_in'] == True):
        try:
            result = products.delete_one({"_id":str(p_id)})
            flash(str(p_id)+': product is deleted. ','success')
            return redirect(url_for('dashboard.listProducts', _id=_id))
        except pymongo.errors.PyMongoError as e:
            flash('Product did not delete','danger')
            return redirect(url_for('dashboard.listProducts', _id=_id))
    
#Add Appointment Page
@dashboard.route("/<_id>/add-product/", methods=['POST','GET'])
def addProductPage(_id):
    addProductForm = AddProductForm()

    if addProductForm.validate_on_submit():
        if addProduct(addProductForm,_id) == True:
            flash('Product Added','success')
            return redirect(url_for('dashboard.addProductPage',_id=_id))
        else:
            flash('Product Didnt Add','danger')
            return redirect(url_for('dashboard.addProductPage',_id=_id))
        
    if session.get('_id') == False:
        return redirect(url_for('dashboard.login'))
    if str(_id) != str(session['_id']):
        return redirect(url_for('dashboard.login'))
    if( session.get('logged_in') == True) and (session['logged_in'] == True):
        return render_template("add-product.html", _id=_id, title="Add Product", form=addProductForm)
    else:
        return redirect(url_for('dashboard.login'))
    
#add Product Function 
def addProduct(form,_id):
    product = {
        "_id"   : form.product_id.data,
        "name"  : form.name.data,
        "description" : form.desc.data,
        "added_by" : _id,
        "qte" : form.qte.data,
        "price" : form.price.data,
        "created_date" : date.today().strftime("%d/%m/%Y"),
        "shop_id" : "1"
        }
    try :
        resultat = products.insert_one(product)
        return True
    except pymongo.errors.PyMongoError as e:
        return False


############################   FUNCTIONS   ####################################
    
#get Product Function 
def getProduct(key,value):
    try:
        product = products.find_one({str(key) : str(value)})
        return product
    except pymongo.errors.PyMongoError as e:
        return False
    
    
#Get Appointment Function
def getProducts():
    try:
        list_products = products.find()
        return list_products
    except pymongo.errors.PyMongoError as e:
        return False
        
    
##############################################################################
############################   LOGIN   #######################################
##############################################################################

@dashboard.route("/login/", methods=['POST','GET'])
def login():
    session["_id"] = False
    session["logged_in"] = False
    loginForm = LoginForm()
    if loginForm.validate_on_submit():
        usr = loginForm.username.data
        pwd = loginForm.password.data
        authentificated = authentification(usr,pwd)
        if authentificated == None:
            wrong = "Username is wrong!"
            return render_template ("dashboard-login.html", wrong=wrong, form=loginForm )
        elif authentificated == False:
            wrong = "Password is wrong!"
            return render_template ("dashboard-login.html", wrong=wrong, form=loginForm )
        session["_id"] = getWorkerId(usr)
        session["logged_in"] = True
        return redirect(url_for('dashboard.home', _id=session["_id"]))

    return render_template("dashboard-login.html", form = loginForm)

#Authentificatoin Function
def authentification(usr,pwd):
    worker = workers.find_one({'username': usr})
    if worker == None:
        return None
    return  worker['password'] == pwd


#Get worker Id From username Function
def getWorkerId(usr):
    worker = workers.find_one({'username': usr})
    return worker['_id']
##############################################################################
############################   SLEEP   #######################################
##############################################################################

#Sleep Page
@dashboard.route('/<_id>/sleep/', methods=['POST','GET'])
def sleep(_id):
    #_id is usr
    session["_id"] = False
    session["logged_in"] = False
    wroker_pic=getWorkerPic(_id)
    usr = getWorkerUser(_id)
    sleepform = SleepForm()
    if sleepform.validate_on_submit():
        pwd = sleepform.password.data
        authentificated = authentification(usr,pwd)
        if authentificated == False:
            wrong = "Password is wrong!"
            return render_template ("sleep.html", usr=usr, pic=wroker_pic, wrong=wrong, form=sleepform, title = "Sleep" )
        session["_id"] = _id
        session["logged_in"] = True
        return redirect(url_for('dashboard.home', _id=session["_id"]))
    return render_template("sleep.html", usr=usr, pic=wroker_pic, form=sleepform, title = "Sleep")


def getWorkerPic(_id):
    worker = workers.find_one({'_id': _id})
    return worker['picture']

def getWorkerUser(_id):
    try:
        worker = workers.find_one({'_id' : _id})
        return worker['username']
    except pymongo.errors.PyMongoError as e:
        return False
    