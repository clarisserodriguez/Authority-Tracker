#%%
import dash
from dash import Dash, dcc, html, Output, Input, ctx, State, ALL, MATCH, dash_table, exceptions
import dash_bootstrap_components as dbc

import pandas as pd
import numpy as np
import os
from datetime import datetime
import re

import sqlalchemy

from sqlalchemy.engine import URL
from sqlalchemy import create_engine
from sqlalchemy.sql import text as sa_text

#from dash import dash_table as dt
import pyodbc
import urllib

from datetime import datetime, date

import plotly.graph_objects as go

from utils import create_html_table,insert_collapsible_buttons, show_stage_sources, \
show_sources_docs, show_docs_prerequisites, count_occurrences, get_dataframe, \
save_to_db, get_template, check_project, get_existing_checklist, truncate_checklist, \
save_to_db_existing, get_auth, create_gantt_tasks, fetch_data, \
insert_to_project_auth_table, create_project_checklist_table_new, \
autofill_table, insert_to_autofill

from database import get_files_info2

#%%
os.chdir(r"C:\Users\administrator\Desktop\Authority Tracker Dashboard New")

# server = '192.168.6.16'
# username = 'arch'
# password = '@rchcorp$uiltIN@@'
# driver = '{ODBC Driver 17 for SQL Server}'


# the top one is giving error, modifying it without function call fetch_data
server = '192.168.6.16'
database = 'Archcorp_'
username = 'arch'
password = '@rchcorp$uiltIN@@'

# connection_string = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password};MultipleActiveResultSets=true"


# ''' Create a connection to the database'''
# conn = pyodbc.connect(connection_string)

# query = "SELECT CONCAT(ProjectCode, ' - ', ProjectName) AS [Project Name] FROM projects WHERE projectState = 0"
    
driver = '{ODBC Driver 17 for SQL Server}'
project_names = fetch_data(server, username, password, driver)

'''# No function call (fetch_data)'''

# project_names = pd.read_sql(query, conn)

#%% 
app = Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

#%% 
app.layout = html.Div([
    
    html.H1('Authority Requirements Dashboard', style={'textAlign': 'center'}),
   
    html.Div(children = [
        # 1. Dropdowns

        html.Div(children = [

            # 1.a. Project Dropdown
            html.Div([
                html.H5('Project:', style={'marginLeft': '30px', 'marginRight': '10px', 'display': 'inline-block'}),
                dcc.Dropdown(options=project_names['Project Name'].tolist(),
                            placeholder='Select a project.',
                            id='project-dropdown',
                            style={'width': '100%',
                                    'margin': '10px',
                                    'verticalAlign': 'middle'
                                    }
                            ),
                    ], style={'display': 'inline-flex', 'flexFlow': 'row nowrap', 'alignItems': 'center', 'width': '35%'}
                    ),
            
            # 1.b. Authority Dropdown
            html.Div([
                html.H5('Authority:', style={'marginLeft': '30px', 'display': 'inline-block'}),
                dcc.Dropdown(options=['Dubai Development Authority',
                                    'Dubai Municipality',
                                    'Trakhees',
                                    'Dubai South',
                                    'Dubai Silicon Oasis',
                                    'Sharjah Municipality',
                                    'Abu Dhabi Municipality',
                                    'Al Ain Municipality',
                                    'DDA and EMAAR'
                                    ],
                            placeholder='Select an authority.',
                            id='authority-dropdown',
                            style={'width': '100%',
                                    'margin': '10px',
                                    'verticalAlign': 'middle'
                                    },
                            disabled=False
                            )
                    ], style={'display': 'inline-flex', 'flexFlow': 'row nowrap', 'alignItems': 'center', 'width': '30%'}
                    )
        ],
        style={'display': 'flex', 'flexFlow': 'row nowrap', 'justifyContent': 'center'}
        ),
        
        html.Div(
            id = 'autofill-table-container',
            children = [autofill_table()],
            style={'display': 'none'}
        ),

        # 3. Collapse buttons and checklist tables
        html.Div([
           
            # 2. Button to save changes 
        
            html.Div(
                [
                    dbc.Button(
                        'Generate Submissions Checklist',
                        id = 'generate-checklist-button',
                        color = 'primary',
                        n_clicks = 0,
                        outline = True,
                        size = 'lg',
                        className = 'ml-auto',
                        style = {'marginRight': '10px','display': 'none'}
                    ),
                    dbc.Button(
                        'Save Changes',
                        id = 'save-changes-button',
                        color = 'primary',
                        n_clicks = 0,
                        outline = True,
                        size = 'lg',
                        className='ml-auto',
                        style={'marginRight': '10px', 'display': 'none'},
                    ),

                    dbc.Modal([
                        dbc.ModalBody("Changes saved successfully!"),
                        dbc.ModalFooter(
                            dbc.Button(
                                "Close", id = "close", className = "ms-auto", n_clicks = 0
                            )
                        )
                    ],
                    id="modal",
                    is_open=False)
                ],
                
                #style={'margin': '10px', 'display': 'flex', 'justifyContent': 'flex-end'}
                style = {'display': 'flex', 'flexFlow': 'row nowrap', 'justifyContent': 'center', 'alignItems': 'center'}

        ),
            
            html.Div(id='output_info3'),
        
            ## Checklist tables

            dbc.Row(
                [                    
                    dbc.Collapse(
                        html.Div(id='auth-table-container',
                                 style={
                                    #  'display': 'flex',
                                    #  'justify-content': 'center',
                                     'align-items': 'center',
                                     'margin': '15px 15px',
                                     'width': '98%'
                                     }),
                        #dbc.Card(dbc.CardBody('INSERT AUTHORITY SUBMISSIONS HERE')),
                        id = 'auth-placeholder',
                        is_open = True
                    ),
                ],
                className = 'collapses'
            ),
        ],
        style={'width': '100%', 'font-size': '16px', 'padding': '8px'}
        )
    ],
#style = {'display': 'flex', 'flexFlow': 'column nowrap', 'justifyContent': 'center', 'alignItems': 'center'}
    )
]
)

