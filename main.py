import pygame
from ctypes import windll
import ctypes
import random
import time
from pygame.locals import *


class Game:
    def __init__(self):
        self._in_progress = True  # Game Status
        self._step = -1  # Game Step
        self._frame = 0  # Game Frame Count
        self._menu_step = 0  # Game Menu Step

    def get_in_progress(self):
        return self._in_progress

    def set_in_progress(self, new_progress):
        self._in_progress = new_progress

    def get_step(self):
        return self._step

    def set_step(self, new_step):
        self._step = new_step

    def get_frame(self):
        return self._frame

    def set_frame(self, new_frame):
        self._frame = new_frame

    def get_menu_step(self):
        return self._menu_step

    def set_menu_step(self, new_menu_step):
        self._menu_step = new_menu_step


class Match:
    def __init__(self, match_type=0):
        self.time_of_day = "day"
        self.status = 1  # Status 1 means pending, Status 0 means ended
        self.player_turn = "blue"
        if match_type == 1:
            self.blue_player = Player()
            self.green_player = Ia()
        elif match_type == 2:
            self.blue_player = BusinessPlayer()
            self.green_player = BusinessPlayer()
        elif match_type == 3:
            self.blue_player = DevilPlayer()
            self.green_player = DevilPlayer()
        else:
            self.blue_player = Player()
            self.green_player = Player()

        self.last_card_played = [[], ""]
        self.match_type = match_type
        self.winner = None


class Player:
    def __init__(self):
        self.castle = 30  # Player's Castle Life
        self.fence = 10  # Player's Fence Life
        self.builders = 2  # Player's Builders
        self.bricks = 5  # Player's Bricks
        self.soldiers = 2  # Player's Soldiers
        self.weapons = 5  # Player's Weapons
        self.magic = 2  # Player's Magic
        self.crystals = 5  # Player's Crystals

        # Fill deck with cards
        self.deck = []
        cards_name = []
        # Getting card names
        for card_key, card_content in cards_list.items():
            for i in range(card_content[0]):
                cards_name.append(card_key)
        # Creating cards in the deck
        for card_type in cards_list:
            for card_number in range(cards_list[card_type][0]):
                self.deck.append(Card(cards_name[0], cards_list[card_type]))
                cards_name.pop(0)
        # Fill hand with cards
        self.hand = []
        for hand_space in range(8):
            new_card = random.randint(1, len(self.deck) - 1)  # Generating a random number to draw
            self.hand.append(self.deck[new_card])  # Putting the card in the hand
            self.deck.pop(new_card)  # Putting the card out of the deck

    # Draw a card
    def draw_card(self):
        if len(self.deck) > 0:
            new_card = random.randint(0, len(self.deck) - 1)  # Generating a random number to draw
            for number in range(len(self.hand)):
                if self.hand[number] == "":
                    self.hand[number] = self.deck[new_card]
                    self.deck.pop(new_card)

    # Play a card
    def play_card(self, chosen_card):
        opponent = match.green_player if match.player_turn == "blue" else match.blue_player
        for action in self.hand[chosen_card].actions:
            if action[1] == "attack":
                attack_result = opponent.fence - action[2]
                if attack_result >= 0:
                    opponent.fence = attack_result
                else:
                    opponent.fence = 0
                    opponent.castle = opponent.castle + attack_result if opponent.castle + attack_result > 0 else 0
            elif action[1] == "steal_stocks":
                resource_types = ["bricks", "weapons", "crystals"]
                for resource in resource_types:
                    result = getattr(opponent, resource) - action[2]
                    if result >= 0:
                        setattr(opponent, resource, result)
                        setattr(self, resource, getattr(self, resource) + action[2])
                    else:
                        setattr(opponent, resource, 0)
                        setattr(self, resource, getattr(self, resource) + action[2] + result)
            else:
                # Action on Player
                if not action[0]:
                    setattr(self, action[1], getattr(self, action[1]) + action[2])
                    if getattr(self, action[1]) < 0:
                        setattr(self, action[1], 0)
                    elif getattr(self, action[1]) > 100:
                        setattr(self, action[1], 100)
                # Action on Opponent
                else:
                    setattr(opponent, action[1], getattr(opponent, action[1]) + action[2])
                    if getattr(opponent, action[1]) < 0:
                        setattr(opponent, action[1], 0)
        # Apply card cost on Player
        setattr(self, self.hand[chosen_card].resource,
                getattr(self, self.hand[chosen_card].resource) - self.hand[chosen_card].cost)
        # Set the card on last play
        match.last_card_played[0] = self.hand[chosen_card]
        # Set data on last played card
        match.last_card_played[1] = "play_blue" if match.player_turn == "blue" else "play_green"
        # Empty card location
        self.hand[chosen_card] = ""
        # Draw a new card
        self.draw_card()

    # Discard a card
    def discard_card(self, chosen_card):
        # Set the card on last play
        match.last_card_played[0] = self.hand[chosen_card]
        # Set data on last played card
        match.last_card_played[1] = "discard_blue" if match.player_turn == "blue" else "discard_green"
        # Empty card location
        self.hand[chosen_card] = ""
        # Draw a new card
        self.draw_card()

    # Gain per turn
    def gain_per_turn(self):
        self.bricks += self.builders
        self.weapons += self.soldiers
        self.crystals += self.magic


class BusinessPlayer(Player):
    def __init__(self):
        super().__init__()
        self.merchants = 10  # Player's Merchants
        self.gold = 32  # Player's Gold

        # Fill deck with cards
        self.deck = []
        cards_name = []
        # Getting card names
        for card_key, card_content in business_cards_list.items():
            for i in range(card_content[0]):
                cards_name.append(card_key)
        # Creating cards in the deck
        for card_type in business_cards_list:
            for card_number in range(business_cards_list[card_type][0]):
                self.deck.append(BusinessCard(cards_name[0], business_cards_list[card_type]))
                cards_name.pop(0)
        # Fill hand with cards
        self.hand = []
        for hand_space in range(8):
            new_card = random.randint(1, len(self.deck) - 1)  # Generating a random number to draw
            self.hand.append(self.deck[new_card])  # Putting the card in the hand
            self.deck.pop(new_card)  # Putting the card out of the deck

    def discard_card(self, chosen_card):
        self.gold += self.hand[chosen_card].gold_price
        super().discard_card(chosen_card)

    def gain_per_turn(self):
        super().gain_per_turn()
        self.gold += self.merchants
        if self.gold >= (2 * self.builders + 2 * self.soldiers + 2 * self.magic):
            self.gold -= (2 * self.builders + 2 * self.soldiers + 2 * self.magic)
        else:
            worker = []
            if self.builders > 0:
                worker.append('builders')
            if self.soldiers > 0:
                worker.append('soldiers')
            if self.magic > 0:
                worker.append('magic')
            selected_worker = random.choice(worker)
            if selected_worker == "builders":
                self.builders -= 1
            elif selected_worker == "soldiers":
                self.soldiers -= 1
            elif selected_worker == "magic":
                self.magic -= 1


class DevilPlayer(Player):
    def __init__(self):
        super().__init__()
        self.adepts = 3
        self.energy = 7

        # Fill deck with cards
        self.deck = []
        cards_name = []
        # Getting card names
        for card_key, card_content in devil_cards_list.items():
            for i in range(card_content[0]):
                cards_name.append(card_key)
        # Creating cards in the deck
        for card_type in devil_cards_list:
            for card_number in range(devil_cards_list[card_type][0]):
                self.deck.append(Card(cards_name[0], devil_cards_list[card_type]))
                cards_name.pop(0)
        # Fill hand with cards
        self.hand = []
        for hand_space in range(8):
            new_card = random.randint(1, len(self.deck) - 1)  # Generating a random number to draw
            self.hand.append(self.deck[new_card])  # Putting the card in the hand
            self.deck.pop(new_card)  # Putting the card out of the deck

    def gain_per_turn(self):
        super().gain_per_turn()
        self.energy += self.adepts


