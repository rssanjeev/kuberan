Purpose: Data Extraction

General Data Extraction Philosophy

- When we design a script to extract data make sure you have the understanding as to what we are extracting. So that the script is adaptive enough to further modifications and enhancements.
- Basically what we are trying to achieve it to build a single source of truth for each ticker and data point about that ticker and consolidate all the data from multiple sources into a single document for each ticker in MongoDB. This way we can ensure that we have all the relevant data for each ticker in one place and we can easily access it whenever we need it. This also ensures that the insight that we will eventually arrive at is based on the most comprehensive and accurate data available.
- We need to be able to standardize the data that we are collection. The data we get from one source might be better than the other, we need to understand the logic and copilot needs to be able to codify that instead of relying on copilot for every thing. This needs to be codified and reviewed periodically so that the user is not basing their decisions on a blind belief that the data is standard across the board.
- So we need to establish a process to compare each and every data point across the data sources and standardize our data to be trust worthy.    
- Use the information that we extract from all the pages and update any other data sources other than Stock Analysis if needed
  - For example: The company overview we have already extracted might have N/A for the number of employees, we can update that information with the data we extract from Stock Analysis
  - Ensure data consistency and integrity across all data sources
- Schedule periodic re-extraction to keep the data up-to-date with respect to the data source, establish a frequency for re-extraction (e.g., quarterly, bi-annually)
- Implement error handling and logging to monitor the extraction process and handle any issues that arise
- Test the extraction process thoroughly to ensure accuracy and completeness of the data
- Ensure compliance with Data Source's terms of service regarding web scraping and data usage
- **Compliance**: Ensure compliance with Data Source's terms of service regarding web scraping and data usage
- Store the extracted data in MongoDB collections as per the defined schema
- Finally, document the entire extraction process, including the code, configurations, and any dependencies used, to facilitate future maintenance and updates.
- Ensure that the extraction process is efficient and can handle a large number of tickers without significant delays
- Just dont blindly extract data and overwrite it. We need to smart about the data point that we are extracting and checking if the data point exists - 
    - Check if the data we are extracting already exists in the database and if it does, compare the new data with the existing data to determine if an update is necessary.
    - If the data point does not exist, insert the new data into the database.
