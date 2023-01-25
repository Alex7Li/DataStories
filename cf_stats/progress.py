import os
n_ratings = len(os.listdir('data/ratings'))
n_submissions = len(os.listdir('data/ratings'))
print(f"{n_ratings=} {n_submissions=} (should be equal)")