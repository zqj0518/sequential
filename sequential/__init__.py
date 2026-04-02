from otree.api import *
import random
import numpy as np

doc = "Sequential housing offer experiment - Auckland"

class C(BaseConstants):
    NAME_IN_URL = 'sequential'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 10
    MAX_OFFERS = 20
    
    TREATMENT_NO_INFO = 'no_info'
    TREATMENT_AVM_RANGE = 'avm_range'
    TREATMENT_QV_POINT = 'qv_point'

# 10套奥克兰房产 - 基于20# 数据来源参考：OneRoof, Homes.co.nz, QV, Barfoot & Thompson 市场报告

houses = [

    # ===== UNDER AVM (成交价低于 AVM - 3套) =====

    dict(
        address="12 Mahia Road",
        suburb="Manurewa",
        bedrooms=3,
        bathrooms=1,
        floor_area=110,
        land_area=620,
        year_built=1975,
        school_zone=["Manurewa East School","Alfriston College"],
        sale_price=565,
        avm_lower=610,
        avm_upper=670,
        qv_estimate=640
    ),

    dict(
        address="8 Clevedon Road",
        suburb="Papakura",
        bedrooms=3,
        bathrooms=1,
        floor_area=95,
        land_area=540,
        year_built=1981,
        school_zone=["Papakura Central School","Papakura High School"],
        sale_price=505,
        avm_lower=550,
        avm_upper=610,
        qv_estimate=575
    ),

    dict(
        address="21 Bairds Road",
        suburb="Otara",
        bedrooms=3,
        bathrooms=1,
        floor_area=102,
        land_area=600,
        year_built=1974,
        school_zone=["Tangaroa College","Otara Primary"],
        sale_price=485,
        avm_lower=530,
        avm_upper=590,
        qv_estimate=555
    ),


    # ===== WITHIN AVM (正常成交 - 4套) =====

    dict(
        address="44 Panama Road",
        suburb="Mount Wellington",
        bedrooms=3,
        bathrooms=2,
        floor_area=140,
        land_area=480,
        year_built=1994,
        school_zone=["Panama Road School","One Tree Hill College"],
        sale_price=875,
        avm_lower=840,
        avm_upper=920,
        qv_estimate=885
    ),

    dict(
        address="15 West Tamaki Road",
        suburb="Glen Innes",
        bedrooms=3,
        bathrooms=1,
        floor_area=125,
        land_area=520,
        year_built=1987,
        school_zone=["Glen Innes School","Tamaki College"],
        sale_price=805,
        avm_lower=770,
        avm_upper=840,
        qv_estimate=810
    ),

    dict(
        address="33 Arthur Street",
        suburb="Onehunga",
        bedrooms=3,
        bathrooms=2,
        floor_area=150,
        land_area=400,
        year_built=2004,
        school_zone=["Onehunga Primary","Onehunga High School"],
        sale_price=945,
        avm_lower=900,
        avm_upper=980,
        qv_estimate=940
    ),

    dict(
        address="18 Ladies Mile",
        suburb="Ellerslie",
        bedrooms=4,
        bathrooms=2,
        floor_area=175,
        land_area=500,
        year_built=1998,
        school_zone=["Ellerslie School","One Tree Hill College"],
        sale_price=1185,
        avm_lower=1140,
        avm_upper=1240,
        qv_estimate=1195
    ),


    # ===== ABOVE AVM (成交价高于 AVM - 3套) =====

    dict(
        address="26 Upland Road",
        suburb="Remuera",
        bedrooms=4,
        bathrooms=3,
        floor_area=195,
        land_area=680,
        year_built=2015,
        school_zone=["Remuera Primary","Remuera Intermediate","Selwyn College"],
        sale_price=2260,
        avm_lower=1950,
        avm_upper=2150,
        qv_estimate=2060
    ),

    dict(
        address="9 Cleveland Road",
        suburb="Parnell",
        bedrooms=3,
        bathrooms=2,
        floor_area=165,
        land_area=420,
        year_built=2008,
        school_zone=["Parnell School","Auckland Grammar","Epsom Girls Grammar"],
        sale_price=1730,
        avm_lower=1480,
        avm_upper=1620,
        qv_estimate=1560
    ),

    dict(
        address="52 Tamaki Drive",
        suburb="Mission Bay",
        bedrooms=4,
        bathrooms=3,
        floor_area=210,
        land_area=730,
        year_built=2018,
        school_zone=["Kohimarama School","Selwyn College"],
        sale_price=2690,
        avm_lower=2280,
        avm_upper=2480,
        qv_estimate=2390
    ),
]


def generate_offers(mean_price, sd_percentage=0.15, num_offers=20, seed=None):
    if seed is not None:
        np.random.seed(seed)
    sd = mean_price * sd_percentage
    offers = np.random.normal(mean_price, sd, num_offers)
    offers = [max(int(round(offer)), 100) for offer in offers]
    random.shuffle(offers)
    return offers

offers = []
for i, house in enumerate(houses):
    house_offers = generate_offers(
        mean_price=house['sale_price'],
        sd_percentage=0.15,
        num_offers=C.MAX_OFFERS,
        seed=1000 + i
    )
    offers.append(house_offers)

class Subsession(BaseSubsession):
    pass

def creating_session(subsession):
    import itertools
    treatments = itertools.cycle([
        C.TREATMENT_NO_INFO,
        C.TREATMENT_AVM_RANGE,
        C.TREATMENT_QV_POINT
    ])
    for player in subsession.get_players():
        if subsession.round_number == 1:
            player.participant.treatment = next(treatments)

class Group(BaseGroup):
    pass

