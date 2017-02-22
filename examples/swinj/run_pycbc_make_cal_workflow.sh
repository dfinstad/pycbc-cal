#! /bin/bash

# random times
#for INJECTION_TIME in 1126253357 1126254257 1126255157 1126256417 1126257557 1126260497 1126266197 1126261397 1126264997 1126297757 1126294817 1126296497; do
for INJECTION_TIME in 1165378840; do

# times to analyze
START_TIME=$((${INJECTION_TIME} - 750))
END_TIME=$((${START_TIME} + 2048))

FRAME_TYPE=L1:L1_HOFT_C01
CHANNEL_NAME=L1:DCS-CALIB_STRAIN_C01

# The location of your configuration (.ini) file
CONFIG_PATH=${PWD}/config.ini

# Paths to the transfer functions
BASE_PATH=${PWD}
TF_PATH=${HOME}/src/pycbc-cal-backup/data/o2/L1/
PATH_ATST=${TF_PATH}/tst_tf.txt
PATH_APU=${TF_PATH}/pum_tf.txt
PATH_AUIM=${TF_PATH}/uim_tf.txt
PATH_C=${TF_PATH}/c_tf.txt
PATH_D=${TF_PATH}/d_tf.txt

WORKFLOW_NAME=cal_${INJECTION_TIME}

# Convert parameter degrees to radians
INC=`python -c "import numpy; print numpy.deg2rad(82.3)"`
POL=`python -c "import numpy; print numpy.deg2rad(181.)"`
RA=`python -c "import numpy; print numpy.deg2rad(131.75)"`
DEC=`python -c "import numpy; print numpy.deg2rad(43.3)"`

mkdir ${WORKFLOW_NAME}
cd ${WORKFLOW_NAME}

# tweak settings to ~match GW170104
pycbc_generate_hwinj --approximant SEOBNRv4 --order pseudoFourPN --mass1 33.8 --mass2 22.7 --inclination ${INC} --polarization ${POL} --ra ${RA} --dec ${DEC} --taper TAPER_START --network-snr 13 --geocentric-end-time ${INJECTION_TIME} --waveform-low-frequency-cutoff 30.0 --gps-start-time ${START_TIME} --gps-end-time ${END_TIME} --instruments L1 --frame-type ${FRAME_TYPE} --strain-high-pass L1:20 --sample-rate L1:16384 --psd-estimation median --psd-segment-length 16 --psd-segment-stride 8 --psd-inverse-length 16 --psd-low-frequency-cutoff 30 --psd-high-frequency-cutoff 1000 --pad-data L1:8 --channel-name ${CHANNEL_NAME}

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
                     adjust_strain:transfer-function-a-uim:${PATH_AUIM} \
                     adjust_strain:transfer-function-c:${PATH_C} \
                     adjust_strain:transfer-function-d:${PATH_D}

# This submits the workflow to the cluster then runs it.
echo pycbc_submit_dax --no-create-proxy --dax ${WORKFLOW_NAME}/${WORKFLOW_NAME}.dax --accounting-group sugwg.astro

cd ${BASE_PATH}

done
