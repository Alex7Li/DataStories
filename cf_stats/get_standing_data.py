import os
import json
from pathlib import Path
import logging

from tqdm import tqdm
import pandas as pd

from get_data import get_cf
data_folder = Path('cf_stats/data')
standings_data_folder = Path('cf_stats/standings_data')


def get_contest_standings():
    metadata_path = standings_data_folder / 'standing_metadata.json'
    if os.path.exists(metadata_path):
        with open(metadata_path) as f:
            contest_metadata = json.load(f)
    else:
        contest_metadata = {}
    for contest_id in tqdm(range(1, 1790), "Getting standings from cf"):
        if contest_id in [179, 184, 210, 307, 310, 390, 391, 392, 393, 394, 395, 396, 397, 398, 399,
                          410, 422, 423, 428, 473, 481, 502, 503, 511, 517, 539, 561, 563, 564, 565,
                          589, 619, 654, 692, 693, 694, 726, 728, 783, 824, 826, 829, 836, 857, 874,
                          880, 881, 882, 885, 905, 941, 942, 943, 945, 968, 969, 970, 971, 972, 973, 974,
                          1018, 1021, 1022, 1024, 1026, 1035, 1048, 1049, 1050, 1069, 1094, 1122, 1123,
                          1124, 1125, 1126, 1127, 1128, 1134, 1135, 1222, 1224, 1226, 1232, 1233, 1258,
                          1289, 1306, 1317, 1318, 1390, 1410, 1412, 1414, 1429, 1448, 1449, 1502,
                          1507, 1518, 1564, 1565, 1568, 1577, 1587, 1590, 1595, 1596, 1597, 1636,
                          1640, 1643, 1653, 1655, 1664, 1683, 1727, 1745, 1756, 1757, 1776, 1789]:
            # I imagine they are just contests that never happended
            # except for the 390~399 range, codeforces seems to have lost this data.
            continue
        data_path = standings_data_folder / 'standings' / f'{contest_id}.csv'
        if os.path.exists(data_path):
            continue
        try:
            recent_contest_standings = get_cf(
                'contest.standings', {'contestId': contest_id})
        except:
            logging.error(f"Could not find contest with id {contest_id}")
            continue
        contest_type = recent_contest_standings['contest']['type']

        # Get all problems from the contest
        problem_inds = []
        problem_points = []
        for problem in recent_contest_standings['problems']:
            problem_inds.append(problem['index'])
            if 'points' not in problem:
                problem_points.append(1)
            else:
                problem_points.append(problem['points'])
        try:
            recent_contest_ratingChanges = get_cf(
                'contest.ratingChanges', {'contestId': contest_id})
        except ConnectionError as e:
            if str(e) == "400":
                # Some unrated contests dosn't work, like
                # https://codeforces.com/contest/1001/standings
                # Others just return empty lists.
                recent_contest_ratingChanges = []
            else:
                raise e
        standing_data = []
        is_rated = len(recent_contest_ratingChanges) > 0
        is_team = False
        # Create standings dataframe
        for standings in recent_contest_standings['rows']:
            if len(standings['party']['members']) > 1:
                is_team = True

        def iterate_over_contestants():
            def compute_handle_standing_map():
                handle_standing_map = {}
                for standings in recent_contest_standings['rows']:
                    for i in range(len(standings['party']['members'])):
                        # The first rated team contest is https://codeforces.com/contest/524
                        handle = standings['party']['members'][i]['handle']
                        handle_standing_map[handle] = standings
                return handle_standing_map
            if is_rated:
                handle_standing_map = compute_handle_standing_map()
                for rating_change in recent_contest_ratingChanges:
                    handle = rating_change['handle']
                    try:
                        standings = handle_standing_map[handle]
                    except KeyError:
                        # Some contests use a merged result table, people will have rating
                        # changes despite not being in the competition according to the API.
                        nonlocal recent_contest_standings
                        # there are quite a few merged table contest ids early on, the first are
                        # 38, 46, 48, 67, 82, 85, 86, 97, ...
                        # also some later on like 1641, 1644, 1679, 1692, 1702, and 1774
                        logging.info(
                            f"{contest_id} uses a merged result table")
                        recent_contest_standings = get_cf(
                            'contest.standings', {'contestId': contest_id, 'showUnofficial': True})
                        handle_standing_map = compute_handle_standing_map()
                        standings = handle_standing_map[handle]
                    assert standings['party']['ghost'] == False
                    # Fix rank=0 in the merged result table competitions
                    standings['rank'] = rating_change['rank']
                    yield standings, rating_change, handle, standings['party']['teamId'] if 'teamId' in standings['party'] else None
            else:
                for standings in recent_contest_standings['rows']:
                    if len(standings['party']['members']) > 1:
                        teamId = standings['party']['teamId']
                    else:
                        teamId = None
                    for member_ind in range(len(standings['party']['members'])):
                        yield standings, None, standings['party']['members'][member_ind]['handle'], teamId
        for standings, rating_change, handle, teamId in iterate_over_contestants():
            party_data = {
                'handle': handle,
                'rank': standings['rank'],
                'points': standings['points'],
                'penalty': standings['penalty'],
                'successfulHackCount': standings['successfulHackCount'],
                'unsuccessfulHackCount': standings['unsuccessfulHackCount'],
            }
            if is_team:
                party_data['teamID'] = teamId
            if rating_change is not None:
                party_data['oldDisplayRating'] = rating_change['oldRating']
                party_data['newDisplayRating'] = rating_change['newRating']
            for i in range(len(standings['problemResults'])):
                results = standings['problemResults'][i]
                party_data[f"points_{problem_inds[i]}"] = results['points']
                party_data[f"rejectedAttemptCount_{problem_inds[i]}"] = results['rejectedAttemptCount']
                if 'bestSubmissionTimeSeconds' in results:
                    party_data[f"time_{problem_inds[i]}"] = results['bestSubmissionTimeSeconds']
                else:
                    party_data[f"time_{problem_inds[i]}"] = pd.NA
            standing_data.append(party_data)

        end_time = recent_contest_standings['contest']['startTimeSeconds'] + \
            recent_contest_standings['contest']['durationSeconds']
        if is_rated:
            assert len(standing_data) == len(recent_contest_ratingChanges)
            # So that we can sort by the rating update time, this is the value we really care about
            end_time = recent_contest_ratingChanges[0]['ratingUpdateTimeSeconds']
        contest_metadata[contest_id] = {
            "problem_inds": ';'.join(problem_inds),
            "problem_points": ';'.join(map(str, problem_points)),
            "rated": is_rated,
            "team": is_team,
            "name": recent_contest_standings['contest']['name'],
            "type": contest_type,
            "end_time": end_time,
        }
        with open(metadata_path, 'w') as f:
            json.dump(contest_metadata, f)
        df = pd.DataFrame.from_records(standing_data, index='rank')
        df = df.to_csv(data_path)


