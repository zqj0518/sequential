from otree.api import *

doc = "Sequential housing offer experiment"


class C(BaseConstants):
    NAME_IN_URL = 'sequential'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 10
    MAX_OFFERS = 20


houses = [
    dict(suburb="Cashmere", area=200, bedrooms=4, year=2011),
    dict(suburb="Cashmere", area=232, bedrooms=3, year=1997),
    dict(suburb="Sumner", area=190, bedrooms=3, year=1980),
    dict(suburb="Burnside", area=160, bedrooms=3, year=1970),
    dict(suburb="Avonhead", area=250, bedrooms=4, year=1949),
    dict(suburb="Halswell", area=215, bedrooms=4, year=2014),
    dict(suburb="Hoon Hay", area=245, bedrooms=3, year=1992),
    dict(suburb="Burwood", area=230, bedrooms=3, year=2001),
    dict(suburb="Burwood", area=180, bedrooms=4, year=1995),
    dict(suburb="Parklands", area=100, bedrooms=3, year=2014),
]


offers = [
    [388,488,683,321,625,744,279,848,276,678,408,435,679,465,393,397,588,358,644,495],
    [739,803,221,729,159,150,299,818,585,875,130,795,481,2,525,429,62,459,748,374],
    [310,290,637,372,619,207,455,400,251,708,452,516,420,607,410,324,214,480,463,617],
    [420,637,727,561,643,663,568,636,422,336,414,479,332,494,546,724,411,267,357,733],
    [292,264,344,266,396,445,266,241,370,484,264,186,578,244,189,565,271,235,350,373],
    [494,225,272,994,602,987,523,683,1400,1574,1413,184,1081,558,273,1182,305,661,785,89],
    [522,252,562,255,370,292,533,237,262,343,220,460,294,535,297,452,284,436,581,197],
    [252,709,966,885,737,449,910,250,933,491,450,394,899,372,505,608,827,712,838,541],
    [789,829,996,390,756,311,267,681,412,287,918,200,371,443,469,701,1020,329,901,105],
    [341,459,453,454,361,240,659,497,382,536,600,784,333,579,541,454,732,471,576,553],
]


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):

    offer_number = models.IntegerField(initial=1)

    decision = models.StringField(
        choices=["Accept", "Reject"],
        blank=True
    )

    accepted_price = models.IntegerField(blank=True)