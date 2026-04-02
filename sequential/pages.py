from otree.api import *
from .models import *


class Decision(Page):

    form_model = 'player'
    form_fields = ['decision']

    def vars_for_template(player):

        house = houses[player.round_number - 1]
        offer_list = offers[player.round_number - 1]
        current_offer = offer_list[player.offer_number - 1]

        return dict(
            suburb=house["suburb"],
            area=house["area"],
            bedrooms=house["bedrooms"],
            year=house["year"],
            offer=current_offer,
            offer_number=player.offer_number
        )

    def before_next_page(player, timeout_happened):

        offer_list = offers[player.round_number - 1]
        current_offer = offer_list[player.offer_number - 1]

        if player.decision == "Accept":
            player.accepted_price = current_offer
            player.payoff = current_offer

        else:
            if player.offer_number < C.MAX_OFFERS:
                player.offer_number += 1
            else:
                player.accepted_price = current_offer
                player.payoff = current_offer


page_sequence = [Decision]