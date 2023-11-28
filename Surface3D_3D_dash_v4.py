## the graph is in div which using flex property, so in children we use vh for height and % for width.
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
import pandas as pd
import numpy as np
import os
import base64
import io
from dash.exceptions import PreventUpdate
import plotly.express as px

# Get a list of all available color scales
colorscales = px.colors.named_colorscales()
layers =['1','2','3','4','5']
layermapping ={'1':(-98618,45832,75290,219740),'2':(-87008,35842,86090,209750),'3':(-45698,-33998,104720,129920),'4':(-41918,-36638,115250,119330),'5' :(-39808,-38548,116810,117870)}
Zmax = 2

# Initialize the Dash app
app = dash.Dash(__name__)
server = app.server

app.layout = html.Div(
    [
        html.H2("Visualization From Chikei Data",style = {"margin":"0%"}),
        html.Div(
                [
                html.Div([
                html.P("Shape change for height:"),
                dcc.Slider(
                id='height-slider',
                min=0.1,
                max=Zmax,
                step=0.1,
                value=Zmax / 2,
                tooltip={"always_visible":False,"placement":"bottom"},
                marks=None, 
                ),],
                style = {"width":"50%", "margin":"0%","display":"inline-block"}
                ),
                html.Div([
                html.P("Colormap:"),        
                dcc.Dropdown(
                id='colormap-dropdown',
                options=colorscales,
                # value='viridis',
                value = 'plasma',style={"margin":"0%"}
                ),],
                style = {"width":"50%", "margin":"0%","display":"inline-block"}
                ),
                ]
                ),
        html.Div(
            [

                dcc.RadioItems(
                    id='file-chooser',
                    options=[
                        {'label': 'One File', 'value': 'one'},
                        {'label': 'Two Files', 'value': 'two'},
                        ],
                    value='one',
                    labelStyle={'display': 'block'},
                    style = {"font-size":"20px","margin-top":"10px","paddingTop":"5px","display":"inline-block"}),
                html.Div(
                    [
                        html.Div([
                            html.Div(dcc.Upload(
                                id='upload-data-one',
                                children=html.Button('Upload File One'),
                                multiple=False),style = {"display":"inline-block","margin-right":"4px"}),
                            html.P("Xmax1= ",style = {"marginBottom":"4px","display":"inline-block","margin-right":"2px"}),
                            dcc.Input(id='input-Xmax1',type='text',style = {"marginBottom":"4px","width":"80px","margin-right":"8px","display":"inline-block"}),
                            html.P("Xmin1= ",style = {"marginBottom":"4px","display":"inline-block","margin-right":"2px"}),
                            dcc.Input(id='input-Xmin1',type='text',style = {"marginBottom":"4px","width":"80px","margin-right":"8px","display":"inline-block"}),
                            html.P("Ymax1= ",style = {"marginBottom":"4px","display":"inline-block","margin-right":"2px"}),
                            dcc.Input(id='input-Ymax1',type='text',style = {"marginBottom":"4px","width":"80px","margin-right":"8px","display":"inline-block"}),
                            html.P("Ymin1= ",style = {"marginBottom":"4px","display":"inline-block","margin-right":"2px"}),
                            dcc.Input(id='input-Ymin1',type='text',style = {"marginBottom":"4px","width":"80px","margin-right":"8px","display":"inline-block"}), ],
                            id='Block-up',style={'display': 'block'}),
                        html.Div([
                            html.Div(dcc.Upload(
                                id='upload-data-two',
                                children=html.Button('Upload File Two'),
                                multiple=False,
                                ),style = {"display":"inline-block","margin-right":"4px"}),
                            html.P("Xmax2= ",style = {"marginTop":"0","display":"inline-block","margin-right":"2px"}),
                            dcc.Input(id='input-Xmax2',type='text',style = {"marginTop":"0","width":"80px","margin-right":"8px","display":"inline-block"}),
                            html.P("Xmin2= ",style = {"marginTop":"0","display":"inline-block","margin-right":"2px"}),
                            dcc.Input(id='input-Xmin2',type='text',style = {"marginTop":"0","width":"80px","margin-right":"8px","display":"inline-block"}),
                            html.P("Ymax2= ",style = {"marginTop":"0","display":"inline-block","margin-right":"2px"}),
                            dcc.Input(id='input-Ymax2',type='text',style = {"marginTop":"0","width":"80px","margin-right":"8px","display":"inline-block"}),
                            html.P("Ymin2= ",style = {"marginTop":"0","display":"inline-block","margin-right":"2px"}),
                            dcc.Input(id='input-Ymin2',type='text',style = {"marginTop":"0","width":"80px","margin-right":"8px","display":"inline-block"}),                          
                                ],id='Block-down',style={'display': 'none'},)
                      
                    ],
                     style = {"marginTop":"0","marginLeft":"30px","display":"inline-block","verticalAlign":"top"}),
                     html.Div([
                         html.Div([
                             html.P("Layer_One: ",style = {"marginBottom":"4px","display":"inline-block","margin-right":"140px"}),
                             html.P("Layer_Two: ",style = {"marginBottom":"4px","display":"inline-block"}),
                         ]),
                         html.Div([
                              dcc.Dropdown(id='layer-first', options=layers,optionHeight =20, style={"marginLeft":"40px","marginTop":"0",'width':'50px',"display":"inline-block",'font-size':'15px'}),
                              dcc.Dropdown(id='layer-second', options=layers,optionHeight =20, style={"marginLeft":"105px","marginTop":"0",'width':'50px',"display":"inline-block",'font-size':'15px'})

                         ])
                         
                                

                     ],
                     style = {"marginTop":"0","marginLeft":"30px","display":"inline-block","verticalAlign":"top"})
                ]
                ),
        html.Button(id='Generate',children='Generate',style={'margin':'0','height':'40px','width':'80px','backgroundColor':'#FFFFCC'}),

        html.Div(id='graph-container',style={'display': 'flex', 'flexDirection': 'row'})
    ],
    style={'transform': 'scale(1)'}
)