class Ia(Player):
    def __init__(self):
        super().__init__()
        self.playable_cards = []
        self.non_playable_cards = []

    # Finds index of a given card in the player's hand
    def get_card_index(self, desired_card):
        index = 0
        for card in range(len(self.hand)):
            if self.hand[card] == desired_card:
                return index
            else:
                index += 1
        return False

    def set_playable_cards(self):
        self.playable_cards = []
        for card in range(len(self.hand)):
            if getattr(self, self.hand[card].resource) >= self.hand[card].cost:
                self.playable_cards.append(self.hand[card])

    def get_opponent_playable_cards(self):
        opponent_playable_cards = []
        for card in range(len(match.blue_player.hand)):
            if getattr(match.blue_player, match.blue_player.hand[card].resource) >= match.blue_player.hand[card].cost:
                opponent_playable_cards.append(match.blue_player.hand[card])
        return opponent_playable_cards

    def set_non_playable_cards(self):
        self.non_playable_cards = []
        for card in range(len(self.hand)):
            if getattr(self, self.hand[card].resource) < self.hand[card].cost:
                self.non_playable_cards.append(self.hand[card])

    def get_defense_cards(self):
        defense_cards = []
        fence_cards = []
        castle_cards = []

        for card in range(len(self.playable_cards)):
            if self.playable_cards[card].actions[0][1] == "fence":
                fence_cards.append(self.playable_cards[card])
        fence_cards.sort(key=lambda x: x.actions[0][2])

        for card in range(len(self.playable_cards)):
            if self.playable_cards[card].actions[0][1] == "castle" and \
                    self.playable_cards[card].actions[0][2] > 1:
                castle_cards.append(self.playable_cards[card])
        castle_cards.sort(key=lambda x: x.actions[0][2])

        for card in range(len(castle_cards)):
            defense_cards.append(castle_cards[card])

        for card in range(len(fence_cards)):
            defense_cards.append(fence_cards[card])

        return defense_cards

    def get_opponent_defense_cards(self):
        opponent_cards = self.get_opponent_playable_cards()
        opponent_defense_cards = []

        for card in range(len(opponent_cards)):
            if opponent_cards[card].actions[0][1] == "castle" and \
                    opponent_cards[card].actions[0][2] > 0:
                opponent_defense_cards.append(opponent_cards[card])
        opponent_defense_cards.sort(key=lambda x: x.actions[0][2])
        return opponent_defense_cards

    def get_ressources_picker_cards(self):
        ressources_picker_cards = []

        if match.blue_player.bricks >= 5 and match.blue_player.weapons >= 5 and match.blue_player.crystals >= 5:
            for card in range(len(self.playable_cards)):
                if self.playable_cards[card].actions[0][1] == "steal_stocks":
                    ressources_picker_cards.append(self.playable_cards[card])

        if match.blue_player.bricks >= 4 and match.blue_player.weapons >= 4 and match.blue_player.crystals >= 4:
            for card in range(len(self.playable_cards)):
                if self.playable_cards[card].actions[0][1] == "bricks" and \
                        self.playable_cards[card].actions[0][2] == -4:
                    ressources_picker_cards.append(self.playable_cards[card])

        if match.blue_player.bricks >= 8:
            for card in range(len(self.playable_cards)):
                if self.playable_cards[card].actions[0][1] == "bricks" and \
                        self.playable_cards[card].actions[0][2] == -8:
                    ressources_picker_cards.append(self.playable_cards[card])

        if match.blue_player.weapons >= 8:
            for card in range(len(self.playable_cards)):
                if self.playable_cards[card].actions[0][1] == "weapons" and \
                        self.playable_cards[card].actions[0][2] == -8:
                    ressources_picker_cards.append(self.playable_cards[card])

        if match.blue_player.crystals >= 8:
            for card in range(len(self.playable_cards)):
                if self.playable_cards[card].actions[0][1] == "crystals" and \
                        self.playable_cards[card].actions[0][2] == -8:
                    ressources_picker_cards.append(self.playable_cards[card])

        # for card in range(len(self.playable_cards)):
        #     if (self.playable_cards[card].actions[0][1] == "bricks" or
        #         self.playable_cards[card].actions[0][1] == "weapons" or
        #         self.playable_cards[card].actions[0][1] == "crystals") and \
        #             self.playable_cards[card].actions[0][2] == 8:
        #         ressources_picker_cards.append(self.playable_cards[card])
        #
        # for card in range(len(self.playable_cards)):
        #     if (self.playable_cards[card].actions[0][1] == "bricks" and
        #         self.playable_cards[card].actions[0][2]) == -4 or \
        #             self.playable_cards[card].actions[0][1] == "steal_stocks":
        #         ressources_picker_cards.append(self.playable_cards[card])
        #
        # for card in range(len(self.playable_cards)):
        #     if (self.playable_cards[card].actions[0][1] == "bricks" or
        #         self.playable_cards[card].actions[0][1] == "weapons" or
        #         self.playable_cards[card].actions[0][1] == "crystals") and \
        #             self.playable_cards[card].actions[0][2] == -8:
        #         ressources_picker_cards.append(self.playable_cards[card])

        return ressources_picker_cards

    def get_attack_cards(self):
        attack_cards = []
        non_castle_attack_cards = []

        for card in range(len(self.playable_cards)):
            if self.playable_cards[card].actions[0][1] == "castle" and \
                    self.playable_cards[card].actions[0][2] < 0:
                attack_cards.append(self.playable_cards[card])
        attack_cards.sort(key=lambda x: x.actions[0][2])

        for card in range(len(self.playable_cards)):
            if self.playable_cards[card].actions[0][1] == "attack":
                non_castle_attack_cards.append(self.playable_cards[card])
        non_castle_attack_cards.sort(key=lambda x: x.actions[0][2])

        for card in range(len(non_castle_attack_cards)):
            attack_cards.append(non_castle_attack_cards[card])
        return attack_cards

    def get_opponent_attack_cards(self):
        opponent_cards = self.get_opponent_playable_cards()
        attack_opponent_cards = []
        castle_attack_cards = []

        for card in range(len(opponent_cards)):
            if opponent_cards[card].actions[0][1] == "castle" and \
                    opponent_cards[card].actions[0][2] < 0:
                castle_attack_cards.append(opponent_cards[card])
        castle_attack_cards.sort(key=lambda x: x.actions[0][2])

        for card in range(len(castle_attack_cards)):
            attack_opponent_cards.append(castle_attack_cards[card])

        for card in range(len(opponent_cards)):
            if opponent_cards[card].actions[0][1] == "attack":
                attack_opponent_cards.append(opponent_cards[card])
        attack_opponent_cards.sort(key=lambda x: x.actions[0][2])
        return attack_opponent_cards

    def get_lap_bonus_cards(self):
        lap_bonus_cards = []

        for card in range(len(self.playable_cards)):
            if self.playable_cards[card].actions[0][1] == "builders" or \
                    self.playable_cards[card].actions[0][1] == "soldiers" or \
                    self.playable_cards[card].actions[0][1] == "magic":
                lap_bonus_cards.append(self.playable_cards[card])
        return lap_bonus_cards

    def get_curse_card(self):
        curse_cards = []

        for card in range(len(self.playable_cards)):
            if self.playable_cards[card].actions[0][1] == "castle" and \
                    self.playable_cards[card].actions[0][2] == 1:
                curse_cards.append(self.playable_cards[card])
        return curse_cards

    # Determines whether it is better to defend or attack based on the cards available
    # Or even discard a useless card
    def attack_or_defense(self):
        opponent_fence = match.blue_player.fence
        if len(self.get_attack_cards()) > 0:
            if self.get_attack_cards()[0].actions[0][1] == "castle":
                attack = self.get_attack_cards()[0].actions[0][2]
            else:
                attack = self.get_attack_cards()[0].actions[0][2] - match.blue_player.fence
        if len(self.get_attack_cards()) > 0 and len(self.get_defense_cards()) > 0:
            if attack > self.get_defense_cards()[0].actions[0][2]:
                return 1
            else:
                if self.get_defense_cards()[0].actions[0][1] == "fence":
                    if self.fence > opponent_fence:
                        if attack < -30:
                            return 3
                        return 1
                    else:
                        if self.fence > 40:
                            return 4
                        return 2
                return 2
        elif len(self.get_attack_cards()) > 0:
            if self.get_attack_cards()[0].actions[0][1] == "castle":
                return 1
            else:
                if attack > -30:
                    return 1
                return 3
        elif len(self.get_defense_cards()) > 0:
            if self.get_defense_cards()[0].actions[0][1] == "castle":
                return 2
            else:
                if self.fence > 40:
                    return 4
                return 2
        return 0

    def pick_useless_card(self):
        for card in range(len(self.non_playable_cards)):
            if self.non_playable_cards[card].actions[0][1] == "crystals" or \
                    self.non_playable_cards[card].actions[0][1] == "weapons" or \
                    self.non_playable_cards[card].actions[0][1] == "bricks":
                return self.non_playable_cards[card]

        if len(self.non_playable_cards) > 0:
            return self.non_playable_cards[0]
        else:
            return self.playable_cards[0]

    def can_loose(self):
        attack_opponent_cards = self.get_opponent_attack_cards()
        defense_opponent_cards = self.get_opponent_defense_cards()
        if len(attack_opponent_cards) > 0:
            if attack_opponent_cards[0].actions[0][1] == "castle":
                if self.castle - attack_opponent_cards[0].actions[0][2] <= 0:
                    return 1
            else:
                if self.castle + self.fence - attack_opponent_cards[0].actions[0][2] <= 0:
                    return 1
        if len(defense_opponent_cards) > 0:
            if match.blue_player.castle + defense_opponent_cards[0].actions[0][2] >= 100:
                return 2
        return 0

    def can_win(self):
        attack_cards = self.get_attack_cards()
        defense_cards = self.get_defense_cards()
        if len(attack_cards) > 0:
            if attack_cards[0].actions[0][1] == "castle":
                if match.blue_player.castle - attack_cards[0].actions[0][2] <= 0:
                    return 1
            else:
                if match.blue_player.castle + match.blue_player.fence - attack_cards[0].actions[0][2] <= 0:
                    return 1
        if len(defense_cards) > 0:
            if defense_cards[0].actions[0][1] == "castle":
                if self.castle + defense_cards[0].actions[0][2] >= 100:
                    return 2
        return 0

    def chose_card(self):
        self.set_playable_cards()
        self.set_non_playable_cards()

        action = self.attack_or_defense()

        if self.can_win() == 1:
            self.play_card(self.get_card_index(self.get_attack_cards()[0]))
        elif self.can_win() == 2:
            self.play_card(self.get_card_index(self.get_defense_cards()[0]))
        elif self.can_loose() == 1 and len(self.get_defense_cards()) > 0:
            self.play_card(self.get_card_index(self.get_defense_cards()[0]))
        elif self.can_loose() == 2 and len(self.get_attack_cards()) > 0:
            self.play_card(self.get_card_index(self.get_attack_cards()[0]))

        if len(self.get_lap_bonus_cards()) > 0:
            self.play_card(self.get_card_index(self.get_lap_bonus_cards()[0]))
        elif len(self.get_curse_card()) > 0:
            self.play_card(self.get_card_index(self.get_curse_card()[0]))
        elif len(self.get_ressources_picker_cards()) > 0:
            self.play_card(self.get_card_index(self.get_ressources_picker_cards()[0]))
        elif action == 1:
            self.play_card(self.get_card_index(self.get_attack_cards()[0]))
        elif action == 2:
            self.play_card(self.get_card_index(self.get_defense_cards()[0]))
        elif action == 3:
            self.discard_card(self.get_card_index(self.get_attack_cards()[-1]))
        elif action == 4:
            self.discard_card(self.get_card_index(self.get_defense_cards()[-1]))
        else:
            self.discard_card(self.get_card_index(self.pick_useless_card()))


