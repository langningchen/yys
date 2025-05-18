# YYS Daily Script Automation

This project automates the daily login reward collection for the YYS game using Selenium. It logs in to the game website, verifies the login status, captures the daily reward, and saves a screenshot of the reward page.

## Features

- Automates the daily login process for YYS.
- Captures a screenshot of the daily reward page.
- Runs on GitHub Actions for scheduled automation.

## Requirements

- Python 3.12 or higher
- Google Chrome and ChromeDriver
- Selenium 4.32.0

## Usage

#### Getting Your YYS Token

1. Open the [YYS game website](https://ys.mihoyo.com/cloud/) in your browser and log in to your account.
2. Open the browser's developer tools (usually F12 or right-click and select "Inspect").
3. Go to the "Application" tab and look for the "Cookies" section in the left sidebar.
4. Find the cookie named `uni_web_token` and copy the value of it. The value should look like `0123456789abcdefghijklmnopqrstuvwxyz012345_mhy`
5. Make sure the token ends with `_mhy`. This is required for the script to work correctly.
6. Store this token securely, as it will be used to authenticate your daily login.

#### Running the Script

##### Using GitHub Actions (RECOMMENDED)

This project includes a GitHub Actions workflow to automate the script daily.

1. Fork this repository to your GitHub account.
2. Add your YYS token as a secret in your repository settings with the name `YYS_TOKEN`.
3. The workflow will run daily at midnight.

##### Running Locally

<details>

<summary>
If you prefer to run the script locally, follow these steps
</summary>

1. Clone this repository:
   ```bash
   git clone https://github.com/langningchen/yys
   cd yys
   ```

2. Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```

3. Ensure Google Chrome and ChromeDriver are installed and compatible with each other.

4. Run the script locally with your token:
    ```bash
    python main.py <your_token>
    ```
   - Replace `<your_token>` with your YYS token. The token must end with `_mhy`.
</details>

## Files

- `main.py`: The main script for automating the daily login process.
- `requirements.txt`: Lists the required Python dependencies.
- `.github/workflows/yys.yml`: GitHub Actions workflow for daily automation.

## Output

The script saves a screenshot of the daily reward page in the current directory with a timestamped filename (e.g., `2023-10-01-00-00-00.png`).

## Troubleshooting

- Ensure your token is valid and ends with `_mhy`.
- Verify that Chrome and ChromeDriver are installed and compatible.
- Check the logs in GitHub Actions for any errors during the workflow execution.

## License

This project is licensed under the GNU General Public License v3.0. See the [LICENSE](LICENSE) file for details.
