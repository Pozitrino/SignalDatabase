import numpy as np
import dash
import flask
import dash_table
import io
from dash.dependencies import Output, Input, State
import dash_html_components as html
import dash_core_components as dcc
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
from werkzeug.wsgi import FileWrapper
from flask import  Response

from utils.DataframeUtils import DataframeHandler
from utils.LocalUtils import LocalUtil
from utils.DatabaseUtils import DatabaseHandler
from utils.JsonUtils import JsonUtil
from utils.PlotUtils import GraphUtil,AnnotsUtil
from utils.GeneralUtils import features,NON_THRESHOLD
from utils.ParserUtils import parse_contents


import os


dir_path = os.path.dirname(os.path.realpath(__file__))
Local = LocalUtil(dir_path)
server = flask.Flask(__name__)
app = dash.Dash(server=server)    
app.title='Signal Database'
Local.rebuild_indexer()



Url_and_storage = html.Div([
    #storing values in browser
    dcc.Store(id='signal-id',storage_type="local"),
    dcc.Store(id='signal-source', data="Local",storage_type="local"),
    dcc.Store(id='aTable-signal-id'),
    dcc.Store(id='sTable-row-count'),
    dcc.Store(id='first-boundary'),
    dcc.Store(id='second-boundary'),
   
    #For changing pages
    html.Div(id='page-content'), 
    dcc.Location(id='url', refresh=False)
])


##################################################################################################################################################
##
## Database_layout
#################################################################################################################################################

Database_layout = html.Div(
     children=[
        dcc.Tabs([
        dcc.Tab(label='Search',value="search", children=[    
        html.Div(className='row',
                 children=[
                    html.Div(className='four columns div-user-controls',
                             children=[
                                 html.Div(
                                     className='div-for-dropdown',
                                     children=[
                                                 
                                               html.Label("Signal Source:"),
                                               dcc.Dropdown(id='source-dropdown',
                                                            options=[
                                                                {'label': 'Local', 'value': 'Local'},
                                                                {'label': 'Atlas DB', 'value': 'Atlas'}
       
                                                                    ],value='Local'
                                                            ),
                                               html.Label("Find signals by:"),
                                               dcc.Dropdown(id='metadata-dropdown',
                                                            options=[
                                                                {'label': 'ID', 'value': 'metadata.id'},
                                                                {'label': 'Name', 'value': 'metadata.name'},
                                                                {'label': 'Description', 'value': 'metadata.description'},
                                                                {'label': 'Author', 'value': 'metadata.authors'},
                                                                {'label': 'Measurement', 'value': 'metadata.measurement'},
                                                                {'label': 'Technology type', 'value': 'metadata.technology_type'},
                                                                {'label': 'Factor types', 'value': 'metadata.factor_types'},
                                                                {'label': 'Date taken', 'value': 'metadata.date_taken'},
                                                                {'label': 'Sample rate', 'value': 'metadata.sample_rate'},
                                                                {'label': 'License', 'value': 'metadata.license'}
                                                                    ],value='metadata.id'
                                                            ),
                                               html.Div(id='my-output'),                                               
                                               dcc.Input(id='input-on-submit', type='text',style={'width':'100%'}),
                                               html.A( html.Button('Get Json', id="json_button",style={'width':'100%','text-align': 'center','min-width': '100px','display': 'none'}), id='download-link',style={'width':'100%'}),
                                               dcc.Link(html.Button('open',id="open",style={'width':'100%','text-align': 'center','min-width': '100px','display': 'none'}),href="/page-1",target="_blank" )
                                      ])
                                ],style={'width': '10%','min-width': '100px'}
                            ),
                html.Div(className='eight columns div-for-charts bg-grey',
                             children=[
                                 
                                 
                                 
                                  html.Div(id='my-output2'),
                                  dcc.Link(dash_table.DataTable(id='search-table',    style_header={
        'backgroundColor': '#e6e6e6','font_size': '15px',
        'fontWeight': 'bold','textAlign': 'center'
    }, style_cell={
       'textAlign': 'center',
       'font_size': '13px',
       'fontWeight': 'bold'
       
    },    style_data_conditional=[
        {
            'if': {'row_index': 'odd'},
            'backgroundColor': '#f8f8f8'
        }
            ]),href="/page-1",target="_blank",style={"color": "black", "text-decoration": "none"})
   
                             ],style={'width': '85%'}),
                
                 
               
             ])   
                
             ]),dcc.Tab(label='Upload and edit signals',value="upload", children=[  
                 
                 
                 html.Label("All signals in database:"),
                 dash_table.DataTable(id='all-signals-table', page_current=0, row_selectable="single",
        row_deletable=False,
    page_size=10,
    page_action='custom',    style_header={
        'backgroundColor': '#e6e6e6','font_size': '15px',
        'fontWeight': 'bold','textAlign': 'center'
    }, style_cell={
       'textAlign': 'center',
       'font_size': '13px',
       'fontWeight': 'bold'
       
    },    style_data_conditional=[
        {
            'if': {'row_index': 'odd'},
            'backgroundColor': '#f8f8f8'
        }
            ]),
                 
                 
                 
                
                 html.Button('Import from mongo', id='import-button'),
                 html.Div(id="buttons",
                             children=[
                html.Button('Delete Signal', id="delete-button",style={'display': 'inline-block'}),
                dcc.Link(html.Button('open',id="open2",style={'display': 'inline-block'}),href="/page-1",target="_blank" )
                
                ],style={'display': 'none'}),
                
                dcc.Tabs([
                 dcc.Tab(label='Upload signal',value="sig_upload", children=[  
                                  html.Label("Upload signal file:"), 

 dcc.Upload(id='upload-data',children=html.Div
            ([
            'Drag and Drop or ',
            html.A('Select Files')
            ]),
        style={
            'width': '25%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px'
        },
         
        multiple=True
    ),
    html.Div(id='output-data-upload') 
                     
                     
                     ]),
                 dcc.Tab(label='Edit Metadata',value="sig_edit", 
                children=[ 
                    
                    
        html.Div(id='placeholder2'),
        
        
        html.Div(children=[ 
        html.Label('Name:'),
        dcc.Input(id='sig_name', type='text'),
        html.Label('Date taken:'),
        dcc.Input(id='sig_date', type='text'),
        ],style={'display': 'inline-block'}),
        
        html.Div(children=[ 
        html.Label('Authors:'),
        dcc.Input(id='sig_authors', type='text'),
        html.Label('Measurement:'),
        dcc.Input(id='sig_measurement', type='text'),
        ],style={'display': 'inline-block'}),
        
         html.Div(children=[ 
        html.Label('Technology types:'),
        dcc.Input(id='sig_technology', type='text'),       
        html.Label('Factor types'),
        dcc.Input(id='sig_factor', type='text'),
        ],style={'display': 'inline-block'}),
         
        html.Div(children=[ 
 
        html.Label('License:'),
        dcc.Input(id='sig_license', type='text'),
        ],style={'display': 'inline-block','vertical-align':'top'}),
        
        html.Div(children=[ 
        html.Label('Description:'),
        dcc.Textarea(id='sig_description'),
        ],style={'display': 'block'}),
        

        
        html.Button('Save changes', id="edit-metadata-button",style={'display': 'block'}) ]),]),
                
        html.Div(id='placeholder')
    

        
        
        
        ])
        ],id="tab-search",value="search")
])

