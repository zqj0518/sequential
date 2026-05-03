from otree.api import *
import random
import numpy as np
import time
import json

doc = """
Sequential housing offer experiment - Auckland
Two-group design (per experiment_design_revised):
  G1 = no_info     (control)
  G2 = qv_point    (QV point estimate disclosed)
Tests anchoring effects in sequential offer acceptance:
  H1: timing (acceptance round)
  H2: |accepted price - QV|
  H3: asymmetric anchor-dependent utility (slope ratio beta/alpha)
"""


class C(BaseConstants):
    NAME_IN_URL = 'sequential'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 10
    MAX_OFFERS = 20

    # Treatments (two-group design)
    TREATMENT_NO_INFO = 'no_info'
    TREATMENT_QV_POINT = 'qv_point'


# 10 Auckland properties
# Data sources: OneRoof, Homes.co.nz, QV, Barfoot & Thompson market reports
# Prices in NZ$ thousands (k)
houses = [
    dict(
        suburb="Torbay",
        bedrooms=4,
        bathrooms=3,
        floor_area=220,
        land_area=611,
        year_built="1960s",
        school_zone=["Long Bay School", "Torbay School"],
        sale_price=1613,
        qv_estimate=1290,
    ),
    dict(
        suburb="Rosedale",
        bedrooms=3,
        bathrooms=2,
        floor_area=148,
        land_area=81,
        year_built="2020",
        school_zone=["St John's School", "Murrays Bay School"],
        sale_price=966,
        qv_estimate=1020,
    ),
    dict(
        suburb="Takapuna",
        bedrooms=4,
        bathrooms=1,
        floor_area=210,
        land_area=497,
        year_built="1950s",
        school_zone=["Takapuna School", "Hauraki School"],
        sale_price=1943,
        qv_estimate=2070,
    ),
    dict(
        suburb="Westmere",
        bedrooms=3,
        bathrooms=3,
        floor_area=323,
        land_area=512,
        year_built="2010s",
        school_zone=["Westmere School (Auckland)", "St Francis Catholic School (Pt Chevalier)"],
        sale_price=4175,
        qv_estimate=4160,
    ),
    dict(
        suburb="Glenfield",
        bedrooms=5,
        bathrooms=5,
        floor_area=240,
        land_area=1330,
        year_built="1970s",
        school_zone=["Glenfield Primary School", "Manuka Primary School"],
        sale_price=1550,
        qv_estimate=2150,
    ),
    dict(
        suburb="Mount Eden",
        bedrooms=5,
        bathrooms=3,
        floor_area=256,
        land_area=1062,
        year_built="1910s",
        school_zone=["Maungawhau School", "Our Lady Sacred Heart School (Epsom)", "Good Shepherd School (Balmoral)"],
        sale_price=4625,
        qv_estimate=3610,
    ),
    dict(
        suburb="Otara",
        bedrooms=3,
        bathrooms=1,
        floor_area=92,
        land_area=513,
        year_built="2020s",
        school_zone=["East Tamaki School", "Sancta Maria Catholic Primary School"],
        sale_price=607,
        qv_estimate=710,
    ),
    dict(
        suburb="New Windsor",
        bedrooms=3,
        bathrooms=1,
        floor_area=126,
        land_area=500,
        year_built="1930s",
        school_zone=["Avondale Primary School (Auckland)", "Jireh Christian School"],
        sale_price=1240,
        qv_estimate=1220,
    ),
    dict(
        suburb="Devonport",
        bedrooms=4,
        bathrooms=1,
        floor_area=258,
        land_area=887,
        year_built="2010s",
        school_zone=["Devonport Primary School", "St Leo's Catholic School (Devonport)"],
        sale_price=3260,
        qv_estimate=2570,
    ),
    dict(
        suburb="Oteha",
        bedrooms=3,
        bathrooms=2,
        floor_area=148,
        land_area=500,
        year_built="2000s",
        school_zone=["Oteha Valley School", "City Impact Church School"],
        sale_price=1320,
        qv_estimate=1280,
    ),
]


def generate_offers(mean_price, sd_percentage=0.15, num_offers=20, seed=None):
    """Draw 20 offers ~ N(sale_price, (15% * sale_price)^2), shuffled. Fixed seed per property."""
    if seed is not None:
        np.random.seed(seed)
    sd = mean_price * sd_percentage
    offers = np.random.normal(mean_price, sd, num_offers)
    offers = [max(int(round(offer)), 100) for offer in offers]
    random.seed(seed)  # also seed random for reproducible shuffle
    random.shuffle(offers)
    return offers


# Pre-generate all offer sequences (fixed seeds for reproducibility)
offers = []
for i, house in enumerate(houses):
    house_offers = generate_offers(
        mean_price=house['sale_price'],
        sd_percentage=0.15,
        num_offers=C.MAX_OFFERS,
        seed=1000 + i,
    )
    offers.append(house_offers)


class Subsession(BaseSubsession):
    pass


