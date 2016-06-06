#!/usr/bin/env bash
set -e

# Set default option values
ENTENV="${SYSTEMPREP_ENVIRONMENT:-False}"
OUPATH="${SYSTEMPREP_OUPATH}"
COMPUTERNAME="${SYSTEMPREP_COMPUTERNAME}"
NOREBOOT="${SYSTEMPREP_NOREBOOT:-False}"
SALTSTATES="${SYSTEMPREP_SALTSTATES:-Highstate}"
AWSREGION="${SYSTEMPREP_AWSREGION:-us-east-1}"
AWSCLI_URL="${SYSTEMPREP_AWSCLI_URL:-https://s3.amazonaws.com/aws-cli/awscli-bundle.zip}"
ROOT_CERT_URL="${SYSTEMPREP_ROOT_CERT_URL}"
SYSTEMPREPMASTERSCRIPTSOURCE="${SYSTEMPREP_MASTER_URL:-https://s3.amazonaws.com/systemprep/Rewrite/MasterScripts/systemprep-linuxmaster.py}"
SYSTEMPREPCONFIG="${SYSTEMPREP_CONFIG_URL:-https://s3.amazonaws.com/systemprep/Rewrite/MasterScripts/config.yaml}"
SALTCONTENTURL="${SYSTEMPREP_SALTCONTENT_URL:-https://systemprep-content.s3.amazonaws.com/linux/salt/salt-content.zip}"
SOURCEISS3BUCKET="${SYSTEMPREP_USES3UTILS:-False}"

# System variables
__SCRIPTPATH=$(readlink -f ${0})
__SCRIPTDIR=$(dirname ${__SCRIPTPATH})
__SCRIPTNAME=$(basename ${__SCRIPTPATH})
LOGGER=$(which logger)
TIMESTAMP=$(date -u +"%Y%m%d_%H%M_%S")
LOGDIR=/var/log
LOGTAG=systemprep
LOGFILE="${LOGDIR}/${LOGTAG}-${TIMESTAMP}.log"
LOGLINK="${LOGDIR}/${LOGTAG}.log"
WORKINGDIR=/usr/tmp/"${LOGTAG}"
CLEANUP=true

print_usage()
{
    cat << EOT

  This script is used to bootstrap an instance using the SystemPrep
  Provisioning Framework.
  Parameters may be passed as short-form or long-form arguments, or they may
  be exported as environment variables. Command line arguments take precedence
  over environment variables.

  Usage: ${__SCRIPTNAME} [options]

  Options:
  -e|--environment|\$SYSTEMPREP_ENVIRONMENT
      The environment in which the system is operating. This is parameter
      accepts a tri-state value:
        "True":   Attempt to detect the environment automatically. WARNING:
                  Currently this value is non-functional.
        "False":  (Default) Do not set an environment. Any content that is
                  dependent on the environment will not be available to this
                  system.
        <string>: Set the environment to the value of "<string>". Note that
                  uppercase values will be converted to lowercase.
  -p|--oupath|\$SYSTEMPREP_OUPATH
      The OU in which to place the instance when joining the domain. If unset
      or an empty string, the framework will use the value from the enterprise
      environment pillar. Default is "".
  -t|--computername|\SYSTEMPREP_COMPUTERNAME
      The computername/hostname to apply to the system.
  -n|--noreboot|\$SYSTEMPREP_NOREBOOT
      Prevent the system from rebooting upon successful application of the
      framework.
  -s|--saltstates|\$SYSTEMPREP_SALTSTATES
      Specifies the salt states to apply to the system.
        "None":       Do not apply any salt states.
        "Highstate":  Apply the salt highstate.
        <string>:     Comma-separated string of states to apply
  -g|--region|\$SYSTEMPREP_AWSREGION
      The region hosting the bucket containing the data. Option value is
      ignored unless '-u|--use-s3-utils' is set.
        <string>:   Default is "us-east-1".
  -c|--awscli-url|\$SYSTEMPREP_AWSCLI_URL
      URL hosting an installable bundle of the AWS CLI utility. If empty, the
      utility is not installed.
        <string>:   Default is "https://s3.amazonaws.com/aws-cli/awscli-bundle.zip".
  -r|--root-cert-url|\$SYSTEMPREP_ROOT_CERT_URL
      URL hosting Root CA certificates that should be injected into the system
      cert bundle. If empty, no certs are added.
        <string>:   Default is "".
  -m|--systemprep-master-url|\$SYSTEMPREP_MASTER_URL
      URL hosting the SystemPrep Master Script.
        <string>:   Default is "https://s3.amazonaws.com/systemprep/MasterScripts/systemprep-linuxmaster.py".
  -f|--systemprep-config-url|\$SYSTEMPREP_CONFIG_URL
        <string>:   Default is "https://s3.amazonaws.com/systemprep/MasterScripts/config.yaml".
  -o|--salt-content-url|\$SYSTEMPREP_SALTCONTENT_URL
      URL hosting an archive zip file of the salt content to apply to the
      system.
        <string>:   Default is "https://systemprep-content.s3.amazonaws.com/linux/salt/salt-content.zip".
  -u|--use-s3-utils|\$SYSTEMPREP_USES3UTILS
      Use S3 utils (awscli, python boto) instead of http utils (curl, wget,
      python requests) to download content. Requires '-g|--region'.
  -h|--help
      Display this message.

EOT

}

