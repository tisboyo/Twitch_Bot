# Import standard python modules
import time
import aio_secrets

# Import Adafruit IO REST client.
from Adafruit_IO import Client, Feed

# to get stored credientials
from os import environ as secrets

ADAFRUIT_IO_KEY = secrets["ADAFRUIT_IO_KEY"]
ADAFRUIT_IO_USERNAME = secrets["ADAFRUIT_IO_USERNAME"]

AIO_CONNECTION_STATE = False
aio =""

def connect_to_aio():
	global AIO_CONNECTION_STATE
	global aio
	# Create an instance of the REST client.
	try:
		print("Atempting to connect to AIO as " + ADAFRUIT_IO_USERNAME)
		aio = Client(ADAFRUIT_IO_USERNAME, ADAFRUIT_IO_KEY)
		print("Connected")
		AIO_CONNECTION_STATE = True
	except:
		print("Failed to connect to AIO, disabling it")
		AIO_CONNECTION_STATE = False


def increment_feed(feed='treat-counter-text'):
	global AIO_CONNECTION_STATE
	global aio
	if (AIO_CONNECTION_STATE == False):
		print("Not publishing, we aren't connected")
		return

	feed_data = aio.data(feed) # returns an array of values
	feed_value = int(feed_data[0].value) # this feed only has 1

	feed_value += 1
	
	print('sending count: ', feed_value)
	aio.send_data('treat-counter-text', feed_value)


connect_to_aio()
increment_feed()
