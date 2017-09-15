import sys
import tweepy

from datetime import datetime


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
    with open(filename, "r") as infile:
        split_lines = [line.strip().split(" = ") for line in infile]
    if not all([len(line) == 2 for line in split_lines]):
        raise ValueError("Config has an invalid line")
    config = {pair[0]: pair[1] for pair in split_lines}
    expected_keys = ["CONSUMER_KEY", "CONSUMER_SECRET", "ACCESS_KEY",
                     "ACCESS_SECRET", "OWNERS_SPREADSHEET"]
    if not all([ex_key in config for ex_key in expected_keys]):
        raise ValueError("Config missing an expected key")
    return config


def CreateAPI(config):
    ckey = config["CONSUMER_KEY"]
    csec = config["CONSUMER_SECRET"]
    akey = config["ACCESS_KEY"]
    asec = config["ACCESS_SECRET"]

    auth = tweepy.OAuthHandler(ckey, csec)
    auth.set_access_token(akey, asec)
    return tweepy.API(auth)


class Account(object):
    """Details of an account that needs monitoring."""

    def __init__(self, name, owner, hours_per_update):
        self._name = name
        self._owner = owner
        self._rate = float(hours_per_update)

    @classmethod
    def FromCSVLine(line):
        spline = line.split(",")
        if len(spline) != 3:
            raise ValueError("Can't parse line: '%s'" % (line,))
        return cls(spline[0], spline[1], spline[2])

    def Check(self, api, now=None):
        """Is the latest tweet timestamp *less* than self._rate hours ago?"""
        if now == None:
            now = datetime.now()
        created_times = [status.created_at for status
                         in api.user_timeline(screen_name=self._name, count=1)]
        most_recent_time = created_times[0]
        delta = now - most_recent_time
        delta_hours = float(delta.total_seconds())/3600
        return delta_hours < self._rate


class OutageBuddy(object):

    def __init__(self, config):
        self._api = CreateAPI(config)
        sheet_url = ("https://spreadsheets.google.com/feeds/download/"
                     "spreadsheets/Export?key=%s&exportFormat=csv" % (
                        config["OWNERS_SPREADSHEET"],))
        with urllib2.urlopen(urllib2.Request(sheet_url)) as infile:
            self._accounts = [Account.FromCSVLine(line) for line in infile
                              if line[0] != "#"]
        self._followers = [] # TODO: Get followers


if __name__ == "__main__":
    config = ReadConfig(sys.argv[1])
    api = CreateAPI(config)
    bgawalt = Account(name="bgawalt", owner="bgawalt",
                      hours_per_update=float(sys.argv[2]))
    print bgawalt.Check(api)
