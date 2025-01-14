# Author: Jonathan Armoza
# Created: January 12, 2025
# Purpose: Contains paths to all of AOLM's datasets and functions that utilize
#          AOLM's text readers to read them

# Imports

# Built-ins
import json
import os

# Custom
from definitions import ROOT_DIR
from ia_huckfinn_reader import IAHuckFinnReader
from mtpo_huckfinn_reader import MTPOHuckFinnReader
from pg_huckfinn_reader import PGHuckFinnReader


# Globals

# Abbreviation constants

IA = "ia"
MTPO = "mtpo"
PG = "pg"

METADATA = "metadata"
TXT = "txt"

huckfinn_source_fullnames = {

    IA: "Internet Archive",
    MTPO: "Mark Twain Project Online",
    PG: "Project Gutenberg"
}

# Paths

huckfinn_directories = {

    IA: {
        "json": "{0}{1}data{1}twain{1}huckleberry_finn{1}internet_archive{1}txt{1}demarcated{1}complete{1}json{1}".format(ROOT_DIR, os.sep),
        "metadata": "{0}{1}data{1}twain{1}huckleberry_finn{1}internet_archive{1}metadata{1}".format(ROOT_DIR, os.sep),
        "txt": "{0}{1}data{1}twain{1}huckleberry_finn{1}internet_archive{1}txt{1}demarcated{1}complete{1}txt{1}".format(ROOT_DIR, os.sep),
    },
    MTPO: "{0}{1}data{1}twain{1}huckleberry_finn{1}mtpo{1}".format(ROOT_DIR, os.sep),
    PG: {
        "txt": "{0}{1}data{1}twain{1}huckleberry_finn{1}project_gutenberg{1}json{1}".format(ROOT_DIR, os.sep),
        "metadata": "{0}{1}data{1}twain{1}huckleberry_finn{1}project_gutenberg{1}metadata{1}".format(ROOT_DIR, os.sep),
    }
}

huckfinn_edition_names = {

    IA: [
        "adventureshuckle00twaiiala",
        "adventuresofhuc00twai",
        "adventuresofhuck00twai_9",
        "adventuresofhuck00twaiuoft",
        "adventuresofhuck1904twai",
        "cihm_50160",
        "dli.ernet.14052",
        "dli.ernet.470159"
    ],
    PG: [
        "2011-05-03",
        "2016-08-17",
        "2021-02-21"
    ]
}

huckfinn_text_filepaths = {

    IA: [f"{huckfinn_directories[IA][TXT]}{edition_name}_demarcated.json" for edition_name in huckfinn_edition_names[IA]],
    MTPO: f"{huckfinn_directories[MTPO]}MTDP10000_edited.xml",
    PG: [f"{huckfinn_directories[PG][TXT]}{edition_name}-HuckFinn.json" for edition_name in huckfinn_edition_names[PG]]
}

huckfinn_metadata_filepaths = {

    IA: [f"{huckfinn_directories[IA][METADATA]}{edition_name}-HuckFinn_metadata.json" for edition_name in huckfinn_edition_names[IA]],
    PG: [f"{huckfinn_directories[PG][METADATA]}{edition_name}-HuckFinn_metadata.json" for edition_name in huckfinn_edition_names[PG]]
}


def read_marktwain_project_online_text():

    mtpo_reader = MTPOHuckFinnReader(huckfinn_text_filepaths[MTPO])
    mtpo_reader.read()
    
    return mtpo_reader    

def read_huckfinn_metadata(p_source_id, p_edition_filenames=None):

    # 1. Determine filepaths to metadata files
    metadata_filepaths = huckfinn_metadata_filepaths[p_source_id]
    if None != p_edition_filenames:
        metadata_filepaths = []
        for edition_filename in p_edition_filenames:
            metadata_filepaths.append(f"{huckfinn_directories[p_source_id][METADATA]}{edition_filename}")

    # 2. Read in metadata on each <p_source_id> edition of Huckleberry Finn
    metadata_json = {}
    for subject_filepath in metadata_filepaths:
        with open(subject_filepath, "r") as json_file:
            metadata_json[os.path.basename(subject_filepath)] = json.load(json_file)

    return metadata_json

def read_huckfinn_text(p_source_id, p_edition_filenames=None):

    huckfinn_text_readers = {}

    # 1. Determine filepaths to text files
    text_filepaths = huckfinn_text_filepaths[p_source_id]
    if None != p_edition_filenames:
        text_filepaths = []
        for edition_filename in p_edition_filenames:
            text_filepaths.append(f"{huckfinn_directories[p_source_id][TXT]}{edition_filename}")

    # 2. Read in each <p_source_id> edition of Huckleberry Finn
    for filepath in text_filepaths:
        if PG == p_source_id:
            huckfinn_text_readers[os.path.basename(filepath)] = PGHuckFinnReader(filepath)
        else: # IA == p_source_id
            huckfinn_text_readers[os.path.basename(filepath)] = IAHuckFinnReader(filepath)
        huckfinn_text_readers[os.path.basename(filepath)].read()

    return huckfinn_text_readers