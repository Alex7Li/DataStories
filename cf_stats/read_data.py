import bisect
from collections import defaultdict, Counter
import json
import logging
import os
from pathlib import Path
from typing import List, TypedDict, Optional, Dict

import numpy as np
import pandas as pd
from tqdm import tqdm
tqdm.pandas()

analysis_folder = Path('cf_stats/analysis')
data_folder = Path('cf_stats/data')
standings_folder = Path('cf_stats/standings_data')
problems = pd.read_csv(data_folder / 'problems.csv')
id_to_problem_ind = defaultdict(lambda: None)
for i in range(len(problems)):
    id_to_problem_ind[problems.iloc[i]['problemId']] = i

cache_folder = Path('cf_stats/cache')
with open(cache_folder / "cache.json") as f:
    first_solve_percentile_cache = json.load(f)


def first_solve_percentile(contest_ind, time):
    """First solve percentile in this contest, lower is better.
    """
    if contest_ind not in first_solve_percentile_cache:
        return pd.NA
    insert_ind = bisect.bisect_left(
        first_solve_percentile_cache[contest_ind], time)
    return 100 * float(insert_ind) / len(first_solve_percentile_cache[contest_ind])


def getPerf(user_contests):
    # sharpen the first few ratings with the performance rating formula
    perf_col = []
    ma_perf_col = []
    gamma = .25
    for i in range(len(user_contests)):
        # estimate the performance ratings, this isn't exactly cf's formula cause I don't know it.
        performance_rating = 4 * \
            (user_contests.iloc[i]['newRating'] - user_contests.iloc[i]
             ['oldRating']) + user_contests.iloc[i]['oldRating']
        perf_col.append(performance_rating)
        if i >= 1:
            ma_perf_col.append(
                (performance_rating * gamma + ma_perf_col[-1] * (1 - gamma)))
        else:
            ma_perf_col.append(performance_rating * gamma)  # moving average
    denom = 0
    for i in range(len(user_contests)):
        denom = gamma + denom * (1 - gamma)
        ma_perf_col[i] = ma_perf_col[i] / denom
    user_contests['perf'] = perf_col
    user_contests['maPerf'] = ma_perf_col
    return user_contests


def is_griefing(contest_results):
    # Sometimes people lose a lot on purpose. Or they cheated or are multiple people.
    # Anyways it's very rare for a legit person to lose 800 rating.
    # so let's just ignore these outliers as they are primarily noise.
    # Even if they are real ratings they are people with huge standard deviation
    # like rainboy and it's super hard to get useful data from them.
    max_rating_so_far = 0
    max_diff = 0
    for i in range(6, len(contest_results)):
        max_rating_so_far = max(
            max_rating_so_far, contest_results.iloc[i]['newRating'])
        max_diff = max(max_rating_so_far -
                       contest_results.iloc[i]['newRating'], max_diff)
        if max_diff > 800:
            return True
    return False


def get_data(subset_size=0):
    filenames = os.listdir(data_folder / 'contests')
    if subset_size != 0:
        filenames = filenames[:subset_size]
    ratings = {}
    submissions = {}
    for handlecsv in tqdm(filenames, "reading data"):
        handle = handlecsv[:-4]
        contest_results = getPerf(pd.read_csv(
            data_folder / 'contests' / handlecsv))
        if not is_griefing(contest_results):
            ratings[handle] = contest_results
            submissions[handle] = pd.read_csv(
                data_folder / 'submissions' / handlecsv)
        else:
            logging.info(f"{handle} may be griefing, ignore")
    return ratings, submissions


def rating_at_time(user_contests, time):
    # Returns (most recent rating, n contests completed to get that rating)
    past_rating_changes = user_contests[user_contests['updateTime'] < time]
    if len(past_rating_changes) == 0:
        return user_contests.iloc[0]['oldRating'], 0  # No contests at the time
    last_contest = past_rating_changes.iloc[len(past_rating_changes) - 1]
    current_rating = last_contest['maPerf']
    return current_rating, last_contest[0]


def shortTermImprovement(user_contests, time):
    req_contests = 2
    oldRating, oldCount = rating_at_time(user_contests, time)
    quarter_year_later = time + 60 * 60 * 24 * 30 * 3
    newRating, newCount = rating_at_time(user_contests, quarter_year_later)
    if oldCount < req_contests or newCount - oldCount < req_contests:
        return None, None  # not enough data
    return newRating - oldRating, oldRating




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
        return 4


