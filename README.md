# The Art of Literary Modeling

Welcome to the repository for 'The Art of Literary Modeling' (AoLM), a PhD project and dissertation by [Jonathan Armoza](https://jonathanarmoza.com/) that conceptualizes a framework for and measures the data quality of collections of digital literature for the digital humanities.

AoLM's code can be divided into three functional parts: reading in digital texts and metadata, making data quality measurements on those inputs, and assessing those measurements. There also exists a small library of utility scripts for text processing and data visualization.

The core of AoLM is its data quality metrics, of which there are six working examples. The repository's assessment code consists of a set of 'experiments' that run these data quality metrics over sample digital texts and metadata and then visualize, analyze, and output the metrics' measurements. Several public domain datasets of literature are also in the repository, including 14 digital editions of Mark Twain's 'Adventures of Huckleberry Finn', all 3 volumes of Twain's autobiography, 9 digital editions of novels by Herman Melville, and digital editions of all of Emily Dickinson's poems and their variants (over 4800 files). Each digital edition (novel/autobiography/poem) has been downloaded directly from their source archive online and processed to a minimal degree to aid their use by the AoLM's data quality metrics. Each digital edition also is complemented by a set of metadata about it provided by those online sources.

Below, is documentation on all three functional parts of AoLM beginning with a tutorial demonstrating how to work with data quality metrics. Additional, file by file documentation for code used in the final version of AoLM – as well as prototypical code that went unused for it – can be found in the 'Appendix' section of the written portion of 'The Art of Literary Modeling'. (Watch this space for a link to that writing once it is made public.)


## Data Quality Metric Tutorial

This tutorial will guide you through a sample exercise in reading a dataset of digital texts, running a data quality metric over them, and producing output files from the metric. The example dataset for the tutorial will be a set of editions of Mark Twain's 'Adventures of Huckleberry' sourced from the 'Internet Archive', 'Project Gutenberg', and 'Mark Twain Project Online' at University of California, Berkeley. 

Comments and pseudocode for this tutorial are found in `aolm_tutorial.py` in the `tutorial` folder which acts as a workspace for you to add code to as you follow along with the tutorial. Follow along with the steps outlined below and place your code in that script file in the `tutorial_workspace` function. Once you have run the script, the output files for this tutorial will be found in the `tutorial/output` folder. If you are satisfied with the results, you may choose to perform your own exercises with running different data quality metrics in the `aolm_code/data_quality/core/dq_metrics` folder. Note that you will need some beginner-level Python proficiency to follow along with the tutorial. The full tutorial solution along with some extra commentary on it can be found in `tutorial_solution.py`.

Functionality to enable further exercises and explorations of AoLM's metrics and datasets can be found in `cli_lib.py` as well as via a script to run AoLM's data quality metrics at the command line in `aolm_cli.py`.

Instructions on how to read digital texts into memory for use by data quality metric objects and how to create assessment code for their outputs can be found [here]().

### Environment Setup

#### 1. Copy the 'Art of Literary Modeling' GitHub repository to your computer

In your terminal, run `git clone https://github.com/jarmoza/aolm_full` in a location on your hard drive where you would like the 'Art of Literary Modeling' code repository to live.

#### 2. Installing Anaconda (OS-specific Instructions)

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

#### 3. Install the 'conda' environment for 'Art of Literary Modeling' 

In the *aolm_full*  folder in your terminal, run `conda env create -f environment.yml`

#### 4. Activate the 'conda' environment

Next, run `conda activate aolm`. Repeat *only* this last command when you want to re-run
the tutorial script in the terminal. (To exit the 'aolm' conda environment, run `conda deactivate`.)

#### 5. Install the required spaCy models

`python3 -m spacy download en_core_web_lg`
`python3 -m spacy download en_core_web_sm`

### Tutorial

#### 1. Parameters for reading data and running a metric (optional)

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

#### 2. Read editions and/or metadata

The next step is to read in the digital edition files and/or metadata files you wish to use for your metric(s). AoLM uses custom JSON file formats for both editions and metadata. (How to build these from raw digital texts/metadata will be explained in a future tutorial, but you may examine the edition and metadata files in the `tutorial/data` folder.) For this tutorial, two convenience functions `read_huckfinn_dataset_files_by_source` and `read_metadata_files_by_source` have been provided for your use. You only need to specify the editions/metadata location and the string ID that represents the subfolder they are stored in (i.e. 'internet_archive').

    edition_readers = read_huckfinn_dataset_files_by_source(
        EDITIONS_LOCATION, TUTORIAL_SOURCE_ID)
    edition_readers.update(read_huckfinn_dataset_files_by_source(
        EDITIONS_LOCATION, TUTORIAL_BASELINE_SOURCE_ID))

    metadata_files = read_metadata_files_by_source(METADATA_LOCATION, TUTORIAL_SOURCE_ID)

#### 3. Run a data quality metric over the editions and/or metadata

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

#### 4. Output results (for inspection, analysis, and visualization)

In this final step, you will output both the tallies and the metric and submetric values of the data quality metric you just ran. Since the implementation of outputting these values has yet to be standardized across AoLM metrics, two convenience functions, `output_metric_tallies` and `output_metric_values` have been provided for your use. The former outputs a CSV file and the latter, a JSON file for the 'record counts' metric. (NOTE: Most other metrics produce JSON file for their 'tallies'.) A `script_run_time` variable has also been provided in the `tutorial_workspace` function if useful for timestamping your outputs.
    
    output_metric_tallies(metric, 'my/output/path/metric_tallies_' + script_run_time + '.csv')

    output_metric_values(metric, 'my/output/path/metric_values_'  + script_run_time + '.json')

#### 5. How to interpret the results in the output files