def creating_session(subsession):
    """Round-robin assign treatments at round 1; persist via participant.vars."""
    import itertools
    treatments = itertools.cycle([
        C.TREATMENT_NO_INFO,
        C.TREATMENT_QV_POINT,
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

    # Timing
    round_start_time = models.FloatField()
    total_decision_time = models.FloatField()
    # Per-offer decision log (JSON list of dicts: offer_number, offer_value, decision, decision_time_ms)
    decision_times = models.LongStringField()


def get_treatment(player):
    return getattr(player.participant, 'treatment', C.TREATMENT_NO_INFO)


# ============================================================================
# PAGES
# ============================================================================

class Introduction(Page):
    @staticmethod
    def is_displayed(player):
        return player.round_number == 1

    @staticmethod
    def vars_for_template(player):
        treatment = get_treatment(player)
        if treatment == C.TREATMENT_QV_POINT:
            instruction_text = (
                "You will see the QV (Quotable Value) estimate for each property "
                "alongside basic property information."
            )
        else:
            instruction_text = (
                "You will see basic property information for each property."
            )
        return dict(
            instruction_text=instruction_text,
            treatment=treatment,
        )


class OfferDecision(Page):
    """Single-offer decision page; loops via live_method until accepted or round 20."""

    @staticmethod
    def is_displayed(player):
        return player.field_maybe_none('accepted_price') is None

    @staticmethod
    def vars_for_template(player):
        # Initialise per-round timing on first offer
        if player.current_offer_number == 1 and player.field_maybe_none('round_start_time') is None:
            player.round_start_time = time.time()
            if 'offer_times' not in player.participant.vars:
                player.participant.vars['offer_times'] = {}

        house = houses[player.round_number - 1]
        offer_list = offers[player.round_number - 1]
        current_offer = offer_list[player.current_offer_number - 1]
        treatment = get_treatment(player)
        is_last_offer = (player.current_offer_number == C.MAX_OFFERS)

        context = dict(
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
            show_qv_estimate=False,
        )

        if treatment == C.TREATMENT_QV_POINT:
            context['show_qv_estimate'] = True
            context['qv_estimate'] = house['qv_estimate']

        return context

    @staticmethod
    def live_method(player, data):
        offer_list = offers[player.round_number - 1]
        current_offer = offer_list[player.current_offer_number - 1]

        action = data.get('action')
        decision_time_ms = data.get('time', 0)

        # Log this offer's decision
        round_key = f'round_{player.round_number}'
        if round_key not in player.participant.vars['offer_times']:
            player.participant.vars['offer_times'][round_key] = []

        player.participant.vars['offer_times'][round_key].append({
            'offer_number': player.current_offer_number,
            'offer_value': current_offer,
            'decision': action,
            'decision_time_ms': decision_time_ms,
        })

        if action == 'accept':
            player.accepted_price = current_offer
            player.final_offer_number = player.current_offer_number
            player.payoff = current_offer
            player.total_decision_time = time.time() - player.round_start_time
            player.decision_times = json.dumps(player.participant.vars['offer_times'][round_key])
            return {0: 'accepted'}

        elif action == 'reject':
            if player.current_offer_number < C.MAX_OFFERS:
                player.current_offer_number += 1
                new_offer = offer_list[player.current_offer_number - 1]
                is_last = (player.current_offer_number == C.MAX_OFFERS)
                return {
                    0: {
                        'new_offer': new_offer,
                        'offer_number': player.current_offer_number,
                        'is_last_offer': is_last,
                    }
                }
            else:
                # Forced acceptance on offer 20
                player.accepted_price = current_offer
                player.final_offer_number = player.current_offer_number
                player.payoff = current_offer
                player.total_decision_time = time.time() - player.round_start_time
                player.decision_times = json.dumps(player.participant.vars['offer_times'][round_key])
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
            decision_time_seconds=round(player.total_decision_time, 1),
            treatment=treatment,
            show_qv_estimate=False,
        )

        if treatment == C.TREATMENT_QV_POINT:
            context['show_qv_estimate'] = True
            context['qv_estimate'] = house['qv_estimate']
            context['distance_from_qv'] = player.accepted_price - house['qv_estimate']

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

        total_time = sum([p.total_decision_time for p in all_rounds])
        average_time = total_time / C.NUM_ROUNDS

        # Deal quality vs QV (replaces former AVM-based bands).
        # Bands: within +/- 5% of QV = "near QV"; below -5% = "below QV"; above +5% = "above QV".
        deals_below = deals_near = deals_above = 0
        for i, p in enumerate(all_rounds):
            qv = houses[i]['qv_estimate']
            lower = qv * 0.95
            upper = qv * 1.05
            if p.accepted_price < lower:
                deals_below += 1
            elif p.accepted_price > upper:
                deals_above += 1
            else:
                deals_near += 1

        return dict(
            total_payoff=total_payoff,
            average_payoff=int(average_payoff),
            average_offer_number=round(average_offer_number, 1),
            total_time_seconds=round(total_time, 1),
            average_time_seconds=round(average_time, 1),
            deals_below_qv=deals_below,
            deals_near_qv=deals_near,
            deals_above_qv=deals_above,
            treatment=get_treatment(player),
        )


page_sequence = [Introduction, OfferDecision, RoundResults, FinalResults]
