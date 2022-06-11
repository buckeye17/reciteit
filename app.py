# core Python packages
import string

# third party Python packages
import dash
from dash import html
from dash import dcc
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from dash.dependencies import Input, Output, State, MATCH, ALL

# Create app
FONT_AWESOME = "https://use.fontawesome.com/releases/v6.0.0/css/all.css"
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.CYBORG, FONT_AWESOME],
    title="Recite It!",
    meta_tags=[{
        "name": "viewport",
        "content": "width=device-width, initial-scale=1"
    }]
)
server = app.server

# Define Layout
app.layout = dbc.Container(
    fluid=True,
    children=[

        # store user input from Break Down tab
        dcc.Store(id='memory-output'),

        dbc.NavbarSimple(
            children=[
                dbc.NavItem(dbc.NavLink(
                    html.Div(
                        className="fa-brands fa-github",
                        title="Github",
                        style={"fontSize": 30}
                    ),
                    href="https://github.com/buckeye17/reciteit"
                )),
            ],
            brand="Recite It!",
            brand_href="#",
            color="dark",
            dark=True,
        ),

        dbc.Tabs([

            # Input tab
            dbc.Tab(
                [
                    dbc.Container(dbc.Row([
                        dbc.Col([
                            dbc.Textarea(
                                value="",
                                placeholder="Type or paste text here",
                                id="input_text",
                                autofocus=True,
                                style={"margin-top": "15px", "height": "65vh"},
                            ),
                        ]),
                    ])),
                ],
                id="input_tab",
                tab_id="input_tab",
                label="1. Input Text",
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
                label="2. Break It Down",
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
                label="3. Study It",
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
                        ), width="auto"),
                        dbc.Col(dbc.Switch(
                            id="punctuation-switch",
                            label="Check punctuation",
                            value=False,
                        ), width="auto"),
                        dbc.Col(dbc.Button(
                            "Clear",
                            color="dark",
                            id="test-clear",
                        ), width="auto"),
                    ],
                    justify="start",
                    style={"margin-bottom": 15}),
                    html.Div(
                        dmc.Container(
                            [],
                            id="test_container",
                            fluid=True,
                        ),
                        className="p-3 bg-light rounded-3",
                    ),
                ],
                id="test_tab",
                tab_id="test_tab",
                label="4. Recite It",
                disabled=True
            ),
        ],
        id="tabs",
        active_tab="input_tab",
        style={"margin-bottom": "15px"}),
    ],
)


@app.callback(
    [Output("input_text", "value"),
     Output("setup_tab", "disabled"),
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
        unit_ls = get_unit_breaks(txt, data_store)
        if unit_ls[break_click_ls.index(1)] in data_store:
            # break click corresponds to a prior Break Down event, not a newline character 
            data_store.pop(break_click_ls.index(1))
            data_store.sort()

        else:
            # break click corresponds to a newline character, not a prior Break Down event
            # find the ith line break in txt
            occurrence = unit_ls[break_click_ls.index(1)]
            ind = -1
            for i in range(0, occurrence):
                space_ind = txt.find(" ", ind + 1)
                if not space_ind:
                    space_ind = len(txt)

                nl_ind = txt.find("\n", ind + 1)
                if not nl_ind:
                    nl_ind = len(txt)
                ind = min(space_ind, nl_ind)

            txt = txt[:ind] + txt[ind + 1:]

    txt_out = txt
    unit_ls = get_unit_breaks(txt_out, data_store)
    
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
                    size="sm",
                    id={"index": i, "type": "break"},
                    style={"margin": 0, "padding": 0}
                ), className="d-grid gap-2"))
                

            word_html_ls.append(dbc.Button(
                word,
                color="light",
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
                    dbc.Col(f"Unit {len(study_html_ls) + 1}", width="auto"),
                    dbc.Col(html.P(unit_str))
                ], align="center")
            )
            unit_start = unit_end

            # test inputs
            test_element_id = {"index": i, "type": "test"}
            test_html_ls.append(
                dbc.Row([
                    dbc.Col([
                        html.Span(f"Unit {len(test_html_ls) + 1}"),
                        html.Span(id={"index": i, "type": "test_icon"}),
                    ], width="auto"),
                    dbc.Col(dmc.Textarea(
                        id=test_element_id,
                        minRows=1,
                        autosize=True,
                        style={"margin": 10},
                    )),
                ], align="center", className="g-0") # zero gutter between columns
            )

            # create client callback for expanding text area as line wrapping occurs
            dash.clientside_callback(
                """function(id, value) {
                    document.getElementById(id).parentNode.dataset.value = value
                    return window.dash_clientside.no_update
                }""",
                Output(test_element_id, "className"),
                [Input(test_element_id, "id"), Input(test_element_id, "value")]
            )

        # add the last unit for study & test tabs
        i = len(unit_ls)
        test_element_id = {"index": i, "type": "test"}
        unit_str = " ".join(words_ls[unit_start:])
        study_html_ls.append(
            dbc.Row([
                dbc.Col(f"Unit {len(study_html_ls) + 1}", width="auto"),
                dbc.Col(html.P(unit_str))
            ], align="center")
        )

        test_html_ls.append(
            dbc.Row([
                dbc.Col([
                    html.Span(f"Unit {len(test_html_ls) + 1}"),
                    html.Span(id={"index": i, "type": "test_icon"}),
                ], width="auto"),
                dbc.Col(dmc.Textarea(
                    id=test_element_id,
                    minRows=1,
                    autosize=True,
                    style={"margin": 10},
                )),
            ], align="center", className="g-0") # zero gutter between columns
        )

    return txt_out, setup_disabled, study_disabled, test_disabled, word_html_ls, study_html_ls, test_html_ls, data_store

