#! /bin/bash

# Various groups of injection times

# Ben's GW150914 injection times
#for INJECTION_TIME in 1126253357; do
#for INJECTION_TIME in 1126253357 1126254257 1126255157 1126256417; do #1126253357
for INJECTION_TIME in 1126257557 1126260497 1126266197 1126261397 1126264997 1126297757 1126294817 1126296497 1126311917 1126313117 1126315517 1126316717; do

#for INJECTION_TIME in 1126311917 1126294817 1126266197 1126260497; do

# L1 injections
#for INJECTION_TIME in 1126253357 1126254257 1126255157 1126256417 1126257557 1126260497 1126266197 1126261397 1126264997 1126297757 1126294817 1126296497; do
#for INJECTION_TIME in 1167613218; do #1167614218 1167615218 1168156818 1168157818 1168158818 1168159818 1168509618 1168510618 1168511618 1168512618 1168513618 1168514618; do

# H1 injections
#for INJECTION_TIME in 1167804018; do
#for INJECTION_TIME in 1167811218 1167872418 1167873418 1167874418; do
#1167875418 1167876418 1167883218 1167884218 1167885218 1167912018 1167913018 1167930018; do

# Coincident O2 injection times
#for INJECTION_TIME in 1168923750 1168924750 1168925750 1168926750; do #1168923750
#for INJECTION_TIME in 1168927750 1168928750 1168932750 1168933750; do

# times to analyze
START_TIME=$((${INJECTION_TIME} - 750))
END_TIME=$((${START_TIME} + 2048))

# check if this time falls in coinc time for both ifos
#pycbc_coinc_time --min-analysis-segments 1 --segment-start-pad 112 --segment-end-pad 16 --segment-length 512 --pad-data 8 --segment-server segments.ligo.org --veto-definer ${HOME}/src/pycbc-cal/examples/swinj/H1L1-HOFT_C01_O2_CBC.xml --verbose --science-veto-levels 1 --trigger-veto-levels 12H --science-names L1:DMT-ANALYSIS_READY:1 H1:DMT-ANALYSIS_READY:1 --gps-start-time ${START_TIME} --gps-end-time ${END_TIME}

#INJ_TIME_FLAG=$(head -n 1 temp_injection_flag.txt)
#if [[ ${INJ_TIME_FLAG} != 1 ]]; then
#echo Skipping bad injection time
#continue
#fi

# Adjust these settings to control injection type and
# detector model to use
EVENT=bens #150914 #170104
MODEL=O1
IFO=H1

# The location of your configuration (.ini) file
#CONFIG_PATH=${PWD}/config_o2_${IFO}.ini

# Paths to the transfer functions
BASE_PATH=${PWD}
if [[ ${MODEL} == O2 ]]; then
echo Using O2 model
TF_PATH=${HOME}/src/pycbc-cal/data/o2/${IFO}
PATH_ATST=${TF_PATH}/tst_tf_2017-01-24.txt
PATH_APU=${TF_PATH}/pum_tf_2017-01-24.txt
PATH_AUIM=${TF_PATH}/uim_tf_2017-01-24.txt
PATH_C=${TF_PATH}/c_tf_2017-01-24.txt
PATH_D=${TF_PATH}/d_tf_2017-01-24.txt
CONFIG_PATH=${PWD}/config_o2_${IFO}.ini
FRAME_TYPE=${IFO}:${IFO}_HOFT_C01
CHANNEL_NAME=${IFO}:DCS-CALIB_STRAIN_C01
else
echo Using O1 model
TF_PATH=${HOME}/src/pycbc-cal/data/o1/${IFO}
PATH_ATST=${TF_PATH}/tf_A_tst.txt
PATH_APU=${TF_PATH}/tf_A_pu.txt
PATH_C=${TF_PATH}/tf_C.txt
PATH_D=${TF_PATH}/tf_D.txt
CONFIG_PATH=${PWD}/config_${IFO}.ini
FRAME_TYPE=${IFO}:${IFO}_HOFT_C02
CHANNEL_NAME=${IFO}:DCS-CALIB_STRAIN_C02
fi

WORKFLOW_NAME=cal_${INJECTION_TIME}_${EVENT}_${IFO}_${MODEL}model

if [[ ${EVENT} == 170104 ]]; then
echo Making 170104 injection
# Set parameters to mimic 170104 event
# Convert parameter degrees to radians
INC=`python -c "import numpy; print numpy.deg2rad(82.3)"`
POL=`python -c "import numpy; print numpy.deg2rad(181.)"`
RA=`python -c "import numpy; print numpy.deg2rad(131.75)"`
DEC=`python -c "import numpy; print numpy.deg2rad(43.3)"`
M1=33.8
M2=22.7
SNR=13.
S1Z=0.
S2Z=0.
elif [[ ${EVENT} == 150914 ]]; then
echo Making 150914 injection
# Set parameters to mimic 150914 event
INC=2.66
POL=1.57
RA=1.79
DEC=-1.23
M1=36.
M2=29.
SNR=25.
S1Z=0.
S2Z=0.
elif [[ ${EVENT} == bens ]]; then
echo "Making Ben's injection"
INC=0.
POL=0.
RA=1.
DEC=1.
M1=47.9
M2=36.6
SNR=28.0
S1Z=0.96
S2Z=-0.9
fi

mkdir ${WORKFLOW_NAME}
cd ${WORKFLOW_NAME}

# create injection
pycbc_generate_hwinj --approximant SEOBNRv2 --order pseudoFourPN --mass1 ${M1} \
    --mass2 ${M2} --inclination ${INC} --polarization ${POL} --ra ${RA} --dec ${DEC} \
    --taper TAPER_START --network-snr ${SNR} --geocentric-end-time ${INJECTION_TIME} \
    --waveform-low-frequency-cutoff 30.0 --gps-start-time ${START_TIME} \
    --gps-end-time ${END_TIME} --instruments ${IFO} --frame-type ${FRAME_TYPE} \
    --strain-high-pass ${IFO}:20 --sample-rate ${IFO}:16384 --psd-estimation median \
    --psd-segment-length 16 --psd-segment-stride 8 --psd-inverse-length 16 \
    --psd-low-frequency-cutoff 30 --psd-high-frequency-cutoff 1000 --pad-data ${IFO}:8 \
    --channel-name ${CHANNEL_NAME} --spin1z ${S1Z} --spin2z ${S2Z}

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
                     #adjust_strain:transfer-function-a-uim:${PATH_AUIM}

# This submits the workflow to the cluster then runs it.
pycbc_submit_dax --no-create-proxy --dax ${WORKFLOW_NAME}/${WORKFLOW_NAME}.dax --accounting-group sugwg.astro

cd ${BASE_PATH}

done