class Player(BasePlayer):
    current_offer_number = models.IntegerField(initial=1)
    accepted_price = models.IntegerField()
    final_offer_number = models.IntegerField()

def get_treatment(player):
    return getattr(player.participant, 'treatment', C.TREATMENT_NO_INFO)

class Introduction(Page):
    @staticmethod
    def is_displayed(player):
        return player.round_number == 1
    
    @staticmethod
    def vars_for_template(player):
        treatment = get_treatment(player)
        if treatment == C.TREATMENT_AVM_RANGE:
            text = "You will see the AVM range for each property."
        elif treatment == C.TREATMENT_QV_POINT:
            text = "You will see the QV estimate for each property."
        else:
            text = "You will see basic property information."
        return dict(instruction_text=text, treatment=treatment)

class OfferDecision(Page):
    """单个offer的决策页面 - 会循环显示直到接受"""
    
    @staticmethod
    def is_displayed(player):
        # 还没接受任何offer
        return player.field_maybe_none('accepted_price') is None
    
    @staticmethod
    def vars_for_template(player):
        house = houses[player.round_number - 1]
        offer_list = offers[player.round_number - 1]
        current_offer = offer_list[player.current_offer_number - 1]
        treatment = get_treatment(player)
        
        # 是否是最后一个offer
        is_last_offer = (player.current_offer_number == C.MAX_OFFERS)
        
        context = dict(
    address=house["address"],
    suburb=house["suburb"],
    bedrooms=house["bedrooms"],
    bathrooms=house["bathrooms"],
    floor_area=house["floor_area"],
    land_area=house["land_area"],
    year_built=house["year_built"],
    school_zone=house["school_zone"],
    current_offer=current_offer,
    offer_number=player.current_offer_number,
    max_offers=C.MAX_OFFERS,
    is_last_offer=is_last_offer,
    treatment=treatment,
    round_number=player.round_number,
    total_rounds=C.NUM_ROUNDS,
    show_avm_range=False,
    show_qv_estimate=False
)

        if treatment == C.TREATMENT_AVM_RANGE:
            avm_midpoint = (house['avm_lower'] + house['avm_upper']) / 2
            context['show_avm_range'] = True
            context['avm_lower'] = house['avm_lower']
            context['avm_upper'] = house['avm_upper']
            context['avm_midpoint'] = int(avm_midpoint)
        elif treatment == C.TREATMENT_QV_POINT:
            context['show_qv_estimate'] = True
            context['qv_estimate'] = house['qv_estimate']
        
        return context
    
    @staticmethod
    def live_method(player, data):
        """使用live方法处理accept/reject，避免页面跳转"""
        offer_list = offers[player.round_number - 1]
        current_offer = offer_list[player.current_offer_number - 1]
        
        action = data.get('action')
        
        if action == 'accept':
            # 接受offer
            player.accepted_price = current_offer
            player.final_offer_number = player.current_offer_number
            player.payoff = current_offer
            return {0: 'accepted'}
            
        elif action == 'reject':
            if player.current_offer_number < C.MAX_OFFERS:
                # 移动到下一个offer
                player.current_offer_number += 1
                new_offer = offer_list[player.current_offer_number - 1]
                is_last = (player.current_offer_number == C.MAX_OFFERS)
                return {
                    0: {
                        'new_offer': new_offer,
                        'offer_number': player.current_offer_number,
                        'is_last_offer': is_last
                    }
                }
            else:
                # 最后一个offer必须接受
                player.accepted_price = current_offer
                player.final_offer_number = player.current_offer_number
                player.payoff = current_offer
                return {0: 'accepted'}

class RoundResults(Page):
    @staticmethod
    def vars_for_template(player):
        house = houses[player.round_number - 1]
        treatment = get_treatment(player)
        
        context = dict(
            suburb=house["suburb"], 
            accepted_price=player.accepted_price,
            final_offer_number=player.final_offer_number, 
            total_offers=C.MAX_OFFERS,
            cumulative_payoff=sum([p.payoff for p in player.in_all_rounds()]),
            treatment=treatment,
            show_avm_range=False,
            show_qv_estimate=False
        )
        
        if treatment == C.TREATMENT_AVM_RANGE:
            context['show_avm_range'] = True
            context['avm_lower'] = house['avm_lower']
            context['avm_upper'] = house['avm_upper']
        elif treatment == C.TREATMENT_QV_POINT:
            context['show_qv_estimate'] = True
            context['qv_estimate'] = house['qv_estimate']
        
        return context

class FinalResults(Page):
    @staticmethod
    def is_displayed(player):
        return player.round_number == C.NUM_ROUNDS
    
    @staticmethod
    def vars_for_template(player):
        all_rounds = player.in_all_rounds()
        total_payoff = sum([p.payoff for p in all_rounds])
        average_payoff = total_payoff / C.NUM_ROUNDS
        average_offer_number = sum([p.final_offer_number for p in all_rounds]) / C.NUM_ROUNDS
        
        deals_below = deals_within = deals_above = 0
        for i, p in enumerate(all_rounds):
            house = houses[i]
            if p.accepted_price < house['avm_lower']:
                deals_below += 1
            elif p.accepted_price > house['avm_upper']:
                deals_above += 1
            else:
                deals_within += 1
        
        return dict(
            total_payoff=total_payoff, 
            average_payoff=int(average_payoff),
            average_offer_number=round(average_offer_number, 1),
            deals_below_avm=deals_below,
            deals_within_avm=deals_within,
            deals_above_avm=deals_above,
            treatment=get_treatment(player)
        )

page_sequence = [Introduction, OfferDecision, RoundResults, FinalResults]