@app.callback(
    [Output({"index": MATCH, "type": "test"}, "value"),
     Output({"index": MATCH, "type": "test"}, "valid"),
     Output({"index": MATCH, "type": "test"}, "invalid"),
     Output({"index": MATCH, "type": "test_icon"}, "children")],
    [Input({"index": MATCH, "type": "test"}, "value"),
     Input("capitalization-switch", "value"),
     Input("punctuation-switch", "value"),
     Input("test-clear", "n_clicks")],
    [State({"index": MATCH, "type": "test"}, "id"),
     State("input_text", "value"),
     State('memory-output', 'data')]
)
def test_checking(test_txt, check_capitalization, check_punctuation, clear_clicks, test_id, txt, data_store):

    ctx = dash.callback_context
    trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]
    if trigger_id == "test-clear":
        return ["", None, None, None]

    unit_ls = get_unit_breaks(txt, data_store)

    # treat new lines like a space
    txt = txt.replace("\n", " ")

    # format text according to desired checking
    test_txt_out = test_txt
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
            unit_start = unit_ls[test_id["index"] - 1]
        
        # determine unit end character index
        if test_id["index"] == len(unit_ls):
            unit_end = len(word_ls)
        else:
            unit_end = unit_ls[test_id["index"]]
        
        unit_txt = " ".join(word_ls[unit_start:unit_end])
        n_char = len(test_txt)

        icon_style = {
            "fontSize": 20,
            "margin-left": 20,
        }
        
        # grade input
        # valid & invalid textarea properties could be used, but emojis seemed 
        # more informative for: exact match, incomplete match, error feedback
        # emojis are documented here: https://fontawesome.com/search?q=emojis&m=free&s=solid%2Cbrands
        if test_txt == unit_txt:
            icon_style["color"] = "Yellow"
            # icon = html.Div(className="fa-solid fa-face-smile", title="Perfect!", style=icon_style)
            icon = html.Div(className="fa-solid fa-star", title="Perfect!", style=icon_style)
            return [test_txt_out, None, None, icon]

        elif unit_txt[:n_char] == test_txt:
            icon_style["color"] = "White"
            # icon = html.Div(className="fa-solid fa-face-meh", title="So far so good", style=icon_style)
            icon = html.Div(className="fa-solid fa-star-half-stroke", title="So far so good", style=icon_style)
            return [test_txt_out, None, None, icon]

        else:
            icon_style["color"] = "Red"
            # icon = html.Div(className="fa-solid fa-face-sad-tear", title="Doh, you made a mistake", style=icon_style)
            icon = html.Div(className="fa-solid fa-hand", title="Doh, you made a mistake", style=icon_style)
            return [test_txt_out, None, None, icon]
        
    else:
        return ["", None, None, None]

def get_unit_breaks(txt, data_store):
    # capture newline characters as if the user wants to start new units
    # these newline characters are not kpt in data store, 
    # they are just read where they are from the text
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
    
    return unit_ls

if __name__ == "__main__":
    app.run_server(host="0.0.0.0", debug=False)