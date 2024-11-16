"# ma-thesis-project" 

## Installation 

This project uses Poetry for dependency management. To set up the project, follow these steps:

1. Install Poetry: If you do not have Poetry installed, you can install it by following the instructions on the Poetry installation page.

2. Clone the repository: Clone the project repository to your local machine using. 

3. Install dependencies: Run the following command in the root directory of the project to install all the required dependencies as specified in the pyproject.toml:

  'poetry install'

This will set up a virtual environment and install everything needed to run the project.


## Composition of the project file

There are 4 folders in the project. 

1. 'scripts': There are 24 scripts in the folder. All of them are named with sequences. Run the scripts according to the order will be fine. For each script, there are docstrings explaining how it works. 

2. 'data': The 'raw_data' folder contains all the prompts and responses. The 'processed_data' contains the results of the analysis. 

3. 'visualization': The folder contains all the visualization plots for the results. 

4. 'tests': Currently, the project does not include test files. I used 'logging' or 'print' statements extensively to monitor the scipts' behavior during the experiment. 


## NOTE: 
1. The differences between 'merged' and 'separate' are: 
merged: 4 files sorted by language pairs
separate: 40 files sorted by language pairs and the sequence of prompts

2. The script 18 to 20 must be run on the GPU server. 
