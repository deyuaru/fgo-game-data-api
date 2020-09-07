<!-- omit in toc -->
# FGO game data API

HTTP API for FGO game data. Transform the raw game data into something a bit more managable.

- [Environment variables](#environment-variables)
- [Run the API server](#run-the-api-server)
- [Linting](#linting)
- [Formatting](#formatting)
- [Dependencies](#dependencies)
- [Testing](#testing)
- [Helper scripts](#helper-scripts)
  - [`extract_enums.py`: `dump.cs` enums exporter](#extract_enumspy-dumpcs-enums-exporter)

### Environment variables

List of environment variables for the main app. All are required except noted:
- `NA_GAMEDATA`: Required, path to NA gamedata's master folder
- `JP_GAMEDATA`: Required, path to JP gamedata's master folder
- `ASSET_URL`: Required, base URL for the game assets
- `EXPORT_ALL_NICE`: Optional, default to `False`. If set to `True`, at start the app will generate nice data of all servant and CE and serve them at the `/export` endpoint. It's recommended to serve the files in the `/export` folder using nginx or equivalent webserver to lighten the load on the API server.
- `DOCUMENTATION_ALL_NICE`: Optional, default to `False`. If set to `True`, there will be links to the exported all nice files in the documentation.
- `LRU_CACHE_SIZE`: Optional, default to `128`. Cache size of the nice lru cache.
- `GITHUB_WEBHOOK_SECRET`: Optional, default to `""`. If set, will add a webhook location at `/GITHUB_WEBHOOK_SECRET/update` that will pull and update the game data. If it's not set, the endpoint is not created.
- `GITHUB_WEBHOOK_GIT_PULL`: Optional, default to `False`. If set, the app will do `git pull` on the gamedata repos when the webhook above is used.
- `GITHUB_WEBHOOK_SLEEP`: Optional, default to `0`. If set, will delay the action above by `GITHUB_WEBHOOK_SLEEP` seconds.

You can also make a .env file at the project root with the following entries instead of setting the environment variables:
```
NA_GAMEDATA="/path/to/gamedata/master/NA"
JP_GAMEDATA="/path/to/gamedata/master/JP"
ASSET_URL="https://example.com/assets/"
EXPORT_ALL_NICE=False
DOCUMENTATION_ALL_NICE=True
LRU_CACHE_SIZE=128
GITHUB_WEBHOOK_SECRET="e81c7b97-9a57-4424-a887-149b4b5adf57"
GITHUB_WEBHOOK_GIT_PULL=True
GITHUB_WEBHOOK_SLEEP=0
```

List of optional enviroment variables for the Docker image can be found [here](https://github.com/tiangolo/uvicorn-gunicorn-docker#environment-variables).

### Run the API server

Run at the project root to start the API server:
```
uvicorn app.main:app --reload --log-level debug --reload-dir app
```

Go to http://127.0.0.1:8000/docs or http://127.0.0.1:8000/redoc for the API documentation.


### Linting

[pylint](https://docs.pylint.org/en/latest/index.html) and [mypy](https://mypy.readthedocs.io/en/stable/) are used to lint the code. pylint's configuration is in [pyproject.toml](pyproject.toml#L37) and mypy's configuration is in [mypy.ini](mypy.ini).

### Formatting

[isort](https://pycqa.github.io/isort/) and [black](https://black.readthedocs.io/en/stable/) are used to format the code. isort's configuration is in [pyproject.toml](pyproject.toml#L37) and black uses default settings.

```
isort app tests export scripts; black app tests export scripts
```

[prettier](https://prettier.io/docs/en/) is used to format the json files.

```
prettier --write tests/*/*.json
prettier --write export/*/Nice*.json
prettier --write export/*/*UserLevel.json --print-width 50
```

### Dependencies

Use [poetry](https://python-poetry.org/docs/) to manage the dependencies. Run `poetry export` after adding a production dependency.

```
poetry export -f requirements.txt -o requirements.txt --without-hashes
```

### Testing

Run pytest at project root to run the tests or use `coverage` to get coverage statistics.

```
coverage run --source=app/ -m pytest; coverage html
```

### Helper scripts

#### [`extract_enums.py`](scripts/extract_enums.py): `dump.cs` enums exporter

Take the `dump.cs` generated by [Il2CppDumper](https://github.com/Perfare/Il2CppDumper) and write the [`gameenums.py`](app/data/gameenums.py) file.

```
python ./scripts/extract_enums.py path_to_dump.cs ./app/data/gameenums.py
```