# Card format :
# [Cards Quantity, Resource type, cost, [[Player focused, Resource edit, Edit number], then loop..], [Card description]]
# Player focused : 0 = Self, 1 Opponent
cards_list = {
    # Bricks card
    "Wall": [3, "bricks", 1, [[0, "fence", 3]], ["Fence +3"]],
    "Base": [3, "bricks", 1, [[0, "castle", 2]], ["Castle +2"]],
    "Defence": [3, "bricks", 3, [[0, "fence", 6]], ["Fence +6"]],
    "Reserve": [3, "bricks", 3, [[0, "castle", 8], [0, "fence", -4]], ["Castle +8", "Fence -4"]],
    "Tower": [3, "bricks", 5, [[0, "castle", 5]], ["Castle +5"]],
    "School": [3, "bricks", 8, [[0, "builders", 1]], ["Builders +1"]],
    "Wain": [2, "bricks", 10, [[0, "castle", 8], [1, "castle", -4]], ["Castle +8", "Enemy castle -4"]],
    "Fence": [2, "bricks", 12, [[0, "fence", 22]], ["Fence +22"]],
    "Fort": [2, "bricks", 18, [[0, "castle", 20]], ["Castle +20"]],
    "Babylon": [2, "bricks", 39, [[0, "castle", 32]], ["Castle +32"]],
    # Weapons card
    "Archer": [3, "weapons", 1, [[1, "attack", 2]], ["Attack : 2"]],
    "Knight": [3, "weapons", 2, [[1, "attack", 3]], ["Attack : 3"]],
    "Rider": [3, "weapons", 2, [[1, "attack", 4]], ["Attack : 4"]],
    "Platoon": [3, "weapons", 4, [[1, "attack", 6]], ["Attack : 6"]],
    "Recruit": [3, "weapons", 8, [[0, "soldiers", 1]], ["Soldiers +1"]],
    "Attack": [2, "weapons", 10, [[1, "attack", 12]], ["Attack : 12"]],
    "Saboteur": [2, "weapons", 12, [[1, "bricks", -4], [1, "weapons", -4], [1, "crystals", -4]], ["Enemy stocks -4"]],
    "Thief": [2, "weapons", 15, [[1, "steal_stocks", 5]], ["Transfer enemy", "stocks : 5"]],
    "Swat": [2, "weapons", 18, [[1, "castle", -10]], ["Enemy castle -10"]],
    "Banshee": [2, "weapons", 28, [[1, "attack", 32]], ["Attack : 32"]],
    # Crystals card
    "Conjure bricks": [3, "crystals", 4, [[0, "bricks", 8]], ["Bricks +8"]],
    "Conjure crystals": [3, "crystals", 4, [[0, "crystals", 8]], ["Crystals +8"]],
    "Conjure weapons": [3, "crystals", 4, [[0, "weapons", 8]], ["Weapons +8"]],
    "Crush bricks": [3, "crystals", 4, [[1, "bricks", -8]], ["Enemy bricks -8"]],
    "Crush crystals": [3, "crystals", 4, [[1, "crystals", -8]], ["Enemy crystals -8"]],
    "Crush weapons": [3, "crystals", 4, [[1, "weapons", -8]], ["Enemy weapons -8"]],
    "Sorcerer": [3, "crystals", 8, [[0, "magic", 1]], ["Magic +1"]],
    "Dragon": [2, "crystals", 21, [[1, "attack", 25]], ["Attack : 25"]],
    "Pixies": [2, "crystals", 22, [[0, "castle", 22]], ["Castle +22"]],
    "Curse": [2, "crystals", 45, [[0, "castle", 1], [0, "fence", 1], [0, "builders", 1],
                                  [0, "bricks", 1], [0, "soldiers", 1], [0, "weapons", 1],
                                  [0, "magic", 1], [0, "crystals", 1],
                                  [1, "castle", -1], [1, "fence", -1], [1, "builders", -1],
                                  [1, "bricks", -1], [1, "soldiers", -1], [1, "weapons", -1],
                                  [1, "magic", -1], [1, "crystals", -1]],
              ["All +1", "Enemy all -1"]]
}

# Card format :
# [Cards Quantity, Resource type, cost, [[Player focused, Resource edit, Edit number], then loop..],
# [Card description], gold_price]
# Player focused : 0 = Self, 1 Opponent
business_cards_list = {
    # Bricks card
    "Wall": [3, "bricks", 1, [[0, "fence", 3]], ["Fence +3"], 2],
    "Base": [3, "bricks", 1, [[0, "castle", 2]], ["Castle +2"], 2],
    "Defence": [3, "bricks", 3, [[0, "fence", 6]], ["Fence +6"], 3],
    "Reserve": [3, "bricks", 3, [[0, "castle", 8], [0, "fence", -4]], ["Castle +8", "Fence -4"], 4],
    "Tower": [3, "bricks", 5, [[0, "castle", 5]], ["Castle +5"], 5],
    "School": [3, "bricks", 8, [[0, "builders", 1]], ["Builders +1"], 10],
    "Wain": [2, "bricks", 10, [[0, "castle", 8], [1, "castle", -4]], ["Castle +8", "Enemy castle -4"], 12],
    "Fence": [2, "bricks", 12, [[0, "fence", 22]], ["Fence +22"], 15],
    "Fort": [2, "bricks", 18, [[0, "castle", 20]], ["Castle +20"], 15],
    "Babylon": [2, "bricks", 39, [[0, "castle", 32]], ["Castle +32"], 40],
    # Weapons card
    "Archer": [3, "weapons", 1, [[1, "attack", 2]], ["Attack : 2"], 2],
    "Knight": [3, "weapons", 2, [[1, "attack", 3]], ["Attack : 3"], 2],
    "Rider": [3, "weapons", 2, [[1, "attack", 4]], ["Attack : 4"], 2],
    "Platoon": [3, "weapons", 4, [[1, "attack", 6]], ["Attack : 6"], 5],
    "Recruit": [3, "weapons", 8, [[0, "soldiers", 1]], ["Soldiers +1"], 10],
    "Attack": [2, "weapons", 10, [[1, "attack", 12]], ["Attack : 12"], 12],
    "Saboteur": [2, "weapons", 12, [[1, "bricks", -4], [1, "weapons", -4], [1, "crystals", -4]],
                 ["Enemy stocks -4"], 15],
    "Thief": [2, "weapons", 15, [[1, "steal_stocks", 5]], ["Transfer enemy", "stocks : 5"], 20],
    "Swat": [2, "weapons", 18, [[1, "castle", -10]], ["Enemy castle -10"], 20],
    "Banshee": [2, "weapons", 28, [[1, "attack", 32]], ["Attack : 32"], 30],
    # Crystals card
    "Conjure bricks": [3, "crystals", 4, [[0, "bricks", 8]], ["Bricks +8"], 5],
    "Conjure crystals": [3, "crystals", 4, [[0, "crystals", 8]], ["Crystals +8"], 5],
    "Conjure weapons": [3, "crystals", 4, [[0, "weapons", 8]], ["Weapons +8"], 5],
    "Crush bricks": [3, "crystals", 4, [[1, "bricks", -8]], ["Enemy bricks -8"], 5],
    "Crush crystals": [3, "crystals", 4, [[1, "crystals", -8]], ["Enemy crystals -8"], 5],
    "Crush weapons": [3, "crystals", 4, [[1, "weapons", -8]], ["Enemy weapons -8"], 5],
    "Sorcerer": [3, "crystals", 8, [[0, "magic", 1]], ["Magic +1"], 10],
    "Dragon": [2, "crystals", 21, [[1, "attack", 25]], ["Attack : 25"], 30],
    "Pixies": [2, "crystals", 22, [[0, "castle", 22]], ["Castle +22"], 30],
    "Curse": [2, "crystals", 45, [[0, "castle", 1], [0, "fence", 1], [0, "builders", 1],
                                  [0, "bricks", 1], [0, "soldiers", 1], [0, "weapons", 1],
                                  [0, "magic", 1], [0, "crystals", 1],
                                  [1, "castle", -1], [1, "fence", -1], [1, "builders", -1],
                                  [1, "bricks", -1], [1, "soldiers", -1], [1, "weapons", -1],
                                  [1, "magic", -1], [1, "crystals", -1]],
              ["All +1", "Enemy all -1"], 10],
    # Gold card
    "Purse": [3, "gold", 0, [[0, "gold", 10]], ["Gold +10"], 0],
    "Welcome trade": [3, "gold", 5, [[0, "merchants", 2]], ["Merchants +1"], 0],
    "Misappropriation": [3, "weapons", 1, [[1, "gold", -10]], ["Enemy gold -10"], 0],
    "New road": [3, "bricks", 5, [[0, "merchants", 5]], ["Merchants +5"], 20],
    "Ambush": [3, "weapons", 10, [[1, "merchants", -3]], ["Enemy merchants -3"], 10],
    "Kidnapping": [3, "weapons", 5, [[0, "merchants", 1], [1, "merchants", -1]],
                   ["Merchants +1", "Enemy merchants -1"], 7],
    "Commercial route": [2, "bricks", 20, [[0, "merchants", 15], [1, "merchants", 5]],
                         ["Merchants +15", "Enemy merchants +5"], 25],
    "Sell lands": [2, "gold", 0, [[0, "gold", 100], [0, "bricks", -5], [0, "weapons", -5], [0, "crystals", -5]],
                   ["Gold +100", "All resources -5"], 10],
    "Buy a kingdom": [2, "gold", 200, [[0, "bricks", +10], [0, "weapons", +10], [0, "crystals", +10],
                                       [0, "builders", +1], [0, "soldiers", +1], [0, "magic", +1]],
                      ["All workers +1", "All resources +10"], 10],
    "Corruption": [2, "gold", 20, [[0, "soldiers", 1], [1, "soldiers", -1]],
                   ["Soldiers +1", "Enemy soldiers -1"], 10]

}

