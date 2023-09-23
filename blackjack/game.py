from enum import Enum, auto
from random import Random
from typing import Iterable, List, Optional

deck = [11, 2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10] * 4


class Action(Enum):
    hit = auto()
    stand = auto()
    split = auto()
    double = auto()
    surrender = auto()


class Deck(List[int]):
    def __init__(self, rng: Random):
        self.rng = rng
        super().__init__(sorted(deck, key=lambda _: self.rng.random()))

    def deal(self) -> int:
        if len(self) == 0:
            self.extend(sorted(deck, key=lambda _: self.rng.random()))
        return self.pop()


class Player:
    def __init__(self, rng: Random):
        self.rng = rng

    def insurance(self, dealer_card: int) -> bool:
        return False

    def play(self, dealer_card: int, cards: List[int]) -> Action:
        return Action.stand


class RandomPlayer(Player):
    def insurance(self, dealer_card: int) -> bool:
        if dealer_card in (10, 11):
            return self.rng.choice((True, False))
        return False

    def play(self, dealer_card: int, cards: List[int]) -> Action:
        return self.rng.choice((Action.hit, Action.stand))


class CautiousPlayer(Player):
    def insurance(self, dealer_card: int) -> bool:
        return dealer_card in (10, 11)

    def play(self, dealer_card: int, cards: List[int]) -> Action:
        if hand_value(cards) <= 11:
            return Action.hit
        return Action.stand


class StrategicPlayer(Player):
    def play(self, dealer_card: int, cards: List[int]) -> Action:
        value = hand_value(cards)

        if len(cards) == 2 and cards[0] == cards[1]:
            card = cards[0]
            if card == 11:
                return Action.split
            if card == 10:
                return Action.stand
            if card == 9:
                if dealer_card in (7, 10, 11):
                    return Action.stand
                return Action.split
            if card == 8:
                if dealer_card == 1:
                    return Action.surrender
                return Action.split
            if card == 7:
                if dealer_card <= 7:
                    return Action.split
                return Action.hit
            if card == 6:
                if dealer_card <= 6:
                    return Action.split
                return Action.hit
            if card == 5:
                if dealer_card <= 9:
                    return Action.double
                return Action.hit
            if card == 4:
                if dealer_card in (5, 6):
                    return Action.split
                return Action.hit
            if card in (3, 2):
                if dealer_card <= 7:
                    return Action.split
                return Action.hit
        elif 11 in cards:
            if value >= 20:
                return Action.stand
            if value == 19:
                if dealer_card == 6:
                    return Action.double
                return Action.stand
            if value == 18:
                if dealer_card <= 6:
                    return Action.double
                if dealer_card <= 8:
                    return Action.stand
                return Action.hit
            if value == 17:
                if dealer_card in (3, 4, 5, 6):
                    return Action.double
                return Action.hit
            if value in (16, 15):
                if dealer_card in (4, 5, 6):
                    return Action.double
                return Action.hit
            if value <= 14:
                if dealer_card in (5, 6):
                    return Action.double
                return Action.hit
        else:
            if value >= 18:
                return Action.stand
            if value == 17:
                if dealer_card == 11:
                    return Action.surrender
                return Action.stand
            if value == 16:
                if dealer_card <= 6:
                    return Action.stand
                if dealer_card <= 8:
                    return Action.hit
                return Action.surrender
            if value == 15:
                if dealer_card <= 9:
                    return Action.stand
                if dealer_card <= 8:
                    return Action.hit
                return Action.surrender
            if value in (13, 14):
                if dealer_card <= 9:
                    return Action.stand
                return Action.hit
            if value == 12:
                if dealer_card in (4, 5, 6):
                    return Action.stand
                return Action.hit
            if value == 11:
                return Action.double
            if value == 10:
                if dealer_card == 9:
                    return Action.double
                return Action.hit
            if value == 9:
                if dealer_card in (3, 4, 5, 6):
                    return Action.double
                return Action.hit
        return Action.hit


def hand_value(cards: Iterable[int]):
    value = sum(cards)
    if value > 21:
        value = sum(1 if card == 11 else card for card in cards)
    return value



def play_blackjack(rng: Random, player: Player, rounds: int = 10) -> float:
    shoe = Deck(rng)

    winnings = 0

    for _ in range(rounds):
        dealer_card = shoe.deal()
        winnings -= 1

        insurance = player.insurance(dealer_card)
        if insurance:
            winnings -= 0.5

        hands = [[shoe.deal(), shoe.deal()]]
        final_hands = []
        while hands:
            hand = hands.pop()
            if hand_value(hand) == 21:
                winnings += 2.5
            else:
                while True:
                    action = player.play(dealer_card, hand)
                    if action is Action.split:
                        if len(hands) != 2 or hands[0] != hands[1]:
                            action = Action.stand
                        else:
                            winnings -= 1
                            new_hand = [hand[1], shoe.deal()]
                            if hand_value(new_hand) == 21:
                                winnings += 2
                            else:
                                hands.append(new_hand)
                            hand = [hand[0], shoe.deal()]
                            if hand_value(hand) == 21:
                                winnings += 2
                                break
                    if action is Action.hit:
                        hand.append(shoe.deal())
                        if hand_value(hand) >= 21:
                            if hand_value(hand) == 21:
                                final_hands.append(hand)
                            break
                    if action is Action.surrender:
                        if len(hand) != 2:
                            action = Action.stand
                        else:
                            winnings += 0.5
                            break
                    if action is Action.double:
                        winnings -= 1
                        hand.append(shoe.deal())
                        if hand_value(hand) <= 21:
                            final_hands.append(hand)
                            final_hands.append(hand)
                        break
                    if action is Action.stand:
                        final_hands.append(hand)
                        break

        dealer_hand = [dealer_card, shoe.deal()]
        if hand_value(dealer_hand) == 21 and insurance:
            winnings += 1
        else:
            while hand_value(dealer_hand) < 17:
                dealer_hand.append(shoe.deal())

        dealer_value = hand_value(dealer_hand)

        for hand in final_hands:
            value = hand_value(hand)
            if value > dealer_value:
                winnings += 2
            elif value == dealer_value:
                winnings += 1

    return winnings

