[CmdLetBinding()]
Param(
  [String]$PythonUrl = "https://www.python.org/ftp/python/3.8.10/python-3.8.10-amd64.exe"
  ,
  [String]$GitUrl
  ,
  [String]$RootCertUrl
)
$__ScriptName = "watchmaker-boostrap.ps1"

# Location to save files.
$SaveDir = ${Env:Temp}

function Install-Msi {
  Param( [String]$Installer, [String[]]$InstallerArgs )
  $Arguments = @()
  $Arguments += "/i"
  $Arguments += "`"${Installer}`""
  $Arguments += $InstallerArgs
  Write-Verbose "Installing $Installer"
  $ret = Start-Process "msiexec.exe" -ArgumentList ${Arguments} -NoNewWindow -PassThru -Wait
}

function Install-Exe {
  Param( [String]$Installer, [String[]]$InstallerArgs )
  Write-Verbose "Installing $Installer"
  $ret = Start-Process "${Installer}" -ArgumentList ${InstallerArgs} -NoNewWindow -PassThru -Wait
}

function Download-File {
  Param( [string]$Url, [string]$SavePath )
  # Download a file, if it doesn't already exist.
  if( !(Test-Path ${SavePath} -PathType Leaf) ) {
    [Net.ServicePointManager]::SecurityProtocol = [Net.ServicePointManager]::SecurityProtocol -bor [Net.SecurityProtocolType]::SystemDefault
    $SecurityProtocolTypes = @([Net.SecurityProtocolType].GetEnumNames())
    if ("Tls11" -in $SecurityProtocolTypes) {
        [Net.ServicePointManager]::SecurityProtocol = [Net.ServicePointManager]::SecurityProtocol -bor [Net.SecurityProtocolType]::Tls11
    }
    if ("Tls12" -in $SecurityProtocolTypes) {
        [Net.ServicePointManager]::SecurityProtocol = [Net.ServicePointManager]::SecurityProtocol -bor [Net.SecurityProtocolType]::Tls12
    }

    (New-Object System.Net.WebClient).DownloadFile(${Url}, ${SavePath})
    Write-Verbose "Downloaded ${Url} to ${SavePath}"
  }
}

function Reset-EnvironmentVariables {
  foreach( $Level in "Machine", "User" ) {
    [Environment]::GetEnvironmentVariables(${Level}).GetEnumerator() | % {
      # For Path variables, append the new values, if they're not already in there.
      if($_.Name -match 'Path$') {
        $_.Value = ($((Get-Content "Env:$($_.Name)") + ";$($_.Value)") -split ';' | Select -unique) -join ';'
      }
      $_
    } | Set-Content -Path { "Env:$($_.Name)" }
  }
}

function Install-Python {
  $PythonFile = "${SaveDir}\$(${PythonUrl}.split("/")[-1])"

  Download-File -Url ${PythonUrl} -SavePath ${PythonFile}

  if ($PythonFile -match "^.*msi$") {
    $Arguments = @()
    $Arguments += "/qn"
    $Arguments += "ALLUSERS=1"
    $Arguments += "ADDLOCAL=ALL"
    Install-Msi -Installer ${PythonFile} -InstallerArgs ${Arguments}
  }
  elseif ($PythonFile -match "^.*exe$") {
    $Arguments = @()
    $Arguments += "/quiet"
    $Arguments += "InstallAllUsers=1"
    $Arguments += "PrependPath=1"
    Install-Exe -Installer ${PythonFile} -InstallerArgs ${Arguments}
  }

  Write-Verbose "Installed Python"
}

function Install-Git {
  $GitFile = "${SaveDir}\$(${GitUrl}.split("/")[-1])"

  Download-File -Url ${GitUrl} -SavePath ${GitFile}

  $Arguments = @()
  $Arguments += "/SILENT"
  $Arguments += "/NOCANCEL"
  $Arguments += "/NORESTART"
  $Arguments += "/SAVEINF=${SaveDir}\git_params.txt"
  Install-Exe -Installer ${GitFile} -InstallerArgs ${Arguments}

  Write-Verbose "Installed Git"
}

function Import-509Certificate {
  Param( [String]$CertFile, [String]$CertRootStore, [String]$CertStore )
  Write-Verbose "Importing certificate: ${CertFile} ..."
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
  Write-Verbose "Creating directory for certificates at ${CertDir}."
  New-Item -Path ${CertDir} -ItemType "directory" -Force -WarningAction SilentlyContinue | Out-Null

  Write-Verbose "... Checking for certificates hosted by: ${RootCertHost} ..."
  $CertUrls = @((Invoke-WebRequest -Uri ${RootCertHost}).Links | Where { $_.href -Match ".*\.cer$" } | ForEach-Object { ${RootCertHost} + $_.href })

  Write-Verbose "... Found $(${CertUrls}.count) certificate(s) ..."
  Write-Verbose "... Downloading and importing certificate(s) ..."
  foreach( $UrlItem in ${CertUrls} ) {
    $CertFile = "${CertDir}\$((${UrlItem}.split('/'))[-1])"
    Download-File ${UrlItem} ${CertFile}
    if( ${CertFile} -match ".*root.*" ) {
      Import-509Certificate ${CertFile} "LocalMachine" "Root"
      Write-Verbose "Imported trusted root CA certificate: ${CertFile}"
    } else {
      Import-509Certificate ${CertFile} "LocalMachine" "CA"
      Write-Verbose "Imported intermediate CA certificate: ${CertFile}"
    }
  }
  Write-Verbose "... Completed import of certificate(s) from: ${RootCertHost}"
}

# Main

if( ${RootCertUrl} ) {
  # Download and install the root certificates.
  Write-Verbose "Root certificates host url is ${RootCertUrl}"
  Install-RootCerts ${RootCertUrl}
}

# Install Python
Write-Verbose "Python will be installed from ${PythonUrl}"
Install-Python

if( ${GitUrl} ) {
  # Download and install git
  Write-Verbose "Git will be installed from ${GitUrl}"
  Install-Git
}

Reset-EnvironmentVariables
Write-Verbose "Reset the PATH environment for this shell"

if ("$Env:TEMP".TrimEnd("\") -eq "${Env:windir}\System32\config\systemprofile\AppData\Local\Temp") {
  $Env:TEMP, $Env:TMP = "${Env:windir}\Temp", "${Env:windir}\Temp"
  Write-Verbose "Forced TEMP envs to ${Env:windir}\Temp"
}

Write-Verbose "${__ScriptName} complete!"
