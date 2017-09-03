import tweepy

def ReadConfig(filename):
    """Read a config file and return a dictionary of its settings.

    Config files are plain text of format `[KEY] = [VALUE][ENDLINE]`.
    OutageBuddy is specifically expecting the following key-value pairs:

    ```
    CONSUMER_KEY = [oAuth consumer key]
    CONSUMER_SECRET = [oAuth consumer secret]
    ACCESS_KEY = [oAuth access key]
    ACCESS_SECRET = [oAuth access secret]
    OWNERS_SPREADSHEET = [URL for Google Spreadsheet of who owns what accounts]
    ```

    The dictionary you receive back from this function will contain these five
    keys, and any other keys found in the file.  If any of the above are missing
    or if any line of the config file isn't formatted correctly, it'll raise a
    ValueError.
    """
    with open(filename, 'r') as infile:
        split_lines = [line.strip().split(" = ") for line in infile]
    if not all([len(line) == 2) for line in split_lines]):
        raise ValueError("Config has an invalid line")
    config = {pair[0]: pair[1] for pair in split_lines}
    expected_keys = ['CONSUMER_KEY', 'CONSUMER_SECRET', 'ACCESS_KEY',
                     'ACCESS_SECRET', 'OWNERS_SPREADSHEET']
    if not all([ex_key in config for ex_key in expected_keys]):
        raise ValueError("Config missing an expected key")
    return config