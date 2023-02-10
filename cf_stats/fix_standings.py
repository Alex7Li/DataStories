import os
import json
import pandas as pd
from tqdm import tqdm
from pathlib import Path
data_folder = Path('cf_stats/data')
standings_data_folder = Path('cf_stats/standings_data')
def main():
    metadata_path = standings_data_folder / 'standing_metadata.json'
    with open(metadata_path) as f:
        contest_metadata = json.load(f)
    offsets = [0, 50, 150, 300, 550, 900, 1400]
    user_rating_offset_contests = {}
    inds = sorted(contest_metadata.keys(), key=lambda x: contest_metadata[x]['end_time'])
    for contest_ind in inds:
        metadata = contest_metadata[contest_ind]
        if metadata['rated']:
            standings = pd.read_csv(standings_data_folder / 'standings' / f"{contest_ind}.csv")
            def update_true_ratings(entry):
                if entry.handle not in user_rating_offset_contests:
                    if entry.oldDisplayRating == 1500:
                        user_rating_offset_contests[entry.handle] = -1
                    else:
                        assert entry.oldDisplayRating == 0
                        assert entry.newDisplayRating[0] < 1000
                        user_rating_offset_contests[entry.handle] = 7
                offset_ind = user_rating_offset_contests[entry.handle]
                if offset_ind >= 0:
                    entry.OldTrueRating = entry.oldDisplayRating + offsets[offset_ind]
                else:
                    entry.OldTrueRating = entry.oldDisplayRating
                if offset_ind >= 1:
                    entry.NewTrueRating = entry.newDisplayRating + offsets[offset_ind - 1]
                else:
                    entry.NewTrueRating = entry.newDisplayRating
                user_rating_offset_contests[entry.handle]-=1
                return entry

            standings = standings.apply(update_true_ratings, axis=1)

def fix_contests(subset_size=0):
    filenames = os.listdir(data_folder / 'contests')
    if subset_size != 0:
        filenames = filenames[:subset_size]
    ratings = {}
    submissions = {}
    for handlecsv in tqdm(filenames, "reading data"):
        file_path =data_folder / 'contests' / handlecsv
        contest_results = pd.read_csv(file_path)
        # fix result of a typo from earlier
        if len(contest_results['oldRating']) > 2:
            contest_results['oldRating'][2] = contest_results['newRating'][1]
        contest_results.to_csv(file_path)
    

if __name__ == '__main__':
    main()