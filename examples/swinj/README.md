# software injection workflow

This example injects a waveform into gravitational-wave frame data then adjusts the strain for the time-varying parameters of the calibration. The adjusted data is then filtered to recover the injection.

To run copy the files to a new directory. Make sure that ``TF_PATH`` in ``run_pycbc_make_cal_workflow.sh`` points to the directory with the transfer function data; default is ``${HOME}/src/pycbc-cal/data/o1/``. Then run
```
sh run_pycbc_make_cal_workflow.sh
```
and it will begin the workflow.
