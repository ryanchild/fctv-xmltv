# Fort Collins TV Guide Downloader

Scrapes FCTV guide data from reflect-vod-fcgov.cablecast.tv and converts to XMLTV format

------------------------------------------------------------------------

### Using Locally:
 - Install script's requirements: `pip install -r requirements.txt`
 - Edit your `run.sh` file to suit / pull in ical files;
 - Plug into your PVR such as TVHeadend, etc.

### Using via docker:
Probably the easiest if you want to get going right away and don't want to install the various python deps on your system...

- Install [Docker](https://www.docker.com/) & [Docker Compose](https://docs.docker.com/compose/install/);
- CD to app source directory and run: `docker-compose down && docker-compose up --build`
