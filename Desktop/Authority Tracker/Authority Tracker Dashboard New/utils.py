#%%
import dash_bootstrap_components as dbc
import pandas as pd
from dash import html, Dash, dcc
import numpy as np
from datetime import datetime

import pyodbc

from sqlalchemy.engine import URL
from sqlalchemy import create_engine
from sqlalchemy.sql import text as sa_text

from sqlalchemy.orm import sessionmaker


#%%
server = '192.168.6.16'
username = 'arch'
password = '@rchcorp$uiltIN@@'
driver = '{ODBC Driver 17 for SQL Server}'

#%%
# Create an html table
def create_html_table(df):

    df2 = df.copy()
    df2 = df.drop(columns = ['Stage', 'Source', 'Document', 'Prerequisites', 'Template'])
    df2 = df2.rename(columns = {'Stage_final': 'Stage',
                                'Source_final': 'Authority',
                                'Document_final': 'Required Submission',
                                'Prerequisites_checkbox': 'Prerequisites',
                                'Document_link': 'Link to the Document',
                                'Template_Link': 'Template'
                                })
    #print(df2.columns.tolist())
    # Table Headers
    header_names = []
    for col in df2.columns.tolist():
        if col == 'Stage':
            header_names.append(html.Th(col, style = {'width': '10%', 'text-align': 'center'}))
        elif col == 'Authority':
            header_names.append(html.Th(col, style = {'width': '5%', 'text-align': 'center'}))
        elif col == 'Required Submission':
            header_names.append(html.Th(col, style = {'width': '15%', 'text-align': 'center'}))
        elif col == 'Prerequisites':
            header_names.append(html.Th(col, style = {'width': '15%', 'text-align': 'center'}))
        elif col == 'Filetype':
            header_names.append(html.Th(col, style = {'width': '2%', 'text-align': 'center'}))
        elif col == 'Expand Stage':
            header_names.append(html.Th(col, style = {'width': '0.5%', 'text-align': 'center'}))
        elif col == 'Expand Source':
            header_names.append(html.Th(col, style = {'width': '0.5%', 'text-align': 'center'}))
        elif col == 'Expand Docs':
            header_names.append(html.Th(col, style = {'width': '0.5%', 'text-align': 'center'}))
        elif col == 'Link to the Document':
            header_names.append(html.Th(col, style = {'width': '20%', 'text-align': 'center'}))
        elif col == 'Remarks':
            header_names.append(html.Th(col, style = {'width': '25%', 'text-align': 'center'}))
        elif col == 'Template':
            header_names.append(html.Th(col, style = {'width': '15%', 'text-align': 'center'}))
    table_header = [html.Thead(html.Tr(header_names))]
    
    #stage_indexes = df[(df['Source'].isna())].index.tolist()
    #stage_source_indexes = df[(~df['Source'].isna())&(df['Document'].isna()) & (df['Prerequisites'].isna())].index.tolist()
    #documents_indexes = df[(~df['Document'].isna())&(df['Prerequisites'].isna()) & (df['Filetype'].isna())].index.tolist()
    
    stage_indexes = df[~df['Stage_final'].isna()].index.tolist()
    stage_source_indexes = df[~df['Source_final'].isna()].index.tolist()
    documents_indexes = df[~df['Document_final'].isna()].index.tolist()
    prereq_indexes = df[(~df['Prerequisites'].isna())].index.tolist()
    #print(len(prereq_indexes))

    # Table Rows
    table_data = []
    
    for row in range(len(df2)):
        row_data = []
        
        for col in df2.columns.tolist():
                row_data.append(html.Td(df2.loc[row, col]))
            
        if row in stage_indexes:
            row_i = html.Tr(
                className = 'stage',
                children = row_data,
                hidden = False            
            )
        
        elif row in stage_source_indexes:
            row_i = html.Tr(
                 className = df.loc[row, 'Stage']+ '-source' ,
                 id = {'type': df.loc[row, 'Stage'] +'-source',
                        'index': df.loc[row, 'Stage']+'-'+df.loc[row, 'Source']},
                 children = row_data,
                 hidden = True            
            )

        elif row in documents_indexes:
            row_i = html.Tr(
                className = df.loc[row, 'Stage']+ df.loc[row, 'Source']+'-document',
                id = {'type': df.loc[row, 'Stage'] + '-document',
                       'index': df.loc[row, 'Stage'] +'_'+ df.loc[row, 'Source']+ '_' +df.loc[row, 'Document']},
                children = row_data,
                hidden = True
            )

        elif row in prereq_indexes:
            row_i = html.Tr(
                className = df.loc[row, 'Stage']+ df.loc[row, 'Source']+df.loc[row, 'Document']+'--prerequisite',
                id = {'type': df.loc[row, 'Stage'] + '--prerequisite',
                      'index': df.loc[row, 'Stage']+'_' +df.loc[row, 'Source']+'_'+df.loc[row, 'Document']+'_'+df.loc[row, 'Prerequisites']+'--prerequisite'},
                children = row_data,
                hidden = True
            )

        table_data.append(row_i)
    
    table_body = [html.Tbody(table_data)]
    
    table = dbc.Table(table_header + table_body,
                       striped=False,
                       bordered=True,
                       hover=True,
                       responsive=True,
                       style = {'width': '100%',
                                'columnDefs': [
                                    {'width': '100px', 'targets': 0},
                                    {'width': '200px', 'targets': 1},
                                    {'width': '300px', 'targets': 2}]
                                })
    
    
    return table

