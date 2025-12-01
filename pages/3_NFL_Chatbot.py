import streamlit as st
import google.generativeai as genai
import requests

# Title of App
st.title("Web Development Lab03")

# Assignment Data 
# TODO: Fill out your team number, section, and team members

st.header("CS 1301")
st.subheader("Team 111, Web Development 03 - Section 1")
st.subheader("Alexander Jaber, Bryce Phan")


# Introduction
# TODO: Write a quick description for all of your pages in this lab below, in the form:
#       1. **Page Name**: Description
#       2. **Page Name**: Description
#       3. **Page Name**: Description
#       4. **Page Name**: Description


# Configure Gemini with secret
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

st.title("NFL Chatbot")
st.write("""
This chatbot can answer questions about NFL teams using real data 
from the ESPN NFL API. Ask anything about offense, defense, key players, 
matchups, or team strengths.
""")

# NFL Data Fetch

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
    if resp.status_code != 200: #IF this deoesnt equal point system, nothing returned
        return None
    return resp.json()


# Load teams
teams = get_nfl_teams()

if not teams:
    st.error("Could not load NFL teams.")
    st.stop()

team_names = [name for (tid, name) in teams]

# User selects ONE team to inform the chatbot
selected_team = st.selectbox("Choose an NFL team to chat about:", team_names)

# get team ID
team_id = [tid for (tid, name) in teams if name == selected_team][0]

team_stats = get_team_stats(team_id)

# Chat History memory for conversation context
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

user_input = st.text_input("Ask a question about this team:")

# Chatbot Response using Gemini
if st.button("Send"):
    if not user_input.strip():
        st.warning("Please enter a question.")
    else:
        try:
            # Build the prompt with real data
            prompt = f"""
You are an NFL analyst chatbot.

Here is the team the user selected:
Team: {selected_team}

Here are the real statistics from ESPN NFL API:
{team_stats}

Here is the conversation history:
{st.session_state.chat_history}

User's question:
{user_input}

Answer naturally. Be clear, helpful, conversational, and use stats when relevant.
"""

            model = genai.GenerativeModel("gemini-pro")
            response = model.generate_content(prompt)

            bot_reply = response.text

            # Save conversation turn
            st.session_state.chat_history.append(("User", user_input))
            st.session_state.chat_history.append(("Bot", bot_reply))

        except Exception as e:
            st.error("The AI is overloaded or rate-limited. Try again.")
            st.session_state.chat_history.append(("Bot", "Sorry, I hit a temporary error. Try again."))


# Display Conversation
st.subheader("Chatbot Conversation")
for speaker, msg in st.session_state.chat_history:
    if speaker == "User":
        st.markdown(f"**You:** {msg}")
    else:
        st.markdown(f"**Bot:** {msg}")
