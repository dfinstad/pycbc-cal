#! /bin/bash

# random times
#for INJECTION_TIME in 1126253357 1126254257 1126255157 1126256417 1126257557 1126260497 1126266197 1126261397 1126264997 1126297757 1126294817 1126296497; do
for INJECTION_TIME in 1126253357; do

# times to analyze
START_TIME=$((${INJECTION_TIME} - 750))
END_TIME=$((${START_TIME} + 2048))

FRAME_TYPE=H1:H1_HOFT_C02
CHANNEL_NAME=H1:DCS-CALIB_STRAIN_C02

# The location of your configuration (.ini) file
CONFIG_PATH=${PWD}/config.ini

# Paths to the transfer functions
BASE_PATH=${PWD}
TF_PATH=${BASE_PATH}/../../data/o1
PATH_ATST=${TF_PATH}/tf_A_tst.txt
PATH_APU=${TF_PATH}/tf_A_pu.txt
PATH_C=${TF_PATH}/tf_C.txt
PATH_D=${TF_PATH}/tf_D.txt

WORKFLOW_NAME=cal_${INJECTION_TIME}

mkdir ${WORKFLOW_NAME}
cd ${WORKFLOW_NAME}

pycbc_generate_hwinj --approximant EOBNRv2 --order pseudoFourPN --mass1 1.4 --mass2 1.4 --inclination 0.0 --polarization 0.0 --ra 1.0 --dec 1.0 --taper TAPER_START --network-snr 28 --geocentric-end-time ${INJECTION_TIME} --waveform-low-frequency-cutoff 30.0 --gps-start-time ${START_TIME} --gps-end-time ${END_TIME} --instruments H1 --frame-type ${FRAME_TYPE} --strain-high-pass H1:20 --sample-rate H1:16384 --psd-estimation median --psd-segment-length 16 --psd-segment-stride 8 --psd-inverse-length 16 --psd-low-frequency-cutoff 30 --psd-high-frequency-cutoff 1000 --pad-data H1:8 --channel-name ${CHANNEL_NAME}

HWINJ_PATH=${PWD}/`ls hwinjcbc_*.xml.gz`

# This makes the workflow.
# The parameters of the software injection (named software injection)
# are passed to pycbc_adjust_strain and pycbc_inspiral via ${HWINJ_PATH}.
pycbc_make_cal_workflow \
  --name ${WORKFLOW_NAME} \
  --config-files ${CONFIG_PATH} \
  --config-overrides workflow:start-time:${START_TIME} \
                     workflow:end-time:${END_TIME} \
                     workflow-tmpltbank:tmpltbank-pregenerated-bank:${HWINJ_PATH} \
                     adjust_strain:injection-file:${HWINJ_PATH} \
                     adjust_strain:transfer-function-a-tst:${PATH_ATST} \
		     adjust_strain:transfer-function-a-pu:${PATH_APU} \
                     adjust_strain:transfer-function-c:${PATH_C} \
                     adjust_strain:transfer-function-d:${PATH_D}

# This submits the workflow to the cluster then runs it.
pycbc_submit_dax --no-create-proxy --dax ${WORKFLOW_NAME}/${WORKFLOW_NAME}.dax --accounting-group sugwg.astro

cd ${BASE_PATH}

done