def get_true_ratings():
    metadata_path = standings_data_folder / 'standing_metadata.json'
    with open(metadata_path) as f:
        contest_metadata = json.load(f)
    offsets = [0, 0, 50, 150, 300, 550, 900, 1400]
    user_rating_offset_contests = {}
    inds = sorted(contest_metadata.keys(),
                  key=lambda x: contest_metadata[x]['end_time'])
    for contest_ind in tqdm(inds, "Adding rank information"):
        metadata = contest_metadata[contest_ind]
        if metadata['rated']:
            file_path = standings_data_folder / \
                'standings' / f"{contest_ind}.csv"
            standings = pd.read_csv(file_path)

            def update_true_ratings(entry):
                if entry.handle not in user_rating_offset_contests:
                    if entry.oldDisplayRating == 1500:
                        user_rating_offset_contests[entry.handle] = -1
                    else:
                        assert entry.oldDisplayRating == 0
                        if entry.newDisplayRating >= 1000:
                            pass
                        user_rating_offset_contests[entry.handle] = 7
                offset_ind = user_rating_offset_contests[entry.handle]
                if offset_ind >= 1:
                    entry['OldTrueRating'] = entry.oldDisplayRating + \
                        offsets[offset_ind]
                    entry['NewTrueRating'] = entry.newDisplayRating + \
                        offsets[offset_ind - 1]
                else:
                    entry['OldTrueRating'] = entry.oldDisplayRating
                    entry['NewTrueRating'] = entry.newDisplayRating
                user_rating_offset_contests[entry.handle] -= 1
                return entry
            
            standings = standings.apply(update_true_ratings, axis=1)

            standings.to_csv(file_path, index=False)


def main():
    os.makedirs(standings_data_folder / 'standings', exist_ok=True)
    # get_contest_standings()
    # get_true_ratings()
    with open(standings_data_folder / 'standings' / "471.csv", 'r') as fr:
        with open(standings_data_folder / "standings_sample.csv", 'w+') as fw:
            fw.writelines(fr.readlines())


if __name__ == '__main__':
    main()