- **Data backup**: Store raw HTML or JSON responses for future reference, also in case of re-processing needs. We might also need to keep in mind when we last loaded the data for each ticker. 
- **Resume capability**: Restart from last checkpoint on failure
- If there is a delay or failure on that ticker, we can skip it and move on to the next ticker and come back to it later. But we need to come back to it at some point. So we need to keep track of which tickers have been processed and which ones are pending and which ones are failing and how many times they have failed.
- **Scalability**: Design the extraction process to handle an increasing number of tickers in the future without significant rework. I might consider upgrading t o pro license if needed.
- **Performance**: Optimize the extraction process to minimize the time taken per ticker, possibly by parallelizing requests where feasible.
- Since we might be a webscraping some of the data extraction, we need to be careful about the rate limits and not to overload the server with too many requests in a short period of time. We might need to implement some kind of throttling mechanism to avoid getting blocked by the server. And if we get blocked by the server, we need to have a way to recover from that and continue the extraction process where we left of not restart it completemly from the beginning.
- Update the copilot instructions file regularly with the path to the documentaiton files so that copilot has the complete context of what we are trying to achieve and its target with not just the extraction process but any process in the future.
- Copilot needs to have complete context of the data source that we are extracting from. So we need to provide copilot with the relevant documentation files that contain the information about the data source, its structure, the relevant HTML elements that we are extracting data from, etc. This way copilot will be able to generate accurate and efficient code for data extraction and project functionality and goals.
- Finally, document the entire extraction process, including the code, configurations, and any dependencies used, to facilitate future maintenance and updates. 
- There are multiple URLs within a single ticker's stock analysis page that we might need to extract data from. For example, the main page has some data, but the financials page has more detailed data. So we need to identify all the relevant URLs for each ticker and extract data from all of them. 
- We need to be careful about the order in which we extract data from these URLs, as some data might depend on others. So we need to plan the extraction process accordingly. Abd also we need to be careful about consolidating the data from multiple URLs into a single document for each ticker in MongoDB. 
- We need to ensure that the data is structured properly and there are no conflicts or duplications.
- Before beginning to extract any data from any of these pages, we need to first analyze the page structure and identify the relevant HTML elements that contain the data we need. We can use browser developer tools to inspect the page and find the relevant elements. Once we have identified the elements, we can write code to extract the data from those elements using BeautifulSoup or any other web scraping library.
- Document the HTML structure of each page and the relevant elements that we are extracting data from. This will help us in future maintenance and updates. 
- Update the copilot instructions to ensure that it understands the HTML structure and the relevant elements for each page. This will help it to generate accurate code for data extraction.
- Also instruct copilot to handle any changes in the HTML structure gracefully. For example, if an element is not found, it should log an error and continue with the extraction process instead of crashing.
- Instruct the copilot to refer to these documentation on the HTML structure and relevant elements while generating code for data extraction. This will help it to generate accurate and efficient code. And also for future updates, we can simply update the documentation and copilot instructions accordingly. This way we can ensure copilot is efficiently using its credits and has the complete context of what we are trying to achieve and its target with the extraction process.
- So we need to fundamentally understand what is a feature here. A feature is a specific functionality or capability that we are building as part of the Kuberan project. For example, STOCKS is a feature in our project. This feature can have multiple sub feature such as stocks overview, financials, forecast, metrics, dividends etc. Each of these features and sub-features might have an extraction designed for it. Like we might have already extracted the stcok overview from MASSIVE API but if we are extracting information from stock analysis website for the same stock overview, then we need to document that extraction process as well. So we need to ensure that we have a clear understanding of what constitutes a feature and sub-feature in our project and document the extraction process accordingly. 

        - So the path for stock analysis extraction documentation should be docs/Stocks/Financials_extractions_stock_analysis.md
        - If we have another extraction designed and planned for Financier feature using a different website, then the path for that documentation should be docs/Financials/Financials_extractions_[website_name].md
        - We might even want to use multiple data sources for a single feature/sub-feature. For Exampl: We might extract the Revenue data for a stock from stockanalysis website as well as yahoo finance website. In such cases we need to document the extraction process for both data sources separately. So the paths for those documentation files should be:
            - docs/Stocks/Financials_extractions_stockanalysis.md
            - docs/Stocks/Financials_extractions_yahoofinance.md
        - This was copilot is able to understand which document to create/read /update based on the feature/sub-feature and data source mentioned in the prompt.
- Since we are just starting out we will be using a lot of free tier data sources, the extraction process needs to be smart enough to standardize the data that we are extracting.
- This will enable us to reach a state where we can get the insights that are hidden behind a pay wall but for free.

Tools to use for Webscraping Extraction:
- Use puppeteer/playwright to navigate to the page and login into your account.
- Retrieving cookies and passing it to a new browser context.
- Puppeteer Usage Documentation Link: https://docs.apify.com/academy/puppeteer-playwright/common-use-cases/logging-into-a-website
    - Refer to this link to get a better understanding of how to best utilize Puppeteer/Playwright for our use case.
- If both Playwright and Puppeteer are not working, we can use Selenium as a last resort. But Selenium must be avoided if possible as it is more resource intensive and slower compared to Puppeteer/Playwright. We need to prioitize keeping the coding simple and efficient and as minimum as possible.
- Use BeautifulSoup if possible to parse the HTML content and extract the relevant data points.

Documentation Philosophy
- Basically we need one document per feature per extraction per phase. So for example, if we are extracting stock analysis data from Stock Analysis website, we need one document for that feature. If we are extracting financial statements data from MASSIVE API, we need one document for that feature. If there are multiple phases for a single feature, we can have multiple documents for each phase. But we need to ensure that the documents are organized and easy to navigate.
- Everytime I ask you to create or update a documentation file, ensure that you follow these guidelines:
    - The documentation needs to be brocken down into smaller parts and added to the relevant sections in the docs/ sub directories. I dont want the documentation to be in a single file. and Each documentation file should not exceed 300 lines. So we might need to create multiple documentation files for different aspects of the feature that we are building. 
    - The documentation on how we are extracting should be a different documentaion than what feature we are building. The feature secific documentaion is different from process specific documentaiton. The latter might change as we progress through the project but the feature specific documentation should remain the same. This way we can ensure consistency and keep our eyes on the goal.
    - For this lets split the docs folder into multiple sub directories based on the domains and features. For example, we can have a sub directory for Stock Analysis extraction, another for Financial Statements extraction, another for ETF analysis etc. This way we can keep the documentation organized and easy to navigate. But the extraction specific documentation should be under Extractions directory. That is Stock Analysis extraction and Financial Statements extraction should be under Extractions directory. 
    - The other documentation related to the features should be under their respective domain directories.
        - The the docs path sould looks like docs/Extractions/Stock_Analysis_Extraction.md
        - And docs/Extractions/Financial_Statements_Extraction.md
    - Whereas the feature specific documentation should be under docs/Financials/Stock_Analysis.md
        - And docs/Financials/Financial_Statements.md


