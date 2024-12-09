Input data and code for "Unlocking the green power of the North Sea: Identifying key energy infrastructure synergies for 2030 and 2040"
--------------------------------
This package contains all input data and code required to run the optimizations
presented in the paper. Below a short overview of the repository.

- case_study_data contains data and scripts for pre- and postprocessing of input data
- src contains a version of AdOpT-NET0, before the package had a versioning system
- MES_NS2030.py is the main script to run the optimizations for the 2030 scenarios
- MES_NS2040.py is the main script to run the optimizations for the 2040 scenarios

Both main scripts (MES_NS2030.py and MES_NS2040.py rely heavily on help functions that
can be found in input_data/optimization/utilities

The study was performed with python 3.12 and all dependencies used were pinned in the
requirements.txt file included here. The optimizations can be rerun by pip-installing
the requirements under python 3.12.
