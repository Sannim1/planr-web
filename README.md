# README
This project has been developed with and tested against `python:2.7` on a `UNIX-Like` operating system. In order to run the project locally, you'd need to ensure that you have installed this version of `python` on a suitable `*nix` OS distribution.

Upon cloning this repository, the project can be set up by following the steps below.

**All commands should be executed from the terminal after you have navigated to the root directory of the project**

### Steps

1. If you do not already have `pip` installed, install the latest stable version by following the instructions at `https://pip.pypa.io/en/stable/installing/` for your OS distribution.

2. Using `pip`, install the  `virtualenv` package by running the following command
    ```sh
    $ pip install virtualenv
    ```
3. Next, make a new virtual environment within the project's root directory by running the following command
    ```sh
    $ virtualenv env
    ```
4. Activate the virtual environment
    ```sh
    $ source env/bin/activate
    ```
5. Install the `python` dependencies for the project
    ```sh
    $ pip install -r requirements.txt
    ```
6. Now, serve the application by running the following command
    ```sh
    $ python run.py
    ```

At this point your terminal output should look similar to the following
```sh
$ python run.py
* Running on http://0.0.0.0:8080/ (Press CTRL+C to quit)
 * Restarting with stat
 * Debugger is active!
 * Debugger pin code: 139-725-617
 ```

Now, the application should be accessible at `http://0.0.0.0:8080/` and if you visit `http://0.0.0.0:8080/release_plans` from your web browser or HTTP client of choice, then you should get the following response:

```
{
    application: "release_planner_service"
}
```