Stocks Oveview Extractions
- We have been using MASSIVE API as our primary data provider for stock overview data. But there are certain data points that are not available in MASSIVE API that we need to extract from other sources. One such source is Stock Analysis website. We will be extracting data from Stock Analysis website for the stock overview feature.
- We can even use other sources like Yahoo Finance, Finviz etc. 

Data Source 1: MASSIVE API
- THe MASSIVE API already provides us with comprehensive overview of a particular stock, but also you get additional information about a particular stock which may not be available in other data sources.
- The basic advantage of this MASSIVE API is that it is fast it is simple and we can technically do it with minimal code compared to Web scraping.
- Currently we have the free dear for the mass of a PA which limits are API calls to five API calls per minute.
- This forces us to be diligent about making API calls and restrict traffic. There's also Photo says to look for other data sources which might not limiters on the API, but would require us to compensate on the technical coding implementation.
- There are a lot of information that I'm not provided by the mass of a PI like for example, the balance sheets, which are not available for the fleet year, which is what we currently using, but we need to look for other sources to get to see him information that is not available with a massive API.
- The documentation regarding the MASSIVE API endpoints can be found here: docs/MASSIVE API Documentation/MASSIVE_REFERENCE_ENDPOINTS_GUID.md

Data Source 2: FINVIZ
- The overview of a stock in finviz can be extracted from the same place where you want to extract the financials: https://finviz.com/quote.ashx?t=NVDA&p=d
- The overview section is present in the same page as the financials section. So we can extract both overview and financials from the same page.
- The overview data is pretty limited or disparate compared to MASSIVE API where you get the stocks overview as a structured data.
- But an advantage with FINVIZ is we get the information such as the location of a stock.
    - For Example: NVDA is based out of USA whereas TSM is TAIWAN. THis is not clear when it comes to MASSIVE where both are mentioned as US based. In this case we can use the finviz's data to standardize ours.





Financials Extractions

Data Source 1: Stock Analysis
Example link: https://stockanalysis.com/stocks/snps/

