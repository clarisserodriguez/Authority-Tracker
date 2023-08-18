import pyodbc
import pandas as pd
pd.set_option('display.max_rows', None)

from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextBoxHorizontal, LTTextLineHorizontal, LTAnno

from PIL import ImageFont
from PIL import Image
from PIL import ImageDraw
from fpdf import FPDF
import re
import fitz
import os

from docx import Document

# Credentials of the database
server = '192.168.6.16'
database = 'ArchAuthorityTracker'
username = 'arch'
password = '@rchcorp$uiltIN@@'

# The connection string
connection_string = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password};MultipleActiveResultSets=true"

# Connecting the connection string to database
conn = pyodbc.connect(connection_string)

query = "SELECT * FROM Autofill"

# Execute the query and fetch the results into a dataframe
df = pd.read_sql(query, conn)


'''Extra code starts here'''
query_authority_check_list = "SELECT TOP 1 * FROM ProjectAuthorityChecklist ORDER BY CreatedDateTime DESC"
            
            
# Execute the query and fetch the results into a dataframe
df_authority_check_list = pd.read_sql(query_authority_check_list, conn)

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



''' Extra code ends here '''
# Close the database connection --- we should not close it ideally here but let's just see
conn.close()


from pdfminer.layout import LTTextBoxHorizontal, LTTextLineHorizontal
from pdfminer.high_level import extract_pages

def extract_sentence_coordinates(pdf_path):
    words = []

    for page_number, page_layout in enumerate(extract_pages(pdf_path), start=1):
        for element in page_layout:
            if isinstance(element, (LTTextBoxHorizontal, LTTextLineHorizontal)):
                for text_box in element:
                    if isinstance(text_box, LTAnno):
                        continue
                    # word is a line here
                    word = text_box.get_text().strip()
                    # x0, y0, x1, y1 are the bounding boxes of the lines
                    x0, y0, x1, y1 = text_box.bbox
                    words.append((word, (x0, y0, x1, y1), page_number))
                    # Uncomment the following line if you want to print each line and its bounding box
#                     print(word, x0, y0, x1, y1, "Page:", page_number)
#                     print("***" * 30)
    return words



# Function to put the words into the pdf files

# Function to put the words into the pdf files
def word_insertion(file_path, dic, file_name, file_ext, folder_name, df):
    doc = fitz.open(file_path)
    font = ImageFont.truetype("arial.ttf", 15)
    
    check = 0
    for i in range(len(doc)):
        page = doc[i]
        pix = page.get_pixmap()

        # Create PIL Image object
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

        # Create ImageDraw object
        draw = ImageDraw.Draw(img)
        
        # Convert each PDF page to an image
#         if i == 0:  
        for a in df.columns:
            for b in dic:
#                 print(i, "**********", int(dic[b][1]) - 1)
                if re.search(str(a).lower(), str(b).lower()) or "Contact" in b or "Proposed Land" in b \
                or b == "Community Name (as per TKS Site Plan)" \
                or b == "Plot No. (as per TKS Site Plan)" or b == "Project ID  P-" or "I," in b or "Plot#" in b \
                or "Project ID." in b or "Project Description:" in b or "Developer's name" in b or "Plot No." in b \
                or 'Reference' in b or "Project Description" in b or "Owner’s name" in b or "Plot Number" in b \
                or "Land Area" in b or "Land Usage" in b or  "Phone Number:" in b or "Building Permit No" in b\
                or "Plot" in b or "Owner" in b or "DATE" in b or "AREA" in b or "PHONE" in b or "CONTRACTOR" in b:
                    
                   
                    # print(b)
                    # print(len(b))
                    if b == "Project Name" or b == "Project Name:" or b == "Project:" or b == "Project Title:" \
                    or b == "Project Title" or "Project        :" in b:
                        
                        if i == int(dic[b][1]) - 1:
#                             print("Project")
        
                            text = df['Project'][0]

                            x = dic[b][0][0] + 120
                            y = dic[b][0][3] + 5

                            y = pix.height - y

                            # Write on image
                            draw.text((x, y), text, fill="black", font=font)

                    elif "Project        :" in b:

#                             print("We are here")
                        if i == int(dic[b][1]) - 1:
#                             print("Project1")
                            text = df['Project'][0]

                            x = dic[b][0][0] - 100
                            y = dic[b][0][3] + 5

                            y = pix.height - y

                            font = ImageFont.truetype("arial.ttf", 50)

                            # Write on image
                            draw.text((x, y), text, fill="black", font=font)

                    elif b == "Community Name (as per TKS Site Plan)":
                        
                        if i == int(dic[b][1]) - 1:
#                             print("Community Name (as per TKS Site Plan)")
                            text = df['Name'][0]
                            x = dic[b][0][0] + 220
                            y = dic[b][0][3] + 2

                            y = pix.height - y

                            # Write on image
                            draw.text((x, y), text, fill="black", font=font)

                    



                    elif b == "Date:" or b == "Date" or "Date" in b or "Date:" in b:
                        if i == int(dic[b][1]) - 1:
#                             print("Date")
                            text = df['Date'][0]
                            if type(dic[b] == tuple):
                                x = dic[b][0][0] + 30
                                y = dic[b][0][3] + 5

                                y = pix.height - y

                                # Write on image
                                draw.text((x, y), text, fill="black", font=font)

                    elif "I,…" in b:
                        if i == int(dic[b][1]) - 1:
#                             print("I,")
                            text = df['Name'][0]
                            if type(dic[b] == tuple):
                                x = dic[b][0][0] + 50
                                y = dic[b][0][3] + 5

                                y = pix.height - y

                                # Write on image
                                draw.text((x, y), text, fill="black", font=font)

                    elif "Plot No. (as per TKS Site Plan)" in b:
                        if i == int(dic[b][1]) - 1:
#                             print("Plot No. (as per TKS Site Plan)")
                            text = df['Plot No'][0]
                            if type(dic[b] == tuple):
                                x = dic[b][0][0] + 210
                                y = dic[b][0][3] + 4

                                y = pix.height - y

                                # Write on image
                                draw.text((x, y), text, fill="black", font=font)

                    elif "Plot#" in b:
                        if i == int(dic[b][1]) - 1:
#                             print("Plot#")
                            text = df['Plot No'][0]
                            if type(dic[b] == tuple):
                                x = dic[b][0][0] + 50
                                y = dic[b][0][3] + 5

                                y = pix.height - y

                                # Write on image
                                draw.text((x, y), text, fill="black", font=font)

                    elif "Plot No." in b:
                        if i == int(dic[b][1]) - 1:
#                             print("Plot No.")
                            text = df['Plot No'][0]
                            if type(dic[b] == tuple):
                                x = dic[b][0][0] + 35
                                y = dic[b][0][3] + 4

                                y = pix.height - y
                                font1 = ImageFont.truetype("arial.ttf", 10)
                                # Write on image
                                draw.text((x, y), text, fill="black", font=font1)

                    elif "Plot Number" in b:
                        if i == int(dic[b][1]) - 1:
#                             print("Plot Number")
                            text = df['Plot No'][0]
                            if type(dic[b] == tuple):
                                x = dic[b][0][0] + 50
                                y = dic[b][0][3] + 4

                                y = pix.height - y
                                font1 = ImageFont.truetype("arial.ttf", 10)
                                # Write on image
                                draw.text((x, y), text, fill="black", font=font1)

                    elif "Project No" in b or "Project #" in b:
                        if i == int(dic[b][1]) - 1:
#                             print("Project No")
                            text = df['Project No'][0]
                            if type(dic[b] == tuple):
                                x = dic[b][0][0] + 100
                                y = dic[b][0][3] + 5

                                y = pix.height - y

                                # Write on image
                                draw.text((x, y), text, fill="black", font=font)

                    elif b == "Project ID  P-":
                        if i == int(dic[b][1]) - 1:
#                             print("Project ID  P-")
                            text = df['Project No'][0]
                            if type(dic[b] == tuple):
                                x = dic[b][0][0] + 100
                                y = dic[b][0][3] + 2

                                y = pix.height - y

                                # Write on image
                                draw.text((x, y), text, fill="black", font=font)


                    elif "Project ID." in b:
                        if i == int(dic[b][1]) - 1:
#                             print("Project ID.")
                            text = df['Project No'][0]
                            if type(dic[b] == tuple):
                                x = dic[b][0][0] + 50
                                y = dic[b][0][3] + 5

                                y = pix.height - y

                                font1 = ImageFont.truetype("arial.ttf", 10)

                                # Write on image
                                draw.text((x, y), text, fill="black", font=font1)


                    elif b == "Contractor" or b == "Contractor:":
                        if i == int(dic[b][1]) - 1:
#                             print("Contractor")
                            text = df['Contractor'][0]
                            if type(dic[b] == tuple):
                                x = dic[b][0][0] + 130
                                y = dic[b][0][3] + 5

                                y = pix.height - y

                                # Write on image
                                draw.text((x, y), text, fill="black", font=font)

                    elif "Developer's name" in b:
                        if i == int(dic[b][1]) - 1:
#                             print("Developer's name")
                            # print("+++"*30)
                            text = df['Contractor'][0]
    #                             print(text)
                            if type(dic[b] == tuple):
                                x = dic[b][0][0] + 130
                                y = dic[b][0][3] + 5

                                y = pix.height - y

                                # Write on image
                                draw.text((x, y), text, fill="black", font=font)


                    elif b == "Description" or b == "Description:":
                        if i == int(dic[b][1]) - 1:
#                             print("Description")
                            text = df['Description'][0]
                            if type(dic[b] == tuple):
                                x = dic[b][0][0] + 100
                                y = dic[b][0][3] + 5

                                y = pix.height - y

                                # Write on image
                                draw.text((x, y), text, fill="black", font=font)

                    elif "Project Description:" in b and "Project Description and Undertakings for Residential Plots" not in b:
                        if i == int(dic[b][1]) - 1:
#                             print("Project Description:")
                            text = df['Description'][0]
                            if type(dic[b] == tuple):
                                x = dic[b][0][0] + 100
                                y = dic[b][0][3] + 7

                                y = pix.height - y

                                font2 = ImageFont.truetype("arial.ttf", 12)

                                # Write on image
                                draw.text((x, y), text, fill="black", font=font2)

                    elif "Project Description" in b and "Project Description and Undertakings for Residential Plots" not in b:
                        if i == int(dic[b][1]) - 1:
#                             print("Project Description")
                            text = df['Description'][0]
                            if type(dic[b] == tuple):
                                x = dic[b][0][0] + 100
                                y = dic[b][0][3] + 7

                                y = pix.height - y

                                font2 = ImageFont.truetype("arial.ttf", 12)

                                # Write on image
                                draw.text((x, y), text, fill="black", font=font2)



                    elif b == "Consultant" or b == "Consultant:":
                        if "Consultant Authorized" not in b:
                            if i == int(dic[b][1]) - 1:
    #                             print("Consultant")
                                text = df['Consultant'][0]
                                if type(dic[b] == tuple):
                                    x = dic[b][0][0] + 120
                                    y = dic[b][0][3] + 5

                                    y = pix.height - y

                                    # Write on image
                                    draw.text((x, y), text, fill="black", font=font)

                    elif b == "Plot No" or b == "Plot No:":
                        if i == int(dic[b][1]) - 1:
#                             print("Plot No")
                            text = df['Plot No'][0]
                            if type(dic[b] == tuple):
                                x = dic[b][0][0] + 120
                                y = dic[b][0][3] + 5

                                y = pix.height - y

                                # Write on image
                                draw.text((x, y), text, fill="black", font=font)



                    elif b == "Height" or b == "Height:" or b == "Proposed Height" or b == "Proposed Height":
                        if i == int(dic[b][1]) - 1:
#                             print("Height")
                            text = df['Height'][0]
                            if type(dic[b] == tuple):
                                x = dic[b][0][0] + 100
                                y = dic[b][0][3] + 5

                                y = pix.height - y

                                # Write on image
                                draw.text((x, y), text, fill="black", font=font)

                    elif b == "Land Use" or b == "Land Use:" or "Land Use" in b or b == "Proposed Land":
                        if i == int(dic[b][1]) - 1:
#                             print("Land Use")
                            text = df['Land Use'][0]
                            if type(dic[b] == tuple):
                                x = dic[b][0][0] + 120
                                y = dic[b][0][3] + 2

                                y = pix.height - y

                                # Write on image
                                draw.text((x, y), text, fill="black", font=font)

                    elif "Land Usage" in b:
                        if i == int(dic[b][1]) - 1:
#                             print("Land Usage")
                            text = df['Land Use'][0]
                            if type(dic[b] == tuple):
                                x = dic[b][0][0] + 60
                                y = dic[b][0][3] + 2

                                y = pix.height - y

                                # Write on image
                                draw.text((x, y), text, fill="black", font=font)

                    elif b == "Built Up Area" or b == "Built Up Area:" or "Built Up" in b:
                        if i == int(dic[b][1]) - 1:
#                             print("Built Up Area")
                            text = df['Built Up Area'][0]
                            if type(dic[b] == tuple):

                                font = ImageFont.truetype("arial.ttf", 10)

                                x = dic[b][0][0] + 100
                                y = dic[b][0][3] + 2

                                y = pix.height - y

                                # Write on image
                                draw.text((x, y), text, fill="black", font=font)

                    elif "Land Area" in b:
                        if i == int(dic[b][1]) - 1:
#                             print("Land Area")
                            text = df['Built Up Area'][0]
                            if type(dic[b] == tuple):

                                font = ImageFont.truetype("arial.ttf", 10)

                                x = dic[b][0][0] + 110
                                y = dic[b][0][3] + 2

                                y = pix.height - y

                                font3 = ImageFont.truetype("arial.ttf", 12)
                                # Write on image
                                draw.text((x, y), text, fill="black", font=font3)

                    elif "Building Permit No" in b:
                        if i == int(dic[b][1]) - 1:
#                             print("Building Permit No")
                            text = df['Building Permit No'][0]
                            if type(dic[b] == tuple):
                                x = dic[b][0][0] + 110
                                y = dic[b][0][3] + 5

                                y = pix.height - y

                                # Write on image
                                draw.text((x, y), text, fill="black", font=font)

                    elif b == "Building Permit No" or b == "Building Permit No:" or "Building Permit" in b:
                        if i == int(dic[b][1]) - 1:
#                             print("Building Permit No")
                            text = df['Building Permit No'][0]
                            if type(dic[b] == tuple):
                                x = dic[b][0][0] + 130
                                y = dic[b][0][3] + 5

                                y = pix.height - y

                                # Write on image
                                draw.text((x, y), text, fill="black", font=font)


                    elif b == "Contact #:" or b == "Contact No:" or "Contact #" in b or "Contact" in b:
                        if i == int(dic[b][1]) - 1:
#                             print("Contact #:")
                            text = df['Contact No'][0]
                            if type(dic[b] == tuple):
                                x = dic[b][0][0] + 70
                                y = dic[b][0][3] + 5

                                y = pix.height - y
                                font3 = ImageFont.truetype("arial.ttf", 10)
                                # Write on image
                                draw.text((x, y), text, fill="black", font=font3)

                    elif "Phone Number:" in b:
                        if i == int(dic[b][1]) - 1:
#                             print("Phone Number:")
                            text = df['Contact No'][0]
                            if type(dic[b] == tuple):
                                x = dic[b][0][0] + 130
                                y = dic[b][0][3] + 5

                                y = pix.height - y

                                # Write on image
                                draw.text((x, y), text, fill="black", font=font)

                    
                    elif b == "Owner's Name" or \
                    b == "Owner's Name:" or b == "Owners Name:":
                        if i == int(dic[b][1]) - 1:
#                             print("Owner Name")
                            text = df['Owner Name'][0]
                            if type(dic[b] == tuple):
                                x = dic[b][0][0] + 110
                                y = dic[b][0][3] + 5

                                y = pix.height - y

                                # Write on image
                                draw.text((x, y), text, fill="black", font=font)



                    elif "Owner Name" in b:
                        if i == int(dic[b][1]) - 1:
#                             print("Owner’s name:")
                            text = df['Owner Name'][0]
                            if type(dic[b] == tuple):
                                x = dic[b][0][0] + 110
                                y = dic[b][0][3] + 5

                                y = pix.height - y

                                # Write on image
                                draw.text((x, y), text, fill="black", font=font)

                    elif "Name:" in b:
                        if i == int(dic[b][1]) - 1:
#                             print("Name:")
                            text = df['Name'][0]
                            if type(dic[b] == tuple):
                                x = dic[b][0][0] + 400
                                y = dic[b][0][3] + 5

                                y = pix.height - y

                                # Write on image
                                draw.text((x, y), text, fill="black", font=font)
                    
                    elif "Project" in b:
                        if len(b) == 165:
                            text = df['Project'][0]
                            if type(dic[b] == tuple):
                                x = dic[b][0][0] + 80
                                y = dic[b][0][3] + 7

                                y = pix.height - y

                                # Write on image
                                draw.text((x, y), text, fill="black", font=font)
                    
                    elif "Owner" in b:
                        if len(b) == 163:
                            text = df['Owner Name'][0]
                            if type(dic[b] == tuple):
                                x = dic[b][0][0] + 80
                                y = dic[b][0][3] + 7

                                y = pix.height - y

                                # Write on image
                                draw.text((x, y), text, fill="black", font=font)
                    
                    elif "DATE" in b:
                        if len(b) == 18:
                            text = df['Date'][0]
                            if type(dic[b] == tuple):
                                x = dic[b][0][0] + 45
                                y = dic[b][0][3] + 6

                                y = pix.height - y

                                # Write on image
                                draw.text((x, y), text, fill="black", font=font)
                    
                    elif "PROJECT" in b:
                        if len(b) == 86:
                            text = df['Project'][0]
                            if type(dic[b] == tuple):
                                x = dic[b][0][0] + 80
                                y = dic[b][0][3] + 6

                                y = pix.height - y

                                # Write on image
                                draw.text((x, y), text, fill="black", font=font)
                                
                    elif "PLOT No" in b:
                        if len(b) == 86:
                            text = df['Plot No'][0]
                            if type(dic[b] == tuple):
                                x = dic[b][0][0] + 80
                                y = dic[b][0][3] + 5

                                y = pix.height - y

                                # Write on image
                                draw.text((x, y), text, fill="black", font=font)
                     
                    elif "OWNER NAME" in b:
                        if len(b) == 84:
                            text = df['Owner Name'][0]
                            if type(dic[b] == tuple):
                                x = dic[b][0][0] + 100
                                y = dic[b][0][3] + 5

                                y = pix.height - y

                                # Write on image
                                draw.text((x, y), text, fill="black", font=font)
                    
                    elif "AREA" in b:
                        if len(b) == 88:
                            text = df['Built Up Area'][0]
                            if type(dic[b] == tuple):
                                x = dic[b][0][0] + 100
                                y = dic[b][0][3] + 5

                                y = pix.height - y

                                # Write on image
                                draw.text((x, y), text, fill="black", font=font)
                                
                    
                    elif "CONSULTANT" in b:
                        if len(b) == 85:
                            text = df['Consultant'][0]
                            if type(dic[b] == tuple):
                                x = dic[b][0][0] + 100
                                y = dic[b][0][3] + 5

                                y = pix.height - y

                                # Write on image
                                draw.text((x, y), text, fill="black", font=font)
                    
                    elif "PHONE NO" in b:
                        if len(b) == 86:
                            text = df['Contact No'][0]
                            if type(dic[b] == tuple):
                                x = dic[b][0][0] + 100
                                y = dic[b][0][3] + 5

                                y = pix.height - y

                                # Write on image
                                draw.text((x, y), text, fill="black", font=font)
                    
                    elif "CONTRACTOR" in b:
                        if len(b) == 85:
                            text = df['Contractor'][0]
                            if type(dic[b] == tuple):
                                x = dic[b][0][0] + 100
                                y = dic[b][0][3] + 5

                                y = pix.height - y

                                # Write on image
                                draw.text((x, y), text, fill="black", font=font)
                    
                    
                           
                    
                    elif "Plot" in b:
                        if len(b) == 162:
                            text = df['Plot No'][0]
                            text1 = df['Built Up Area'][0]
                            if type(dic[b] == tuple):
                                x = dic[b][0][0] + 80
                                y = dic[b][0][3] + 7

                                y = pix.height - y

                                # Write on image
                                draw.text((x, y), text, fill="black", font=font)
                                
                                
                                x = dic[b][0][0] + 260
                                y = dic[b][0][3] + 6

                                y = pix.height - y

                                # Write on image
                                draw.text((x, y), text1, fill="black", font=font)
                    

                    if check == 0:
                        if "Owner’s name" in b:
                            if i == int(dic[b][1]) - 1:
