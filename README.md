Sitemap.xml Checker with Python

This Python script checks the URLs listed in a website's sitemap.xml file to ensure they are accessible and returns their HTTP status codes. It also verifies the site's robots.txt file to identify any disallowed URLs.

Prerequisites

- Python 3.x installed on your system.
- Required Python libraries: requests, pandas, openpyxl.

You can install the necessary libraries using pip:

pip install requests pandas openpyxl

Usage

1. Clone this repository or download the sm.py script.

2. Run the script from the command line, providing the domain name as an argument:

python sm.py yourdomain.com

Replace yourdomain.com with the actual domain you want to check.

3. The script will perform the following actions:

- Fetch the robots.txt file from the specified domain.
- Parse the sitemap.xml file to extract all listed URLs.
- Check each URL's HTTP status code.
- Identify URLs disallowed by robots.txt.
- Save the results to an Excel file named sitemap_report.xlsx.

Output

The output Excel file, sitemap_report.xlsx, contains the following columns:

- URL: The URL extracted from the sitemap.
- Status Code: The HTTP status code returned by the URL.
- Allowed by robots.txt: Indicates whether the URL is allowed or disallowed by the site's robots.txt file.

Notes

- Ensure that the domain you specify has a sitemap.xml file accessible at the root level (e.g., https://yourdomain.com/sitemap.xml).
- The script uses a default User-Agent header to mimic a mobile browser. You can modify this in the HEADERS dictionary within the script if needed.
- The script includes a delay between requests to avoid overwhelming the server.

License

This project is licensed under the MIT License.

