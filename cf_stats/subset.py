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
def main():
    rca = pd.read_csv(analysis_folder / 'rating_change_all.csv')
    rca = rca.groupby('start_color').sample(1000)
    rca = rca.sort_values(by='start_rating')
    rca.to_csv(analysis_folder / 'rating_change_mobile_subset.csv')

if __name__ == '__main__':
    main()