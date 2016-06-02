<powershell>
# Location to save files.
$SaveDir = ${env:Temp}

# Log files for debugging user-data and PowerShell commands.
$LogFile = "${SaveDir}\UserData_Output_$(Get-Date -Format `"yyyyMMdd_hhmmsstt`").log"
Start-Transcript -Path "${SaveDir}\Transcript_Output_$(Get-Date -Format `"yyyyMMdd_hhmmsstt`").log" -Append

# Url for obtaining Python MSI.
$Version = "2.7.11"
$PythonMSI = 'python-' + ${Version} + '.msi';
$PythonUrl = 'https://www.python.org/ftp/python/' + ${Version} + '/' + ${PythonMSI}

function Log {
  Param( [string]$Message )
  $Message | Out-File -Filepath $LogFile -Append
}

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
}

Get-Python
Log "UserData PowerShell script finished."
Stop-Transcript
</powershell>
<persist>false</persist>
