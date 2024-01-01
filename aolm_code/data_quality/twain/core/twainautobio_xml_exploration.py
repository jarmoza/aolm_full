# Imports

# Built-ins
import glob
import os
import statistics

# Third party
from bs4 import BeautifulSoup


# Globals

data_paths = {}
data_paths["root"] = "..{0}..{0}data{0}".format(os.sep)
data_paths["twain"] = { 

	"autobio": "{0}twain{1}autobiography{1}tei{1}". format(data_paths["root"], os.sep),
    "autobio_text_out": "{0}{1}output{1}twain_autobio{1}".format(os.getcwd(), os.sep)
}

# Dictionary for volume names:
filename_to_volume = {
    
    "MTDP10362.xml": "vol1",
    "MTDP10363.xml": "vol2",
    "MTDP10364.xml": "vol3"
}

# Get all Twain autobiography tei paths
tei_files = [tei_filepath for tei_filepath in glob.glob(data_paths["twain"]["autobio"] + "*")]

# Builds a block of text from input with tokens uniformly spaced and without endlines
def rebuild_text(p_text):

    formatted_text = p_text.replace("\n", " ")
    text_pieces = [token.strip() for token in formatted_text.split(" ") if len(token.strip()) > 0]
    formatted_text = " ".join(text_pieces)
    return formatted_text

def show_file_word_lengths(p_folder, p_extension):

    doc_lengths = []

    for filepath in glob.glob(p_folder + "*." + p_extension):
        with open(filepath, "r") as input_file:
            text_data = input_file.read()
            # print("{0}: {1}".format(os.path.basename(filepath), len(text_data.split(" "))))
            doc_lengths.append(len(text_data.split(" ")))

    print("Min: {0}".format(min(doc_lengths)))
    print("Max: {0}".format(max(doc_lengths)))
    print("Mean: {0}".format(statistics.mean(doc_lengths)))
    print("Mode: {0}".format(statistics.mode(doc_lengths)))
    print("Median: {0}".format(statistics.median(doc_lengths)))

# Takes a TEI Twain file and converts each of its body text's sections (div1 tags) into a separate txt file
def write_unaltered_text_to_file():

    # 1. Create a separate file for each section of the body of each autobiography volume
    soup = None
    for tei_filepath in tei_files:

        with open(tei_filepath, "r") as tei_file:

            # A. Read in tei file into BeautifulSoup structure
            soup = BeautifulSoup(tei_file.read(), "xml")

            # B. Get all div1 tags in the text body
            div1_body_tags = soup.find("text").find("body").find_all("div1")
            div1_body_text = [tag.get_text() for tag in div1_body_tags]

            # C. Output all body section text to separate files
            volume = filename_to_volume[os.path.basename(tei_filepath)]
            for index in range(len(div1_body_text)):
                with open("{0}{1}output{1}twain_autobio{1}twain_autobio_{2}_body_{3}.txt".format(os.getcwd(), os.sep, volume, index), 
                    "w") as output_file:
                    formatted_text = rebuild_text(div1_body_text[index])
                    output_file.write(formatted_text)


def main():

    # write_unaltered_text_to_file()

    show_file_word_lengths(data_paths["twain"]["autobio_text_out"], "txt")    

if "__main__" == __name__:
    main()