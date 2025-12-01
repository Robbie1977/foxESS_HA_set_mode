# FoxESS K Series Inverter Control via API

This solution provides a way to control the working mode of FoxESS K series inverters through their Open API. It includes a Python script for direct API interaction and Home Assistant integration for automation.

## Prerequisites

- A FoxESS account with a K series inverter
- API key from FoxESS cloud platform
- Python 3.x installed
- Home Assistant (optional, for automation)

## Obtaining the API Key

1. Log in to your FoxESS cloud account at [https://www.foxesscloud.com](https://www.foxesscloud.com)
2. Go to your personal center (profile/settings)
3. Navigate to "API Management" or "Open API" section
4. Generate a new API key
5. **Important**: Keep this key secure and never share it publicly

## Installation

1. Clone or download this repository
2. Install required Python packages:
   ```bash
   pip install -r requirements.txt
   ```
   Or manually:
   ```bash
   pip install requests
   ```
3. Edit `foxess_control.py` and replace the placeholders:
   - `API_KEY = "your_api_key_here"` with your actual API key
   - `INVERTER_SN = "your_inverter_serial_number_here"` with your inverter's serial number

**Note**: The script can be placed in either `/config/custom_components/foxess/` or `/homeassistant/custom_components/foxess/` depending on how you access your Home Assistant files. Both paths work identically.

## Finding Your Inverter Serial Number

You can find your inverter's serial number in several ways:

1. Through the FoxESS app or web portal
2. Using the API: Run `python3 foxess_control.py get` after setting up the API key (it will show an error but reveal the SN)
3. Check the physical label on your inverter

## Usage

### Command Line

The script supports the following commands:

```bash
# Get current working mode
python3 foxess_control.py get

# Set to Self-Use mode (prioritize home consumption)
python3 foxess_control.py selfuse

# Set to Backup mode (battery backup priority)
python3 foxess_control.py backup

# Set to Feed-in mode (maximize grid export)
python3 foxess_control.py feedin

# Set to Peak Shaving mode
python3 foxess_control.py peakshaving
```

### Working Modes

- **SelfUse**: Prioritizes home energy consumption, uses battery when solar insufficient
- **Backup**: **Recommended for EV charging** - Battery acts as backup power, house draws from grid while solar charges battery, preventing battery discharge during charging
- **Feedin**: Maximizes energy export to grid, uses all available solar
- **PeakShaving**: Balances load during peak demand periods

## Home Assistant Integration

### 1. Place the Script

Copy `foxess_control.py` to your Home Assistant config directory:

- **Via File Editor**: Place the file at `/config/custom_components/foxess/foxess_control.py`
- **Via Samba/File Share**: Place the file at `/homeassistant/custom_components/foxess/foxess_control.py`

Create the `foxess` directory if it doesn't exist. This keeps the control script alongside your existing FoxESS integration.

### 2. Configure the Script

Edit `foxess_control.py` and update these two lines at the top:

```python
API_KEY = "your_api_key_here"          # Replace with your FoxESS API key
INVERTER_SN = "your_inverter_sn_here"   # Replace with your inverter serial number
```

### 3. Update configuration.yaml

Add the following shell commands to your `configuration.yaml`:

```yaml
shell_command:
  foxess_backup: "python3 /config/custom_components/foxess/foxess_control.py backup"
  foxess_self_use: "python3 /config/custom_components/foxess/foxess_control.py selfuse"
  foxess_feedin: "python3 /config/custom_components/foxess/foxess_control.py feedin"
  foxess_get_mode: "python3 /config/custom_components/foxess/foxess_control.py get"
```

**Note**: Use `/config/` path if accessing via Home Assistant File Editor, or `/homeassistant/` if using Samba shares. Both point to the same location.

### 4. Restart Home Assistant

Restart your Home Assistant instance to load the new shell commands.

## Testing in Home Assistant

### 1. Test the Script Directly

First, test the script works by running it directly. Use the Terminal add-on or SSH into Home Assistant:

```bash
# Navigate to the script location
cd /config/custom_components/foxess

# Test getting current mode
python3 foxess_control.py get

# Test setting backup mode
python3 foxess_control.py backup

# Test setting self-use mode
python3 foxess_control.py selfuse
```

You should see JSON responses indicating success (errno: 0).

### 2. Test Shell Commands

Once the script works, test the shell commands through Home Assistant:

1. Go to **Developer Tools** → **Actions** tab
2. In the **Service** dropdown, select `shell_command.foxess_get_mode`
3. Click **Call Service**

The service should return the current working mode of your inverter. The response will be a JSON object containing the mode information, typically showing something like:

```json
{
  "errno": 0,
  "result": {
    "value": "SelfUse",
    "unit": "",
    "precision": 0,
    "range": {
      "min": 0,
      "max": 0
    }
  }
}
```

The current mode is indicated by the `value` field in the `result` object (possible values: "SelfUse", "Backup", "Feedin", "PeakShaving").

### 3. Create Automations

Once testing is successful, create your automations. Here's an example for EV charging coordination:

```yaml
automation:
  - alias: "Backup mode when EV charging"
    trigger:
      - platform: state
        entity_id: sensor.ohme_charger_status  # adjust to your Ohme entity
        to: "charging"
    action:
      - service: shell_command.foxess_backup

  - alias: "Return to SelfUse after EV charging"
    trigger:
      - platform: state
        entity_id: sensor.ohme_charger_status
        from: "charging"
    action:
      - service: shell_command.foxess_self_use
```

**Note**: Adjust the `entity_id` to match your Ohme charger's status sensor.

## API Details

### Authentication

The FoxESS API uses token-based authentication with MD5 signatures:

- **Token**: Your API key
- **Timestamp**: Current Unix timestamp in milliseconds
- **Signature**: MD5 hash of `path\r\ntoken\r\ntimestamp`

### Rate Limits

- 1440 API calls per day per inverter
- Query endpoints: 1 call per second
- Update endpoints: 1 call every 2 seconds

### Endpoints Used

- `POST /op/v0/device/setting/set` - Set device settings (WorkMode)
- `POST /op/v0/device/setting/get` - Get device settings (WorkMode)

## Troubleshooting

### Common Issues

1. **Invalid API Key**: Double-check your API key in the script
2. **Wrong Serial Number**: Verify your inverter's SN
3. **Rate Limiting**: Wait a few seconds between API calls
4. **Network Issues**: Ensure stable internet connection

### Error Codes

- `40256`: Missing request headers
- `40257`: Invalid request body
- `40400`: Too frequent requests

### Home Assistant Issues

- Ensure the script path is correct in `configuration.yaml`
- Check Home Assistant logs for shell command errors
- Verify Python and requests library are installed

## Security Notes

- Never commit your API key to version control
- Use environment variables or secure storage for the API key
- Regularly rotate your API key if compromised
- The API key has full access to your FoxESS account

## Repository Contents

- `foxess_control.py` - Main Python script for API interaction
- `configuration.yaml` - Home Assistant configuration example
- `requirements.txt` - Python dependencies
- `README.md` - This documentation
- `LICENSE` - MIT License

## Contributing

Feel free to submit issues or pull requests to improve this solution.

## License

This project is provided as-is without warranty. Use at your own risk.