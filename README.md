# Overview

## Introduction

A stock data storage and statistical calculator application with Flask as the framework, SQLAlchemy as the Database Interface, MySQL as the production environment Database.

For more information on the API you can refer to the Swagger generate OpenAPI documentation:
- Latest API documentation is provided in the `conf/api.swagger.json`
- Online Swagger UI is reachable via [here](http://localhost:5000/api).

## Commands

**Start Application**
```
docker compose -f ./docker-compose.prod.yml build
docker compose -f ./docker-compose.prod.yml up -d
```

The following commands must all be used inside the `backend` container.

**Run Tests**
```
pytest -vs
```

**Fetch Last 2 Weeks Data from AlphaVantageAPI**
```
python get_raw_data.py
```

## Methodologies Used

**Overall**

I used Flask for this project, because the requested project has simple APIs, services, a single model (a single Data Domain), and overall seems like a light weight project.

I created 2 separate environments, DEV and PROD, each can be separately configured with their `docker-compose.yml`, `Dockerfile` and `.env` files.

The [TIME_SERIES_DAILY_ADJUSTED](https://www.alphavantage.co/documentation/#dailyadj) function of AlphaVantage was used to implement the core of the API calling of this project. A client interface was created for communicating with the external API service. This interface class (provided in the `lib/avantage_api.py`) is configurable and easily extendable if other functionalities of the AlphaVantageAPI is needed. 

---

**Performance Optimizers**

The project API endpoints needed to support a peak of 100QPS, so in order to accommodate such high API calls:
- Caching and memoization techniques were used to reduce the computation cost of some procedures in the application.
- Used SQLAlchemy as the interface for communicating with the database; because:
    > SQLAlchemy includes several connection pool implementations... To maintain long running connections in memory for efficient re-use, as well as to provide management for the total number of connections an application might use simultaneously...\
    > ([source](https://docs.sqlalchemy.org/en/20/core/pooling.html))
    
    This could be used to reduce the number of times connections to the database are recreated.

When calling the [TIME_SERIES_DAILY_ADJUSTED](https://www.alphavantage.co/documentation/#dailyadj) endpoint, the optional parameter `outputSize` is set to `compact` to reduce the memory and network load.\
> By default, outputsize=compact. Strings compact and full are accepted with the following specifications: compact returns only the latest 100 data points; full returns the full-length time series of 20+ years of historical data. The "compact" option is recommended if you would like to reduce the data size of each API call.

For the current scope, we only need data for the past 14 days (max of 10 data points per calling); so we don't need any more data than that.

---

**Tests**

I created the relevant test files and test cases for the application in the `tests` directory. The testing strategies implemented were:
- Code Quality Testing: Used flake8 as code linter for testing code quality. Also made sure that the PROD container image will not be built unless the linter validates the quality of the codes.
- Unit Testing: Created the unit tests for separate modules such as the `FinancialData` model.
- Functional Testing: Created test cases for when using each feature (services provided in `financial` directory for example) in the application.
- Integration Testing: Created test cases for calling the `get_raw_data` script, and the API endpoints generated.

---

**Utils**
Python native logger was created and separate files dedicated to the runtime environment were used. Core procedures all are logged to the `data/log/*.log`.

`data` directory contains all the data used by the application:
- `data/fixtures`: Keeps constant files that act as textual variable holders.
- `data/streaming`: Keeps the database files.
- `data/log`: Keeps the application logs.

Fixture loaders were also defined in the `lib/utils.py`, to follow DRY principle.

---

**Docs**

Important modules, classes, and complex functions have been documented with DocStrings and comments.

Also for API Specifications, Swagger OpenAPI Documentation has been used (generated automatically by [Flask-RestX](https://flask-restx.readthedocs.io/)).


### Python Packages Used
- python-dotenv==1.0.0: For loading the `.env` files.
- flask==2.3.2: As the project light weight framework.
- flask-restx==1.1.0: As the project REST framework.
- flask_mysqldb==1.0.1: Driver for interacting with MySQL through Flask.
- Flask-SQLAlchemy==3.0.2: As the project Database Interface.
- flask-cors==3.0.10: CORS Protection.
- Flask-Caching==2.0.2: For caching purposes.
- pytest==7.3.1: For writing and executing test cases.
- faker==18.10.1: For generating random variables for test cases.
- mock==5.0.2: For mocking method calls during tests.
- requests==2.28.2: For sending HTTP requests.
- werkzeug==2.3.4: Flask's default WSGI server.
- webargs==8.2.0: For parsing and validating HTTP request objects, while using flask.
- pandas==1.5.3: For statistical data operations. No version specified.

## Improvement Points

### Within Scope

**High Priority**
- Decorate _all_ responses from the API calls to adhere to the desired response format.\
    At the current state of the application, if there's an input validation error, the Flask-RESTX framework will respond with an automatic format and there's no error message decoration. This could probably be fixed with more tweaking but it was not pursued due to time restrictions.
- Decorate _404 not found_ responses to the endpoints that are not defined, and to the endpoints that raise it due to content not found.
- Migrate from static application creation to Application Creator Factory design. This will supply the application with a flexible configurable feature. More on that [here](https://flask.palletsprojects.com/en/2.3.x/patterns/appfactories/?highlight=factory). This design pattern was not used for the current project because of time restrictions.

**Others**
- Attend to _TODO_ tasks that are marked in comments throughout the project.
- Add test cases for the `lib.utils`, `lib.db` modules.
- Fix the `bulk_upsert` for `lib.db.SQLite` Database class to enable `bulk_upsert` from DEV ENV.

### Out of Scope

The following improvement points were not requested, nor were they relevant to the current scope of design and implementation of the project. They could be added in future revisions/updates to add more flexibility or additional features to the project:

- Add STG ENV.
- Read `api_key` from a CDN instead of a local file. This could be implemented as a sort of a Factory that will detect and load it locally or from a remote CDN, based on the input arguments.
- Add a standardized protocol for APIs, using a tool such as [gRPC](https://grpc.io/).
- Add OAuth2 security to the APIs.
- Add stricter CORS to the APIs.
- Add a production-level server such as [nginx](https://www.nginx.com/) using [gunicorn](https://gunicorn.org/) to the PROD ENV configuration and docker services.
- Add a Dockerfile for PROD MySQL container, and copy a custom configuration/options file to the container at `/etc/my.cnf`
- Add a better Caching service; I suggest [Redis](https://redis.io/).
- If the amount of data is going to be very large, I suggest horizontal sharding of the database. This way the read/write load will be distributed and availability would increase.
- We could use python multi-threading and multi-processing to parallelize the information processing steps.


# Developer Notes
## Total Hours Spent on the Project

- 31/05: 4H (2H Research + 2H Development)
- 01/06: 2H
- 02/06: 6H (2H Research + 4H Development)
- 03/06: 6H
- 04/06: 9H (2H Research + 7H Development)
- Total: 27H (6H Research + 21H Development)

## Final Remarks

This was the first application I have ever developed with Flask framework; basically I started learning this framework, as I started developing this project (I usually develop my projects with Django, but this project was so light-weight and small that Django would've been an overkill). I hope that it is satisfactory according to your standards.

I'm always happy to learn and receiving feedback is an important step in the learning process, so please give me feedback on the project.

Thank you for your time and consideration.