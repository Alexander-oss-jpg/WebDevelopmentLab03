import streamlit as st
import requests
import pandas as pd

st.title("NFL Team Stats Viewer")

st.write("This app uses the ESPN NFL API to show basic stats for one team.")

TEAMS_URL = "https://site.api.espn.com/apis/site/v2/sports/football/nfl/teams"
STATS_URL = "https://site.api.espn.com/apis/site/v2/sports/football/nfl/teams/{team_id}/statistics"


@st.cache_data
def get_nfl_teams():
    """Return a list of (id, name) for all NFL teams."""
    resp = requests.get(TEAMS_URL)
    if resp.status_code != 200:
        return []

    data = resp.json()
    teams = data.get("sports", [{}])[0].get("leagues", [{}])[0].get("teams", [])
    team_list = []

    for t in teams:
        team_info = t.get("team", {})
        team_id = team_info.get("id")
        name = team_info.get("displayName")
        if team_id and name:
            team_list.append((team_id, name))

    return team_list


@st.cache_data
def get_team_stats(team_id):
    """Return the raw stats JSON for a single team."""
    url = STATS_URL.format(team_id=team_id)
    resp = requests.get(url)
    if resp.status_code != 200:
        return None
    return resp.json()


teams = get_nfl_teams()

if not teams:
    st.error("Could not load NFL teams.")
    st.stop()

team_names = [name for (_id, name) in teams]
selected_name = st.selectbox("Choose a team:", team_names)

# find id for chosen team
selected_id = None
for tid, name in teams:
    if name == selected_name:
        selected_id = tid
        break

stat_choice = st.selectbox(
    "Choose a stat category:",
    ["Passing", "Rushing", "Receiving"]
)

stats_data = get_team_stats(selected_id)

if stats_data is None:
    st.error("Could not load stats for that team.")
    st.stop()

categories = stats_data.get("splits", {}).get("categories", [])

rows = []

for cat in categories:
    cat_name = cat.get("displayName", "")
    if stat_choice.lower() in cat_name.lower():
        for stat in cat.get("stats", []):
            stat_name = stat.get("displayName", "")
            stat_value = stat.get("displayValue", "0")
            rows.append({"Stat": stat_name, "Value": stat_value})

if not rows:
    st.warning("No stats found for that category.")
    st.stop()

st.subheader(f"{stat_choice} stats for {selected_name}")

df = pd.DataFrame(rows)

st.dataframe(df, use_container_width=True)

# try to make a simple bar chart with numeric values
df_chart = df.copy()
df_chart["Value"] = pd.to_numeric(
    df_chart["Value"].astype(str).str.replace(",", ""),
    errors="coerce"
)
df_chart = df_chart.dropna()

if not df_chart.empty:
    chart_data = df_chart.set_index("Stat")
    st.bar_chart(chart_data)
else:
    st.info("No numeric values available to plot for this category.")
