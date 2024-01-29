# Running ToDBot
- Once the project is setup below, make sure the ToD Google Sheet is shared with the `client_email` address provided in the `creds.json` file you downloaded.
- Activate your conda environment `conda activate ToDBot`
- Run `python.exe .\bot.py` in Powershell to run the bot
- Verify there are no errors on startup, and the bot has connected to the correct discord server.

# Managing Dependencies

 - Use a module called `pipreqs`. It can be installed using `pip install pipreqs`
 - Then, run `pipreqs.exe --force` to overwrite the current `requirements.txt` file. 
 - You can then run `pip install -r requirements.txt` to install all dependencies
 - Using this module allows us to only create a dependency file for dependencies actually used in the project.

# Setup

### Setup Device for the bot
- Make sure you are running Windows 10 Pro (or use Microsoft Activation Scripts)
- [Disable Automatic Updates](https://learn.microsoft.com/en-us/answers/questions/1351413/how-do-you-turn-off-windows-10-updates-which-are-r)
- If necessary, disable the computer shutting down when closing the lid of the laptop

### Install Conda 
`https://conda.io/projects/conda/en/latest/user-guide/install/windows.html`

Follow instructions [here](https://stackoverflow.com/questions/44515769/conda-is-not-recognized-as-internal-or-external-command)
 - add the `/Scripts` and `/Library/bin` paths to environment variables

Run the following commands: 
```
conda init
conda create --name ToDBot python=3.9
# restart powershell
conda activate ToDBot
# Then install dependencies as directed in the Managing Dependencies section
```

### Discord credentials
- Share an already generated token with yourself across a secured method (email, or personal Google Drive), or do the following:
- Sign in to Discord on Desktop
- Navigate to the [Discord Developers Page](https://discord.com/developers/applications)
- Click on ToDBot, then OAuth2
- Click Reset Token to get new token

### Google Sheets credentials
- Sign in to Google, and navigate to the google cloud console
- Click on `IAM & Admin`
- Go to `Service Accounts`
- Click on the three dots next to one of the service accounts and click `Manage Details`. Then, at the top, go to `Keys`
- Click `ADD KEY` and then `Create New Key` and save as a JSON.
- Name this file `creds.json` and save in the root directory of this repo.