# Card format :
# [Cards Quantity, Resource type, cost, [[Player focused, Resource edit, Edit number], then loop..], [Card description]]
# Player focused : 0 = Self, 1 Opponent
devil_cards_list = {
    # Bricks card
    "Wall": [3, "bricks", 1, [[0, "fence", 3]], ["Fence +3"]],
    "Base": [3, "bricks", 1, [[0, "castle", 2]], ["Castle +2"]],
    "Defence": [3, "bricks", 3, [[0, "fence", 6]], ["Fence +6"]],
    "Reserve": [3, "bricks", 3, [[0, "castle", 8], [0, "fence", -4]], ["Castle +8", "Fence -4"]],
    "Tower": [3, "bricks", 5, [[0, "castle", 5]], ["Castle +5"]],
    "School": [4, "bricks", 8, [[0, "builders", 1]], ["Builders +1"]],
    "Wain": [2, "bricks", 10, [[0, "castle", 8], [1, "castle", -4]], ["Castle +8", "Enemy castle -4"]],
    "Fence": [2, "bricks", 12, [[0, "fence", 22]], ["Fence +22"]],
    "Fort": [2, "bricks", 18, [[0, "castle", 20]], ["Castle +20"]],
    "Babylon": [2, "bricks", 39, [[0, "castle", 32]], ["Castle +32"]],
    # Weapons card
    "Archer": [3, "weapons", 1, [[1, "attack", 2]], ["Attack : 2"]],
    "Knight": [3, "weapons", 2, [[1, "attack", 3]], ["Attack : 3"]],
    "Rider": [3, "weapons", 2, [[1, "attack", 4]], ["Attack : 4"]],
    "Platoon": [3, "weapons", 4, [[1, "attack", 6]], ["Attack : 6"]],
    "Recruit": [4, "weapons", 8, [[0, "soldiers", 1]], ["Soldiers +1"]],
    "Attack": [2, "weapons", 10, [[1, "attack", 12]], ["Attack : 12"]],
    "Saboteur": [2, "weapons", 12, [[1, "bricks", -4], [1, "weapons", -4], [1, "crystals", -4]], ["Enemy stocks -4"]],
    "Thief": [2, "weapons", 15, [[1, "steal_stocks", 5]], ["Transfer enemy", "stocks : 5"]],
    "Swat": [2, "weapons", 18, [[1, "castle", -10]], ["Enemy castle -10"]],
    "Banshee": [2, "weapons", 28, [[1, "attack", 32]], ["Attack : 32"]],
    # Crystals card
    "Conjure bricks": [3, "crystals", 4, [[0, "bricks", 8]], ["Bricks +8"]],
    "Conjure crystals": [3, "crystals", 4, [[0, "crystals", 8]], ["Crystals +8"]],
    "Conjure weapons": [3, "crystals", 4, [[0, "weapons", 8]], ["Weapons +8"]],
    "Crush bricks": [3, "crystals", 4, [[1, "bricks", -8]], ["Enemy bricks -8"]],
    "Crush crystals": [3, "crystals", 4, [[1, "crystals", -8]], ["Enemy crystals -8"]],
    "Crush weapons": [3, "crystals", 4, [[1, "weapons", -8]], ["Enemy weapons -8"]],
    "Sorcerer": [4, "crystals", 8, [[0, "magic", 1]], ["Magic +1"]],
    "Dragon": [2, "crystals", 21, [[1, "attack", 25]], ["Attack : 25"]],
    "Pixies": [2, "crystals", 22, [[0, "castle", 22]], ["Castle +22"]],
    "Curse": [2, "crystals", 45, [[0, "castle", 1], [0, "fence", 1], [0, "builders", 1],
                                  [0, "bricks", 1], [0, "soldiers", 1], [0, "weapons", 1],
                                  [0, "magic", 1], [0, "crystals", 1],
                                  [1, "castle", -1], [1, "fence", -1], [1, "builders", -1],
                                  [1, "bricks", -1], [1, "soldiers", -1], [1, "weapons", -1],
                                  [1, "magic", -1], [1, "crystals", -1]],
              ["All +1", "Enemy all -1"]],
    # Energy card
    "Pact": [3, "energy", 2, [[0, "castle", -2], [0, "energy", 5]], ["Energy +5", "Castle -2"]],
    "Slavery": [3, "energy", 2, [[0, "soldiers", -1], [0, "builders", 2], [0, "magic", -1]],
                ["Builders +2", "Soldiers -1", "Magic -1"]],
    "Ragnarok": [3, "energy", 2, [[0, "soldiers", 2], [0, "builders", -1], [0, "magic", -1]],
                 ["Soldiers +2", "Builders -1", "Magic -1"]],
    "Senility": [3, "energy", 2, [[0, "soldiers", -1], [0, "builders", -1], [0, "magic", 2]],
                 ["Magic +2", "Soldiers -1", "Builders -1"]],
    "Summon imp": [3, "energy", 2, [[1, "castle", -2]], ["Enemy castle -2"]],
    "Soul Brick": [3, "energy", 4, [[0, "castle", 2], [0, "fence", 3]], ["Castle +2", "Fence +3"]],
    "Devil trade": [3, "energy", 5, [[0, "castle", -4], [0, "bricks", 4], [0, "weapons", 4], [0, "crystals", 4]],
                    ["Castle -4", "All stocks +4"]],
    "Skull canon": [3, "energy", 5, [[1, "attack", 8]], ["Attack : 8"]],
    "Hell feast": [3, "energy", 6, [[0, "castle", -5], [1, "bricks", -4], [1, "weapons", -4], [1, "crystals", -4]],
                   ["Castle -5", "Enemy stocks -4"]],
    "Necronomicon": [3, "energy", 8, [[0, "adepts", 1]], ["Adepts +1"]],
    "Famine": [2, "energy", 8, [[1, "builders", -1]], ["Enemy builders -1"]],
    "War": [2, "energy", 8, [[1, "soldiers", -1]], ["Enemy soldiers -1"]],
    "Pestilence": [2, "energy", 8, [[1, "magic", -1]], ["Enemy magic -1"]],
    "Forced work": [2, "energy", 10, [[0, "bricks", 12], [0, "weapons", 12], [0, "crystals", 12], [0, "builders", -1],
                                      [0, "soldiers", -1], [0, "magic", -1]],
                    ["All stocks +12", "All non-adept", "workers -1"]],
    "Bone wall": [2, "energy", 10, [[0, "fence", 30], [0, "builders", -1]], ["Fence +30", "Builders -1"]],
    "Minion army": [2, "energy", 22, [[1, "attack", 10], [1, "bricks", -4], [1, "weapons", -4], [1, "crystals", -4]],
                    ["Attack : 10", "Enemy stocks -4"]],
    "Sacrifice": [2, "energy", 24, [[0, "castle", -15], [1, "castle", -30]], ["Castle -15", "Enemy Castle -30"]],
    "Death": [2, "energy", 30, [[1, "builders", -1], [1, "soldiers", -1], [1, "magic", -1]],
              ["All non-adept", "enemy workers -1"]],
    "Demon Lord": [2, "energy", 30, [[1, "attack", 34]], ["Attack : 34"]]
}


class Card:
    def __init__(self, card_name, card_content):
        self.name = card_name
        self.resource = card_content[1]
        self.cost = card_content[2]
        self.actions = card_content[3]
        self.description = card_content[4]


class BusinessCard(Card):
    def __init__(self, card_name, card_content):
        super().__init__(card_name, card_content)
        self.gold_price = card_content[5]


# Pygame Initialization
pygame.init()
FPS = 60
fpsClock = pygame.time.Clock()

# Display Window Icon
icon_app = pygame.image.load("Content\\Images\\Game_icon.png")
pygame.display.set_icon(icon_app)

# Set Screen Size
size_list = {"medium": [1280, 720],
             "high": [1600, 900],
             "maximum": [1920, 1080]}
list_ratio = {"medium": 1.5, "high": 1.2, "maximum": 1}
screen_size = "medium"
screen_ratio = list_ratio[screen_size]
user32 = ctypes.windll.user32

# Enable Process DPI Aware for maximum size
if screen_size == "maximum":
    windll.user32.SetProcessDPIAware()

# Initialize screen
my_screen = pygame.display.set_mode((size_list[screen_size][0], size_list[screen_size][1]), pygame.FULLSCREEN)

# Set Screen Name
pygame.display.set_caption("Castlewars")

# Game's Initialization
castlewars = Game()
match = Match()

# Init Colors
DARK_GREY = (30, 30, 30)
LIGHT_GREY = (150, 150, 150)
WHITE = (255, 255, 255)
BLUE = (0, 80, 220)
GREEN = (0, 220, 80)
LIGHT_BROWN = (210, 155, 50)
BROWN = (140, 103, 33)
LIGHT_RED = (255, 60, 60)
RED = (170, 40, 40)
LIGHT_PURPLE = (120, 0, 255)
PURPLE = (80, 0, 170)
LIGHT_YELLOW = (220, 165, 0)
YELLOW = (150, 112, 0)
LIGHT_CYAN = (0, 200, 125)
CYAN = (0, 133, 42)

# Fill Screen with Dark Grey
my_screen.fill(DARK_GREY)

