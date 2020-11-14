import csv

from os import listdir
from os.path import isfile, join


FOLDER_PATH_SOURCE = './archive'
FOLDER_PATH_XML = './archive_xml'


def read_folder(folder_path):
    filenames = [str(f) for f in listdir(folder_path) if isfile(join(folder_path, f))]
    return filenames

def read_csv(folder, file):
    with open('{}/{}'.format(folder, file), newline='', encoding='utf8') as csvfile:
        csv_data = csv.reader(csvfile, delimiter=',')
        return_data = []

        # url, matchdatetime, station, show, showid, preview, Snippet
        
        for (index, data) in enumerate(csv_data):
            if index!=0:
                row_dict = dict()
                row_dict['filename'] = str(file)
                row_dict['url'] = str(data[0])
                row_dict['datetime'] = str(data[1])
                row_dict['station'] = str(data[2])
                row_dict['show'] = str(data[3])
                row_dict['showid'] = str(data[4])
                row_dict['preview'] = str(data[5])
                row_dict['snippet'] = str(data[6])

                return_data.append(row_dict)
    
    return return_data 

def write_xml(folder, file, row_dict):
    with open('{}/{}.xml'.format(folder, file), "w", encoding="utf-8") as xml_file:
        xml_file.write("<add>\n")
        xml_file.write("<doc>\n")

        for key in row_dict:
            # print(key, row_dict[key])
            xml_file.write('<field name="{}">{}</field>\n'.format(key, row_dict[key]))

        xml_file.write("</doc>\n")
        xml_file.write("</add>\n")


if __name__ == "__main__":
    
    all_csv_data = []
    file_paths = read_folder(FOLDER_PATH_SOURCE)
    for file in file_paths:
        file_data = read_csv(FOLDER_PATH_SOURCE, file)
        for row in file_data:
            all_csv_data.append(row)
    index = 10
    for row in all_csv_data:
        write_xml(FOLDER_PATH_XML, str(index), row)
        index = index + 1

