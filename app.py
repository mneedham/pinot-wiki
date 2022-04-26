import pandas as pd
import streamlit as st
from pinotdb import connect
from streamlit_autorefresh import st_autorefresh
from datetime import datetime
import plotly.express as px
from streamlit_tags import st_tags
import time

st.set_page_config(layout="wide")

conn = connect(host='localhost', port=8099, path='/query/sql', scheme='http')

def overview():
    st.header("Overview")
    query = """
    select count(*) FILTER(WHERE  ts > ago('PT1M')) AS events1Min,
           count(*) FILTER(WHERE  ts <= ago('PT1M') AND ts > ago('PT2M')) AS events1Min2Min,
           distinctcount(user) FILTER(WHERE  ts > ago('PT1M')) AS users1Min,
           distinctcount(user) FILTER(WHERE  ts <= ago('PT1M') AND ts > ago('PT2M')) AS users1Min2Min,
           distinctcount(domain) FILTER(WHERE  ts > ago('PT1M')) AS domains1Min,
           distinctcount(domain) FILTER(WHERE  ts <= ago('PT1M') AND ts > ago('PT2M')) AS domains1Min2Min
    from wikievents 
    where ts > ago('PT2M')
    limit 1
    """

    curs = conn.cursor()
    curs.execute(query)
    df_summary = pd.DataFrame(curs, columns=[item[0] for item in curs.description])


    metric1, metric2, metric3 = st.columns(3)

    metric1.metric(
        label="Changes",
        value=df_summary['events1Min'].values[0],
        delta=float(df_summary['events1Min'].values[0] - df_summary['events1Min2Min'].values[0])
    )

    metric2.metric(
        label="Users",
        value=df_summary['users1Min'].values[0],
        delta=float(df_summary['users1Min'].values[0] - df_summary['users1Min2Min'].values[0])
    )

    metric3.metric(
        label="Domains",
        value=df_summary['domains1Min'].values[0],
        delta=float(df_summary['domains1Min'].values[0] - df_summary['domains1Min2Min'].values[0])
    )

    query = """
    select ToDateTime(DATETRUNC('minute', ts), 'yyyy-MM-dd hh:mm:ss') AS dateMin, count(*)
    from wikievents 
	group by dateMin
	order by dateMin desc
	LIMIT 30
    """

    curs = conn.cursor()
    curs.execute(query)
    df_ts = pd.DataFrame(curs, columns=[item[0] for item in curs.description])

    fig = px.line(df_ts, x='dateMin', y="count(*)", color_discrete_sequence =['#0b263f'])
    fig['layout'].update(margin=dict(l=0,r=0,b=0,t=40), title="Changes per minute")
    fig.update_yaxes(range=[0, df_ts["count(*)"].max() * 1.1])
    st.plotly_chart(fig, use_container_width=True)


    st.header("Recent Changes")

    query = """
    select ts, user, title, domain
    from wikievents 
    order by ts desc
    LIMIT 20
    """

    curs = conn.cursor()
    curs.execute(query)
    df = pd.DataFrame(curs, columns=[item[0] for item in curs.description])

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
    LIMIT 30
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

st.sidebar.title('Wikipedia Recent Changes')

now = datetime.now()
dt_string = now.strftime("%d %B %Y %H:%M:%S")
st.sidebar.write(f"Last update: {dt_string}")

if not "sleep_time" in st.session_state:
    st.session_state.sleep_time = 2

if not "auto_refresh" in st.session_state:
    st.session_state.auto_refresh = True

auto_refresh = st.sidebar.checkbox('Auto Refresh?', st.session_state.auto_refresh)

if auto_refresh:
    number = st.sidebar.number_input('Refresh rate in seconds', value=st.session_state.sleep_time)
    st.session_state.sleep_time = number


selection = st.sidebar.radio("Go to", list(PAGES.keys()))
page = PAGES[selection]
page()
st.markdown("""
<style>
section.main[tabindex='0'] div[data-testid='stVerticalBlock'] div.element-container:nth-child(1):has(> iframe) {
    display: none;
}

</style>
""", unsafe_allow_html=True)

if auto_refresh:
    time.sleep(number)
    st.experimental_rerun()