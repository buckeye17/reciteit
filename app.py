# core Python packages
import string

# third party Python packages
import dash
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State, MATCH, ALL

app = dash.Dash(__name__)
server = app.server

# Create app
FONT_AWESOME = "https://use.fontawesome.com/releases/v6.0.0/css/all.css"
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.CYBORG, FONT_AWESOME])
server = app.server

# Define Layout
app.layout = dbc.Container(
    fluid=True,
    children=[

        # store user input from Break Down tab
        dcc.Store(id='memory-output'),

        dbc.NavbarSimple(
            children=[
                dbc.NavItem(dbc.NavLink("Github", href="https://github.com/buckeye17/reciteit")),
            ],
            brand="Recite It!",
            brand_href="#",
            color="dark",
            dark=True,
        ),

        dbc.Tabs([

            # # Tips tab
            # dbc.Tab(
            #     html.Div(
            #         dbc.Container(
            #             [
            #                 html.P(
            #                     "Study the text until you're ready to type it",
            #                     className="lead",
            #                 ),
            #                 html.Hr(className="my-2"),
            #                 html.P(""),
            #             ],
            #             fluid=True,
            #             className="py-3",
            #         ),
            #         className="p-3 bg-light rounded-3",
            #     ),
            #     id="tips_tab",
            #     tab_id="tips_tab",
            #     label="Tips"
            # ),

            # Input tab
            dbc.Tab(
                [
                    dbc.Row([
                        dbc.Col([
                            dbc.Textarea(
                                value="",
                                placeholder="Type or paste text here",
                                id="input_text",
                                autofocus=True,
                                style={"margin-top": "15px", "height": "65vh"},
                            ),
                        ]),
                    ]),
                ],
                id="input_tab",
                tab_id="input_tab",
                label="Input",
            ),

            # Break Down tab
            dbc.Tab(
                html.Div(
                    dbc.Container(
                        [
                            html.P(
                                "Break the text into units that will be easy to memorize by clicking on the word where a new unit will start.",
                                className="lead",
                            ),
                            html.Hr(className="my-2"),
                            html.P("", id="setup_txt_container"),
                        ],
                        fluid=True,
                        className="py-3",
                    ),
                    className="p-3 bg-light rounded-3",
                ),
                id="setup_tab",
                tab_id="setup_tab",
                label="Break Down",
                disabled=True
            ),

            # Study tab
            dbc.Tab(
                html.Div(
                    dbc.Container(
                        [
                            html.P(
                                "Study the text until you're ready to type it",
                                className="lead",
                            ),
                            html.Hr(className="my-2"),
                            html.P("", id="study_txt_container"),
                        ],
                        fluid=True,
                        className="py-3",
                    ),
                    className="p-3 bg-light rounded-3",
                ),
                id="study_tab",
                tab_id="study_tab",
                label="Study",
                disabled=True
            ),

            # Test tab
            dbc.Tab(
                [
                    dbc.Row([
                        dbc.Col(dbc.Switch(
                            id="capitalization-switch",
                            label="Check capitalization",
                            value=False,
                        ), width=3),
                        dbc.Col(dbc.Switch(
                            id="punctuation-switch",
                            label="Check punctuation",
                            value=False,
                        ), width=3),
                    ], justify="start"),
                    html.Div(
                        dbc.Container(
                            [],
                            id="test_container",
                            fluid=True,
                            className="py-3",
                        ),
                        className="p-3 bg-light rounded-3",
                    ),
                ],
                id="test_tab",
                tab_id="test_tab",
                label="Test",
                disabled=True
            ),
        ],
        id="tabs",
        active_tab="input_tab",
        style={"margin-bottom": "15px"}),
    ],
)


