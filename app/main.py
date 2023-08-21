#!usr/bin/python3

import asyncio
import yaml

from fastapi import FastAPI, Path, Response

from utils.event_streaming import stream_and_process_events, \
								  read_events_from_json
from utils.metrics import calculate_average_time_between_pull_requests, \
					      calculate_event_counts_within_offset
from utils.visualization import visualize_event_counts


# Read application configuration
with open("cfg/configuration.yaml", "r") as config_file:
    CONFIG = yaml.safe_load(config_file)
	
# Initialize app
app = FastAPI()


@app.get("/")
async def index():
    """
    Endpoint for the API introduction.

    :param request: The incoming request.
    :return: A dictionary containing a welcome message.
    """
    return {"message": "Welcome to GitHub event monitoring API"}

@app.on_event('startup')
async def app_startup():
	"""
	Start streaming events and processing them in intervals.

	:return: cached events from JSON file or fail text
	"""
	asyncio.create_task(stream_and_process_events(CONFIG))

@app.get("/show_cached_events")
async def show_cached_events():
	"""
	Return content of cached events.

	:return: cached events from JSON file or fail text
	"""
	if CONFIG["cache_events"]:
		return read_events_from_json(CONFIG["cache_filepath"])
	else:
		return {"message": "Caching of events is not enabled."}


@app.get("/avg_pr_time/{repo_input:path}")
async def get_avg_pr_time(
	repo_input: str = Path(..., title="Repository name or ID")):
	"""
	Get average pull request time for given GitHub repository.

	:param repo_input: name or ID of GitHub repository
	:return: repository identification and either average time or fail text
	"""
	avg_time = calculate_average_time_between_pull_requests(repo_input)
	if avg_time is not None:
		return {"repository": repo_input, "avg_pr_time": avg_time}

	return {"repository": repo_input,
			"message": "Not enough data for calculation"}


@app.get("/event_counts/{event_type}/{offset}")
async def get_event_counts(event_type: str, offset: int):
	"""
	Get count of specified type of events within offset set by minutes.

	:param event_type:  type specification for event
	:param offset:  time offset in minutes
	"""
	event_count = calculate_event_counts_within_offset(event_type, offset)
	return {"event_type": event_type, "event_count": event_count}


@app.get("/event_counts_plot")
async def get_event_counts_plot():
	"""
	Get for visualization of event counts in time.

	:return: Response carrying an image in .png format
	"""
	img_bytes = visualize_event_counts()
	return Response(content=img_bytes,
					media_type="image/png",
					headers={"Content-Type": "image/png"})