##################################################################################################################################################
##
##Graph page Layout 
##################################################################################################################################################


Graph_page = html.Div([
   
    
   html.Div([

        dcc.Tabs([
        
                 dcc.Tab(label='Original signal', children=[
                         dcc.Graph(id='original-signal-figure'),
                         
    
    
    dcc.Tabs([
     dcc.Tab(label='Signal properties', value='properties', children=[    
    dash_table.DataTable(id='sProperties-table',    style_header={
        'backgroundColor': '#e6e6e6','font_size': '20px',
        'fontWeight': 'bold','textAlign': 'center'
    }, style_cell={
       'textAlign': 'center',
       'font_size': '13px',
       'fontWeight': 'bold'
       
    },    style_data_conditional=[
        {
            'if': {'row_index': 'odd'},
            'backgroundColor': '#f8f8f8'
        }
            ]
            
            
            
        
    )]),dcc.Tab(label='Annotations', value='annotations', children=[
 
        html.Div(id='X_value'),
        
        
        
        html.Div(id='Y_value'),
        
        html.Div(id='Channel'),
        
        html.Label('Label:'),
        dcc.Input(id='ann_label', type='text'),
        
        html.Label('Notes:'),
        dcc.Input(id='ann_notes', type='text'),
        html.Button('Add annotation to graph', id="annotation-button",style={'display': 'none'}),
        html.Button('Save annotation', id="annotation-save",style={'display': 'none'})
        
        
        
        
        
        
        ]), 
            
                 ],id="tabs4",value="properties")]),
                 dcc.Tab(label='Filters',value="filters", children=[
                         dcc.Graph(id='filters-figure'),
                
                
                dcc.Tabs([
                dcc.Tab(label='Lowpass',value="lowpass", children=[
                                    
                   html.Label('Filter channels:',id="lp_label"), 
                                    dcc.Dropdown(
        id='lp-chan-sel',
       multi=True
    ),
                    
                html.Div(id='lp_label_cutoff'),

                    dcc.Slider(id='slider-lp-cutoff',min=0.25,step=0.25,
                    updatemode='drag'
                   ),
                html.Div(id='lp_label_order'),
                 dcc.Slider(id='slider-lp-order',
                   min=1,
                   max=10,
                   step=1,
                   value=1,
 marks={i : '{}'.format(i) for i in range(1,11,1)},
        
        
        
   
    included=True,updatemode='drag'
                   ),
                 




                 ]),
                dcc.Tab(label='Highpass',value="highpass", children=[
                    
                    html.Label('Filter channels:',id="hp_label"), 
                                    dcc.Dropdown(
        id='hp-chan-sel',
       multi=True
    ),
                    html.Div(id='hp_label_cutoff'),
                    dcc.Slider(id='slider-hp-cutoff',min=0.25,step=0.25,
                    updatemode='drag'
                   ),
                
                html.Div(id='hp_label_order'),
                 dcc.Slider(id='slider-hp-order',
                   min=1,
                   max=10,
                   step=1,
                   value=1,
 marks={i : '{}'.format(i) for i in range(1,11,1)},
        
        
        
   
    included=True,updatemode='drag'
                   )
                 

                 ]),
                dcc.Tab(label='Bandpass',value="bandpass", children=[
                    html.Label('Filter channels:',id="bp_label"), 
                                    dcc.Dropdown(
        id='bp-chan-sel',
       multi=True
    ),
                    html.Div(id='bp_label_cutoff'),
                    dcc.RangeSlider(id='slider-bp-cutoff',min=0.25,step=0.25,
                    updatemode='drag',allowCross=False
                   ),
                html.Div(id='bp_label_order'),
                 dcc.Slider(id='slider-bp-order',
                   min=1,
                   max=10,
                   step=1,
                   value=1,
 marks={i : '{}'.format(i) for i in range(1,11,1)},
        
        
        
   
    included=True,updatemode='drag'
                   )
                 

                 ]),
            dcc.Tab(label='Bandstop',value="bandstop", children=[
                    html.Label('Filter channels:',id="bs_label"), 
                                    dcc.Dropdown(
        id='bs-chan-sel',
       multi=True
    ),
                    html.Div(id='bs_label_cutoff'),
                    dcc.RangeSlider(id='slider-bs-cutoff',min=0.25,step=0.25,
                    updatemode='drag',allowCross=False
                   ),
                html.Div(id='bs_label_order'),
                 dcc.Slider(id='slider-bs-order',
                   min=1,
                   max=10,
                   step=1,
                   value=1,
 marks={i : '{}'.format(i) for i in range(1,11,1)},
        
        
        
   
    included=True,updatemode='drag'
                   )
                 

                 ]),    
                
                


],id="filters-tab",value="tab1")

    ]), 
    
    dcc.Tab(label='Fourier transform',value="Fourier", children=[
            dcc.Graph(id='graph-fourier'),
                 

                 ])
   
    ],id="tabs1")  
            
    

  ])  
]) 


