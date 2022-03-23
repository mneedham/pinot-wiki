import pandas as pd
import streamlit as st
from pinotdb import connect
from streamlit_autorefresh import st_autorefresh
from datetime import datetime
import plotly.express as px
from streamlit_tags import st_tags

st.set_page_config(layout="wide")
st.title("Wikipedia Recent Changes")

now = datetime.now()
dt_string = now.strftime("%d %B %Y %H:%M:%S")
st.write(f"Last update: {dt_string}")

conn = connect(host='localhost', port=8099, path='/query/sql', scheme='http')

def overview():
    st.header("Overview")
    st.markdown("""
    <style>
    ul.summary
    {
    display:flex;  
    list-style:none;
    margin: 0;
    padding: 0;
    }

    ul.summary li {
        margin: 0;
        padding-right: 5px;
        width: 150px;
    }

    ul.summary li:first-child {
        padding-right: 20px;
        width: 140px;
    }
    </style>
    """, unsafe_allow_html=True)


    query = """
    select count(*) AS changes, distinctcount(user) AS users, distinctcount(domain) AS domains
    from wikievents 
    where wikievents."timestamp" > cast(ago('PT1M') as long) / 1000
    """

    curs = conn.cursor()
    curs.execute(query)
    df_last_1min = pd.DataFrame(curs, columns=[item[0] for item in curs.description])

    query = """
    select count(*) AS changes, distinctcount(user) AS users, distinctcount(domain) AS domains
    from wikievents 
    where wikievents."timestamp" > cast(ago('PT5M') as long) / 1000
    """

    curs = conn.cursor()
    curs.execute(query)
    df_last_5min = pd.DataFrame(curs, columns=[item[0] for item in curs.description])

    query = """
    select count(*) AS changes, distinctcount(user) AS users, distinctcount(domain) AS domains
    from wikievents 
    where wikievents."timestamp" > cast(ago('PT10M') as long) / 1000
    """

    curs = conn.cursor()
    curs.execute(query)
    df_last_10min = pd.DataFrame(curs, columns=[item[0] for item in curs.description])

    query = """
    select count(*) AS changes, distinctcount(user) AS users, distinctcount(domain) AS domains 
    from wikievents 
    where wikievents."timestamp" > cast(ago('PT1H') as long) / 1000
    """

    curs = conn.cursor()
    curs.execute(query)
    df_last_1hour = pd.DataFrame(curs, columns=[item[0] for item in curs.description])

    query = """
    select count(*) AS changes, distinctcount(user) AS users, distinctcount(domain) AS domains 
    from wikievents 
    """

    curs = conn.cursor()
    curs.execute(query)
    df_all = pd.DataFrame(curs, columns=[item[0] for item in curs.description])

    st.markdown(f"""

    <ul class="summary">
    <li><em>Last 1 min</em></li>
    <li>Changes: <strong>{'{:,}'.format(df_last_1min['changes'].values[0]).ljust(20)}</strong> </li>
    <li>Users: <strong>{df_last_1min['users'].values[0]:,}</strong> </li>
    <li>Domains: <strong>{df_last_1min['domains'].values[0]:,}</strong> </li>
    </ul>

    <ul class="summary">
    <li><em>Last 5 mins</em></li>
    <li>Changes: <strong>{'{:,}'.format(df_last_5min['changes'].values[0]).ljust(20)}</strong> </li>
    <li>Users: <strong>{df_last_5min['users'].values[0]:,}</strong> </li>
    <li>Domains: <strong>{df_last_5min['domains'].values[0]:,}</strong> </li>
    </ul>

    <ul class="summary">
    <li><em>Last 10 mins</em></li>
    <li>Changes: <strong>{'{:,}'.format(df_last_10min['changes'].values[0]).ljust(20)}</strong> </li>
    <li>Users: <strong>{df_last_10min['users'].values[0]:,}</strong> </li>
    <li>Domains: <strong>{df_last_10min['domains'].values[0]:,}</strong> </li>
    </ul>

    <ul class="summary">
    <li><em>Last 1 hour</em></li>
    <li>Changes: <strong>{'{:,}'.format(df_last_1hour['changes'].values[0]).ljust(20)}</strong> </li>
    <li>Users: <strong>{df_last_1hour['users'].values[0]:,}</strong> </li>
    <li>Domains: <strong>{df_last_1hour['domains'].values[0]:,}</strong> </li>
    </ul>

    <ul class="summary">
    <li><em>All Time</em></li>
    <li>Changes: <strong>{'{:,}'.format(df_all['changes'].values[0]).ljust(20)}</strong> </li>
    <li>Users: <strong>{df_all['users'].values[0]:,}</strong> </li>
    <li>Domains: <strong>{df_all['domains'].values[0]:,}</strong> </li>
    </ul>

    """, unsafe_allow_html=True)

    st.header("Recent Changes")

    query = """
    select "timestamp", user, title, domain
    from wikievents 
    order by wikievents."timestamp" desc
    LIMIT 20
    """

    curs = conn.cursor()
    curs.execute(query)
    df = pd.DataFrame(curs, columns=[item[0] for item in curs.description])
    df['timestamp'] = df['timestamp'].apply(lambda timestamp: datetime.fromtimestamp(timestamp))

    st.table(df)

