import sys
sys.path.append('.')

import dash
import dash_table
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
from dash.dependencies import Output, Input, State
from datetime import date, datetime
import pandas as pd
import sqlite3
from sqlalchemy.orm import sessionmaker
from sqlalchemy import and_, func

from css_style import SIDEBAR_STYLE, CONTENT_STYLE, DROPDOWN_STYLE
from model.model import db_connect, create_table, TJob, TJobAnalysis, TCompany, TDashboard
from config.config import DB_PATH, DB_CONNECTION_STRING


LOGO_PATH = 'https://i.pinimg.com/originals/5b/90/ec/5b90ece9ecee96fa8c6a59547d43dc60.gif'


class DashDataProcessor:

    def __init__(self, **kwarg):
        # database connection
        self.db_connect()


    def db_connect(self):
        engine = db_connect(DB_CONNECTION_STRING)
        create_table(engine)
        self.Session = sessionmaker(bind=engine)


def get_job_count_graph_data(company_ids=[], start_date=None, end_date=None):
    session = data_processor.Session()
    data = []
    try:
        '''
        select represent_date, sum(apply_count), sum(need_count)
        from t_dashboard
        group by represent_date
        '''
        query = session.query(
                    TDashboard.represent_date,
                    func.sum(TDashboard.apply_count).label('APPLY_COUNT'),
                    func.sum(TDashboard.need_count).label('NEED_COUNT'),
                ).group_by(
                    TDashboard.represent_date
                ).order_by(
                    TDashboard.represent_date.asc()
                )
        result_df = pd.read_sql(query.statement, session.bind)

        represent_date = [convert_int_to_date(x) for x in result_df['REPRESENT_DATE']]
        apply_count = result_df['APPLY_COUNT'].tolist()
        need_count = result_df['NEED_COUNT'].tolist()
        data = [{
            'name': 'APPLY_COUNT',
            'x': represent_date,
            'y': apply_count,
        }, {
            'name': 'NEED_COUNT',
            'x': represent_date,
            'y': need_count,
        }]

    except Exception as e:
        print(e)

    finally:
        session.close()
        return data

data_processor = DashDataProcessor()

def convert_int_to_date(date_int):
    ''' From 20210719 to datetime.datetime(2021, 7, 19, 0, 0)
    '''
    year = int(date_int / 10000)
    month = int(date_int / 100) % 100
    day = int(date_int) % 100
    return datetime(year=year, month=month, day=day)


def generate_dropdown_list(options, values=[]):
    ''' dropdown_list = [
            {'label': 'one', 'value': 0},
            {'label': 'two', 'value': 1}
        ]'''
    dropdown_list = []
    if len(values):
        for value, option in zip(values, options):
            dropdown_list.append({'label': option, 'value': value})
        return dropdown_list

    for option in options:
        dropdown_list.append({'label': option, 'value': option})
    return dropdown_list


def get_company_dropdown_options():
    with sqlite3.connect(DB_PATH) as con:
        query = "SELECT DISTINCT COMPANY_NAME, COMPANY_ID FROM T_JOB"
        df = pd.read_sql(query, con=con)
    return generate_dropdown_list(df['COMPANY_NAME'].tolist(), df['COMPANY_ID'].tolist())

def get_job_category_dropdown_options():
    options = [
        {'label': 'Data Analysis', 'value': 1},
        {'label': 'Programmer', 'value': 2}
    ]
    return options


NAVBAR_HTML = dbc.Navbar(
    children=[
        html.A(
            # Use row and col to control vertical alignment of logo / brand
            dbc.Row(
                [
                    dbc.Col(html.Img(src=LOGO_PATH, height="30px")),
                    dbc.Col(
                        dbc.NavbarBrand("HR Bank Dashboard", className="ml-2")
                    ),
                ],
                align="center",
                no_gutters=True,
            ),
            href="#",
        )
    ],
    color="black",
    dark=True,
    sticky="top",
)