# Add interactive buttons
def insert_collapsible_buttons(df):
    
    #stage_indexes = df[(df['Source'].isna())].index.tolist()
    #stage_source_indexes = df[(~df['Source'].isna())&(df['Document'].isna()) & (df['Prerequisites'].isna())].index.tolist()
    #documents_indexes = df[(~df['Document'].isna())&(df['Prerequisites'].isna()) & (df['Filetype'].isna())].index.tolist()

    # Create Stage_final, Source_final, Document_final

    stage_indexes = df[~df['Stage_final'].isna()].index.tolist()
    stage_source_indexes = df[~df['Source_final'].isna()].index.tolist()
    documents_indexes = df[~df['Document_final'].isna()].index.tolist()
    prereq_indexes = df[(~df['Prerequisites'].isna())].index.tolist()

    # print(df.columns)

    # print(len(stage_indexes))
    # print(len(stage_source_indexes))
    # print(len(documents_indexes))
    # print(len(prereq_indexes))

    # print(len(df))

    df_dict = {}

    for col in df.columns.tolist():
        df_dict[col] = df[col].to_list()

    collapse_col = []
    collapse_source_col = []
    collapse_docs_col = []
    checklist_col = []
    template_link = []
    document_link = []
    remarks_col = []
    
    print(df.columns)
    for i in range(len(df)):
        # Stage
        if i in stage_indexes:
            #print(df.loc[i, 'Stage']+'-button')
            collapse_col.append(
                    dbc.Button('▼',
                               color='light',
                               className = 'stage-collapse',
                               id= df.loc[i, 'Stage']+'-button',                                   
                               n_clicks=0,
                               outline = False))
                               
            template_link.append('')

        else:
            collapse_col.append('')
        
        # Authority
        if i in stage_source_indexes:
            collapse_source_col.append(
                    dbc.Button('▼',
                               color='light',
                               className = 'stage-source-collapse',
                               id={'type': df.loc[i, 'Stage']+'-source-button',
                                    'index': df.loc[i, 'Stage']+'-'+df.loc[i, 'Source']+'-button'},                                   
                               n_clicks=0,
                               outline = False))
                               
            template_link.append('')

        else:
            collapse_source_col.append('')
        
        # Required Submission
        if (i in documents_indexes) and (len(df[df['Document']==df.loc[i, 'Document']]) > 0):
            collapse_docs_col.append(
                        dbc.Button('▼',
                                color='light',
                                className = 'documents-collapse',
                                id={'type': df.loc[i, 'Stage']+'-document-button',
                                        'index': df.loc[i, 'Stage']+'-'+df.loc[i, 'Source']+'-'+df.loc[i, 'Document']+'-button'},                                   
                                n_clicks=0,
                                outline = False))
                                
            if not pd.isna(df.loc[i, 'Template']):
                template_link.append(dbc.Input(id = {'type': 'template',
                                     'index': df.loc[i, 'Document']+'-template'}, 
                             type="input", style={'width': '100%'},
                             value = df.loc[i, 'Template'])
                             #value=html.A(df.loc[i, 'Template'], href=df.loc[i, 'Template'])
                             )

                template_link[-1] = html.A(df.loc[i, 'Document'], href=df.loc[i, 'Template'], target='_blank')
            else:
                template_link.append(np.nan)        

                                
        else:
            collapse_docs_col.append('')
 
        
        if i in prereq_indexes:
            # new project - no existing checklist
            if 'IsComplete' not in df.columns:
                checklist_col.append(dbc.Checklist(
                    id = {'type': 'checkboxes',
                        'index': str(df.loc[i, 'Stage'])+'_' +str(df.loc[i, 'Source'])+'_'+str(df.loc[i, 'Document'])+'_'+str(df.loc[i, 'Prerequisites'])+'--prerequisite'},
                    options = [{'label': str(df.loc[i,'PrerequisiteID']) + '. ' + str(df.loc[i, 'Prerequisites']), 'value': str(df.loc[i, 'Stage']) + '_' + str(df.loc[i, 'Document']) + '_' + str(df.loc[i, 'Prerequisites']) + '--prerequisite'}],
                    label_checked_style = {'color': 'green'},
                    input_checked_style={'backgroundColor': '#0abd2d',
                                        'borderColor': '#0abd2d'}
                                    ))
            # existing
            else:
                if df.loc[i, 'IsComplete'] == 1:
                    checklist_col.append(dbc.Checklist(
                        id = {'type': 'checkboxes',
                            'index': str(df.loc[i, 'Stage'])+'_' +str(df.loc[i, 'Source'])+'_'+str(df.loc[i, 'Document'])+'_'+str(df.loc[i, 'Prerequisites'])+'--prerequisite'},
                        options = [{'label': str(df.loc[i,'PrerequisiteID']) + '. ' + str(df.loc[i, 'Prerequisites']), 'value': str(df.loc[i, 'Stage']) + '_' + str(df.loc[i, 'Document']) + '_' + str(df.loc[i, 'Prerequisites']) + '--prerequisite'}],
                        label_checked_style = {'color': 'green'},
                        input_checked_style={'backgroundColor': '#0abd2d',
                                            'borderColor': '#0abd2d'},
                        value = [str(df.loc[i, 'Stage']) + '_' + str(df.loc[i, 'Document']) + '_' + str(df.loc[i, 'Prerequisites']) + '--prerequisite']
                                        ))
                else:
                    checklist_col.append(dbc.Checklist(
                        id = {'type': 'checkboxes',
                            'index': str(df.loc[i, 'Stage'])+'_' +str(df.loc[i, 'Source'])+'_'+str(df.loc[i, 'Document'])+'_'+str(df.loc[i, 'Prerequisites'])+'--prerequisite'},
                        options = [{'label': str(df.loc[i,'PrerequisiteID']) + '. ' + str(df.loc[i, 'Prerequisites']), 'value': str(df.loc[i, 'Stage']) + '_' + str(df.loc[i, 'Document']) + '_' + str(df.loc[i, 'Prerequisites']) + '--prerequisite'}],
                        input_checked_style={'backgroundColor': '#0abd2d',
                                            'borderColor': '#0abd2d'}
                                        ))                    


            
            #print(template_link)
            # Add the link separately
            if not pd.isna(df.loc[i, 'Template']):
                template_link.append(dbc.Input(id = {'type': 'template',
                                     'index': df.loc[i, 'Prerequisites']+'-template'}, 
                             type="input", style={'width': '100%'},
                             value = df.loc[i, 'Template'])
                             #value=html.A(df.loc[i, 'Template'], href=df.loc[i, 'Template'])
                             )

                template_link[-1] = html.A(df.loc[i, 'Prerequisites'], href=df.loc[i, 'Template'], target='_blank')
            else:
                template_link.append(np.nan)


        else:
            #template_link.append('')

            if i in documents_indexes:
                if "IsComplete" not in df.columns:
                    checklist_col.append(
                        dcc.Dropdown(
                        options = [
                                    {'label': html.Span(['Incomplete'], style={'color': 'Red', 'font-size': 15, 'font-weight': 'bolder'})
                                    , 'value': 'Incomplete'},

                                    {'label': html.Span(['Complete'], style={'color': 'Green', 'font-size': 15, 'font-weight': 'bolder'})
                                    , 'value': 'Complete'},

                                    {'label': html.Span(['Not Applicable'], style={'color': 'Gray', 'font-size': 15, 'font-weight': 'bolder'})
                                    , 'value': 'Not Applicable'},
                                    
                                ],
                        id = {'type': 'submission-perc',
                            'index': str(df.loc[i, 'Stage'])+'_'+ str(df.loc[i, 'Source'])+'_'+str(df.loc[i, 'Document'])},
                        value = 'Incomplete'
                        )
                    )
                else:
                    #print(df.loc[i, 'IsComplete'])
                    if df.loc[i, 'IsComplete'] == 1:
                        checklist_col.append(
                            dcc.Dropdown(
                            options = [
                                        {'label': html.Span(['Incomplete'], style={'color': 'Red', 'font-size': 15, 'font-weight': 'bolder'})
                                        , 'value': 'Incomplete'},

                                        {'label': html.Span(['Complete'], style={'color': 'Green', 'font-size': 15, 'font-weight': 'bolder'})
                                        , 'value': 'Complete'},

                                        {'label': html.Span(['Not Applicable'], style={'color': 'Gray', 'font-size': 15, 'font-weight': 'bolder'})
                                    , 'value': 'Not Applicable'},
                                    ],
                            id = {'type': 'submission-perc',
                                'index': str(df.loc[i, 'Stage'])+'_'+ str(df.loc[i, 'Source'])+'_'+str(df.loc[i, 'Document'])},
                            value = 'Complete'
                            )
                        )
                    elif df.loc[i, 'IsComplete'] == 2:
                        checklist_col.append(
                            dcc.Dropdown(
                            options = [
                                        {'label': html.Span(['Incomplete'], style={'color': 'Red', 'font-size': 15, 'font-weight': 'bolder'})
                                        , 'value': 'Incomplete'},

                                        {'label': html.Span(['Complete'], style={'color': 'Green', 'font-size': 15, 'font-weight': 'bolder'})
                                        , 'value': 'Complete'},

                                         {'label': html.Span(['Not Applicable'], style={'color': 'Gray', 'font-size': 15, 'font-weight': 'bolder'})
                                    , 'value': 'Not Applicable'},
                                    ],
                            id = {'type': 'submission-perc',
                                'index': str(df.loc[i, 'Stage'])+'_'+ str(df.loc[i, 'Source'])+'_'+str(df.loc[i, 'Document'])},
                            value = 'Not Applicable'
                            )
                        )
                    else:
                        checklist_col.append(
                            dcc.Dropdown(
                            options = [
                                        {'label': html.Span(['Incomplete'], style={'color': 'Red', 'font-size': 15, 'font-weight': 'bolder'})
                                        , 'value': 'Incomplete'},

                                        {'label': html.Span(['Complete'], style={'color': 'Green', 'font-size': 15, 'font-weight': 'bolder'})
                                        , 'value': 'Complete'},

                                        {'label': html.Span(['Not Applicable'], style={'color': 'Gray', 'font-size': 15, 'font-weight': 'bolder'})
                                        , 'value': 'Not Applicable'},

                                    ],
                            id = {'type': 'submission-perc',
                                'index': str(df.loc[i, 'Stage'])+'_'+ str(df.loc[i, 'Source'])+'_'+str(df.loc[i, 'Document'])},
                            value = 'Incomplete'
                            )
                        )                        

            elif i in stage_indexes:
                # New project - no existing checklist
                if 'IsComplete' not in df.columns: 
                    checklist_col.append(
                        dcc.Dropdown(
                            options = [
                                        {'label': html.Span(['Incomplete'], style={'color': 'Red', 'font-size': 15, 'font-weight': 'bolder'})
                                        , 'value': 'Incomplete'},

                                        {'label': html.Span(['Complete'], style={'color': 'Green', 'font-size': 15, 'font-weight': 'bolder'})
                                        , 'value': 'Complete'}
                                    ],
                            id = {'type': 'stage-perc',
                                        'index': str(df.loc[i, 'Stage'])+ '_' +str(df.loc[i, 'Source'])+'_'+str(df.loc[i, 'Document'])},
                            value = 'Incomplete'
                                    )
                    )
                
                else:
                    if df.loc[i, 'IsComplete'] == 1:
                        checklist_col.append(
                            dcc.Dropdown(
                                options = [
                                            {'label': html.Span(['Incomplete'], style={'color': 'Red', 'font-size': 15, 'font-weight': 'bolder'})
                                            , 'value': 'Incomplete'},

                                            {'label': html.Span(['Complete'], style={'color': 'Green', 'font-size': 15, 'font-weight': 'bolder'})
                                            , 'value': 'Complete'}
                                        ],
                                id = {'type': 'stage-perc',
                                            'index': str(df.loc[i, 'Stage'])+ '_' +str(df.loc[i, 'Source'])+'_'+str(df.loc[i, 'Document'])},
                                value = 'Complete'
                                        )
                        )
                    else:
                        checklist_col.append(
                        dcc.Dropdown(
                            options = [
                                        {'label': html.Span(['Incomplete'], style={'color': 'Red', 'font-size': 15, 'font-weight': 'bolder'})
                                        , 'value': 'Incomplete'},

                                        {'label': html.Span(['Complete'], style={'color': 'Green', 'font-size': 15, 'font-weight': 'bolder'})
                                        , 'value': 'Complete'}
                                    ],
                            id = {'type': 'stage-perc',
                                        'index': str(df.loc[i, 'Stage'])+ '_' +str(df.loc[i, 'Source'])+'_'+str(df.loc[i, 'Document'])},
                            value = 'Incomplete'
                                    )
                    )

            elif i in stage_source_indexes:
                checklist_col.append('')



        if (i in documents_indexes) or ((i not in documents_indexes) and (i not in stage_indexes) and (i not in stage_source_indexes)):
            # Case when new project, no existing checklist
            if 'IsComplete' not in df.columns:
                if i in documents_indexes:
                    document_link.append(
                         dbc.Textarea(
                         id = {'type': 'document-link',
                                         'index': df.loc[i, 'Document']+'-document-link'},
                         style={'width': '100%', 'resize': 'both', 'overflow': 'auto'},
                         wrap= True
                         , value = ""
                         )                        
                    )


                    remarks_col.append(
                        dbc.Textarea(
                        id = {'type': 'remarks',
                              'index': df.loc[i, 'Document']+'-document-remarks'},
                        style={'width': '100%', 'resize': 'both', 'overflow': 'auto'},
                        wrap= True
                        )
                    )
                elif ((i not in documents_indexes) and (i not in stage_indexes) and (i not in stage_source_indexes)):
                    
                    document_link.append(
                         dbc.Textarea(
                         id = {'type': 'document-link',
                                         'index': str(df.loc[i, 'Prerequisites'])+'-prerequisite-link'},
                         style={'width': '100%', 'resize': 'both', 'overflow': 'auto'},
                         wrap= True
                         , value = ""
                         )                        
                    )


                    remarks_col.append(
                        dbc.Textarea(
                        id = {'type': 'remarks',
                              'index': str(df.loc[i, 'Prerequisites'])+'-prerequisite-remarks'},
                        style={'width': '100%', 'resize': 'both', 'overflow': 'auto'},
                        wrap= True
                        )
                    )


            else:
                # Case when there is an existing checklist
                if i in documents_indexes:

                    if not pd.isna(df.loc[i, 'FinalDocumentLink']):
                        document_link.append(
                            dbc.Textarea(
                            id = {'type': 'document-link',
                                            'index': df.loc[i, 'Document']+'-document-link'},
                            style={'width': '100%', 'resize': 'both', 'overflow': 'auto'},
                            wrap= True
                            ,value = df.loc[i, "FinalDocumentLink"]
                            )                        
                        )
                        
                    else:
                        document_link.append(
                            dbc.Textarea(
                            id = {'type': 'document-link',
                                            'index': df.loc[i, 'Document']+'-document-link'},
                            style={'width': '100%', 'resize': 'both', 'overflow': 'auto'},
                            wrap= True
                            , value = df.loc[i, 'FinalDocumentLink']
                            )                        
                        )

                        

                    remarks_col.append(
                        dbc.Textarea(
                        id = {'type': 'remarks',
                              'index': df.loc[i, 'Document']+'-document-remarks'},
                        style={'width': '100%', 'resize': 'both', 'overflow': 'auto'},
                        wrap= True
                        , value = df.loc[i, 'Remarks']
                        )
                    )


                elif ((i not in documents_indexes) and (i not in stage_indexes) and (i not in stage_source_indexes)):
                   
                    if not pd.isna(df.loc[i, 'FinalDocumentLink']):

                        document_link.append(

                            dbc.Textarea(
                            id = {'type': 'document-link',
                                 'index': str(df.loc[i, 'Prerequisites'])+'-prerequisite-link'},
                            style={'width': '100%', 'resize': 'both', 'overflow': 'auto'},
                            wrap= True,
                            value = df.loc[i, "FinalDocumentLink"]
                            )                        
                        )
                        
                    else:
                        document_link.append(
                            dbc.Textarea(
                            id = {'type': 'document-link',
                                  'index': str(df.loc[i, 'Prerequisites'])+'-prerequisite-link'},
                            style={'width': '100%', 'resize': 'both', 'overflow': 'auto'},
                            wrap= True
                            , value = df.loc[i, 'FinalDocumentLink']
                            )                        
                        )


                    remarks_col.append(
                        dbc.Textarea(
                        id = {'type': 'remarks',
                              'index': str(df.loc[i, 'Prerequisites'])+'-prerequisite-remarks'},
                        style={'width': '100%', 'resize': 'both', 'overflow': 'auto'},
                        wrap= True
                        , value = df.loc[i, 'Remarks']
                        )
                    )                    

        else:
            document_link.append('')
            remarks_col.append('')

    df_dict['Expand Stage'] = collapse_col
    df_dict['Expand Source'] = collapse_source_col
    df_dict['Expand Docs'] = collapse_docs_col
    df_dict['Prerequisites_checkbox'] = checklist_col
    df_dict['Document_link'] = document_link
    df_dict['Remarks'] = remarks_col
    df_dict['Template_Link'] = template_link
    
    print(len(collapse_col))
    print(len(collapse_source_col))
    print(len(collapse_docs_col))
    print(len(checklist_col))
    print(len(document_link))
    print(len(remarks_col))
    print(len(template_link))
    print(len(df))

    df = pd.DataFrame.from_dict(df_dict)
    df = df[['Stage_final','Stage', 'Expand Stage',
            'Source_final','Source','Expand Source',
            'Document_final', 'Document', 'Expand Docs',
            'Prerequisites','Prerequisites_checkbox', 'Filetype',
            'Template', 'Template_Link','Document_link', 'Remarks'
            ]]

    return df