# Are we EL-compatible and do we have 6.5+ behaviour?
get_mode() {
    UPDATETRUST="/usr/bin/update-ca-trust"
    CERTUTIL="/usr/bin/certutil"
    if [ -x ${UPDATETRUST} ]; then
        echo "6.5"
    elif [ -x ${CERTUTIL} ]; then
        echo "6.0"
    else
        echo "Cannot determine CA update-method. Aborting."
        exit 1
    fi
}  # --- end of function get_mode  ---

# Try to fetch all CA .cer files from our root_cert_url
fetch_ca_certs() {
    if [ $# -ne 2 ]; then
        echo "fetch_ca_certs requires two parameters."
        echo "  \$1, 'url', is a url hosting the root CA certificates."
        echo "  \$2, 'cert_dir', is a directory in which to save the certificates."
        exit 1
    fi

    URL="${1}"
    FETCH_CERT_DIR="${2}"
    WGET="/usr/bin/wget"
    local TIMESTAMP=$(date -u +"%Y%m%d_%H%M_%S")

    # Create a working directory
    if [ -d "${FETCH_CERT_DIR}" ]; then
        echo "'${FETCH_CERT_DIR}' already exists. Recreating for safety."
        mv "${FETCH_CERT_DIR}" "${FETCH_CERT_DIR}"-"${TIMESTAMP}".bak || \
        ( echo "Couldn't move '${FETCH_CERT_DIR}'. Aborting..." && exit 1 )
    fi

    install -d -m 0700 -o root -g root "${FETCH_CERT_DIR}" || \
    ( echo "Could not create '${FETCH_CERT_DIR}'. Aborting..." && exit 1 )

    # Make sure wget is available
    if [ ! -x ${WGET} ]; then
        echo "The wget utility not found. Attempting to install..."
        yum -y install wget || \
        ( echo "Could not install 'wget', which is required to download the certs. Aborting..." && exit 1 )
    fi

    echo "Attempting to download the root CA certs..."
    ${WGET} -r -l1 -nd -np -A.cer -P "${FETCH_CERT_DIR}" --quiet $URL || \
    ( echo "Could not download certs via 'wget'. Check the url. Quitting..." && \
      exit 1 )
}  # --- end of function fetch_ca_certs  ---

# Update CA trust store
update_trust() {
    if [ $# -ne 2 ]; then
        echo "update_trust requires two parameters."
        echo "  \$1, 'mode', is either '6.0' or '6.5', as determined by the 'GetMode' function."
        echo "  \$2, 'cert_dir', is a directory that contains the root certificates."
        exit 1
    fi

    MODE="${1}"
    UPDATE_CERT_DIR="${2}"

    if [[ "6.5" == "${MODE}" ]]; then
        cert_dir="/etc/pki/ca-trust/source/anchors"
        echo "Copying certs to $cert_dir..."
        (cd "${UPDATE_CERT_DIR}" ; find . -print | cpio -vpud "${cert_dir}" )
        echo "Enabling 'update-ca-trust'..."
        update-ca-trust force-enable
        echo "Extracting root certificates..."
        update-ca-trust extract && echo "Certs updated successfully." || \
        ( echo "ERROR: Failed to update certs." && exit 1 )
    elif [[ "6.0" == "${MODE}" ]]; then
        CADIR="/etc/pki/custom-CAs"
        if [ ! -d ${CADIR} ]; then
            install -d -m 0755 ${CADIR}
        fi
        echo "Copying certs to ${CADIR}..."
        ( cd "${UPDATE_CERT_DIR}" ; find . -print | cpio -vpud "${CADIR}" )
        for ADDCER in $(find ${CADIR} -type f -name "*.cer" -o -name "*.CER")
        do
            echo "Adding \"${ADDCER}\" to system CA trust-list"
            ${CERTUTIL} -A -t u,u,u -d . -i "${ADDCER}" || \
            ( echo "ERROR: Failed to update certs." && exit 1 )
        done
    else
        echo "Unknown 'mode'. 'mode' must be '6.5' or '6.0'."
        exit 1
    fi
}  # --- end of function update_trust  ---

# Parse command-line parameters
SHORTOPTS="e:p:ns:g:c:f:r:m:o:t:uh"
LONGOPTS=(
    "environment:,oupath:,noreboot,saltstates:,region:,awscli-url:,"
    "root-cert-url:,systemprep-master-url:,salt-content-url:,use-s3-utils,"
    "systemprep-config-url:,computername:,help")
LONGOPTS_STRING=$(IFS=$''; echo "${LONGOPTS[*]}")
ARGS=$(getopt \
    --options "${SHORTOPTS}" \
    --longoptions "${LONGOPTS_STRING}" \
    --name "${__SCRIPTNAME}" \
    -- "$@")

if [ $? -ne 0 ]; then
    # Bad arguments.
    print_usage
    exit 1
fi

eval set -- "${ARGS}"

while [ true ]; do

    case "${1}" in
        -e|--environment)
            shift; ENTENV="${1}" ;;
        -p|--oupath)
            shift; OUPATH="${1}" ;;
        -n|--noreboot)
            NOREBOOT="True" ;;
        -s|--saltstates)
            shift; SALTSTATES="${1}" ;;
        -g|--region)
            shift; AWSREGION="${1}" ;;
        -c|--awscli-url)
            shift; AWSCLI_URL="${1}" ;;
        -r|--root-cert-url)
            shift; ROOT_CERT_URL="${1}" ;;
        -m|--systemprep-master-url)
            shift; SYSTEMPREPMASTERSCRIPTSOURCE="${1}" ;;
        -f|--systemprep-config-url)
            shift; SYSTEMPREPCONFIG="${1}" ;;
        -o|--salt-content-url)
            shift; SALTCONTENTURL="${1}" ;;
        -u|--use-s3-utils)
            SOURCEISS3BUCKET="True" ;;
        -h|--help)
            print_usage; exit 0 ;;
        --)
            shift; break ;;
        *)
            print_usage
            echo "ERROR: Unhandled option parsing error."
            exit 1
            ;;
    esac
    shift
