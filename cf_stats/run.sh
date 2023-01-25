screen -X -S cf_data_gen quit
screen -S cf_data_gen -dm python get_data.py
screen -list