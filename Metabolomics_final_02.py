from PySimpleGUI import theme, Text, Submit, Cancel, InputText, FolderBrowse, FileBrowse, Window, Button, ChangeLookAndFeel, Checkbox
from os import chdir
from pandas import read_excel, ExcelWriter, concat, set_option

def Change(name, layout):
    global window
    window = Window(name, layout)

ChangeLookAndFeel('DefaultNoMoreNagging')





layout =[[Text("READ ME", size=(10,1), text_color='red')],

        [Text("Welcome, this program was made to process LC-MS features and peak areas by different applying "
"different cutoffs like retention time cutoffs, m/z value cutoffs, and relative standard deviation cutoffs of "
"averages. If the data was exported directly from mzMine, you can proceed forward with the data processing. If"
" not, ensure that the dataset meets these following requirements.", size=(60,6), text_color='black')],

        [Text("1. Ensure that you have 2 Blank sample which are names \"Blank_1.raw Peak area\" and \"Blank_2.raw "
"Peak area\". If you have more than two Blank samples, please manually process the rest.", size=(60,4), text_color='black')],

        [Text("2. Make certain that these columns are present in your dataset: \"row ID\", \"row m/z\", and \"row "
"retention time\" like they are presented from the mzMine data. ", size=(60,4), text_color='black')],

        [Text("3. If your data contains technical replicates, make sure they are an equal number of each technical"
" replicates for each sample and they are named sequentially.  Ex.  Bat_1, Bat_2, and Bat_3.", size=(60,5), text_color='black')],

        [Text("4. If your data contains biological replicates ensure there are an equal number of biological"
" replicates for each sample.If your data doesn't contain biological replicates, enter \"0\" when prompted.", size=(60,4), text_color='black')],
        [Button('Next -->')]
                 ]


Change('Metabolomics', layout)
event, values = window.read()





layout2 = [
            [Text('Save Folder', size=(23, 1)), InputText(), FolderBrowse()],
            [Text('Dataset File', size=(23, 1)), InputText(), FileBrowse()],
            [Text('New File Name', size=(23, 1)), InputText()],
            [Button('Next -->')]
                     ]

if event == ('Next -->'):
    window.close(); del window
    Change('Metabolomics', layout2)


layout3= [
            [Text('Blank Cutoff', size=(30, 1)), InputText()],
            [Text('Higher Retention Time Cutoff ', size=(30, 1)), InputText()],
            [Text('Lower Retention Time Cutoff ', size=(30, 1)), InputText()],
            [Text('Higher m/z Cutoff', size=(30, 1)), InputText()],
            [Text('Lower m/z Cutoff', size=(30, 1)), InputText()],
            [Text('RSD cutoff', size=(30, 1)), InputText()],
            [Text('# of Technical Replicates per sample', size=(30, 1)), InputText()],
            [Text('# of Biological Replicates per sample ', size=(30, 1)), InputText()],
            [Submit()]

            ]
event, values = window.read()
folder_path, filename, new_file = values[0], values[1],values[2]
window.close(); del window
if event == ('Next -->'):
    Change('Metabolomics', layout3)


                     

event, values = window.read()
blank_cutoff, higher_rt, lower_rt, higher_mz, lower_mz, rsd_cut, tech_amt, bio_amt= values[0], values[1],values[2],values[3],values[4],values[5],values[6],values[7]
chdir(folder_path)



#reading original document
set_option('display.float_format', '{:.3g}'.format)
df = read_excel(filename)
df = df.round(3)
writer = ExcelWriter((new_file+'.xlsx'), engine='xlsxwriter') #reading original document


#concatenate m/z and RT

df = df.drop(['row ID'], axis = 1)
df["mz/RT"] = df["row m/z"].astype(str) + '/'+ df["row retention time"].astype(str)
df = df.set_index('mz/RT')
df.to_excel(writer, sheet_name='original')

#delete blank
title = str("{:.2e}".format(int(blank_cutoff)))
df = df[df['Blank_1.raw Peak area']<=float(blank_cutoff)]
df = df.drop(['Blank_1.raw Peak area'], axis = 1)
df.to_excel(writer, sheet_name=title+ ' Blank Cutoff')


#m/z value cutoff

df = df[df['row m/z']<= float(higher_mz)]
df = df[df['row m/z']>= float(lower_mz)]
df.to_excel(writer, sheet_name= str(lower_mz) + '<mz<' + str(higher_mz))

#retention time cutoff

df = df[df['row retention time']>= float(lower_rt)]
df = df[df['row retention time']<= float(higher_rt)]
df.to_excel(writer, sheet_name= str(lower_rt) + '<rt<' + str(higher_rt))

#sorting samples

df = df.drop(['row retention time','row m/z'], axis = 1)
df = df.reindex(sorted(df.columns), axis=1)
name = list(df)


#new column names
new_names = []
for i in range(0, len(name), (int(tech_amt))):
    new_names.append(name[i])

#average technical replicates
df_mean = concat([df.iloc[:,i:i+(int(tech_amt))].mean(axis=1)for i in range(0,len(df.columns),int(tech_amt))], axis=1)
df_mean.columns = new_names
df_mean.to_excel(writer, sheet_name='average technical')


#RSD

df_std = concat([df.iloc[:,i:i+(int(tech_amt))].std(axis=1)for i in range(0,len(df.columns),int(tech_amt))], axis=1)
df_std.columns = new_names
df_rsd = df_std.div(df_mean)
df_rsd = df_rsd.fillna(0)
df_rsd.to_excel(writer, sheet_name='RSD values')


#RSD  cutoff

df_mean = df_mean[df_rsd <= float(rsd_cut)]
df_mean = df_mean.fillna(0)
df_mean.to_excel(writer, sheet_name='RSD cutoff')


# average biological replicate
if int(bio_amt)==0:
    print()
else:
    new_names_bio = []
    for i in range(0, len(new_names), (int(bio_amt))):
        new_names_bio.append(new_names[i])

    print(new_names_bio)
    print(new_names)

    df_bio_mean = concat([df_mean.iloc[:,i:i+(int(bio_amt))].mean(axis=1)for i in range(0,len(df_mean.columns),int(bio_amt))], axis=1) 
    df_bio_mean.columns = new_names_bio
    df_bio_mean.to_excel(writer, sheet_name='average biological')


writer.save()
window.close()


   
    





                 






  








