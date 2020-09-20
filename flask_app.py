from flask import Flask, render_template, redirect, url_for, session, request
from forms import SignInForm
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import pprint
import pandas as pd
import numpy as np
import pprint
from sklearn.preprocessing import MinMaxScaler
from sklearn.neighbors import NearestNeighbors
import yaml

app = Flask(__name__)

with open('./credentials.yml') as f:
    credentials = yaml.load(f, Loader=yaml.FullLoader)

app.config['SECRET_KEY'] = credentials['wtf_forms']['SECRET_KEY']

sp_oauth = spotipy.oauth2.SpotifyOAuth(client_id=credentials['api']['client_id'],
                                       client_secret=credentials['api']['client_secret'],
                                       redirect_uri="http://127.0.0.1:5000/SpotifyRedirect",
                                       scope="user-library-read, user-top-read")


@app.route('/')
def homePage():
    print("Hello")
    login_url = sp_oauth.get_authorize_url()
    return redirect(login_url)
    # results = sp.current_user_top_tracks(limit=50, time_range='medium_term')
    print("World")
    form = SignInForm()
    if form.validate_on_submit():
        return redirect(url_for('userInfo'))
    return render_template('HomePage.html', form=form)


@app.route('/SpotifyRedirect')
def spotifyRedirect():
    code = request.args['code']
    token_info = sp_oauth.get_access_token(code)
    access_token = token_info['access_token']
    session['access_token'] = access_token
    access_token = session['access_token']
    return (redirect('/Recommendations'))