- We will use the Snynopsys as an example for this documentation. The same process/philosophy will be applied to all other tickers as well.
- For Example: https://stockanalysis.com/stocks/snps/
    - Main Page: https://stockanalysis.com/stocks/snps/
    - Financials Page: https://stockanalysis.com/stocks/snps/financials/
    - Forecast Page: https://stockanalysis.com/stocks/snps/forecasts/
    - Statistics Page: https://stockanalysis.com/stocks/snps/statistics/
    - Metrics Page: https://stockanalysis.com/stocks/snps/statistics/
       - This metrics pages has sub-tabs within itselfs like Metrics, Revewnue by Segment [https://stockanalysis.com/stocks/snps/metrics/revenue-by-segment/], Operating Margin by Segment [https://stockanalysis.com/stocks/snps/metrics/operating-margin-by-segment/], Operating Income by Segment [https://stockanalysis.com/stocks/snps/metrics/operating-income-by-segment/], Revenue by Type [https://stockanalysis.com/stocks/snps/metrics/revenue-by-type/], Gross margin by type [https://stockanalysis.com/stocks/snps/metrics/gross-margin-by-type/], Product revenue breakdown [https://stockanalysis.com/stocks/snps/metrics/product-revenue-breakdown/] and Operating Expense Breakdown [https://stockanalysis.com/stocks/snps/metrics/operating-expense-breakdown/]. 
       - Like this we have for multiple sub-tabs within other tabs like Profile, Statistics, Financials, etc.

- Another thing we need to remeber is that the Income sub-tab under the FInancials tab has a "Synopsys Income Statement" for this SNPS ticker which is for the SYNOPSYS INC company. This Income statement has a table of information on its income both Annual and QUaterly that can be toggled using the options provided. By default its annaual but if we click hte quarterly option we are redirected to  https://stockanalysis.com/stocks/snps/financials/?p=quarterly

    - This content of the table. And we need to extract both annual and quarterly data for all the relevant tickers. And store it in a structured format in MongoDB. As we are using MongoDB we need to design the document schema accordingly to accommodate both annual and quarterly data within a single document for each ticker. And as we update the data for each ticker we need to ensure that we are not overwriting any existing data but rather updating it in a way that preserves the historical data as well. So we need to design the update process accordingly. But this update process need to be efficient enough that it does nt update the same information twice.

    - The same applies to the general extraction as well. 
        - For Example: The URL [https://stockanalysis.com/stocks/snps/financials/] defaults to the Income sub-tab where the Revenue for the Fiscal Year - FY 2025 & Period Ending Oct 31, 2025 is shown as 7,054. At the top just under the sub-tab title "Synopsys Income Statement" it says "Financials in millions USD. Fiscal year is November - October." This means that all the financial data shown in this table is in millions of USD i.e. 7,054 means 7,054,000,000 USD. Which is 7.054 Billion USD. The same number is also shown in "Synopsys Revenue" page [https://stockanalysis.com/stocks/snps/revenue/] "Revenue (ttm) $7.05B". 7,054,000,000 USD might be the exact technical representation of the revenue but for general purposes we can round it off to 7.05 Billion USD. The extraction system needs to be smart enough to identify such cases and extract the data accordingly. 

        - Simialrly when it comes to Market cap, it appearrs twice - First time over here: https://stockanalysis.com/stocks/snps/market-cap/ and the second time over here: https://stockanalysis.com/stocks/snps/revenue/ So when the system is extracting data from the main page https://stockanalysis.com/stocks/snps/ it sees the Market Cap value of $62.12B right under the stock price of $482.79 iit needs to identify that this value is also present in the Revenue page as well and ensure that they are same/equal. 

        - So we need to extract this information as well and store it in MongoDB along with the other data we extract from this page.

    - It also has a Revenue attribute in the table, this also serves as a link to https://stockanalysis.com/stocks/snps/revenue/ page that dontains the detailed breakdown of the revenue for the company. So we need to extract data from this page as well. This page actually lives under the Statitics tab. So we need to be careful about identifying all the relevant URLs for each ticker and extracting data from all of them. And consolidating the data into a single document for each ticker in MongoDB.
    - This is just one example of a sub-tab under a tab, there are multiple such sub-tabs under other tabs as well. So we need to identify all of them and extract data from all of them.
    - This is just one example of a URL redirecting to a different sub-tab under a different tab. There are multiple such cases across different tickers. So we need to be careful about identifying all such cases and extracting data from all of them.
    
- Each of these tabs & sub-tabs might have info panels with insights
    - For Example: Synopsys Market Cap [https://stockanalysis.com/stocks/snps/market-cap/] Sub-tab has an info panel with the insight "Synopsys has a market cap or net worth of $89.78 billion as of December 11, 2025. Its market cap has increased by 3.43% in one year." and Synopsys Dividend Information tab [https://stockanalysis.com/stocks/snps/dividend/] has "There is no dividend history available for Synopsys. This usually means that the stock has never paid a dividend." The same goes to Synopsys Revenue tab [https://stockanalysis.com/stocks/snps/revenue/] has "In the fiscal year ending October 31, 2025, Synopsys had annual revenue of $7.05B with 15.12% growth. Synopsys had revenue of $2.25B in the quarter ending October 31, 2025, with 37.83% growth." Even though our goal is to arrive at these insights on our own using the raw data that we extract from these pages, we can still extract these insights as well and store them in MongoDB. This way we can have a reference point to compare our own insights against. This can help us validate our own insights and ensure that we are on the right track. So we need to identify all such info panels across different tabs & sub-tabs and extract the insights from them as well.

- We can skip extracting the charts data https://stockanalysis.com/stocks/snps/chart/ shown here. WE will be building our own dashboards and charts using the raw data that we extract from these pages. So we dont need to extract the chart data itself.

- The Company description shown here at https://stockanalysis.com/stocks/snps/company/  is also importatnt. Even thought we have already extacted company level overview from other data sources sucha s MASSIVE API, Alpha Vantage, Finnhub etc, we can still extract this description as well and store it in MongoDB. This way we can have a more comprehensive company profile for each ticker. So we need to identify such pages across different tickers and extract the company description from them as well. 
- This page [https://stockanalysis.com/stocks/] shows the list of stocks available on stocksanalysis.com. We already have a complete stocks overview at this endpoint /stocks/complete/{ticker} from MASSIVE API. See if we can find additional data points on this page that are not available in our existing data and extract them as well. 
- This must be a common behavious for each and every data point we are extracting It must be source agnostic. What we have must be the superset of what we are extracting. So always check if the data point we are extracting already exists in our existing data. If it does, compare the values and see if there is any difference. If there is a difference, we need to investigate further and see which one is more accurate. If the data point does not exist, we can simply add it to our existing data.
- A stocks hompage ex: https://stockanalysis.com/stocks/aapl/ has multiple tabs and sub-tabs within itself. We need to identify all the relevant tabs and sub-tabs for each ticker and extract data from all of them. And consolidate the data into a single document for each ticker in MongoDB.

- Dont create a new extraction documentation file for every small change or addition to the extraction process. Instead, group related changes together and document them in a single file. This way we can avoid clutter and keep the documentation organized and easy to navigate. If there are updates to the extraction process update the document itself. 



Data Source 2: Finviz
- We can also see if we can extract the same information we are planning to extract from stockanalysis.com from https://finviz.com/ where all the financial data is available as a single table. 
    - For Example: The same ticker https://finviz.com/quote.ashx?t=SNPS&p=d - This is the Stock Detail sub-tab - has all the financial data in a single table below the chart.
    - Above that table we mentioned in the previous point, there a link with the hyper text "Scroll to Statements: and when clicked it takes you to the statementes section in the same page with the URL: https://finviz.com/quote.ashx?t=SNPS&p=d#statements - Here you will find the income statement, balance sheet and cash flow statement all in a single page split into tabs and by period of ANnual and Quarterly. Right now with this free tier we have access o last 3 quarters and last 3 annaual statements. Basically the content of the same table varies with the period, statement type and how the data needs to be presented i.e. YoY Growth or YoY Growth %. 
    - This webpage also provide information on ownership i.e. Who owns what percentage of this stock/company. 
- See if you can navigate throuhg this page and extract all the relevant financial data from the homepage as well.
- There is a table called "Price Reaction to Earnings Reports" which shows how the stock price reacted to the earnings reports over the last few quarters something around 8 quarters. This can be useful information to have as well. So we need to extract this information as well.
- For now we have the free account, but we need to be prepared to extract additional data once we upgrade to the Elite account. But we dont have access to the structure of the data that we can extract with that account. But we will cross that bridge when we come to it. For now focus on extracting the data that is available with the free account.
- The high level information about a stock is available on the stocks hompage itself. But in hypertext - url form. 
    - For Example: At https://finviz.com/quote.ashx?t=SNPS&p=d we have the hypertext of the company name right next to the ticker symbol. - SNPS Synopsys, Inc - Where Synopsys, Inc is the hypertext which when clicked takes you to the company profile page at https://www.synopsys.com/
    - Below that we have the hypertexts - Technology • Software - Infrastructure • USA • NASD
        - The first leads to the https://finviz.com/screener.ashx?v=111&f=sec_technology which shows all the technology sector stocks. 
        - The second leads to https://finviz.com/screener.ashx?v=111&f=ind_softwareinfrastructure which shows all the software infrastructure industry stocks.
        - The third leads to https://finviz.com/screener.ashx?v=111&f=geo_usa which shows all the USA based stocks.
        - The fourth leads to https://finviz.com/screener.ashx?v=111&f=exch_nasd which shows all the NASDAQ listed stocks.
- If I ask copilot to create a new extraction to get all the stocks in the USA, it needs to know that this information is available on finviz.com and it needs to navigate to https://finviz.com/screener.ashx?v=111&f=geo_usa to get the list of all USA based stocks.
- The same applies to the other URLs as well. 
- To further expand your knowledge about basic Stock Screener - Which is what were are eventually building on top of the data that we are extracting now - refer to the content of this URL: https://finviz.com/help/screener.ashx
    - There are several URLs used in each sub-section in this page - This will help you build a map as to how they are related to on another. 
    - This will help you plan out our extraction process efficiently.
    - It also shows where each of the topics mentioned in this page are appearing. 
    - Extract this information and build our own knowledge base. This knowledge base will be just the starting point as we find more and more resources like finviz, stocksanalysis we will build on top of this and expand our knowledge.
    - Indexing/Documentation of these resources are very important. This will help the script to know where is what.

