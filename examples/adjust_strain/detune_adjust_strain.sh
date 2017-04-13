#! /bin/bash

TF_BASEDIR=/home/daniel.finstad/src/pycbc-cal/data/o1/H1
TF_ATST=${TF_BASEDIR}/tf_A_tst.txt
TF_APU=${TF_BASEDIR}/tf_A_pu.txt
TF_C=${TF_BASEDIR}/tf_C.txt
TF_D=${TF_BASEDIR}/tf_D.txt


GPS_START_TIME=1126252607
GPS_END_TIME=$((${GPS_START_TIME}+2048))

pycbc_adjust_strain --verbose --pad-data 8 --sample-rate 16384 \
    --transfer-function-a-tst ${TF_ATST} \
    --transfer-function-a-pu ${TF_APU} \
    --transfer-function-c ${TF_C} \
    --transfer-function-d ${TF_D} \
    --strain-high-pass 20 \
    --fc0 341 \
    --fs0 10 \
    --q0 5 \
    --channel-name H1:DCS-CALIB_STRAIN_C01 \
    --frame-type H1_HOFT_C01 \
    --gps-start-time ${GPS_START_TIME} \
    --gps-end-time ${GPS_END_TIME} \
    --kappa-tst-re 1.0 \
    --kappa-tst-im 0.0 \
    --kappa-pu-re 1.0 \
    --kappa-pu-im 0.0 \
    --kappa-c 1.0 \
    --delta-fc 0.0 \
    --delta-fs 0.0 \
    --delta-q 10.0 \
    --output-frame H1-ADJUSTED_FRAME_DELTA_Q_10.0-1126258712-2048.gwf \
    --src
