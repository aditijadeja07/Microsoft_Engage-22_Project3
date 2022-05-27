#importing modules
import streamlit as st
st.set_page_config(page_title="Song Recommendation Engine", layout="wide")

import pandas as pd
from sklearn.neighbors import NearestNeighbors
import plotly.express as px
import streamlit.components.v1 as components

# for better performance of application
@st.cache(allow_output_mutation=True)

# loading the data
def load_data():
    df = pd.read_csv("data/filtered_track_df.csv")
    df['genres'] = df.genres.apply(lambda x: [i[1:-1] for i in str(x)[1:-1].split(", ")])
    exploded_track_df = df.explode("genres")
    return exploded_track_df

#defining genre and audio feature list
genre_names = ['Dance Pop', 'Electronic', 'Electropop', 'Hip Hop', 'Jazz', 'K-pop', 'Latin', 'Pop', 'Pop Rap', 'R&B', 'Rock']
audio_feats = ["acousticness", "danceability", "energy", "instrumentalness", "valence", "tempo"]

exploded_track_df = load_data()


# function to find nearest neighbour for given combination
def n_neighbors_uri_audio(genre, start_year, end_year, test_feat):
    genre = genre.lower()
    genre_data = exploded_track_df[(exploded_track_df["genres"]==genre) & (exploded_track_df["release_year"]>=start_year) & (exploded_track_df["release_year"]<=end_year)]
    genre_data = genre_data.sort_values(by='popularity', ascending=False)[:500]

    neigh = NearestNeighbors()
    neigh.fit(genre_data[audio_feats].to_numpy())

    n_neighbors = neigh.kneighbors([test_feat], n_neighbors=len(genre_data), return_distance=False)[0]

    uris = genre_data.iloc[n_neighbors]["uri"].tolist()
    audios = genre_data.iloc[n_neighbors][audio_feats].to_numpy()
    return uris, audios

#----------main page---------- 
def page():
    title = "Song Recommendation Engine"
    st.title(title)
    
    intro = '<p style="font-family:Courier; color:pink; font-size: 20px;">Welcome to our application !Kindly select your favourite genre then Try playing around with different settings and Enjoy the songs recommended by our system!</p>'
    st.markdown(intro, unsafe_allow_html=True)

    st.markdown("##")

# creating a container 
    with st.container():
        col1, col2,col3,col4 = st.columns((2,0.5,0.5,0.5))
        with col3:
            gen = '<p style="font-family:Courier; color:White; font-size: 20px;">Choose your favourite genre:</p>'
            st.markdown(gen, unsafe_allow_html=True)
            genre = st.radio(
                "",
                genre_names, index=genre_names.index("Pop"))
        with col1:
            fet = '<p style="font-family:Courier; color:White; font-size: 20px;">Set the combination of audio features: </p>'
            st.markdown(fet, unsafe_allow_html=True)
            start_year, end_year = st.slider(
                'Select the year range',
                1990, 2019, (2015, 2017)
            )
            acousticness = st.slider(
                'Acousticness',
                0.0, 1.0, 0.1)
            danceability = st.slider(
                'Danceability',
                0.0, 1.0, 0.2)
            energy = st.slider(
                'Energy',
                0.0, 1.0, 0.3)
            instrumentalness = st.slider(
                'Instrumentalness',
                0.0, 1.0, 0.4)
            valence = st.slider(
                'Valence',
                0.0, 1.0, 0.2)
            tempo = st.slider(
                'Tempo',
                0.0, 244.0, 118.0)

    tracks_per_page = 6
    test_feat = [acousticness, danceability, energy, instrumentalness, valence, tempo]
    uris, audios = n_neighbors_uri_audio(genre, start_year, end_year, test_feat)


    tracks = []
    for uri in uris:
        track = """<iframe src="https://open.spotify.com/embed/track/{}" width="260" height="380" frameborder="0" allowtransparency="true" allow="encrypted-media"></iframe>""".format(uri)
        tracks.append(track)

#keeping track of previous inputs for displaying unique song every time
    if 'previous_inputs' not in st.session_state:
        st.session_state['previous_inputs'] = [genre, start_year, end_year] + test_feat
    
    current_inputs = [genre, start_year, end_year] + test_feat
    if current_inputs != st.session_state['previous_inputs']:
        if 'start_track_i' in st.session_state:
            st.session_state['start_track_i'] = 0
        st.session_state['previous_inputs'] = current_inputs

    if 'start_track_i' not in st.session_state:
        st.session_state['start_track_i'] = 0

# container of displaying songs
    with st.container():
        col1, col2, col3 = st.columns([2,1,2])
        if st.button("Recommend More Songs"):
            if st.session_state['start_track_i'] < len(tracks):
                st.session_state['start_track_i'] += tracks_per_page
                
#current 6 tracks and audio
        current_tracks = tracks[st.session_state['start_track_i']: st.session_state['start_track_i'] + tracks_per_page]
        current_audios = audios[st.session_state['start_track_i']: st.session_state['start_track_i'] + tracks_per_page]
        
# displaying songs left[col1] and right[col3] side 
        if st.session_state['start_track_i'] < len(tracks):
            for i, (track, audio) in enumerate(zip(current_tracks, current_audios)):
                if i%2==0:
                    with col1:
                        components.html(
                            track,
                            height=400,
                        )
                        with st.expander("See more details"):
                            df = pd.DataFrame(dict(
                            r=audio[:5],
                            theta=audio_feats[:5]))
                            fig = px.line_polar(df, r='r', theta='theta', line_close=True)
                            fig.update_layout(height=400, width=340)
                            st.plotly_chart(fig)
            
                else:
                    with col3:
                        components.html(
                            track,
                            height=400,
                        )
                        with st.expander("See more details"):
                            df = pd.DataFrame(dict(
                                r=audio[:5],
                                theta=audio_feats[:5]))
                            fig = px.line_polar(df, r='r', theta='theta', line_close=True)
                            fig.update_layout(height=400, width=340)
                            st.plotly_chart(fig)
                            
# if there is no more song to recommend
        else:
            st.write("No songs left to recommend")

page()
