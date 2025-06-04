# CI/CD Pipeline - Simple Flask API

This repository demonstrates a simple Flask RESTful API for managing items, accompanied by unit tests, code quality checks (Pylint), and load testing (Locust), all integrated into a Continuous Integration/Continuous Delivery (CI/CD) pipeline using GitHub Actions.

## Table of Contents

1.  [Features](#features)
2.  [Project Structure](#project-structure)
3.  [Getting Started](#getting-started)
    * [Prerequisites](#prerequisites)
    * [Cloning the Repository](#cloning-the-repository)
    * [Setting up the Virtual Environment](#setting-up-the-virtual-environment)
    * [Installing Dependencies](#installing-dependencies)
    * [Running the Flask Application](#running-the-flask-application)
4.  [Testing](#testing)
    * [Running Unit Tests](#running-unit-tests)
    * [Running Load Tests (Locust)](#running-load-tests-locust)
5.  [Code Quality](#code-quality)
6.  [CI/CD with GitHub Actions](#ci/cd-with-github-actions)
7.  [License](#license)

## Features

This Flask API provides standard CRUD (Create, Read, Update, Delete) operations for a collection of in-memory items:

* **GET /api/items**: Retrieve all items.
* **GET /api/items/&lt;id&gt;**: Retrieve a single item by its ID.
* **POST /api/items**: Add a new item.
* **PUT /api/items/&lt;id&gt;**: Update an existing item by its ID.
* **DELETE /api/items/&lt;id&gt;**: Delete an item by its ID.

## Project Structure

The project is organized as follows:
CI-CD-Pipeline/
├── .github/                  # GitHub Actions workflow configurations
│   └── workflows/
│       └── ci.yml            # CI/CD pipeline definition (see Section 5)
├── app/                      # Contains the main Flask application
│   ├── __init__.py           # IMPORTANT: This must be an empty file!
│   └── main.py               # Your core Flask API application
├── tests/                    # Contains unit tests for the Flask API
│   ├── __init__.py           # IMPORTANT: This must be an empty file!
│   └── test_main.py          # Your unit tests (see Section 3)
├── locustfile.py             # Locust script for load testing the API
├── requirements.txt          # Python dependencies
├── .pylintrc                 # Pylint configuration file (see Section 4)
└── README.md                 # Your project's README (see Section 6)