# index layout
app.layout = Url_and_storage

#complete layout
app.validation_layout = html.Div([
    Url_and_storage,
    Database_layout,
    Graph_page,
])




##################################################################################################################################################
##
##index page callbacks
##################################################################################################################################################

#Switches pages
@app.callback(Output('page-content', 'children'),
              Input('url', 'pathname'))
def display_page(pathname):
    if pathname == "/page-1":
        return Graph_page
    else:
        return Database_layout

##################################################################################################################################################
##
##Search Tab
##################################################################################################################################################

#Updates signal source i.e Local db or Cloud db
@app.callback(Output('signal-source', 'data'), [Input('source-dropdown', 'value')])
def update_sig_source(value):
    return value

#Updates link for download
@app.callback(Output('download-link', 'href'), 
              [Input('signal-id', 'data'),
              Input('signal-source', 'data')])
def update_link(value,source):
    return '/dash/urlToDownload?value={}&source={}'.format(value,source)


#Returns selected signal as json, reacts to url change
@app.server.route('/dash/urlToDownload')
def download_json():
    value = flask.request.args.get('value')
    source = flask.request.args.get('source')
    str_io = io.StringIO()
    
    if source == 'Local':
        json_dict = Local.load(int(value))
        str_io.write(json.dumps(json_dict, indent=2))
    else:
        database=DatabaseHandler()
        json_dict=database.load_from_database("metadata.id",int(value))
        str_io.write(json.dumps(json_dict[0], indent=2))
    mem = io.BytesIO()
    mem.write(str_io.getvalue().encode('utf-8'))
    mem.seek(0)
    str_io.close()
    
    file_wrapper = FileWrapper(mem)
    headers = {
        'Content-Disposition': 'attachment; filename="Signal Id_{}.json"'.format(value)
    }
    response = Response(file_wrapper,
                        mimetype='application/json',
                        direct_passthrough=True,
                        headers=headers)
    return response


