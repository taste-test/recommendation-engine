import csv
import os

# Define class for the mongo object
class ImageMetadata(object):

    def __init__(self, Id, Name, PinterestUrl, StructuralEmphasis, Slenderness, Symmetry, Repetition, Complexity, Sequence, PinterestSection):
        self.Id = Id
        self.Name = Name
        self.PinterestUrl = PinterestUrl
        self.StructuralEmphasis = StructuralEmphasis
        self.Slenderness = Slenderness
        self.Symmetry = Symmetry
        self.Repetition = Repetition
        self.Complexity = Complexity
        self.Sequence = Sequence
        self.PinterestSection = PinterestSection

if __name__ == '__main__':

    __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

    # Load csv file
    with open(os.path.join(__location__,'taste_test_images.csv'), 'rb') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=';', quotechar='|')
        for row in spamreader:
            data = ImageMetadata(row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9])
            print data.Name