def process_uploaded_file(contents):
    # Process the uploaded file and return the data
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    data = pd.read_csv(io.StringIO(decoded.decode('utf-8')), header=None)
    data = data.iloc[:, :-1]
    return data.values

def create_3d_surface(height_grid, x, y, selected_colormap,title):
    fig = go.Figure(data=[go.Surface(z=height_grid, x=x, y=y, colorscale=selected_colormap,colorbar=dict(orientation='h'))],layout=go.Layout(title=title))
    fig.update_traces(contours_z=dict(show=True, usecolormap=True, highlightcolor="limegreen", project_z=True))
    return fig

@app.callback(
    Output('input-Xmax1','value'),
    Output('input-Xmin1','value'),
    Output('input-Ymax1','value'),
    Output('input-Ymin1','value'),
    Input('layer-first','value')
)
def undate_input(value):
    result = layermapping.get(value)
    if result is not None:
        Xmin1,Xmax1,Ymin1,Ymax1 = result
        return Xmax1,Xmin1,Ymax1,Ymin1
    else:
        return 0,0,0,0
@app.callback(
    Output('input-Xmax2','value'),
    Output('input-Xmin2','value'),
    Output('input-Ymax2','value'),
    Output('input-Ymin2','value'),
    Input('layer-second','value')
)
def undate_input(value):
    result = layermapping.get(value)
    if result is not None:
        Xmin2,Xmax2,Ymin2,Ymax2 = result
        return Xmax2,Xmin2,Ymax2,Ymin2
    else:
        return 0,0,0,0

