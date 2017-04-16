# Sensors Data Collection
[![python](https://www.python.org/static/favicon.ico)](https://www.python.org/)[![raspi](https://pbs.twimg.com/profile_images/817056871181938688/bZHaUcRZ_normal.jpg)](https://www.raspberrypi.org/)

Small project that takes advantage of python multithreading to log readings from several sensors connected to a Raspberry Pi into a MySQL database.
This application is part of the ingestion stage for a more complex data analytics project in Georgetown SCS: Classroom Occupancy Prediction, created by:
- Abraham Montilla
- Nikolay Bandura
- Svetlana Zolotareva
- Mengdi Yue
- Kristen McIntyre

To use the project, simply run `sudo python data_collection.py`. The need of `sudo` is due to permission restrictions related to the bluetooth library. Be aware that DBLogger.py file must be updated with the correct user, password and database credentials.

The following is the output of `sudo python datacollection.py --help`
```sh
usage: dataCollection.py [-h] [-v] [-i ITER_SECONDS]

Reads from several sensors and logs values into MySQL database.

optional arguments:
  -h, --help            show this help message and exit
  -v, --verbose         show fetched values in stdout for every iteration
  -i ITER_SECONDS, --iter-seconds ITER_SECONDS
                        seconds to wait before a new reading iteration
                        executes.
```

# Sensors involved
### Synchronous
These sensors are logged every five seconds (by default) in the database.
  - Temperature and Humidity
  - CO2
  - Light
  - Noise
  - Bluetooth discoverable-devices count
### Asynchronous
These sensors are logged in the database every time an event happens.
  - Door opening/closing

# Technology
The project runs with Python 2.6 using sensors connected to a Raspberry Pi 3 Model B.
