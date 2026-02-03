def classify_scale(players):
    if len(players) <= 2:
        return "DUEL"
    if len(players) <= 4:
        return "SKIRMISH"
    return "TEAMFIGHT"
