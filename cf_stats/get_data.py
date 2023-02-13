import os
import json
import logging
import requests
import time
import datetime
import itertools
from pathlib import Path
import pandas as pd
from tqdm import tqdm
import fix_standings
logging.basicConfig(filename='logfile.log', filemode='w', level=logging.INFO)

data_folder = Path('cf_stats/data')
standings_data_folder = Path('cf_stats/standings_data')

skip_503 = False

# https://codeforces.com/apiHelp says:
# API may be requested at most 1 time per two seconds.
CF_WAIT_TIME_SECONDS = 2
SECONDS_PER_USER = CF_WAIT_TIME_SECONDS * 2
last_query_time = 0
last_query = ""


def get_cf(method, params):
    global last_query_time, last_query
    time.sleep(max(0.0, last_query_time - time.time() + CF_WAIT_TIME_SECONDS))
    request_result = requests.get(
        f'https://codeforces.com/api/{method}', params)
    last_query = f"{method} {params}"
    last_query_time = time.time()

    while request_result.status_code == 503 or request_result.status_code == 403:
        if request_result.status_code == 503:
            if skip_503:
                logging.error(f"503: skipping {method} {params}")
                break
            logging.error('503 error')
            time.sleep(.1)  # Just a server not responsive, can wait
        if request_result.status_code == 403:
            # cf is mad at you, too many requests probably. Let's stop for now.
            # Stopped happening after using the cf wait time (:
            sleep_time = 120
            logging.error(f"403 error, waiting for {sleep_time} seconds")
            time.sleep(sleep_time)
        request_result = requests.get(
            f'https://codeforces.com/api/{method}', params)
    if request_result.status_code != 200:
        raise ConnectionError(request_result.status_code)
    text = json.loads(request_result.text)
    if text['status'] != 'OK':
        logging.error(f"Status not OK {text['status']}")
        raise ConnectionError()
    return text['result']


def get_rated_handles(activeOnly=True):
    rated_users = None
    while rated_users == None:
        try:
            rated_users = get_cf('user.ratedList', {
                                 'activeOnly': activeOnly, 'includeRetired': True})
        except ConnectionError as e:
            logging.info(f'Rated handles error {e}')
    return [user['handle'] for user in rated_users]


def get_problem_id(problem):
    if 'problemsetName' in problem:
        problem_id = f"{problem['problemsetName']}:{problem['index']}"
        if problem['problemsetName'] != 'acmsguru':
            print(f'problemset: {problem["problemsetName"]}')
    else:
        problem_id = f"{problem['contestId']}:{problem['index']}"
    return problem_id


def format_submission(submission):
    if submission['problem']['type'] != 'PROGRAMMING':
        # There are some strange problems where you don't submit code.
        # Basically just 2 contests:
        # https://codeforces.com/contest/1164/problem/A
        # https://codeforces.com/contest/1273/problem/A
        return None
    if submission['author']['ghost']:
        # Should never happen since we are only scraping data from real users
        print(f"Ghost author: {submission['author']}")
        return None
    return {
        'submissionId': submission['id'],
        'problemName': submission['problem']['name'],
        'problemId': get_problem_id(submission['problem']),
        # Time submission was created (unix seconds)
        'creationTime': submission['creationTimeSeconds'],
        # Time since contest started for the submission, (1 << 30) -1
        # for practice.
        'relativeTimeSeconds': submission['relativeTimeSeconds'],
        'participantType': submission['author']['participantType'],
        'verdict': submission['verdict'],
        'testset': submission['testset'],
        'programmingLanguage': submission['programmingLanguage'],
        'passedTestCount': submission['passedTestCount'],
        # points scored, for IOI style contests
        'points': submission['points'] if 'points' in submission else float('nan'),
    }


def generate_user_submissions(handle):
    submissions = get_cf(
        'user.status', {'handle': handle, 'count': 10000, 'from': 1})
    submission_data = []
    for submission in submissions:
        formatted = format_submission(submission)
        if formatted is not None:
            submission_data.append(formatted)
    df = pd.DataFrame.from_records(submission_data, index='submissionId')
    return df


def generate_user_rating_history(handle):
    rating_changes = get_cf('user.rating', {'handle': handle})
    rating_change_list = []
    for rating_change in rating_changes:
        formatted = {
            # Time that rating was updated (unix seconds)
            'updateTime': rating_change['ratingUpdateTimeSeconds'],
            'oldRating': rating_change['oldRating'],
            'newRating': rating_change['newRating'],
            'rank': rating_change['rank'],
        }
        rating_change_list.append(formatted)
    df = pd.DataFrame.from_records(rating_change_list)
    return df


def gen_user_data_files(handle, submission_fname, rating_fname):
    try:
        if not os.path.isfile(submission_fname):
            submissions = generate_user_submissions(handle)
            submissions = postprocess_submissions(submissions)
            submissions.to_csv(submission_fname, index=False)
            contests = generate_user_rating_history(handle)
            contests = postprocess_contests(contests)
            contests.to_csv(rating_fname, index=False)
    except ConnectionError as e:
        # Log error and just keep going we don't want the script to get stuck
        # because someone changed their username or something.
        logging.warning(f"Got error {e} on request {last_query}")


def generate_sample_user_data():
    # make one sample so I can annotate it on kaggle.
    handle = "WolfBlue"  # That's me!
    submission_fname = data_folder / f'submissions_sample.csv'
    rating_fname = data_folder / f'contests_sample.csv'
    gen_user_data_files(handle, submission_fname, rating_fname)


