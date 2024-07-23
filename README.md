# Social Media Bot

## Installation

### 1. Install Dependencies

> In some cases, ```numpy``` will fail to load the c-extensions when running on a Raspberry pi. To fix this, run
> ```sudo apt-get install libatlas-base-dev```.

First, set up the virtual environment. Make sure you are in the ```social-media``` directory:

```python3 -m venv venv```

```source venv/bin/activate```

> To deactivate the virtual environment, run ```deactivate```.

Then, install the requirements for the project:

```pip install -r requirements.txt```

### 2. Set up the systemd service

Now, set up the systemd service. To do this, modify line 7 and 8 in ```etc/social-media-bot.service``` to indicate the path 
of the ```src``` directory and ```main.py```, respectively. Then, copy the service file to ```/etc/systemd/system/``` and enable the service:

```sudo cp etc/social-media.service /etc/systemd/system/```

```sudo chmod +x main.py```

```sudo systemctl daemon-reload```

```sudo systemctl enable social-media.service```

```sudo systemctl start social-media.service```

Finally, verify the service is running:

```sudo systemctl status social-media.service```