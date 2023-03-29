In order to test documentation updates prior to submitting a PR, it is recommended that you perform a local rendering of the documentation. Once rendered, view the newly-created HTML files to ensure proper presence, location and formatting of new documentation-content.

To perform a local rendering, it is recommended that the contributor execute, from the project's root-directory:

1. `sphinx-build -a -E -W --keep-going -b html docs <DESTINATION_FOR_RENDERED_DOCUMENTS>`
1. `sphinx-build -b doctest docs <DESTINATION_FOR_RENDERED_DOCUMENTS>`
1. `sphinx-build -b linkcheck docs <DESTINATION_FOR_RENDERED_DOCUMENTS>`

The above is what the [TOX modules execute](/tox.ini#L31-L33) to create the production docmentation (as hosted at watchmaker's <a href="https://watchmaker.readthedocs.io" target="_blank">Read the Docs</a> site).

In order to successfully run the above, it will be necessary to have installed the following pip modules into your testing/documentation-environment:

- sphinx
- sphinx_rtd_theme
- myst_parser
- oschmod
- backoff
- compatibleversion

Once the `sphinx-build` commands have executed, the rendered documentation will appear as `.html` files in the `<DESTINATION_FOR_RENDERED_DOCUMENTS>` directory.
