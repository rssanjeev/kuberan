Purpose: Kuberan - A comprehensive tool to gather all relevant information required to enable the user to make informed trading decisions.

Functional Philosophy:
- Build Knowledgebase: Continuously update and expand on the the understanding of trading terminalofies and user references. 
- Data Aggregation: Collects data from multiple reliable financial data providers to ensure accuracy and comprehensiveness.
- User-Centric Design: Focuses on delivering information in a clear, concise manner that is easy to understand and act upon.
- Real-Time Updates: Provides up-to-date information to help users respond to market changes promptly.
- Analytical Tools: Includes features for technical analysis, trend identification, and risk assessment to support strategic decision-making.
- Customization: Allows users to tailor the information and alerts based on their specific trading strategies and preferences.

Key Features:
[Priority Features]
- Knowledgebase: Comprehensive knowledgebase covering trading terminologies, strategies, and best practices. [docs/Trader_Knowledgebase.md]
- Data Extractions: Extracts data from various sources whether it's an API or web scraping. [docs/Data_Extraction.md]
- Data Standardization: Standardizes data from multiple sources to ensure consistency and reliability. [docs/Data_Standardization.md]

[Future Features]
- News Integration: Aggregates relevant news articles and updates that may impact trading decisions.
- Alerts & Notifications: Customizable alerts for significant market movements or news events.
- User Interface: Intuitive interface for easy navigation and information access.
- Reporting: Generates reports summarizing market conditions and trading performance.

Intended Users:
- Individual Traders: Retail investors looking for a comprehensive tool to assist in their trading decisions. These traders range from novices to experienced individuals. So the tool is designed to be user-friendly for all levels especially beginners. This tool aims to empower the user to make informed decisions. Help them to understand the market better and make them see the bigger picture.

Current Status:
- the current status of the application can be verified with these documentations:
    - docs/KUBERAN_MASSIVE_IMPLEMENTATION_PLAN.md
    - docs/FRONTEND_IMPLEMENTATION_PLAN.md
    - docs/KUBERAN_MASSIVE_IMPLEMENTATION_PLAN.md

Development Philosophy:
- None of the Pythons scripts should be more than 350 lines of code if a particular functionality requires to be more thanit needs to be a separate file.
- All the scripts should have proper logging implemented so that in case of any failure it is easy to debug.
- All the timestamps, including the logs, should be in Eastern Standard Time.
- All the configurations should be in the config files and not hardcoded anywhere in the scripts.
- All the scripts should have proper error handling implemented so that in case of any failure the script does not crash but logs the error and continues with the next item.
- All the scripts should have proper docstrings and comments so that it is easy to understand the functionality of the script.
- All the scripts should follow the PEP 8 guidelines for Python code style.
- All the scripts should have unit tests implemented to ensure the functionality of the script.
- All the scripts should be modular and reusable so that it is easy to maintain and extend the functionality of the script.
- All the scripts should be optimized for performance to ensure that they run efficiently.
- We have already started working on and completed a few of the features that we have developed using async.
- All the scripts should use async wherever possible to ensure that they run efficiently and do not block the main thread.
- All the scripts should use type hints to ensure that the code is easy to understand and maintain
- The copilot instructions file should be updated. Every time the code is updated. Copilot should be able to find the file that it's looking for or the functionality it is looking for based on the documentation that we already have. 
- If it is needed, copilot should be able to copy the documentation and place it under the .github folder to ensure efficient credit usage.