# Module to create a watchmaker-win-instance CloudFormation stack
# Assumes that watchmaker-win-instance.template is stored in same directory as watchmaker-win-instance.tf

variable "Name" {
  type        = "string"
  description = "Name of Instance"
}

variable "AmiId" {
  type        = "string"
  description = "ID of the AMI to launch"
}

variable "AppScriptParams" {
  type        = "string"
  description = "Parameter string to pass to the application script. Ignored if AppScriptUrl is blank"
  default     = ""
}

variable "AppScriptShell" {
  type        = "string"
  description = "Shell with which to execute the application script. Ignored if AppScriptUrl is blank"
  default     = "powershell"
}

variable "AppScriptUrl" {
  type        = "string"
  description = "#(Optional) Region-based HTTPS URL to the application script in an S3 bucket. Leave blank to launch without an application script. If specified, an appropriate InstanceRole is required"
  default     = ""
}

variable "AppVolumeDevice" {
  type        = "string"
  description = "#(Optional) Device to mount an extra EBS volume. Leave blank to launch without an extra application volume"
  default     = ""
}

variable "AppVolumeType" {
  type        = "string"
  description = "Type of EBS volume to create. Ignored if AppVolumeDevice is blank"
  default     = "gp2"
}

variable "AppVolumeSize" {
  type        = "string"
  description = "Size in GB of the EBS volume to create. Ignored if AppVolumeDevice is blank"
  default     = "1"
}

variable "KeyPairName" {
  type        = "string"
  description = "Public/private key pairs allow you to securely connect to your instance after it launches"
}

variable "InstanceType" {
  type        = "string"
  description = "Amazon EC2 instance type"
  default     = "t2.micro"
}

variable "InstanceRole" {
  type        = "string"
  description = "(Optional) IAM instance role to apply to the instance"
  default     = ""
}

variable "PrivateIp" {
  type        = "string"
  description = "(Optional) Set a static, primary private IP. Leave blank to auto-select a free IP"
  default     = ""
}

variable "NoPublicIp" {
  type        = "string"
  description = "Controls whether to assign the instance a public IP. Recommended to leave at true _unless_ launching in a public subnet"
  default     = "true"
}

variable "NoReboot" {
  type        = "string"
  description = "Controls whether to reboot the instance as the last step of cfn-init execution"
  default     = "false"
}

variable "SecurityGroupIds" {
  type        = "string"
  description = "List of security groups to apply to the instance"
}

variable "SubnetId" {
  type        = "string"
  description = "ID of the subnet to assign to the instance"
}

variable "PypiIndexUrl" {
  type        = "string"
  description = "URL to the PyPi Index"
  default     = "https://pypi.org/simple"
}

variable "PythonInstaller" {
  type        = "string"
  description = "URL to the Python Installer Executable"
  default     = "https://www.python.org/ftp/python/3.6.3/python-3.6.3-amd64.exe"
}

variable "WatchmakerBootstrapper" {
  type        = "string"
  description = "URL to the Watchmaker PowerShell bootstrapper for Windows"
  default     = "https://raw.githubusercontent.com/plus3it/watchmaker/master/docs/files/bootstrap/watchmaker-bootstrap.ps1"
}

variable "WatchmakerConfig" {
  type        = "string"
  description = "(Optional) URL to a Watchmaker config file"
  default     = ""
}

variable "WatchmakerEnvironment" {
  type        = "string"
  description = "Environment in which the instance is being deployed"
  default     = ""
}

variable "WatchmakerOuPath" {
  type        = "string"
  description = "(Optional) DN of the OU to place the instance when joining a domain. If blank and WatchmakerEnvironment enforces a domain join, the instance will be placed in a default container. Leave blank if not joining a domain, or if WatchmakerEnvironment is false"
  default     = ""
}

variable "WatchmakerComputerName" {
  type        = "string"
  description = "(Optional) Sets the hostname/computername within the OS"
  default     = ""
}

variable "WatchmakerAdminGroups" {
  type        = "string"
  description = "(Optional) Colon-separated list of domain groups that should have admin permissions on the EC2 instance"
  default     = ""
}

variable "WatchmakerAdminUsers" {
  type        = "string"
  description = "(Optional) Colon-separated list of domain users that should have admin permissions on the EC2 instance"
  default     = ""
}

variable "WatchmakerS3Source" {
  type        = "string"
  description = "Flag that tells watchmaker to use its instance role to retrieve watchmaker content from S3"
  default     = "false"
}

variable "CfnEndpointUrl" {
  type        = "string"
  description = "(Optional) URL to the CloudFormation Endpoint. e.g. https://cloudformation.us-east-1.amazonaws.com"
  default     = "https://cloudformation.us-east-1.amazonaws.com"
}

variable "ToggleCfnInitUpdate" {
  type        = "string"
  description = "A/B toggle that forces a change to instance metadata, triggering the cfn-init update sequence"
  default     = "A"
}

resource "aws_cloudformation_stack" "watchmaker-win-instance" {
  name = "${var.Name}"

  parameters {
    AmiId                  = "${var.AmiId}"
    AppScriptParams        = "${var.AppScriptParams}"
    AppScriptShell         = "${var.AppScriptShell}"
    AppScriptUrl           = "${var.AppScriptUrl}"
    AppVolumeDevice        = "${var.AppVolumeDevice}"
    AppVolumeType          = "${var.AppVolumeType}"
    AppVolumeSize          = "${var.AppVolumeSize}"
    KeyPairName            = "${var.KeyPairName}"
    InstanceType           = "${var.InstanceType}"
    InstanceRole           = "${var.InstanceRole}"
    PrivateIp              = "${var.PrivateIp}"
    NoPublicIp             = "${var.NoPublicIp}"
    NoReboot               = "${var.NoReboot}"
    SecurityGroupIds       = "${var.SecurityGroupIds}"
    SubnetId               = "${var.SubnetId}"
    PypiIndexUrl           = "${var.PypiIndexUrl}"
    PythonInstaller        = "${var.PythonInstaller}"
    WatchmakerBootstrapper = "${var.WatchmakerBootstrapper}"
    WatchmakerConfig       = "${var.WatchmakerConfig}"
    WatchmakerEnvironment  = "${var.WatchmakerEnvironment}"
    WatchmakerOuPath       = "${var.WatchmakerOuPath}"
    WatchmakerComputerName = "${var.WatchmakerComputerName}"
    WatchmakerAdminGroups  = "${var.WatchmakerAdminGroups}"
    WatchmakerAdminUsers   = "${var.WatchmakerAdminUsers}"
    WatchmakerS3Source     = "${var.WatchmakerS3Source}"
    CfnEndpointUrl         = "${var.CfnEndpointUrl}"
    ToggleCfnInitUpdate    = "${var.ToggleCfnInitUpdate}"
  }

  #on_failure = "DO_NOTHING" #DO_NOTHING , ROLLBACK, DELETE

  #Assumes that watchmaker-win-instance.template is stored in same directory as watchmaker-win-instance.tf
  template_body = "${file("${path.module}/watchmaker-win-instance.template")}"
}
