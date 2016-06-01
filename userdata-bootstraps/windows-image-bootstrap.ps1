<powershell>
# Grab instance volume letter and current user running script.
$DriveLetter = (Get-Partition | Where-Object -FilterScript {$_.DriveLetter})[0].DriveLetter
$UserName = [Environment]::UserName

# Location to save files.
$SaveDir = "${DriveLetter}:\Users\${UserName}\Downloads"

# Log file for debugging user-data.
$LogFile = "${DriveLetter}:\UserData_Output_$(Get-Date -Format `"yyyyMMdd_hhmmsstt`").log"

function Log {
  Param( [string]$Message )
  $Message | Out-File -Filepath $LogFile -Append
}

Log "User running this script is ${UserName}."
Log "Downloading and creating entries in drive: ${DriveLetter}."

function Install-Python-MSI {
  Param( [string]$PathToMSI )
  $Arguments = @()
  $Arguments += "/i"
  $Arguments += "`"${PathToMSI}`""
  $Arguments += "ALLUSERS=`"1`""
  $Arguments += "/passive"
  Start-Process "msiexec.exe" -ArgumentList ${Arguments} -Wait
}

function Download-File {
  Param( [string]$Url, [string]$SavePath )
  # Download a file, if it doesn't already exist.
  if( !(Test-Path ${SavePath} -PathType Leaf)) {
    Log "Downloading ${Url} to ${SavePath}."
    (New-Object System.Net.WebClient).DownloadFile(${Url}, ${SavePath})
  }
}

function Get-Python {
  Param( [string]$Version="2.7.11" )
  # Download Python indicated by version. For example: Get-Python "2.7.11"
  $FileName = 'python-' + $Version + '.msi';
  $SavePath = '' + $SaveDir + '\' + $FileName;
  if( !(Test-Path -PathType Container $SaveDir) ) {
    Log "${SaveDir} does not exist."
    exit
  }

  $Url = 'https://www.python.org/ftp/python/' + $Version + '/' + $FileName
  Download-File $Url $SavePath
  Log "Installing Python ${Version}."
  Install-Python-MSI ${SavePath}

  Log "Add Python to environment variable, PATH."
  [Environment]::SetEnvironmentVariable("Path", "${env:Path};C:\Python27\;C:\Python27\Scripts\", "Machine")
}

Get-Python
</powershell>