#Updates search table and return number of rows
@app.callback(
    [Output('search-table', 'data'), Output('search-table', 'columns'),
     Output('sTable-row-count', 'data')],
    [Input('metadata-dropdown', 'value'),Input('input-on-submit', 'value'),
     Input('signal-source', 'data')]
)
def update_sTable(dropdown_value,input_value,storage):
        if input_value.strip().isdigit():
           input_value = int(input_value) 
        if storage == 'Local':
            id_list = Local.search(dropdown_value, input_value)        
            df = DataframeHandler.dataframe_local(id_list)
        else:
             database=DatabaseHandler()
             json_dict = database.load_from_database(dropdown_value,input_value)
             df = DataframeHandler.dataframe(json_dict)

        columns=[{"name": i, "id": i} for i in df.columns] 
               
        return df.to_dict('records'),columns,len(df.index)






#Clears search table active cell (the red highlight thing)
@app.callback(
    [Output("search-table", "selected_cells"), Output("search-table", "active_cell")],
    [Input('metadata-dropdown', 'value'),Input('input-on-submit', 'value'),
     Input('aTable-signal-id', 'data')],
    State("search-table", "active_cell")
)
def clear_cell(dropdown_value,input_value,aTable,active_cell):    
    if active_cell:
        return [], None


#Gets signal id from highlighted row
@app.callback(Output('signal-id','data'),
              [Input('search-table', 'active_cell'),Input('aTable-signal-id', 'data')],
              State('search-table', 'data')
               )
def get_active_letter(active_cell,aTable_sig_id,data_t):
    if active_cell:
        sig_id=data_t[active_cell['row']]['ID']
        return sig_id
    else:
        return aTable_sig_id



#Updates the number of found signals in local db or cloud db
@app.callback(
    [Output(component_id='my-output', component_property='children'),
     Output(component_id='my-output2', component_property='children')],
    [Input('metadata-dropdown', 'value'),Input('sTable-row-count', 'data'),
     Input('input-on-submit', 'value')]
)
def update_number_of_found_signals(input_value,row_count,value):
    input_value = input_value[9:] 
    if row_count == None:
       row_count=0 
       value="empty"
    
    return '{}:'.format(input_value),'Found {} signals where {} is equal to {}:'.format(row_count,input_value,value) 

#Shows/hides Get json button
@app.callback(
   Output(component_id='json_button', component_property='style'),
   Input('search-table', 'active_cell'))
def show_hide_buttons(active_cell):
    if active_cell:
        return {'width':'100%','text-align': 'center','min-width': '100px','display': 'block'}
    else:
        return {'display': 'none'}


##################################################################################################################################################
##
##Upload and edit signals
##################################################################################################################################################


#Updates the table with all signals
@app.callback(
    [Output('all-signals-table', 'data'), Output('all-signals-table', 'columns')],
    [Input('output-data-upload', 'children'),    Input('all-signals-table', "page_current"),
     Input('signal-source', 'data'),
    Input('all-signals-table', "page_size"),Input('buttons', 'style'),Input('placeholder', 'children'),
    Input("placeholder2", "children")]
)
def update_aTable(filename,page_current,storage,page_size,buttons,placeholder,placeholder2):
        if storage == 'Local':
            id_list = Local.all_signals()
            df = DataframeHandler.dataframe_local(id_list)
        else:    
            database = DatabaseHandler()
            df = DataframeHandler.dataframe(database.all_signals())
            
        columns=[{"name": i, "id": i} for i in df.columns] 
               
        return df.iloc[
        page_current*page_size:(page_current+ 1)*page_size
    ].to_dict('records'),columns


#Updates signal id of selected row
@app.callback(
    Output('aTable-signal-id', 'data'),
    Input('all-signals-table', 'selected_rows'),State('all-signals-table', 'data')
)
def selected_row(selected_row,data_t):
    sig_id=data_t[selected_row[0]]['ID']
    return sig_id


#Deletes signal and resets the selected row to unselected row
@app.callback(
    Output('all-signals-table', 'selected_rows'),
    [Input('delete-button', 'n_clicks'),Input('tab-search', 'value')],
    State('signal-source', 'data'),State('aTable-signal-id', 'data'),
    prevent_initial_call=True
)
def delete_signal_reset_row(button,cur_tab,storage,sig_id):
        
    
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if 'delete-button' in changed_id:
    
        if storage == 'Local':
           Local.delete(int(sig_id))
        else:    
            database = DatabaseHandler()
            database.delete(int(sig_id))
    return [] 


#Hides/shows buttons for deleting/opening of signal
@app.callback(
   Output(component_id='buttons', component_property='style'),
   [Input('all-signals-table', 'selected_rows'),Input('source-dropdown', 'value')])
def show_hide_delete_buttons(active_cell,source_dropdown):
    if active_cell:
        return {'text-align': 'center','min-width': '100px','display': 'inline-block'}
    else:
        return {'display': 'none'}


