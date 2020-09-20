# Spotify Recommendations

## What is this:
[This](http://collinjoseph.pythonanywhere.com/ProjectInfo) is a website made to give any Spotify user a personal recommendation from the Spotify's United States Top 50 songs playlist.

## How to use it:
Simply press the form button.
It will redirect you to a spotify page to sign into.
Once that is completed you will be shown your personal recommendation.

## How does it work:
It is a combinations of data collection from Spotify, data processing, and machine learning to create your personal recommendation.

### 1) Data Collection:
Pressing the button below will you take you to a authentication page for Spotify.
There you will sign into your account.
This grants the server temporary access to some of your music preferences.
With that permission the server requests your most played songs from the last 4 weeks.
Using the list of songs, the server pulls a list of features on each song including things like the "energy" and "acousticness" of the song.
### 2) Data Processing:
Spotify like most APIs returns jsons.
So the next step was to take the jsons and convert them to data frames.
Then lastly with the data organized, the data is scaled using a min max scalar.
### 3) Machine Learning:
The first step is to train a nearest neighbors algorithm on the music from the Top 50 playlist.
You can think of this like graphing all those points of a 9 dimensional graph.
Then the next step is to go through your most played songs and compare the features of them with songs from the playlist.
This is done by finding the Euclidean distance between each point and then picking the two points that are closest to each other.
Then this is what is presented on the recommendation page, the recommended song and the favorite of yours that it is similar to.
