# The Art of Literary Modeling

## Overview

Welcome to the repository for 'The Art of Literary Modeling' (AoLM), a PhD project and dissertation by [Jonathan Armoza](https://jonathanarmoza.com/) that develops a framework for measuring and assessing the data quality of corpora of digital literature in digital humanities research.

This repository accompanies the dissertation *The Art of Literary Modeling* and contains the code used for the experiments and tutorial demonstrations described in the text.

### Functionality and Code

AoLM's code can be divided into three functional parts: (1) reading in and processing digital texts and metadata into comparable components, (2) making data quality measurements on those inputs, and (3) assessing those measurement outputs together to determine the overall quality of the dataset.

The core of AoLM is its data quality metrics, of which there are [six working examples](aolm_code/data_quality/core/dq_metrics). The repository's assessment code consists of a set of [workflow scripts dubbed 'experiments'](experiments/chapter1) that run these data quality metrics over sample corpora of digital texts and metadata and then output all of the metrics' measurements to file and/or plot select metric measurements for visual comparison.

Accompanying and aiding that reading/measurement/assessment code is a small library of utility scripts for text processing and data visualization. Text processing code used by the final version of the project can be found in the [aolm_code/objects](aolm_code/objects) and [aolm_code/utilities](aolm_code/utilities) folders, and visualization code can be found within the 'experiment' and separate plotting scripts in the [experiments/chapter1](experiments/chapter1) folder.

Below, you will find documentation on all three functional parts of AoLM including a tutorial demonstrating how to work with data quality metrics. Additional, file-by-file documentation for code used in the final version of AoLM – as well as prototypical code that went unused for it – can be found in the 'Appendix' section of the written portion of 'The Art of Literary Modeling'. (Watch this space for a link to that writing once it is made public.)

NOTE: Any script in the AoLM repository requires the installation and activation of the 'aolm' conda environment. See the setup section of the [data quality metric tutorial](#data-quality-metric-tutorial) for installing this environment on your system from the command line.

### Accompanying Datasets

Several public domain datasets of literature are also in the repository, including [14 digital editions of Mark Twain's _Adventures of Huckleberry Finn_](data/twain/huckleberry_finn) from [Project Gutenberg](https://www.gutenberg.org/), the [Internet Archive](https://archive.org/), and [Mark Twain Project Online](https://legacy.mtpo2.org/landing_writings.shtml), [all 3 volumes of Twain's autobiography](data/twain/autobiography) from Mark Twain Project Online, [9 digital editions of novels by Herman Melville](data/melville/collected)  from Project Gutenberg, and [digital editions of all of Emily Dickinson's poems and their variants (over 4800 files)](data/dickinson/eda) from [Emily Dickinson Archive](https://www.edickinson.org/). Each digital edition (novel/autobiography/poem) has been downloaded directly from their source archive online and processed to a minimal degree to aid their use by AoLM's data quality metrics while maintaining as much of their rawness as possible. Each digital edition is also supplemented by a set of metadata about it provided by those source archives.

## Table of Contents

1. [Quickstart](#quick-start)
2. [Text and Metadata Ingestion](#text-and-metadata-ingestion)
3. [Data Quality Metrics](#data-quality-metrics)
4. [Data Quality Metric Tutorial](#data-quality-metric-tutorial)
5. [Workflow Scripts and Overall Data Quality Assessment](#workflow-scripts-and-overall-data-quality-assessment)
6. [Command Line Tool](#command-line-tool)
7. [Reproducibility](#reproducibility)
8. [Glossary](#glossary)

## Quick Start

1. Clone the repository and create the environment:

```bash
git clone https://github.com/jarmoza/aolm_full
cd aolm_full
conda env create -f environment.yml
conda activate aolm
```

2. Install spaCy models:

```bash
python -m spacy download en_core_web_lg
python -m spacy download en_core_web_sm
```

3. Run the (solved) tutorial:

```bash
python tutorial/tutorial_solution.py
```

## Text and Metadata Ingestion

In order to measure the data quality of digital text files and metadata about them, AoLM processes those files into generalized components in order to compare them. AoLM's [archive-specific reader objects](aolm_code/objects) make this possible. Below is a description of the JSON file formats for text and metadata as well as a description of those reader objects – which may be extended and modified using class inheritance for your own projects.

### Digital Text Processing

With AoLM's ethos of only using minimal intervention during the processing of digital texts in order to read them into memory for data quality measurement, the suggestion is to locate beginning and ends of the primary components of your raw digital source text. If there are subcomponents of the body text that you wish to isolate, inserting a consistent demarcation marker (i.e. `"CHAPTER <roman numeral>."`) is recommended. The [reader objects](aolm_code/objects) and text JSON format have implementations that accommodate both begin and end lines as well as text component demarcation markers. You can observe an example of chapter markers in this ['raw' text edition of _Adventures of Huckleberry Finn_](data/twain/huckleberry_finn/internet_archive/txt/demarcated/complete/txt/adventuresofhuc00twai_demarcated.txt).


### Text JSON File Format Description

AoLM's text JSON file format has two sections: `keys` and `component`. The `keys` section contains values to help a text processing script navigate the raw input `txt` file of the work and values to describe the output from text processing that will appear in the `components` section. AoLM uses the [`IAHuckFinnWriter` class object](aolm_code/data_quality/twain/internet_archive/ia_huckfinn_writer.py) to do this work - where the JSON file's `keys` section is filled out by the user and then the paths to the raw txt and that JSON file are given to `IAHuckFinnWriter` to produce the `components` section of the JSON file. (The resulting completed JSON file can then be read into memory by a reader object. See below.) See this example of a completed JSON version of [the February 2021 edition of _Adventures of Huckleberry Finn_ on Project Gutenberg](data/twain/huckleberry_finn/project_gutenberg/json/2021-02-21-HuckFinn.json).

The `keys` section contains `order`, `input`, and `output` subsections. `order` defines the order of the primary components of the text (i.e. `[header, frontmatter, body, footer]`). A `startline` and `endline` are defined for each of those text components in the `input` subsection. The `output` subsection specifies the key that will be used in the file's `component` section. As you will see in the example file, `body` is a special case in that it contains subcomponents (i.e. chapters for a novel). NOTE: The prefix to be used to find those subcomponents in the raw text is specified in `body` in the input subsection under the key `subcomponent_input_prefix`. A prefix for those subcomponents (chapters) as they will appear in the `component` section is specified in `body` in the `output` subsection.

### Metadata JSON File Format Description

The metadata JSON files used by the metadata sufficiency metric, AoLM's only metadata metric, is more straightforward. See this example of [metadata from the Internet Archive](data/twain/huckleberry_finn/internet_archive/metadata/adventureshuckle00twaiiala-HuckFinn_metadata.json). Here key-value pairs from the source archive's metadata are simply listed in the file. (Note that the key strings themselves have been normalized for the sake of the metric's comparsion.) However, in cases where metadata must be manually extracted (i.e. from within the provided raw text like Project Gutenberg editions), AoLM's metadata file format (and metadata metric) also allows for an `unkeyed_fields` key where such key-value pairs can be placed separately from metadata that was specifically provided separately by the source archive. See [this metadata file from the February 2021 Project Gutenberg edition of _Adventures of Huckleberry Finn_](data/twain/huckleberry_finn/project_gutenberg/metadata/2021-02-21-HuckFinn_metadata.json) for an example of that scenario.

### Reading in Text JSON Files Using Reader Objects

AoLM uses reader objects to load texts from their JSON file format into memory as a set of generalized components that its metric objects can use to make tallies and evaluative measurements from.

AoLM's scheme for doing this uses object-oriented programming class inheritance beginning with a [`AOLMText` object](aolm_code/objects/aolm_text.py) which is used in [the base reader class, `AOLMTextReader`](aolm_code/objects/aolm_textreader.py). Child classes that derive from `AOLMTextReader` are created for texts coming from specific source archives so that the reading/ingestion functionality can be tailored to inputs coming from those sources. See for example, [the Internet Archive reader for _Huckleberry Finn_ editions](aolm_code/objects/ia_huckfinn_reader.py) as opposed to [the Mark Twain Project Online reader for _Huckleberry Finn_ editions](aolm_code/objects/mtpo_huckfinn_reader.py).

## Data Quality Metrics

Each data quality metric is part of what is called a "data quality assessment framework" (DQAF) in Information Science. AoLM uses as its foundation many of the concepts concerning data quality from the field and specifically from information scientist Laura Sebastian-Coleman in her book, _Measuring Data Quality for Ongoing Improvement_ (2012).

The metrics implemented for the project reflect several core categories for data quality provided by Sebastian-Coleman, and are listed in the table below. In order to begin creating your own metrics, have a look at [`dq_metric.py`](aolm_code/data_quality/core/dq_metric.py). This script defines the base class to derive from for your own metrics, and contains the core functionality needed for a metric object. Those core functions include the constructor, `compute`, `evaluate`, and output methods. Your derived child class can and likely will include more helper functionality. Take a look at the code for my own metrics in the [`aolm_code/data_quality/core/dq_metrics`](aolm_code/data_quality/core/dq_metrics) folder to see examples of derived/expanded metric functionality.

### Data Quality Categories and Dimensions

| category | dimensions |
|----------|------------|
| [intrinsic](#intrinsic-data-quality) | - [accuracy](#accuracy-dimension) <br> - [objectivity](#objectivity-dimension) <br> - [believability](#believability-dimension) <br> - [reputation](#reputation-dimension) |
| [contextual](#contextual-data-quality) | - [value-added](#value-added-dimension) <br> - [relevancy](#relevancy-dimension) <br> - [timeliness](#timeliness-dimension) <br> - [completeness](#completeness-dimension) <br> - [appropriate amount of data](#appropriate-amount-of-data-dimension) |
| [representational](#representational-data-quality) | - [interpretability](#interpretability-dimension) <br> - [ease of understanding](#ease-of-understanding-dimension) <br> - [representational consistency](#representational-consistency-dimension) <br> - [representational conciseness](#representational-conciseness-dimension) |
| [accessibility](#accessibility-data-quality) | - [accessibility](#accessibility-dimension) <br> - [access security](#access-security-dimension) |

### Data Quality Metrics

| name | category | primary dimensions | secondary / inferred dimensions | function |
|------|----------|--------------------|----------------------------------|----------|
| [lexical validity](aolm_code/data_quality/core/dq_metrics/dataset_validity/lexical_validity.py) | [intrinsic](#intrinsic-data-quality) | - [accuracy](#accuracy-dimension) | - [believability](#believability-dimension) | comparing data against external objects |
| [record consensus](aolm_code/data_quality/core/dq_metrics/dataset_consistency/consistency_recordconsensus.py) | [representational](#representational-data-quality) | - [representational consistency](#representational-consistency-dimension) | - [interpretability](#interpretability-dimension) | the intelligibility of data |
| [metadata sufficiency](aolm_code/data_quality/core/dq_metrics/dataset_completeness/metadata_sufficiency.py) | [contextual](#contextual-data-quality) | - [completeness](#completeness-dimension) <br> - [value-added](#value-added-dimension) | - [relevancy](#relevancy-dimension) | measurements based on the task or use case(s) for data |
| [record counts to control records](aolm_code/data_quality/core/dq_metrics/dataset_completeness/recordcounts_to_controlrecords.py) | [contextual](#contextual-data-quality) | - [completeness](#completeness-dimension) | - [accuracy](#accuracy-dimension) | |
| [authorial signature](aolm_code/data_quality/core/dq_metrics/dataset_signature/authorial_signature.py) | [representational](#representational-data-quality) | - [representational consistency](#representational-consistency-dimension) | - [interpretability](#interpretability-dimension) | |
| [legomena](aolm_code/data_quality/core/dq_metrics/dataset_signature/legomena.py) | [representational](#representational-data-quality) | - [interpretability](#interpretability-dimension) | - [representational consistency](#representational-consistency-dimension) | |

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

NOTE: All files and folders necessary for this tutorial exist in the project's `tutorial` folder. You will need to use your operating system's terminal/command prompt program as well as your favorite text editor program. Keep in mind that this will need to be an editor capable of editing plain text like 'Notepad', 'TextEdit', or a software development environment like 'Visual Studio Code' rather than a word processor like 'Microsoft Word'. This is because the AoLM's code is in Python, a programming language which requires the use of tab characters to create code block hierarchy (a.k.a. 'scope'). Here are the files and folders you will make use of for the tutorial:

1. [`tutorial/aolm_tutorial.py`](tutorial/aolm_tutorial.py) - The script file you will edit for the tutorial. Contains comments and pseudocode to help your work.
2. [`tutorial/tutorial_solution.py`](tutorial/tutorial_solution.py) - The script file containing the tutorial solution
3. [`tutorial/data`](tutorial/data) - The `small_set` and `full_set` folders in here are where digital editions for the tutorial exist. Note the `editions` and `metadata` subfolders in each. You will point your code in the tutorial script to the `editions` folder within `small_set` or `fullset`.
4. [`tutorial/output`](tutorial/output) - A folder that has been provided for you to point your code in the tutorial script to place your output files

The [`aolm_tutorial.py`](tutorial/aolm_tutorial.py) in the [`tutorial`](tutorial) folder acts as a workspace for you to add code to as you follow along with the tutorial. Follow along with the steps outlined below and place your code in that script file in the `tutorial_workspace` function. Once you have run the script, the output files for this tutorial will be found in the [`tutorial/output`](tutorial/output) folder. If you are satisfied with the results, you may choose to perform your own exercises by running different data quality metrics from the [`aolm_code/data_quality/core/dq_metrics`](aolm_code/data_quality/core/dq_metrics) folder. Note that you will need some beginner-level Python proficiency to follow along with the tutorial. The full tutorial solution along with some extra commentary on it can be found in [`tutorial_solution.py`](tutorial/tutorial_solution.py).

Functionality to enable further exercises and explorations of AoLM's metrics and datasets can be found in [`cli_lib.py`](tutorial/cli_lib.py) as well as via a script to run AoLM's data quality metrics at the command line in [`aolm_cli.py`](tutorial/aolm_cli.py). (NOTE: `aolm_cli.py` functions as a **command-line tool for AoLM** and has still to be fully tested. See the [command line tool](#command-line-tool) section below.)

### Environment Setup

#### 1. _Copy the 'Art of Literary Modeling' GitHub repository to your computer_

In your terminal, run the `git clone` command below in a location on your hard drive where you would like the 'Art of Literary Modeling' code repository to live. (You can use the `cd` command to do this, e.g. `cd /UserDirectory/code` if such a folder exists. `mkdir` can be used to create new folders in your present directory as well, e.g. `mkdir code`.)

`git clone https://github.com/jarmoza/aolm_full`

![Cloning the repository to your computers](tutorial/images/0.%20git%20clone%20repository.png)

#### 2. _Installing Conda_ (OS-specific Instructions)

First, check whether `conda` is already installed. Open your terminal (Command Prompt, PowerShell, or Terminal) and run:

`conda --version`

If you see a version number (for example, `conda 24.11.0`), you can skip this step.

If not, follow the instructions for your operating system below.

---

**Windows**
1. Open Command Prompt or PowerShell
2. `curl -LO https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Windows-x86_64.exe`
3. `start "" /wait Miniforge3-Windows-x86_64.exe /InstallationType=JustMe /AddToPath=1 /S`
3. Close your terminal, then open a new one
4. `conda --version`

---
    
**macOS, Apple silicon**
1. Open Terminal
2. `curl -LO https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-MacOSX-arm64.sh`
3. `bash Miniforge3-MacOSX-arm64.sh -b`
4. `conda init`
5. Close your Terminal, then open a new one
6. `conda --version`

---

**macOS, Intel**
1. Open Terminal
2. `curl -LO https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-MacOSX-x86_64.sh`
3. `bash Miniforge3-MacOSX-x86_64.sh -b`
4. `conda init`
5. Close your Terminal, then open a new one
6. `conda --version`

---

**Linux**
1. Open a terminal
2. `curl -LO https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-x86_64.sh`
3. `bash Miniforge3-Linux-x86_64.sh -b`
4. `conda init`
5. Close your terminal, then open a new one
6. `conda --version`

---

![Installing conda](tutorial/images/1.%20conda%20installation.png)

**Troubleshooting: `conda` not found**

If `conda --version` does not return a version number:

**Windows**

1. Close and reopen your terminal
2. `%USERPROFILE%\miniforge3\Scripts\activate`
3. Try `conda --version` again

**macOS/Linux**

1. `source ~/miniforge3/bin/activate`
2. `conda init`
3. Close and reopen your terminal
4. Try `conda --version` again

#### 3. _Install the 'conda' environment_ for 'Art of Literary Modeling' 

In the *aolm_full* folder in your terminal, create the conda environment by running:

```bash
conda env create -f environment.yml
```

![Create the conda environment](tutorial/images/2.%20create%20conda%20environment.png)

#### 4. _Activate the 'conda' environment_

Next, run the following command. Repeat *only* this last command when you want to re-run
the tutorial script in the terminal. (To exit the 'aolm' conda environment, run `conda deactivate`.)

`conda activate aolm`

![Activate the conda environment](tutorial/images/3.%20Activate%20the%20conda%20environment.png)

#### 5. _Install the required spaCy models_

AoLM's metrics require the use two of spaCy's language models. Run the following commands in your terminal to download them:

```bash
python -m spacy download en_core_web_lg
python -m spacy download en_core_web_sm
```

Run the following command to ensure the models installed successfully:

```bash
python -c "import spacy; spacy.load('en_core_web_lg'); print('spaCy model installed correctly')"
```

![Install and test the spaCy models](tutorial/images/4.%20Install%20and%20test%20spaCy%20models.png)

### Tutorial

**Places to put code corresponding to the numbered and lettered steps below can be found in the `tutorial_workspace` function found in `tutorial/aolm_tutorial.py`.**

#### 1. _Define parameters_ for reading data and running a metric (optional)

The first thing you will do is define string variables for IDs and folder paths that will be used for reading digital texts/metadata and then later, running a data quality metric(s) over those texts/metadata. (This step can be skipped if you don't mind repeatedly entering raw string values into function/constructor calls.) These are used by AoLM's reader objects and data quality metric objects. A set of pre-defined values for these parameters have been placed at the top of the tutorial script for your convenience.

**Helpful Notes:**
- The `pwd` command in your terminal/power shell program will show you the current, full directory path you are located in. (`cd` is the command in the Windows command prompt.)
- Copy and paste the output into a string variable definition
- The path must end in a folder separator character - `/` for macOS and Linux, `\` for Windows

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

The next step is to read in the digital edition files and/or metadata files you wish to use for your metric(s). AoLM uses custom JSON file formats for both editions and metadata. (The composition of these files are mentioned above in the 'Text and Metadata Ingestion' section.) For this tutorial, two convenience functions `read_huckfinn_dataset_files_by_source` and `read_metadata_files_by_source` have been provided for your use. You only need to specify the editions/metadata location and the string ID that represents the subfolder they are stored in (i.e. 'internet_archive'). Two differently-sized datasets have been provided for your use in the [`tutorial/data`](tutorial/data) folder. The tutorial script defaults to using a dataset with just a few editions for comparison via the [`small_set`](tutorial/data/small_set) folder, but a [`full_set`](tutorial/data/full_set) folder also exists. (NOTE: `metadata_files` is defined below as an example, but is not used for this tutorial.)

##### A. Reading Editions into Memory

    edition_readers = read_huckfinn_dataset_files_by_source(
        EDITIONS_LOCATION, TUTORIAL_SOURCE_ID)
    edition_readers.update(read_huckfinn_dataset_files_by_source(
        EDITIONS_LOCATION, TUTORIAL_BASELINE_SOURCE_ID))

##### B. Reading Metadata into Memory (not for this tutorial; shown here for your future experimentation with the metadata metric)

    metadata_files = read_metadata_files_by_source(METADATA_LOCATION, TUTORIAL_SOURCE_ID)

#### 3. _Run a data quality metric_ over the editions and/or metadata

This next step is where you will run a data quality metric on your editions or metadata. The [available AoLM metrics](aolm_code/data_quality/core/dq_metrics) include: 'record consensus', 'record counts to control records', 'lexical validity', 'metadata suffiency', 'authorial signature', and 'legomena'. Each class name you will need for these metrics can be found at the top of the tutorial script file in the section that lists all of the imports. This tutorial uses the 'record counts to control records' metric. (Its class name is `DatasetCompleteness_RecordCountsToControlRecords`.)

##### A. Create the data quality metric object

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

This line creates a data quality metric object.

##### B. Compute the metric's tallies over the editions

Each metric object performs two steps to produce its metric and sub-metric values. The metric object's `compute` function tallies the values of the editions or metadata it uses for producing the final metric values.

    metric.compute()

##### C. Calculate about the metric and sub-metric values

Then the metric object's `evaluate` function calculates statistics based on those tallies to produce the metric and sub-metric values.

    metric.evaluate()

#### 4. _Output results_ (for inspection, analysis, and visualization)

In this final step, you will output both the tallies and the metric and sub-metric values of the data quality metric you just ran. Since the implementation of outputting these values has yet to be standardized across AoLM metrics, two convenience functions, `output_metric_tallies` and `output_metric_values` have been provided for your use. The former outputs a CSV file and the latter, a JSON file for the 'record counts to control records' metric. There has been an [`output`](tutorial/output) folder provided in the [`tutorial`](tutorial) folder for your convenience. (NOTE: Most other metrics produce JSON file for their tallies.) The path for the output files below can once again by using the `pwd` command to find the current directory path and adding the `output` folder name to its end. A `script_run_time` variable has also been provided in the `tutorial_workspace` function of `aolm_tutorial.py` if useful for timestamping your outputs.

##### A. Output the tallies
    
    output_metric_tallies(metric, "/UserDirectory/code/aolm_full/tutorial/output/" + "metric_tallies_" + script_run_time + '.csv')

##### B. Output the metric and sub-metric values

    output_metric_values(metric, "/UserDirectory/code/aolm_full/tutorial/output/" + "metric_values_"  + script_run_time + '.json')

#### 5. Run the finished Python script

Once your edits are made in `aolm_tutorial.py`,

1. Make sure you are located in the tutorial directory in your terminal program (i.e. using `cd /UserDirectory/code/aolm_full/tutorial/`if that is the path where you placed the `aolm_full` project directory)
2. Run the following command:

    python aolm_tutorial.py

**Congratulations! You have just run a data quality metric over a number of editions of _Adventures of Huckleberry Finn_ and output its measurements.**

Look inside the `tutorial/output` folder for the `csv` and `json` files containing the `record counts to control record` metric values.

![Run the tutorial script](tutorial/images/5.%20Run%20the%20tutorial%20script.png)

#### 6. _Interpreting the results_ in the output files

**Metric Tallies File**

The first stage of a metric (called `compute`) tallies the components of a corpus of digital texts it intends to evaluate for data quality. In this case with the 'record counts to control records' metric, the tallies output CSV file will contain percent match of the words and sentences of each chapter of each _Huckleberry Finn_ edition against the Mark Twain Project Online's (MTPO) edition of the novel.

The CSV's column headers include: `edition_name`, `chapter_name`, `count_type`, and `percent`. Each row of values found in the CSV file depict the amount of words or amount of sentences that match when comparing a particular chapter in an edition against the same chapter in the MTPO edition.

**Helpful Note:**
CSV files are best viewed in your preferred spreadsheet program (e.g. 'Microsoft Excel').

**Metric Values File**

The second stage of a metric (called `evaluate`) takes the tallies from the first stage and performs some light statistical calculations over them in order to determine the data quality of the corpus. This includes multiple levels of sub-metrics that are all used to calculate the final metric's overall data quality value. All of this information is output in hierarchical JSON form with descriptive key names.

Output values include:

1. the overall metric `value` (the mean of the corpus' percent match for chapter, word, and sentence counts)
2. `sub-metric` values for the corpus
    - the percent match for the corpus for chapter count
    - the percent match for the corpus for word count
    - the percent match for the corpus for sentence count
    - the total percent coverage concerning the presence of chapters in each edition (currently unusued in the overall metric value calculation)
3. `sub-sub-metric` values for each edition
    - the percent matches of chapters
    - the percent matches of words
    - the percent matches of sentences

**Helpful Note:**
JSON files are best viewed in the plain text editor you used to edit the tutorial code.

## Workflow Scripts and Overall Data Quality Assessment

The concept of a data quality assessment framework (DQAF) includes the notion that after one uses a set of the metrics to measure and evaluate aspects of a dataset, those metric outputs should then be used together to make an overall assessment of that dataset's quality.

Data quality assessment is meant to be iterative work, performed at intervals, depending on how often a dataset is updated. It sums up all of the data quality work performed, and ideally assigns a timestamp to that assessment.  In essence, freezing the assessment in time states, "This was the determined quality of the dataset using these measures at this day/time." 

One simple form of assessment calculation could be a weighted average of each data quality metric's topline value – with weights assigned according to one's own judgment of the importance of a particular metric in determining a dataset's overall quality rating. (However, assessment calculations can be as complicated as one deems fit.)

AoLM's data quality measuring workflow scripts in the [`experiments/chapter1`](experiments/chapter1) folder apply one or more data quality metrics to a selected corpus of digital texts. For instance, [`huckfinn_dataquality.py`](experiments/chapter1/huckfinn_dataquality.py) and [`huckfinn_dataquality_experiment2.py`](experiments/chapter1/huckfinn_dataquality_experiment2.py) in that folder provide illustrative examples of data quality metrics being applied individually (`huckfinn_dataquality_experiment2.py`) or in combination (`huckfinn_dataquality.py`) over a dataset. Measurement tallies and evaluative data quality ratings are output via the metrics' `output` and `eval_output` class methods. `huckfinn_dataquality.py` provides a good example of this in its `output_results` function. With those metric outputs (typically CSV or JSON file form – see the exact metric's output functions) a full data quality assessment calculation can then be made programmatically via script or manually calculated by the person performing the measurements and assessment.

Those two workflow script files – along with several others in the [`experiments/chapter1`](experiments/chapter1) folder – also contain examples of visualizing the metric outputs, notably the bar and heatmap plots featured in the dissertation draft (see the `plot_results`, `plot_results2`, and `plot_heatmap` functions in either script file).

## Command Line Tool

The Art of Literary Modeling (AoLM) provides a command-line tool for running data quality metrics on digital texts and their associated metadata. The tool currently only supports evaluating the data quality of the multiple digital editions of _Adventures of Huckleberry Finn_ found in the project's datasets (e.g. from the Internet Archive, Project Gutenberg, and Mark Twain Project Online) by running any of the project's 6 data quality metrics over them. The tool produces tallies of aspects of the edition (i.e. words, sentences, chapters) and produces data quality scores from the respective metric(s). Metrics can be executed individually or in combination, and results are exported as CSV and JSON files for downstream analysis and visualization.

NOTE: The command line tool is a work-in-progress and as of early 2026 is undergoing debugging and testing.

### Usage

The command-line tool, [`tutorial/aolm_cli.py`](tutorial/aolm_cli.py), can be run via the Python interpreter in your terminal.

```bash
python aolm_cli.py [FLAGS]` OR `python3 aolm_cli.py [FLAGS]
```

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

```bash
python aolm_cli.py --metrics mv --source-id internet_archive
```

## Reproducibility

This repository provides multiple environment specifications for reproducing AoLM's dissertation work and for further use of its code:

- `environment.yml` — recommended for most users; easier to install and sufficient for running the tutorial  
- `environment.lock.yml` — a more tightly specified environment derived from the original development setup  
- `conda_spec.txt` — an explicit, fully pinned environment for maximum reproducibility  

Choose the method below based on your needs.

---

### Method 1: Standard environment (`environment.yml`)

For most users, the environment can be created using the provided `environment.yml` file:

```bash
conda env create -f environment.yml
conda activate aolm
```

If dependency resolution fails on some systems, the libmamba solver may help:

```bash
conda env create -f environment.yml --solver=libmamba
```

---

### Method 2: Reproduction using `environment.lock.yml`

For a closer approximation of the original development environment:

```bash
conda env create -f environment.lock.yml
conda activate aolm
```

---

### Method 3: Exact environment reproduction (`conda_spec.txt`)

The file `conda_spec.txt` contains an explicit list of packages and build hashes exported from the original working environment. This allows the environment used during the project work for *Art of Literary Modeling* to be reproduced as closely as possible.

```bash
conda create --name aolm --file conda_spec.txt
conda activate aolm
```

---

### Exact spaCy model versions

The dissertation analyses were run using the following spaCy model versions:

```text
en_core_web_lg==3.8.0
en_core_web_sm==3.8.0
```

When using the standard environment (`environment.yml`), spaCy will install the latest compatible model version. For exact reproduction of the research environment, install the versions listed above.

---

### Installing spaCy models

The spaCy language models used in the project are installed separately:

```bash
python -m pip install en_core_web_lg==3.8.0
python -m pip install en_core_web_sm==3.8.0
```

These models were used for all NLP processing in the tutorial and dissertation analyses.

## Glossary

### Core Information Science Terms (Wang, Strong, Sebastian-Coleman)

#### Data Quality
> The degree to which data meets the expectations of data consumers for a specific intended use.

#### Data Quality Assessment Framework (DQAF)
> A structured, iterative system for evaluating, measuring, and improving data quality through profiling, measurement, and assessment cycles.

#### Data Quality Dimension
> A specific aspect of data quality (e.g., accuracy, completeness) used to define and organize measurements.

#### Data Quality Category
> A higher-level grouping of dimensions:
> - Intrinsic
> - Contextual
> - Representational
> - Accessibility

---

### Intrinsic Data Quality (Category)

#### Intrinsic Data Quality
> The extent to which data correctly represents real-world values or trusted reference sources.

#### Accuracy (dimension)
> Correctness of data values relative to a real-world object or reference standard.

#### Objectivity (dimension)
> Degree to which data is generated without bias or subjective distortion.

#### Believability (dimension)
> Degree to which data is regarded as credible by users.

#### Reputation (dimension)
> Trustworthiness of the data source or provenance.

---

### Contextual Data Quality (Category)

#### Contextual Data Quality
> The extent to which data is appropriate for a specific task or use case.

#### Relevancy (dimension)
> Applicability of data to the task at hand.

#### Timeliness (dimension)
> Currency and availability of data relative to its use.

#### Completeness (dimension)
> Degree to which required data is present.

#### Appropriate Amount of Data (dimension)
> Sufficiency (not excess or deficiency) of data for a task.

#### Value-Added (dimension)
> Contribution of data to achieving a specific goal or outcome.

---

### Representational Data Quality (Category)

#### Representational Data Quality
> The extent to which data is presented clearly and is interpretable.

#### Interpretability (dimension)
> Clarity of meaning, units, and definitions.

#### Ease of Understanding (dimension)
> Degree to which data can be readily comprehended.

#### Representational Consistency (dimension)
> Uniformity of format and structure across data.

#### Representational Conciseness (dimension)
> Compactness of representation without loss of meaning.

---

### Accessibility Data Quality (Category)

#### Accessibility Data Quality
> The extent to which data can be obtained and used.

#### Accessibility (dimension)
> Ease and speed with which data can be retrieved.

#### Access Security (dimension)
> Controls governing who can access data and under what conditions.

---

### Core Processes

#### Profiling
> Examination of a dataset’s structure, content, and distributions to understand its condition.

#### Column Profiling
> Analysis of individual fields (type, format, range, validity).

#### Structural Profiling
> Analysis of relationships across data (dependencies, hierarchies, cardinality).

#### Assessment
> Interpretive comparison of measured data against expectations to determine quality.

#### Measurement (Information Science)
> A specific procedure used to evaluate a data quality dimension.

