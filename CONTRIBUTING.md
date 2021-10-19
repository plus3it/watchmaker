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
[Development](#development-guide) guide.

## Feature Requests and Feedback

The best way to send feedback is to [file an issue][0] on GitHub.

If you are proposing a feature:

*   Explain in detail how it would work.
*   Keep the scope as narrow as possible, to make it easier to implement.
*   Remember that this is a community-driven, open-source project, and that
    code contributions are welcome. :)

## Development Guide

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

5.  When you're done making changes, use [tox][2] to run the linter, the tests,
    and the doc builder:

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

6.  In addition to building the package and running the tests, `tox` will build
    any docs associated with the change. They will be located in the
    `dist/docs` directory. Navigate to the folder, open index.html in your
    browser, and verify that the doc text and formatting are as you intended.

    If you _only_ want to build the docs, run:

    ```shell
    tox -e docs
    ```

7.  Commit your changes and push your branch to GitHub:

    ```shell
    git add .
    git commit -m "Your detailed description of your changes."
    git push origin name-of-your-bugfix-or-feature
    ```

8.  Submit a pull request through the GitHub website.

## Pull Request Guidelines

If you need some code review or feedback while you are developing the code just
open the pull request.

For pull request acceptance, you should:

1.  Include passing tests (Ensure `tox` is successful).
2.  Update documentation whenever making changes to the API or functionality.
3.  Add a note to `CHANGELOG.md` about the changes. Include a link to the
    pull request.

## Tox Tips

1.  The _primary_ tox environments for `watchmaker` include:

    *   `check`
    *   `docs`
    *   `py26`
    *   `py27`
    *   `py35`
    *   `py36`

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

## Build a Development Branch in EC2

To install and run a development branch of watchmaker on a new EC2 instance,
specify something like this for EC2 userdata:

*   **For Linux**: Modify `GIT_REPO` and `GIT_BRANCH` to reflect working
    values for your development build. Modify `PIP_URL` and `PYPI_URL` as
    needed.

    ```shell
    #!/bin/sh
    GIT_REPO=https://github.com/<your-github-username>/watchmaker.git
    GIT_BRANCH=<your-branch>

    PYPI_URL=https://pypi.org/simple

    # Install pip
    python3 -m ensurepip

    # Install git
    yum -y install git

    # Upgrade pip and setuptools
    python3 -m pip install --index-url="$PYPI_URL" --upgrade pip setuptools

    # Clone watchmaker
    git clone "$GIT_REPO" --branch "$GIT_BRANCH" --recursive

    # Install watchmaker
    cd watchmaker
    python3 -m pip install --index-url "$PYPI_URL" --editable .

    # Run watchmaker
    watchmaker --log-level debug --log-dir=/var/log/watchmaker
    ```

*   **For Windows**: Modify `GitRepo` and `GitBranch` to reflect working
    values for your development build. Optionally modify `BootstrapUrl`,
    `PythonUrl`, `GitUrl`, and `PypiUrl` as needed.

    ```shell
    <powershell>
    $GitRepo = "https://github.com/<your-github-username>/watchmaker.git"
    $GitBranch = "<your-branch>"

    $BootstrapUrl = "https://watchmaker.cloudarmor.io/repo/releases/latest/watchmaker-bootstrap.ps1"
    $PythonUrl = "https://www.python.org/ftp/python/3.8.10/python-3.8.10-amd64.exe"
    $GitUrl = "https://github.com/git-for-windows/git/releases/download/v2.33.1.windows.1/Git-2.33.1-64-bit.exe"
    $PypiUrl = "https://pypi.org/simple"

    # Download bootstrap file
    $BootstrapFile = "${Env:Temp}\$(${BootstrapUrl}.split("/")[-1])"
    (New-Object System.Net.WebClient).DownloadFile($BootstrapUrl, $BootstrapFile)

    # Install python and git
    & "$BootstrapFile" `
        -PythonUrl "$PythonUrl" `
        -GitUrl "$GitUrl" `
        -Verbose -ErrorAction Stop

    # Upgrade pip and setuptools
    python -m pip install --index-url="$PypiUrl" --upgrade pip setuptools

    # Clone watchmaker
    git clone "$GitRepo" --branch "$GitBranch" --recursive

    # Install watchmaker
    cd watchmaker
    pip install --index-url "$PypiUrl" --editable .

    # Run watchmaker
    watchmaker --log-level debug --log-dir=C:\Watchmaker\Logs
    </powershell>
    ```

[0]: https://github.com/plus3it/watchmaker/issues
[1]: https://travis-ci.org/plus3it/watchmaker/pull_requests
[2]: https://tox.readthedocs.io/en/latest/install.html
[3]: https://github.com/plus3it/watchmaker/tree/main/docs