def whos_making_changes():
    st.header("Who's making changes?")

    query = """
    select bot, count(*) AS changes
    from wikievents 
    group by bot
    """

    curs = conn.cursor()
    curs.execute(query)
    df = pd.DataFrame(curs, columns=[item[0] for item in curs.description])

    fig = px.pie(df, names="bot", values="changes", color_discrete_sequence =['#0b263f', '#ccc'], title="Bots vs Non Bots")
    fig.update_xaxes(categoryorder='category descending')
    fig['layout'].update(margin=dict(l=0,r=0,b=0,t=40))
    st.write(fig)

    query = """
    select user, count(user) AS changes
    from wikievents 
    group by user
    order by changes DESC
    LIMIT 10
    """

    curs = conn.cursor()
    curs.execute(query)
    df = pd.DataFrame(curs, columns=[item[0] for item in curs.description])


    fig = px.bar(df, x="changes", y="user", color_discrete_sequence =['#0b263f']*len(df), title="Top Users")
    fig.update_yaxes(categoryorder='max ascending')
    fig['layout'].update(margin=dict(l=0,r=0,b=0,t=40))
    st.write(fig)

    query = """
    select user, count(user) AS changes
    from wikievents 
    WHERE bot = True
    group by user
    order by changes DESC
    LIMIT 10
    """

    curs = conn.cursor()
    curs.execute(query)
    df = pd.DataFrame(curs, columns=[item[0] for item in curs.description])


    fig = px.bar(df, x="changes", y="user", color_discrete_sequence =['#0b263f']*len(df), title="Top Bots")
    fig.update_yaxes(categoryorder='max ascending')
    fig['layout'].update(margin=dict(l=0,r=0,b=0,t=40))
    st.write(fig)

    query = """
    select user, count(user) AS changes
    from wikievents 
    WHERE bot = False
    group by user
    order by changes DESC
    LIMIT 10
    """

    curs = conn.cursor()
    curs.execute(query)
    df = pd.DataFrame(curs, columns=[item[0] for item in curs.description])


    fig = px.bar(df, x="changes", y="user", color_discrete_sequence =['#0b263f']*len(df), title="Top Non Bots")
    fig.update_yaxes(categoryorder='max ascending')
    fig['layout'].update(margin=dict(l=0,r=0,b=0,t=40))
    st.write(fig)

