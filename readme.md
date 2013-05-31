Sitemap Checker
===============

The Sitemap Checker project is small collection of scripts that can be used to check
the health of a website's xml sitemap or sitemap index. The Python script requires
the lxml library and the requests module. The PowerShell script requires
PowerShell 3.0. Running a script produces a CSV file with each row containing a URL
from the sitemap, the status code, whether or not the URL is canonical, and the
canonical URL.

To test a sitemap with python, open a command line and type:

	C:\>python SitemapVerify.py [URL] [saveas location]

To run the powershell version:

	PS C:\> .\SitemapVerify.ps1 [URL] [saveas location]

There is also a version of the PowerShell script, SitemaveVerifyLocal.ps1, that can be 
run on a locally saved sitemap. To use it:

	PS C:\> .\SitemapVerifyLocal.ps1 [sitemap path] [saveas path]

The sitemap index scripts work exactly the same way, but the PowerShell version is not
quite ready to be used. Happy map checking!
