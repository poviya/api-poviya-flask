from pymongo import MongoClient

def get_database_connection():
    client = MongoClient('mongodb://ue2g5msik4gkxati5lj3:xoj1Sbtcyp5UHW1870d@b2dhwys4he0suwxbecrc-mongodb.services.clever-cloud.com:2143/b2dhwys4he0suwxbecrc', 27017)
    return client['b2dhwys4he0suwxbecrc']
