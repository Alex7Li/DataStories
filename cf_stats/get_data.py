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
logging.basicConfig(filename='logfile.log', filemode='w', level=logging.INFO)

data_folder = Path('cf_stats/data')

skip_503 = False

# https://codeforces.com/apiHelp says:
# API may be requested at most 1 time per two seconds.
CF_WAIT_TIME_SECONDS = 2
SECONDS_PER_USER = CF_WAIT_TIME_SECONDS * 2
last_query_time = 0
last_query = ""
def get_cf(method, params):
    global last_query_time, last_query
    time.sleep(max(0.0, last_query_time - time.time() +  CF_WAIT_TIME_SECONDS))
    request_result = requests.get(f'https://codeforces.com/api/{method}', params)
    last_query = f"{method} {params}"
    last_query_time = time.time()

    while request_result.status_code == 503 or request_result.status_code == 403:
        if request_result.status_code == 503:
            if skip_503:
                logging.error(f"503: skipping {method} {params}")
                break
            logging.error('503 error')
            time.sleep(.1) # Just a server not responsive, can wait
        if request_result.status_code == 403:
            # cf is mad at you, too many requests probably. Let's stop for now.
            # Stopped happening after using the cf wait time (:
            sleep_time = 120
            logging.error(f"403 error, waiting for {sleep_time} seconds")
            time.sleep(sleep_time) 
        request_result = requests.get(f'https://codeforces.com/api/{method}', params)
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
            rated_users = get_cf('user.ratedList', {'activeOnly': activeOnly, 'includeRetired': True})
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
    submissions = get_cf('user.status', {'handle': handle, 'count': 10000, 'from': 1})
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
    handle = "WolfBlue" # That's me!
    submission_fname = data_folder / f'submissions_sample.csv'
    rating_fname = data_folder / f'contests_sample.csv'
    gen_user_data_files(handle, submission_fname, rating_fname)


def generate_user_data(handles, subset_size=-1):
    handles = handles[:subset_size]
    handles_to_load = [handle for handle in handles if 
                       not os.path.isfile(data_folder / 'submissions' / f'{handle}.csv') or
                       not os.path.isfile(data_folder / 'contests' / f'{handle}.csv') ]
    handles_to_not_load = set(handles) - set(handles_to_load)
    logging.info(f"N Cached handles: {len(handles_to_not_load)}.")
    logging.info(f"Cached handles: {handles_to_not_load}")
    logging.info(f"Unsaved handles: {set(handles_to_load)}")
    logging.info(f"handles to query: {len(handles_to_load)}.")
    logging.info(f"ETA: {(SECONDS_PER_USER * (len(handles_to_load))) / 3600:.3f} hours.")
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
            rating = problemInfo['rating'] if 'rating' in problemInfo else float('nan')
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
        handle = handles[:-4] # strip .csv
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


def main():
    logging.info(f"Script begins running at {datetime.datetime.now()}")
    os.makedirs(data_folder / 'contests', exist_ok=True)
    os.makedirs(data_folder / 'submissions', exist_ok=True)
    rated_handles = get_rated_handles()

    logging.info(f"There are {len(rated_handles)} different rated users")

    generate_user_data(rated_handles)
    n_contests = len(os.listdir(data_folder / 'contests'))
    n_submissions = len(os.listdir(data_folder / 'submissions'))
    logging.info(f"Script complete at {datetime.datetime.now()}")
    logging.info(f"{n_contests=} {n_submissions=}")
    print(f"{n_contests=} {n_submissions=}")
    dedup_handles(destroy=True)

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
                user_contests.iloc[2]['oldRating'] += 500
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

def postprocess():
    filenames = os.listdir(data_folder / 'contests')
    contests = {}
    submissions = {}
    for handlecsv in tqdm(filenames, "postprocessing data"):
        handle = handlecsv[:-4]
        contests[handle] = pd.read_csv(data_folder / 'contests' / handlecsv, index_col=False)
        submissions[handle] = pd.read_csv(data_folder / 'submissions' / handlecsv, index_col=False)
        contests[handle].rename({"Unnamed: 0":"a"}, axis="columns", inplace=True)
        contests[handle].drop(["a"], axis=1, inplace=True)
        submissions[handle].rename({"Unnamed: 0":"a"}, axis="columns", inplace=True)
        submissions[handle].drop(["a"], axis=1, inplace=True)
        contests[handle].to_csv(data_folder / 'contests' / handlecsv, index=False)
        submissions[handle].to_csv(data_folder / 'submissions' / handlecsv, index=False)

if __name__ == '__main__':
    postprocess()
    generate_sample_user_data()
    # generate_problem_data()
    # main()