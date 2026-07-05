# Install
```
python -m venv .venv
source .venv/bin/activate 
```

# Sync
```
./ao3_history.py sync --username <ao3 username> --base-url https://archiveofourown.org
```
Note: requests are throttled to no more than one per second

# Search
```
./ao3_history.py search "some query text"
./ao3_history.py search --tag "some tag"
./ao3_history.py search "some query text" --tag "and some tag"
./ao3_history.py search "some query text" --tag "and some tag" --tag "and this tag too"
```
`query` => searches title and author, returns if either hits a match
`tag(s)` => searches tags, all specified tags must match
`query AND tag(s)` => searches title and author, either msut match. then all tags must match
