from src.logfile_etl.feature_extractor.abstract_feature_extractor import \
    AbstractFeatureExtractor
from src.logfile_etl.parallel_commands_tracker import ParallelCommandsTracker


class ArriveTimeExtractor(AbstractFeatureExtractor):
    intervals_per_hour = 4
    minutes_per_interval = 60 / intervals_per_hour

    def get_feature_name(self) -> str:
        return "arrive time"

    def extract_feature(
            self, parallel_commands_tracker: ParallelCommandsTracker, tid: str
    ):
        received_at = parallel_commands_tracker[tid]["receivedAt"].strftime(
            "%H:%M:%S.%f"
        )
        return int(received_at.hour) * self.intervals_per_hour + int(received_at.minute) // self.minutes_per_interval