##################################################################################################################################################
##
##Upload signal tab
##################################################################################################################################################
#Uploads files to db. Returns if it was successful or not.
@app.callback(Output('output-data-upload', 'children'),
              Input('upload-data', 'contents'),
             [ State('upload-data', 'filename'),
               State('upload-data', 'last_modified'),
               State('signal-source', 'data')
              
              ])
def upload_file(list_of_contents, list_of_names, list_of_dates,storage):
    if list_of_contents is not None:
         children = [
            parse_contents(c, n, d,storage,dir_path) for c, n, d in
            zip(list_of_contents, list_of_names, list_of_dates)]
         return children


#Imports data from local to cloud database or vice versa. Depending on 
#selected signal source
@app.callback(Output('placeholder', 'children'),
              Input('import-button', 'n_clicks'),State('signal-source', 'data'),
              prevent_initial_call=True)
def import_signals(imp_button,storage):
        database = DatabaseHandler()
        if storage == "Local":
           
           database.mongo_import(dir_path) 
        else:
            
           database.local_import(dir_path)          
        return ""

#Changes label of button, depending on selected signal source
@app.callback(Output('import-button', 'children'),
              Input('signal-source', 'data'))
def change_text(storage):
    if storage == "Local":
        return "Import from MongoDB"
    else:
        return "Import from LocalDB"


##################################################################################################################################################
##
## Edit metadata tab
##################################################################################################################################################
#Puts existing metadata to textboxes
@app.callback(
    [
     Output('sig_name', 'value'),
     Output('sig_description', 'value'),
     Output('sig_authors', 'value'),
     Output('sig_measurement', 'value'),
     Output('sig_technology', 'value'),
     Output('sig_factor', 'value'),
     Output('sig_date', 'value'),
     Output('sig_license', 'value'),
    ],
    Input('aTable-signal-id','data'),State('signal-source', 'data')
)
def edit_signal_update_inputs(data_t,storage):
    if storage == "Local":
        json_dict = Local.load(data_t)
    else:
        database = DatabaseHandler()
        json_dict=database.load_from_database_one(data_t)
    
    return (json_dict["metadata"]["name"],json_dict["metadata"]["description"],
            json_dict["metadata"]["authors"],json_dict["metadata"]["measurement"],
            json_dict["metadata"]["technology_type"],json_dict["metadata"]["factor_types"],
            json_dict["metadata"]["date_taken"],json_dict["metadata"]["license"])




#Saves updated metadata to db
@app.callback(
    Output("placeholder2", "children"),
    Input('edit-metadata-button','n_clicks'),
    [
     State('aTable-signal-id', 'data'),
     State('sig_name', 'value'),
     State('sig_description', 'value'),
     State('sig_authors', 'value'),
     State('sig_measurement', 'value'),
     State('sig_technology', 'value'),
     State('sig_factor', 'value'),
     State('sig_date', 'value'),
     State('sig_license', 'value'),
     State('signal-source', 'data')
    ], prevent_initial_call=True
)
def update_signal_metadata(click,sig_id,sig_name,sig_description,sig_authors,
                           sig_measurement,sig_technology,sig_factor,sig_date,
                           sig_license,storage):
    if storage == "Local":
        Local.update_metadata(int(sig_id), sig_name, sig_description, sig_authors,
                              sig_measurement, sig_technology, sig_factor, sig_date,
                              sig_license)
    else:
        database = DatabaseHandler()
        database.update(sig_id, sig_name, sig_description, sig_authors, sig_measurement,
                        sig_technology, sig_factor, sig_date, sig_license)
    
    return ""
    


 
##################################################################################################################################################
##
##      Graph page callbacks
############################################################################################################################################################
##################################################################################################################################################
##
## Original signal tab
##################################################################################################################################################
#Updates the figure of original signal and adds/saves annotations
@app.callback(Output('original-signal-figure','figure'),
               [Input('signal-id', 'data'),Input('annotation-button', 'n_clicks'),Input('annotation-save', 'n_clicks')],
               [State('signal-source', 'data'),State('original-signal-figure', 'clickData'),State('ann_label','value'),State('ann_notes','value')])

