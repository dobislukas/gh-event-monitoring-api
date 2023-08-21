import pytz
from datetime import datetime, timedelta
from utils.event_streaming import EVENT_TO_TIMESTAMPS_DICT, \
								  REPO_NAME_TO_ID_DICT, \
								  REPO_ID_TO_PR_TIMES_DICT


def calculate_average_time_between_pull_requests(repo_input: str):
	"""
	Compute and return average time between pull request
	for	GitHub repository specified by its name or ID.
	Time is returnd in seconds.

	:param repo_input: name or ID of GitHub repository
	:return: average time between repository pull requests
	"""

	# Get repository ID if repository was submitted in name
	repo_id = REPO_NAME_TO_ID_DICT[repo_input] \
		if "/" in repo_input else int(repo_input)

	# Calculate average if there are at least two pull requests
	if repo_id in REPO_ID_TO_PR_TIMES_DICT.keys() and \
		len(REPO_ID_TO_PR_TIMES_DICT[repo_id]) > 1:

		pr_times = REPO_ID_TO_PR_TIMES_DICT[repo_id]
		avg_time = sum(
			(pr_times[i] - pr_times[i - 1]).total_seconds()
	   		for i in range(1, len(pr_times))
	   		) / (len(pr_times) - 1)

		return avg_time
	return None


def calculate_event_counts_within_offset(event_type: str, offset: int):
	"""
	Compute and return count for specified type of
	GitHub events within time offset specified in seconds.

	:param event_type: type of monitored event
	:return: count of events of specified type
	"""
	if event_type in EVENT_TO_TIMESTAMPS_DICT.keys():

		curr_time = datetime.now().astimezone(pytz.utc)
		curr_time_with_offset = curr_time - timedelta(minutes=offset)

		event_count = sum(
			list(map(
				lambda t: t >= curr_time_with_offset,
				EVENT_TO_TIMESTAMPS_DICT[event_type])))

		return event_count
	return 0
