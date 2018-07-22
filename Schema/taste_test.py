from marshmallow import Schema, fields, ValidationError, pre_load, post_load, pre_dump, post_dump

class ImageComparison(object):
    def __init__(self, feature, positiveImage, negativeImage, preference):
        self.Feature = feature
        self.PositiveImage = positiveImage
        self.NegativeImage = negativeImage
        self.Preference = preference

class ImageComparisonSchema(Schema):
    Feature = fields.String()
    PositiveImage = fields.String()
    NegativeImage = fields.String()
    Preference = fields.String()

    @post_load
    def make_image_comparison(self, data):
        return ImageComparison(data['Feature'],data['PositiveImage'], data['NegativeImage'], data['Preference'])

class ImageComparisonList(object):
    def __init__(self, comparisonList):
        self.ComparisonList = comparisonList

class ImageComparisonListSchema(Schema):
    ComparisonList = fields.List(fields.Nested(ImageComparisonSchema), many=True)

    @post_load
    def make_image_comparison_list(self, data):
        return ImageComparisonList(data['ComparisonList'])

class ImageFeatureScore(object):
    def __init__(self, feature, score):
        self.Feature = feature
        self.Score = score

class ImageFeatureScoreSchema(Schema):
    Feature = fields.String()
    Score = fields.Float();

    @post_load
    def make_feature_score(self, data):
        return ImageFeatureScore(data['Feature'], data['Score'])

class TasteProfile(object):
    def __init__(self, scoreList, imageList):
        self.FeatureScores = scoreList
        self.RepresentativeImages = imageList

class TasteProfileSchema(Schema):
    FeatureScores = fields.List(fields.Nested(ImageFeatureScoreSchema), many=True)
    RepresentativeImages = fields.List(fields.String(), many=True)

    @post_load
    def make_taste_profile(self, data):
        return TasteProfile(data['FeatureScores'], data['RepresentativeImages'])