done

if [[ ! -d ${LOGDIR} ]]; then
    echo "Creating ${LOGDIR} directory." 2>&1 | ${LOGGER} -i -t "${LOGTAG}" -s 2> /dev/console
    mkdir -p ${LOGDIR} 2>&1 | ${LOGGER} -i -t "${LOGTAG}" -s 2> /dev/console
fi
if [[ ! -d ${WORKINGDIR} ]]; then
    echo "Creating ${WORKINGDIR} directory" 2>&1 | ${LOGGER} -i -t "${LOGTAG}" -s 2> /dev/console
    mkdir -p ${WORKINGDIR} 2>&1 | ${LOGGER} -i -t "${LOGTAG}" -s 2> /dev/console
fi
install -b -m 0600 /dev/null ${LOGFILE}
exec > >(tee "${LOGFILE}" | "${LOGGER}" -i -t "${LOGTAG}" -s 2> /dev/console) 2>&1
ln -s -f ${LOGFILE} ${LOGLINK}
cd ${WORKINGDIR}

echo "Entering SystemPrep script -- ${__SCRIPTNAME}"

if [[ -n "${ROOT_CERT_URL}" ]]; then

    fetch_ca_certs "${ROOT_CERT_URL}" "${WORKINGDIR}/certs"
    update_trust "$(get_mode)" "${WORKINGDIR}/certs"

    # Configure the ENV so the awscli sees the updated certs
    export AWS_CA_BUNDLE=/etc/pki/tls/certs/ca-bundle.crt
