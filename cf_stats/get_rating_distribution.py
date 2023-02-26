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

def main():
    standings_folder = Path('cf_stats/standings_data')

    contest_id = '1782'
    data_path = standings_folder / 'standings' / f'{contest_id}.csv'
    with open(data_path) as f:
        df = pd.read_csv(f)
    sum(df['NewTrueRating'] > 2100)
    df.hist('NewTrueRating')

if __name__ == '__main__':
    main()
