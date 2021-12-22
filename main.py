# Flask 
from flask import Flask, render_template, request, session
# Dashboard
from dashboard.main import dashboard
from shop.main import shop
# MongoDB
import pymongo
from pymongo import MongoClient
# Token date
from datetime import date





# FLASK RUN APP_
app = Flask(__name__)


# Dashboard BluePrint
app.register_blueprint(dashboard, url_prefix="/dashboard")
# Shop BluePrint
app.register_blueprint(shop, url_prefix="/shop")

# SECRET KEY
app.secret_key = "boringeye69"


# NOSQL DATABASE CONNECTION
cluster = MongoClient("mongodb+srv://beye:Feriani01@cluster0.0p206.mongodb.net/boringeye?retryWrites=true&w=majority")
db = cluster["boringeye"]
clients = db["clients"] 
feedback = db["feedback"]
tokens = db["tokens"]
visitors = db["visitors"]

##############################################################################
############################   HOME   ########################################
##############################################################################

# Home Page 
@app.route('/', methods=['POST','GET'])
def home():
    if request.method == 'POST':
        session['ip'] = request.remote_addr
        session['name'] = request.form['name']
        session['email'] = request.form['email']
        session['message'] = request.form['message']
        isSent = sendFeedback()
        if isSent:
            msg = "Your message has been successfully sent. We will contact you very soon!"
            return  render_template("message_redirect.html",title="THANK YOU",msg=msg, color="green")
        else:
            msg = "Error Message Not Sent ! Please Contact us at boringeye@support.com"
            return  render_template("message_redirect.html",title="Error",msg=msg, color="red")
    elif request.method == 'GET':
        addVisitor(request.remote_addr)
        return render_template('index.html')

def addVisitor(ip):
    visitor = visitors.find_one({"_id" : str(ip)})
    if visitor == None:
        visitor = {
            "_id"   : str(ip),
            "date" : date.today().strftime("%d/%m/%Y")
        }
        try :
            resultat = visitors.insert_one(visitor)
            return True
        except pymongo.errors.PyMongoError as e:
            return False
        
    else:
        return False
        
        
        
############################   FUNCTIONS   ####################################

# Function send feedback (Contact Us) Function     
def sendFeedback():
    msg = {"ip" : session['ip'],
        "name" : session['name'],
        "email"  : session["email"],
        "message" : session["message"],
        "from" : "BE",
        "date" : date.today().strftime("%d/%m/%Y")
        }
    try :
        resultat = feedback.insert_one(msg)
        return True
    except pymongo.errors.PyMongoError as e:
        return False

##############################################################################
############################   ERROR HANDLER   ###############################
##############################################################################
# 404 PAGE
@app.errorhandler(404)
def page_not_found(e):
    return render_template('error_page.html', num="404", title="Page not found", msg=str(e)), 404

# 500 PAGE
@app.errorhandler(500)
def internal_server_error(e):
    return render_template('error_page.html', num="500", title="Internal server error", msg=str(e)), 500



if __name__ == "__main__":
    app.run(debug=True,use_reloader=False)