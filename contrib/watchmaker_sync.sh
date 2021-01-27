#!/bin/bash
set -eo pipefail
#
# Script to automate the updating of the Watchmaker-binary
# repository-contents
#################################################################
PROGNAME="$( basename "${0}" )"
DEBUG="${DEBUG:-UNDEF}"
GET_WAM="watchmaker-latest-standalone-linux-x86_64"
HTTP_PROXY="${HTTP_PROXY:-}"
HTTPS_PROXY="${HTTPS_PROXY:-}"
REPO_DIR="${REPO_DIR:-}"
WAM_STAGE="${REPO_DIR}/${GET_WAM}"
WATCHMAKER_URL="https://watchmaker.cloudarmor.io/releases/latest/${GET_WAM}"

# Make interactive-execution more-verbose unless explicitly told not to
if [[ $( tty -s ) -eq 0 ]] && [[ ${DEBUG} == "UNDEF" ]]
then
   DEBUG="true"
fi


# Error handler function
function err_exit {
   local ERRSTR
   local ISNUM
   local SCRIPTEXIT

   ERRSTR="${1}"
   ISNUM='^[0-9]+$'
   SCRIPTEXIT="${2:-1}"

   if [[ ${DEBUG} == true ]]
   then
      # Our output channels
      logger -i -t "${PROGNAME}" -p kern.crit -s -- "${ERRSTR}"
   else
      logger -i -t "${PROGNAME}" -p kern.crit -- "${ERRSTR}"
   fi

   # Only exit if requested exit is numerical
   if [[ ${SCRIPTEXIT} =~ ${ISNUM} ]]
   then
      exit "${SCRIPTEXIT}"
   fi
}

# Print out a basic usage message
function UsageMsg {

   local SCRIPTEXIT
   SCRIPTEXIT="${1:-1}"

   (
      echo "Usage: ${0} [GNU long option] [option] ..."
      echo "  Options:"
      printf '\t%-4s%s\n' '-h' 'Print this message'
      printf '\t%-4s%s\n' '-P' 'HTTPS proxy information'
      printf '\t%-4s%s\n' '-p' 'HTTP proxy information'
      printf '\t%-4s%s\n' '-r' 'Repository root-folder'
      printf '\t%-4s%s\n' '-u' 'URL to download watchmaker stadalone binaries from'
      echo "  GNU long options:"
      printf '\t%-20s%s\n' '--help' 'See "-h" short-option'
      printf '\t%-20s%s\n' '--http-proxy' 'See "-p" short-option'
      printf '\t%-20s%s\n' '--https-proxy' 'See "-P" short-option'
      printf '\t%-20s%s\n' '--repo-dir' 'See "-r" short-option'
      printf '\t%-20s%s\n' '--wam-url' 'See "-u" short-option'
   )
   exit "${SCRIPTEXIT}"
}

# Fetch WAM standalone package and return version fetched
function GetWam {
   local WATCHMAKER_HOST

   # Extract hostname from URL
   WATCHMAKER_HOST="$(
       echo ${WATCHMAKER_URL} | sed \
        -e 's#http[s]://##' \
        -e 's#/.*$##'
      )"

   if [[ -z ${HTTP_PROXY} ]] &&
      [[ $(
         timeout 5 bash -c "echo > /dev/tcp/${WATCHMAKER_HOST}/80"
      )$? -ne 0 ]] && [[ $(
         timeout 5 bash -c "echo > /dev/tcp/${WATCHMAKER_HOST}/443"
      )$? -ne 0 ]]
   then
      err_exit "${WATCHMAKER_HOST} not reachable on port 80 or 443" "none"
      err_exit "Do you need to specify an HTTP_PROXY?" 1
   fi


   # Download watchmaker to temporary location
   install -bDm 0755 <( 
         export http_proxy="${HTTP_PROXY}" > /dev/null && \
         export https_proxy="${HTTPS_PROXY}" > /dev/null && \
         curl -s "${WATCHMAKER_URL}"
      ) "${WAM_STAGE}" || \
        err_exit "Failed to fetch watchmaker standalone-binary" 1

   # return wam version
   "${WAM_STAGE}" --version | sed -e 's/\s.*$//' -e 's#^.*/##'
}


