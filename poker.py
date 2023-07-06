#!/usr/bin/env python
# -*- coding: utf-8 -*-

# -----------------
# Реализуйте функцию best_hand, которая принимает на вход
# покерную "руку" (hand) из 7ми карт и возвращает лучшую
# (относительно значения, возвращаемого hand_rank)
# "руку" из 5ти карт. У каждой карты есть масть(suit) и
# ранг(rank)
# Масти: трефы(clubs, C), пики(spades, S), червы(hearts, H), бубны(diamonds, D)
# Ранги: 2, 3, 4, 5, 6, 7, 8, 9, 10 (ten, T), валет (jack, J), дама (queen, Q), король (king, K), туз (ace, A)
# Например: AS - туз пик (ace of spades), TH - дестяка черв (ten of hearts), 3C - тройка треф (three of clubs)

# Задание со *
# Реализуйте функцию best_wild_hand, которая принимает на вход
# покерную "руку" (hand) из 7ми карт и возвращает лучшую
# (относительно значения, возвращаемого hand_rank)
# "руку" из 5ти карт. Кроме прочего в данном варианте "рука"
# может включать джокера. Джокеры могут заменить карту любой
# масти и ранга того же цвета, в колоде два джокерва.
# Черный джокер '?B' может быть использован в качестве треф
# или пик любого ранга, красный джокер '?R' - в качестве черв и бубен
# любого ранга.

# Одна функция уже реализована, сигнатуры и описания других даны.
# Вам наверняка пригодится itertools.
# Можно свободно определять свои функции и т.п.
# -----------------

import itertools
import typing as tp
from typing import Union, Optional


def card_rank(card: str) -> int:
    if card[0] == "J":
        return 11
    elif card[0] == "Q":
        return 12
    elif card[0] == "K":
        return 13
    elif card[0] == "A":
        return 14
    elif card[0] == "T":
        return 10
    else:
        return int(card[0])


def remove_sublist_from_list(source: tp.List[int], what_remove: tp.List[int]) -> tp.List[int]:
    return list(filter(lambda x: x not in what_remove, source))


def hand_rank(hand: tp.List[str]) -> Union[
    tuple[int, int], tuple[int, Optional[int], Optional[int]], tuple[int, int, list[int]], tuple[
        int, Optional[int], list[int]], tuple[int, Optional[list[int]], int], tuple[int, list[int]]]:
    """Возвращает значение определяющее ранг 'руки'"""
    ranks = card_ranks(hand)
    if straight(ranks) and flush(hand):  # стритфлеш
        return 8, max(ranks)  # пока двоякая форма туза (как туз и как единичка) не реализована
    elif kind(4, ranks):  # каре
        return 7, kind(4, ranks), kind(1, ranks)
    elif kind(3, ranks) and kind(2, ranks):  # фуллхаус
        return 6, kind(3, ranks), kind(2, ranks)
    elif flush(hand):  # флеш
        return 5, max(ranks), ranks
    elif straight(ranks):  # стрит
        return 4, max(ranks)
    elif kind(3, ranks):  # сет (3 одинаковых)
        return 3, kind(3, ranks), remove_sublist_from_list(ranks, [kind(3, ranks)])
    elif two_pair(ranks):  # две пары
        return 2, two_pair(ranks), remove_sublist_from_list(ranks, two_pair(ranks))[0]
    elif kind(2, ranks):  # одна пара
        return 1, kind(2, ranks), remove_sublist_from_list(ranks, [kind(2, ranks)])
    else:  # набор карт
        return 0, ranks


def card_ranks(hand: tp.List[str]) -> tp.List[int]:
    """Возвращает список рангов (его числовой эквивалент),
    отсортированный от большего к меньшему"""
    ranks = []
    for card in hand:
        ranks.append(card_rank(card))
    return sorted(ranks, reverse=True)


def flush(hand: tp.List[str]) -> bool:
    """Возвращает True, если все карты одной масти"""
    exist_suit = None
    for card in hand:
        if exist_suit is None:
            exist_suit = card[1]
        elif exist_suit != card[1]:
            return False
    return True


