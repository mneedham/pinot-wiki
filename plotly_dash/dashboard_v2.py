import pandas as pd
from dash import Dash, html, dash_table, dcc, Input, Output
import plotly.graph_objects as go
from pinotdb import connect
from dash_utils import add_delta_trace, add_trace
import plotly.express as px
import datetime

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = Dash(__name__, external_stylesheets=external_stylesheets)
app.title = "Wiki Recent Changes Dashboard"

connection = connect(host="localhost", port="8099", path="/query/sql", scheme=( "http"))


@app.callback([
    Output(component_id='indicators', component_property='figure')
  ],[
    Input('interval-component', 'n_intervals')
])
def indicators(n):
    # Find changes that happened in the last 1 minute
    # Find changes that happened between 1 and 2 minutes ago
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

    curs = connection.cursor()
    curs.execute(query)
    df_summary = pd.DataFrame(curs, columns=[item[0] for item in curs.description])
    curs.close()

    fig = go.Figure(layout=go.Layout(height=300))
    if df_summary["events1Min"][0] > 0:
        if df_summary["events1Min"][0] > 0:
            add_delta_trace(fig, "Changes", df_summary["events1Min"][0], df_summary["events1Min2Min"][0], 0, 0)
            add_delta_trace(fig, "Users", df_summary["users1Min"][0], df_summary["users1Min2Min"][0], 0, 1)
            add_delta_trace(fig, "Domain", df_summary["domains1Min"][0], df_summary["domains1Min2Min"][0], 0, 2)
        else:
            add_trace(fig, "Changes", df_summary["events1Min"][0], 0, 0)
            add_trace(fig, "Users", df_summary["users1Min2Min"][0], 0, 1)
            add_trace(fig, "Domains", df_summary["domains1Min2Min"][0], 0, 2)
        fig.update_layout(grid = {"rows": 1, "columns": 3,  'pattern': "independent"},) 
    else:
        fig.update_layout(annotations = [{"text": "No events found", "xref": "paper", "yref": "paper", "showarrow": False, "font": {"size": 28}}])
    return fig,

@app.callback([
    Output(component_id='time-series', component_property='figure')
  ],[
    Input('interval-component', 'n_intervals')
])
def time_series(n):
    query = """
    select ToDateTime(DATETRUNC('minute', ts), 'yyyy-MM-dd hh:mm:ss') AS dateMin, count(*) AS changes, 
        distinctcount(user) AS users,
        distinctcount(domain) AS domains
    from wikievents 
    where ts > ago('PT1H')
    group by dateMin
    order by dateMin desc
    LIMIT 30
    """

    curs = connection.cursor()
    curs.execute(query)
    df_ts = pd.DataFrame(curs, columns=[item[0] for item in curs.description])
    curs.close()

    df_ts_melt = pd.melt(df_ts, id_vars=['dateMin'], value_vars=['changes', 'users', 'domains'])

    line_chart = px.line(df_ts_melt, x='dateMin', y="value", color='variable', color_discrete_sequence =['blue', 'red', 'green'])
    line_chart['layout'].update(margin=dict(l=0,r=0,b=0,t=40), title="Changes/Users/Domains per minute")
    line_chart.update_yaxes(range=[0, df_ts["changes"].max() * 1.1])
    return line_chart,

@app.callback([
    Output(component_id='latest-timestamp', component_property='children')
  ],[
    Input('interval-component', 'n_intervals')
])
def timestamp(n):
    return [html.Span(f"Last updated: {datetime.datetime.now()}")]

app.layout = html.Div([
    html.H1("Wiki Recent Changes Dashboard", style={'text-align': 'center'}),
    html.Div(id='latest-timestamp', style={"padding": "5px 0", "text-align": "center"}),
    dcc.Interval(
            id='interval-component',
            interval=1 * 1000,
            n_intervals=0
        ),
    html.Div(id='content', children=[
        dcc.Graph(id="indicators"),
        dcc.Graph(id="time-series"),
    ])
])

if __name__ == '__main__':
    app.run_server(debug=True)
