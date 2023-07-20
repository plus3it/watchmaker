<powershell>
$BootstrapUrl = "https://watchmaker.cloudarmor.io/releases/latest/watchmaker-bootstrap.ps1"
$PythonUrl = "https://www.python.org/ftp/python/3.10.11/python-3.10.11-amd64.exe"
$PypiUrl = "https://pypi.org/simple"

# Use TLS 1.2+
[Net.ServicePointManager]::SecurityProtocol = "Tls12, Tls13"

# Download bootstrap file
$BootstrapFile = "${Env:Temp}\$(${BootstrapUrl}.split('/')[-1])"
(New-Object System.Net.WebClient).DownloadFile("$BootstrapUrl", "$BootstrapFile")

# Install python
& "$BootstrapFile" -PythonUrl "$PythonUrl" -Verbose -ErrorAction Stop

# Install Watchmaker
python -m pip install --index-url="$PypiUrl" --upgrade pip setuptools
python -m pip install --index-url="$PypiUrl" --upgrade watchmaker

# Run Watchmaker
watchmaker --log-level debug --log-dir=C:\Watchmaker\Logs
</powershell>
