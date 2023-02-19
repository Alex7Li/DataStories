import pandas as pd
from pathlib import Path
import sklearn.linear_model
analysis_folder = Path('cf_stats/analysis')


def analyze(df, y='rating_change'):
    feature_columns = ['n_easy_correct', 'n_hard_correct'] #, 'avg_wrong', 'avg_contest_wrong', 'first_solve_percentile']  # , 'start_rating']
    X_data = df[feature_columns]
    y_data = df[[y]]
    model = sklearn.linear_model.LinearRegression(copy_X=True)
    model.fit(X_data, y_data)
    print(f"Coefficient of determination: {model.score(X_data, y_data)}")
    assert model.coef_.shape[0] == 1
    print(list(zip(feature_columns, model.coef_[0])))


def predict_rating_change():
    df = pd.read_csv(analysis_folder / 'rating_change_all.csv')
    print(df['n_submissions'].corr(df['rating_change']))
    print(df['n_hard_correct'].corr(df['rating_change']))
    df['n_easy_correct'] = df['n_submissions'] - df['n_hard_correct']
    print("All")
    analyze(df)
    for rating_color in ['pupil', 'novice', 'specialist', 'expert', 'candidate master', 'master', 'grandmaster']:
        print(rating_color)
        df_color = df[df['start_color'] == rating_color]
        analyze(df_color)

def predict_first_solve_time():
    df = pd.read_csv(analysis_folder / 'first_solve_delta_all.csv')
    print(df['n_submissions'].corr(df['delta_first_solve_percentilew']))
    print(df['n_hard_correct'].corr(df['delta_first_solve_percentile']))
    df['n_easy_correct'] = df['n_submissions'] - df['n_hard_correct']
    print("All")
    analyze(df, 'delta_first_solve_percentile')
    for rating_color in ['pupil', 'novice', 'specialist', 'expert', 'candidate master', 'master', 'grandmaster']:
        print(rating_color)
        df_color = df[df['start_color'] == rating_color]
        analyze(df_color, 'delta_first_solve_percentile')


if __name__ == '__main__':
    # predict_rating_change()
    predict_first_solve_time()