### Functions to expand and collapse the rows

def show_stage_sources(stage, table_children, n_clicks):
    hidden_value = []
    for i,row in enumerate(table_children['props']['children'][1]['props']['children']):
        if (stage + '-source' in row['props']['className']):
            if n_clicks % 2 != 0:
                hidden_value.append(False)
            else:
                hidden_value.append(True)
    return hidden_value

def show_sources_docs(stage, source, table_children, n_clicks):
    hidden_value = []
    for i,row in enumerate(table_children['props']['children'][1]['props']['children']):
        if (stage + source +'-document' in row['props']['className']):
            if n_clicks % 2 != 0:
                hidden_value.append(False)
            else:
                hidden_value.append(True)

    return hidden_value

def show_docs_prerequisites(source,document, table_children, n_clicks):
    hidden_value = []
    for i,row in enumerate(table_children['props']['children'][1]['props']['children']):
        if (source + document +'--prerequisite' in row['props']['className']):
            if n_clicks % 2 != 0:
                hidden_value.append(False)
            else:
                hidden_value.append(True)

    return hidden_value

# Functions to calculate percentage completion
def count_occurrences(submissions_list, prereq_list):
    occurrences_list = []
    for submission in submissions_list:

        count = 0
        for prereq_string in prereq_list:

            if str(submission) in str(prereq_string):
                count = count + 1
        occurrences_list.append(count)
    return occurrences_list