@app.callback(
    [Output("setup_tab", "disabled"),
     Output("study_tab", "disabled"),
     Output("test_tab", "disabled"),
     Output("setup_txt_container", "children"),
     Output("study_txt_container", "children"),
     Output("test_container", "children"),
     Output('memory-output', 'data')],
    [Input({"index": ALL, "type": "word"}, "n_clicks"),
     Input({"index": ALL, "type": "break"}, "n_clicks"),
     Input("input_text", "value")],
    [State('memory-output', 'data')]
)
def input_submission(word_click_ls, break_click_ls, txt, data_store):

    if txt:
        setup_disabled, study_disabled, test_disabled = False, False, False
    else:
        setup_disabled, study_disabled, test_disabled = True, True, True

    if data_store is None:
        data_store = []

    # if a word has been clicked, update the layout of the words
    if word_click_ls.count(1):
        data_store.append(word_click_ls.index(1))
        data_store.sort()
    
    # if an "X" has been clicked, update the layout of the words
    if break_click_ls.count(1):
        data_store.pop(break_click_ls.index(1))
        data_store.sort()

    # capture newline characters as if the user wants to start new units
    # do not put these newline characters in data store, 
    # just read where they are from the text
    newline_ls = txt.split("\n")
    unit_ls = data_store.copy()
    if len(newline_ls) > 1:
        word_ind = 0
        for line in newline_ls[:-1]:
            line_word_ls = line.split(" ")
            word_ind += len(line_word_ls)

            if word_ind not in data_store:
                unit_ls.append(word_ind)
                unit_ls.sort()
    
    # now treat newline characters like a space
    txt = txt.replace("\n", " ")

    # build the words shown in the break down tab
    word_html_ls = []
    study_html_ls = []
    test_html_ls = []
    if txt:
        words_ls = txt.split(" ")
        for i, word in enumerate(words_ls):
            if i in unit_ls:
                
                # add an "X" to prepare for a new unit
                word_html_ls.append(html.Div(dbc.Button(
                    "X",
                    color="dark",
                    # outline=True,
                    size="sm",
                    id={"index": i, "type": "break"},
                    style={"margin": 0, "padding": 0}
                ), className="d-grid gap-2"))
                

            word_html_ls.append(dbc.Button(
                word,
                color="light",
                # outline=True,
                id={"index": i, "type": "word"},
                style={"margin": 5, "padding": 2}
            ))
    
        # build the text for the study & test tabs
        unit_start = 0
        for i, unit_end in enumerate(unit_ls):

            # study text
            unit_str = " ".join(words_ls[unit_start:unit_end])
            study_html_ls.append(
                dbc.Row([
                    dbc.Col(f"Unit {len(study_html_ls) + 1}", width=1),
                    dbc.Col(html.P(unit_str))
                ], align="center")
            )
            unit_start = unit_end

            # test inputs
            test_html_ls.append(
                dbc.Row([
                    dbc.Col([
                        html.Span(f"Unit {len(test_html_ls) + 1}"),
                        html.Span(id={"index": i, "type": "test_icon"}),
                    ], width=1),
                    dbc.Col(dbc.Textarea(id={"index": i, "type": "test"}, rows=1, style={"margin": 10})),
                ], align="center", className="g-0") # zero gutter between columns
            )

        # add the last unit for study & test tabs
        i = len(unit_ls)
        unit_str = " ".join(words_ls[unit_start:])
        study_html_ls.append(
            dbc.Row([
                dbc.Col(f"Unit {len(study_html_ls) + 1}", width=1),
                dbc.Col(html.P(unit_str))
            ], align="center")
        )

        test_html_ls.append(
            dbc.Row([
                dbc.Col([
                    html.Span(f"Unit {len(test_html_ls) + 1}"),
                    html.Span(id={"index": i, "type": "test_icon"}),
                ], width=1),
                dbc.Col(dbc.Textarea(id={"index": i, "type": "test"}, rows=1, style={"margin": 10})),
            ], align="center", className="g-0") # zero gutter between columns
        )

    return setup_disabled, study_disabled, test_disabled, word_html_ls, study_html_ls, test_html_ls, data_store

@app.callback(
    [Output({"index": MATCH, "type": "test"}, "valid"),
     Output({"index": MATCH, "type": "test"}, "invalid"),
     Output({"index": MATCH, "type": "test_icon"}, "children")],
    [Input({"index": MATCH, "type": "test"}, "value"),
     Input("capitalization-switch", "value"),
     Input("punctuation-switch", "value")],
    [State({"index": MATCH, "type": "test"}, "id"),
     State("input_text", "value"),
     State('memory-output', 'data')]
)
def test_checking(test_txt, check_capitalization, check_punctuation, test_id, txt, data_store):

    # treat new lines like a space
    txt = txt.replace("\n", " ")

    # format text according to desired checking
    if not check_capitalization:
        if txt:
            txt = txt.lower()
        
        if test_txt:
            test_txt = test_txt.lower()
    
    if not check_punctuation:
        if txt:
            txt = txt.translate(str.maketrans('', '', string.punctuation))
        
        if test_txt:
            test_txt = test_txt.translate(str.maketrans('', '', string.punctuation))

    if test_txt:
        word_ls = txt.split(" ")

        # determine unit start character index
        if test_id["index"] == 0:
            unit_start = 0
        else:
            unit_start = data_store[test_id["index"] - 1]
        
        # determine unit end character index
        if test_id["index"] == len(data_store):
            unit_end = len(word_ls)
        else:
            unit_end = data_store[test_id["index"]]
        
        unit_txt = " ".join(word_ls[unit_start:unit_end])
        n_char = len(test_txt)

        icon_style = {
            "fontSize": 30,
            "margin-left": 20,
        }
        
        # grade input
        # valid & invalid textarea properties could be used, but emojis seemed 
        # more informative for: exact match, incomplete match, error feedback
        # emojis are documented here: https://fontawesome.com/search?q=emojis&m=free&s=solid%2Cbrands
        if test_txt == unit_txt:
            icon_style["color"] = "Green"
            icon = html.Div(className="fa-solid fa-face-smile", title="Perfect!", style=icon_style)
            return [None, None, icon]

        elif unit_txt[:n_char] == test_txt:
            icon_style["color"] = "Orange"
            icon = html.Div(className="fa-solid fa-face-meh", title="So far so good", style=icon_style)
            return [None, None, icon]

        else:
            icon_style["color"] = "Red"
            icon = html.Div(className="fa-solid fa-face-sad-tear", title="Doh, you made a mistake", style=icon_style)
            return [None, None, icon]
        
    else:
        return [None, None, None]

if __name__ == "__main__":
    app.run_server(host="0.0.0.0", debug=False)