# Load Images
images = {
    "chucklefish": pygame.image.load("Content\\Images\\Credits\\Chucklefish_t.png"),
    "developers": pygame.image.load("Content\\Images\\Credits\\Developers_t.png"),
    "starbound": pygame.image.load("Content\\Images\\Credits\\Starbound_t.png"),
    "fade": pygame.image.load("Content\\Images\\Fade_black.png"),
    "menu_t": pygame.image.load("Content\\Images\\Menu\\Menu_back_t.png"),
    "menu": pygame.image.load("Content\\Images\\Menu\\Menu_back.png"),
    "menu_game_choice": pygame.image.load("Content\\Images\\Menu\\Menu_game_choice.png"),
    "menu_game_standard": pygame.image.load("Content\\Images\\Menu\\Menu_game_standard.png"),
    "menu_game_custom": pygame.image.load("Content\\Images\\Menu\\Menu_game_custom.png"),
    "hover0": pygame.image.load("Content\\Images\\Menu\\hover0.png"),
    "hover1": pygame.image.load("Content\\Images\\Menu\\hover1.png"),
    "hover2": pygame.image.load("Content\\Images\\Menu\\hover2.png"),
    "exit": pygame.image.load("Content\\Images\\Menu\\Exit.png"),
    "exit_dark_hover": pygame.image.load("Content\\Images\\Menu\\Exit_dark_hover.png"),
    "exit_hover": pygame.image.load("Content\\Images\\Menu\\Exit_hover.png"),
    "replay": pygame.image.load("Content\\Images\\Menu\\Replay.png"),
    "replay_hover": pygame.image.load("Content\\Images\\Menu\\Replay_hover.png"),
    "builders": pygame.image.load("Content\\Images\\Icons\\Builders.png"),
    "bricks": pygame.image.load("Content\\Images\\Icons\\Bricks.png"),
    "soldiers": pygame.image.load("Content\\Images\\Icons\\Soldiers.png"),
    "weapons": pygame.image.load("Content\\Images\\Icons\\Weapons.png"),
    "magic": pygame.image.load("Content\\Images\\Icons\\Magic.png"),
    "crystals": pygame.image.load("Content\\Images\\Icons\\Crystals.png"),
    "merchants": pygame.image.load("Content\\Images\\Icons\\Merchants.png"),
    "gold": pygame.image.load("Content\\Images\\Icons\\Gold.png"),
    "adepts": pygame.image.load("Content\\Images\\Icons\\Adepts.png"),
    "energy": pygame.image.load("Content\\Images\\Icons\\Energy.png"),
    "day_background": pygame.image.load("Content\\Images\\Map\\Day.png"),
    "day_base": pygame.image.load("Content\\Images\\Map\\Day_base.png"),
    "night_background": pygame.image.load("Content\\Images\\Map\\Night.png"),
    "night_base": pygame.image.load("Content\\Images\\Map\\Night_base.png"),
    "sunrise_background": pygame.image.load("Content\\Images\\Map\\Sunrise.png"),
    "sunrise_base": pygame.image.load("Content\\Images\\Map\\Sunrise_base.png"),
    "sunset_background": pygame.image.load("Content\\Images\\Map\\Sunset.png"),
    "sunset_base": pygame.image.load("Content\\Images\\Map\\Sunset_base.png"),
    "players_data": pygame.image.load("Content\\Images\\Assets\\Day\\Players_data.png"),
    "players_data_custom": pygame.image.load("Content\\Images\\Assets\\Day\\Players_data_custom.png"),
    "facing_card": pygame.image.load("Content\\Images\\Cards\\Facing card.png"),
    "business_card_icons": pygame.image.load("Content\\Images\\Cards\\Business card icons.png"),
    "card_icons": pygame.image.load("Content\\Images\\Cards\\Card icons.png"),
    "discard_icon": pygame.image.load("Content\\Images\\Cards\\Discard icon.png"),
    "sell_icon": pygame.image.load("Content\\Images\\Cards\\Sell icon.png"),
    "no_play_icon": pygame.image.load("Content\\Images\\Cards\\No play icon.png"),
    "play_icon": pygame.image.load("Content\\Images\\Cards\\Play icon.png"),
    "blue_flag": pygame.image.load("Content\\Images\\Icons\\Flag Blue.png"),
    "green_flag": pygame.image.load("Content\\Images\\Icons\\Flag Green.png"),
    "castle_blue": pygame.image.load("Content\\Images\\Icons\\Blue Castle.png"),
    "fence_blue": pygame.image.load("Content\\Images\\Icons\\Blue Fence.png"),
    "castle_green": pygame.image.load("Content\\Images\\Icons\\Green Castle.png"),
    "fence_green": pygame.image.load("Content\\Images\\Icons\\Green Fence.png"),
    "victory": pygame.image.load("Content\\Images\\Assets\\Day\\Victory.png"),
    "blue_fence": pygame.image.load("Content\\Images\\Assets\\Day\\Blue_Player Fence.png"),
    "blue_fence_top": pygame.image.load("Content\\Images\\Assets\\Day\\Blue_Player Fence_top.png"),
    "blue_tower_4": pygame.image.load("Content\\Images\\Assets\\Day\\Blue_Player Tower_4.png"),
    "blue_tower_3": pygame.image.load("Content\\Images\\Assets\\Day\\Blue_Player Tower_3.png"),
    "blue_tower_2": pygame.image.load("Content\\Images\\Assets\\Day\\Blue_Player Tower_2.png"),
    "blue_tower_1": pygame.image.load("Content\\Images\\Assets\\Day\\Blue_Player Tower_1.png"),
    "blue_tower_0": pygame.image.load("Content\\Images\\Assets\\Day\\Blue_Player Tower_0.png"),
    "green_fence": pygame.image.load("Content\\Images\\Assets\\Day\\Green_Player Fence.png"),
    "green_fence_top": pygame.image.load("Content\\Images\\Assets\\Day\\Green_Player Fence_top.png"),
    "green_tower_4": pygame.image.load("Content\\Images\\Assets\\Day\\Green_Player Tower_4.png"),
    "green_tower_3": pygame.image.load("Content\\Images\\Assets\\Day\\Green_Player Tower_3.png"),
    "green_tower_2": pygame.image.load("Content\\Images\\Assets\\Day\\Green_Player Tower_2.png"),
    "green_tower_1": pygame.image.load("Content\\Images\\Assets\\Day\\Green_Player Tower_1.png"),
    "green_tower_0": pygame.image.load("Content\\Images\\Assets\\Day\\Green_Player Tower_0.png")
}

# Set Music files' Location to variables
menu_music = "content\\Music\\Bensound-Epic-Menu.mp3"
battle_music = "content\\Music\\Bensound-The-duel-Battle.mp3"

# Set Volume and Load Music files
pygame.mixer.music.set_volume(0.3)
pygame.mixer.music.load(menu_music)
pygame.mixer.music.play()
active_music = [time.time(), menu_music]


# Display any image
def display_image(image, position):
    image = pygame.transform.scale(image,
                                   (int(image.get_width() / screen_ratio), int(image.get_height() / screen_ratio)))
    position = (position[0] / screen_ratio, position[1] / screen_ratio)
    my_screen.blit(image, position)


# Function to write in the GUI
def write(text, text_size, text_color, text_position):
    font = pygame.font.Font("Content\\Police\\hobo.ttf", int(text_size / screen_ratio))
    content = font.render(text, True, text_color)
    text_position = (text_position[0] / screen_ratio, text_position[1] / screen_ratio)
    my_screen.blit(content, text_position)


# Edit Background Music
def change_background_music(new_music):
    pygame.mixer.music.fadeout(500)
    pygame.mixer.music.load(new_music)
    pygame.mixer.music.play()
    return [time.time(), new_music]


# Handle continuous background music
def handle_background_music(last_music_launched):
    if last_music_launched[1] == menu_music:
        if castlewars.get_step() in (-1, 0):
            if last_music_launched[0] + 178 < time.time():
                return change_background_music(menu_music)
        else:
            return change_background_music(battle_music)
    else:
        if castlewars.get_step() == 1:
            if last_music_launched[0] + 118 < time.time():
                return change_background_music(battle_music)
        else:
            return change_background_music(menu_music)
    return last_music_launched


# Fade to Black
def fade_to_black(iteration, start_iteration):
    images["fade"].set_alpha((iteration - start_iteration) * 3)
    my_screen.blit(images["fade"], (0, 0))