# DF to Save
def get_dataframe(table_children):
    updated_df = pd.DataFrame(columns = ['Stage', 'Authority', 'Submission', 'Prerequisite', 'IsComplete',
                                             'Filetype', 'Template', 'FinalDocumentLink', 'Remarks'])
        
    for i,row in enumerate(table_children['props']['children'][1]['props']['children']):
        #print(row)
        # Stage
        updated_df.loc[i, 'Stage'] = row['props']['children'][0]['props']['children']

        # Authority
        updated_df.loc[i, 'Authority'] = row['props']['children'][2]['props']['children']

        # Submission
        updated_df.loc[i, 'Submission'] = row['props']['children'][4]['props']['children']

        # Prerequisite: row['props']['children'][6]
        if row['props']['children'][6]['props']['children'] == '':
            updated_df.loc[i, 'Prerequisite'] = ''
        else:
            updated_df.loc[i, 'Prerequisite'] = row['props']['children'][6]['props']['children']['props']['id']['index'].split('_')[-1].split('--')[0].strip()
        
        # IsComplete
        if row['props']['children'][6]['props']['children'] == '':
            updated_df.loc[i, 'IsComplete'] = np.nan
        elif (row['props']['children'][6]['props']['children']['props']['id']['type'] == 'checkboxes'):
            
            if 'value' in row['props']['children'][6]['props']['children']['props']:
                updated_df.loc[i, 'IsComplete'] = 1
            else:
                updated_df.loc[i, 'IsComplete'] = 0
        elif (row['props']['children'][6]['props']['children']['props']['id']['type'] == 'submission-perc'):
            if row['props']['children'][6]['props']['children']['props']['value'] == 'Incomplete':
                updated_df.loc[i, 'IsComplete'] = 0
            elif row['props']['children'][6]['props']['children']['props']['value'] == 'Complete':
                updated_df.loc[i, 'IsComplete'] = 1
            else:
                updated_df.loc[i, 'IsComplete'] = 2
        elif (row['props']['children'][6]['props']['children']['props']['id']['type'] == 'stage-perc'):
            if row['props']['children'][6]['props']['children']['props']['value'] == 'Incomplete':
                updated_df.loc[i, 'IsComplete'] = 0
            else:
                updated_df.loc[i, 'IsComplete'] = 1
        else:
            updated_df.loc[i, 'IsComplete'] = 0

        # Filetype: row['props']['children'][7]
        updated_df.loc[i, 'Filetype'] = row['props']['children'][7]['props']['children']

        # Template: row['props']['children'][8]
        if row['props']['children'][8]['props']['children'] == None:
            updated_df.loc[i, 'Template'] = ''
        elif row['props']['children'][8]['props']['children'] == '':
            updated_df.loc[i, 'Template'] = ''
        else:
            updated_df.loc[i, 'Template'] = row['props']['children'][8]['props']['children']['props']['href']

        # Link to the final document: row['props']['children'][9]
        if row['props']['children'][9]['props']['children'] == '':
            updated_df.loc[i, 'FinalDocumentLink'] = ''
        elif 'value' not in row['props']['children'][9]['props']['children']['props']:
            updated_df.loc[i, 'FinalDocumentLink'] = ''
        else:
            updated_df.loc[i, 'FinalDocumentLink'] = row['props']['children'][9]['props']['children']['props']['value']
            
        # Remarks: row['props']['children'][10]
        if row['props']['children'][10]['props']['children'] == '':
            updated_df.loc[i, 'Remarks'] = ''
        elif 'value' not in row['props']['children'][10]['props']['children']['props']:
            updated_df.loc[i, 'Remarks'] = ''
        else:
            updated_df.loc[i, 'Remarks'] = row['props']['children'][10]['props']['children']['props']['value']
        

    # fill the nans
    stage_indexes = updated_df[~updated_df['Stage'].isna()].index
    authority_indexes = updated_df[~updated_df['Authority'].isna()].index
    submission_indexes = updated_df[~updated_df['Submission'].isna()].index

    # assign values
    updated_df.to_csv('get_dataframe_out_01.csv', index=False)
    df = assign_missing_values(stage_indexes, updated_df, 'Stage')
    df = assign_missing_values(authority_indexes, df, 'Authority')
    df.loc[df.index.isin(stage_indexes), 'Authority'] = ''

    df = assign_missing_values(submission_indexes, df, 'Submission')
    df.loc[df.index.isin(stage_indexes) | df.index.isin(authority_indexes), 'Submission'] = ''
    df.loc[df.index.isin(submission_indexes), 'Prerequisite'] = ''
   
    # remove NaNs from the Prerequisite column
    df['Prerequisite'] = df['Prerequisite'].replace('nan', None)
    df.to_csv('get_dataframe_out_02.csv', index=False)
    # replace with DB IDs

    # get stage IDs
    database = 'ArchcorpNotes'
    conn = pyodbc.connect(
    f"DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}"
    )

    stage_query = "SELECT * FROM Project_Stage"
    stage_table = pd.read_sql(stage_query, conn)

    conn.close()

    stage_ids = stage_table.set_index('Name')['Id'].to_dict()

    df['StageID'] = df['Stage'].map(stage_ids)

    # get the submission IDs
    database = 'ArchAuthorityTracker'
    conn = pyodbc.connect(
    f"DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}"
    )

    auth_query = "SELECT * FROM AuthoritySubmissions"
    subm_table = pd.read_sql(auth_query, conn)

    conn.close()

    subm_ids = subm_table.set_index('SubmissionName')['ID'].to_dict()

    df['SubmissionID'] = df['Submission'].map(subm_ids)
    
    # get the prerequisiteIDs

    conn = pyodbc.connect(
    f"DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}"
    )

    prereq_query = "SELECT * FROM Prerequisites"
    prereq_table = pd.read_sql(prereq_query, conn)

    prereq_table.to_csv('Prerequisites-table.csv', index=False)
    prereq_table['Name'] = prereq_table['Name'].str.strip()

    conn.close()

    prereq_ids = prereq_table.set_index('Name')['ID'].to_dict()
    print(prereq_ids)
    print(df['Prerequisite'].unique())


    missing_keys = set(df['Prerequisite']) - set(prereq_ids.keys())
    print("Missing keys:", missing_keys)

    df['PrerequisiteID'] = df['Prerequisite'].map(prereq_ids)
    df.to_csv('get_dataframe_out_03.csv', index=False)

    # get the filetypeIDs
    conn = pyodbc.connect(
    f"DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}"
    )

    filetype_query = "SELECT * FROM FileTypes"
    filetype_table = pd.read_sql(filetype_query, conn)

    conn.close()

    filetype_ids = filetype_table.set_index('Name')['ID'].to_dict()

    df['FiletypeID'] = df['Filetype'].map(filetype_ids)

    # get Authority IDs

    conn = pyodbc.connect(
    f"DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}"
    )

    auth_query = "SELECT * FROM Authorities"
    auth_table = pd.read_sql(auth_query, conn)

    conn.close()

    auth_ids = auth_table.set_index('AuthorityName')['AuthorityID'].to_dict()    

    df['AuthorityID'] = df['Authority'].map(auth_ids)

    df.to_csv('Sample_DF_for_DB.csv', index=False)


    ## Update the IsComplete column and the FinalDocumentLink column
    ## 1.) Update IsComplete = 1 for all rows with the same PrerequisiteID, if at least 1 prerequisite is marked as completed
    ## 2.) Copy the FinalDocumentLink for all rows with the same PrerequisiteID, use the 1st occurrence as the reference

    df = update_is_complete(df)

    df.to_csv('Sample_DF_for_DB_after_func.csv', index=False)

    return df


def assign_missing_values(index_list, df, col):
    for i in range(len(df)):
        if pd.isna(df.loc[i, col]):
            max_less_than_index = find_max_less_than_index(index_list, i)
            if max_less_than_index is not None:
                df.loc[i, col] = df.loc[max_less_than_index, col]
    return df

def find_max_less_than_index(list, i):
    filtered_list = [num for num in list if num < i]
    if filtered_list:
        return max(filtered_list)
    else:
        return None


def connect_to_db(database):
    server = '192.168.6.16'
    database = database
    username = 'arch'
    password = '@rchcorp$uiltIN@@'
    driver = '{ODBC Driver 17 for SQL Server}'
    conn = pyodbc.connect(
    f"DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}"
    )
    
    return conn


