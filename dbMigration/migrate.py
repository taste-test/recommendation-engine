import csv
import os, sys
from flask import jsonify
sys.path.insert(0, os.path.abspath(".."))
from pymongo import MongoClient


import Schema.taste_test as TasteTestSchemata

if __name__ == '__main__':

    image_metadata_schema = TasteTestSchemata.ImageMetadataSchema()

    DB_NAME = str(os.environ.get('TASTE_DB_NAME'))
    DB_HOST = str(os.environ.get('TASTE_DB_HOST'))
    DB_PORT = int(os.environ.get('TASTE_DB_PORT'))
    DB_USER = str(os.environ.get('TASTE_DB_USER'))
    DB_PASS = str(os.environ.get('TASTE_DB_PASS'))
    
    connection = MongoClient(DB_HOST, DB_PORT)
    db = connection[DB_NAME]
    db.authenticate(DB_USER, DB_PASS)
    image_data = db.image_data

    __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

    # Load csv file
    with open(os.path.join(__location__,'taste_test_images.csv'), 'rb') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=';', quotechar='|')
        for row in spamreader:
            mod = []
            for val in row:
                mod.append(val.replace('"', ''))
            row=mod
            data = TasteTestSchemata.ImageMetadata(row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9])
            post_data, errors = image_metadata_schema.dump(data)
            result = image_data.insert_one(post_data)
            print('One post: {0}'.format(result.inserted_id))