def original_signal_figure(data_t,annots_click,annots_save_click,source,data_g_click,label,notes):        
        if source == "Local":
            json_dict = Local.load(data_t)
            signal = JsonUtil(json_dict)
            if signal.sample_count>4096:
              json_dict = signal.signal_resample()
                        
        else:    
            database = DatabaseHandler()
            json_dict = database.load_from_database("metadata.id",int(data_t))[0]
            signal = JsonUtil(json_dict)
            if signal.sample_count>4096:
              json_dict = signal.signal_resample()
        
        changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
        annots = AnnotsUtil()
        if data_g_click:
            if 'annotation-save' in changed_id:
                
                ev = annots.create_event(data_g_click["points"][0]["pointIndex"], label, notes, data_g_click["points"][0]["curveNumber"])
                annots.add_event(json_dict["annotations"], ev, 0)
                Local.delete(data_t)
                Local.save(json_dict)
                Local.rebuild_indexer()
            else:
                ev = annots.create_event(data_g_click["points"][0]["pointIndex"], label, notes, data_g_click["points"][0]["curveNumber"])
                annots.add_event(json_dict["annotations"], ev, 0)
        
        return GraphUtil(json_dict).simple_plot()





#Gets the zooms values and transform them to the closest usable index of signal.  
@app.callback([Output('first-boundary','data'),Output('second-boundary','data')],
               Input('original-signal-figure', 'relayoutData'),
               [State('original-signal-figure','figure'),State('signal-id', 'data'),State('signal-source', 'data')]
               
               )
def zoom_indexes(r_data:dict, figure,data_t,source):
        
    if 'xaxis.autorange' in r_data:
        return -1,-1
    
    if 'xaxis.range[0]' in r_data:
            left = r_data['xaxis.range[0]']
            right = r_data['xaxis.range[1]']
            
            if source == "Local":
                json_dict=Local.load(data_t)
            else: 
                database = DatabaseHandler()
                json_dict = database.load_from_database("metadata.id",int(data_t))[0]
          
            
            signal = JsonUtil(json_dict)

            if signal.sample_count>4096:
              json_dict = signal.signal_resample()
              signal = JsonUtil(json_dict)
            
            x_axis = signal.x_index

            if left < 0:
                left = 0
            
            if right < 0:
                right = 0
            
            if right > x_axis[len(x_axis)-1]:
               right =  x_axis[len(x_axis)-1]
             
            if left > x_axis[len(x_axis)-1]:
               left =  x_axis[len(x_axis)-1]   
            
            a = np.format_float_positional(x_axis[1], trim='-')
            r = list(str(a))
            period_index = r.index('.')
            r[len(r)-1] = "1"
            
            
            after_dot = len(r) - int(period_index+1) 
            while period_index+1 < len(r)-1:
                r[period_index+1] = "0"
                period_index= period_index +1



            adjustment = float(''.join(r))
    
            left_check = 0
            right_check = 0
            first_index = round(left,after_dot)
            last_index = round(right,after_dot)
            
            
            while left_check == 0:

                left_match = np.where(x_axis == first_index)
                if len(left_match[0]) == 0:
                    first_index = round(first_index - adjustment,after_dot)
                else:
                    left_check = 1
            
            while right_check == 0:

                right_match = np.where(x_axis == last_index)
                if len(right_match[0]) == 0:
                   last_index = round(last_index + adjustment,after_dot)
                else:
                    right_check = 1
            

            return int(left_match[0]),int(right_match[0])


##################################################################################################################################################
##
## Signal properties tab
##################################################################################################################################################

#Updates table with signal properties
@app.callback([Output('sProperties-table', 'data'), Output('sProperties-table', 'columns')],
               [Input('signal-id', 'data'),Input('first-boundary','data'), Input('second-boundary','data')],State('signal-source', 'data'))
def update_properties_table(data_t,low,high,source):
        
    
        if source == "Local":
            json_dict = Local.load(data_t)
        else:    
            database = DatabaseHandler()
            json_dict = database.load_from_database("metadata.id",int(data_t))[0]

        cont = JsonUtil(json_dict) 
        if cont.sample_count>4096:
              json_dict = cont.signal_resample()
        
        signal = cont.signals      
        chan_count = cont.channel_count
        l = 1
        
        if low == -1:
            low = 0
            high = len(signal[0])-1
        
        
        if chan_count != 1:
            Sig_cut = np.array([signal[0][low:high]])
            while l < chan_count:  
                Sig_cut =np.concatenate((Sig_cut,np.array([signal[l][low:high]]))) 
                l=l+1    
        else:
            Sig_cut = np.array([signal[0][low:high]])
            
        df = DataframeHandler.features_dataframe(chan_count, features(Sig_cut,NON_THRESHOLD))
        columns=[{"name": i, "id": i} for i in df.columns]
        
        return df.to_dict('records'),columns



##################################################################################################################################################
##
## Annotations tab
##################################################################################################################################################
#Shows/hides buttons for saving annotations.
@app.callback(
   Output(component_id='annotation-save', component_property='style'),
  [ Input('annotation-button', 'n_clicks'),Input('annotation-save', 'n_clicks')])
def show_hide_annots_save(annots_button,annots_save_button):
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if 'annotation-save' in changed_id:
        return {'display': 'none'}
    elif 'annotation-button' in changed_id:
        return {'display': 'block'}
    else:
        return {'display': 'none'}


