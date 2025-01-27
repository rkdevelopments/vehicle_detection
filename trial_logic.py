import datetime
import os
import hashlib

class TrialManager:
    def __init__(self, trial_period_days=2):
        self.trial_period_days = trial_period_days
        self.trial_file = "trial_info.dat"

    def _hash_date(self, date):
        """Generate a hash for the given date."""
        return hashlib.sha256(date.encode()).hexdigest()

    def _get_today_hashed(self):
        """Return today's date as a hashed string."""
        today = datetime.date.today().isoformat()
        return self._hash_date(today)

    def _write_trial_start_date(self):
        """Write the trial start date to the file."""
        today_hashed = self._get_today_hashed()
        with open(self.trial_file, "w") as f:
            f.write(today_hashed)

    def _read_trial_start_date(self):
        """Read the trial start date from the file."""
        try:
            with open(self.trial_file, "r") as f:
                return f.read().strip()
        except FileNotFoundError:
            return None

    def is_trial_valid(self):
        """Check if the trial period is still valid."""
        start_date_hashed = self._read_trial_start_date()

        if not start_date_hashed:
            # Start trial for the first time
            self._write_trial_start_date()
            return True

        # Check if the trial period has expired
        today = datetime.date.today()
        for days in range(self.trial_period_days + 1):
            valid_date = today - datetime.timedelta(days=days)
            if self._hash_date(valid_date.isoformat()) == start_date_hashed:
                return True

        return False

    def days_remaining(self):
        """Get the number of days remaining in the trial period."""
        start_date_hashed = self._read_trial_start_date()

        if not start_date_hashed:
            return self.trial_period_days

        today = datetime.date.today()
        for days in range(self.trial_period_days + 1):
            valid_date = today - datetime.timedelta(days=days)
            if self._hash_date(valid_date.isoformat()) == start_date_hashed:
                return self.trial_period_days - days

        return 0
