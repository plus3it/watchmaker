{#- Set the name of the winrepo package. -#}
{%- set name = 'netbanner' -%}

{#-
Define variables that may be unique to the system and are required for one of
the winrepo parameters.
-#}

{#-
Define a dictionary of versions with variables that are distinct for each
version.
-#}
{%- load_yaml as versions %}
2.1.161:
  filename: 'NetBanner.Setup+2.1.161.msi'
  full_name: 'Microsoft NetBanner'
1.3.93:
  filename: 'netbanner.msi'
  full_name: 'NetBanner'
{% endload %}

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
  reboot: False
  install_flags: ' ALLUSERS=1 /quiet /qn /norestart'
  msiexec: True
  uninstall_flags: ' /qn'
{# `versions` are winrepo params that are distinct per version. #}
versions:
  {% for version,params in versions.items() %}
  '{{ version }}':
    installer: >-
      https://path/to/your/netbanner/{{ version }}/{{ params.filename }}
    full_name: {{ params.full_name }}
    uninstaller: >-
      https://path/to/your/netbanner/{{ version }}/{{ params.filename }}
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