#Shows/hides buttons for adding annotations.
@app.callback(
   Output(component_id='annotation-button', component_property='style'),
  [ Input('annotation-button', 'n_clicks'),Input('original-signal-figure', 'clickData')])
def show_hide_annots_add(annots_button,figure_clickData):
    if figure_clickData == None:
        return {'display': 'none'}
    
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if 'annotation-button' in changed_id:
        return {'display': 'none'}
    else:
        return {'display': 'block'}


##################################################################################################################################################
##
## Filters tab
##################################################################################################################################################
#Updates figure after applying filters and changing zoom levels.
@app.callback(
    Output('filters-figure', 'figure'),
    [Input('filters-tab', 'value'),
     Input('slider-lp-cutoff', 'drag_value'),
     Input('slider-lp-order', 'drag_value'),
     Input('slider-hp-cutoff', 'drag_value'),
     Input('slider-hp-order', 'drag_value'),
     Input('slider-bp-cutoff', 'drag_value'),
     Input('slider-bp-order', 'drag_value'),
     Input('slider-bs-cutoff', 'drag_value'),
     Input('slider-bs-order', 'drag_value'),
     Input('lp-chan-sel', 'value'),
     Input('hp-chan-sel', 'value'),
     Input('bp-chan-sel', 'value'),
     Input('bs-chan-sel', 'value'),
     Input('first-boundary','data'), 
     Input('second-boundary','data')
     ],
        [State('signal-id', 'data'),State('signal-source', 'data')])
def filter_graph(tab,lp_cutoff,lp_order,hp_cutoff,hp_order,bp_cutoff,
                 bp_order,bs_cutoff,bs_order,lp_chan,hp_chan,bp_chan,
                 bs_chan,low,high,data_t,source):
       
       if source == "Local":
           json_dict=Local.load(data_t)

       else: 
           database = DatabaseHandler()
           json_dict = database.load_from_database("metadata.id",int(data_t))[0]
    
       signal = JsonUtil(json_dict)
       if signal.sample_count>4096:
          json_dict = signal.signal_resample()
    
       figure = GraphUtil(json_dict) 
       if tab == "lowpass":
           return figure.filter_plot(lp_cutoff,lp_order,'lowpass',lp_chan,low,high) 
       
       if tab == "highpass":
           return figure.filter_plot(hp_cutoff,hp_order,'highpass',hp_chan,low,high)
       
       if tab == "bandpass":
           return figure.filter_plot(bp_cutoff,bp_order,'bandpass',bp_chan,low,high)        
       
       if tab == "bandstop":
           return figure.filter_plot(bs_cutoff,bs_order,'bandstop',bs_chan,low,high) 
        
       else:
         sig = signal.signals
         sig_duration = signal.x_index
        
        
         if low != -1:
             sig_duration = sig_duration[low:high]
         else:
             low = 0
             high = len(sig_duration)-1

         i=0 
         fig = make_subplots(rows=signal.channel_count, cols=1,shared_xaxes=True)
        
         while i < signal.channel_count:
              
            
               fig.add_trace(
               go.Scatter(x=sig_duration, y=sig[i][low:high],name = f'{i+1} .channel'),
               row=i+1, col=1, 
               )
              
               i += 1
         fig.update_layout(title_text="Graph of selected signal:" )
         return fig





#Updates dropdown for selecting what channels to filter
@app.callback(
    [Output('lp-chan-sel', 'options'),Output('lp-chan-sel', 'value'),Output('lp-chan-sel', 'style'),
     Output('hp-chan-sel', 'options'),Output('hp-chan-sel', 'value'),Output('hp-chan-sel', 'style'),
     Output('bp-chan-sel', 'options'),Output('bp-chan-sel', 'value'),Output('bp-chan-sel', 'style'),
     Output('bs-chan-sel', 'options'),Output('bs-chan-sel', 'value'),Output('bs-chan-sel', 'style'),
     Output('lp_label', 'style'),Output('hp_label', 'style')
    ,Output('bs_label', 'style'),Output('bp_label', 'style')],
    [Input('original-signal-figure', 'figure')],
    [State('signal-id', 'data'),State('signal-source', 'data')])
def update_channel_dropdown(figure,data_t,source): 
        if source == "Local":
            json_dict = Local.load(data_t)
        else:    
            database = DatabaseHandler()
            json_dict = database.load_from_database("metadata.id",int(data_t))[0]
        
        signal = JsonUtil(json_dict)
        chan_count = signal.channel_count
        chan_list = []
        
        if chan_count == 1:
            
            return (chan_list,[], {'display': 'none'},chan_list,[],
        {'display': 'none'},chan_list,[], {'display': 'none'},chan_list,[],
        {'display': 'none'},{'display': 'none'},{'display': 'none'},
        {'display': 'none'},{'display': 'none'})
        i=0
        while i < chan_count:
            chan_list.append({'label': i+1, 'value': i+1})
            i=i+1
        
        return (chan_list,[],{'display': 'block'},chan_list,[], 
                {'display': 'block'},chan_list,[], {'display': 'block'},
                chan_list,[], {'display': 'block'},{'display': 'block'},
                {'display': 'block'},{'display': 'block'},{'display': 'block'})