@app.callback(
    [ Output('graph-container', 'children'),
      Output('Block-down', 'style')],
    [Input('Generate','n_clicks'),
     Input('height-slider', 'value'),
     Input('colormap-dropdown', 'value'),
     Input('file-chooser', 'value')],
    [State('upload-data-one', 'contents'),
     State('upload-data-two', 'contents'),
     State('upload-data-one', 'filename'),
     State('upload-data-two', 'filename'),
     State('input-Xmax1', 'value'),
     State('input-Xmin1', 'value'),
     State('input-Ymax1', 'value'),
     State('input-Ymin1', 'value'),
     State('input-Xmax2', 'value'),
     State('input-Xmin2', 'value'),
     State('input-Ymax2', 'value'),
     State('input-Ymin2', 'value'),]
)
def update_graph(click,scaling_factor, selected_colormap, file_chooser_value, file_one_contents, file_two_contents,file_one_filename,file_two_filename,xmax1,xmin1,ymax1,ymin1,xmax2,xmin2,ymax2,ymin2):
    if file_chooser_value == 'one' and file_one_contents is None:
        style = {'display': 'none'}
        children = [dcc.Graph(figure=go.Figure())]
        return children, style

    elif file_chooser_value == 'two' and (file_one_contents is None or file_two_contents is None):
        style = {'display': 'block'}
        children = [dcc.Graph(figure=go.Figure())]
        return children, style

    if file_chooser_value == 'one':
        height_grid_one = process_uploaded_file(file_one_contents)
        height_grid_two = np.zeros_like(height_grid_one)  # Create an empty array for the second file
        file_one_name = extract_filename(file_one_filename)
        file_two_name = None
        style = {'display': 'none'}
    else:
        height_grid_one = process_uploaded_file(file_one_contents)
        height_grid_two = process_uploaded_file(file_two_contents)
        # Take the minimum shape to ensure compatibility
        sh_y2, sh_x2 = height_grid_two.shape
        x2, y2 = np.linspace(int(xmin2), int(xmax2), sh_x2), np.linspace(int(ymin2), int(ymax2), sh_y2)

        style = {'display': 'block'}
        file_one_name = extract_filename(file_one_filename)
        file_two_name = extract_filename(file_two_filename)
    # Create the X, Y coordinates for the grid
    sh_y1, sh_x1 = height_grid_one.shape
    x, y = np.linspace(int(xmin1), int(xmax1), sh_x1), np.linspace(int(ymin1), int(ymax1), sh_y1)


    # Create 3D surface plots for each file
    fig_one = create_3d_surface(height_grid_one, x, y, selected_colormap,file_one_name)
    fig_one.update_layout(scene=dict(
        xaxis_title='X-axis',
        yaxis_title='Y-axis',
        zaxis_title='Height',
        camera=dict(
            up=dict(x=0, y=0, z=1),
            center=dict(x=0, y=0, z=0),
            eye=dict(x=-1.25, y=-2.0, z=1.25),
        ),
        aspectratio={'x': 1, 'y': 1, 'z': scaling_factor},
    ))

### change the width of graph according to the number of the figures
    if file_chooser_value == 'two':
        children = [dcc.Graph(figure=fig_one,style={"width":"50%","height":"90vh"})]
    else:
        children = [dcc.Graph(figure=fig_one,style={"width":"100%","height":"90vh"})]

    if file_chooser_value == 'two':
        fig_two = create_3d_surface(height_grid_two, x2, y2, selected_colormap,file_two_name)
        fig_two.update_layout(scene=dict(
            xaxis_title='X-axis',
            yaxis_title='Y-axis',
            zaxis_title='Height',
            camera=dict(
                up=dict(x=0, y=0, z=1),
                center=dict(x=0, y=0, z=0),
                eye=dict(x=-1.25, y=-2.0, z=1.25),
            ),
            aspectratio={'x': 1, 'y': 1, 'z': scaling_factor},
        ))

        children.append(dcc.Graph(figure=fig_two,style={"width":"50%","height":"90vh"}))




    return children,style

def extract_filename(filename):
    filename_netname, filename_type = filename.split('.')
    return filename_netname
    
if __name__ == "__main__":
    app.run_server(debug=True)