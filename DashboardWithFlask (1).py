import base64
import io

import dash
from dash.dependencies import Input, Output, State
from dash import dcc, html
import plotly.graph_objects as go
from dash import dash_table
from plotly.subplots import make_subplots
import plotly.express as px
import pandas as pd
import numpy as np

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets, suppress_callback_exceptions=True)
server = app.server

# def layout 
app.layout = html.Div([
    html.H1("HCI연구실 plotly를 사용한 dashboard 만들기 project"),
    dcc.Upload(
        id='upload-data',
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select Files')
        ]),
        style={
            'width': '100%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px'
        },
        # Allow multiple files to be uploaded
        multiple=True
    ),
    
    html.Div(id='output-div'),
    
    html.Div(id='output-div1'),
   
    html.Div(id='output-datatable'),
])
#------------------------------------------------------------------------------------------------------------------
# daf datatable
def parse_contents(contents, filename):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')))
            df['Weight_diff']=df['Weight'].diff()
        elif 'xls' in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded))
            df['Weight_diff']=df['Weight'].diff()
        elif 'xlsx' in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded))
            df['Weight_diff']=df['Weight'].diff()

    except Exception as e:
        print(e)
        return html.Div([
            '파일 형식 혹은 양식을 맞춰주세요'
        ], style={'color':'red'})

    return html.Div([
        html.H5(filename),

        html.Button(id="submit-button", children="Create weight dashboard"), 

        html.Button(id="submit-button1", children="Create ABGA dashboard"), 
        
        html.Hr(), 
        
        dash_table.DataTable( 
            data=df.to_dict('records'),
            columns=[{'name': i, 'id': i} for i in df.columns],
            page_size=15
        ),
        dcc.Store(id='stored-data', data=df.to_dict('records')),
        html.Hr(),  


        # For debugging, display the raw contents provided by the web browser
        html.Div('Raw Content'),
        html.Pre(contents[0:200] + '...', style={
            'whiteSpace': 'pre-wrap',
            'wordBreak': 'break-all'
        })
    ])
    
#------------------------------------------------------------------------------------------------------------------
# datatable
@app.callback(Output('output-datatable', 'children'),
              Input('upload-data', 'contents'),
              State('upload-data', 'filename'))
def update_output(list_of_contents, list_of_names):
    if list_of_contents is not None:
        children = [
            parse_contents(c, n) for c, n in
            zip(list_of_contents, list_of_names)]
        return children

#------------------------------------------------------------------------------------------------------------------
# graph1
@app.callback(Output('output-div', 'children'),
              Input('submit-button','n_clicks'),
              State('stored-data','data'))

def make_graphs(n, data):
    if n is None:
        return dash.no_update
    else:
        data_df = pd.DataFrame(data)
        fig_weight = make_subplots(
            rows=2, cols=2,
            start_cell="top-left",  # 시작 위치를 바꿀 수 있음
            subplot_titles=("weight with trendline", "input(Pie chart)", "weight diff"),
            specs=[[{"type": "xy"}, {"type": "domain"}],
                   [{"colspan": 2}, None]],
        )
        trendline = [0.863375,0.7965625,0.77,0.771875,0.775,0.800625,0.813125,
                    0.8546875,0.8705625,0.890625,0.9090625,0.92375,0.9396875,0.9535625]
        fig_weight.add_trace(go.Scatter(x=data_df['Date'],y=data_df['Weight'][:14], mode='markers+text',text = data_df['Weight'][:14],textposition='top center' ,name='weight'),row=1,col=1)
        fig_weight.add_trace(go.Scatter(x=data_df['Date'],y=np.array(trendline)+0.2, mode='lines', opacity = 0.3,name='trendline'),row=1,col=1)

        pie_data = [data_df['Breastfeeding_oral'][3],data_df['TPN'][3]]
        fig_weight.add_trace(go.Pie(labels=['Breastfeeding_oral','TPN'],values=pie_data),row=1,col=2)

        y_diff = data_df['Weight'].diff()
        y_diff[0] = 0
    
        fig_weight.add_trace(go.Waterfall(x=data_df['Date'],y=y_diff,textposition="outside",text=data_df['Weight']),row=2,col=1)
        fig_weight.update_traces(increasing_marker_color='red', selector=dict(type='waterfall'),row=2,col=1)
        fig_weight.update_traces(decreasing_marker_color='blue', selector=dict(type='waterfall'),row=2,col=1)
        fig_weight.update_layout(width = 2400,height = 1500)

        fig_weight.update_layout(hoverlabel=dict(
            bgcolor="white",
            font_size=30,
            font_family="Rockwell"
        ),font=dict(size = 15))
        return html.Hr(), html.P('weight와 IO성분 dashboard입니다',style={'textAlign': 'center'}),dcc.Graph(figure=fig_weight),html.Hr()

