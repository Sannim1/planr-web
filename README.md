# README
This project provides a REST API for the generation of optimal release plans based on the EVOLVE model of release plan. To try out the API, a comprehensive documentation is available at `http://docs.planrweb.apiary.io/#`

The project has been developed with and tested against `python:2.7` on a `UNIX-Like` operating system. In order to run the project locally, you'd need to ensure that you have installed this version of `python` on a suitable `*nix` OS distribution.

Upon cloning this repository, the project can be set up by following the setup instructions below.

### Setup Instructions
**All commands should be executed from the terminal after you have navigated to the root directory of the project**
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

### Project Structure
The `app` directory contains the Flask application module with a `release_planner` Blueprint as one of it's submodules.

JSON schema specifications for requests and responses can be found in the `spec/` directory, while unit and functional tests reside in the `tests/` directory.

The project file structure is shown below.
```
├── app
│   ├── __init__.py
│   └── release_planner
│       ├── algorithms
│       │   ├── evolve.py
│       │   ├── __init__.py
│       ├── controllers.py
│       ├── __init__.py
│       ├── planner.py
│       └── validator.py
├── build.sh
├── config.py
├── Dockerfile
├── env
├── main.py
├── nginx.conf.sample
├── README.md
├── requirements.txt
├── run.py
├── run_tests.sh
├── spec
│   ├── release_planning_request_specification.json
│   ├── release_planning_response_specification.json
│   └── samples
│       ├── release_planning_request.json
│       └── release_planning_response.json
└── tests
```
