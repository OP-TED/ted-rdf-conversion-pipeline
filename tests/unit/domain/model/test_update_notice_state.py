#!/usr/bin/python3

# test_update_notice_state.py
# Date:  08/02/2022
# Author: Eugeniu Costetchi
# Email: costezki.eugen@gmail.com 

""" """
import datetime

from deepdiff import DeepDiff
from schematics.models import Model
from schematics.types import StringType, DateTimeType, ListType, ModelType
from schematics.transforms import blacklist


class Movie(Model):
    name = StringType(required=True)
    director = StringType()
    release_date = DateTimeType()
    personal_thoughts = StringType()

    class Options:
        roles = {'public': blacklist('personal_thoughts')}

    def __init__(self, name, **kwargs):
        super().__init__(**kwargs)
        self.name = name


class Collection(Model):
    name = StringType(required=True)
    movies = ListType(ModelType(Movie), required=True)
    notes = StringType()

    class Options:
        roles = {'public': blacklist('notes')}


def test_schematics():
    trainspotting = Movie("Trainspotting1")
    # trainspotting.name = u'Trainspotting'
    trainspotting.director = u'Danny Boyle'
    trainspotting.release_date = datetime.datetime(1996, 7, 19, 0, 0)
    trainspotting.personal_thoughts = 'This movie was great!'

    trainspotting_valid = Movie("Trainspotting")
    trainspotting_valid.name = u'Trainspotting'

    # trainspotting_valid.validate()
    # trainspotting.validate()

    d = DeepDiff(trainspotting, trainspotting_valid, get_deep_distance=True)
    print(d)

    favorites = Collection()
    favorites.name = 'My favorites'
    favorites.notes = 'These are some of my favorite movies'
    favorites.movies = [trainspotting, ]

    # favorites.validate()

# def test_setting_normalised_metadata(publicly_available_notice):
#     print(publicly_available_notice)
