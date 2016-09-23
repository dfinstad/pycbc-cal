#! /bin/bash

TF_BASEDIR=/home/bdlackey/cbccalibration/calibrationdata/O1/
TF_ATST=${TF_BASEDIR}/tf_A_tst.txt
TF_APU=${TF_BASEDIR}/tf_A_tst.txt
TF_C=${TF_BASEDIR}/tf_A_tst.txt
TF_D=${TF_BASEDIR}/tf_A_tst.txt

pycbc_adjust_strain --pad-data 8 --sample-rate 16384 \
    --transfer-function-atst ${TF_ATST} \
    --transfer-function-apu ${TF_APU} \
    --transfer-function-c ${TF_C} \
    --transfer-function-d ${TF_D} \
    --strain-high-pass 20 \
    --fc0 341 \
    --channel-name H1:DCS-CALIB_STRAIN_C02 \
    --frame-type H1_HOFT_C02 \
    --gps-start-time 1126258704 \
    --gps-end-time 1126260768 \
    --kappa-tst 0.75 \
    --kappa-tstim 0.0 \
    --kappa-pu 1.0 \
    --kappa-puim 0.0 \
    --kappa-c 1.0 \
    --delta-fc 0.0 \
    --ifo H1 \
    --output-frame H1-ADJUSTED_FRAME_KAPPA_TST_0.75-1126258712-2048.gwf
