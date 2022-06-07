from dash import html, dash_table
import plotly.graph_objects as go

def as_data_table_or_message(df, message):
    return as_datatable(df) if df.shape[0] > 0 else message

def as_datatable(df):
    style_table = {'overflowX': 'auto'}
    style_cell = {
        'minWidth': '50px', 'width': '150px', 'maxWidth': '18   0px',
        'overflow': 'hidden',
        'textOverflow': 'ellipsis',
        'padding': '10px'
    }

    return [html.Div([dash_table.DataTable(
        df.to_dict('records'), [{"name": i, "id": i} for i in df.columns],
        style_table=style_table,
        style_cell=style_cell
    )])]

def add_delta_trace(fig, title, value, last_value, row, column):
    fig.add_trace(go.Indicator(
        mode = "number+delta",
        title= {'text': title},
        value = value,
        delta = {'reference': last_value, 'relative': True},
        domain = {'row': row, 'column': column})
    )

def add_trace(fig, title, value, row, column):
    fig.add_trace(go.Indicator(
        mode = "number",
        title= {'text': title},
        value = value,
        domain = {'row': row, 'column': column})
    )