fi

AWS="/usr/local/bin/aws"
if [[ -n "${AWSCLI_URL}" ]]; then
    AWSCLI_FILENAME=$(echo ${AWSCLI_URL} | awk -F'/' '{ print ( $(NF) ) }')
    AWSCLI_FULLPATH=${WORKINGDIR}/${AWSCLI_FILENAME}
    cd ${WORKINGDIR}
    echo "Downloading aws cli -- ${AWSCLI_URL}"
    curl -L -O -s -S ${AWSCLI_URL} || \
            ( echo "Could not download file. Check the url and whether 'curl' is in the path. Quitting..." && exit 1 )
    hash unzip 2> /dev/null || \
        yum -y install unzip || \
            ( echo "Could not install unzip, which is required to install the awscli. Quitting..." && exit 1 )
    echo "Unzipping aws cli -- ${AWSCLI_FULLPATH}"
    unzip -o $AWSCLI_FULLPATH || ( echo "Could not unzip file. Quitting..." && exit 1 )
    echo "Installing aws cli -- ${WORKINGDIR}/awscli-bundle/install"
    python ${WORKINGDIR}/awscli-bundle/install -i /opt/awscli -b $AWS || \
        ( echo "Could not install awscli. Quitting..." && exit 1 )
fi

SCRIPTFILENAME=$(echo ${SYSTEMPREPMASTERSCRIPTSOURCE} | awk -F'/' '{ print ( $(NF) ) }')
SCRIPTFULLPATH=${WORKINGDIR}/${SCRIPTFILENAME}
if [[ "true" = ${SOURCEISS3BUCKET,,} ]]; then
    echo "Downloading master script from S3 bucket using AWS Tools -- ${SYSTEMPREPMASTERSCRIPTSOURCE}"
    BUCKET=$(echo ${SYSTEMPREPMASTERSCRIPTSOURCE} | awk -F'.' '{ print substr($1,9)}' OFS="/")
    KEY=$(echo ${SYSTEMPREPMASTERSCRIPTSOURCE} | awk -F'/' '{$1=$2=$3=""; print substr($0,4)}' OFS="/")
    $AWS s3 cp s3://${BUCKET}/${KEY} ${SCRIPTFULLPATH} --region ${AWSREGION} || \
        ( BUCKET=$(echo ${SYSTEMPREPMASTERSCRIPTSOURCE} | awk -F'/' '{ print $4 }' OFS="/") ; \
          KEY=$(echo ${SYSTEMPREPMASTERSCRIPTSOURCE} | awk -F'/' '{$1=$2=$3=$4=""; print substr($0,5)}' OFS="/") ; \
          $AWS s3 cp s3://${BUCKET}/${KEY} ${SCRIPTFULLPATH} --region ${AWSREGION} ) || \
              ( echo "Could not download file using AWS Tools. Check the url, and the instance role. Quitting..." && exit 1 )
else
    echo "Downloading master script from web host -- ${SYSTEMPREPMASTERSCRIPTSOURCE}"
    curl -L -O -s -S ${SYSTEMPREPMASTERSCRIPTSOURCE} || \
            ( echo "Could not download file. Check the url and whether 'curl' is in the path. Quitting..." && exit 1 )
fi

if [[ "true" = ${SOURCEISS3BUCKET,,} ]]; then
    BUCKET=$(echo ${SYSTEMPREPCONFIG} | awk -F'.' '{ print substr($1,9)}' OFS="/")
    KEY=$(echo ${SYSTEMPREPCONFIG} | awk -F'/' '{$1=$2=$3=""; print substr($0,4)}' OFS="/")
    $AWS s3 cp s3://${BUCKET}/${KEY} ${SCRIPTFULLPATH} --region ${AWSREGION} || \
        ( BUCKET=$(echo ${SYSTEMPREPCONFIG} | awk -F'/' '{ print $4 }' OFS="/") ; \
          KEY=$(echo ${SYSTEMPREPCONFIG} | awk -F'/' '{$1=$2=$3=$4=""; print substr($0,5)}' OFS="/") ; \
          $AWS s3 cp s3://${BUCKET}/${KEY} ${SCRIPTFULLPATH} --region ${AWSREGION} )
else
    curl -L -O -s -S ${SYSTEMPREPCONFIG}
fi

# Temporarily suppress rsyslog rate limiting
if [[ -e /etc/rsyslog.conf ]]; then
    echo "Temporarily disabling rsyslog rate limiting"
    RSYSLOGFLAG=1
    # Replace or append the $SystemLogRateLimitInterval parameter
    grep -q '^$SystemLogRateLimitInterval' /etc/rsyslog.conf && \
        sed -i.bak -e \
        "s/^$SystemLogRateLimitInterval.*/$SystemLogRateLimitInterval 0/" \
        /etc/rsyslog.conf || \
        sed -i.bak "$ a\$SystemLogRateLimitInterval 0" /etc/rsyslog.conf
    echo "Restarting rsyslog..."
    service rsyslog restart
fi
if [[ -e /etc/systemd/journald.conf ]]; then
    echo "Temporarily disabling journald rate limiting"
    JOURNALDFLAG=1
    # Replace or append the RateLimitInterval parameter
    grep -q '^RateLimitInterval' /etc/systemd/journald.conf && \
        sed -i.bak -e \
        "s/^RateLimitInterval.*/RateLimitInterval=0/" \
        /etc/rsyslog.conf || \
        sed -i.bak "$ a\RateLimitInterval=0" /etc/systemd/journald.conf
    echo "Restarting systemd-journald..."
    systemctl restart systemd-journald.service
fi

echo "Writing SystemPrep Parameters to log file..."
echo "   SaltStates=${SALTSTATES}"
echo "   SaltContentSource=${SALTCONTENTURL}"
echo "   NoReboot=${NOREBOOT}"
echo "   EntEnv=${ENTENV}"
echo "   OuPath=${OUPATH}"
echo "   ComputerName=${COMPUTERNAME}"
echo "   SourceIsS3Bucket=${SOURCEISS3BUCKET}"
echo "   AwsRegion=${AWSREGION}"

echo "Running the SystemPrep master script -- ${SCRIPTFULLPATH}"
python ${SCRIPTFULLPATH} \
    "SaltStates=${SALTSTATES}" \
    "SaltContentSource=${SALTCONTENTURL}" \
    "NoReboot=${NOREBOOT}" \
    "EntEnv=${ENTENV}" \
    "OuPath=${OUPATH}" \
    "ComputerName=${COMPUTERNAME}" \
    "SourceIsS3Bucket=${SOURCEISS3BUCKET}" \
    "AwsRegion=${AWSREGION}" || \
    error_result=$?  # If error, capture the exit code

if [[ -n "${RSYSLOGFLAG}" || -n "${JOURNALDFLAG}" ]]; then
    echo "Sleeping 50 seconds to let logger catch up with the output of the python script..."
    sleep 50
    if [[ -n "${RSYSLOGFLAG}" ]]; then
        echo "Re-storing previous rsyslog configuration"
        mv -f /etc/rsyslog.conf.bak /etc/rsyslog.conf
        echo "Restarting rsyslog..."
        service rsyslog restart
    fi
    if [[ -n "${JOURNALDFLAG}" ]]; then
        echo "Re-storing previous journald configuration"
        mv -f /etc/systemd/journald.conf.bak /etc/systemd/journald.conf
        echo "Restarting systemd-journald..."
        systemctl restart systemd-journald.service
    fi
fi

if [[ -n $error_result ]]; then
    echo "ERROR: There was an error executing the SystemPrep Master script!"
    echo "Check the log file at: ${LOGLINK}"
    echo "Exiting SystemPrep bootstrap script -- ${__SCRIPTNAME}"
    exit $error_result
else
    echo "SUCCESS: SystemPrep Master script completed successfully!"
    if [[ "true" == "${CLEANUP}" ]]; then
        echo "Deleting the working directory -- ${WORKINGDIR}"
        rm -rf ${WORKINGDIR}
    fi
    echo "Exiting SystemPrep bootstrap script -- ${__SCRIPTNAME}"
    exit 0
fi