# Starting credits
def starting_credits(iteration):
    if iteration == 550:
        display_image(images["menu"], (0, 0))
        return 0
    elif iteration > 500:
        display_image(images["menu_t"], (0, 0))
    elif iteration == 498:
        my_screen.fill(DARK_GREY)
    elif iteration > 463:
        fade_to_black(iteration, 463)
    elif iteration > 263:
        display_image(images["starbound"], (1920 / 2 - images["starbound"].get_width() / 2,
                                            1080 / 2 - images["starbound"].get_height() / 2))
    elif iteration == 260:
        my_screen.fill(DARK_GREY)
    elif iteration > 225:
        fade_to_black(iteration, 225)
    elif iteration > 25:
        display_image(images["chucklefish"], (1920 / 2 - images["chucklefish"].get_width() / 2, 1080 // 15))
        display_image(images["developers"], (1920 / 2 - images["developers"].get_width() / 2, 1080 // 1.7))

    return -1


# Handle credits animations
def handle_credits(actual_game_frame):
    if (event.type == KEYDOWN and (event.key == K_RETURN or event.key == K_ESCAPE)) or \
            (event.type == MOUSEBUTTONDOWN and event.button == 1):
        if actual_game_frame < 260:
            return 260
        elif actual_game_frame < 498:
            return 498
        elif actual_game_frame < 550:
            return 550
    return actual_game_frame


# Menu handler
def menu_handler(active_game):
    # Handle events position
    mouse_x, mouse_y = pygame.mouse.get_pos()
    display_image(images["menu"], (0, 0))

    # Buttons position
    button_pos = [[730, 1190], [788, 1132], [847, 1073]]

    # Main menu handle
    if active_game.get_menu_step() == 0:
        # If user presses escape, game left
        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                active_game.set_in_progress(False)

        # Handle change game activity
        for button in range(3):
            if button_pos[button][0] / screen_ratio < mouse_x < button_pos[button][1] / screen_ratio:
                if (587 + 130 * button) / screen_ratio < mouse_y < (635 + 130 * button) / screen_ratio:
                    display_image(images["hover" + str(button)], (687 + 59 * button, 581 + 130 * button))
                    if event.type == MOUSEBUTTONDOWN and event.button == 1:
                        if button == 0:  # Play
                            active_game.set_menu_step(2)
                        elif button == 1:  # Options
                            pass
                        elif button == 2:  # Quit
                            active_game.set_in_progress(False)

    # Settings menu handle
    elif active_game.get_menu_step() == 1:
        pass

    # Game mods choice menu handle
    elif active_game.get_menu_step() == 2:
        display_image(images["menu_game_choice"], (0, 0))

        # If user presses escape, game left
        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                active_game.set_menu_step(0)

        # Handle change game activity
        for button in range(3):
            if button_pos[button][0] / screen_ratio < mouse_x < button_pos[button][1] / screen_ratio:
                if (587 + 130 * button) / screen_ratio < mouse_y < (635 + 130 * button) / screen_ratio:
                    display_image(images["hover" + str(button)], (687 + 59 * button, 581 + 130 * button))
                    if event.type == MOUSEBUTTONDOWN and event.button == 1:
                        if button == 0:  # Standard Games
                            active_game.set_menu_step(3)
                        elif button == 1:  # Custom Games
                            active_game.set_menu_step(4)
                        elif button == 2:  # Back
                            active_game.set_menu_step(0)

    # Game mods Standard
    elif active_game.get_menu_step() == 3:
        display_image(images["menu_game_standard"], (0, 0))

        # If user presses escape, game left
        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                active_game.set_menu_step(2)

        # Handle change game activity
        for button in range(3):
            if button_pos[button][0] / screen_ratio < mouse_x < button_pos[button][1] / screen_ratio:
                if (587 + 130 * button) / screen_ratio < mouse_y < (635 + 130 * button) / screen_ratio:
                    display_image(images["hover" + str(button)], (687 + 59 * button, 581 + 130 * button))
                    if event.type == MOUSEBUTTONDOWN and event.button == 1:
                        if button == 0:  # Player vs Player Game
                            active_game.set_step(1)
                            active_game.set_menu_step(0)
                        elif button == 1:  # Player vs IA Game
                            match.green_player = Ia()
                            match.match_type = 1
                            active_game.set_step(1)
                            active_game.set_menu_step(0)
                            pass
                        elif button == 2:  # Back
                            active_game.set_menu_step(2)

    # Game mods Custom
    elif active_game.get_menu_step() == 4:
        display_image(images["menu_game_custom"], (0, 0))

        # If user presses escape, game left
        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                active_game.set_menu_step(2)

        # Handle change game activity
        for button in range(3):
            if button_pos[button][0] / screen_ratio < mouse_x < button_pos[button][1] / screen_ratio:
                if (587 + 130 * button) / screen_ratio < mouse_y < (635 + 130 * button) / screen_ratio:
                    display_image(images["hover" + str(button)], (687 + 59 * button, 581 + 130 * button))
                    if event.type == MOUSEBUTTONDOWN and event.button == 1:
                        if button == 0:  # Business Warfare
                            match.blue_player = BusinessPlayer()
                            match.green_player = BusinessPlayer()
                            match.match_type = 2
                            active_game.set_step(1)
                            active_game.set_menu_step(0)
                        elif button == 1:  # Devil Army
                            match.blue_player = DevilPlayer()
                            match.green_player = DevilPlayer()
                            match.match_type = 3
                            active_game.set_step(1)
                            active_game.set_menu_step(0)
                        elif button == 2:  # Back
                            active_game.set_menu_step(2)

    return active_game


# Display Castles
def display_castles(active_match):
    # # # Display Content # # #
    tower_dic = [0, 10, 25, 50, 75]
    tower_max = [10, 25, 50, 75, 100]
    tower_height = [224, 314, 434, 564, 671]
    tower_ratio = [5, 6, 4.8, 5.2, 4.28]

    # Adapt background to the time of day
    display_image(images[active_match.time_of_day + "_background"], (0, 0))

    # Display Blue Player Tower
    for t in range(4, -1, -1):
        if active_match.blue_player.castle >= tower_dic[t]:
            display_image(images["blue_tower_" + str(t)],
                          (460, 814 - tower_height[t] +
                           ((tower_max[t] - active_match.blue_player.castle) * tower_ratio[t])))
            break

    # Display Green Player Tower
    for t in range(4, -1, -1):
        if active_match.green_player.castle >= tower_dic[t]:
            display_image(images["green_tower_" + str(t)],
                          (1220, 814 - tower_height[t] +
                           ((tower_max[t] - active_match.green_player.castle) * tower_ratio[t])))
            break

    # Display background base
    display_image(images[active_match.time_of_day + "_base"], (0, 814))


# Display Fences
def display_fences(active_match):
    # Display Blue Player Fence
    for blue_fence in range(1, active_match.blue_player.fence // 2 + 1):
        display_image(images["blue_fence"], (740, 1004 - blue_fence * 12))
    display_image(images["blue_fence_top"], (740, 950 - active_match.blue_player.fence // 2 * 12))

    # Display Green Player Fence
    for green_fence in range(1, active_match.green_player.fence // 2 + 1):
        display_image(images["green_fence"], (1090, 1004 - green_fence * 12))
    display_image(images["green_fence_top"], (1090, 950 - active_match.green_player.fence // 2 * 12))


# Display players data
def display_players_data(active_match):
    # Set a variable for y display
    y_custom = 0

    # Display Player's data
    if active_match.match_type in (0, 1):
        display_image(images["players_data"], (0, 0))
    else:
        y_custom = 1
        display_image(images["players_data_custom"], (0, 0))

    # Players color
    colors = ["blue", "green"]

    # Display Blue Flag
    display_image(images["blue_flag"], (124, 190 - y_custom * 120))
    write("Blue Player", 25, WHITE, (158, 195 - y_custom * 120))

    # Display Green Flag
    display_image(images["green_flag"], (1608, 190 - y_custom * 120))
    write("Green Player", 25, WHITE, (1642, 195 - y_custom * 120))

    # Display each data
    for player in range(2):
        display_image(images["castle_" + colors[player]], (98 + 1495 * player, 250 - y_custom * 120))
        write("Castle", 20, WHITE, (150 + 1495 * player, 255 - y_custom * 120))
        castle_value = active_match.blue_player.castle if not player \
            else active_match.green_player.castle
        write(str(castle_value), 20, WHITE, (300 + 1495 * player, 255 - y_custom * 120))

        display_image(images["fence_" + colors[player]], (100 + 1495 * player, 295 - y_custom * 120))
        write("Fence", 20, LIGHT_GREY, (150 + 1495 * player, 305 - y_custom * 120))
        fence_value = active_match.blue_player.fence if not player \
            else active_match.green_player.fence
        write(str(fence_value), 20, WHITE, (300 + 1495 * player, 305 - y_custom * 120))

        display_image(images["builders"], (99 + 1495 * player, 368 - y_custom * 120))
        write("Builders", 20, LIGHT_BROWN, (150 + 1495 * player, 375 - y_custom * 120))
        builders_value = active_match.blue_player.builders if not player \
            else active_match.green_player.builders
        write(str(builders_value), 20, WHITE, (300 + 1495 * player, 375 - y_custom * 120))

        display_image(images["bricks"], (105 + 1495 * player, 423 - y_custom * 120))
        write("Bricks", 20, BROWN, (150 + 1495 * player, 425 - y_custom * 120))
        bricks_value = active_match.blue_player.bricks if not player \
            else active_match.green_player.bricks
        write(str(bricks_value), 20, WHITE, (300 + 1495 * player, 425 - y_custom * 120))

        display_image(images["soldiers"], (101 + 1495 * player, 487 - y_custom * 120))
        write("Soldiers", 20, LIGHT_RED, (150 + 1495 * player, 495 - y_custom * 120))
        soldiers_value = active_match.blue_player.soldiers if not player \
            else active_match.green_player.soldiers
        write(str(soldiers_value), 20, WHITE, (300 + 1495 * player, 495 - y_custom * 120))

        display_image(images["weapons"], (99 + 1495 * player, 538 - y_custom * 120))
        write("Weapons", 20, RED, (150 + 1495 * player, 545 - y_custom * 120))
        weapons_value = active_match.blue_player.weapons if not player \
            else active_match.green_player.weapons
        write(str(weapons_value), 20, WHITE, (300 + 1495 * player, 545 - y_custom * 120))

        display_image(images["magic"], (98 + 1495 * player, 612 - y_custom * 120))
        write("Magic", 20, LIGHT_PURPLE, (150 + 1495 * player, 615 - y_custom * 120))
        magic_value = active_match.blue_player.magic if not player \
            else active_match.green_player.magic
        write(str(magic_value), 20, WHITE, (300 + 1495 * player, 615 - y_custom * 120))

        display_image(images["crystals"], (99 + 1495 * player, 660 - y_custom * 120))
        write("Crystals", 20, PURPLE, (150 + 1495 * player, 665 - y_custom * 120))
        crystals_value = active_match.blue_player.crystals if not player \
            else active_match.green_player.crystals
        write(str(crystals_value), 20, WHITE, (300 + 1495 * player, 665 - y_custom * 120))

        if active_match.match_type == 2:
            display_image(images["merchants"], (99 + 1495 * player, 730 - y_custom * 120))
            write("Merchants", 20, LIGHT_YELLOW, (150 + 1495 * player, 735 - y_custom * 120))
            merchants_value = active_match.blue_player.merchants if not player \
                else active_match.green_player.merchants
            write(str(merchants_value), 20, WHITE, (300 + 1495 * player, 735 - y_custom * 120))

            display_image(images["gold"], (99 + 1495 * player, 780 - y_custom * 120))
            write("Gold", 20, YELLOW, (150 + 1495 * player, 785 - y_custom * 120))
            gold_value = active_match.blue_player.gold if not player \
                else active_match.green_player.gold
            if not player:
                malus_gold_value = active_match.blue_player.builders * 2 + active_match.blue_player.soldiers * 2 \
                                   + active_match.blue_player.magic * 2
            else:
                malus_gold_value = active_match.green_player.builders * 2 + active_match.green_player.soldiers * 2 \
                                   + active_match.green_player.magic * 2
            next_gold = "+" + str(merchants_value - malus_gold_value) if merchants_value - malus_gold_value > 0 \
                else str(merchants_value - malus_gold_value)
            write(str(gold_value) + " (" + next_gold + ")", 20, WHITE, (250 + 1495 * player, 785 - y_custom * 120))

        elif active_match.match_type == 3:
            display_image(images["adepts"], (99 + 1495 * player, 730 - y_custom * 120))
            write("Adepts", 20, LIGHT_CYAN, (150 + 1495 * player, 735 - y_custom * 120))
            adepts_value = active_match.blue_player.adepts if not player \
                else active_match.green_player.adepts
            write(str(adepts_value), 20, WHITE, (300 + 1495 * player, 735 - y_custom * 120))

            display_image(images["energy"], (99 + 1495 * player, 775 - y_custom * 120))
            write("Energy", 20, CYAN, (150 + 1495 * player, 785 - y_custom * 120))
            energy_value = active_match.blue_player.energy if not player \
                else active_match.green_player.energy
            write(str(energy_value), 20, WHITE, (300 + 1495 * player, 785 - y_custom * 120))


# Display last card played
def display_last_card_played(active_match, position):
    last_card = active_match.last_card_played
    # Last card played
    display_image(images["facing_card"], position)
    if not last_card[0]:
        write("Last card", 20, LIGHT_GREY, (position[0] + 28, position[1] + 112))
        write("played", 20, LIGHT_GREY, (position[0] + 44, position[1] + 147))
    else:
        # Write card's name
        write(last_card[0].name, 16, LIGHT_GREY,
              ((position[0] + 71 - len(last_card[0].name) * 4), position[1] + 17))

        # Write card's cost
        write("Cost :", 15, LIGHT_GREY, (position[0] + 15, position[1] + 70))
        if last_card[0].resource == "bricks":
            display_image(images[last_card[0].resource], (position[0] + 82, position[1] + 67))
        else:
            display_image(images[last_card[0].resource], (position[0] + 75, position[1] + 65))
        write(str(last_card[0].cost), 20, LIGHT_GREY, (position[0] + 115, position[1] + 68))

        # Write card's gold price
        if active_match.match_type == 2:
            write("Price :", 15, LIGHT_GREY, (position[0] + 15, position[1] + 105))
            display_image(images["gold"], (position[0] + 77, position[1] + 97))
            write(str(last_card[0].gold_price), 20, LIGHT_GREY, (position[0] + 115, position[1] + 103))

            # Write card's description if business
            if len(last_card[0].description) == 1:
                write(last_card[0].description[0], 13, LIGHT_GREY,
                      (position[0] + 80 - len(last_card[0].description[0]) * 4, position[1] + 139))
            else:
                for num in range(len(last_card[0].description)):
                    write(last_card[0].description[num], 13, LIGHT_GREY,
                          (position[0] + 80 - len(last_card[0].description[num]) * 4, position[1] + 127 + 25 * num))

        elif active_match.match_type == 3:
            # Write card's description if devil
            if len(last_card[0].description) == 1:
                write(last_card[0].description[0], 15, LIGHT_GREY,
                      (position[0] + 74 - len(last_card[0].description[0]) * 4, position[1] + 129))
            else:
                y_pos = 117 if len(last_card[0].description) < 3 else 105
                for num in range(len(last_card[0].description)):
                    write(last_card[0].description[num], 15, LIGHT_GREY,
                          (position[0] + 74 - len(last_card[0].description[num]) * 4, position[1] + y_pos + 25 * num))

        else:
            # Write card's description
            if len(last_card[0].description) == 1:
                write(last_card[0].description[0], 15, LIGHT_GREY,
                      (position[0] + 74 - len(last_card[0].description[0]) * 4, position[1] + 129))
            else:
                for num in range(len(last_card[0].description)):
                    write(last_card[0].description[num], 15, LIGHT_GREY,
                          (position[0] + 74 - len(last_card[0].description[num]) * 4, position[1] + 117 + 25 * num))

        # Write card action
        if active_match.match_type == 2:
            discarded_msg = "Sold by"
            color_msg = LIGHT_YELLOW
        else:
            discarded_msg = "Discarded by"
            color_msg = RED
        cards_data = \
            {"play_blue": ["Played by", "Blue player", WHITE, BLUE],
             "play_green": ["Played by", "Green player", WHITE, GREEN],
             "discard_blue": [discarded_msg, "Blue player", color_msg, BLUE],
             "discard_green": [discarded_msg, "Green player", color_msg, GREEN]}
        write(cards_data[last_card[1]][0], 15, cards_data[last_card[1]][2], (position[0] + 32, position[1] + 175))
        write(cards_data[last_card[1]][1], 15, cards_data[last_card[1]][3], (position[0] + 32, position[1] + 200))


# Display cards
def display_cards(active_match):
    # Player's Turn
    display_image(images["facing_card"], (732, 135))
    write("Player's Turn", 20, LIGHT_GREY, (743, 150))
    if active_match.player_turn == "blue":
        write("Blue Player", 20, BLUE, (753, 260))
    else:
        write("Green Player", 20, GREEN, (745, 260))

    # Display last played card
    display_last_card_played(active_match, (1038, 135))

    # Active player's cards
    player = active_match.blue_player if active_match.player_turn == "blue" else active_match.green_player

    # Display the 8 cards in the player's hands
    for card in range(8):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        # Set cards
        display_image(images["facing_card"], (255 + 180 * card, 805))

        # Verify if there is a card
        if player.hand[card] != '':
            # Highlight playable cards
            if active_match.match_type == 2:
                if getattr(player, player.hand[card].resource) >= player.hand[card].cost and player.gold >= player.hand[
                    card].gold_price and ((player.hand[card].name == "Reserve" and getattr(player, "fence") >= 4)
                                          or (player.hand[card].name == "Sell lands" and getattr(player, "bricks") >= 5
                                              and getattr(player, "weapons") >= 5 and getattr(player, "crystals") >= 5)
                                          or (player.hand[card].name != "Reserve"
                                              and player.hand[card].name != "Sell lands")):
                    display_image(images["facing_card"], (255 + 180 * card, 805))
            else:
                if getattr(player, player.hand[card].resource) >= player.hand[card].cost \
                        and ((player.hand[card].name == "Reserve" and getattr(player, "fence") >= 4)
                             or player.hand[card].name != "Reserve"):
                    display_image(images["facing_card"], (255 + 180 * card, 805))

            # Hover on a card
            if (255 + 180 * card) / screen_ratio < mouse_x < (225 + 180 * (card + 1)) / screen_ratio:
                if 805 / screen_ratio < mouse_y < 1060 / screen_ratio:
                    # Display use/discard icons
                    if active_match.match_type == 2:
                        display_image(images["business_card_icons"], (255 + 180 * card, 980))
                    else:
                        display_image(images["card_icons"], (255 + 180 * card, 980))
                    if 980 / screen_ratio < mouse_y < (980 + 35) / screen_ratio:
                        if (288 + 180 * card) / screen_ratio < mouse_x < (313 + 180 * card) / screen_ratio:
                            if active_match.match_type == 2:
                                display_image(images["sell_icon"], (255 + 180 * card, 980))
                                write("Sell?", 15, LIGHT_YELLOW, (270 + 180 * card, 1017))
                            else:
                                display_image(images["discard_icon"], (255 + 180 * card, 980))
                                write("Discard?", 15, RED, (270 + 180 * card, 1017))
                        elif (348 + 180 * card) / screen_ratio < mouse_x < (373 + 180 * card) / screen_ratio:
                            # Handle use icon
                            if getattr(player, player.hand[card].resource) >= player.hand[card].cost:
                                # Check if card is Reserve (Switch Fence for Castle), need more than 4 Fence
                                if active_match.match_type == 2:
                                    if player.gold < player.hand[card].gold_price:
                                        display_image(images["no_play_icon"], (255 + 180 * card, 980))
                                        write("Lack golds", 15, RED, (275 + 180 * card, 1017))
                                    elif player.hand[card].name == "Reserve" and getattr(player, "fence") < 4:
                                        display_image(images["no_play_icon"], (255 + 180 * card, 980))
                                        write("Lack fences", 15, RED, (275 + 180 * card, 1017))
                                    elif player.hand[card].name == "Sell lands" and getattr(player, "bricks") < 5 \
                                            and getattr(player, "weapons") < 5 and getattr(player, "crystals") < 5:
                                        display_image(images["no_play_icon"], (255 + 180 * card, 980))
                                        write("Lack resources", 15, RED, (275 + 180 * card, 1017))
                                    else:
                                        display_image(images["play_icon"], (255 + 180 * card, 980))
                                        write("Play?", 15, GREEN, (345 + 180 * card, 1017))
                                elif player.hand[card].name == "Reserve" and getattr(player, "fence") < 4:
                                    display_image(images["no_play_icon"], (255 + 180 * card, 980))
                                    write("Lack fences", 15, RED, (275 + 180 * card, 1017))
                                else:
                                    display_image(images["play_icon"], (255 + 180 * card, 980))
                                    write("Play?", 15, GREEN, (345 + 180 * card, 1017))
                            else:
                                display_image(images["no_play_icon"], (255 + 180 * card, 980))
                                write("Lack resources", 15, RED, (275 + 180 * card, 1017))

            # Write card's name
            write(player.hand[card].name, 16, LIGHT_GREY, ((326 - len(player.hand[card].name) * 4) + 180 * card, 822))

            # Write card's cost
            write("Cost :", 15, LIGHT_GREY, (270 + 180 * card, 875))
            if player.hand[card].resource == "bricks":
                display_image(images[player.hand[card].resource], (340 + 180 * card, 872))
            else:
                display_image(images[player.hand[card].resource], (330 + 180 * card, 870))
            write(str(player.hand[card].cost), 20, LIGHT_GREY, (370 + 180 * card, 873))

            # Write card's gold price
            if active_match.match_type == 2:
                write("Price :", 15, LIGHT_GREY, (270 + 180 * card, 910))
                display_image(images["gold"], (330 + 180 * card, 900))
                write(str(player.hand[card].gold_price), 20, LIGHT_GREY, (370 + 180 * card, 910))

                # Write card's description if business
                if len(player.hand[card].description) == 1:
                    write(player.hand[card].description[0], 13, LIGHT_GREY,
                          ((335 - len(player.hand[card].description[0]) * 4) + 180 * card, 940))
                else:
                    for num in range(len(player.hand[card].description)):
                        write(player.hand[card].description[num], 13, LIGHT_GREY,
                              ((335 - len(player.hand[card].description[num]) * 4) + 180 * card, 940 + 25 * num))

            elif active_match.match_type == 3:
                # Write card's description if devil
                if len(player.hand[card].description) == 1:
                    write(player.hand[card].description[0], 15, LIGHT_GREY,
                          ((329 - len(player.hand[card].description[0]) * 4) + 180 * card, 934))
                else:
                    y_pos = 922 if len(player.hand[card].description) < 3 else 910
                    for num in range(len(player.hand[card].description)):
                        write(player.hand[card].description[num], 15, LIGHT_GREY,
                              ((329 - len(player.hand[card].description[num]) * 4) + 180 * card, y_pos + 25 * num))

            else:
                # Write card's description
                if len(player.hand[card].description) == 1:
                    write(player.hand[card].description[0], 15, LIGHT_GREY,
                          ((329 - len(player.hand[card].description[0]) * 4) + 180 * card, 934))
                else:
                    for num in range(len(player.hand[card].description)):
                        write(player.hand[card].description[num], 15, LIGHT_GREY,
                              ((329 - len(player.hand[card].description[num]) * 4) + 180 * card, 922 + 25 * num))

        # Display empty if no card can be drawn
        else:
            write("No card", 20, LIGHT_GREY, (291 + 180 * card, 917))
            write("left", 20, LIGHT_GREY, (309 + 180 * card, 952))


# Display exit settings/buttons
def display_exit_settings(active_match):
    mouse_x, mouse_y = pygame.mouse.get_pos()
    if active_match.status:
        display_image(images["exit"], (-75, 945))
        display_image(images["exit_dark_hover"], (-75, 945))
        if 0 / screen_ratio < mouse_x < 225 / screen_ratio:
            if 945 / screen_ratio < mouse_y < 1005 / screen_ratio:
                display_image(images["exit_hover"], (-75, 945))
    else:
        display_image(images["replay"], (785, 637))
        display_image(images["exit"], (810, 732))
        if 785 / screen_ratio < mouse_x < 1135 / screen_ratio:
            if 637 / screen_ratio < mouse_y < 697 / screen_ratio:
                display_image(images["replay_hover"], (785, 637))
            elif 810 / screen_ratio < mouse_x < 1110 / screen_ratio:
                if 732 / screen_ratio < mouse_y < 792 / screen_ratio:
                    display_image(images["exit_hover"], (810, 732))


# In Game Display
def in_game_display(active_match):
    # Display in game content
    display_castles(active_match)
    display_fences(active_match)
    display_players_data(active_match)
    display_cards(active_match)
    display_exit_settings(active_match)


# In Game Events
def in_game_events(active_game, active_match):
    mouse_x, mouse_y = pygame.mouse.get_pos()
    # If user presses escape, match left
    if event.type == KEYDOWN:
        if event.key == K_ESCAPE:
            active_game.set_step(0)  # Set step to Menu
            active_match = Match()  # Reset match

    if event.type == MOUSEBUTTONDOWN and event.button == 1:
        if 0 / screen_ratio < mouse_x < 225 / screen_ratio:
            if 945 / screen_ratio < mouse_y < 1005 / screen_ratio:
                active_game.set_step(0)  # Set step to Menu
                active_match = Match()  # Reset match

    # Set active player
    player = active_match.blue_player if active_match.player_turn == "blue" else active_match.green_player
    opponent = active_match.green_player if active_match.player_turn == "blue" else active_match.blue_player

    # Card On-click
    if isinstance(player, Ia):
        player.chose_card()
        pygame.mouse.set_pos(mouse_x, mouse_y + 1)
        if player.castle == 100 or opponent.castle == 0:
            active_match.winner = active_match.player_turn
            active_match.status = 0
        elif opponent.castle == 100 or player.castle == 0:
            active_match.winner = "green" if active_match.player_turn == "blue" else "blue"
            active_match.status = 0
        else:
            active_match.player_turn = "green" if active_match.player_turn == "blue" else "blue"
            opponent.gain_per_turn()
    else:
        for a_card in range(8):
            # When click on a card
            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                if player.hand[a_card] != '':
                    if 980 / screen_ratio < mouse_y < (980 + 35) / screen_ratio:
                        if (288 + 180 * a_card) / screen_ratio < mouse_x < (313 + 180 * a_card) / screen_ratio:
                            player.discard_card(a_card)
                            if player.castle == 100 or opponent.castle == 0:
                                active_match.status = 0
                            else:
                                active_match.player_turn = "green" if active_match.player_turn == "blue" else "blue"
                                opponent.gain_per_turn()
                        elif (348 + 180 * a_card) / screen_ratio < mouse_x < (373 + 180 * a_card) / screen_ratio:
                            # Check if player has enough resources to play
                            if active_match.match_type == 2:
                                if getattr(player, player.hand[a_card].resource) >= player.hand[a_card].cost \
                                        and player.gold >= player.hand[a_card].gold_price:
                                    # Check if card is Reserve (Switch Fence for Castle), need more than 4 Fence
                                    if (player.hand[a_card].name == "Reserve" and getattr(player, "fence") >= 4) \
                                            or (
                                            player.hand[a_card].name == "Sell lands" and getattr(player, "bricks") >= 5
                                            and getattr(player, "weapons") >= 5 and getattr(player, "crystals") >= 5) \
                                            or (player.hand[a_card].name != "Reserve"
                                                and player.hand[a_card].name != "Sell lands"):
                                        player.play_card(a_card)
                                        # Check the win condition
                                        if player.castle == 100 or opponent.castle == 0:
                                            active_match.winner = active_match.player_turn
                                            active_match.status = 0
                                        elif opponent.castle == 100 or player.castle == 0:
                                            active_match.winner = "green" if active_match.player_turn == "blue" \
                                                else "blue"
                                            active_match.status = 0
                                        else:
                                            active_match.player_turn = "green" if active_match.player_turn == "blue" \
                                                else "blue"
                                            opponent.gain_per_turn()
                            else:
                                if getattr(player, player.hand[a_card].resource) >= player.hand[a_card].cost:
                                    # Check if card is Reserve (Switch Fence for Castle), need more than 4 Fence
                                    if (player.hand[a_card].name == "Reserve" and getattr(player, "fence") >= 4) \
                                            or player.hand[a_card].name != "Reserve":
                                        player.play_card(a_card)
                                        # Check the win condition
                                        if player.castle == 100 or opponent.castle == 0:
                                            active_match.winner = active_match.player_turn
                                            active_match.status = 0
                                        elif opponent.castle == 100 or player.castle == 0:
                                            active_match.winner = "green" if active_match.player_turn == "blue" \
                                                else "blue"
                                            active_match.status = 0
                                        else:
                                            active_match.player_turn = "green" if active_match.player_turn == "blue" \
                                                else "blue"
                                            opponent.gain_per_turn()

    return active_game, active_match


# Show Game Result
def show_game_result(active_game, active_match):
    # Show game result
    display_image(images["victory"], (0, 0))
    winner_color = BLUE if active_match.winner == "blue" else GREEN
    winner_pos = (846, 500) if active_match.winner == "blue" else (830, 500)
    write(active_match.winner.capitalize() + " Player's", 35, winner_color, winner_pos)
    write("Victory", 35, WHITE, (892, 550))

    # If user presses escape, match left
    if event.type == KEYDOWN:
        if event.key == K_ESCAPE:
            active_game.set_step(0)  # Set step to Menu
            active_match = Match()  # Reset match

    mouse_x, mouse_y = pygame.mouse.get_pos()
    if event.type == MOUSEBUTTONDOWN and event.button == 1:
        if 785 / screen_ratio < mouse_x < 1135 / screen_ratio:
            # Replay Button
            if 637 / screen_ratio < mouse_y < 697 / screen_ratio:
                match_type = active_match.match_type
                active_match = Match(match_type)  # Reset match

            # Exit Button
            elif 810 / screen_ratio < mouse_x < 1110 / screen_ratio:
                if 732 / screen_ratio < mouse_y < 792 / screen_ratio:
                    active_game.set_step(0)  # Set step to Menu
                    active_match = Match()  # Reset match

    return active_game, active_match


# Main
while castlewars.get_in_progress():
    # Every events are happening here
    for event in pygame.event.get():
        # Handle In Game
        if castlewars.get_step() == 1:
            in_game_display(match)
            if match.status:
                castlewars, match = in_game_events(castlewars, match)
            else:
                castlewars, match = show_game_result(castlewars, match)
        # Handle Menu
        elif castlewars.get_step() == 0:
            castlewars = menu_handler(castlewars)

        # Allow to Pass Credits
        elif castlewars.get_step() == -1:
            castlewars.set_frame(handle_credits(castlewars.get_frame()))

    # Game's start with credits
    if castlewars.get_step() == -1:
        castlewars.set_step(starting_credits(castlewars.get_frame()))

    # Increment Frame count
    castlewars.set_frame(castlewars.get_frame() + 1)

    # Handle background Music
    active_music = handle_background_music(active_music)

    # Update display
    pygame.display.update()
    fpsClock.tick(FPS)
pygame.quit()
