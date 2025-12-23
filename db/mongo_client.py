from pymongo import MongoClient
import os
uri = "mongodb+srv://reddyhashish:Hasini120@cluster0.ckmru0d.mongodb.net/capestone"
MONGO_URI = os.getenv("MONGO_URI", uri)
client = MongoClient(MONGO_URI)
db = client["darkweb_pipeline"]
