# Sync-Polar-Balance-scale-to-Garmin-Connect
Synchronize weightmeasures from a Polar Balance scale to Garmin Connect. For the complete story check my (dutch) website https://www.sydspost.nl/index.php/2023/01/10/3109/

Based on/thanks to:
- Polar Electro for accesslink example, https://github.com/polarofficial/accesslink-example-python
- Matt Tucker for Fit-tool, https://pypi.org/project/fit-tool/
- Bastien Adabie for garmin_uploader, https://github.com/La0/garmin-uploader

Prerequisites
- Polar Flow account, https://flow.polar.com/
- Polar Balance scale connected to Polar Flow account
- Garmin connect account, https://connect.garmin.com/
- Python 3 and pip related to Python 3

Getting Started

1. Create new API client on Polar AccessLink
Navigate to https://admin.polaraccesslink.com. Log in with your Polar Flow account and create a new client.

Use http://localhost:5000/oauth2_callback as the authorization callback domain.

2. Configure client credentials
Fill in your client id and secret in config.yml (example):

client_id: 57a715f8-b7e8-11e7-abc4-cec278b6b50a
client_secret: 62c54f4a-b7e8-11e7-abc4-cec278b6b50a

3. Install python dependencies
pip3 install -r requirements.txt

4. Link user
Polar Flow User account needs to be linked to sync application before application can get any user data. User is asked for authorization in Polar Flow, and user is redirected back to application callback url with authorization code once user has accepted the request.

To start example callback service, run:

python authorization.py
and navigate to https://flow.polar.com/oauth2/authorization?response_type=code&client_id=<YOUR_CLIENT_ID> to link user account. After linking has been done you may close authorization.py. Linking saves access token and user id to config.yml

5. Edit the provided config file and add your Garmin Connect username and password.

⚠️ WARNING!!! The username and password are stored in clear text, WHICH IS NOT SECURE. If you have concerns about storing your garmin connect username and password in an unsecure file, do not use this option.

Edit the provided text file named .guploadrc (or gupload.ini for Windows users) containing the following:

[Credentials]
username=<username>
password=<password>

Replace username and password with your Garmin Connect login credentials.

6. Run sync.py

python sync.py

If there is no new weight measurement, the script ends without uploading data to Garmin Connect. This prevents double of multiple registrations.

To run application with a certain frequency, add this command to a scheduler like cron on linux. Example:
0 3 * * * cd /home/pi/Sync-Polar-Balance-scale-to-Garmin-Connect; python3 /home/pi/Sync-Polar-Balance-scale-to-Garmin-Connect/sync.py
