ScriptFang — Advanced XSS Payload Generator & Fuzzer
Welcome to ScriptFang, the ultimate tool designed for penetration testers and security researchers to generate, test, and fuzz XSS payloads with ease and power.

#Features
-Diverse Payload Generation: Choose from a wide range of XSS payload types (classic, WAF bypass, Angular, script breakout, Cloudflare bypass, and more).

-Multi-Payload Generation: Generate multiple payloads at once to increase fuzzing coverage.

-Integrated Fuzzer: Automatically fuzz targets with all payloads from your payload repository, tracking reflections, blocks, and errors live.

-Sleek GUI: PyQt6-based intuitive interface with live feedback and animated background for a smooth experience.

-Export Capability: Save your generated payloads for offline use or manual testing.

#Installation
Clone or download this repository.

Make sure you have Python 3.9+ installed.

#Install dependencies:

bash
Copy
Edit
pip install -r requirements.txt
(Make sure PyQt6 and requests are installed.)

#Usage
Run the tool:

bash
Copy
Edit
python gui.py
Enter the target URL (e.g., https://victim.com/search?q=).

Select a payload category or generate multiple payloads.

Click Test Payload to check reflection or Fuzz Target to fuzz the target with all available payloads.

Review live feedback in the output panel.

Export payloads if desired.

Payload Management
Payload files are stored under /tools/payloads/.

Each .txt file contains payloads of a specific category.

Add or edit payload files to customize your fuzzing arsenal.

Contribution
Contributions and payload improvements are welcome! Feel free to fork the repo and submit pull requests.

Disclaimer
Use ScriptFang responsibly. Only test systems you have explicit permission to assess. The author is not liable for misuse.

#Contact
Created by Talyx
GitHub: Github.com/Talyx66
