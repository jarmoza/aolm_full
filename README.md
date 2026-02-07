# The Art of Literary Modeling

## Overview

Welcome to the repository for 'The Art of Literary Modeling' (AoLM), a PhD project and dissertation by [Jonathan Armoza](https://jonathanarmoza.com/) that develops a framework for measuring and assessing the data quality of corpora of digital literature in digital humanities research.

AoLM's code can be divided into three functional parts: reading in and processing digital texts and metadata into comparable components, making data quality measurements on those inputs, and assessing those measurement outputs together to determine the overall quality of the dataset. Accompanying and aiding this code is a small library of utility scripts for text processing and data visualization.

The core of AoLM is its data quality metrics, of which there are [six working examples](aolm_code/data_quality/core/dq_metrics). The repository's assessment code consists of a set of ['experiments'](experiments/chapter1) that run these data quality metrics over sample digital texts and metadata and then visualize, analyze, and output the metrics' measurements. Several public domain datasets of literature are also in the repository, including [14 digital editions of Mark Twain's 'Adventures of Huckleberry Finn'](data/twain/huckleberry_finn), [all 3 volumes of Twain's autobiography](data/twain/autobiography), [9 digital editions of novels by Herman Melville](data/melville/collected), and [digital editions of all of Emily Dickinson's poems and their variants (over 4800 files)](data/dickinson/eda). Each digital edition (novel/autobiography/poem) has been downloaded directly from their source archive online and processed to a minimal degree to aid their use by the AoLM's data quality metrics while maintaining a much of their rawness as possible. Each digital edition also is supplemented by a set of metadata about it provided by those source archives.

Below you will find documentation on all three functional parts of AoLM including a tutorial demonstrating how to work with data quality metrics. Additional, file by file documentation for code used in the final version of AoLM – as well as prototypical code that went unused for it – can be found in the 'Appendix' section of the written portion of 'The Art of Literary Modeling'. (Watch this space for a link to that writing once it is made public.)

## Table of Contents

1. [Text and Metadata Ingestion](#text-and-metadata-ingestion)
2. [Data Quality Metrics](#data-quality-metrics)
3. [Data Quality Metric Tutorial](#data-quality-metric-tutorial)
4. [Overall Data Quality Assessment](#overall-data-quality-assessment)


## Text and Metadata Ingestion

In order to measure the data quality of digital text files and metadata about them, AoLM processes those files into generalized components in order to compare them. AoLM's archive-specific reader objects make this possible. Below is a description of the JSON file formats for text and metadata as well as a description of those reader objects – which may be extended and modified using class inheritance for your own projects.

### Digital Text Processing

With AoLM's ethos of only using minimal intervention during the processing of digital texts in order to read them into computer memory for data quality measurement, the suggestion is to locate beginning and ends of the primary components of your raw digital source text. If there are subcomponents of the body text that you wish to isolate a consistent marker (i.e. `"CHAPTER <roman numeral>."`) is recommended and the [reader objects](aolm_code/objects) and text JSON format have implementations that accommodate both begin and end lines as well as text component prefixes. You can observe an example of chapter markers in this ['raw' text edition of _Adventures of Huckleberry Finn_](data/twain/huckleberry_finn/internet_archive/txt/demarcated/complete/txt/adventuresofhuc00twai_demarcated.txt).


### Text JSON File Format Description

The text JSON file format has two sections: `keys` and `component`. `keys` are mostly to help external scripts navigate the raw input `txt` file of the work and to describe the output from text processing that will appear in the `components` section. For an example file to see how this is laid out look at [the February 2021 edition of _Adventures of Huckleberry Finn_ on Project Gutenberg](data/twain/huckleberry_finn/project_gutenberg/json/2021-02-21-HuckFinn.json).

The `keys` section contains `order`, `input`, and `output` subsections. `order` defines the order of the primary components of the text (i.e. `[header, frontmatter, body, footer]`). A `startline` and `endline` are defined for each of those text components in the `input` subsection. The `output` subsection specifies the key that will be used in the file's `component` section. As you will see in the example file, `body` is a special case in that in contains subcomponents (e.g. chapters for a novel). NOTE: The prefix to be used to find those subcomponents in the raw text is specified in the `body` input subsection, and a prefix for the chapters as they will appear in the `component` section is specified in the `output` subsection.

### Metadata JSON File Format Description

The metadata JSON files used by the metadata sufficiency metric (AoLM's only metadata metric) is somewhat straightforward. As can be seen in [this example of metadata from the Internet Archive](data/twain/huckleberry_finn/internet_archive/metadata/adventureshuckle00twaiiala-HuckFinn_metadata.json), key-value pairs from the source archive's metadata are simply listed in the file. However, in cases where metadata must be manually extracted, AoLM's metadata file format (and metadata metric) also includes an `unkeyed_fields` key where such key-value pairs can be placed. See [this metadata file from the February 2021 edition of _Adventures of Huckleberry Finn_](data/twain/huckleberry_finn/project_gutenberg/metadata/2021-02-21-HuckFinn_metadata.json) for example.

### Reading in Text JSON Files Using Reader Objects`

AoLM uses reader objects to ingest texts from the format of its text JSON file into memory as a set of generalized components that its metric objects can use to make tallies and evaluative measurements from.

AoLM's scheme for doing this uses object-oriented programming class inheritance beginning with a [`AOLMText` object](aolm_code/objects/aolm_text.py) which is used [the base reader class, `AOLMTextReader`](aolm_code/objects/aolm_textreader.py). Child classes that derive from `AOLMTextReader` are created for texts coming from specific source archives so that the reading/ingestion functionality can be tailored to inputs coming from those sources. See for example, [the Internet Archive reader for _Huckleberry Finn_ editions](aolm_code/objects/ia_huckfinn_reader.py) as opposed to [the Mark Twain Project Online reader for _Huckleberry Finn_ editions](aolm_code/objects/mtpo_huckfinn_reader.py).

## Data Quality Metrics

Each data quality metric is part of what is called a "data quality assessment framework in Information Science. AoLM uses as foundation many of the concepts concerning data quality from the field and specifically from information scientist Laura Sebastian-Coleman in her book, "Measuring Data Quality for Ongoing Improvement (2012).

The metrics implemented for the project reflect several core categories for data quality that Sebastian-Coleman listed in the table below. However, metrics themselves are relatively straightforward to create on your own. In order to begin creating your own metrics, have a look at [`dq_metric.py](aolm_code/data_quality/core/dq_metric.py). This acts as the base class to derive from for metrics. It contains the core functionality needed. Its core functions include the constructor, `compute`, `evaluate`, and output methods. Your derived child class can and likely will include more helper functionality. Take a look at the code for my own metrics in the [aolm_code/data_quality/core/dq_metrics](aolm_code/data_quality/core/dq_metrics) folder to see examples of expanded metric functionality.

| name                             | category         | dimensions                     | function                                               |
|----------------------------------|------------------|--------------------------------|--------------------------------------------------------|
| lexical validity                 | intrinsic        | - accuracy                     | comparing data against external objects                |
|                                  |                  | - objectivity                  |                                                        |
|                                  |                  | - believability                |                                                        |
|                                  |                  | - reputation                   |                                                        |
| record consensus                 | representational | - interpretability             | the intelligibility of data                            |
|                                  |                  | - ease of understanding        |                                                        |
|                                  |                  | - representational             |                                                        |
|                                  |                  | - consistency                  |                                                        |
|                                  |                  | - representational conciseness |                                                        |
| metadata sufficiency             | contextual       | - amount of value-added        | measurements based on the task or use case(s) for data |
|                                  |                  | - relevancy                    |                                                        |
|                                  |                  | - timeliness                   |                                                        |
|                                  |                  | - completeness                 |                                                        |
|                                  |                  | - appropriate amount of data   |                                                        |
| record counts to control records | contextual       | “                              |                                                        |
| authorial signature              | representational | “                              |                                                        |
| legomena                         | representational | “                              |                                                        |

### Lexical Validity

The lexical validity metric utilizes three external dictionaries ([spaCy](https://spacy.io/), [the Corpus of Historical American English](https://www.english-corpora.org/coha/), and [WordNet](https://wordnet.princeton.edu/)) to check if a token in a digital text is a valid/known English word. It evaluates this measurement at the chapter, edition, and corpus level.

### Record Consensus

The record consensus metric takes a set of digital editions and sees how much of a works words and sentences match above a given percent match threshold across all editions. It does this at the chapter, edition, and corpus level.

### Metadata Sufficiency

The metadata sufficiency metric looks at metadata of digital editions that source from the same digital archive and considers the percent coverage of metadata keys as well as the percent of mismatch between (potentially) differently keyed values for those metadata keys.

### Record Counts to Control Record

The record counts to control record metric compares a set of editions against a (presumed) master edition to understand how much each of those compared editions' words and sentences and chapters match with those of the master edition. It evaluates these measures at the chapter, edition, and corpus level.

### Authorial Signature

The authorial signature metric determines the average (document-length normalized) term frequency vector for a collection of digital texts and then measures the distance between each edition's term frequency vector (also normalized) to determine the distance each digital edition is that "authorial signature" average vector.

### Legomena

The legmona metric works similarly to the authorial signature except in this case it looks to the n-legomena (i.e. hapax legomena are words used just once in a body of text, dis legemona are words used twice, etc.) featured in a set of digital texts ('n' is specified by the user of the metric). An average, normalized legomena vector is determined for the whole set of digital texts, but this measurement also occurs at the chapter and edition level.

## Data Quality Metric Tutorial

This tutorial will guide you through a sample exercise in _reading a dataset of digital texts_, _running the record counts to control records data quality metric_ over them, and _producing output files_ from the metric. The example dataset for the tutorial will be a set of editions of Mark Twain's 'Adventures of Huckleberry' sourced from the 'Internet Archive', 'Project Gutenberg', and 'Mark Twain Project Online' at University of California, Berkeley. 

Comments and pseudocode for this tutorial are found in `aolm_tutorial.py` in the `tutorial` folder which acts as a workspace for you to add code to as you follow along with the tutorial. Follow along with the steps outlined below and place your code in that script file in the `tutorial_workspace` function. Once you have run the script, the output files for this tutorial will be found in the `tutorial/output` folder. If you are satisfied with the results, you may choose to perform your own exercises with running different data quality metrics in the `aolm_code/data_quality/core/dq_metrics` folder. Note that you will need some beginner-level Python proficiency to follow along with the tutorial. The full tutorial solution along with some extra commentary on it can be found in `tutorial_solution.py`.

Functionality to enable further exercises and explorations of AoLM's metrics and datasets can be found in `cli_lib.py` as well as via a script to run AoLM's data quality metrics at the command line in `aolm_cli.py`.

Instructions on how to read digital texts into memory for use by data quality metric objects and how to create assessment code for their outputs can be found [here]().

### Environment Setup

#### 1. _Copy the 'Art of Literary Modeling' GitHub repository to your computer_

In your terminal, run `git clone https://github.com/jarmoza/aolm_full` in a location on your hard drive where you would like the 'Art of Literary Modeling' code repository to live.

#### 2. _Installing Anaconda_ (OS-specific Instructions)

Check to see if 'conda' is installed on your system already by running `conda --version`.

If you do not yet have Anaconda ('conda') installed on your system, run the following
commands in your terminal:

**Windows**
- `curl -LO https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Windows-x86_64.exe`
- `start "" /wait Miniforge3-Windows-x86_64.exe /InstallationType=JustMe /AddToPath=1 /S`
- `conda --version`
    
**macOS, Apple silicon**
- `curl -LO https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-MacOSX-arm64.sh`
- `bash Miniforge3-MacOSX-arm64.sh -b`
- `source ~/miniforge3/bin/activate`
- `conda --version`

**macOS, Intel**
- `curl -LO https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-MacOSX-x86_64.sh`
- `bash Miniforge3-MacOSX-x86_64.sh -b`
- `source ~/miniforge3/bin/activate`
- `conda --version`

**Linux**
- `curl -LO https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-x86_64.sh`
- `bash Miniforge3-Linux-x86_64.sh -b`
- `source ~/miniforge3/bin/activate`
- `conda --version`

#### 3. _Install the 'conda' environment_ for 'Art of Literary Modeling' 

In the *aolm_full*  folder in your terminal, run `conda env create -f environment.yml`

#### 4. _Activate the 'conda' environment_

Next, run `conda activate aolm`. Repeat *only* this last command when you want to re-run
the tutorial script in the terminal. (To exit the 'aolm' conda environment, run `conda deactivate`.)

#### 5. _Install the required spaCy models_

`python3 -m spacy download en_core_web_lg`
`python3 -m spacy download en_core_web_sm`

### Tutorial

#### 1. _Define parameters_ for reading data and running a metric (optional)

The first thing you will do is define string variables for IDs and folder paths that will be used for reading digital texts/metadata and then later, running a data quality metric(s) over those texts/metadata. (This step can be skipped if you don't mind entering raw parameter values into function/constructor calls.) These are used by AoLM's reader objects and data quality metric objects. A set of pre-defined values for these parameters have been placed at the top of the tutorial script for your convenience.

##### A. File Locations

Define one (or two) variables for the locations of your digital editions. As mentioned, pre-defined dataset and metadata location paths have been placed at the top of the tutorial file, including a `TUTORIAL_DATASET_LOCATION`.

    EDITIONS_LOCATION = 'mypath/to/digital_edition/files'
    METADATA_LOCATION = 'mypath/to/metadata/files'

##### B. Unique String IDs

Define variables for IDs for the digital source of the compared editions and any baseline edition (e.g. metrics like 'record counts to control records' that use a baseline edition). Some metrics will not require either ID if they are not comparing across digital sources. 

    TUTORIAL_BASELINE_SOURCE_ID = 'mark_twain_project'
    TUTORIAL_SOURCE_ID = 'internet_archive'
    TUTORIAL_METRIC_ID = 'my_unique_metric_id'
    TUTORIAL_COLLECTION_TITLE = 'Internet Archive'
    TUTORIAL_WORK_TITLE = 'Adventures of Huckleberry Finn'å

#### 2. _Read editions and/or metadata_

The next step is to read in the digital edition files and/or metadata files you wish to use for your metric(s). AoLM uses custom JSON file formats for both editions and metadata. (How to build these from raw digital texts/metadata will be explained in a future tutorial, but you may examine the edition and metadata files in the `tutorial/data` folder.) For this tutorial, two convenience functions `read_huckfinn_dataset_files_by_source` and `read_metadata_files_by_source` have been provided for your use. You only need to specify the editions/metadata location and the string ID that represents the subfolder they are stored in (i.e. 'internet_archive').

    edition_readers = read_huckfinn_dataset_files_by_source(
        EDITIONS_LOCATION, TUTORIAL_SOURCE_ID)
    edition_readers.update(read_huckfinn_dataset_files_by_source(
        EDITIONS_LOCATION, TUTORIAL_BASELINE_SOURCE_ID))

    metadata_files = read_metadata_files_by_source(METADATA_LOCATION, TUTORIAL_SOURCE_ID)

#### 3. _Run a data quality metric_ over the editions and/or metadata

This next step is where you get to choose which data quality metric(s) you wish to run on your editions or metadata. The available AoLM metrics include: 'record consensus', 'record counts to control records', 'lexical validity', 'metadata suffiency', 'authorial signature', and 'legomena'. Each class name you will need for these metrics can be found at the top of the tutorial script file in the section that lists all of the imports. This tutorial uses the 'record counts to control records' metric. (Its class name is `DatasetCompleteness_RecordCountsToControlRecords`.)

First, create the metric object and give it the parameters its constructor requires. (To see where these metric class constructors are defined look at the Python files in *aolm_code/data_quality/core/dq_metrics*. In the `class` section you will see a constructor definition that begins with `def __init__(...):`. This is where you will find the class object's required parameters. However, there is also a general `create_metric` function in `cli_lib.py` that is also used by AoLM's command line script to create metric objects.)

    metric = DatasetCompleteness_RecordCountsToControlRecords(
        TUTORIAL_METRIC_ID,
        edition_readers,
        TUTORIAL_SOURCE_ID,
        TUTORIAL_WORK_TITLE,
        TUTORIAL_COLLECTION_TITLE,
        EDITIONS_LOCATION,
        TUTORIAL_BASELINE_SOURCE_ID
    )

Congratulations! You have just created your first data quality metric object.

Each metric object performs two steps to produce its metric and submetric values. The metric object's `compute` function tallies the values of the editions or metadata it uses for producing the final metric values. Then the metric object's `evaluate` function calculates statistics based on those tallies to produce the metric and submetric values.

    metric.compute()

    metric.evaluate()

#### 4. _Output results_ (for inspection, analysis, and visualization)

In this final step, you will output both the tallies and the metric and submetric values of the data quality metric you just ran. Since the implementation of outputting these values has yet to be standardized across AoLM metrics, two convenience functions, `output_metric_tallies` and `output_metric_values` have been provided for your use. The former outputs a CSV file and the latter, a JSON file for the 'record counts' metric. There has been an [`output`](tutorial/output) folder provided in the [`tutorial`](tutorial) folder for your convenience. (NOTE: Most other metrics produce JSON file for their 'tallies'.) A `script_run_time` variable has also been provided in the `tutorial_workspace` function of `aolm_tutorial.py` if useful for timestamping your outputs.
    
    output_metric_tallies(metric, 'my/output/path/metric_tallies_' + script_run_time + '.csv')

    output_metric_values(metric, 'my/output/path/metric_values_'  + script_run_time + '.json')

#### 5. _Interpret the results_ in the output files

**Metric Tallies File**

The first stage of a metric (called `compute`) tallies the components of a corpus of digital texts it intends to evaluate for data quality. In this case with the record counts to control record metric, the tallies output CSV file will contain percent match of the words and sentences of each chapter of each edition.

The column headers include: `edition_name`, `chapter_name`, `count_type`, and `percent`.

**Metric Values File**

The second stage of a metric (called `evaluate`) takes the tallies from the first stage and performs some light statistical calculations over them in order to determine the 'data quality' of the corpus. This includes multiple levels of sub-metrics that eventually are all used to calculate the final overall metric data quality value. All of this information is output in hiearchical JSON form with descriptive key names. Output values include the overall metric value, the percent match for the corpus for chapter count, word count, and sentence count, the total percent coverage calculation concerning chapters/words/sentences for each edition, and the sub-sub-metric values of the percent matches of those items for each edition.

## Overall Data Quality Assessment

The concept of a data quality assessment framework (DQAF) includes the notion that all of the metrics one performs over a dataset should then be used in concert to help determine an overall data quality measurement for that dataset.

An assessment sums up all of the data quality work you have been performing with a timestamp attached that states, "This was the determined quality of the dataset using these measures at this day/time." Data quality assessment is meant to be iterative work that is performed at intervals, depending on how often a dataset is updated.

One simple form of assessment calculation could simply be a weighted average of overall data metric values – with weights determined according to your own judgment of the importance of a particular metric in determining a dataset's quality rating. (Although assessment calculations can be as complicated as one deems.)

The script [`huckfinn_dataquality.py`](experiments/chapter1/huckfinn_dataquality.py) in the [`experiments` folder](experiments/chapter1) provides a good example of multiple data metrics being used together. The assessment calculation can then be made via script or manually based on the metric outputs.