def save_to_db(project_name, filled_df, authority_name):

    auth_dict = {'Al Ain Municipality': 'aam',
                 'Dubai Silicon Oasis': 'dso',
                 'DDA and EMAAR': 'dda_emaar',
                 'Dubai Municipality': 'dm',
                 'Dubai Development Authority': 'dda',
                 'Sharjah Municipality': 'sm',
                 'Trakhees': 'trakhees',
                 'Dubai South': 'ds',
                 'Abu Dhabi Municipality': 'ad'
                 }

    auth_name = auth_dict[authority_name]

    # get the project id and project code
    database = "Archcorp_"
    conn = pyodbc.connect(
    f"DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}"
    )

    proj_code = project_name.split('-')[0].strip()

    project_query = "SELECT * FROM Projects WHERE ProjectCode ='" + proj_code + "'"
    project_query = pd.read_sql(project_query, conn)

    #project_query = pd.read_sql("SELECT * FROM Projects WHERE ProjectCode ='" + proj_code + "'", con=engine)

    proj_id = project_query.loc[0, 'Id']

    # Insert to ProjectChecklist table
    connection_str = connect_to_db('ArchAuthorityTracker')


    checklist_name = 'auth_project_' + str(proj_id)
    current_dt = datetime.now()

    # Save the authority ID
    auth_id_query = "SELECT AuthorityID FROM ProjectAuthorityChecklist WHERE ChecklistName = '" + str(auth_name) + "_template_01'"
    auth_id_table = pd.read_sql(auth_id_query, connection_str)

    auth_id = auth_id_table.loc[0, 'AuthorityID']
    #print(auth_id)

    values = str(proj_id) + ',' + str(proj_code)+ ",'" + checklist_name +"', '" + str(current_dt) + "','" + str(current_dt) + "', " + str(auth_id)

    cursor = connection_str.cursor()
    
    update_dt_query = "INSERT INTO ProjectAuthorityChecklist (ProjectID, ProjectCode, ChecklistName, CreatedDateTime, ModifiedDateTime, AuthorityID)\
                   VALUES (" + values + ")"
                   
    
    cursor.execute(update_dt_query)

    # Commit the changes to the database
    connection_str.commit()
    
    # Create table
    filled_df['ModifiedDT'] = current_dt
    #print(filled_df.columns)
    filled_df2 = filled_df[['StageID', 'AuthorityID', 'SubmissionID', 'PrerequisiteID', 'FiletypeID', 'IsComplete', 'Template', 'FinalDocumentLink', 'Remarks', 'ModifiedDT']]
    filled_df2 = filled_df2.fillna('')
    update_dt_query = "CREATE TABLE [" + checklist_name + "](ID INT IDENTITY(1,1) PRIMARY KEY,\
                         StageID INT, \
                         AuthorityID INT, \
                         SubmissionID varchar(max), \
                         PrerequisiteID varchar(max), \
                         FiletypeID varchar(50), \
                         IsComplete int, \
                         Template varchar(500), \
                         FinalDocumentLink varchar(500), \
                         Remarks varchar(max), \
                         ModifiedDT datetime2(7)) "
    
    cursor.execute(update_dt_query)
    connection_str.commit()
    
    # Insert values
    insert_query = f"INSERT INTO [" + checklist_name + "] values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
    cursor = connection_str.cursor()


    for row in filled_df2.values.tolist():
        cursor.execute(insert_query, row)

    connection_str.commit()

    # Close the cursor and database connection
    cursor.close()
    connection_str.close()

#%%
# def get_stage_names(auth_template_table):
#     connection_str = connect_to_db('ArchcorpNotes')
#     connection_url = URL.create("mssql+pyodbc", query={"odbc_connect": connection_str})
#     engine = create_engine(connection_url)

#     stage_table = pd.read_sql("SELECT * FROM Project_Stage", con = engine)
#     stage_ids = stage_table.set_index('Id')['Name'].to_dict()

#     auth_template_table['Stage'] = auth_template_table['StageID'].map(stage_ids)
#     auth_template_table['Stage_final'] = np.where(auth_template_table['AuthorityID'] == 0, auth_template_table['Stage'], np.nan)

#     return auth_template_table


def get_stage_names(auth_template_table):

    # Define the connection details
    server = '192.168.6.16'
    database = 'ArchcorpNotes'
    username = 'arch'
    password = '@rchcorp$uiltIN@@'
    driver = '{ODBC Driver 17 for SQL Server}'

    # Establish the database connection
    conn = pyodbc.connect(
    f"DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}"
    )

    query = "SELECT * FROM Project_Stage"
    stage_table = pd.read_sql(query, conn)

    conn.close()

    stage_ids = stage_table.set_index('Id')['Name'].to_dict()

    auth_template_table['StageID'] = auth_template_table['StageID'].astype(int)

    auth_template_table['Stage'] = auth_template_table['StageID'].map(stage_ids)

    auth_template_table.loc[auth_template_table['AuthorityID'].isna(), 'AuthorityID'] = 0
    auth_template_table['AuthorityID'] = auth_template_table['AuthorityID'].astype(int)
    auth_template_table['Stage_final'] = np.where(auth_template_table['AuthorityID'] == 0, auth_template_table['Stage'], np.nan)

    return auth_template_table

#%%
def get_authority_names(auth_template_table):
# get the authority IDs
    connection_str = connect_to_db('ArchAuthorityTracker')

    authority_table = pd.read_sql("SELECT * FROM Authorities", connection_str)
    authority_ids = authority_table.set_index('AuthorityID')['AuthorityName'].to_dict()

    auth_template_table['Source'] = auth_template_table['AuthorityID'].map(authority_ids)

    #print(auth_template_table['SubmissionID'].unique())
    #print(auth_template_table['AuthorityID'].unique())
    #auth_template_table['Source_final'] = np.where((auth_template_table['Submission'].isna()) & (auth_template_table['AuthorityID']!=0), auth_template_table['Source'], np.nan)
    auth_template_table['Source_final'] = np.where((auth_template_table['SubmissionID'].isna()) & (auth_template_table['AuthorityID']!=0), auth_template_table['Source'], np.nan)
    return auth_template_table

#%%
def get_template(authority):
    auth_dict = {'Al Ain Municipality': 'aam',
                 'Dubai Silicon Oasis': 'dso',
                 'DDA and EMAAR': 'dda_emaar',
                 'Dubai Municipality': 'dm',
                 'Dubai Development Authority': 'dda',
                 'Sharjah Municipality': 'sm',
                 'Trakhees': 'trakhees',
                 'Dubai South': 'ds',
                 'Abu Dhabi Municipality': 'ad'
                 }
    ##
    connection_str = connect_to_db('ArchAuthorityTracker')


    auth_template_table = pd.read_sql("SELECT * FROM " + auth_dict[authority] + '_template_01 ORDER BY StageID, AuthorityID, SubmissionID', connection_str)
    auth_template_table = auth_template_table.replace('', np.nan)

    ### Add the stage names, authority names
    auth_template_table = get_stage_names(auth_template_table)
    auth_template_table = get_authority_names(auth_template_table)
    auth_template_table.to_csv('auth_template_table.csv', index=False)

    auth_template_table = get_submission_names(auth_template_table)
    auth_template_table = get_prerequisite_names(auth_template_table)
    auth_template_table = get_filetype_names(auth_template_table)
    
    # create the 'Document_final' column
    auth_template_table['Document'] = auth_template_table['Submission']
    auth_template_table['Document_final'] = np.where((auth_template_table['Prerequisite'].isna()), auth_template_table['Document'], np.nan)

    auth_template_table = auth_template_table.rename(columns = {'Prerequisite': 'Prerequisites'})
    auth_template_table['Prerequisites'] = np.where(auth_template_table['Prerequisites'].isna(), np.nan, auth_template_table['Prerequisites'])
        
    auth_template_table.to_csv('auth_template_db.csv')
    return auth_template_table


# %%
def check_project(project_name):
        proj_code = project_name.split('-')[0].strip()

        # DB Connection
        connection_str = connect_to_db('ArchAuthorityTracker')

        exists_query = f"SELECT COUNT(*) AS Count FROM ProjectAuthorityChecklist WHERE ProjectCode = {proj_code}"
        exists = pd.read_sql(exists_query, connection_str)
        if exists.loc[0,'Count'] > 0:
            return True
        else:
            return False

#%%
def get_existing_checklist(project_name):
    proj_code = project_name.split('-')[0].strip()

    # DB Connection
    connection_str = connect_to_db('ArchAuthorityTracker')

    checklist_name_query = f"SELECT ChecklistName FROM ProjectAuthorityChecklist WHERE ProjectCode = {proj_code}"
    checklist_name = pd.read_sql(checklist_name_query, connection_str)

    checklist_name = checklist_name.loc[0, 'ChecklistName']

    auth_template_table = pd.read_sql("SELECT * FROM " + checklist_name + " ORDER BY StageID, AuthorityID, SubmissionID", connection_str)
    auth_template_table = auth_template_table.replace('', np.nan)

    ### Add the stage names, authority names
    auth_template_table = get_stage_names(auth_template_table)
    auth_template_table = get_authority_names(auth_template_table)
    auth_template_table = get_submission_names(auth_template_table)
    auth_template_table = get_prerequisite_names(auth_template_table)
    auth_template_table = get_filetype_names(auth_template_table)

    # create the 'Document_final' column
    auth_template_table['Document'] = auth_template_table['Submission']
    auth_template_table['Document_final'] = np.where((auth_template_table['Prerequisite'].isna()), auth_template_table['Document'], np.nan)


    auth_template_table = auth_template_table.rename(columns = {'Prerequisite': 'Prerequisites'})
    auth_template_table['Prerequisites'] = np.where(auth_template_table['Prerequisites'].isna(), np.nan, auth_template_table['Prerequisites'])

    return auth_template_table