#%%
@app.callback(
    Output('authority-dropdown', 'value'),
    Output('authority-dropdown', 'disabled'),
    Output('generate-checklist-button', 'style'),
    Output('autofill-table-container', 'style'),
    Output('auth-table-container', 'children'),
    Output('save-changes-button', 'style'),
    Input('generate-checklist-button', 'n_clicks'),
    Input('project-dropdown', 'value'),
    State('authority-dropdown', 'value'),
    State('autofill-table-container', 'children'),
    prevent_initial_call=True
)
def update_or_display_checklist(generate_checklist_clicks, project_name, authority_name, autofill_data):
    ctx = dash.callback_context
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else None

    # If the generate-checklist-button was clicked
    if triggered_id == 'generate-checklist-button':
        proj_exists = check_project(project_name)
        
        if proj_exists:
            auth_name = get_auth(project_name)
            return auth_name, True, {'display': 'none'}, {'display': 'none'}, None, {'marginRight': '10px'}
        
        else:
            # Insert a row to the Autofill table in the database
            insert_to_autofill(autofill_data)
            # Insert a row to the ProjectAuthorityChecklist table
            insert_to_project_auth_table(project_name, authority_name)

            # Create an empty checklist table for the project - using the template_01 table of the selected authority
            create_project_checklist_table_new(project_name, authority_name)

            # Call abhishek's autofill which will overwrite the templates column in the DB!!!
            
            server = '192.168.6.16'
            database = 'ArchAuthorityTracker'
            username = 'arch'
            password = '@rchcorp$uiltIN@@'
            
            connection_string = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password};MultipleActiveResultSets=true"
            
            conn = pyodbc.connect(connection_string)
            
            cursor = conn.cursor()
            
            query = "SELECT * FROM Autofill"

            # Execute the query and fetch the results into a dataframe
            df = pd.read_sql(query, conn)

            query_authority_check_list = "SELECT TOP 1 * FROM ProjectAuthorityChecklist ORDER BY CreatedDateTime DESC"
            
            
            # Execute the query and fetch the results into a dataframe
            df_authority_check_list = pd.read_sql(query_authority_check_list, conn)
            
            print(df)
            
            
            flag = 0
            for i in range(len(df)):
                if int(df['Project Code'][i]) == int(df_authority_check_list['ProjectCode'][0]):
                    print(df['Project Code'][i], "*********", df_authority_check_list['ProjectCode'][0])
                    df = df.iloc[[i]]
                    df.reset_index(drop=True, inplace=True)
                    print("*********************************************************")
                    print(df)
                    flag = 1
                    break
            
            # if flag == 0:
                # return 0
                
                

            query_check_list_name = "SELECT * FROM " + df_authority_check_list['ChecklistName'][0]
            df_check_list_name = pd.read_sql(query_check_list_name, conn)
            
            
            
            folder_path = r"C:\Users\administrator\Downloads\final downloaded forms"
            # folder_path = r"C:\Users\abhishek.singh\Downloads\final downloaded forms"
            for i in range(len(df_check_list_name)):
                if df_check_list_name['Template'][i] != '':
                    authority_id = df_check_list_name['AuthorityID'][i]
                    prerequisite_id = df_check_list_name['PrerequisiteID'][i]
                    get_files_info2(folder_path, authority_id, prerequisite_id, df)
            
            

            for i in range(len(df_check_list_name)):
                if df_check_list_name['Template'][i] != '':
                    authority_id = df_check_list_name['AuthorityID'][i]
                    prerequisite_id = df_check_list_name['PrerequisiteID'][i]
                    for root, dirs, files in os.walk(r"C:\Users\administrator\Desktop\YashK\ArchcorpAISearch_DBC_ADBC_CIVIL\AISearch_V5_CompareFeature\assets"):
                    # for root, dirs, files in os.walk(r"C:\Users\abhishek.singh\Downloads\modified_forms"):
                            for file_name in files:
                                file_path = os.path.join(root, file_name)
                                file_name, file_ext = os.path.splitext(file_name)
                    #             print("File Name:", file_name)
                    #             print("Extension:", file_ext)
                    #             print("Path:", file_path)
                                folder_name = file_path.split('\\')
                                folder_name = folder_name[-2]
                                print(folder_name)
                                num = folder_name.split(' ')
                                if len(num) > 1:
                                    folder_number = folder_name.split(' ')[1]
                                    if int(folder_number) == int(authority_id):
                                        file_id = file_name.split(" ")[0]
                                        if int(file_id) == int(prerequisite_id):
                                            intermediate_path = df['Project'][0].replace(" ", "_") + "/" + folder_name + "/" + file_name + file_ext
                                            final_path = "http://192.168.6.238:8050/assets/" + intermediate_path
                                            final_path = final_path.replace("'", "''")
                                            sql_query = f"""
                                                            UPDATE {df_authority_check_list['ChecklistName'][0]}
                                                            SET Template = '{final_path}'
                                                            WHERE AuthorityID = {authority_id} AND PrerequisiteID = {prerequisite_id}
                                                        """
                                            cursor = conn.cursor()
                                            cursor.execute(sql_query)
                                            conn.commit()

            # Update the authority id
            cursor = conn.cursor()
            sql_query_01 = f"UPDATE {df_authority_check_list['ChecklistName'][0]} SET AuthorityID = 0 WHERE AuthorityID = ''"
            cursor.execute(sql_query_01)
            conn.commit()

            # Update the PrerequisiteID
            cursor = conn.cursor()
            sql_query_02 = f"UPDATE {df_authority_check_list['ChecklistName'][0]} SET PrerequisiteID = '' WHERE AuthorityID = 0"
            cursor.execute(sql_query_02)
            conn.commit()            

            conn.commit()
            cursor.close()
            conn.close()

            
            # Load the auto-filled df
            df = get_existing_checklist(project_name)
            df_01 = insert_collapsible_buttons(df)
            auth_df_table = create_html_table(df_01)

            #df.to_csv('NEW-DF-FOR-GANTT.csv')

            # Insert to gantt tasks
            create_gantt_tasks(df, project_name)

            return authority_name, True, {'display': 'none'}, {'display': 'none'}, auth_df_table, {'marginRight': '10px'}
            #return authority_name, True, generate_checklist_style, autofill_style, auth_df_table, {'marginRight': '10px'}


    # If the project-dropdown value changed (no button click)
    elif triggered_id == 'project-dropdown':
        proj_exists = check_project(project_name)
        if proj_exists:
            auth_name = get_auth(project_name)
            auth_dropdown_disabled = True
            generate_checklist_style = {'display': 'none'}
            autofill_style = {'display': 'none'}

            df = get_existing_checklist(project_name)
            df = insert_collapsible_buttons(df)
            auth_df_table = create_html_table(df)

            return auth_name, auth_dropdown_disabled, generate_checklist_style, autofill_style,auth_df_table, {'marginRight': '10px'}
        else:
            auth_dropdown_disabled = False
            generate_checklist_style = {'marginRight': '10px'}
            autofill_style = {'marginRight': '10px'}
            return None, auth_dropdown_disabled, generate_checklist_style, autofill_style,None, {'display': 'none'}

    return dash.no_update  # If none of the inputs triggered the callback, return no_update for all outputs
       
                            
