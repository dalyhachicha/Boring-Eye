#MongoDB
from pymongo import MongoClient
from datetime import date

#NOSQL DATABASE CONNECTION
cluster = MongoClient("mongodb+srv://beye:Feriani01@cluster0.0p206.mongodb.net/boringeye?retryWrites=true&w=majority")
db = cluster["boringeye"]
clients = db["clients"] 
workers = db["workers"]
visitors = db["visitors"]

workers_counts = workers.count()
patients_counts = clients.count()
today_clients_count = clients.find({'date': date.today().strftime("%d/%m/%Y")}).count()
visitors_count = visitors.count()