# %%
def truncate_checklist(project_name):
    proj_code = project_name.split('-')[0].strip()

    # DB Connection
    connection_str = connect_to_db('ArchAuthorityTracker')

    checklist_name_query = f"SELECT ChecklistName FROM ProjectAuthorityChecklist WHERE ProjectCode = {proj_code}"
    checklist_name = pd.read_sql(checklist_name_query, connection_str)

    checklist_name = checklist_name.loc[0, 'ChecklistName']
    
    cursor = connection_str.cursor()
    
    update_dt_query = "TRUNCATE TABLE [" + checklist_name + "]"
    # Commit the changes to the database
    cursor.execute(update_dt_query)
    
    connection_str.commit()

    # Close the cursor and database connection
    cursor.close()
    connection_str.close()
    print(str(checklist_name) + ' table truncated')

    return checklist_name

#%%
def save_to_db_existing(checklist_name, filled_df):

    # 1.) Update the modified date in the ProjectAuthorityChecklist table

    # DB Connection
    connection_str = connect_to_db('ArchAuthorityTracker')

    current_dt = datetime.now()

    update_dt_query = "UPDATE ProjectAuthorityChecklist SET ModifiedDateTime = '" + str(current_dt) + "' WHERE ChecklistName = '" + str(checklist_name) +"'"
    cursor = connection_str.cursor()
    
    cursor.execute(update_dt_query)

    # Commit the changes to the database
    connection_str.commit()
    

    # 2.) Save the updated checklist to the DB 

    filled_df['ModifiedDT'] = current_dt

    print(filled_df.columns)

    cols = ['StageID', 'AuthorityID', 'SubmissionID', 'PrerequisiteID', 'FiletypeID', 'Template', 'ModifiedDT', 'IsComplete', 'FinalDocumentLink', 'Remarks']
    filled_df2 = filled_df[cols]
    filled_df2 = filled_df2.fillna('')

    print(filled_df2.head())


    # Insert values
    #insert_query = f"INSERT INTO [" + checklist_name + "] values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
    insert_query = f"INSERT INTO [{checklist_name}] values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"

    for row in filled_df2.values.tolist():
        cursor.execute(insert_query, row)
    
    connection_str.commit()

    # Close the cursor and database connection
    cursor.close()
    connection_str.close()


#%%
def get_auth(project_name):

    auth_dict = {'Al Ain Municipality': 'AAM',
                 'Dubai Silicon Oasis': 'DSOA',
                 'DDA and EMAAR': 'DDA AND EMAAR',
                 'Dubai Municipality': 'DM',
                 'Dubai Development Authority': 'DDA',
                 'Sharjah Municipality': 'SM',
                 'Trakhees': 'TRAKHEES',
                 'Dubai South': 'DS',
                 'Abu Dhabi Municipality': 'ADM'
                 }

    proj_code = project_name.split('-')[0].strip()

    
    # DB Connection
    connection_str = connect_to_db('ArchAuthorityTracker')

    auth_id_query = f"SELECT AuthorityID FROM ProjectAuthorityChecklist WHERE ProjectCode = {proj_code}"
    auth_id = pd.read_sql(auth_id_query, connection_str)

    auth_id = auth_id.loc[0, 'AuthorityID']


    auth_name_query = f"SELECT AuthorityName FROM Authorities WHERE AuthorityID = {auth_id}"
    auth_name = pd.read_sql(auth_name_query, connection_str)

    auth_name = auth_name.loc[0, 'AuthorityName']

    authority_name_full = [key for key, val in auth_dict.items() if val == auth_name]
    #print(authority_name_full)

    return authority_name_full[0]


#%%
def create_gantt_tasks(filled_df, project_name):
    # Insert the authority submissions in the gantt tasks

    # Get the project ID
    connection_str = connect_to_db('Archcorp_')

    proj_code = project_name.split('-')[0].strip()

    project_query = pd.read_sql("SELECT * FROM Projects WHERE ProjectCode ='" + proj_code + "'", connection_str)
    proj_id = project_query.loc[0, 'Id']

    query = f"SELECT \
        CASE \
        WHEN EXISTS (SELECT 1 FROM TASKS WHERE PROJECTID = {proj_id} AND Name = 'Design') THEN 1 \
        ELSE 0 \
        END AS IsDesignPresent"

    result = pd.read_sql(query, connection_str)
    print(result)
    connection_str.close()

    if result.loc[0, 'IsDesignPresent'] == 1:

        # insert the submissions as a task, insert until DD stage
        filled_df['Stage'] = np.where(filled_df['Stage'] == 'Detailed Design', 'Detail Design', filled_df['Stage'])
        filled_df = filled_df[filled_df['Stage'] != 'Construction Stage']
        insert_gantt_tasks_design(filled_df, proj_id)

    else:
        # Check if Construction Supervision stage is present
        connection_str = connect_to_db('Archcorp_')
        query = f"SELECT \
        CASE \
        WHEN EXISTS (SELECT 1 FROM TASKS WHERE PROJECTID = {proj_id} AND Name = 'Construction Supervision') THEN 1 \
        ELSE 0 \
        END AS IsConstructionPresent"

        result = pd.read_sql(query, connection_str)
        connection_str.close()

        if result.loc[0, 'IsConstructionPresent'] == 1:
            filled_df_cs = filled_df[filled_df['Stage'] == 'Construction Stage']

            # Get the task id for construction supervision
            connection_str = connect_to_db('Archcorp_')
            cs_query = f"SELECT \
                * FROM Tasks \
                WHERE ProjectID = {proj_id} AND Name LIKE 'Construction Supervision'"
            
            cs_row = pd.read_sql(cs_query, connection_str)
            current_dt = datetime.now()

            # Insert AOR as a subtask of Construction Supervision
            values = ('AOR',
                     str(cs_row.loc[0,'StartDate']),
                     str(cs_row.loc[0, 'EndDate']),
                     str(0) ,
                     str(0) ,
                     str(current_dt),
                     str(1),
                     str(cs_row.loc[0,'Id']) ,
                     str(92),
                     str(proj_id),
                     str(0),
                     str(1),
                     str(92),
                     str(current_dt))
            
            insert_subtask_query = "INSERT INTO tasks (Name, StartDate, EndDate, Progress, Duration, \
                CreatedDate, TaskType, ParentTaskID, CreatedBy, ProjectId, IsCompleted, \
                IsActive, ModifiedBy, ModifiedDate) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
            
            cursor = connection_str.cursor()
            cursor.execute(insert_subtask_query, values)
            
            connection_str.commit()

            cursor.close()
            connection_str.close()

            # Insert to the submissions as subtasks to the 'Construction Supervision' stage
            connection_str = connect_to_db('Archcorp_')
            cs_task_id_query = f"SELECT Id FROM tasks WHERE ProjectID = {proj_id} and  Name = 'Construction Supervision'"
            cs_task_id = pd.read_sql(cs_task_id_query, connection_str)
            connection_str.close()
            values_to_insert = []

            filled_df_cs = filled_df_cs[~filled_df_cs['Submission'].isna()]
            
            for index, row in filled_df_cs.iterrows():

                '''
                Name,
                StartDate,
                EndDate,
                Progress,
                Duration,
                CreatedDate,
                TaskType,
                ParentTaskID,
                CreatedBy,
                ProjectId,
                IsCompleted,
                IsActive,
                ModifiedBy,
                ModifiedDate
                '''

                values = (row['Submission'],
                        str(cs_row.loc[0,'StartDate']),
                        str(cs_row.loc[0, 'EndDate']),
                        str(0) ,
                        str(0) ,
                        str(current_dt),
                        str(1),
                        str(cs_task_id.loc[0,'Id']) ,
                        str(92),
                        str(proj_id),
                        str(0),
                        str(1),
                        str(92),
                        str(current_dt))
                
                values_to_insert.append(values)
        
        print(values_to_insert)
        #connection_str.close()
        connection_str = connect_to_db('Archcorp_')
        cursor = connection_str.cursor()

        # Construct the query with placeholders for values
        query = "INSERT INTO tasks (Name, StartDate, EndDate, Progress, Duration, \
        CreatedDate, TaskType, ParentTaskID, CreatedBy, ProjectId, IsCompleted, \
        IsActive, ModifiedBy, ModifiedDate) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
        
        cursor = connection_str.cursor()

        for row in values_to_insert: #.values.tolist():
            cursor.execute(query, row)
            
        connection_str.commit()

        # Close the cursor and database connection
        cursor.close()
        connection_str.close()
            