#%%
# Expand the contents per Stage
@app.callback(
    Output({'type': 'Pre-Concept-source', 'index': ALL}, 'hidden'),
    Input('Pre-Concept-button', 'n_clicks'),
    [State('auth-table-container', 'children')],
    prevent_initial_call = True
)
def update_table_visibility(n_clicks, table_children):

    if (n_clicks is not None) and (n_clicks > 0):
        hidden_value = show_stage_sources('Pre-Concept', table_children, n_clicks)
        return hidden_value

#%%
@app.callback(
    Output({'type': 'Concept Design-source', 'index': ALL}, 'hidden'),
    Input('Concept Design-button', 'n_clicks'),
    [State('auth-table-container', 'children')],
    prevent_initial_call = True
)
def update_table_visibility(n_clicks, table_children):

    if (n_clicks is not None) and (n_clicks > 0):
        hidden_value = show_stage_sources('Concept Design', table_children, n_clicks)
        return hidden_value

#%%
@app.callback(
    Output({'type': 'Schematic Design-source', 'index': ALL}, 'hidden'),
    Input('Schematic Design-button', 'n_clicks'),
    [State('auth-table-container', 'children')],
    prevent_initial_call = True
)
def update_table_visibility(n_clicks, table_children):
    if (n_clicks is not None) and (n_clicks > 0):
        hidden_value = show_stage_sources('Schematic Design', table_children, n_clicks)
        return hidden_value

