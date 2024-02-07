# func_mriqc
This package contains workflows for executing [MRIQC](https://mriqc.readthedocs.io/en/latest/) on individual subjects and groups. The individual subject workflow [`mriqc_subj`](#mriqc_subj) is written for the Duke Compute Cluster (DCC) while the group workflow [`mriqc_group`]() is written for labarserv2.


## Usage
- Install into project environment on both the DCC (see [here](https://github.com/labarlab/conda_dcc)) and/or labarserv2 (see [here](https://github.com/labarlab/conda_labarserv2)) via `$ python setup.py install`.
- Trigger package help and usage via entrypoint `$ func_mriqc`.

```
(emorep)[nmm51-dcc: ~]$func_mriqc 

Version : 1.0.0

This package conducts MRIQC for subject- and group-level MRI
datasets. Trigger helps and usages with the following entrypoints:

    mriqc_subj    : conduct subject-level MRIQC
    mriqc_group   : conduct group-level MRIQC

```

## Requirements
- A singularity image of MRIQC on the DCC
- A docker container of MRIQC on labarserv2


## mriqc_subj
This sub-package executes MRIQC for each subject on the DCC. 


### Setup
- Install into project environment on the DCC (see [here](https://github.com/labarlab/conda_dcc)) via `$ python setup.py install`
- Store a singularity image of MRIQC on the DCC
- Set the global variable `SING_MRIQC` to store the path to the singularity image


### Usage
Trigger sub-package help and usage via `$ mriqc_subj`:

```
(emorep)[nmm51-dcc: ~]$mriqc_subj
usage: mriqc_subj [-h] [--fd-thresh FD_THRESH] [--proj-dir PROJ_DIR]
                  [--proj-research PROJ_RESEARCH] -s SUB_LIST [SUB_LIST ...] -e SESS -k
                  RSA_KEY

Conduct participant MRIQC.

Run subjects through "participant" mode of MRIQC. Work is
conducted in:
    /work/<user>/EmoRep/Exp2_Compute_Emotion/data_scanner_BIDS/derivatives/mriqc

Final files saved to group directory:
    /hpc/group/labarlab/EmoRep/Exp2_Compute_Emotion/data_scanner_BIDS/derivatives/mriqc

A single process of MRIQC is conducted for each subject,
and run scripts and parent/child stdout/err files are
written to:
    /work/<user>/EmoRep/Exp2_Compute_Emotion/data_scanner_BIDS/derivatives/logs/mriqc_<timestamp>.

Requires environmental variable SING_MRIQC to supply paths to
singularity image of MRIQC.

Example
-------
mriqc_subj \
    -k $RSA_LS2 \
    -s sub-ER0009 sub-ER0010 \
    -e ses-day2

Notes
-----
Written to be executed on the Duke Compute Cluster.

optional arguments:
  -h, --help            show this help message and exit
  --fd-thresh FD_THRESH
                        Framewise displacement threshold
                        (default : 0.3)
  --proj-dir PROJ_DIR   Path to BIDS-formatted project directory
                        (default : /hpc/group/labarlab/EmoRep/Exp2_Compute_Emotion/data_scanner_BIDS)
  --proj-research PROJ_RESEARCH
                        Path to parent directory of mriqc.simg location
                        (default : /hpc/group/labarlab/research_bin)

Required Arguments:
  -s SUB_LIST [SUB_LIST ...], --sub-list SUB_LIST [SUB_LIST ...]
                        List of subject IDs to submit for MRIQC
  -e SESS, --sess SESS  BIDS session ID
  -k RSA_KEY, --rsa-key RSA_KEY
                        Location of labarserv2 RSA key

```

The `mriqc_subj` workflow will schedule SBATCH jobs for each subject that will:
- Download data from Keoki
- Execute MRIQC for subject data
- Upload MRIQC to Keoki

Also, see [Diagrams](#diagrams)

### Considerations
- Rawdata on Keoki needs to be in BIDS format
- Only a single session can be executed at once, triggering the workflow for different simultaneous sessions of the same subject will result in process failures


## mriqc_group
TODO


## Diagrams
Diagram of processes, showing workflow as a function of package methods. Additionally, parent and child processes are illustrated, as well as which steps are multi-processed.
![Process](diagrams/process.png)

Diagram of imports.
![Imports](diagrams/imports.png)
