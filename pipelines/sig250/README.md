# Signature250 Avgd Ingestion Pipeline

Data pipeline that reads in binary files (.ad2cp) output from a Nortek Signature250 mounted on a bottom 
lander at PacWave. It is currently set up to read the waves measurement dataset (as measured by the 
vertical beam/altimeter) and ignores the water velocity dataset (the bin-averaged version is read in 
the `sig250_avgd` pipeline).

## Prerequisites

* Ensure that your development environment has been set up according to
[the instructions](../../README.md#development-environment-setup).

> **Windows Users** - Make sure to run your `conda` commands from an Anaconda prompt OR from a WSL shell with miniconda
> installed. If using WSL, see [this tutorial on WSL](https://tsdat.readthedocs.io/en/latest/tutorials/wsl.html) for
> how to set up a WSL environment and attach VS Code to it.

* Make sure to activate the pacwave anaconda environment before running any 
commands:  `conda activate pacwave`


## Editing pipeline data fields
This pipeline is set up to handle data created by a Nortek Signature250. It also has some basic parameters 
set up for sampling in Sequim Bay.

1. If you are not running the echo sounder, navigate to `pipelines/sig250/config` and open `retriever.yaml`. 
Remove all entries that have the `_echo` tag. You can do this as well for `dataset.yaml`, but this isn't critical.

2. There are a number of parameters listed in `retriever.yaml` in lines 15-18 that should be updated.

    a. "depth_offset" is the distance below the waterline that the ADCP transducers sit

    b. "salinity" is the water salinity, which ranges around 31 for the channel into Sequim Bay

    c. "magnetic_declination" is the current magnetic declination. You can look this up online.

3. In `dataset.yaml`, update the information under the `attrs` block per the data collection specifics.

4. There is one parameter listed in `shared/quality.yaml` that can be updated:

    a. "correlation_threshold", on line 71, is for a QC test that removes velocity data below a certain % acoustic signal 
    correlation.

5. You may need to update the "trigger" listed in `config/pipeline.yaml` for your ADCP's binary file extension.


## Running your pipeline
This section shows you how to run the ingest pipeline created by the template.  Note that `{ingest-name}` refers
to the pipeline name you typed into the template prompt, and `{location}` refers to the location you typed into
the template prompt.

1. Make sure to be in the `ingest-pacwave` folder

```bash
cd $PATH_TO_PIPELINE/ingest-pacwave
conda env create
conda activate pacwave
```

2. Run the runner.py with your test data input file as shown below:

```bash
python runner.py ingest $PATH_TO_DATA/{filename}.{ext}
```

3. Finally, data and plots are saved in `ingest-pacwave/storage/root/`
