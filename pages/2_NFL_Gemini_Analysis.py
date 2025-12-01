import streamlit as st
import google.generativeai as genai
import requests



genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# TODO: Fill out your team number, section, and team members

st.title("NBA Insights: AI-Powered Breakdown")
st.header("CS 1301")
st.subheader("Team 111, Web Development - Section A")
st.subheader("Alexander Jaber, Bryce Phan")


# Import functions from Phase 2 if needed
# from 1_NFL_API_Analysis import get_nfl_teams, get_team_stats

genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

st.title("NFL Insights: AI-Powered Team Breakdown")

st.write("""
This page uses real NFL team data from ESPN and processes it through Google Gemini 
to create a clear, human-style comparison between two NFL teams. 
You select the teams — the model generates the breakdown.
""")


TEAMS_URL = "https://site.api.espn.com/apis/site/v2/sports/football/nfl/teams"

@st.cache_data
def get_nfl_teams():
    resp = requests.get(TEAMS_URL)
    if resp.status_code != 200:
        return []
    data = resp.json()
    teams = data.get("sports", [{}])[0].get("leagues", [{}])[0].get("teams", [])
    team_list = []
    for t in teams:
        info = t.get("team", {})
        tid = info.get("id")
        name = info.get("displayName")
        if tid and name:
            team_list.append((tid, name))
    return team_list

@st.cache_data
def get_team_stats(team_id):
    url = f"https://site.api.espn.com/apis/site/v2/sports/football/nfl/teams/{team_id}/statistics"
    resp = requests.get(url)
    if resp.status_code != 200:
        return None
    return resp.json()


teams = get_nfl_teams()

if not teams:
    st.error("Could not load NFL teams.")
    st.stop()

team_names = [name for (_id, name) in teams]

# User Inputs 

team_1 = st.selectbox("Choose your first NFL team:", team_names)
team_2 = st.selectbox("Choose your second NFL team:", team_names)

detail = st.slider("Choose detail level for the breakdown:", 1, 5, 3)

st.write("Click below to generate a custom AI comparison.")

# Generate Analysis

if st.button("Generate Team Comparison"):
    try:
        with st.spinner("Fetching stats and generating analysis..."):
            
            id_1 = [tid for (tid, name) in teams if name == team_1][0]
            id_2 = [tid for (tid, name) in teams if name == team_2][0]

            stats_1 = get_team_stats(id_1)
            stats_2 = get_team_stats(id_2)

            prompt = f"""
You are an NFL analyst. Use the real team statistics provided below.

Team 1: {team_1}
Stats: {stats_1}

Team 2: {team_2}
Stats: {stats_2}

Write a breakdown in a natural, conversational tone.
Detail level: {detail}/5.

Include:
- Offensive strengths
- Defensive strengths
- Key weaknesses
- Playstyle tendencies (run-heavy, pass-heavy, aggressive, conservative)
- A simple head-to-head prediction
"""

            model = genai.GenerativeModel("gemini-pro")
            response = model.generate_content(prompt)

            st.subheader(f"{team_1} vs {team_2}: AI-Generated Breakdown")
            st.write(response.text)

    except Exception as e:
        st.error(f"Error generating analysis: {e}")
