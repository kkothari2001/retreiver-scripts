import retriever as rt
import zipfile as zp
import geopandas as gpd
from difflib import HtmlDiff
import os
import shutil

# Download the datasets
datasets_tested = ['harvard-forest', 'bioclim']
for dataset in rt.reload_scripts():
    if(dataset.name in datasets_tested):
        rt.download(dataset.name, path="./downloaded-data")

# Extract the zip files into the appropriate folders and preprocess them as required
for zip_filename in os.listdir(path="./downloaded-data"):
    folder_name = zip_filename[:-4]
    folder_path = './raw-data/{}'.format(folder_name)

    print('Unzipping {} ...'.format(zip_filename))
    zip_ref = zp.ZipFile('./downloaded-data/{}'.format(zip_filename))
    zip_ref.extractall(folder_path)
    print("Extracted {}".format(zip_filename))
    zip_ref.close()
    '''
    If the zip contains only one subdirectory the files and directories inside must be brought up one level
    '''
    if len(os.listdir(folder_path)) == 1:
        print(zip_filename + " contained only one folder so lifting data 1 level up inside the raw-data folder!")
        subfolder_path = './raw-data/{folder}/{subfolder}'.format(
            folder=folder_name, subfolder=os.listdir(folder_path)[0])
        if os.path.isdir(subfolder_path):
            for filename in os.listdir(subfolder_path):
                print("Moving {}".format(filename))
                shutil.move(subfolder_path + "/" + filename,
                            folder_path+"/"+filename)

            shutil.rmtree(subfolder_path)

# Prepare the folders for conversion into csv and convert all .shp files into csv via geopandas library
if not os.path.exists('./new-data'):
    os.mkdir('./new-data')

for folder in os.listdir(path='./raw-data'):

    if not os.path.exists('./new-data/{}'.format(folder)):
        os.mkdir('./new-data/{}'.format(folder))

    for shapefile in os.listdir('./raw-data/{}'.format(folder)):
        if shapefile.endswith(".shp"):
            df = gpd.read_file("./raw-data/{}/{}".format(folder, shapefile))
            filename = shapefile[:-4] + ".csv"
            print("Creating {}".format(filename))
            df.to_csv("./new-data/{}/{}".format(folder, filename))
            del df

# Create the old-data folder if it doesn't exist
if not os.path.exists('./old-data'):
    print("No old data to compare to, creating it based on the new data downloaded")
    shutil.copytree('./new-data', './old-data')


# Create the diffs using the HtmlDiff class from difflib
if not os.path.exists('./diffs'):
    os.mkdir('./diffs')

for folder in os.listdir('./new-data'):

    if not os.path.exists('./diffs/{}'.format(folder)):
        os.mkdir('./diffs/{}'.format(folder))

    print("Finding differences in {}...".format(folder))
    for csv in os.listdir('./new-data/{}'.format(folder)):
        if csv.endswith(".csv"):
            html_diff = HtmlDiff()
            html_filename = csv[:-4] + ".html"
            with open('./new-data/{}/{}'.format(folder, csv), "r", encoding="ISO-8859-1") as new_file,\
                    open('./old-data/{}/{}'.format(folder, csv), "r", encoding="ISO-8859-1") as old_file, \
                    open('./diffs/{}/{}'.format(folder, html_filename), "w") as diff_file:
                diff_lines = html_diff.make_file(
                    old_file, new_file, context=True, numlines=1)  # Not very sure about how numlines works over here
                diff_file.writelines(diff_lines)
