Sitemap Checker
===============

The Sitemap Checker project is small collection of scripts that can be used to
check the health of a website's xml sitemap or sitemap index. The Python script
requires the lxml library and the requests module. The PowerShell script
requires PowerShell 3.0. Running a script produces a CSV file with each row
containing a URL from the sitemap, the status code, whether or not the URL is
canonical, and the canonical URL.

To test a sitemap with python, open a command line and type:

	C:\>python SitemapVerify.py [URL] [saveas.csv]

To run the powershell version:

	PS C:\> .\SitemapVerify.ps1 [URL] [saveas.csv]

To test a sitemap saved on your computer, use a SitemapVerifyLocal script, and
use as the first argument a file name instead of a URL.

To test a sitemap index with python:

	C:\>python IndexVerify.py [URL] [new saveas folder]

To test a sitemap index with powershell:

	PS C:\> .\IndexVerify.py [URL] [new saveas folder]

The sitemap index scripts work exactly the same way, but the PowerShell version
is not quite ready to be used. Happy map checking!
