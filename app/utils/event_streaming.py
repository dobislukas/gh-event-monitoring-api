from typing import List

import asyncio
import requests
import json

import pytz
from datetime import datetime

# I tried implementing class to simulate database interactions but it would 2x the size of code.
EVENT_TO_TIMESTAMPS_DICT = {}
REPO_NAME_TO_ID_DICT = {}
REPO_ID_TO_PR_TIMES_DICT = {}


async def stream_and_process_events(config: dict):
	"""
	Download, filter and process GitHub events.
	Events can be cached for application debuging.

	:param config: dictionary with user set app configuration
	"""

	gh_api_url = config["gh_api_url"]
	monitored_types = config["monitored_event_types"]
	monitoring_frequency = config["monitoring_frequency_in_seconds"]

	caches_events = config["cache_events"]
	cache_filepath = config["cache_filepath"]

	filtered_event_count = 0
	total_event_count = 0

	while True:
		events = download_events_as_json(url=gh_api_url)
		total_event_count += len(events)

		events = filter_events_by_type(events=events, types=monitored_types)
		process_events_for_metrics(events)
		filtered_event_count += len(events)

		if caches_events:
			save_events_to_json(events, cache_filepath)

		print(f"APP: Events \
		 {filtered_event_count}/{total_event_count}\
		 (filtered/downloaded)")
		await asyncio.sleep(monitoring_frequency)


def download_events_as_json(url: str):
	"""
	Make GET request for GitHub events at specified URL.

	:param url: string URL of GitHub API
    :return: list of GitHub events
	"""
	response = requests.get(url)
	events = response.json()
	return events


def filter_events_by_type(events: List[dict], types: List[str]):
	"""
	Filter GitHub events to leave only events of specified types.

	:param events: list of GitHub events
	:param types: list of specified event types
    :return: filtered list of GitHub events
	"""
	filtered_events = [event for event in events if event['type'] in types]
	return filtered_events


def process_events_for_metrics(events: List[dict]):
	"""
	Save event creation timestamp under each monitored type.
	Additionaly for PullRequestEvent group timestamps
	from same repository under its repository ID.

	:param events: list of GitHub events
	"""
	for event in events:
		event_type = event['type']
		created_at = event['created_at']
		timestamp = datetime.strptime(
			created_at, '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=pytz.utc)

		if event_type in EVENT_TO_TIMESTAMPS_DICT.keys():
			EVENT_TO_TIMESTAMPS_DICT[event_type].append(timestamp)
		else:
			EVENT_TO_TIMESTAMPS_DICT[event_type] = [timestamp]

		if event_type == 'PullRequestEvent':
			repo_id = event['repo']['id']
			repo_name = event['repo']['name']
			if repo_id not in REPO_ID_TO_PR_TIMES_DICT.keys():
				REPO_NAME_TO_ID_DICT[repo_name] = repo_id
				REPO_ID_TO_PR_TIMES_DICT[repo_id] = []
			REPO_ID_TO_PR_TIMES_DICT[repo_id].append(timestamp)


def save_events_to_json(events: List[dict], filepath: str):
	"""
	Save content of events into JSON file.

	:param events: list of GitHub events
	:param filepath: location of JSON file
	"""
	with open(filepath, "a") as events_file:
		for event in events:
			events_file.write(json.dumps(event))
			events_file.write("\n")


def read_events_from_json(filepath: str):
	"""
	Read and return events from JSON file.

	:param filepath: location of JSON file
    :return: events saved as content of JSON file.
	"""
	with open(filepath, "r") as events_file:
		events = [json.loads(line.strip()) for line in events_file]
	return events
