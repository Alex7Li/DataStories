import itertools
import pandas as pd
from pathlib import Path
import sklearn.linear_model
analysis_folder = Path('cf_stats/analysis')


def analyze(df, y='rating_change'):
    feature_columns = ['n_easy_correct', 'n_hard_correct'] #, 'avg_wrong', 'avg_contest_wrong', 'first_solve_percentile']  # , 'start_rating']
    feature_columns = ['solves_newbie', 'solves_pupil', 'solves_specialist', 'solves_expert', 'solves_cm', 'solves_master', 'solves_gm']
    feature_columns = ['solves_d1', 'solves_d2', 'solves_d3']
    X_data = df[feature_columns]
    y_data = df[[y]]
    model = sklearn.linear_model.LinearRegression(copy_X=True)
    model.fit(X_data, y_data)
    print(f"Coefficient of determination: {model.score(X_data, y_data)}")
    assert model.coef_.shape[0] == 1
    print(list(zip(feature_columns, model.coef_[0])))

def read_rating_change():
    df = pd.read_csv(analysis_folder / 'rating_change_all.csv')
    df['n_easy_correct'] = df['n_submissions'] - df['n_hard_correct']
    df['solves_d3'] = df['solves_newbie'] + df['solves_pupil']
    df['solves_d2'] = df['solves_specialist'] + df['solves_expert']
    df['solves_d1'] = df['solves_cm'] + df['solves_master'] + df['solves_gm']
    return df

def predict_rating_change():
    df = read_rating_change()
    print("All")
    analyze(df)
    for rating_color in ['newbie', 'pupil', 'specialist', 'expert', 'candidate master', 'master', 'grandmaster']:
        print(rating_color)
        df_color = df[df['start_color'] == rating_color]
        analyze(df_color)

def predict_first_solve_time():
    df = pd.read_csv(analysis_folder / 'first_solve_delta_all.csv')
    print(df['n_submissions'].corr(df['delta_first_solve_percentile']))
    print(df['n_hard_correct'].corr(df['delta_first_solve_percentile']))
    df['n_easy_correct'] = df['n_submissions'] - df['n_hard_correct']
    print("All")
    analyze(df, 'delta_first_solve_percentile')
    for rating_color in ['pupil', 'novice', 'specialist', 'expert', 'candidate master', 'master', 'grandmaster']:
        print(rating_color)
        df_color = df[df['start_color'] == rating_color]
        analyze(df_color, 'delta_first_solve_percentile')

def get_correlation_matrix():
    df = read_rating_change()
    column_names = ['n_easy_correct', 'n_hard_correct', 'first_solve_percentile', 'delta_first_solve_percentile', 'rating_change']
    values = [[df[row_name].corr(df[col_name]) for col_name in column_names] for row_name in column_names]
    out_df = pd.DataFrame(values, columns=column_names, index=column_names)
    out_df.to_csv(analysis_folder /'correlations.csv')
    
    expand_json = {
        'Row': [],
        'Col': [],
        'Correlation': [],
    }
    for row_name, col_name in itertools.product(column_names, column_names):
        expand_json['Row'].append(row_name)
        expand_json['Col'].append(col_name)
        expand_json['Correlation'].append(df[row_name].corr(df[col_name]))
    expand_df = pd.DataFrame(expand_json, index=None)
    expand_df.to_csv(analysis_folder /'correlations_expand.csv')

if __name__ == '__main__':
    # predict_rating_change()
    # predict_first_solve_time()
    get_correlation_matrix()
