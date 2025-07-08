'''
from pymongo import MongoClient
from config import MONGO_URI, MONGO_DB_NAME

client = MongoClient(MONGO_URI)
db = client[MONGO_DB_NAME]

stm_collection = db["stm"]
ltm_collection = db["ltm"]
factual_memory_collection = db["factual_memory"]
'''