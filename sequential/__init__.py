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
# 10套奥克兰房产
# 数据来源参考：OneRoof, Homes.co.nz, QV, Barfoot & Thompson 市场报告

houses = [

    dict(
        address="5 Tainui Street",
        suburb="Torbay",
        bedrooms=4,
        bathrooms=3,
        floor_area=220,
        land_area=611,
        year_built="1960s",
        school_zone=["Long Bay School", "Torbay School"],
        sale_price=1613,
        avm_lower=1252,
        avm_upper=1464,
        qv_estimate=1290
    ),

    dict(
        address="9/52B Rosedale Road",
        suburb="Rosedale",
        bedrooms=3,
        bathrooms=2,
        floor_area=148,
        land_area=81,
        year_built="2020",
        school_zone=["St John's School", "Murrays Bay School"],
        sale_price=966,
        avm_lower=1000,
        avm_upper=1132,
        qv_estimate=1020
    ),

    dict(
        address="5 Beacholm Road",
        suburb="Takapuna",
        bedrooms=4,
        bathrooms=1,
        floor_area=210,
        land_area=497,
        year_built="1950s",
        school_zone=["Takapuna School", "Hauraki School"],
        sale_price=1943,
        avm_lower=1968,
        avm_upper=2476,
        qv_estimate=2070
    ),

    dict(
        address="1 Weona Place",
        suburb="Westmere",
        bedrooms=3,
        bathrooms=3,
        floor_area=323,
        land_area=512,
        year_built="2010s",
        school_zone=["Westmere School (Auckland)", "St Francis Catholic School (Pt Chevalier)"],
        sale_price=4175,
        avm_lower=3962,
        avm_upper=4971,
        qv_estimate=4160
    ),

    dict(
        address="1 Hall Road",
        suburb="Glenfield",
        bedrooms=5,
        bathrooms=5,
        floor_area=240,
        land_area=1330,
        year_built="1970s",
        school_zone=["Glenfield Primary School", "Manuka Primary School"],
        sale_price=1550,
        avm_lower=1681,
        avm_upper=2275,
        qv_estimate=2150
    ),

    dict(
        address="36 Woodside Road",
        suburb="Mount Eden",
        bedrooms=5,
        bathrooms=3,
        floor_area=256,
        land_area=1062,
        year_built="1910s",
        school_zone=["Maungawhau School", "Our Lady Sacred Heart School (Epsom)", "Good Shepherd School (Balmoral)"],
        sale_price=4625,
        avm_lower=3319,
        avm_upper=4004,
        qv_estimate=3610
    ),

    dict(
        address="12 Valder Avenue",
        suburb="Otara",
        bedrooms=3,
        bathrooms=1,
        floor_area=92,
        land_area=513,
        year_built="2020s",
        school_zone=["East Tamaki School", "Sancta Maria Catholic Primary School"],
        sale_price=607,
        avm_lower=668,
        avm_upper=750,
        qv_estimate=710
    ),

    dict(
        address="86 Bollard Avenue",
        suburb="New Windsor",
        bedrooms=3,
        bathrooms=1,
        floor_area=126,
        land_area=500,
        year_built="1930s",
        school_zone=["Avondale Primary School (Auckland)", "Jireh Christian School"],
        sale_price=1240,
        avm_lower=1173,
        avm_upper=1334,
        qv_estimate=1220
    ),

    dict(
        address="1A Mozeley Avenue",
        suburb="Devonport",
        bedrooms=4,
        bathrooms=1,
        floor_area=258,
        land_area=887,
        year_built="2010s",
        school_zone=["Devonport Primary School", "St Leo's Catholic School (Devonport)"],
        sale_price=3260,
        avm_lower=2459,
        avm_upper=3102,
        qv_estimate=2570
    ),

    dict(
        address="63 Nimstedt Avenue",
        suburb="Oteha",
        bedrooms=3,
        bathrooms=2,
        floor_area=148,
        land_area=500,
        year_built="2000s",
        school_zone=["Oteha Valley School", "City Impact Church School"],
        sale_price=1320,
        avm_lower=1162,
        avm_upper=1334,
        qv_estimate=1280
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
