import itertools
from pathlib import Path

from scipy.signal import savgol_filter
import pandas as pd

analysis_folder = Path('cf_stats/analysis')

def make_bands(df, x_var, y_var, bands, width=100, freq=10, min_val=None, max_val=None):
    df = df.sort_values(by=x_var)
    if min_val is None:
        min_val = df.iloc[0][x_var]
    if max_val is None:
        max_val = df.iloc[len(df) - 1][x_var]
    def format_v(band):
        if band == y_var:
            return band
        return f"{band * 100}%"
    band_vals = {format_v(band):[] for band in itertools.chain([y_var], bands)}
    for center in range(min_val + width, max_val - width, freq):
        vals = df[(center - width < df[x_var]) & (df[x_var] < center + width)] [y_var]
        for i, v in enumerate(vals.quantile(bands)):
            band_vals[format_v(bands[i])].append(v)
        band_vals[y_var].append(center)
    for b in bands:
        band_vals[format_v(b)] = savgol_filter(
            band_vals[format_v(b)], 20, 2)
    new_df = pd.DataFrame(band_vals)
    return new_df

def plot_rating_change(fname):
    df = pd.read_csv(analysis_folder / f'{fname}.csv')
    x_var = 'n_submissions'
    y_var = 'rating_change'
    bands = [.05, .15, .3, .5, .7, .85, .95]
    out_df = make_bands(df, x_var, y_var, bands, min_val=-100, max_val=2000)
    with open(analysis_folder / f'{fname}_bands.csv', 'w+') as f:
        out_df.to_csv(f, index=False)

def plot_rating_value(fname):
    df = pd.read_csv(analysis_folder / f'{fname}.csv')
    x_var = 'n_submissions'
    y_var = 'rating'
    bands = [.05, .15, .3, .5, .7, .85, .95]
    out_df = make_bands(df, x_var, y_var, bands, min_val=-200, width=200, max_val=10000)
    with open(analysis_folder / f'{fname}_bands.csv', 'w+') as f:
        out_df.to_csv(f, index=False)

if __name__ == '__main__':
    # plot_rating_change('rating_change_all')
    plot_rating_value('rating_overall')