def rating_to_name(rating):
    if rating == None:
        return 'unknown'
    if rating < 1200:
        return 'newbie'
    if rating < 1400:
        return 'pupil'
    if rating < 1600:
        return 'specialist'
    if rating < 1900:
        return 'expert'
    if rating < 2100:
        return 'candidate master'
    if rating < 2400:
        return 'master'
    else:
        return 'grandmaster'


def event_order(user_contests, user_submissions):
    contests = user_contests.itertuples()
    next_contest = next(contests)
    # Data is in reversed chronological order for submissions.
    submissions = user_submissions.itertuples(index=True)
    for submission in submissions:
        while next_contest.updateTime < submission.creationTime:
            yield next_contest
            next_contest = next(contests)
        yield submission


class PeriodInfo(TypedDict):
    start_rating: int
    end_rating: int
    n_correct: int
    n_hard_correct: int
    n_gm_correct: int
    n_master_correct: int
    n_cm_correct: int
    n_expert_correct: int
    n_specialist_correct: int
    n_pupil_correct: int
    n_newbie_correct: int
    n_contests: int
    n_contest_correct: int
    n_contest_wrong: int
    n_wrong: int
    period_time: int
    median_first_solve_percentile: Optional[float]
    username: str
    temp_data: Optional[Dict]


