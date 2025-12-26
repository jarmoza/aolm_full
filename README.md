# The Art of Literary Modeling

Welcome to the repository for 'The Art of Literary Modeling' (AoLM), a project by [Jonathan Armoza](https://jonathanarmoza.com/) that measures the data quality of collections of digital literature.

This repo contains code for processing and reading digital texts and metadata of digital texts as well as text processing utilities for doing so. The core functionality of AoLM are its data quality metrics, of which there are a set of six examples. The repo's code also includes a set of 'experiments' that run these data quality metrics on a set of sample digital texts and metadata and visualize and assess the metrics' output values. Several public domain datasets of literature are also in the repo, including Mark Twain's 'Adventures of Huckleberry Finn', Twain's autobiography, the novels of Herman Melville, and the poems of Emily Dickinson. Each have been downloaded from their digital sources and processed to a minimal degree to aid their use by the AoLM's data quality metrics. 


## Data Quality Metric Tutorial

This tutorial will guide you through a sample exercise in reading a dataset of digital texts, running a data quality metric over them, and producing output files from the metric. The example dataset for the tutorial will be a set of 10 editions of Mark Twain's 'Adventures of Huckleberry' sourced from the 'Internet Archive'. 

Comments and pseudocode for this tutorial are found in `aolm_tutorial.py` in the `tutorial` folder. Follow along the steps outlined below and place your code in that script file in the `tutorial_workspace` function. Once you have run the script and are satisfied with the results, you may choose to perform your own exercises with running different data quality metrics in the `aolm_code/data_quality/core/dq_metrics` folder. Note that you will need some beginner-level Python proficiency to follow along with the tutorial. The full tutorial solution along with some extra commentary on it can be found in `tutorial_solution.py`.

Functionality to enable further exercises and explorations of AoLM's metrics and datasets can be found in `cli_lib.py` as well as via a script to run AoLM's data quality metrics at the command line in `aolm_cli.py`.

### Environment Setup

#### 1. Installing Anaconda (OS-specific Instructions)

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

#### 2. Install the 'conda' environment for 'Art of Literary Modeling' 

In the *aolm_full* folder in your terminal, run `conda env create -f environment.yml`

#### 3. Activate the 'conda' environment

Next, run `conda activate aolm`. Repeat *only* this last command when you want to re-run
the tutorial script in the terminal. (To exit the 'aolm' conda environment, run `conda deactivate`.)

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