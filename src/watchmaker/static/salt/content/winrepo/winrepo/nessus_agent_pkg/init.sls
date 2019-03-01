{#- Set the name of the winrepo package. -#}
{%- set name = 'nessus-agent' -%}

{#-
Define variables that may be unique to the system and are required for one of
the winrepo parameters.
-#}

{#- Define a list of versions. -#}
{%- set versions = [ '6.11.1' ] -%}

{#-
Initialize the `package` dictionary, which will contain the information needed
for the winrepo package definition. This dictionary is structured so that the
jinja content can be separated into another file, and this single variable can
be imported into an accompanying winrepo sls file.
-#}
{%- load_yaml as package -%}
name: {{ name }}
pillar: '{{ name }}:winrepo'
{# `common_params` are winrepo params that are the same for all versions. #}
common_params:
  full_name: 'Nessus Agent (x64)'
  install_flags: ' /quiet /norestart /log "C:\Watchmaker\Logs\nessus_agent_install.log" NESSUS_KEY=<nessus_server_key> NESSUS_SERVER="<nessus_server_name:nessus_server_port>" NESSUS_GROUPS="<nessus_group_name>"'
  msiexec: True
  uninstall_flags: ' /quiet /qn /uninstall'
{# `versions` are winrepo params that are distinct per version. #}
versions:
  {% for version in versions %}
  '{{ version }}':
    installer: >-
      https://path/to/your/NessusAgent.msi
    uninstaller: >-
      https://path/to/your/NessusAgent.msi
  {% endfor %}
{%- endload -%}

{#-
Update and merge the `package.versions` dictionary with winrepo version
settings from pillar.
-#}
{%-
do package.versions.update(salt['pillar.get'](
    package.pillar ~ ':versions',
    default=package.versions,
    merge=True))
-%}

{#-
Create the winrepo state definition, looping over the versions and merging in
the `package.common_params` dictionary.
-#}
{{ package.name }}:
  {%- for version,params in package.versions.items() %}
  {%- do params.update(salt['pillar.get'](
      package.pillar ~ ':common_params',
      default=package.common_params,
      merge=True)) %}
  '{{ version }}':
    {{ params }}
  {%- endfor %}
