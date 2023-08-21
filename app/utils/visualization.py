import io
import pandas as pd

import plotly.graph_objs as go
import plotly.io as pio
from plotly.subplots import make_subplots

from utils.event_streaming import EVENT_TO_TIMESTAMPS_DICT


def visualize_event_counts():
	"""
	Create visualization of GitHub event counts in time.

    :return: plotted visualization in bytes of .png format
	"""
	data = {
		"Datetime": [timestamp
			for event_list in EVENT_TO_TIMESTAMPS_DICT.values()
			for timestamp in event_list],
		"Event Type": [event_type
			for event_type, event_list in EVENT_TO_TIMESTAMPS_DICT.items()
			for _ in event_list]
	}
	total_event_count = len(data["Datetime"])

    # Group data by event type and datetime intervals
	df = pd.DataFrame(data)
	df_grouped = df.groupby(
		['Datetime', 'Event Type']).size().unstack(fill_value=0)

	# Add traces for each event type
	fig = make_subplots(rows=1, cols=1, shared_xaxes=True)
	for event_type in EVENT_TO_TIMESTAMPS_DICT.keys():
		fig.add_trace(
		    go.Scatter(
		        x=df_grouped.index,
		        y=df_grouped[event_type],
		        mode='lines',
		        stackgroup='one',
		        name=event_type
		    )
		)

	# Update layout
	fig.update_layout(
		xaxis_title='DateTime',
		yaxis_title='Event Counts',
		title=f'Sums of monitored types of events over time, \
		[{total_event_count} events in total]',
		showlegend=True
	)

	# Export the figure as a PNG image
	img_stream = io.BytesIO()
	pio.write_image(fig, img_stream, format="png")

	# Get the bytes from the image stream
	img_bytes = img_stream.getvalue()

	return img_bytes
