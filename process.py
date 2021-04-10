import pickle
import gzip

def test():
    [person_to_id,
     person_to_games,
     games] = pickle.load(gzip.open("generals_data.p.gz","rb"))

    # person_to_id is a dict of username -> internal ID
    # person_to_id is a list of internal ID -> [game index, ...]
    # games is a list of index -> [[server_uid, timestamp, turns, userID1, stars, userID2, stars], ...]

    print(len(games))
    person = person_to_id['MeltedToast']
    person_games = person_to_games[person]
    print("MeltedToast has played", len(person_games))
        
    won_games = sum([games[game][3] == person for game in person_games])
    print("With a win rate of", won_games/len(person_games))

test()