def straight(ranks: tp.List[int]) -> bool:
    """Возвращает True, если отсортированные ранги формируют последовательность 5ти,
    где у 5ти карт ранги идут по порядку (стрит)"""
    five = 1
    for idx, rank in enumerate(ranks):
        if idx == 0:
            continue
        else:
            if ranks[idx - 1] - rank == 1:
                five += 1
                if five == 5:
                    return True
            else:
                return False
    return False


def kind(n: int, ranks: tp.List[int]) -> tp.Optional[int]:
    """Возвращает первый ранг, который n раз встречается в данной руке.
    Возвращает None, если ничего не найдено"""
    ranks_count = {}
    for rank in ranks:
        if rank in ranks_count.keys():
            ranks_count[rank] += 1
        else:
            ranks_count[rank] = 1
    for rank in sorted(ranks_count.keys(), reverse=True):
        if ranks_count[rank] == n:
            return rank
    return None


def two_pair(ranks: tp.List[int]) -> tp.Optional[tp.List[int]]:
    """Если есть две пары, то возврщает два соответствующих ранга,
    иначе возвращает None"""
    ranks_count = {}
    for rank in ranks:
        if rank in ranks_count.keys():
            ranks_count[rank] += 1
        else:
            ranks_count[rank] = 1
    result = []
    for rank in sorted(ranks_count.keys(), reverse=True):
        if ranks_count[rank] == 2:
            result.append(rank)
            if len(result) == 2:
                return result
    return None


def sub_rank_power(sub_rank: tp.Any) -> float:
    if sub_rank is None:
        return 0.0
    if type(sub_rank) is int:
        return sub_rank
    elif type(sub_rank) is str:
        return card_rank(sub_rank)
    elif type(sub_rank) is list:
        sub_power = 0
        for idx, val in enumerate(sub_rank):
            sub_power += val * 0.01 ** idx
        return sub_power
    else:
        raise RuntimeError(f"Неизвестный тип для сравнения {type(sub_rank)}")


def hand_power(rank: tp.Tuple[tp.Any, tp.Any, tp.Any]) -> float:
    result = rank[0] if type(rank[0]) is int else card_rank(rank[0])
    if len(rank) > 1 and rank[1] is not None:
        result += 0.01 * sub_rank_power(rank[1])
    if len(rank) > 2 and rank[2] is not None:
        result += 0.000001 * sub_rank_power(rank[2])
    return result


def best_hand(hand: tp.List[str]) -> tp.List[str]:
    """Из "руки" в 7 карт возвращает лучшую "руку" в 5 карт """
    best = None
    power = 0
    for test_hand in itertools.combinations(hand, 5):
        rank = hand_rank(test_hand)
        test_power = hand_power(rank)
        if test_power > power:
            best = test_hand
            power = test_power
    return sorted(best)


def generate_all_card_suite(suite: str) -> tp.List[str]:
    cards = "T J Q K A".split() + [str(x) for x in range(2, 10)]
    return [f"{x}{suite}" for x in cards]


def joker_replacement_generator(is_black: bool) -> tp.List[str]:
    if is_black:
        cards = generate_all_card_suite("C")
        cards += generate_all_card_suite("S")
    else:
        cards = generate_all_card_suite("H")
        cards += generate_all_card_suite("D")
    return cards


def prepare_hand_iterator(hand: tp.List[str]) -> tp.Generator[
    tp.List[str], None, None]:
    clear_cards = []
    joker_iterators = None
    for card in hand:
        if card == "?B":
            joker_iterators = itertools.product(joker_iterators, joker_replacement_generator(
                True)) if joker_iterators else joker_replacement_generator(True)
        elif card == "?R":
            joker_iterators = itertools.product(joker_iterators, joker_replacement_generator(
                False)) if joker_iterators else joker_replacement_generator(False)
        else:
            clear_cards.append(card)
    if joker_iterators:
        for joker_cards in joker_iterators:
            result_card = clear_cards.copy()
            if type(joker_cards) == str:
                result_card.append(joker_cards)
            else:
                result_card += [card for card in joker_cards if card not in result_card]
            if len(result_card) < 7:
                continue
            yield result_card
    else:
        yield hand