@app.route('/Recommendations')
def top40recommendations():
    access_token = session['access_token']
    sp = spotipy.Spotify(access_token)
    results = sp.current_user_top_tracks(limit=50, time_range='medium_term')

    personalDF = pd.DataFrame(columns=['ID', 'Artist', 'Track'])

    for row in results['items']:
        personalDF = personalDF.append({'ID': row['id'], 'Artist': row['artists'][0]['name'], 'Track': row['name']},
                                       ignore_index=True)

    personalIDList = personalDF['ID'].tolist()

    personalAudioFeaturesOnly = sp.audio_features(personalIDList)

    personalAudioFeaturesDF = pd.DataFrame(columns=['ID',
                                                    'Artist',
                                                    'Track',
                                                    'danceability',
                                                    'energy',
                                                    'loudness',
                                                    'speechiness',
                                                    'acousticness',
                                                    'instrumentalness',
                                                    'liveness',
                                                    'valence',
                                                    'tempo'])

    counter = 0
    for dict in personalAudioFeaturesOnly:
        tempDict = {
            'ID': personalDF.iloc[counter][0],
            'Artist': personalDF.iloc[counter][1],
            'Track': personalDF.iloc[counter][2],
            'danceability': dict['danceability'],
            'energy': dict['energy'],
            'loudness': dict['loudness'],
            'speechiness': dict['speechiness'],
            'acousticness': dict['acousticness'],
            'instrumentalness': dict['instrumentalness'],
            'liveness': dict['liveness'],
            'valence': dict['valence'],
            'tempo': dict['tempo']}
        personalAudioFeaturesDF = personalAudioFeaturesDF.append(tempDict, ignore_index=True)
        counter += 1

    top50 = sp.playlist_items('37i9dQZEVXbLRQDuF5jeBp')

    top50DF = pd.DataFrame(columns=['ID', 'Artist', 'Track'])

    for row in top50['items']:
        top50DF = top50DF.append(
            {'ID': row['track']['id'], 'Artist': row['track']['artists'][0]['name'], 'Track': row['track']['name']},
            ignore_index=True)

    top50IDList = top50DF['ID'].tolist()

    top50AudioFeaturesOnly = sp.audio_features(top50IDList)
    top50AudioFeaturesDF = pd.DataFrame(columns=['ID',
                                                 'Artist',
                                                 'Track',
                                                 'danceability',
                                                 'energy',
                                                 'loudness',
                                                 'speechiness',
                                                 'acousticness',
                                                 'instrumentalness',
                                                 'liveness',
                                                 'valence',
                                                 'tempo'])

    counter = 0
    for dict in top50AudioFeaturesOnly:
        tempDict = {
            'ID': top50DF.iloc[counter][0],
            'Artist': top50DF.iloc[counter][1],
            'Track': top50DF.iloc[counter][2],
            'danceability': dict['danceability'],
            'energy': dict['energy'],
            'loudness': dict['loudness'],
            'speechiness': dict['speechiness'],
            'acousticness': dict['acousticness'],
            'instrumentalness': dict['instrumentalness'],
            'liveness': dict['liveness'],
            'valence': dict['valence'],
            'tempo': dict['tempo']}
        top50AudioFeaturesDF = top50AudioFeaturesDF.append(tempDict, ignore_index=True)
        counter += 1

    top50AudioFeaturesDataOnlyDF = top50AudioFeaturesDF.drop(columns=['ID', 'Artist', 'Track'])
    top50AudioFeaturesDataOnlyDF['instrumentalness'] = top50AudioFeaturesDataOnlyDF['instrumentalness'].astype(
        str).astype('float')

    personalAudioFeaturesDataOnlyDF = personalAudioFeaturesDF.drop(columns=['ID', 'Artist', 'Track'])
    personalAudioFeaturesDataOnlyDF['instrumentalness'] = personalAudioFeaturesDataOnlyDF['instrumentalness'].astype(
        str).astype('float')

    scaler = MinMaxScaler()

    scaler.fit(top50AudioFeaturesDataOnlyDF)

    top50AudioFeaturesDataOnlyDF = pd.DataFrame(scaler.transform(top50AudioFeaturesDataOnlyDF),
                                                columns=top50AudioFeaturesDataOnlyDF.columns)

    top50AudioFeaturesDataOnlyDF = pd.DataFrame(scaler.transform(top50AudioFeaturesDataOnlyDF),
                                                columns=top50AudioFeaturesDataOnlyDF.columns)

    top50AudioFeaturesDF = top50AudioFeaturesDF.join(top50AudioFeaturesDataOnlyDF, lsuffix='_drop', rsuffix='_scaled')

    for name in top50AudioFeaturesDF.columns:
        if ('drop' in name):
            top50AudioFeaturesDF = top50AudioFeaturesDF.drop(columns=[name])

    personalAudioFeaturesDF = personalAudioFeaturesDF.join(personalAudioFeaturesDataOnlyDF, lsuffix='_drop',
                                                           rsuffix='_scaled')

    for name in personalAudioFeaturesDF.columns:
        if ('drop' in name):
            personalAudioFeaturesDF = personalAudioFeaturesDF.drop(columns=[name])

    KNN = NearestNeighbors(n_neighbors=1, p=2)
    KNN.fit(top50AudioFeaturesDataOnlyDF)
    distances, index = KNN.kneighbors(personalAudioFeaturesDataOnlyDF, return_distance=True)

    min = np.amin(distances[np.nonzero(distances)])

    i = 0
    for x in distances:
        if (x == min):
            minIndex = i
            break
        else:
            i += 1

    # print("Min distance:",min)
    print("Recomended Song:", top50AudioFeaturesDF.iloc[index[minIndex]]['Track'].values[0], "by",
          top50AudioFeaturesDF.iloc[index[minIndex]]['Artist'].values[0])
    print("Based off:", personalAudioFeaturesDF.iloc[minIndex]['Track'], "by",
          personalAudioFeaturesDF.iloc[minIndex]['Artist'])

    outString = "Recomended Song: {s1} by {a1} Based off: {s2} by {a2}".format(
        s1=top50AudioFeaturesDF.iloc[index[minIndex]]['Track'].values[0],
        a1=top50AudioFeaturesDF.iloc[index[minIndex]]['Artist'].values[0],
        s2=personalAudioFeaturesDF.iloc[minIndex]['Track'],
        a2=personalAudioFeaturesDF.iloc[minIndex]['Artist'])

    print(outString)
    print(type(outString))

    return outString

if __name__ == '__main__':
    app.run()