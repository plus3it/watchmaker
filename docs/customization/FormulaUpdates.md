```{eval-rst}
.. image:: ../images/cropped-plus3it-logo-cmyk.png
   :width: 140px
   :alt: Powered by Plus3 IT Systems
   :align: right
   :target: https://www.plus3it.com
```
<br>

# Testing Updates to Existing Formulas

The formulae-contents that are installed and configured for use by Watchmaker can be modified through a custom `config.yaml` file. This is done through the `config.yaml` file's `user_formula` dictionary-parameter (see: the [discussion](ConfigYaml.md) of the `config.yaml` file's `user_formulas` parameter and _take special note of guidance around file-formatting and indenting_). This parameter may be used to enable the setup of "in progress" updates to existing formulae. This is done by specifying dictionary-values for `user_formulas` in a custom `config.yaml` file:

```
all:
  salt:
    [...elided...]
    user_formulas:
      <TEST_FORMULA_1>: <TEST_FORMULA_ARCHIVE_1_URI>
      <TEST_FORMULA_2>: <TEST_FORMULA_ARCHIVE_2_URI>
      [...elided...]
      <TEST_FORMULA_N>: <TEST_FORMULA_ARCHIVE_N_URI>
```

```{eval-rst}
.. note::
    While multiple formulae are shown in the above snippet, it's not generally
    recommended to use this method for more than one, formula at a time. The
    above is primarily to illustrate that the ``user_formulas`` parameter is a
    dictionary.
```

Once the custom `config.yaml` file is in the desired state, it can be uploaded to an S3-based testing-bucket, web server[^1] or even staged locally within the testing-system.

## About Testing Updates

To the greatest extent possible, formulae should be _portable_. It is recommended that when testing updates, the developer:

- Tests with a bog-standard configuration (the custom `config.yaml` file's `salt_content` parameter's value is set to `null`)
- Tests with the target-environment's or target-environments' custom `salt-content.zip` file(s)
- Tests with a customized version of the bog-standard `salt-config.zip` file if to-be-tested formula's config-inputs have been changed
- Tests with a `salt-config.zip` file cloned from the target-environment's or target-environments' custom `salt-config.zip` file if to-be-tested formula's config-inputs have been changed

Exercising across environments, in this way, will better assure that proposed updates do not break an existing formula's portability.

## About Hosting of Modified Formula-Content

The modified formulae's contents _can_ be installed from any Watchmaker-supported source-type &ndash; S3-hosted, web server hosted or local files. However, it is expected that most personnel attempting to test modifications to existing formulae will want to load that modified content _directly_ from their development content-management system (CMS). To have watchmaker load content _directly_ from the source CMS:

1. Visit the CMS (GitHub.Com when devloping for the main Watchmaker project)
2. Navigate to the content-developer's source fork/branch
3. Find the `https://` URL of fork/branch's ZIP-archive of the code to be tested.
4. Use the value from the prior step as the value for `<TEST_FORMULA_ARCHIVE_URI>`

Modification of existing/already-integrated formulae's content typically takes place on GitHub.Com. As of this document's authoring date, the above process looks like:

1. Browse to `https://www.github.com/plus3it/<FORMULA_NAME>`
2. Click on the down-arrow on the `Fork` button to bring up the `Existing Forks` list
3. Click on the developer's fork
4. On the landing-page for the developer's fork, click on the branch button's down-arrow[^2]. This opens the `Switch branches/tags` dropdown
5. Select the desired branch from the `Switch branches/tags` dropdown
6. Click on the `Code` button's down-arrow. Right-click on the `Download ZIP` text in the drop-down that the down-arrow opens. This opens a context-menu of link-actions.
7. Click on the `Copy Link Address` menu-option (if using a browser other than Chrome, the specific menu-option may be different, but the equivalent action should be obvious) to copy the branch-archive's URL into your system's copy-buffer.
8. Paste the branch-archive's URL (from your system's copy-buffer) as the `<TEST_FORMULA_ARCHIVE_URI>` value in your custom `config.yaml` file

```{eval-rst}
.. warning::
    If you created your modification-branch in a private fork, it will be 
    necessary to create an API-token that grants your test-host the ability to 
    access the archive-URL. Creating such tokens is outside the scope of this 
    document.
```

## Execution With Standard Configuration-Options

Assuming that the executing system has access to the specified URI(s), watchmaker will:

1. Download the requested formula ZIP-archive(s)
2. Unarchive them to the `.../formulas` directory &ndash; replacing the standard contents with the testing-contents 

As an already-integrated formula, it should already be executed when a full/generic Watchmaker-run is requested.

While the modified formula should execute in place of the already-integrated formula contents as part of a full/generic Watchmaker-run, it will save testing-time to execute _only_ the modified formula. This can be done by explicitly selecting _only_ the modified-formula for execution using a method similar to:

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
The modified formula's execution will be logged into the directory requested via the manual invocation.

## Execution With Modified/New Configuration-Options

Because Watchmaker will overwrite existing formula-content with the referenced formula-content, it should only be necessary to execute the updated formula with a custom  `salt-content.zip` if:

- One wishes to test with specific testing-values for existing formula-parameters
- The formula-updates add new parameters
- The formula-updates rename existing parameters
- The formula-updates change existing parameters' data-types. 

If executing to cover one of the above scenarios, it will be necessary to either manually update the `.../pillar` directory's contents with the appropiate data (see: [_The `pillar` Directory-Tree_](SaltContent.md#the-pillar-directory-tree)) or create a custom `salt-config.zip` file and reference it from the custom `config.yaml` file.

## Final Notes

If modification of an existing formula adds or removes parameters, renames existing parameters or changes existing parameters' data-types, it is *critical* that the formula-project's `pillar.example` or `pillar.example.yaml` file be updated to reflect these changes.

[^1]: If hosting on a web server and configuration content may be deemed sensitive, apply suitable access controls to the file and specify the fetch-URL with the appropriate authentication-elements.
[^2]: This button will typically start out labeled either `master` or `main` (depending how old the formula's project is)