# Parse the args
OPTIONBUFR=$( getopt \
   -o hp:P:r:u: \
   --long help,http-proxy:,https-proxy:,repo-dir:,wam-url: \
   -n "${PROGNAME}" -- "$@")

eval set -- "${OPTIONBUFR}"

###################################
# Parse contents of ${OPTIONBUFR}
###################################
while true
do
   case "$1" in
      -h|--help)
            UsageMsg 0
            ;;
      -P|--https-proxy)
            case "$2" in
               "")
                  err_exit "Error: option required but not specified"
                  shift 2;
                  exit 1
                  ;;
               *)
                  HTTPS_PROXY="${2}"
                  shift 2;
                  ;;
            esac
            ;;
      -p|--http-proxy)
            case "$2" in
               "")
                  err_exit "Error: option required but not specified"
                  shift 2;
                  exit 1
                  ;;
               *)
                  HTTP_PROXY="${2}"
                  shift 2;
                  ;;
            esac
            ;;
      -r|--repo-dir)
            case "$2" in
               "")
                  err_exit "Error: option required but not specified"
                  shift 2;
                  exit 1
                  ;;
               *)
                  REPO_DIR="${2}"
                  shift 2;
                  ;;
            esac
            ;;
      -u|--wam-url)
            case "$2" in
               "")
                  err_exit "Error: option required but not specified"
                  shift 2;
                  exit 1
                  ;;
               *)
                  WATCHMAKER_URL="${2}"
                  shift 2;
                  ;;
            esac
            ;;
      --)
         shift
         break
         ;;
      *)
         err_exit "Internal error!"
         exit 1
         ;;
   esac
done


######################
## Main program-flow
######################

if [[ -z ${REPO_DIR:-} ]]
then
   err_exit "Failed to specify a repo-location and no env-var specified" "none"
   UsageMsg 1
fi

# How to handle proxy-settings if only one specified
if [[ -n ${HTTP_PROXY} ]] && [[ -z ${HTTPS_PROXY} ]]
then
   HTTPS_PROXY="${HTTP_PROXY}"
elif [[ -n ${HTTPS_PROXY} ]] && [[ -z ${HTTP_PROXY} ]]
then
   HTTP_PROXY="${HTTPS_PROXY}"
fi

WAM_VER="$( GetWam )"
WAM_INSTDIR="${REPO_DIR}/${WAM_VER}"

if [[ -d ${WAM_INSTDIR} ]]
then
   err_exit "Already latest Watchmaker version. Nuking temp-file... " "none"
   rm "${WAM_STAGE}" || err_exit FAILED exit 1
   err_exit "Success!" "none"
else
   err_exit "Creating ${WAM_INSTDIR}... " "none"
   install -dDm 0755 -o root -g root "${WAM_INSTDIR}" || err_exit FAILED 1
   err_exit "Success!" "none"

   err_exit "Moving ${WAM_STAGE} into ${WAM_INSTDIR}... " "none"
   mv "${WAM_STAGE}" "${WAM_INSTDIR}" || err_exit FAILED 1
   err_exit "Success!" "none"

   err_exit "Creating 'watchmaker' alias... " "none"
   (
     cd "${WAM_INSTDIR}" || err_exit "Failed changind directory" 1
     ln "${GET_WAM}" watchmaker || err_exit FAILED 1
   )
   err_exit "Success!" "none"

   if [[ -L ${REPO_DIR}/latest ]]
   then
      err_exit "Nuking existing 'latest' pointer... " "none"
      rm "${REPO_DIR}/latest" || err_exit FAILED 1
      err_exit "Success!" "none"
   fi

   err_exit "Updating 'latest' pointer... " "none"
   (
     cd "${REPO_DIR}" || err_exit "Failed changind directory" 1
     ln -fs "${WAM_VER}" "${REPO_DIR}/latest" || err_exit FAILED 1
   )
   err_exit "Success!" "none"
fi