def what_changes():
    st.header("What changes made?")

    query = """
    select domain, count(user) AS changes
    from wikievents 
    group by domain
    order by changes DESC
    LIMIT 10
    """

    curs = conn.cursor()
    curs.execute(query)
    df = pd.DataFrame(curs, columns=[item[0] for item in curs.description])

    fig = px.bar(df, x="changes", y="domain", color_discrete_sequence =['#0b263f']*len(df), title="By Domain")
    fig.update_yaxes(categoryorder='max ascending')
    fig['layout'].update(margin=dict(l=0,r=0,b=0,t=40))
    st.write(fig)

    query = """
    select type, count(user) AS changes
    from wikievents 
    group by type
    order by changes DESC
    LIMIT 10
    """

    curs = conn.cursor()
    curs.execute(query)
    df = pd.DataFrame(curs, columns=[item[0] for item in curs.description])

    fig = px.bar(df, x="changes", y="type", color_discrete_sequence =['#0b263f']*len(df), title="Types of changes")
    fig.update_yaxes(categoryorder='max ascending')
    fig['layout'].update(margin=dict(l=0,r=0,b=0,t=40))
    st.write(fig)

def drill_down():
    st.header("Drill Down By User")

    curs = conn.cursor()
    curs.execute("""
    select user, count(user) AS changes
    from wikievents 
    group by user
    order by changes DESC
    LIMIT 20
    """)

    df = pd.DataFrame(curs, columns=[item[0] for item in curs.description])

    users = list(df["user"].values)

    def select_user_callback():
        st.session_state['selected_user'] = st.session_state.select_user  

    if 'selected_user' not in st.session_state:
        selected_user = st.selectbox('Select User', users, 
            key='select_user', on_change=select_user_callback
        )
    else:
        selected_user = st.selectbox('Select User', users, 
          users.index(st.session_state.selected_user) if st.session_state.selected_user in users else 0, 
          key='select_user',
          on_change=select_user_callback
        )

    curs = conn.cursor()
    curs.execute("""
    select count(user) AS changes
    from wikievents 
    WHERE user = %(user)s
    """, {"user": selected_user})

    df = pd.DataFrame(curs, columns=[item[0] for item in curs.description])
    st.markdown(f"""
    Changes: **{'{:,}'.format(df['changes'].values[0])}**
    """)

    query = """
    select domain, count(user) AS changes
    from wikievents 
    WHERE user = %(user)s
    group by domain
    order by changes DESC
    LIMIT 10
    """

    curs = conn.cursor()
    curs.execute(query, {"user": selected_user})
    df = pd.DataFrame(curs, columns=[item[0] for item in curs.description])

    fig = px.bar(df, x="changes", y="domain", color_discrete_sequence =['#0b263f']*len(df), title="By Domain")
    fig.update_yaxes(categoryorder='max ascending')
    fig['layout'].update(margin=dict(l=0,r=0,b=0,t=40))
    st.write(fig)

    query = """
    select type, count(user) AS changes
    from wikievents 
    WHERE user = %(user)s
    group by type
    order by changes DESC
    LIMIT 10
    """

    curs = conn.cursor()
    curs.execute(query, {"user": selected_user})
    df = pd.DataFrame(curs, columns=[item[0] for item in curs.description])

    fig = px.bar(df, x="changes", y="type", color_discrete_sequence =['#0b263f']*len(df), title="Types of changes")
    fig.update_yaxes(categoryorder='max ascending')
    fig['layout'].update(margin=dict(l=0,r=0,b=0,t=40))
    st.write(fig)

PAGES = {
    "Overview": overview,
    "Who's making changes?": whos_making_changes,
    "Where changes were made?": what_changes,
    "Drill Down By User": drill_down
}

st.sidebar.title('Navigation')

agree = st.sidebar.checkbox('Auto Refresh?', True)

if agree:
     st_autorefresh(interval=5000, key="fizzbuzzcounter")


selection = st.sidebar.radio("Go to", list(PAGES.keys()))
page = PAGES[selection]
page()
