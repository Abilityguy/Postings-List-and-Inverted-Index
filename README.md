# Postings-List-and-Inverted-Index

## Postings list sample format
![alt text](Images/postings_list.png)

Each element is of the format [docID, word position ]. The word position is the position of the word after preprocessing. 

## Inverted Index sample format
![alt text](Images/inverted_index.png)

Each element is of the format [frequency of word, [postings_list] ]. The postings list is integrated into the inverted index.

## Details about files

### utils/process_raw_data.py 
This file is just to combine all the csv files into a single csv and save it somewhere. 

### generate_list_index.py
This file is to generate the postings list and inverted index and save it as pickle files for later use.

### postings_list.pkl
The saved dictionary of the postings list.

### inverted_index.pkl
The saved dictionary of the inverted index.

### The combined csv file
I have combined all the 480 csv files into a single one and have uploaded it [here](https://drive.google.com/file/d/1f6SX0i5eNJ8LA_WG4gVm3VR30FzG7Vqs/view?usp=sharing). The indexes of these files has been used as the docID for the postings list and inverted index.
