```{eval-rst}
.. image:: ../images/cropped-plus3it-logo-cmyk.png
   :width: 140px
   :alt: Powered by Plus3 IT Systems
   :align: right
   :target: https://www.plus3it.com
```
<br>

# Testing New Formulas

The formulae-contents that are installed and configured for use by Watchmaker can be modified through a custom `config.yaml` file. This is done through the `config.yaml` file's `user_formula` dictionary-parameter (see: the [discussion](ConfigYaml.md) of the `config.yaml` file's `user_formulas` parameter and _take special note of guidance around file-formatting and indenting_). This parameter may be used to enable the setup of new, yet-to-be integrated formulae[^1]. This is done by specifying dictionary-values for `user_formulas` in a custom `config.yaml` file:

```
all:
  salt:
    [...elided...]
    user_formulas:
      <NEW_FORMULA_1>: <NEW_FORMULA_ARCHIVE_1_URI>
      <NEW_FORMULA_2>: <NEW_FORMULA_ARCHIVE_2_URI>
      [...elided...]
      <NEW_FORMULA_N>: <NEW_FORMULA_ARCHIVE_N_URI>
```

```{eval-rst}
.. note::
    While multiple new formulae are shown in the above snippet, it's not
    generally recommended to use this method for more than one, new formula at
    a time. The above is primarily to illustrate that the `user_formulas`
    parameter is a dictionary
```

Once the custom `config.yaml` file is in the desired state, it can be uploaded to an S3-based testing-bucket, web server[^2] or even staged locally within the testing-system.

## About Testing New Formulae

To the greatest extent possible, formulae should be portable. It is recommended that when testing updates, the developer:

* Tests without use of a custom `salt-content.zip`
* Tests using custom Pillar-data &ndash; either by hand-modifying Pillar content or using a modified `salt-content.zip` cloned from the target deployment-environments' `salt-content.zip` &ndash; for one or more targeted deployment-environments

Exercising across environments, in this way, will better assure that newly-created formulae operate as portably as expected prior to the newly-created formulae's integration into standard or site-specific Watchmaker executions.


## Execution - Generic/Defaults

Assuming that the executing system has access to the specified URIs, watchmaker will:

1. Download the requested formula ZIP-archive(s)
2. Unarchive them to the `.../formulas` directory
3. Update the `.../minion` file's `file_roots:base` list

If the site's `salt-content.zip` has not been modified to cause execution, the new formula can be explicitly executed using a method similar to:

- Linux invocation:
    ```shell
    watchmaker \
      -c s3://<TESTING_BUCKET>/config.yaml \
      -s <FORMULA_NAME> \
      --log-level debug --log-dir=/var/log/watchmaker
    ```
- Windows invocation:
    ```shell
    watchmaker --log-level debug --log-dir=C:\Watchmaker\Logs -c s3://<TESTING_BUCKET>/config.yaml -s <FORMULA_NAME>

    ```
The new formula's execution will be logged into the directory requested via the manual invocation.

## Execution - Tailored

If the new formula has variable configuration-data that needs to come from pillar, it will be necessary to either manually update the `.../pillar` directory's contents with the appropiate data (see: [_The `pillar` Directory-Tree_](SaltContent.md#the-pillar-directory-tree)) or create a custom `salt-config.zip` file and reference it from the custom `config.yaml` file.

## Final Notes

All formulae that have Pillar-settable or Pillar-overridable parameters should include a `pillar.example` or `pillar.example.yaml` file with the project's content. This file should be placed in the project's root-directory. The file should be valid YAML with explanatory comments for each configuration item. If a new formula's execution-customizability is more complex than is easily accommodated by comment-entries in the example Pillar YAML file, add a `README_PillarContents.md` file to the project. This file should contain sufficiently-expository content to allow new users of the formula to fully understand how to tailor the formulae's execution to their site's needs.

[^1]: "Yet-to-be-integrated" formulae are any formulas that have not yet been set up for automated execution as part of a _full_ Watchmaker run. See the [_Modifying Formulae Execution-Parameters_](SiteParameters.md) document for tips.
[^2]: If hosting on a web server and configuration content may be deemed sensitive, apply suitable access controls to the file and specify the fetch-URL with the appropriate authentication-elements.