#%%
def insert_gantt_tasks_design(filled_df, proj_id):

    filled_df = filled_df[filled_df['Stage'] != 'Construction Stage']
    connection_str = connect_to_db('Archcorp_')

    # Get the taskid for task - AOR per stage
    aor_query = f"SELECT \
        T1.ID, \
        T1.Name, \
        T2.Name AS ParentTaskName, \
        T1.StartDate, \
        T1.EndDate \
        FROM TASKS T1\
        LEFT JOIN TASKS T2 \
        ON T1.ParentTaskId = T2.Id \
        WHERE T1.NAME = 'AOR' \
        AND T1.ProjectID = {proj_id}"
    
    aor_table = pd.read_sql(aor_query, connection_str)
    print(aor_table)

    stages = filled_df['Stage'].unique()
    print(stages)

    filled_df = filled_df[~filled_df['Submission'].isna()]
    print(filled_df['Submission'].unique())

    for stage in stages:

        aor_row = aor_table[aor_table['ParentTaskName'].str.contains(stage)].reset_index(drop=True)
        print(aor_row)
        #print(aor_row)
        filled_df_subset = filled_df[(filled_df['Stage'] == stage) & (filled_df['Submission'] != '')].drop_duplicates(subset='Submission')
        #print(filled_df_subset)

        current_dt = datetime.now()
        
        values_to_insert = []

        for index, row in filled_df_subset.iterrows():

            '''
            Name,
            StartDate,
            EndDate,
            Progress,
            Duration,
            CreatedDate,
            TaskType,
            ParentTaskID,
            CreatedBy,
            ProjectId,
            IsCompleted,
            IsActive,
            ModifiedBy,
            ModifiedDate
            '''

            values = (row['Submission'],
                     str(aor_row.loc[0,'StartDate']),
                     str(aor_row.loc[0, 'EndDate']),
                     str(0) ,
                     str(0) ,
                     str(current_dt),
                     str(1),
                     str(aor_row.loc[0,'ID']) ,
                     str(92),
                     str(proj_id),
                     str(0),
                     str(1),
                     str(92),
                     str(current_dt))
            
            values_to_insert.append(values)

        print(values_to_insert)

        # Perform bulk insert
        connection_str = connect_to_db('Archcorp_')

        # Construct the query with placeholders for values
        query = "INSERT INTO tasks (Name, StartDate, EndDate, Progress, Duration, \
        CreatedDate, TaskType, ParentTaskID, CreatedBy, ProjectId, IsCompleted, \
        IsActive, ModifiedBy, ModifiedDate) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
        
        cursor = connection_str.cursor()
        
        for row in values_to_insert: #.values.tolist():
            cursor.execute(query, row)
            
        connection_str.commit()

        # Close the cursor and database connection
        cursor.close()
        connection_str.close()

# %%
def get_submission_names(auth_template_table):

    # Define the connection details
    server = '192.168.6.16'
    database = 'ArchAuthorityTracker'
    username = 'arch'
    password = '@rchcorp$uiltIN@@'
    driver = '{ODBC Driver 17 for SQL Server}'

    # Establish the database connection
    conn = pyodbc.connect(
    f"DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}"
    )
    
    query = "SELECT * FROM AuthoritySubmissions"
    subm_table = pd.read_sql(query, conn)

    # Close the DB connection
    conn.close()

    subm_ids = subm_table.set_index('ID')['SubmissionName'].to_dict()
    subm_ids[0] = ''

    #print(subm_ids)

    auth_template_table['SubmissionID'] = np.where(auth_template_table['SubmissionID'].isna(), '0', auth_template_table['SubmissionID'])
    #print(auth_template_table['SubmissionID'].unique())
    auth_template_table['SubmissionID'] = auth_template_table['SubmissionID'].astype(int)
    #print(auth_template_table['SubmissionID'].unique())
    
    auth_template_table['Submission'] = auth_template_table['SubmissionID'].map(subm_ids)

    #print(auth_template_table['SubmissionID'].unique())
    auth_template_table['Submission'] = np.where(auth_template_table['Submission'] == '', np.nan, auth_template_table['Submission'])


    return auth_template_table
# %%
def get_prerequisite_names(auth_template_table):
    # Define the connection details
    server = '192.168.6.16'
    database = 'ArchAuthorityTracker'
    username = 'arch'
    password = '@rchcorp$uiltIN@@'
    driver = '{ODBC Driver 17 for SQL Server}'

    # Establish the database connection
    conn = pyodbc.connect(
    f"DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}"
    )
    
    query = "SELECT * FROM Prerequisites"
    prereq_table = pd.read_sql(query, conn)

    prereq_ids = prereq_table.set_index('ID')['Name'].to_dict()
    prereq_ids[0] = ''

    #print(prereq_ids)

    auth_template_table['PrerequisiteID'] = np.where(auth_template_table['PrerequisiteID'].isna(), '0', auth_template_table['PrerequisiteID'])
    auth_template_table['PrerequisiteID'] = auth_template_table['PrerequisiteID'].astype(int)
    auth_template_table['Prerequisite'] = auth_template_table['PrerequisiteID'].map(prereq_ids)

    auth_template_table['Prerequisite'] = np.where(auth_template_table['Prerequisite'] == '', np.nan, auth_template_table['Prerequisite'])

    return auth_template_table

# %%
def get_filetype_names(auth_template_table):

    # Define the connection details
    server = '192.168.6.16'
    database = 'ArchAuthorityTracker'
    username = 'arch'
    password = '@rchcorp$uiltIN@@'
    driver = '{ODBC Driver 17 for SQL Server}'

    # Establish the database connection
    conn = pyodbc.connect(
    f"DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}"
    )
    
    query = "SELECT * FROM FileTypes"
    filetype_table = pd.read_sql(query, conn)

    conn.close()

    filetype_ids = filetype_table.set_index('ID')['Name'].to_dict()
    filetype_ids[0] = ''

    auth_template_table['FiletypeID'] = np.where(auth_template_table['FiletypeID'].isna(), '0', auth_template_table['FiletypeID'])
    auth_template_table['FiletypeID'] = auth_template_table['FiletypeID'].astype(int)
    auth_template_table['Filetype'] = auth_template_table['FiletypeID'].map(filetype_ids)
    auth_template_table['Filetype'] = np.where(auth_template_table['Filetype'] == '', np.nan, auth_template_table['Filetype'])

    return auth_template_table
# %%
def fetch_data(server, username, password, driver):
    print("abc")
    # Define the connection details
    database = 'Archcorp_'
    
    
    connection_string = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password};MultipleActiveResultSets=true"

    # Establish the database connection
    conn = pyodbc.connect(connection_string)
    
    project_query = "SELECT \
    CONCAT(ProjectCode, ' - ', ProjectName) AS [Project Name]\
    FROM \
    projects \
    WHERE IsActive = 1"

    project_names = pd.read_sql(project_query, conn)
    
    project_names.dropna(inplace=True)
    
    conn.close()
    
    return project_names

def update_is_complete(df):
    # Group the DataFrame by PrerequisiteID
    grouped = df.groupby(['PrerequisiteID', 'AuthorityID'])

    # Iterate over the groups
    for (prerequisite_id, authority_id), group in grouped:
        # Check if at least one row in the group is marked as completed
        if group['IsComplete'].eq(1).any():
            # Get the FinalDocumentLink value from the first completed row
            completed_link = group.loc[group['IsComplete'] == 1, 'FinalDocumentLink'].iloc[0]

            # Set IsComplete to 1 for all rows in the group
            df.loc[group.index, 'IsComplete'] = 1

            # Copy the FinalDocumentLink value to other rows in the group
            df.loc[group.index, 'FinalDocumentLink'] = completed_link

    return df

