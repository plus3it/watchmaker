# Contributing

Contributions are welcome, and they are greatly appreciated! Every little bit
helps, and credit will always be given.

## Bug Reports

When [reporting a bug][0] please include:

*   Your operating system name and version.
*   Any details about your local setup that might be helpful in
    troubleshooting.
*   Detailed steps to reproduce the bug.

## Documentation Improvements

Watchmaker could always use more documentation, whether as part of the official
Watchmaker docs, in docstrings, or even on the web in blog posts, articles, and
such. The official documentation is maintained within this project in
docstrings or in the [docs][3] directory. Contributions are
welcome, and are made the same way as any other code. See
[Development](#development).

## Feature Requests and Feedback

The best way to send feedback is to [file an issue][0] on GitHub.

If you are proposing a feature:

*   Explain in detail how it would work.
*   Keep the scope as narrow as possible, to make it easier to implement.
*   Remember that this is a volunteer-driven project, and that code
    contributions are welcome :)

## Development

To set up `watchmaker` for local development:

1.  Fork [watchmaker](https://github.com/plus3it/watchmaker) (look for the
    "Fork" button).

2.  Clone your fork locally and update the submodules:

    ```shell
    git clone https://github.com/your_name_here/watchmaker.git && cd watchmaker
    git submodule update --init --recursive
    ```

3.  Create a branch for local development:

    ```shell
    git checkout -b name-of-your-bugfix-or-feature
    ```

4.  Now you can make your changes locally.

5.  When you're done making changes, run the linter, the tests, the doc
    builder, and a spell checker using [tox][2]:

    ```shell
    tox
    ```

    > **NOTE**: This will test the package in all versions of Python listed in
    > `tox.ini`. If `tox` cannot find the interpreter for the version, the test
    > will fail with an `InterpreterNotFound` error. This is ok, as long as at
    > least one interpreter runs and the tests pass. You can also specify which
    > [tox environments](#tips) to execute, which can be used to restrict the
    > Python version required.
    >
    > You can also rely on Travis and Appveyor to [run the tests][1] after
    > opening the pull request. They will be slower though...

6.  Commit your changes and push your branch to GitHub:

    ```shell
    git add .
    git commit -m "Your detailed description of your changes."
    git push origin name-of-your-bugfix-or-feature
    ```

7.  Submit a pull request through the GitHub website.

## Pull Request Guidelines

If you need some code review or feedback while you are developing the code just
open the pull request.

For pull request acceptance, you should:

1.  Include passing tests (Ensure ``tox`` is successful).
2.  Update documentation whenever making changes to the API or functionality.
3.  Add a note to ``CHANGELOG.md`` about the changes. Include a link to the
    pull request.

## Tips

1.  The primary tox environments for `watchmaker` include:

    *   `check`
    *   `docs`
    *   `py26`
    *   `py27`
    *   `py33`
    *   `py34`
    *   `py35`

2.  To run a subset of environments:

    ```shell
    tox -e <env1>,<env2>,<env3>,etc
    ```

3.  To run a subset of tests:

    ```shell
    tox -e <environment> -- py.test -k <test_myfeature>
    ```

4.  To run all the test environments in _parallel_, use `detox`:

    ```shell
    pip install detox
    detox
    ```

[0]: https://github.com/plus3it/watchmaker/issues
[1]: https://travis-ci.org/plus3it/watchmaker/pull_requests
[2]: https://tox.readthedocs.io/en/latest/install.html
[3]: https://github.com/plus3it/watchmaker/tree/develop/docs