def generate_user_data(handles, subset_size=-1):
    handles = handles[:subset_size]
    handles_to_load = [handle for handle in handles if
                       not os.path.isfile(data_folder / 'submissions' / f'{handle}.csv') or
                       not os.path.isfile(data_folder / 'contests' / f'{handle}.csv')]
    handles_to_not_load = set(handles) - set(handles_to_load)
    logging.info(f"N Cached handles: {len(handles_to_not_load)}.")
    logging.info(f"Cached handles: {handles_to_not_load}")
    logging.info(f"Unsaved handles: {set(handles_to_load)}")
    logging.info(f"handles to query: {len(handles_to_load)}.")
    logging.info(
        f"ETA: {(SECONDS_PER_USER * (len(handles_to_load))) / 3600:.3f} hours.")
    pbar = tqdm(handles_to_load)
    for handle in pbar:
        submission_fname = data_folder / 'submissions' / f'{handle}.csv'
        rating_fname = data_folder / 'contests' / f'{handle}.csv'
        gen_user_data_files(handle, submission_fname, rating_fname)


def generate_problem_data():
    formated = []
    for problem_data in itertools.chain([get_cf('problemset.problems', {})],
                                        [get_cf('problemset.problems', {'problemsetName': 'acmsguru'})]):
        for problemInfo, statistics in zip(problem_data['problems'], problem_data['problemStatistics']):
            rating = problemInfo['rating'] if 'rating' in problemInfo else float(
                'nan')
            formated.append({
                'problemId': get_problem_id(problemInfo),
                'tags': '+'.join(problemInfo['tags']),
                'rating': rating,
                'name': problemInfo['name'],
                'solved': statistics['solvedCount'],
            })
    df = pd.DataFrame.from_records(formated, index='problemId')
    df = df.to_csv(data_folder / 'problems.csv')


# Cleanup functions
def dedup_handles(destroy=False):
    good_handles = get_rated_handles(activeOnly=False)
    # Ran this during christmas, when people can change their handles :|
    renamed_handles = []
    for handles in os.listdir(data_folder / 'contests'):
        handle = handles[:-4]  # strip .csv
        if handle not in good_handles:
            renamed_handles.append(handle)
    print(f"There are {len(renamed_handles)} invalid handles")
    logging.info(f"Invalid handles {renamed_handles}")
    if destroy:
        # Don't want to lose a bunch of data due to a typo
        assert(len(renamed_handles) < 1000)
        for handle in renamed_handles:
            os.remove(f'data/contests/{handle}.csv')
            os.remove(f'data/submissions/{handle}.csv')


def postprocess_contests(user_contests):
    """Overwrite the oldRating and newRating field with estimated approximate values,
    see https://codeforces.com/blog/entry/77890
    """
    if user_contests.iloc[0]['newRating'] < 1000:
        # Almost surely using the new system.
        user_contests.iloc[0]['oldRating'] += 1400
        user_contests.iloc[0]['newRating'] += 900
        if len(user_contests) > 1:
            user_contests.iloc[1]['oldRating'] += 900
            user_contests.iloc[1]['newRating'] += 550
            if len(user_contests) > 2:
                user_contests.iloc[2]['oldRating'] += 550
                user_contests.iloc[2]['newRating'] += 300
                if len(user_contests) > 3:
                    user_contests.iloc[3]['oldRating'] += 300
                    user_contests.iloc[3]['newRating'] += 150
                    if len(user_contests) > 4:
                        user_contests.iloc[4]['oldRating'] += 150
                        user_contests.iloc[4]['newRating'] += 50
                        if len(user_contests) > 5:
                            user_contests.iloc[5]['oldRating'] += 50
    else:
        # Almost surely using the old system. oldRating is still 0 in the raw data.
        user_contests.iloc[0]['oldRating'] += 1500
    return user_contests


def postprocess_submissions(user_submissions):
    user_submissions = user_submissions[::-1]
    return user_submissions


def get_contest_standings():
    metadata_path = standings_data_folder / 'standing_metadata.json'
    if os.path.exists(metadata_path):
        with open(metadata_path) as f:
            contest_metadata = json.load(f)
    else:
        contest_metadata = {}
    for contest_id in tqdm(range(1, 1791)):
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
                        # The first rated team contest is https://codeforces.com/contest/534
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


def main():
    logging.info(f"Script begins running at {datetime.datetime.now()}")
    os.makedirs(standings_data_folder / 'standings', exist_ok=True)
    # generate_problem_data()
    get_contest_standings()
    # fix_standings.main()

    # os.makedirs(data_folder / 'contests', exist_ok=True)
    # os.makedirs(data_folder / 'submissions', exist_ok=True)
    # rated_handles = get_rated_handles()

    # logging.info(f"There are {len(rated_handles)} different rated users")

    # generate_user_data(rated_handles)
    # n_contests = len(os.listdir(data_folder / 'contests'))
    # n_submissions = len(os.listdir(data_folder / 'submissions'))
    # logging.info(f"Script complete at {datetime.datetime.now()}")
    # logging.info(f"{n_contests=} {n_submissions=}")
    # print(f"{n_contests=} {n_submissions=}")
    # dedup_handles(destroy=True)


if __name__ == '__main__':
    main()


# not used functions
def users_from_contest(id):
    recent_contest_standings = get_cf('contest.standings', {'contestId': id})
    rows = recent_contest_standings['rows']
    handles = []
    for row in rows:
        assert len(row['party']['members']) == 1
        for k, v in row['party']['members'][0].items():
            if k == 'handle':
                handles.append(v)
    return handles


def get_active_handles():
    users = set(users_from_contest(1730)).union(set(users_from_contest(1731)))
    return users
