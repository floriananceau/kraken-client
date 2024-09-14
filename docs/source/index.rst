===========================================
Kraken API Client in Python - Documentation
===========================================

A lightweight and simple Python client to interact with the `Kraken API <https://www.kraken.com/features/api>`_. This client supports both public and private API calls, handling authentication and one-time passwords (OTP) for secure access to Kraken's trading platform, while returning full `requests.Response` objects for complete flexibility.

Contents
========

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   api

Overview
========

The Kraken API Client allows you to interact with Kraken's public and private API endpoints, including features such as authentication and OTP for secure private API requests.

Installation
============

You can only install this Kraken API client directly from Gitlab using:

.. code-block:: bash

   pip install --index-url https://gitlab.com/api/v4/projects/61674596/packages/pypi/simple/ kraken-client

Usage
=====

Below are some examples of how to use the Kraken API client.

Basic Initialization
---------------------

.. code-block:: python

    from kraken_api import Client

    # Initialize the client with your Kraken API key and secret
    client = Client(api_key="your_api_key", api_secret="your_api_secret")

    # Example public API call to get the server time
    response = client.public('Time')
    print(response.json())

    # Example private API call to get account balance
    response = client.private('Balance')
    print(response.json())

Using One-Time Password (OTP)
-----------------------------

If you have two-factor authentication enabled, you can include the OTP in the client initialization:

.. code-block:: python

    from kraken_api import Client

    # Initialize the client with your API credentials and OTP
    client = Client(api_key="your_api_key", api_secret="your_api_secret", otp="your_otp")

    # Make a private API request
    response = client.private('Balance')
    print(response.json())

Fetching Account Balance
------------------------

.. code-block:: python

    from kraken_api import Client

    client = Client(api_key="your_api_key", api_secret="your_api_secret")
    response = client.private('Balance')

    # Get the JSON response
    balance = response.json()
    print(f"Your balance: {balance['result']}")

Fetching Server Time
--------------------

.. code-block:: python

    from kraken_api import Client

    client = Client()
    response = client.public('Time')

    # Print the server time
    server_time = response.json()
    print(f"Server time: {server_time['result']['unixtime']}")

Contributing
============

We welcome contributions! Please follow the steps below to get started.

Setting Up Your Development Environment
---------------------------------------

This project requires `uv <https://github.com/universalv/uv>`_, a tool for managing virtual environments and dependencies. `uv` ensures that the project's dependencies are installed in a dedicated environment, isolated from your system's global Python setup.

Using the Makefile Commands
---------------------------

The project includes a `Makefile` with several commands to help with development tasks:

Install the package dependencies:

.. code-block:: bash

    make install

Sets up the project environment by syncing dependencies using `uv sync`. This command creates a virtual environment and installs all required packages.

Linting & Formatting:

.. code-block:: bash

    make check

Runs `ruff` to check for code style, syntax, or formatting issues in the `src/` directory.

.. code-block:: bash

    make format

Automatically formats the code in the `src/` directory using `ruff`.

Running Tests:

.. code-block:: bash

    make tests

Executes the test suite using `pytest` to ensure that all tests pass and the code is functioning as expected.

License
=======

This project is licensed under the MIT License. See the `LICENSE <LICENSE.txt>`_ file for more details.
