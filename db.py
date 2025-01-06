from pymongo import MongoClient

client = MongoClient("mongodb://13.61.104.237:27017/")

db = client["db_Alx"]
