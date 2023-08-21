# Github Event Monitoring REST API

REST API application monitoring WatchEvent, PullRequestEvent and IssuesEvent from GitHub.
The events are streamed each 60 seconds, this is configurable in app/cfg/configuration.yaml file.

Its functionality offers:
* a) Return the average time between pull requests for a given repository (specified by either name or ID).
* b) Return the total number of events grouped by the event type for an offset given in minutes.
* c) Return an image of visualized sums of monitored types of events over time.

## Installation

1. Inside the project directory build the Docker image container.
```
docker build . -t gh-event-monitor
```
2. Run the built image.
```
docker run -p 80:80 gh-event-monitor
```
3. The app is now available on your device at [http://0.0.0.0:80](http://0.0.0.0:80).

## How to use endpoints

### Average time between pull requests for a repository

To retrieve the average time between pull requests for a specific repository, you can use the following endpoint:

**Endpoint:** `/avg_pr_time/{repo_input:path}`

**Method:** GET

**Parameters:**
- `repo_input`: The name or ID of the repository you want to query.

**Example Usage:**
```bash
curl http://0.0.0.0:80/avg_pr_time/owner/repository
```
```bash
curl http://0.0.0.0:80/avg_pr_time/repository-id
```
### Event count for specified event type
To get the total number of events of a specified type within a given time offset, you can use the following endpoint:

**Endpoint:** `/event_counts/{event_type}/{offset}`

**Method:** GET

**Parameters:**
- `event_type`: The type of event you want to count (e.g., WatchEvent, PullRequestEvent).
- `offset`: The time offset in minutes.

**Example Usage:**
```bash
curl http://0.0.0.0:80/event_counts/PullRequestEvent/60
```

### Visualization
To visualize the sums of monitored types of events over time, you can access the following endpoint:

**Endpoint:** `/avg_pr_time/{repo_input:path}`

**Method:** GET

**Example Usage:**
You need to wait atleast two instances of events download/filtering and processing to have content in plot.
```bash
curl http://0.0.0.0:80/event_counts_plot
```

### Debug: Show cached events
If application is run with "cache_events: true" in cfg/configuration.yaml, then you can access full text of monitored events at the following endpoint:

**Endpoint:** `/show_cached_events`

**Method:** GET

**Example Usage:**
```bash
curl http://0.0.0.0:80/show_cached_events
```
