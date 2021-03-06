import pandas as pd
import numpy as np
import datetime

class billboard:
    def __init__(self):
        #features = pd.read_csv('Hot 100 Audio Features.csv')
        f = pd.read_csv('audio_features.csv')
        # only include tracks that have a spotify id on file for now
        #f = f[~f['spotify_track_id'].isnull()][f.columns[0:5]].drop_duplicates()
        f = f.dropna(subset=['spotify_track_id', 'spotify_genre'])[f.columns[0:5]].drop_duplicates()
        f['spotify_genre'] = [x.strip('[]').strip('\'').split('\', \'') for x in f['spotify_genre']]
        self.features = f

        #stuff = pd.read_csv('Hot Stuff.csv')
        stuff = pd.read_csv('https://query.data.world/s/go22golrhaeqllglpuxnnd7irb3l2j')
        stuff['WeekID'] = pd.to_datetime(stuff['WeekID'])
        self.stuff = stuff

    def weeklyAvg(self):
        # average weekly position
        avg_pos = self.stuff[['WeekID', 'Week Position', 'SongID']].groupby(by=['SongID']).mean()
        # first week the track appeared in the chart
        minweek = self.stuff[['WeekID', 'SongID']].groupby(by=['SongID']).min().rename(columns={'WeekID':'firstWeekID'})
        # last week the track appeared in the chart
        maxweek = self.stuff[['WeekID', 'SongID']].groupby(by=['SongID']).max().rename(columns={'WeekID':'lastWeekID'})
        # total # of weeks the track was in the chart
        max_occ = self.stuff[['SongID','Instance','Weeks on Chart']].groupby(by=['SongID']).max()

        stats = avg_pos.join(minweek).join(maxweek).join(max_occ)
        self.data = self.features.join(stats, on='SongID').rename(columns={'Week Position':'Avg Weekly'})

    def getList(self, how='avg', length=30, genre=['pop','dance pop'], startY=2019, endY=2019):
        # songs should have left chart after lower bound (e.g. 2019 songs should still be on chart after 2019/1/1)
        lowerBound = datetime.datetime(startY, 1, 1)
        # songs should have entered chart before upper bound (e.g. 2019 songs should have been on chart before 2019/12/31)
        upperBound = datetime.datetime(endY, 12, 31)

        #if how == ''  ; implement later for other possible ranking methods
        self.weeklyAvg()

        data = self.data
        filter_t = data[(data['firstWeekID'] < upperBound) & (data['lastWeekID'] > lowerBound)]
        filter_g = filter_t[filter_t.spotify_genre.apply(lambda x: bool(set(x) & set(genre)))]
        
        playlist = filter_g.sort_values(['Instance','Avg Weekly','Weeks on Chart'], ascending=[True,True,False]).reset_index(drop=True)
        #return playlist[playlist.columns[0:5]][:length] # for test
        return playlist['spotify_track_id'][:length].to_list()