from flask import Flask, jsonify, request, Blueprint
import numpy as np
import os, sys, math
sys.path.insert(0, os.path.abspath(".."))
import pandas as pd
from random import random, randint
from collections import defaultdict
from pymongo import MongoClient

import Schema.taste_test as TasteTestSchemata

imagecomparisonlist_schema = TasteTestSchemata.ImageComparisonListSchema()
tasteprofile_schema = TasteTestSchemata.TasteProfileSchema()
image_metadata_schema = TasteTestSchemata.ImageMetadataSchema()

TasteTest = Blueprint('TasteTest', __name__)

def _connect_mongo():
    """ A util for making a connection to mongo """

    DB_NAME = str(os.environ.get('TASTE_DB_NAME'))
    DB_HOST = str(os.environ.get('TASTE_DB_HOST'))
    DB_PORT = int(os.environ.get('TASTE_DB_PORT'))
    DB_USER = str(os.environ.get('TASTE_DB_USER'))
    DB_PASS = str(os.environ.get('TASTE_DB_PASS'))
    
    connection = MongoClient(DB_HOST, DB_PORT)
    db = connection[DB_NAME]
    db.authenticate(DB_USER, DB_PASS)

    return db

##def getImageData():
##
##    db = _connect_mongo()
##
##    col_names = [u'Name', u'PinterestUrl', u'StructuralEmphasis', u'Slenderness', u'Symmetry', u'Repetition', u'Complexity', u'Sequence', u'PinterestSection']
##    df  = pd.DataFrame(columns = col_names)
##
##    metadata = db.image_data.find()
##    for image in metadata:
##        if image[u'Repetition'] != u'"Repetition"':
##            del image[u'_id']
##            del image[u'Id']
##            for val in image:
##                image[val] = image[val].replace('"', '')
##            df.loc[len(df)] = image 
##
##    with pd.option_context('display.max_rows', 20, 'display.max_columns', 9):
##        print(df)
##    
##    return df

def getImageData():
    
    results = pd.read_csv(os.path.join(os.getcwd(),'API','Taste','taste_test_images.csv'), sep=";")
    del results['Id']

    with pd.option_context('display.max_rows', 20, 'display.max_columns', 9):
        print(results)
    
    return results

def generate_input_dict(lst, feat, intfeats_to_feat):
    imgs = lst[feat].copy()
    intchoice = randint(0, len(imgs.keys()) - 1)
    feats_dic = imgs[imgs.keys()[intchoice]]
    ret = {'feature': intfeats_to_feat[feat]}
    ret.update({ch: feats_dic[ch][randint(0, len(feats_dic[ch])-1)] for ch in feats_dic.keys() if ch != '_'})
    if '0' in ret.keys() and '1' in ret.keys():
        return ret
    else:
        return generate_input_dict(lst, feat, intfeats_to_feat)

#given results back and inputted list of images, get counts
def evaluate_feat(input_dicts, output_list):
    feats_agg = defaultdict(dict)
    for idx, input_dict in enumerate(input_dicts):
        if output_list[idx] in feats_agg[input_dict['feature']].keys():
            feats_agg[input_dict['feature']][output_list[idx]] += 1
        else:
            feats_agg[input_dict['feature']][output_list[idx]] = 1
    return feats_agg

def FeatureList():
    return [ u'StructuralEmphasis', u'Slenderness', u'Symmetry', u'Repetition', u'Complexity']

