# To properly use this PowerShell script within userdata for a new EC2 image, 
# be sure to embed it within powershell tags.
#
# Other tags that may be of use are persist, which determines whether the 
# userdata will run after reboots, and script which is for shell scripts to 
# be run.
#
# To obtain the right version of Python and the right version of WatchMaker, 
# be sure to modify the variables $Version and $WatchMakerUrl.
#
# In addition, pass in a string to a root certificate host url to have
# certificates downloaded and imported into this Windows instance.

#-----------------------------------------------------------------------------#

# Urls for obtaining Python MSI and WatchMaker.
[CmdLetBinding()] 
Param( 
  [String]$Version = "2.7.11"
  ,
  [String]$PythonUrl = ""
  ,
  [String]$WatchMakerUrl = "https://s3.amazonaws.com/dicelab-eggs/test-watchmaker-0.1-py2.6.egg"
  ,
  [String]$RootCertUrl
  [String]$WatchMakerUrl = "https://s3.amazonaws.com/dicelab-eggs/watchmaker-0.1-py2.7.egg"
)

# Location to save files.
$SaveDir = ${env:Temp}

# Log files for debugging user-data and PowerShell commands.
$LogFile = "${SaveDir}\UserData_Output_$(Get-Date -Format `"yyyyMMdd_hhmmsstt`").log"
Start-Transcript -Path "${SaveDir}\Transcript_Output_$(Get-Date -Format `"yyyyMMdd_hhmmsstt`").log" -Append

$PythonMSI = "python-" + ${Version} + ".msi";
if( $PythonUrl -eq "" ) {
  $PythonUrl = 'https://www.python.org/ftp/python/' + ${Version} + '/' + ${PythonMSI}
}

function Log {
  Param( [string]$Message )
  $Message | Out-File -Filepath $LogFile -Append
}

Log "Python MSI will be onbtained from ${PythonUrl}."
Log "WatchMaker will be installed from ${WatchMakerUrl}."

function Install-Python-MSI {
  Param( [String]$PathToMSI )
  $Arguments = @()
  $Arguments += "/i"
  $Arguments += "`"${PathToMSI}`""
  $Arguments += "ALLUSERS=`"1`""
  $Arguments += "/passive"
  Start-Process "msiexec.exe" -ArgumentList ${Arguments} -Wait
}

function Download-File {
  Param( [String]$Url, [String]$SavePath )
  # Download a file, if it doesn't already exist.
  if( !(Test-Path ${SavePath} -PathType Leaf) ) {
    (New-Object System.Net.WebClient).DownloadFile(${Url}, ${SavePath})
    Log "Downloaded ${Url} to ${SavePath}."
  }
}

function Reset_Env_Variable {
  foreach( $Level in "Machine", "User" ) {
    [Environment]::GetEnvironmentVariables($Level).GetEnumerator() | % {
      # For Path variables, append the new values, if they're not already in there.
      if($_.Name -match 'Path$') { 
        $_.Value = ($((Get-Content "Env:$($_.Name)") + ";$($_.Value)") -split ';' | Select -unique) -join ';'
      }
      $_
    } | Set-Content -Path { "Env:$($_.Name)" }
  }
}

function Get-Python {
  $SavePath = '' + $SaveDir + '\' + $PythonMSI;
  if( !(Test-Path -PathType Container $SaveDir) ) {
    Log "${SaveDir} does not exist."
    exit
  }

  Download-File $PythonUrl $SavePath
  Install-Python-MSI ${SavePath}
  Log "Installed Python ${Version}."

  [Environment]::SetEnvironmentVariable("Path", "${env:Path};C:\Python27\;C:\Python27\Scripts\", "Machine")
  Log "Added Python directories to environment variable, PATH."
  Reset_Env_Variable

  # Upgrade pip.
  # pip install --upgrade pip : Do not use this as it throws an access denied error.
  easy_install -U pip
  Log "Upgraded pip using easy_intall."
  
  # Install Python dependencies for WatchMaker -- actually, WatcMaker will take care of these.
  #pip install boto3
  #pip install pyyaml
  #Log "Added Python modules, boto3 and pyyaml, for WatchMaker."
  easy_install ${WatchMakerUrl}
  Log "Installed Plus3's WatchMaker and dependencies for Python."

  python -c 'import watchmaker'
  Log "Tested that watchmaker installed."
}

function Import-509Certificate {
  Param( [String]$CertFile, [String]$CertRootStore, [String]$CertStore )
  Log "Importing certificate: ${CertFile} ..."
  $Pfx = New-Object System.Security.Cryptography.X509Certificates.X509Certificate2
  $Pfx.import($CertFile)
  $Store = New-Object System.Security.Cryptography.X509Certificates.x509Store(${CertStore},${CertRootStore})
  $Store.open("MaxAllowed")
  $Store.add($Pfx)
  $Store.close()
}

function Install-RootCerts {
  Param( [string]$RootCertHost )
  $CertDir = "${SaveDir}\certs-$(${RootCertHost}.Replace(`"http://`",`"`"))"
  Log "Creating directory for certificates at ${CertDir}."
  New-Item -Path ${CertDir} -ItemType "directory" -Force -WarningAction SilentlyContinue | Out-Null

  Log "... Checking for certificates hosted by: ${RootCertHost} ..."
  $CertUrls = @((Invoke-WebRequest -Uri ${RootCertHost}).Links | Where { $_.href -Match ".*\.cer$" } | ForEach-Object { ${RootCertHost} + $_.href })

  Log "... Found $(${CertUrls}.count) certificate(s) ..."
  Log "... Downloading and importing certificate(s) ..."
  foreach( $UrlItem in ${CertUrls} ) {
    $CertFile = "${CertDir}\$((${UrlItem}.split('/'))[-1])"
    Download-File ${UrlItem} ${CertFile}
    if( ${CertFile} -Match ".*root.*" ) {
      Import-509Certificate ${CertFile} "LocalMachine" "Root"
      Log "Imported trusted root CA certificate: ${CertFile}"
    } else {
      Import-509Certificate ${CertFile} "LocalMachine" "CA"
      Log "Imported intermediate CA certificate: ${CertFile}"
    }
  }
  Log "... Completed import of certificate(s) from: ${RootCertHost}"
}

Log "Root certificates host url is ${RootCertUrl}."
if( ${RootCertUrl} ) {
  # Download and install the root certificates.
  try {
    Install-RootCerts ${RootCertUrl}
  } catch {
    # Unhandled exception, log an error and exit.
    Log "ERROR: Encountered a problem installing root certificates."
    Stop-Transcript
    Throw
  }
}

Get-Python
Log "UserData PowerShell script finished."
Stop-Transcript