#%%
@app.callback(
    Output({'type': 'Detailed Design-source', 'index': ALL}, 'hidden'),
    Input('Detailed Design-button', 'n_clicks'),
    [State('auth-table-container', 'children')],
    prevent_initial_call = True
)
def update_table_visibility(n_clicks, table_children):

    if (n_clicks is not None) and (n_clicks > 0):

        hidden_value = show_stage_sources('Detailed Design', table_children, n_clicks)
        return hidden_value
    
#%%
@app.callback(
    Output({'type': 'Construction Stage-source', 'index': ALL}, 'hidden'),
    Input('Construction Stage-button', 'n_clicks'),
    [State('auth-table-container', 'children')],
    prevent_initial_call = True
)
def update_table_visibility(n_clicks, table_children):
    if (n_clicks is not None) and (n_clicks > 0):
        hidden_value = show_stage_sources('Construction Stage', table_children, n_clicks)
        return hidden_value
    
#%%
@app.callback(
    Output({'type': 'Pre-Concept-document', 'index':ALL}, 'hidden'),
    [Input({'type': 'Pre-Concept-source-button', 'index': ALL}, 'n_clicks')],
    [State({'type': 'Pre-Concept'+ '-source', 'index': ALL}, 'id')],
    [State('auth-table-container', 'children')],
    prevent_initial_call = True
)
def update_table_visibility(n_clicks, sources,table_children):
    if (n_clicks is not None) and any(click != 0 for click in n_clicks):
        authority_sources = [item['index'].split('-')[-1] for item in sources]
        hidden_value_all = []
        for i in range(len(authority_sources)):
            hidden_value = show_sources_docs('Pre-Concept', authority_sources[i],table_children, n_clicks[i])
            hidden_value_all.append(hidden_value)

        hidden_value_all = [item for sublist in hidden_value_all for item in sublist]
        return hidden_value_all

