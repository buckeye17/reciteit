from dash import Dash, html, dcc, clientside_callback, Output, Input


app = Dash(__name__)
app.layout = html.Div(
    [
        html.Label(
            [
                html.Span("Name: "),
                dcc.Input(id="name_input", size="4", placeholder="John")
            ],
            className="input-sizer",
        ),
        html.Label(
            [
                html.Span("Text: "),
                dcc.Textarea(rows=1, id="text_input", placeholder="Hello World!")
            ],
            className="input-sizer stacked",
        ),
    ],
    style={"display": "flex", "flexDirection": "column", "alignItems": "start"}
)


for element_id in ["name_input", "text_input"]:
    clientside_callback(
        """function(id, value) {
            document.getElementById(id).parentNode.dataset.value = value
            return window.dash_clientside.no_update
        }""",
        Output(element_id, "className"),
        [Input(element_id, "id"), Input(element_id, "value")]
    )


if __name__ == "__main__":
    app.run_server(debug=True)