def bucketed_period_info(user_contests, user_submissions, username, timeframe_days=356, contest_offset=2) -> List[PeriodInfo]:
    """Transform each 1 year period and user into a List of objects with information about that period.

    Args:
        timeframe_days (int, optional): number of days per bucket. Defaults to 356.
        contest_offset (int, optional): Number of first contests to skip. Defaults to 2.

    Returns: n_submissions each year and rating at the start of each year, there will be 1 more
        rating bucket than submission bucket.
    """
    timeframe = 60 * 60 * 24 * timeframe_days
    if len(user_contests) <= contest_offset + 1:
        return []
    start_time = user_contests.iloc[contest_offset]['updateTime']
    end_time = user_contests.iloc[-1]['updateTime'] + 1
    total_time = end_time - start_time
    time_buckets = (int)(total_time + timeframe) // timeframe

    def bucket_ind(time):
        ind = (int)((time - start_time) // timeframe)
        return ind
    NO_RATING = -99999
    buckets = [PeriodInfo(start_rating=NO_RATING, end_rating=NO_RATING,
                          n_correct=0, n_hard_correct=0,
                          n_gm_correct=0,
                          n_master_correct=0,
                          n_cm_correct=0,
                          n_expert_correct=0,
                          n_specialist_correct=0,
                          n_pupil_correct=0,
                          n_newbie_correct=0,
                          median_first_solve_percentile=None,
                          n_wrong=0,
                          n_contest_wrong=0,
                          n_contest_correct=0,
                          n_contests=0,
                          username=username,
                          period_time=0,
                          temp_data={'first_solves': {}})
               for _ in range(time_buckets)]
    buckets[0]['start_rating'] = user_contests.iloc[contest_offset]['newRating']
    if time_buckets < 1:
        return []
    for i in range(contest_offset + 1, len(user_contests)):
        contest = user_contests.iloc[i]
        bucket = bucket_ind(contest['updateTime'])
        if bucket >= len(buckets):
            continue
        assert bucket >= 0
        if bucket + 1 < len(buckets):
            buckets[bucket + 1]['start_rating'] = contest['newRating']
        buckets[bucket]['end_rating'] = contest['newRating']
        buckets[bucket]['n_contests'] += 1
        buckets[bucket]['period_time'] = contest['updateTime']
    solved_problems = set()

    def count_submission(submission):
        bucket = bucket_ind(submission['creationTime'])
        if bucket < 0 or bucket >= time_buckets or buckets[bucket]['start_rating'] == NO_RATING:
            return
        nonlocal solved_problems
        if submission['verdict'] == 'OK':
            if submission['problemId'] not in solved_problems: # don't double-count
                solved_problems.add(submission['problemId'])
                buckets[bucket]['n_correct'] += 1
                problem_ind = id_to_problem_ind[submission['problemId']]
                if problem_ind != None:
                    problem = problems.iloc[problem_ind]
                    problem_rating: int = problem['rating']  # type: ignore
                    match rating_to_name(problem_rating):
                        case 'newbie': buckets[bucket]['n_newbie_correct'] += 1
                        case 'pupil': buckets[bucket]['n_pupil_correct']+=1
                        case 'specialist': buckets[bucket]['n_specialist_correct']+=1
                        case 'expert': buckets[bucket]['n_expert_correct']+=1
                        case 'candidate master': buckets[bucket]['n_cm_correct']+=1
                        case 'master': buckets[bucket]['n_master_correct']+=1
                        case 'grandmaster': buckets[bucket]['n_gm_correct']+=1
                        case _: pass
                    if problem_rating > buckets[bucket]['start_rating']:
                        buckets[bucket]['n_hard_correct'] += 1
                    if submission['participantType'] == "CONTESTANT":
                        buckets[bucket]['n_contest_correct'] += 1
                        contest_id, problem_id = submission['problemId'].split(
                            ':')
                        solve_percentile = first_solve_percentile(
                            contest_id, submission['relativeTimeSeconds'])
                        if pd.notna(solve_percentile):
                            first_solve_data = buckets[bucket]['temp_data']['first_solves']
                            if contest_id in first_solve_data:
                                first_solve_data[contest_id] = min(
                                    solve_percentile, first_solve_data[contest_id])
                            else:
                                first_solve_data[contest_id] = solve_percentile
        else:  # verdict is not OK
            if submission['participantType'] == "CONTESTANT":
                buckets[bucket]['n_contest_wrong'] += 1
            buckets[bucket]['n_wrong'] += 1
    user_submissions.apply(count_submission, axis=1)
    for i in range(len(buckets)):
        if len(buckets[i]['temp_data']['first_solves']):
            buckets[i]['median_first_solve_percentile'] = float(np.median(
                list(buckets[i]['temp_data']['first_solves'].values())))
        else:
            buckets[i]['median_first_solve_percentile'] = None
        del buckets[i]['temp_data']
    i = 0
    while i < len(buckets):
        while i < len(buckets) and \
            (buckets[i]['start_rating'] == NO_RATING or buckets[i]['end_rating'] == NO_RATING
             or buckets[i]['median_first_solve_percentile'] is None):
            del buckets[i]
        i += 1
    return buckets

def compute_rating_change_correlation(contests, submissions, fname: Path,
                                      timeframe_days=356, contest_offset=2,
                                      get_delta_first_solves=False):
    all_buckets: List[PeriodInfo] = []
    for user, user_submissions in tqdm(submissions.items(), "Calculating solve and rating correlation"):
        user_contests = contests[user]
        buckets = bucketed_period_info(user_contests, user_submissions, user, timeframe_days, contest_offset)
        if get_delta_first_solves:
            for i in range(1, len(buckets)):
                buckets[i]['delta_first_solve_percentile'] = buckets[i]['median_first_solve_percentile'] - buckets[i - 1]['median_first_solve_percentile']
            all_buckets.extend(buckets[1:])
        else:
            all_buckets.extend(buckets)
    obj = {
        'n_submissions': [b['n_correct'] for b in all_buckets],
        'rating_change': [b['end_rating'] - b['start_rating'] for b in all_buckets],
        'start_rating': [b['start_rating'] for b in all_buckets],
        'start_color': [rating_to_name(b['start_rating']) for b in all_buckets],
        'n_hard_correct': [b['n_hard_correct'] for b in all_buckets],
        'avg_wrong':  [b['n_wrong'] / b['n_correct'] for b in all_buckets],
        'avg_contest_wrong':  [b['n_contest_wrong'] / b['n_contest_correct'] for b in all_buckets],
        'n_contests':  [b['n_contests'] for b in all_buckets],
        'username': [b['username'] for b in all_buckets],
        'time': [b['period_time'] for b in all_buckets],
        'first_solve_percentile': [(100.0 - b['median_first_solve_percentile']) for b in all_buckets],
        'solves_newbie': [b['n_newbie_correct'] for b in all_buckets],
        'solves_pupil': [b['n_pupil_correct'] for b in all_buckets],
        'solves_specialist': [b['n_specialist_correct'] for b in all_buckets],
        'solves_expert': [b['n_expert_correct'] for b in all_buckets],
        'solves_cm': [b['n_cm_correct'] for b in all_buckets],
        'solves_master': [b['n_master_correct'] for b in all_buckets],
        'solves_gm': [b['n_gm_correct'] for b in all_buckets]
    }
    if get_delta_first_solves:
        obj['delta_first_solve_percentile'] = [(-b['delta_first_solve_percentile']) for b in all_buckets]
    df = pd.DataFrame(obj)
    df = df.sort_values(by='start_rating')
    df.to_csv(fname, index=False)
    return df

def get_overall_stats(contests, submissions, fname):
    ratings = []
    submission_counts = []
    for user, submissions in submissions.items():
        ok_verdicts = submissions[submissions['verdict'] == 'OK']
        ok_ids = pd.unique(ok_verdicts['problemId'])
        submission_counts.append(len(ok_ids))
        curRating = contests[user].iloc[len(contests[user]) - 1]['newRating']
        ratings.append(curRating)
    df = pd.DataFrame({
        'n_submissions': submission_counts,
        'rating': ratings,
    })
    df.to_csv(fname, index=False)

def create_user_stories(df=None):
    if df is None:
        with open(analysis_folder / 'rating_change_10k.csv') as f:
            df = pd.read_csv(f)
    df = df.sort_values(by='time')
    long_term_users = []
    for username, n_years in Counter(df['username']).items():
        if n_years >= 5:
            long_term_users.append(username)
    
    df = df.loc[df['username'].isin(long_term_users)]
    df.to_csv(analysis_folder / 'rating_change_long_term.csv', index=False)

def problemLearnings(contests, submissions):
    n_buckets = 5
    problemIncreases = [defaultdict(lambda: 0) for _ in range(n_buckets)]
    problemCounts = [defaultdict(lambda: 0) for _ in range(n_buckets)]
    for user, submissionList in tqdm(submissions.items(), "Calculating problem learnings"):
        user_ratings = contests[user]
        if len(user_ratings) < 5:
            continue  # data is not that useful
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
                improvement, oldRating = shortTermImprovement(
                    user_ratings, submission['creationTime'])
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
            problemUsefulness.append((mean, count, pId))
        logging.info(f"Problems with enough data: {len(problemUsefulness)}")
        problemUsefulness = sorted(problemUsefulness, key=lambda x: x[0])
        logging.info(
            f"Most useful:  {list(reversed(problemUsefulness[-50:]))}")
        logging.info("ALL:")
        logging.info(problemUsefulness)
        bucketsUsefulness.append(problemUsefulness)
    return bucketsUsefulness


def reformat_problem_tags():
    tagsets = problems['tags']
    tag_set = set()

    def get_tags(tag_str: str) -> List[str]:
        if pd.notna(tag_str):
            return tag_str.split('+')
        else:
            return []
    for tagset in tagsets:
        tag_set = tag_set.union(get_tags(tagset))
    extra_cols = {name: [False for _ in range(
        len(problems))] for name in tag_set.union(['rank'])}
    for i in range(len(problems)):
        tags = get_tags(problems.iloc[i]['tags'])
        for tag in tags:
            extra_cols[tag][i] = True
        difficulty = problems.iloc[i]['rating']
        if difficulty:
            extra_cols['rank'][i] = rating_to_name(difficulty)
        else:
            extra_cols['rank'][i] = None

    df = pd.DataFrame(extra_cols)
    df = problems.join(df)
    df = df.dropna()
    df.to_csv(analysis_folder / 'problems_with_tags.csv', index=False)


def explode_problem_tags():
    problem_w_tag_list = problems.assign(tags=problems['tags'].str.split("+"))
    problem_w_tag_list['rank'] = problems['rating'].map(rating_to_name)
    exploded = problem_w_tag_list.explode('tags')
    exploded.to_csv(analysis_folder / 'problems_tag_explode.csv', index=False)
    return exploded

def count_problem_tags(exploded):
    counts = exploded.groupby('tags').count()['problemId']
    counts.to_csv(analysis_folder / 'problem_tag_count.csv', index=True)
    

def main():
    # count_problem_tags(explode_problem_tags())
    subset_size = 0
    logging.basicConfig(
        filename=f'read_data_{subset_size}.log', filemode='w', level=logging.INFO)
    contests, submissions = get_data(subset_size)
    df = compute_rating_change_correlation(contests, submissions,  analysis_folder / 'rating_change.csv', get_delta_first_solves=True)
    df = get_overall_stats(contests, submissions,  analysis_folder / 'rating_overall.csv')
    # create_user_stories(df)
    problemLearnings(contests, submissions)


if __name__ == "__main__":
    main()
