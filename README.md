# Ingest PacWave Pipeline Repository

[![tests](https://github.com/tsdat/pipeline-template/actions/workflows/tests.yml/badge.svg)](https://github.com/tsdat/pipeline-template/actions/workflows/tests.yml)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

This repository contains a collection of one or more `tsdat` pipelines (as found under the ``pipelines`` folder) for processing METOcean measurements collected at the PacWave wave energy test site. The pipelines are grouped by measurement platform as follows:

#### FLOATr buoys
The FLOATr buoys provide meteorological measurements of wind speed and direction, air temperature and pressure, shortwave radiation (light). An onboard CTD (conductivity-temperature-depth) sensor (Seabird SBE 37-SM MicroCAT) provides measurements of water temperature, salinity, and dissolved oxygen. Down-looking ADCPs (RDI Workhorse 600 kHz) installed on the FLOATr buoys provide observations of water velocity. These data are collected using a Campbell datalogger and telemetered to shore in 
real-time. Buoys are named with a 3 digit number that increases for each deployment.

  - `floatr_met` - pipeline that ingests meteorological data stored in **.met** CSV files.
  - `floatr_ctd` - ingest pipeline that reads CTD data stored in **.ocean** CSV files.
  - `floatr_adcp` - ingest pipeline that reads down-looking ADCP data stored in **.adcp** CSV files.
  - `floatr_adcp_raw` - ingest pipeline that reads the raw binary data collected from the down-looking ADCP's SD card.

#### Spotter and Nexsens buoys
The wave buoys (Spotter and Nexsens) provide measurements of standard and directional wave statistics as well as additional metocean variables, depending on the firmware version installed. Data are provided in the original json file format as pulled from the cloud API, and processed data are provided in netCDF4 format. Raw Spotter CSV datafiles are uploaded sporadically as the buoys are recovered and SD cards retrieved. Nexsens buoys have been decommissioned but are kept here for documentation

 - `spotter` - ingest pipeline that reads JSON files pulled from Sofar's cloud API as well as CSV files downloaded from Sofar's dashboard
 - `spotter_raw` - ingest pipeline that reads netcdf files of converted raw Spotter3 data on the buoy's SD card.
 - `vap_spotter` - VAP pipeline for combining multiple individual files from the `spotter` ingest pipeline. Not currently in use.
 - `nexsens` - ingest pipeline that reads JSON files pulled from Nexsens' cloud API. Not currently in use.

#### Nortek Signature250
Bottom deployments of Nortek Signature250 ADCPs are measuring water velocity and surface waves. These instruments are recording
in dual-profile mode: one profile is collecting water surface measurements for wave analysis, the second profile is collecting
water velocity measurements.

 - `sig250` - ingest pipeline that processes the altimeter surface measurements stored in the **.ad2cp** file.
 - `sig250_avgd` - ingest pipeline that processes the in-instrument bin-averaged water velocity data stored in the **avgd.ad2cp** file.

 #### CRAB (in-development)
 The Coastal Real-time Acoustic Buoy (CRAB) is a passive acoustic instrumentation system that collects passive acoustic measurements on the seafloor and telemeters data on-shore in near-real-time. The hydrophones are controlled via a WISPR
 system onboard the bottom lander, which sends data to the surface buoy at a specified interval to send to a shore-side server.

 - `crab` - ingest pipeline processes near-real-time acoustic data stored in WISPR-generated **.dat** files.

## Repository Structure

The repository is made up of the following core pieces:

- **`runner.py`**: Main entry point for running a pipeline.

- **`pipelines/*`**: Collection of custom data pipelines using `tsdat`.

- **`pipelines/example_ingest`**: An out-of-the-box example `tsdat` pipeline.

- **`templates/*`**: Template(s) used to generate new pipelines.

- **`shared/*`**: Shared configuration files that may be used across multiple pipelines.

- **`utils/*`**: Utility scripts.

## Prerequisites

The following are required to develop a `tsdat` pipeline:

1. **A GitHub account.** [Click here to create an account if you don't have one already](https://github.com/)

2. **An Anaconda environment.**  We strongly recommend developing in an Anaconda Python environment to ensure
that there are no library dependency issues.  [Click here for more information on installing Anaconda on your computer](https://docs.anaconda.com/anaconda/install/index.html)

    > **Windows Users** - You can install Anaconda directly to your Windows box OR you can run via a linux
    environment using the Windows Subsystem for Linux (WSL).  See
    [this tutorial on WSL](https://tsdat.readthedocs.io/en/latest/tutorials/setup_wsl.html) for
    how to set up a WSL environment and attach VS Code to it.

## Creating a repository from the pipeline-template

You can create a new repository based upon the `tsdat` pipeline-template repository in GitHub:

1. Click this '[Use this template](https://github.com/tsdat/pipeline-template/generate)' link and
follow the steps to copy the template repository into to your account.
    > **NOTE:** If you are looking to get an older version of the template, you will need to
    select the box next to 'Include all branches' and set the branch your are interested
    in as your new default branch.

2. On github click the 'Code' button to get a link to your code, then run

    ```shell
    git clone <the link you copied>
    ```

    from the terminal on your computer where you would like to work on the code.

## Setting up your Anaconda environment

1. Open a terminal shell from your computer
   - Linux or Mac: open a regular terminal
   - Windows: open an Anaconda prompt if you installed Anaconda directly
   to Windows, OR open a WSL terminal if you installed Anaconda via WSL.

2. Run the following commands to create and activate your conda environment:

    ```shell
    conda env create
    conda activate pacwave
    ```

3. Verify your environment is set up correctly by running the tests for this repository:

    ```shell
    pytest
    ```

    If you get the following warning message when running the test:

    ```shell
    UserWarning: pyproj unable to set database path.
    ```

    Then run the following additional commands to permanently remove this warning message:

    ```shell
    conda remove --force pyproj
    pip install pyproj
    ```

    If everything is set up correctly then all the tests should pass.

## Opening your repository in VS Code

1. Open the cloned repository in VS Code. *(This repository contains default settings for
VS Code that will make it much easier to get started quickly.)*

2. Install the recommended extensions (there should be a pop-up in VS Code with recommendations).

    > **Windows Users**: In order to run python scripts in VSCode, follow steps A-C below:

    A. Install the extension Code Runner (authored by Jun Han).

    B. Press `F1`, type `Preferences: Open User Settings (JSON)` and select it.

    C. Add the following lines to the list of user settings, and update `<path to anaconda>` for
    your machine:

    ```json
    {
        "terminal.integrated.defaultProfile.windows": "Command Prompt",
        "python.condaPath": "C:/<path to anaconda>/Anaconda3/python.exe",
        "python.terminal.activateEnvironment": true,
        "code-runner.executorMap": {
            "python": "C:/<path to anaconda>/Anaconda3/Scripts/activate.bat && $pythonPath $fullFileName"
        },
    }
    ```

3. Tell VS Code to use your new conda environment:
    - Press `F1` to bring up the command pane in VS Code
    - Type `Python: Select Interpreter` and select it.
    - Select the newly-created `pacwave` conda environment from the drop-down list. You may need to refresh the list (cycle icon in the top right) to see it.
    - Bring up the command pane and type `Developer: Reload Window` to reload VS Code
    and ensure the settings changes propagate correctly.

4. Verify your VS Code environment is set up correctly by running the tests for this repository:
    - Press `F1` to bring up the command pane in VS Code
    - Type `Test: Run All Tests` and select it
    - A new window pane will show up on the left of VS Code showing test status
    - Verify that all tests have passed (Green check marks)

5. Set up yaml validation: run `tsdat generate-schema` from the command line

    > NOTE: if you would like to validate your configuration files using one of the supported standards (i.e., ACDD or
    IOOS), then please use the `--standards` flag and pass either `acdd` or `ioos`.

## Processing Data

- The `runner.py` script can be run from the command line to process input data files:

    ```shell
    python runner.py <ingest, vap> <path(s) to file(s) to process>

    ```shell
    > The pipeline(s) used to process the data will depend on the specific patterns declared
    by the `pipeline.yaml` files in each pipeline module in this repository.


- The `runner.py` script can optionally take a glob pattern in addition to a filepath. E.g.,
to process all 'csv' files in some input folder `data/to/process/` you would run:

    ```shell
    python runner.py ingest data/to/process/*.csv
    ```

- The `--help` option can be used to show additional usage information:

    ```shell
    python runner.py --help
    ```

### VAP Pipelines

- Value Added Product (VAP) Pipelines operate on the output of ingest pipelines. 

- The command to run these pipelines has a slightly different structure, where we enter the 
pipeline.yaml configuration file to use, as well as a start and end date:

    ```shell
    python runner.py vap <pipeline/<pipeline-name>/config/pipeline.yaml> --begin yyyymmdd.HHMMSS --end yyyymmdd.HHMMSS
    ```

- The --help option can also be used here if you get stuck:

    ```shell
    python runner.py vap --help
    ```

## Additional resources

- Learn more about `tsdat`:
  - GitHub: <https://github.com/tsdat/tsdat>
  - Documentation: <https://tsdat.readthedocs.io>
  - Data standards: <https://github.com/tsdat/data_standards>
- Learn more about `xarray`:
  - GitHub: <https://github.com/pydata/xarray>
  - Documentation: <https://xarray.pydata.org>
- Learn more about 'pydantic':
  - GitHub: <https://github.com/samuelcolvin/pydantic/>
  - Documentation: <https://pydantic-docs.helpmanual.io>
- Other useful tools:
  - VS Code: <https://code.visualstudio.com/docs>
  - Docker: <https://docs.docker.com/get-started/>
  - `pytest`: <https://github.com/pytest-dev/pytest>
  - `black`: <https://github.com/psf/black>
  - `matplotlib` guide: <https://realpython.com/python-matplotlib-guide/>
