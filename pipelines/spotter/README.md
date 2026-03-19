# PacWave Spotter Wave Buoy Ingestion Pipeline

This pipeline is designed to read processed Spotter data from Sofar's online dashboard,
either the manually downloaded CSV files or JSON strings pulled via the [API](https://docs.sofarocean.com/spotter-and-smart-mooring/spotter-data/wave-data). Data in
JSON format should be saved as a text file before inputting to the pipeline.

## Prerequisites

* Ensure that your development environment has been set up according to
[the instructions](../../README.md#development-environment-setup).

> **Windows Users** - Make sure to run your `conda` commands from an Anaconda prompt OR from a WSL shell with miniconda
> installed. If using WSL, see [this tutorial on WSL](https://tsdat.readthedocs.io/en/latest/tutorials/wsl.html) for
> how to set up a WSL environment and attach VS Code to it.

* Make sure to activate the pacwave anaconda environment before running any commands:  `conda activate pacwave`

## Running your pipeline
This section shows you how to run the ingest pipeline created by the template.  Note that `{ingest-name}` refers
to the pipeline name you typed into the template prompt, and `{location}` refers to the location you typed into
the template prompt.

1. Make sure to be at your $REPOSITORY_ROOT. (i.e., where you cloned the pipeline-template repository)

2. Run the runner.py with your test data input file as shown below:

```bash
cd $REPOSITORY_ROOT
conda activate pacwave # <-- you only need to do this the first time you start a terminal shell
python runner.py ingest pipelines/{ingest-name}/test/data/input/{location}_data.csv
```

## Testing your pipeline
This template is set up with a pytest unit test to ensure your pipeline is working correctly.  It is intended that the
pytest unit tests will be run automatically before pipeline deployment to prevent against breaking code changes.  To
run your tests locally, run these commands from your anaconda environment shell:

```bash
cd $REPOSITORY_ROOT
pytest
```
