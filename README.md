# The Art of Literary Modeling

## Overview

Welcome to the repository for 'The Art of Literary Modeling' (AoLM), a PhD project and dissertation by [Jonathan Armoza](https://jonathanarmoza.com/) that develops a framework for measuring and assessing the data quality of corpora of digital literature in digital humanities research.

### Functionality and Code

AoLM's code can be divided into three functional parts: (1) reading in and processing digital texts and metadata into comparable components, (2) making data quality measurements on those inputs, and (3) assessing those measurement outputs together to determine the overall quality of the dataset.

The core of AoLM is its data quality metrics, of which there are [six working examples](aolm_code/data_quality/core/dq_metrics). The repository's assessment code consists of a set of [workflow scripts dubbed 'experiments'](experiments/chapter1) that run these data quality metrics over sample corpora of digital texts and metadata and then output all of the metrics' measurements to file and/or plot select metric measurements for visual comparison.

Accompanying and aiding that reading/measurement/assessment code is a small library of utility scripts for text processing and data visualization. Text processing code used by the final version of the project can be found in the [aolm_code/objects](aolm_code/objects) and [aolm_code/utilities](aolm_code/utilities) folders, and visualization code can be found within the 'experiment' and separate plotting scripts in the [experiments/chapter1](experiments/chapter1) folder.

Below, you will find documentation on all three functional parts of AoLM including a tutorial demonstrating how to work with data quality metrics. Additional, file-by-file documentation for code used in the final version of AoLM – as well as prototypical code that went unused for it – can be found in the 'Appendix' section of the written portion of 'The Art of Literary Modeling'. (Watch this space for a link to that writing once it is made public.)

NOTE: Any script in the AoLM repository requires the installation and activation of the 'aolm' conda environemnt. See the setup section of the [data quality metric tutorial](#data-quality-metric-tutorial) for installing this environment on your system from the command line.

### Accompanying Datasets

Several public domain datasets of literature are also in the repository, including [14 digital editions of Mark Twain's _Adventures of Huckleberry Finn_](data/twain/huckleberry_finn) from [Project Gutenberg](https://www.gutenberg.org/), the [Internet Archive](https://archive.org/), and [Mark Twain Project Online](https://legacy.mtpo2.org/landing_writings.shtml), [all 3 volumes of Twain's autobiography](data/twain/autobiography) from Mark Twain Project Online, [9 digital editions of novels by Herman Melville](data/melville/collected)  from Project Gutenberg, and [digital editions of all of Emily Dickinson's poems and their variants (over 4800 files)](data/dickinson/eda) from [Emily Dickinson Archive](https://www.edickinson.org/). Each digital edition (novel/autobiography/poem) has been downloaded directly from their source archive online and processed to a minimal degree to aid their use by AoLM's data quality metrics while maintaining as much of their rawness as possible. Each digital edition is also supplemented by a set of metadata about it provided by those source archives.

## Table of Contents

1. [Text and Metadata Ingestion](#text-and-metadata-ingestion)
2. [Data Quality Metrics](#data-quality-metrics)
3. [Data Quality Metric Tutorial](#data-quality-metric-tutorial)
4. [Workflow Scripts and Overall Data Quality Assessment](#workflow-scripts-and-overall-data-quality-assessment)
5. [Command Line Tool](#command-line-tool)


## Text and Metadata Ingestion

In order to measure the data quality of digital text files and metadata about them, AoLM processes those files into generalized components in order to compare them. AoLM's [archive-specific reader objects](aolm_code/objects) make this possible. Below is a description of the JSON file formats for text and metadata as well as a description of those reader objects – which may be extended and modified using class inheritance for your own projects.

### Digital Text Processing

With AoLM's ethos of only using minimal intervention during the processing of digital texts in order to read them into memory for data quality measurement, the suggestion is to locate beginning and ends of the primary components of your raw digital source text. If there are subcomponents of the body text that you wish to isolate, inserting a consistent demarcation marker (i.e. `"CHAPTER <roman numeral>."`) is recommended. The [reader objects](aolm_code/objects) and text JSON format have implementations that accommodate both begin and end lines as well as text component demarcation markers. You can observe an example of chapter markers in this ['raw' text edition of _Adventures of Huckleberry Finn_](data/twain/huckleberry_finn/internet_archive/txt/demarcated/complete/txt/adventuresofhuc00twai_demarcated.txt).


### Text JSON File Format Description

AoLM's text JSON file format has two sections: `keys` and `component`. The `keys` section contains values to help a text processing script navigate the raw input `txt` file of the work and values to describe the output from text processing that will appear in the `components` section. AoLM uses the [`IAHuckFinnWriter` class object](aolm_code/data_quality/twain/internet_archive/ia_huckfinn_writer.py) to do this work - where the JSON file's `keys` section is filled out by the user and then the paths to the raw txt and that JSON file are given to `IAHuckFinnWriter` to produce the `components` section of the JSON file. (The resulting completed JSON file can then be read into memory by a reader object. See below.) See this example of a completed JSON version of [the February 2021 edition of _Adventures of Huckleberry Finn_ on Project Gutenberg](data/twain/huckleberry_finn/project_gutenberg/json/2021-02-21-HuckFinn.json).

The `keys` section contains `order`, `input`, and `output` subsections. `order` defines the order of the primary components of the text (i.e. `[header, frontmatter, body, footer]`). A `startline` and `endline` are defined for each of those text components in the `input` subsection. The `output` subsection specifies the key that will be used in the file's `component` section. As you will see in the example file, `body` is a special case in that it contains subcomponents (i.e. chapters for a novel). NOTE: The prefix to be used to find those subcomponents in the raw text is specified in `body` in the input subsection under the key `subcomponent_input_prefix`. A prefix for those subcomponents (chapters) as they will appear in the `component` section is specified in `body` in the `output` subsection.

### Metadata JSON File Format Description

The metadata JSON files used by the metadata sufficiency metric, AoLM's only metadata metric, is more straightforward. See this example of [metadata from the Internet Archive](data/twain/huckleberry_finn/internet_archive/metadata/adventureshuckle00twaiiala-HuckFinn_metadata.json). Here key-value pairs from the source archive's metadata are simply listed in the file. However, in cases where metadata must be manually extracted (i.e. from within the provided raw text like Project Gutenberg editions), AoLM's metadata file format (and metadata metric) also allows for an `unkeyed_fields` key where such key-value pairs can be placed separately from metadata that was specifically provided separately by the source archive. See [this metadata file from the February 2021 Project Gutenberg edition of _Adventures of Huckleberry Finn_](data/twain/huckleberry_finn/project_gutenberg/metadata/2021-02-21-HuckFinn_metadata.json) for an example of that scenario.

### Reading in Text JSON Files Using Reader Objects

AoLM uses reader objects to load texts from their JSON file format into memory as a set of generalized components that its metric objects can use to make tallies and evaluative measurements from.

AoLM's scheme for doing this uses object-oriented programming class inheritance beginning with a [`AOLMText` object](aolm_code/objects/aolm_text.py) which is used in [the base reader class, `AOLMTextReader`](aolm_code/objects/aolm_textreader.py). Child classes that derive from `AOLMTextReader` are created for texts coming from specific source archives so that the reading/ingestion functionality can be tailored to inputs coming from those sources. See for example, [the Internet Archive reader for _Huckleberry Finn_ editions](aolm_code/objects/ia_huckfinn_reader.py) as opposed to [the Mark Twain Project Online reader for _Huckleberry Finn_ editions](aolm_code/objects/mtpo_huckfinn_reader.py).

## Data Quality Metrics

Each data quality metric is part of what is called a "data quality assessment framework" (DQAF) in Information Science. AoLM uses as its foundation many of the concepts concerning data quality from the field and specifically from information scientist Laura Sebastian-Coleman in her book, _Measuring Data Quality for Ongoing Improvement_ (2012).

The metrics implemented for the project reflect several core categories for data quality provided by Sebastian-Coleman, and are listed in the table below. In order to begin creating your own metrics, have a look at [`dq_metric.py](aolm_code/data_quality/core/dq_metric.py). This script defines the base class to derive from for your own metrics, and contains the core functionality needed for a metric object. Those core functions include the constructor, `compute`, `evaluate`, and output methods. Your derived child class can and likely will include more helper functionality. Take a look at the code for my own metrics in the [aolm_code/data_quality/core/dq_metrics](aolm_code/data_quality/core/dq_metrics) folder to see examples of derived/expanded metric functionality.

| name                             | category         | dimensions                     | function                                               |
|----------------------------------|------------------|--------------------------------|--------------------------------------------------------|
| [lexical validity](aolm_code/data_quality/core/dq_metrics/dataset_validity/lexical_validity.py)                 | intrinsic        | - accuracy                     | comparing data against external objects                |
|                                  |                  | - objectivity                  |                                                        |
|                                  |                  | - believability                |                                                        |
|                                  |                  | - reputation                   |                                                        |
| [record consensus](aolm_code/data_quality/core/dq_metrics/dataset_consistency/consistency_recordconsensus.py)                 | representational | - interpretability             | the intelligibility of data                            |
|                                  |                  | - ease of understanding        |                                                        |
|                                  |                  | - representational             |                                                        |
|                                  |                  | - consistency                  |                                                        |
|                                  |                  | - representational conciseness |                                                        |
| [metadata sufficiency](aolm_code/data_quality/core/dq_metrics/dataset_completeness/metadata_sufficiency.py)             | contextual       | - amount of value-added        | measurements based on the task or use case(s) for data |
|                                  |                  | - relevancy                    |                                                        |
|                                  |                  | - timeliness                   |                                                        |
|                                  |                  | - completeness                 |                                                        |
|                                  |                  | - appropriate amount of data   |                                                        |
| [record counts to control records](aolm_code/data_quality/core/dq_metrics/dataset_completeness/recordcounts_to_controlrecords.py) | contextual       | “                              |                                                        |
| [authorial signature](aolm_code/data_quality/core/dq_metrics/dataset_signature/authorial_signature.py)              | representational | “                              |                                                        |
| [legomena](aolm_code/data_quality/core/dq_metrics/dataset_signature/legomena.py)                         | representational | “                              |                                                        |

### Lexical Validity

The [lexical validity](aolm_code/data_quality/core/dq_metrics/dataset_validity/lexical_validity.py) metric utilizes three external dictionaries ([spaCy](https://spacy.io/), [the Corpus of Historical American English](https://www.english-corpora.org/coha/), and [WordNet](https://wordnet.princeton.edu/)) to check if tokens in a digital text are valid/known English words. It evaluates this measurement at the chapter, edition, and corpus level.

### Record Consensus

The [record consensus](aolm_code/data_quality/core/dq_metrics/dataset_consistency/consistency_recordconsensus.py) metric takes a set of digital editions and sees how much of a work's words and sentences match above a given percent match threshold across all editions. It does this at the chapter, edition, and corpus level.

### Metadata Sufficiency

The [metadata sufficiency](aolm_code/data_quality/core/dq_metrics/dataset_completeness/metadata_sufficiency.py) metric looks at metadata among digital editions that source from the same digital archive and considers the percent coverage of metadata keys as well as the percent of mismatch between (potentially) identical, but differently keyed values for those metadata keys.

### Record Counts to Control Records

The [record counts to control records](aolm_code/data_quality/core/dq_metrics/dataset_completeness/recordcounts_to_controlrecords.py) metric compares a set of editions against a (presumed) master edition to understand how much each of those compared editions' words and sentences and chapter counts match with those of the master edition. It evaluates these measurements at the chapter, edition, and corpus level.

### Authorial Signature

The [authorial signature](aolm_code/data_quality/core/dq_metrics/dataset_signature/authorial_signature.py) metric determines the average (document-length normalized) term frequency vector for a collection of digital texts and then measures the distance between each edition's term frequency vector (also normalized) to determine the distance each digital edition is from that "authorial signature" average vector. (NOTE: This produces a data quality measure in different terms than the percentages of the previous metrics.)

### Legomena

The [legomena](aolm_code/data_quality/core/dq_metrics/dataset_signature/legomena.py) metric looks to the n-legomena featured in a set of digital texts – where 'n' is specified by the user of the metric. (Hapax legomena are words used just once in a body of text, dis legemona are words used twice, etc.) Vectors are computed consisting of the average counts for each legomena word for each chapter and edition. The average legomena total of those counts is calculated for the whole set of digital texts, and the average legomena count per work is considered as the final metric value. (This follows with the authorial signature's metric data quality measure as something other than a percent.)

## Data Quality Metric Tutorial

This tutorial will guide you through a sample exercise in (1) _reading a dataset of digital texts_, (2) _running the record counts to control records data quality metric_ over them, and (3) _producing output files_ from the metric. The example dataset for the tutorial will be a set of editions of Mark Twain's _Adventures of Huckleberry_ sourced from the [Internet Archive](https://archive.org/), [Project Gutenberg](https://www.gutenberg.org/), and [Mark Twain Project Online](https://legacy.mtpo2.org/landing_writings.shtml) at University of California, Berkeley. 

Comments and pseudocode for this tutorial are found in [`aolm_tutorial.py`](tutorial/aolm_tutorial.py) in the [`tutorial`](tutorial) folder which acts as a workspace for you to add code to as you follow along with the tutorial. Follow along with the steps outlined below and place your code in that script file in the `tutorial_workspace` function. Once you have run the script, the output files for this tutorial will be found in the [`tutorial/output`](tutorial/output) folder. If you are satisfied with the results, you may choose to perform your own exercises by running different data quality metrics from the [`aolm_code/data_quality/core/dq_metrics`](aolm_code/data_quality/core/dq_metrics) folder. Note that you will need some beginner-level Python proficiency to follow along with the tutorial. The full tutorial solution along with some extra commentary on it can be found in [`tutorial_solution.py`](tutorial/tutorial_solution.py).

Functionality to enable further exercises and explorations of AoLM's metrics and datasets can be found in [`cli_lib.py`](tutorial/cli_lib.py) as well as via a script to run AoLM's data quality metrics at the command line in [`aolm_cli.py`](tutorial/aolm_cli.py). (NOTE: `aolm_cli.py` functions as a **command-line tool for AoLM** and has still to be fully tested. See the [command line tool](#command-line-tool) section below.)

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

In the *aolm_full* folder in your terminal, run `conda env create -f environment.yml`

#### 4. _Activate the 'conda' environment_

Next, run `conda activate aolm`. Repeat *only* this last command when you want to re-run
the tutorial script in the terminal. (To exit the 'aolm' conda environment, run `conda deactivate`.)

#### 5. _Install the required spaCy models_

AoLM's metrics require the use two of spaCy's language models. Run the following commands in your terminal to download them:

`python3 -m spacy download en_core_web_lg`
`python3 -m spacy download en_core_web_sm`

### Tutorial

#### 1. _Define parameters_ for reading data and running a metric (optional)

The first thing you will do is define string variables for IDs and folder paths that will be used for reading digital texts/metadata and then later, running a data quality metric(s) over those texts/metadata. (This step can be skipped if you don't mind repeatedly entering raw string values into function/constructor calls.) These are used by AoLM's reader objects and data quality metric objects. A set of pre-defined values for these parameters have been placed at the top of the tutorial script for your convenience.

##### A. File Locations

Define one (or two) variables for the locations of your digital editions. As mentioned, pre-defined dataset and metadata location paths have been placed at the top of the tutorial file, including a `TUTORIAL_DATASET_LOCATION`.

    EDITIONS_LOCATION = 'mypath/to/digital_edition/files'
    METADATA_LOCATION = 'mypath/to/metadata/files'

##### B. Unique String IDs

Define variables for IDs for the digital source of the compared editions and any baseline (e.g. 'master') edition In this case, the 'record counts to control records' metric requires a baseline edition. Other metrics will not require either ID if they are not comparing across digital text source archives like this metric does. 

    TUTORIAL_BASELINE_SOURCE_ID = 'mark_twain_project'
    TUTORIAL_SOURCE_ID = 'internet_archive'
    TUTORIAL_METRIC_ID = 'my_unique_metric_id'
    TUTORIAL_COLLECTION_TITLE = 'Internet Archive'
    TUTORIAL_WORK_TITLE = 'Adventures of Huckleberry Finn'

#### 2. _Read editions and/or metadata_

The next step is to read in the digital edition files and/or metadata files you wish to use for your metric(s). AoLM uses custom JSON file formats for both editions and metadata. (The composition of these files are mentioned above in the 'Text and Metadata Ingestion' section.) For this tutorial, two convenience functions `read_huckfinn_dataset_files_by_source` and `read_metadata_files_by_source` have been provided for your use. You only need to specify the editions/metadata location and the string ID that represents the subfolder they are stored in (i.e. 'internet_archive'). Two differently-sized datasets have been provided for your use in the [`tutorial/data`](tutorial/data) folder. The tutorial script defaults to using a dataset with just a few editions for comparison via the ['small_set'](tutorial/data/small_set) folder, but a ['full_set'](tutorial/data/full_set) folder also exists. (NOTE: `metadata_files` is defined below as an example, but is not used for this tutorial.)

    edition_readers = read_huckfinn_dataset_files_by_source(
        EDITIONS_LOCATION, TUTORIAL_SOURCE_ID)
    edition_readers.update(read_huckfinn_dataset_files_by_source(
        EDITIONS_LOCATION, TUTORIAL_BASELINE_SOURCE_ID))

    metadata_files = read_metadata_files_by_source(METADATA_LOCATION, TUTORIAL_SOURCE_ID)

#### 3. _Run a data quality metric_ over the editions and/or metadata

This next step is where you will run a data quality metric on your editions or metadata. The [available AoLM metrics](aolm_code/data_quality/core/dq_metrics) include: 'record consensus', 'record counts to control records', 'lexical validity', 'metadata suffiency', 'authorial signature', and 'legomena'. Each class name you will need for these metrics can be found at the top of the tutorial script file in the section that lists all of the imports. This tutorial uses the 'record counts to control records' metric. (Its class name is `DatasetCompleteness_RecordCountsToControlRecords`.)

First, create the metric object and give it the parameters its constructor requires. (To see where these metric class constructors are defined look at the Python files in [`aolm_code/data_quality/core/dq_metrics`](aolm_code/data_quality/core/dq_metrics). In the `class` section you will see a constructor definition that begins with `def __init__(...):`. This is where you will find the class object's required parameters. However, there is also a helper `create_metric` function in `cli_lib.py` you may utilize.)

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

Each metric object performs two steps to produce its metric and sub-metric values. The metric object's `compute` function tallies the values of the editions or metadata it uses for producing the final metric values. Then the metric object's `evaluate` function calculates statistics based on those tallies to produce the metric and sub-metric values.

    metric.compute()

    metric.evaluate()

#### 4. _Output results_ (for inspection, analysis, and visualization)

In this final step, you will output both the tallies and the metric and sub-metric values of the data quality metric you just ran. Since the implementation of outputting these values has yet to be standardized across AoLM metrics, two convenience functions, `output_metric_tallies` and `output_metric_values` have been provided for your use. The former outputs a CSV file and the latter, a JSON file for the 'record counts to control records' metric. There has been an [`output`](tutorial/output) folder provided in the [`tutorial`](tutorial) folder for your convenience. (NOTE: Most other metrics produce JSON file for their tallies.) A `script_run_time` variable has also been provided in the `tutorial_workspace` function of `aolm_tutorial.py` if useful for timestamping your outputs.
    
    output_metric_tallies(metric, 'my/output/path/metric_tallies_' + script_run_time + '.csv')

    output_metric_values(metric, 'my/output/path/metric_values_'  + script_run_time + '.json')

#### 5. _Interpreting the results_ in the output files

**Metric Tallies File**

The first stage of a metric (called `compute`) tallies the components of a corpus of digital texts it intends to evaluate for data quality. In this case with the 'record counts to control records' metric, the tallies output CSV file will contain percent match of the words and sentences of each chapter of each edition.

The CSV's column headers include: `edition_name`, `chapter_name`, `count_type`, and `percent`.

**Metric Values File**

The second stage of a metric (called `evaluate`) takes the tallies from the first stage and performs some light statistical calculations over them in order to determine the data quality of the corpus. This includes multiple levels of sub-metrics that are all used to calculate the final metric's overall data quality value. All of this information is output in hierarchical JSON form with descriptive key names. Output values include the overall metric value, the percent match for the corpus for chapter count, word count, and sentence count, the total percent coverage calculation concerning chapters/words/sentences for each edition, and the sub-sub-metric values of the percent matches of those items for each edition.

## Workflow Scripts and Overall Data Quality Assessment

The concept of a data quality assessment framework (DQAF) includes the notion that all of the metrics one performs over a dataset should then somehow be used in concert to help determine an overall data quality measurement for that dataset.

An assessment sums up all of the data quality work you have been performing with a timestamp attached that states in essence, "This was the determined quality of the dataset using these measures at this day/time." Data quality assessment is meant to be iterative work that is performed at intervals, depending on how often a dataset is updated.

One simple form of assessment calculation could simply be a weighted average of overall data metric values – with weights assigned according to your own judgment of the importance of a particular metric in determining a dataset's quality rating. (Though such assessment calculations can be as complicated as one deems.)

AoLM's data quality measuring workflow scripts in the [`experiments/chapter1`](experiments/chapter1) folder apply one or more data quality metrics to a selected corpus of digital texts. For instance, [`huckfinn_dataquality.py`](experiments/chapter1/huckfinn_dataquality.py) and [`huckfinn_dataquality_experiment2.py`](experiments/chapter1/huckfinn_dataquality_experiment2.py) in that folder provide illustrative examples of data metrics being applied individually (`huckfinn_dataquality_experiment2.py`) or in combination (`huckfinn_dataquality.py`) over a dataset. Measurement tallies and evaluative data quality ratings are output via the metrics' `output` and `eval_output` class methods. `huckfinn_dataquality.py` provides a good example of this in its `output_results` function. With those metric outputs (typically CSV or JSON file form) a full data quality assessment calculation can then be made programmatically via script or manually calculated by a user.

Those two workflow script files – along with several others in the [`experiments/chapter1`](experiments/chapter1) folder – also contain examples of visualizing the metric outputs, particularly the bar and heatmap plots featured in the dissertation draft (see the `plot_results`, `plot_results2`, and `plot_heatmap` functions in either script file).

## Command Line Tool

The Art of Literary Modeling (AoLM) provides a command-line tool for running data quality metrics on digital texts and their associated metadata. The tool currently only supports evaluating the data quality of the multiple digital editions of _Adventures of Huckleberry Finn_ found in the project's datasets (e.g. from the Internet Archive, Project Gutenberg, and Mark Twain Project Online) by running any of the project's 6 data quality metrics over them. The tool produces tallies of aspects of the edition (i.e. words, sentences, chapters) and produces data quality scores from the respective metric(s). Metrics can be executed individually or in combination, and results are exported as CSV and JSON files for downstream analysis and visualization.

NOTE: The command line tool is a work-in-progress and as of early 2026 is undergoing debugging and testing.

### Usage

The command-line tool, [`tutorial/aolm_cli.py`](tutorial/aolm_cli.py), can be run via the Python interpreter in your terminal.

`python aolm_cli.py [FLAGS]` OR `python3 aolm_cli.py [FLAGS]`

#### Primary Flags

| Flag | Description |
|--------|-------------|
| `--input-folder` | Path to the folder containing edition dataset files used by most text-based metrics. |
| `--metadata-folder` | Path to the folder containing metadata files used by the Metadata Sufficiency metric. |
| `--source-id` | Identifier for the primary edition source being evaluated (e.g., `internet_archive`, `project_gutenberg`). Defaults to the "small_set" dataset but can be adjusted in `aolm_cli.py` |
| `--baseline-source-id` | Identifier for a baseline edition source used in metrics that compare against a baseline, (e.g. 'master' edition) [default value: `mark_twain_project`]. |
| `--work-title` | Full title of the literary work being analyzed. |
| `--collection-title` | Name of the collection of editions being evaluated. |
| `--metrics` | String of metric codes to execute. Multiple metrics can be combined (e.g., `mv`, `acr`). |
| `--output-folder` | Destination folder for generated metric output files. |

Some primary flags also utilize their own set of arguments to help the tool understand exactly what is being requested to run. For example, the arguments for `--metrics` would be placed to the right of it and include the following:

#### Metric Arguments

| Code | Metric |
|--------|-------------|
| `m` | Metadata Sufficiency |
| `v` | Lexical Validity |
| `c` | Record Consensus |
| `a` | Authorial Signature |
| `l` | Legomena |
| `r` | Record Counts to Control Records |

#### Source ID Arguments

| Source ID | Description |
|------------|------------------------------|
| `internet_archive` | Editions sourced from the Internet Archive JSON datasets |
| `project_gutenberg` | Editions sourced from Project Gutenberg JSON datasets |
| `mark_twain_project` | Scholarly XML edition from the Mark Twain Project (used as the baseline/master edition) |

#### Example Usage with Flags and Arguments

The following command runs the metadata sufficiency and lexical validity metrics over the editions of _Huckleberry Finn_ from the Internet Archive. (Recall that it would be `python3` if that's your interpreter.)

`python aolm_cli.py --metrics mv --source-id internet_archive`