import requests
import time
import os
import base64
import heapq
import collections
import json
import pickle
import urllib
import pickle
import multiprocessing as mp
import gzip

def crawl():
    URL = "http://generals.io/api/replaysForUsername?u=%s&offset=%d&count=200"
    
    seen = set(["Anonymous"])
    all_people = collections.defaultdict(int)
    all_people["Spraget"] = 0

    games_found = 0
    ii = 0
    
    while len(all_people):
        stars, who = max((v,k) for k,v in all_people.items())
    
        if who in seen:
            del all_people[who]
            continue
        seen.add(who)
    
        print("Loading games for", who, stars)
        print("Number of people in queue:", len(all_people))
        strname = base64.b64encode(bytes(who, 'utf8')).decode("ascii").replace("/","_")
        print(strname)

        if os.path.exists("games/people/"+strname):
            print("Loading from cache")
            data = json.load(open("games/people/"+strname))
        else:
            data = []
            for offset in range(0,100000,200):
                while True:
                    try:
                        for _ in range(5):
                            r = requests.get(URL%(urllib.parse.quote_plus(who), offset))
                            if r.status_code == 200:
                                break
                            else:
                                print("Weird", r.status_code, r.content)
                                time.sleep(60)
                    except:
                        continue
                    try:
                        r.json()
                    except:
                        print(r)
                        print(r.text)
                        print(r.content)
                        raise
                    if len(r.json()) > 0 and 'error' in r.json():
                        print("Told to wait")
                        time.sleep(60)
                        continue
                    else:
                        break
                j = r.json()
                if len(j) == 0: break
                data.extend(j)
        
            open("games/people/"+strname, "w").write(json.dumps(data))
    
        games_found += len(data)
        print("Found", len(data), "more games for a total of", games_found)
            
        for row in data:
            if row['type'] != '1v1': continue # 0hVTg==
            if (time.time()-int(row['started'])/1000.)/(60*60*24) > 365*2: continue
            for person in row['ranking']:
                if person['name'] not in seen:
                    #heapq.heappush(people, (-person['stars'], person['name']))
                    all_people[person['name']] = max(all_people[person['name']], person['stars'] or 0)
        print("Done walking rankings")

def download():
    people = os.listdir("games/people")
    for i,person in enumerate(people):
        games = json.loads(open("games/people/"+person).read())

        print("%d/%d: %s", i, len(people), base64.b64decode(person))

        print("\tSaving", len(games), 'games')
        for game in games:
            if os.path.exists("games/replays/"+game['id']): continue
            if game['type'] != '1v1': continue
            if (time.time()-int(game['started'])/1000.)/(60*60*24) > 365: continue
            print(game['id'])
            try:
                dat = requests.get("http://generalsio-replays-na.s3.amazonaws.com/%s.gior"%game['id'])
                open("games/replays/"+game['id'], "wb").write(dat.content)
            except Exception as e:
                print(e)
                time.sleep(60)
            time.sleep(3)

def fix(x):
    try:
        return [x['id'], x['started'], x['turns'],
                x['ranking'][0]['name'], x['ranking'][0]['stars'],
                x['ranking'][1]['name'], x['ranking'][1]['stars']]
    except:
        return None

def load(x):
    return {x['id']:fix(x)  for x in json.load(open(x)) if x['type'] == '1v1'}
            
def minify():
    fs = sorted(["games/people/" + f for f in os.listdir("games/people")])
    p = mp.Pool(4)
    games = list(p.map(load,fs))
    print(sum(len(x) for x in games))

    r = {}
    for x in games:
        r.update(x)

    #vs = list(zip(*r.values()))
    pickle.dump(r, open("/tmp/a.p","wb"))
    #print(len(json.dumps(r)))
    

def minify2():
    r = pickle.load(open("/tmp/a.p","rb"))

    person_to_id = {}
    person_to_games = []
    games = []
    r = [x for x in r.values() if x is not None and (time.time()-x[1]/1000.)/(60*60*24) < 365*2]
    for i,x in enumerate(r):
        games.append(x)
        if x[3] not in person_to_id:
            person_to_games.append([])
            person_to_id[x[3]] = len(person_to_id)
        x[3] = person_to_id[x[3]]
        person_to_games[x[3]].append(i)
        if x[5] not in person_to_id:
            person_to_games.append([])
            person_to_id[x[5]] = len(person_to_id)
        x[5] = person_to_id[x[5]]
        person_to_games[x[5]].append(i)
    pickle.dump([person_to_id,
                 person_to_games,
                 games],
                open("generals_data.p","wb"))

def get_70plus():
    [person_to_id,
     person_to_games,
     games] = pickle.load(gzip.open("generals_data.p.gz","rb"))

    id_to_person = {v: k for k,v in person_to_id.items()}
    max_ranking = collections.defaultdict(int)
    for x in games:
        if x[4] is not None:
            max_ranking[x[3]] = max(max_ranking[x[3]], x[4])
        if x[6] is not None:
            max_ranking[x[5]] = max(max_ranking[x[5]], x[6])

    keep = [k for k,v in max_ranking.items() if v >= 70]
    for x in [id_to_person[x] for x in keep]:
        print(x)
    

    
    
    
            
#download()
#crawl()
minify2()
#get_70plus()