@app.callback(
    Output({'type': 'Concept Design-document', 'index':ALL}, 'hidden'),
    [Input({'type': 'Concept Design-source-button', 'index': ALL}, 'n_clicks')],
    [State({'type': 'Concept Design'+ '-source', 'index': ALL}, 'id')],
    [State('auth-table-container', 'children')],
   # [State({'type': 'Concept Design-document', 'index':ALL}, 'hidden')],
    prevent_initial_call=True
)
def update_table_visibility(n_clicks, sources,table_children):  
    if (n_clicks is not None) and any(click != 0 for click in n_clicks):
        authority_sources = [item['index'].split('-')[-1] for item in sources]
        print(authority_sources)
        hidden_value_all = []
        for i in range(len(authority_sources)):
            hidden_value = show_sources_docs('Concept Design', authority_sources[i],table_children, n_clicks[i])
            hidden_value_all.append(hidden_value)

        hidden_value_all = [item for sublist in hidden_value_all for item in sublist]
        return hidden_value_all

@app.callback(
    Output({'type': 'Schematic Design-document', 'index':ALL}, 'hidden'),
    [Input({'type': 'Schematic Design-source-button', 'index': ALL}, 'n_clicks')],
    [State({'type': 'Schematic Design'+ '-source', 'index': ALL}, 'id')],
    [State('auth-table-container', 'children')],
    prevent_initial_call = True
)
def update_table_visibility(n_clicks, sources,table_children):
    
    if (n_clicks is not None) and any(click != 0 for click in n_clicks):
        authority_sources = [item['index'].split('-')[-1] for item in sources]
        hidden_value_all = []
        for i in range(len(authority_sources)):
            hidden_value = show_sources_docs('Schematic Design', authority_sources[i],table_children, n_clicks[i])
            hidden_value_all.append(hidden_value)

        hidden_value_all = [item for sublist in hidden_value_all for item in sublist]
        return hidden_value_all

@app.callback(
    Output({'type': 'Detailed Design-document', 'index':ALL}, 'hidden'),
    [Input({'type': 'Detailed Design-source-button', 'index': ALL}, 'n_clicks')],
    [State({'type': 'Detailed Design'+ '-source', 'index': ALL}, 'id')],
    [State('auth-table-container', 'children')],
    prevent_initial_call = True
)
def update_table_visibility(n_clicks, sources,table_children):
   
    if (n_clicks is not None) and any(click != 0 for click in n_clicks):
        authority_sources = [item['index'].split('-')[-1] for item in sources]
        hidden_value_all = []
        for i in range(len(authority_sources)):
            hidden_value = show_sources_docs('Detailed Design', authority_sources[i],table_children, n_clicks[i])
            hidden_value_all.append(hidden_value)

        hidden_value_all = [item for sublist in hidden_value_all for item in sublist]
        return hidden_value_all
    
@app.callback(
    Output({'type': 'Construction Stage-document', 'index':ALL}, 'hidden'),
    [Input({'type': 'Construction Stage-source-button', 'index': ALL}, 'n_clicks')],
    [State({'type': 'Construction Stage'+ '-source', 'index': ALL}, 'id')],
    [State('auth-table-container', 'children')],
    prevent_initial_call = True
)
def update_table_visibility(n_clicks, sources,table_children):
        
    if (n_clicks is not None) and any(click != 0 for click in n_clicks):
        authority_sources = [item['index'].split('-')[-1] for item in sources]
        hidden_value_all = []
        for i in range(len(authority_sources)):
            hidden_value = show_sources_docs('Construction Stage', authority_sources[i],table_children, n_clicks[i])
            hidden_value_all.append(hidden_value)

        hidden_value_all = [item for sublist in hidden_value_all for item in sublist]
        return hidden_value_all

#%%
@app.callback(
    Output({'type': 'Pre-Concept--prerequisite', 'index': ALL}, 'hidden'),
    #Output('sample-container', 'children'),
    [Input({'type': 'Pre-Concept-document-button', 'index': ALL}, 'n_clicks')],
    [State({'type': 'Pre-Concept' + '-document', 'index': ALL}, 'id')],
    [State('auth-table-container', 'children')],
    [State({'type': 'Pre-Concept--prerequisite', 'index': ALL}, 'hidden')],
    prevent_initial_call = True
)
def update_table_visibility(n_clicks, document_index, table_children, sample_output):
    
    if (n_clicks is not None) and any(click != 0 for click in n_clicks):
        documents = [item['index'].split('_')[-1] for item in document_index]
        sources = [item['index'].split('_')[1] for item in document_index]
        hidden_value_all = []

        for i in range(len(document_index)):
            hidden_value = show_docs_prerequisites(sources[i],documents[i],table_children, n_clicks[i])
            hidden_value_all.append(hidden_value)

        hidden_value_all = [item for sublist in hidden_value_all for item in sublist]
        return hidden_value_all