def GenerateComparisonList(n):
    # get image metadata
    data = getImageData()

    # format pandas dataframe
    feats_names = FeatureList()
    intfeats_to_feat= {'feat{}'.format(k): f for k, f in enumerate(feats_names)}
    feats_to_intfeat= { f: 'feat{}'.format(k) for k, f in enumerate(feats_names)}
    data = data.rename(columns=feats_to_intfeat)
    cols_to_select = intfeats_to_feat.keys() + ['Name']
    tagged_data = data[cols_to_select]

    # create inverse from feats
    num_feats = len(intfeats_to_feat)
    for f in range(num_feats):
        inverse_feats = ['feat'+str(k) for k in range(num_feats) if k !=f]
        tagged_data['inverse'+str(f)] = tagged_data[inverse_feats].apply(lambda x: ''.join(x), axis=1)

    # create the combo of images to feed the site
    lst={}
    for f in range(num_feats):
        lst['feat'+str(f)] = defaultdict(dict)
        grpd = tagged_data.groupby(['feat'+str(f),'inverse'+str(f)])['Name']
        all_combos = grpd.groups.keys()
        for i,j in grpd.groups.keys():
            lst['feat'+str(f)][j][i] = grpd.get_group((i,j)).values

    # create dict of randomly chosen images opposite on one feat not other feats
    input_dicts = [generate_input_dict(lst, ft, intfeats_to_feat) for ft in ['feat'+str(k) for k in range(num_feats)]*n]

    # format list of comparison objects
    comparisonList = []
    for i in input_dicts:
        comparison = TasteTestSchemata.ImageComparison(i['feature'],i['1'],i['0'],"")
        comparisonList.append(comparison)

    return comparisonList

def SummarizeComparisons(comparisons):

    #create summary
    featureDict = {}
    for name in FeatureList():
        featureDict.update({name:{"Total":0.0, "Count":0}})

    #Get Representative Image List
    data = getImageData()
    del data['PinterestUrl']
    del data['Sequence']
    del data['PinterestSection']

    #Score along each feature
    for comparison in comparisons:
        print(comparison.Feature)
        if (comparison.Preference == "Positive"):
            print("+1")
            featureDict[comparison.Feature]["Total"] += 1
            featureDict[comparison.Feature]["Count"] += 1
        elif (comparison.Preference == "Negative"):
            print("-1")
            featureDict[comparison.Feature]["Total"] -= 1
            featureDict[comparison.Feature]["Count"] += 1
        else:
            #Empty or "NA"
            featureDict[comparison.Feature]["Count"] += 1

        # Remove the data already encountered
        data = data[data.Name != comparison.NegativeImage]
        data = data[data.Name != comparison.PositiveImage]

    #print len(data["Name"])

    scoreList = []
    #dist = sqrt((q1-p1)^2+(q2-p2)^2+(q3-p3)^2+(q4-p4)^2+(q5-p5)^2)
    shp = data['Slenderness'].shape
    sq_dist = np.zeros(shp)
    for feature in featureDict:
        score = featureDict[feature]["Total"] / featureDict[feature]["Count"]
        scoreSchema = TasteTestSchemata.ImageFeatureScore(feature, score)
        scoreList.append(scoreSchema)
        imageScores = []
        for row in data[feature]:
            if row == '1':
                imageScores.append(1.0)
            elif row == '0':
                imageScores.append(-1.0)
            elif row == '_':
                imageScores.append(0.0)
        #print "image scores ", imageScores
        imageScores = np.array(imageScores)
        sq_dist = np.add(sq_dist,np.square(np.subtract(imageScores,score*np.ones(shp))))
        
    data['distance'] = np.sqrt(sq_dist)
    sorted_data = data.sort_values('distance')
    
    testImageList = []
    for i in range(5):
        testImageList.append(sorted_data['Name'][i])

    summary = TasteTestSchemata.TasteProfile(scoreList,testImageList)

    return summary


@TasteTest.route('/taste/test/comparisons/generate/<int:n>/', methods=['GET'])
def get_comparisons(n):
    comparisonList = GenerateComparisonList(n)
    resultList = TasteTestSchemata.ImageComparisonList(comparisonList)
    serialized, errors = imagecomparisonlist_schema.dump(resultList)
    return jsonify(serialized)


@TasteTest.route('/taste/test/comparisons/summary/', methods=['POST'])
def post():
    json_data = request.get_json()
    if not json_data:
        return jsonify({'message': 'No input data provided'}), 400
    # Validate and deserialize input
    deserialized, errors = imagecomparisonlist_schema.load(json_data)
    if errors:
        return jsonify(errors), 422

    summary = SummarizeComparisons(deserialized.ComparisonList)
    print(summary)

    serialized, errors = tasteprofile_schema.dump(summary)
    return jsonify(serialized)