#------------------------------------------------------------------------------------------------------------------
# graph2    
@app.callback(Output('output-div1', 'children'),
              Input('submit-button1','n_clicks'),
              State('stored-data','data'))
def make_graphs(n, data):
    if n is None:
        return dash.no_update
    else:
        data_df = pd.DataFrame(data)
        fig_ABGA = make_subplots(
            rows=2, cols=3,
            start_cell="top-left",  # 시작 위치를 바꿀 수 있음
            subplot_titles=("pH", "HCO3", "TCO2", "Ionized Ca","An.Gap"),
            specs=[[{"type": "xy"}, {"colspan": 2},None],
                   [{"type": "xy"}, {"type": "xy"},{"type": "xy"}]])

        fig_ABGA.add_trace(go.Scatter(x=data_df['Date'],y=data_df['pH'], mode='markers+text',text=data_df['pH'],textposition='top center',name='pH'),row = 1, col=1)
        fig_ABGA.add_hline(y=7.35, line_dash="dot",row = 1, col=1)
        fig_ABGA.add_hline(y=7.45, line_dash="dot",row = 1, col=1)
        fig_ABGA.add_hrect(y0=7.35, y1=7.45, line_width=0, fillcolor="green", opacity=0.2,row = 1, col=1)

        fig_ABGA.add_trace(go.Scatter(x=data_df['Date'],y=data_df['HCO3'], mode='markers+text',text=data_df['HCO3'],textposition='top center',name='HCO3'),row = 1, col=2)
        fig_ABGA.add_hline(y=22, line_dash="dot",row = 1, col=2)
        fig_ABGA.add_hline(y=26, line_dash="dot",row = 1, col=2)
        fig_ABGA.add_hrect(y0=22, y1=26, line_width=0, fillcolor="green", opacity=0.2,row = 1, col=2)

        fig_ABGA.add_trace(go.Scatter(x=data_df['Date'],y=data_df['TCO2'], mode='markers+text',text=data_df['TCO2'],textposition='top center',name='TCO2'),row=2,col=1)
        fig_ABGA.add_hline(y=22, line_dash="dot",row=2,col=1)
        fig_ABGA.add_hline(y=29, line_dash="dot",row=2,col=1)
        fig_ABGA.add_hrect(y0=22, y1=29, line_width=0, fillcolor="green", opacity=0.2,row=2,col=1)

        fig_ABGA.add_trace(go.Scatter(x=data_df['Date'],y=data_df['Ionized Ca'], mode='markers+text',text=data_df['Ionized Ca'],textposition='top center',name='Ionized Ca'),row=2,col=2)
        fig_ABGA.add_hline(y=1.15, line_dash="dot",row=2,col=2)
        fig_ABGA.add_hline(y=1.3, line_dash="dot",row=2,col=2)
        fig_ABGA.add_hrect(y0=1.15, y1=1.3, line_width=0, fillcolor="green", opacity=0.2,row=2,col=2)

        fig_ABGA.add_trace(go.Scatter(x=data_df['Date'],y=data_df['An.Gap'], mode='markers+text',text=data_df['An.Gap'],textposition='top center',name='An.Gap'),row=2,col=3)
        fig_ABGA.add_hline(y=3, line_dash="dot",row=2,col=3)
        fig_ABGA.add_hline(y=11, line_dash="dot",row=2,col=3)
        fig_ABGA.add_hrect(y0=3, y1=11, line_width=0, fillcolor="green", opacity=0.2,row=2,col=3)
        fig_ABGA.update_layout(width = 2400,height = 1500)

        fig_ABGA.update_layout(hoverlabel=dict(
            bgcolor="white",
            font_size=30,
            font_family="Rockwell"
        ),font=dict(size = 15))
        return html.P('혈액검사(ABGA) dashboard입니다. ',style={'textAlign': 'center'}), dcc.Graph(figure=fig_ABGA),html.Hr()   

    
#------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':
    app.run_server(debug=True)
