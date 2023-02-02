import os
import pandas as pd
from pathlib import Path
from collections import defaultdict
import tqdm
import math
import heapq
import logging

data_folder = Path('cf_stats/data')

def getTrueRatings(user_contests):
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
        # Almost surely using the old system.
        user_contests.iloc[0]['newRating'] += 1500
    return user_contests

def getPerf(user_contests):
    # sharpen the first few ratings with the performance rating formula
    perf_col = []
    ma_perf_col = []
    gamma = .25
    for i in range(len(user_contests)):
        # estimate the performance ratings, this isn't exactly cf's formula cause I don't know it.
        performance_rating = 4 * (user_contests.iloc[i]['newRating'] - user_contests.iloc[i]['oldRating']) + user_contests.iloc[i]['oldRating']
        perf_col.append(performance_rating)
        if i > 1:
            ma_perf_col.append((performance_rating * gamma +  ma_perf_col[-1] * (1 - gamma)))
        else:
            ma_perf_col.append(performance_rating * gamma) # moving average
    denom = 0
    for i in range(len(user_contests)):
        denom = gamma + denom * (1 - gamma)
        ma_perf_col[i] = ma_perf_col[i] / denom
    user_contests['perf'] = perf_col
    user_contests['maPerf'] = ma_perf_col
    return user_contests
    
def get_data(subset_size=0):
    filenames = os.listdir(data_folder / 'ratings')
    if subset_size != 0:
        filenames = filenames[:subset_size]
    ratings = {}
    submissions = {}
    for handlecsv in tqdm.tqdm(filenames, "reading data"):
        handle = handlecsv[:-4]
        ratings[handle] = getPerf(getTrueRatings(pd.read_csv(data_folder / 'ratings' / handlecsv)))
        submissions[handle] = pd.read_csv(data_folder / 'submissions' / handlecsv)
    return ratings, submissions


def rating_at_time(user_contests, time):
    # Returns (most recent rating, n contests completed to get that rating)
    past_rating_changes = user_contests[user_contests['updateTime'] < time]
    if len(past_rating_changes) == 0:
        return user_contests.iloc[0]['oldRating'], 0 # No contests at the time
    last_contest = past_rating_changes.iloc[len(past_rating_changes) - 1]
    current_rating = last_contest['maPerf']
    return current_rating, last_contest[0]
    

def shortTermImprovement(user_contests, time):
    req_contests = 2
    oldRating, oldCount = rating_at_time(user_contests, time)
    quarter_year_later = time + 60 * 60 * 24 * 30 * 3
    newRating, newCount = rating_at_time(user_contests, quarter_year_later)
    if oldCount < req_contests or newCount - oldCount < req_contests:
        return None, None # not enough data
    return newRating - oldRating, oldRating

n_buckets = 5
def rating_to_bucket(rating):
    if rating < 1000:
        return 0
    if rating < 1400:
        return 1
    if rating < 1800:
        return 2
    if rating < 2200:
        return 3
    else:
        assert rating >= 2200
        # assert 4 == n_buckets - 1
        return 4

def problemLearnings(contests, submissions):
    problemIncreases = [defaultdict(lambda: 0) for _ in range(n_buckets)]
    problemCounts = [defaultdict(lambda: 0) for _ in range(n_buckets)]
    for user, submissionList in tqdm.tqdm(submissions.items(), "Calculating problem learnings"):
        user_ratings = contests[user]
        if len(user_ratings) < 5:
            continue # data is not that useful
        seen_problems = set({})
        for i in range(len(submissionList)):
            submission = submissionList.iloc[i]
            # Don't count contest submissions since they affect ratings directly.
            # Don't count failing submissions.
            if submission['participantType'] == 'CONTESTANT' or submission['verdict'] != 'OK':
                pass
            # Don't count repeat problems
            pId = submission['problemId']
            if pId not in seen_problems:
                seen_problems.add(pId)
                improvement, oldRating = shortTermImprovement(user_ratings, submission['creationTime'])
                if improvement is not None:
                    bucket = rating_to_bucket(oldRating)
                    problemIncreases[bucket][pId] += improvement
                    problemCounts[bucket][pId] += 1
    bucketsUsefulness = []
    for i in range(n_buckets):
        problemUsefulness = []
        logging.info(f"Bucket {i}")
        for pId, count in problemCounts[i].items():
            if count < 30:
                continue
            mean = problemIncreases[i][pId] / count
            problemUsefulness.append((mean, count, pId));
        logging.info(f"Problems with enough data: {len(problemUsefulness)}")
        # most useful
        problemUsefulness = sorted(problemUsefulness, key=lambda x: x[0])
        logging.info(f"Most useful:  {list(reversed(problemUsefulness[-50:]))}")
        logging.info("ALL:")
        logging.info(problemUsefulness)
        bucketsUsefulness.append(problemUsefulness)
    return bucketsUsefulness

def event_order(contests, submissions, username):
    contest_ind = 0
    submission_ind = 0
    user_contests = contests[username]
    user_submissions = submissions[username]
    for submission_ind in range(len(user_submissions)):
        while(contest_ind < len(contests)): # and contest date is after submission date
            pass

def main():
    subset_size = 1000
    contests, submissions = get_data(subset_size)
    logging.basicConfig(filename=f'best_problems_{subset_size}.log', filemode='w', level=logging.INFO)
    problemLearnings(contests, submissions)
    print("Done, check log file")

if __name__ == "__main__":
    main()