##################################################################################################################################################
##
## Updating sliders
##################################################################################################################################################
@app.callback(
    [Output('lp_label_cutoff', 'children'),Output('lp_label_order', 'children')],
    [
      Input('slider-lp-cutoff', 'drag_value'),
      Input('slider-lp-order', 'drag_value')
    ])
def Update_lp_labels(cutoff,order):
  return  'Filter cuttoff: {} [Hz]'.format(cutoff),'Filter order: {}'.format(order)

@app.callback(
    [Output('hp_label_cutoff', 'children'),Output('hp_label_order', 'children')],
    [
     Input('slider-hp-cutoff', 'drag_value'),
     Input('slider-hp-order', 'drag_value')
    ])
def Update_hp_labels(cutoff,order):
    
    return  'Filter cuttoff: {} [Hz]'.format(cutoff),'Filter order: {}'.format(order)

@app.callback(
    [Output('bp_label_cutoff', 'children'),Output('bp_label_order', 'children')],
    [
     Input('slider-bp-cutoff', 'drag_value'),
     Input('slider-bp-order', 'drag_value')
    ])
def Update_bp_labels(cutoff,order):
    
    return  'Filter cuttoff: {} [Hz] to {} [Hz]'.format(cutoff[0],cutoff[1]),'Filter order: {}'.format(order)
   
@app.callback(
    [Output('bs_label_cutoff', 'children'),Output('bs_label_order', 'children')],
    [
     Input('slider-bs-cutoff', 'drag_value'),
     Input('slider-bs-order', 'drag_value')
    ])
def Update_bs_labels(cutoff,order):
    
    return  'Filter cuttoff: {} [Hz] to {} [Hz]'.format(cutoff[0],cutoff[1]),'Filter order: {}'.format(order)



#Updates slider labels
@app.callback(
    [Output('slider-lp-cutoff', 'max'),
     Output('slider-lp-cutoff', 'value'),
     Output('slider-lp-cutoff','marks'),
     Output('slider-hp-cutoff', 'max'),
     Output('slider-hp-cutoff', 'value'),
     Output('slider-hp-cutoff','marks'),         
     Output('slider-bp-cutoff', 'max'),
     Output('slider-bp-cutoff', 'value'),
     Output('slider-bp-cutoff','marks'),
     Output('slider-bs-cutoff', 'max'),
     Output('slider-bs-cutoff', 'value'),
     Output('slider-bs-cutoff','marks')],
    Input('original-signal-figure','figure'),
    [State('signal-id', 'data'),State('signal-source', 'data')])
def update_values_of_sliders(figure,data_t,source):
      
          if source == "Local":
            json_dict = Local.load(data_t)
            signal = JsonUtil(json_dict)
            if signal.sample_count>4096:
              json_dict = signal.signal_resample()
          else:    
            database = DatabaseHandler()
            json_dict = database.load_from_database("metadata.id",int(data_t))[0]
          
          signal=JsonUtil(json_dict) 
          fs=signal.sample_rate
          label_step = 0
          if (fs/2) < 250:
              label_step = 5
          else:
              label_step= 100
          
          slider_values = {i : '{}'.format(i) for i in range(0,int(fs/2)+label_step,label_step)}
          
          return ((fs/2)-0.25,(fs/2)-0.25,slider_values,(fs/2)-0.25,0.25,
                  slider_values,(fs/2)-0.25,[0.25,(fs/2)-0.25],slider_values,
                  (fs/2)-0.25,[0.25,(fs/2)-0.25],slider_values)




##################################################################################################################################################
##
## Fourier transform
##################################################################################################################################################
#Updates graph for fourier transform
@app.callback(
    Output('graph-fourier', 'figure'),
    [Input('first-boundary','data'), Input('second-boundary','data'),Input('signal-id', 'data')],
     State('signal-source', 'data')
)
def fourier_graph(low,high,data_t,source):
       if source == "Local":
           json_dict=Local.load(data_t)
           signal = JsonUtil(json_dict)
           if signal.sample_count>4096:
              json_dict = signal.signal_resample()
       else: 
           database = DatabaseHandler()
           json_dict = database.load_from_database("metadata.id",int(data_t))[0]
               
       return GraphUtil(json_dict).plot_fft(low,high)


#Run app
if __name__ == '__main__':
    app.run_server(debug=False)