def insert_to_project_auth_table(project_name, authority_name):
    auth_dict = {'Al Ain Municipality': 'aam',
                 'Dubai Silicon Oasis': 'dso',
                 'DDA and EMAAR': 'dda_emaar',
                 'Dubai Municipality': 'dm',
                 'Dubai Development Authority': 'dda',
                 'Sharjah Municipality': 'sm',
                 'Trakhees': 'trakhees',
                 'Dubai South': 'ds',
                 'Abu Dhabi Municipality': 'ad'
                 }

    auth_name = auth_dict[authority_name]

    # get the project id and project code
    database = "Archcorp_"
    conn = pyodbc.connect(
    f"DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}"
    )

    proj_code = project_name.split('-')[0].strip()

    project_query = "SELECT * FROM Projects WHERE ProjectCode ='" + proj_code + "'"
    project_query = pd.read_sql(project_query, conn)

    proj_id = project_query.loc[0, 'Id']

    # Insert to ProjectChecklist table
    connection_str = connect_to_db('ArchAuthorityTracker')

    checklist_name = 'auth_project_' + str(proj_id)
    current_dt = datetime.now()

    # Save the authority ID
    auth_id_query = "SELECT AuthorityID FROM ProjectAuthorityChecklist WHERE ChecklistName = '" + str(auth_name) + "_template_01'"
    auth_id_table = pd.read_sql(auth_id_query, connection_str)

    auth_id = auth_id_table.loc[0, 'AuthorityID']
    #print(auth_id)

    values = str(proj_id) + ',' + str(proj_code)+ ",'" + checklist_name +"', '" + str(current_dt) + "','" + str(current_dt) + "', " + str(auth_id)

    cursor = connection_str.cursor()
    
    update_dt_query = "INSERT INTO ProjectAuthorityChecklist (ProjectID, ProjectCode, ChecklistName, CreatedDateTime, ModifiedDateTime, AuthorityID)\
                   VALUES (" + values + ")"
                   
    
    cursor.execute(update_dt_query)

    # Commit the changes to the database
    connection_str.commit()

    # Close the cursor and database connection
    cursor.close()
    connection_str.close()

def create_project_checklist_table_new(project_name, authority_name):

    # Insert to ProjectChecklist table
    connection_str = connect_to_db('ArchAuthorityTracker')

    auth_dict = {'Al Ain Municipality': 'aam',
                 'Dubai Silicon Oasis': 'dso',
                 'DDA and EMAAR': 'dda_emaar',
                 'Dubai Municipality': 'dm',
                 'Dubai Development Authority': 'dda',
                 'Sharjah Municipality': 'sm',
                 'Trakhees': 'trakhees',
                 'Dubai South': 'ds',
                 'Abu Dhabi Municipality': 'ad'
                 }

    auth_name = auth_dict[authority_name]

    # get the project id and project code
    connection_str = connect_to_db('Archcorp_')

    proj_code = project_name.split('-')[0].strip()

    project_query = "SELECT * FROM Projects WHERE ProjectCode ='" + proj_code + "'"
    project_query = pd.read_sql(project_query, connection_str)

    proj_id = project_query.loc[0, 'Id']
   
    connection_str.close()

    # Create new table for the project
    connection_str = connect_to_db('ArchAuthorityTracker')
    cursor = connection_str.cursor()

    create_project_table_query = f"SELECT * INTO auth_project_{proj_id} FROM {auth_name}_template_01"
    
    cursor.execute(create_project_table_query)
    connection_str.commit()


    # Query to add columns for: IsComplete, FinalDocumentLink, and Remarks
    add_cols_query = f"ALTER TABLE auth_project_{proj_id} \
                    ADD IsComplete INT DEFAULT 0"
    
    cursor.execute(add_cols_query)
    connection_str.commit()

    add_cols_query_01 = f"ALTER TABLE auth_project_{proj_id} \
                    ADD FinalDocumentLink VARCHAR(500) DEFAULT ''"
    
    cursor.execute(add_cols_query_01)
    connection_str.commit()

    add_cols_query_02 = f"ALTER TABLE auth_project_{proj_id} \
                    ADD Remarks VARCHAR(MAX) DEFAULT ''"
    
    cursor.execute(add_cols_query_02)
    connection_str.commit()


    cursor.close()
    connection_str.close()
    
# %%
def autofill_table():

    autofill_df = {
        'Ref': [''],
        'Date': [''],
        'Project': [''],
        'Project Number': [''],
        'Project Title': [''],
        'Project Description': [''],
        'Project Code': [''],
        'Owner Name': [''],
        'Name': [''],
        'Contact Number': [''],
        'Receipt Number': [''],
        'Consultant Name': [''],
        'Contractor': [''],
        'Plot Number': [''],
        'Height': [''],
        'Building Permit No': [''],
        'Land Use': [''],
        'Built up Area': ['']
    }
    autofill_df = pd.DataFrame(autofill_df)
    autofill_df = autofill_df.transpose()
    autofill_df['Field'] = autofill_df.index
    autofill_df = autofill_df.reset_index(drop=True)
    autofill_df[''] = ''
    autofill_df = autofill_df.drop(columns = 0)

    print(len(autofill_df))
    header_names = []
    for col in autofill_df.columns.tolist():
        if col == 'Field':
            header_names.append(html.Th(col, style = {'width': '5%', 'text-align': 'center'}))
        else: 
            header_names.append(html.Th(col, style = {'width': '15%', 'text-align': 'center'}))
    table_header = [html.Thead(html.Tr(header_names))]

    table_data = []

    # make the 'Values' column editable
    input_col = []
    for i in range(len(autofill_df)):
        if autofill_df.loc[i, 'Field'] == 'Date':
            input_col.append(dcc.DatePickerSingle(
                id='Date-input',
                date= datetime.now(),  # Initial date in the format 'YYYY-MM-DD'
                display_format='DD/MM/YYYY'  # Format in which the date is displayed
                ))
        elif autofill_df.loc[i, 'Field']  == 'Project Description':
            input_col.append(dbc.Textarea(
                         id = {'type': 'autofill-input',
                               'index': autofill_df.loc[i, 'Field']+'-input'},
                         style={'width': '100%', 'resize': 'both', 'overflow': 'auto'},
                         wrap= True
                         , value = autofill_df.loc[i, '']
                         ))   
        else:
            input_col.append(dbc.Input(id = {'type': 'autofill-input',
                                        'index': autofill_df.loc[i, 'Field']+'-input'}, 
                                type="input", style={'width': '100%'},
                                value = autofill_df.loc[i, '']))
        
    autofill_df['Input-col'] = input_col
    autofill_df = autofill_df.drop(columns = '')

    for row in range(len(autofill_df)):
        row_data = []

        for col in autofill_df.columns.tolist():
            row_data.append(html.Td(autofill_df.loc[row, col]))

        row_i = html.Tr(id = autofill_df.loc[row, 'Field']+ '-field',
                        children = row_data)
        
        table_data.append(row_i)

    table_body = [html.Tbody(table_data)]

    table = dbc.Table(table_header + table_body,
                       striped=False,
                       bordered=True,
                       hover=True,
                       responsive=True,
                       style = {'width': '50%',
                                'columnDefs': [
                                    {'width': '100px', 'targets': 0},
                                    {'width': '200px', 'targets': 1},
                                    {'width': '300px', 'targets': 2}],
                                'margin': 'auto' 
                                },             
                    )
    
    return table


#%%

# Function to extract data from nested dictionary
def extract_data(cell):
    if isinstance(cell, dict) and 'props' in cell and 'children' in cell['props']:
        return extract_data(cell['props']['children'])
    elif isinstance(cell, list):
        return [extract_data(item) for item in cell]
    else:
        return cell
    


def insert_to_autofill(autofill_data):
    # Extract data from the table_data

    data = []
    for row in autofill_data[0]['props']['children']:
        row_data = extract_data(row)
        data.append(row_data)

    print(data)

    # Create pandas DataFrame
    # Remove the ['Field', ''] element in the list
    data = data[1]

    # Extract column names

    columns = [item[0] for item in data]
    rows = [item[1] for item in data]

    autofill_df = pd.DataFrame(columns = columns)

    for i in range(len(columns)):
        if columns[i] == 'Date':
            autofill_df.loc[0, columns[i]] = rows[1]['props']['date']
        else:
            autofill_df.loc[0, columns[i]] = rows[i]['props']['value']

    autofill_df['Date'] = pd.to_datetime(autofill_df['Date'], format='%Y-%m-%d').dt.date

    final_df = autofill_df[['Ref', 'Date', 'Project', 'Owner Name', 
                            'Project Number', 'Project Description',
                            'Name', 'Receipt Number', 'Project Title',
                            'Consultant Name', 'Contractor', 'Plot Number',
                            'Height', 'Building Permit No', 'Contact Number',
                            'Land Use', 'Built up Area', 'Project Code'
                            ]]
    
    connection_str = connect_to_db('ArchAuthorityTracker')
    
    # Insert values
    num_columns = len(final_df.columns)
    question_marks = ", ".join(["?"] * num_columns)

    insert_query = f"INSERT INTO [Autofill] values ({question_marks})"
    cursor = connection_str.cursor()

    for row in final_df.values.tolist():
        cursor.execute(insert_query, row)

    connection_str.commit()

    # Close the cursor and database connection
    cursor.close()
    connection_str.close()