#                                 print("Owner’s name")
                                check = 1
                                text = df['Owner Name'][0]
                                
                                if type(dic[b] == tuple):
                                    x = dic[b][0][0] + 80
                                    y = dic[b][0][3] + 5

                                    y = pix.height - y

                                    # Write on image
                                    draw.text((x, y), text, fill="black", font=font)
                                    
                                    
                                    
                    
        # Save image
        img.save('output_image' + str(i) + '.png')
    # Convert images back to PDF
    pdf = FPDF()
    # Add images to PDF
    for i in range(len(doc)):
        pdf.add_page()
        pdf.image('output_image' + str(i) + '.png', 0, 0, 210, 297)  # A4 size
    
    
    
    folder_path = os.path.join("C:\\Users\\administrator\\Desktop\\YashK\\ArchcorpAISearch_DBC_ADBC_CIVIL\\AISearch_V5_CompareFeature\\assets", df['Project'][0].replace(" ", "_"), folder_name)
#     print("folder created")
    
    if not os.path.exists(folder_path):
        # Create the folder if it doesn't exist
        os.makedirs(folder_path)
    
    path = os.path.join(folder_path, file_name + file_ext)
    # path = "C:\\C:\\C:\\Users\\abhishek.singh\\Downloads\\modified_forms\\" + file_name + file_ext
    # Save PDF
    pdf.output(path, "F")
    
    


def word_insertion_in_docx(file_path, file_name, file_ext, folder_name, df):
#     print("we are inside word_insertion_in_docx")
    doc = Document(file_path)
    
    for paragraph in doc.paragraphs:
#         print(paragraph)
        for column_names in df.columns:  
            if column_names in paragraph.text:
#                 print(column_names)
                runs = paragraph.runs
                for i in range(len(runs)):
#                     print(runs[i].text)
                    if column_names in runs[i].text or 'Reference' in runs[i].text or runs[i].text in column_names:
                        runs[i].text = runs[i].text.replace(column_names + ":", column_names + ' : ' + df[column_names][0])
    
    folder_path = os.path.join("C:\\Users\\administrator\\Desktop\\YashK\\ArchcorpAISearch_DBC_ADBC_CIVIL\\AISearch_V5_CompareFeature\\assets", df['Project'][0].replace(" ", "_"), folder_name)
    
    
    
    if not os.path.exists(folder_path):
        # Create the folder if it doesn't exist
        os.makedirs(folder_path)
    
    path = os.path.join(folder_path, file_name + file_ext)
    doc.save(path)
    
    




import os
def get_files_info2(folder_path, authority_id, prerequisite_id, df):
    for root, dirs, files in os.walk(folder_path):
        for file_name in files:
            file_path = os.path.join(root, file_name)
            file_name, file_ext = os.path.splitext(file_name)
            folder_name = file_path.split('\\')
            folder_name = folder_name[-2]
            folder_number = folder_name.split(' ')[1]
            if int(folder_number) ==  int(authority_id):
                # print(folder_number)
                if file_ext == ".pdf":
                # function call to get the bounding box of all the words present in the pdf
                    sentence_coordinates = extract_sentence_coordinates(file_path)

                    dic = {}
                    for word, coordinates, page in sentence_coordinates:
                    #     print(f"Word: {word}")
                    #     print(f"Coordinates: {coordinates}\n")
                        dic[word] = [coordinates, page]
                    
#                     print(dic)
                    word_insertion(file_path, dic, file_name, file_ext, folder_name, df)

                elif file_ext == ".docx":
#                     print("we are here")
                    word_insertion_in_docx(file_path, file_name, file_ext, folder_name, df)
                    
        