@app.callback(
    Output({'type': 'Concept Design--prerequisite', 'index': ALL}, 'hidden'),
    #Output('sample-container', 'children'),
    [Input({'type': 'Concept Design-document-button', 'index': ALL}, 'n_clicks')],
    [State({'type': 'Concept Design' + '-document', 'index': ALL}, 'id')],
    [State('auth-table-container', 'children')],
    [State({'type': 'Concept Design--prerequisite', 'index': ALL}, 'hidden')],
    prevent_initial_call = True
)
def update_table_visibility(n_clicks, document_index, table_children, sample_output):
   
    if (n_clicks is not None) and any(click != 0 for click in n_clicks):
        
        documents = [item['index'].split('_')[-1] for item in document_index]
        sources = [item['index'].split('_')[1] for item in document_index]
        hidden_value_all = []

        for i in range(len(document_index)):
            hidden_value = show_docs_prerequisites(sources[i],documents[i],table_children, n_clicks[i])
            hidden_value_all.append(hidden_value)

        hidden_value_all = [item for sublist in hidden_value_all for item in sublist]
        return hidden_value_all

@app.callback(
    Output({'type': 'Schematic Design--prerequisite', 'index': ALL}, 'hidden'),
    #Output('sample-container', 'children'),
    [Input({'type': 'Schematic Design-document-button', 'index': ALL}, 'n_clicks')],
    [State({'type': 'Schematic Design' + '-document', 'index': ALL}, 'id')],
    [State('auth-table-container', 'children')],
    [State({'type': 'Schematic Design--prerequisite', 'index': ALL}, 'hidden')],
    prevent_initial_call = True
)
def update_table_visibility(n_clicks, document_index, table_children, sample_output):
    
    if (n_clicks is not None) and any(click != 0 for click in n_clicks):
        #print(document_index)
        documents = [item['index'].split('_')[-1] for item in document_index]
        sources = [item['index'].split('_')[1] for item in document_index]
        hidden_value_all = []

        for i in range(len(document_index)):
            hidden_value = show_docs_prerequisites(sources[i],documents[i],table_children, n_clicks[i])
            hidden_value_all.append(hidden_value)

        #print(hidden_value_all)
        hidden_value_all = [item for sublist in hidden_value_all for item in sublist]
        return hidden_value_all
    
@app.callback(
    Output({'type': 'Detailed Design--prerequisite', 'index': ALL}, 'hidden'),
    #Output('sample-container', 'children'),
    [Input({'type': 'Detailed Design-document-button', 'index': ALL}, 'n_clicks')],
    [State({'type': 'Detailed Design' + '-document', 'index': ALL}, 'id')],
    [State('auth-table-container', 'children')],
    [State({'type': 'Detailed Design--prerequisite', 'index': ALL}, 'hidden')],
    prevent_initial_call = True
)
def update_table_visibility(n_clicks, document_index, table_children, sample_output):
       
    if (n_clicks is not None) and any(click != 0 for click in n_clicks):
        #print(document_index)
        documents = [item['index'].split('_')[-1] for item in document_index]
        sources = [item['index'].split('_')[1] for item in document_index]
        hidden_value_all = []

        for i in range(len(document_index)):
            hidden_value = show_docs_prerequisites(sources[i],documents[i],table_children, n_clicks[i])
            hidden_value_all.append(hidden_value)

        #print(hidden_value_all)
        hidden_value_all = [item for sublist in hidden_value_all for item in sublist]
        return hidden_value_all

#%%