SELECT_PANEL_CARD = dbc.Card([
    dbc.CardHeader(html.H4('Select what you want')),
    dbc.CardBody([
        # Company
        html.Label("Comapny", className="lead"),
        dcc.Dropdown(
            id="company-dropdown-id", clearable=True, style=DROPDOWN_STYLE, multi=True,
            options=get_company_dropdown_options(),
        ),

        # Job Category
        html.Label("Job Category", className="lead"),
        dcc.Dropdown(
            id="job-category-dropdown-id", clearable=True, style=DROPDOWN_STYLE, multi=True,
            options=get_job_category_dropdown_options(),
        ),

        # Date
        html.Label("Date Range", className="lead"),
        dcc.DatePickerRange(
            id='date-picker-range-id',
            min_date_allowed=date(2020, 1, 1),
            max_date_allowed=date(2021, 12, 31),
            initial_visible_month=date(2021, 8, 1),
            end_date=date(2021, 10, 6),
            style=DROPDOWN_STYLE
        ),

        # Salary
        html.Label("Salary", className="lead"),
        html.Div(
            dcc.RangeSlider(
                min=0,
                max=5,
                step=1,
                marks={
                    0: '0',
                    1: '22k',
                    2: '35k',
                    3: '45k',
                    4: '60k',
                    5: '60k up'
                },
                value=[0, 5],
                id="salary-slider-id",
            ),
            style=DROPDOWN_STYLE,
        ),

        # Button
        dbc.Button("Go", id="submit-btn-id", color="primary", n_clicks=0, block=True),
    ])
])

PLOT_CARD = dbc.Card([
    # dbc.CardHeader(html.H5('Plots')),
    dcc.Tabs(
        children=[
            dcc.Tab(
                label='Job Count',
                children=[
                    dcc.Loading(
                        id="plot1",
                        children=[dcc.Graph(id="job-count-graph-id")],
                        type="default",
                    )
                ]
            ),
            dcc.Tab(
                label='Plot Two',
                children=[
                    dcc.Loading(
                        id="plot2",
                        children=[dcc.Graph(id="plot2_graph")],
                        type="default",
                    )
                ]
            )
        ]
    )
])

PLOT_HTML = dbc.Container(
    [
        dbc.Row([
            dbc.Col(SELECT_PANEL_CARD, width=4),
            dbc.Col(PLOT_CARD, width=8)
        ])
    ],
)


SIDE_MENU_HTML = html.Div(
    [
        html.H2("One For All", className="display-12"),
        html.Hr(),
        html.P(
            "A simple sidebar layout with navigation links", className="lead"
        ),
        dbc.Nav(
            [
                dbc.NavLink("Home", href="/", active="exact"),
                dbc.NavLink("Plot Plot", href="/plot", active="exact"),
                dbc.NavLink("Page 2", href="/page-2", active="exact"),
            ],
            vertical=True,
            pills=True,
        ),
    ],
    style=SIDEBAR_STYLE,
)


CONTENT_HTML = html.Div(id="page-content", style=CONTENT_STYLE)


app = dash.Dash(__name__, suppress_callback_exceptions=True, external_stylesheets=[dbc.themes.BOOTSTRAP])
# server = app.server  # for Heroku deployment

# app.layout = html.Div(children=[NAVBAR, BODY])
app.layout = html.Div([dcc.Location(id="url"), SIDE_MENU_HTML, CONTENT_HTML])


# Change Page Content
@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def render_page_content(pathname):
    if pathname == "/":
        return html.P("This is the content of the home page!")
    elif pathname == "/plot":
        return [PLOT_HTML]# html.P("This is the content of page 1. Yay!")
    elif pathname == "/page-2":
        return html.P("Oh cool, this is page 2!")
    # If the user tries to reach a different page, return a 404 message
    return dbc.Jumbotron(
        [
            html.H1("404: Not found", className="text-danger"),
            html.Hr(),
            html.P(f"The pathname {pathname} was not recognised..."),
        ]
    )


# Graph
@app.callback(
    Output('job-count-graph-id', 'figure'),
    [Input('submit-btn-id', 'n_clicks'),],
    [
     State('date-picker-range-id', 'start_date'),
     State('date-picker-range-id', 'end_date'),
     State('company-dropdown-id', 'value'),
     State('job-category-dropdown-id', 'value'),
     State('salary-slider-id', 'value'),
    ])
def update_job_count_graph(n_clicks, start_date, end_date, company_dropdown_value, job_category_dropdown_value, salary_slider_value):
    print(f'start date: {start_date}')
    print(f'end date: {end_date}')
    print(f'company: {company_dropdown_value}')
    print(f'job category: {job_category_dropdown_value}')
    print(f'salary: {salary_slider_value}')
    data = get_job_count_graph_data(company_dropdown_value, start_date, end_date)
    fig = {
        'data': data,
        'layout': {
            'xaxis': {
                'title': 'Date',
                'tickformat': '%Y/%m/%d',
            },
            'yaxis': {
                'title': 'Count',
            },
            'hovermode': 'x unified'
        }
    }
    return fig


if __name__ == "__main__":
    app.run_server(debug=True)