def best_wild_hand(hand: tp.List[str]):
    """best_hand но с джокерами"""
    best = None
    power = 0
    for wild_hand in prepare_hand_iterator(hand):
        rank = best_hand(wild_hand)
        test_power = hand_power(hand_rank(rank))
        if test_power > power:
            best = rank
            power = test_power
    print(f"result wild hand = {sorted(best)}")
    return sorted(best)


def test_best_hand():
    print("test_best_hand...")
    assert (sorted(best_hand("6C 7C 8C 9C TC 5C JS".split()))
            == ['6C', '7C', '8C', '9C', 'TC'])
    assert (sorted(best_hand("6C 7C 8C 9C TC 5C JC".split()))
            == ['7C', '8C', '9C', 'JC', 'TC'])
    assert (sorted(best_hand("TD TC TH 7C 7D 8C 8S".split()))
            == ['8C', '8S', 'TC', 'TD', 'TH'])
    assert (sorted(best_hand("JD TC TH 7C 7D 7S 7H".split()))
            == ['7C', '7D', '7H', '7S', 'JD'])
    print('OK')


def test_best_wild_hand():
    print("test_best_wild_hand...")
    assert (sorted(best_wild_hand("6C 7C 8C 9C TC 5C ?B".split()))
            == ['7C', '8C', '9C', 'JC', 'TC'])
    assert (sorted(best_wild_hand("TD TC 5H 5C 7C ?R ?B".split()))
            == ['7C', 'TC', 'TD', 'TH', 'TS'])
    assert (sorted(best_wild_hand("JD TC TH 7C 7D 7S 7H".split()))
            == ['7C', '7D', '7H', '7S', 'JD'])
    print('OK')


def test_flush():
    print("test_flush function..")
    assert (flush("6C 7C 8C 9C TC 5C".split()))
    assert (not flush("6C 7C 8C 9C TC 5B".split()))
    assert (flush("5B".split()))
    assert (flush("".split()))
    print('OK')


def test_card_ranks():
    print("test_card_ranks function..")
    assert (card_ranks("6C 7C 8C 9C TC 5C".split()) == [10, 9, 8, 7, 6, 5])
    assert (card_ranks("JD TC TH 7C 7D 7S 7H".split()) == [11, 10, 10, 7, 7, 7, 7])
    print('OK')


def test_straight():
    print("test_straight function..")
    assert (straight(card_ranks("6C 7C 8C 9C TC".split())))
    assert (not straight(card_ranks("QC 6C 7C 8C 9C".split())))
    assert (straight(card_ranks("5C 6C 7C 8C 9C".split())))
    assert (not straight(card_ranks("JD TC TH 7C 7D 7S 7H".split())))
    assert (not straight(card_ranks("JD TC TH".split())))
    assert (not straight(card_ranks("".split())))
    print('OK')


def test_kind():
    print("test_kind function..")
    assert (kind(2, card_ranks("6C 7C 8C 9C TC 5C".split())) is None)
    assert (kind(1, card_ranks("6C 7C 8C 9C TC 5C".split())) == 10)
    assert (kind(4, card_ranks("JD TC TH 7C 7D 7S 7H".split())) == 7)
    assert (kind(3, card_ranks("JD TC TH 7C 7D 7S 7H".split())) is None)
    print('OK')


def test_two_pairs():
    print("test_two_pairs function..")
    assert (two_pair(card_ranks("6C 7C 8C 9C TC 5C".split())) is None)
    assert (two_pair(card_ranks("JD TC TH 7C 7D 7S 7H".split())) is None)
    assert (two_pair(card_ranks("JD TC TH 7C 7D 5S 5H".split())) == [10, 7])
    print('OK')


if __name__ == '__main__':
    test_flush()
    test_card_ranks()
    test_straight()
    test_kind()
    test_two_pairs()
    test_best_hand()
    test_best_wild_hand()