#%%
# Callbacks to calculate the documents' percentage completion
@app.callback(
    Output({'type': 'submission-perc', 'index':ALL}, 'value'),
    #Output('sample-container', 'children'),
    [Input({'type': 'checkboxes', 'index': ALL}, 'value')],
    [State({'type': 'checkboxes', 'index': ALL}, 'id')],
    [State({'type': 'submission-perc', 'index':ALL}, 'id')],
    [State({'type': 'submission-perc', 'index':ALL}, 'value')],
    prevent_initial_call = True
)
def calculate_document_completion(selected_prerequisites, prereq_indexes, submissions_index, sample_output):
  
    if any(element is not None for element in selected_prerequisites):

        submissions = []
        for i in range(len(submissions_index)):
            submission_name = submissions_index[i]['index'].split('_')[-1]
            submissions.append(submission_name)
        
        prereqs = []
        for i in range(len(prereq_indexes)):
            prereqs_name = prereq_indexes[i]['index']
            prereqs.append(prereqs_name)

        total_prereqs = count_occurrences(submissions, prereqs)
        
        selected_prerequisites = [x for x in selected_prerequisites if x is not None]
        selected_prerequisites = [item for sublist in selected_prerequisites for item in sublist]

        selected_prereqs = count_occurrences(submissions, selected_prerequisites)
        
        perc_completion = [((num / denom) * 100) if denom != 0 else '0.0' for num, denom in zip(selected_prereqs, total_prereqs)]
        perc_completion = [str(item) + '%' for item in perc_completion]
        
        output = ['Complete' if item == '100.0%' else 'Incomplete' for item in perc_completion]
        return output

#%%
# Update the stage completion
@app.callback(
         Output({'type': 'stage-perc', 'index':ALL}, 'value'),
         #Output('sample-container', 'value'),
         [Input({'type': 'submission-perc', 'index':ALL}, 'value')],
         [State({'type': 'submission-perc', 'index':ALL}, 'id')],
         [State({'type': 'stage-perc', 'index':ALL}, 'value')],
         [State({'type': 'stage-perc', 'index':ALL}, 'id')],
         prevent_initial_call = True
)
def update_stage_completion(submission_perc, submission_id, sample_output, sample_output_id):

    print(submission_perc)
    #print(submission_id)
    #print(sample_output)
    #print(sample_output_id)

    stages = [item['index'].split('_')[0] for item in sample_output_id]

    stages_count = {}

    for stage in stages:
        stage_count = 0
        for submission in submission_id:
            if stage in submission['index']:
                stage_count +=1
        stages_count[stage] = stage_count

    print(stages_count)

    output = []

    stage_indexes_dict = {}
    total_count = 0

    for stage, count in stages_count.items():
        start = total_count
        end = total_count + count
        stage_indexes_dict[stage] = list(range(start, end))
        total_count += count

    # Print the new dictionary
    print(stage_indexes_dict)

    for stage in stages:
        stage_subset = submission_perc[stage_indexes_dict[stage][0]: stage_indexes_dict[stage][-1]+1]
        complete_num = stage_subset.count('Complete')
        stage_total = stages_count[stage]
        perc_complete = complete_num/stage_total

        if perc_complete == 1.0:
            output.append('Complete')
        else:
            output.append('Incomplete')

    print(output)


    return output    

#%%

@app.callback(
    Output("modal", "is_open"),
    Output('project-dropdown', 'options'),
    Output('project-dropdown', 'value'),
    [Input('save-changes-button', 'n_clicks'), Input("close", "n_clicks")],
    [State("modal", "is_open")],
    State('project-dropdown', 'value'),
    State('auth-table-container', 'children'),
    State('authority-dropdown', 'value'),
    prevent_initial_call = True
)
def save_table(save_clicks, close_clicks, is_open, project_name, table_children, authority_name):
    ctx = dash.callback_context
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else None

    if triggered_id == 'save-changes-button':
        if project_name is not None:
            proj_exists = check_project(project_name)

            if proj_exists:
                checklist_name = truncate_checklist(project_name)
                print(checklist_name)
                filled_df = get_dataframe(table_children)
                save_to_db_existing(checklist_name, filled_df)
                project_names = fetch_data(server, username, password, driver)
                project_options = project_names['Project Name'].tolist()
                project_value = project_name

        return True, project_options, project_value

    if triggered_id == 'close':
        return False, dash.no_update, dash.no_update

    return is_open, dash.no_update, dash.no_update

#%%
if __name__ == '__main__':
    # app.run_server()
    app.run_server(host = '192.168.6.238', port = 8056,debug=False)
    
