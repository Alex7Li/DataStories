import os
import pandas as pd
from pathlib import Path
from collections import defaultdict
import itertools
import logging
from tqdm import tqdm
from typing import List, TypedDict
tqdm.pandas()

analysis_folder = Path('cf_stats/analysis')
data_folder = Path('cf_stats/data')
problems = pd.read_csv(data_folder / 'problems.csv')
id_to_problem_ind = defaultdict(lambda: None)
for i in range(len(problems)):
    id_to_problem_ind[problems.iloc[i]['problemId']] = i


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


def is_griefing(user_ratings):
    # Sometimes people lose a lot on purpose.
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


def rating_to_name(rating):
    if rating == None:
        return 'unknown'
    if rating < 1200:
        return 'pupil'
    if rating < 1400:
        return 'novice'
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
    username: str


def bucketed_period_info(user_contests, user_submissions, username, timeframe_days=356, contest_offset=2, get_tags=False) -> List[PeriodInfo]:
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
    buckets = [PeriodInfo(start_rating=NO_RATING, end_rating=NO_RATING, n_correct=0, n_hard_correct=0, username=username)
               for _ in range(time_buckets)]
    buckets[0]['start_rating'] = user_contests.iloc[contest_offset]['newRating']
    if time_buckets <= 1:
        return []
    for i in range(contest_offset + 1, len(user_contests)):
        contest = user_contests.iloc[i]
        bucket = bucket_ind(contest['updateTime'])
        if bucket >= n_buckets:
            continue
        assert bucket >= 0
        if bucket + 1 < len(buckets):
            buckets[bucket + 1]['start_rating'] = contest['newRating']
        buckets[bucket]['end_rating'] = contest['newRating']

    def count_submission(submission):
        bucket = bucket_ind(submission['creationTime'])
        if bucket < 0 or bucket >= time_buckets or buckets[bucket]['start_rating'] == NO_RATING:
            return
        if submission['verdict'] == 'OK':
            buckets[bucket]['n_correct'] += 1
            problem_ind = id_to_problem_ind[submission['problemId']]
            if problem_ind != None:
                problem = problems.iloc[problem_ind]
                problem_rating: int = problem['rating']  # type: ignore
                if problem_rating > buckets[bucket]['start_rating']:
                    buckets[bucket]['n_hard_correct'] += 1
    user_submissions.apply(count_submission, axis=1)
    i = 0
    while i < len(buckets):
        while i < len(buckets) and (buckets[i]['start_rating'] == NO_RATING or buckets[i]['end_rating'] == NO_RATING):
            del buckets[i]
        i += 1
    return buckets


def compute_solve_rating_correlation(contests, submissions):
    all_buckets = []
    for user, user_submissions in tqdm(submissions.items(), "Calculating solve and rating correlation"):
        user_contests = contests[user]
        buckets = bucketed_period_info(user_contests, user_submissions, user)
        all_buckets.extend(buckets)
    df = pd.DataFrame({
        'n_submissions': [b['n_correct'] for b in all_buckets],
        'rating_change': [b['end_rating'] - b['start_rating'] for b in all_buckets],
        'start_rating': [b['start_rating'] for b in all_buckets],
        'start_color': [rating_to_name(b['start_rating']) for b in all_buckets],
        'n_hard_correct': [b['n_hard_correct'] for b in all_buckets],
        'username': [b['username'] for b in all_buckets]
    })
    df = df.sort_values(by='start_rating')
    df.to_csv(analysis_folder / 'rating_change.csv', index=False)


def problemLearnings(contests, submissions):
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
    extra_cols = {name: [False for _ in range(len(problems))] for name in tag_set.union(['rank'])}
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

def main():
    explode_problem_tags()
    # subset_size = 200
    # contests, submissions = get_data(subset_size)
    # compute_solve_rating_correlation(contests, submissions)
    # logging.basicConfig(
    #     filename=f'best_problems_{subset_size}.log', filemode='w', level=logging.INFO)
    # problemLearnings(contests, submissions)


if __name__ == "__main__":
    main()
