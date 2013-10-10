param ($indexurl = $(throw "sitemap file path required"),
	$savefolder = $(throw "save folder path required"))

# Create folder to save CSVs. Program produces 1 CSV for each sitemap.
New-Item -Path $savefolder -ItemType Directory

# Download and parse XML sitemap. Trim any leading BOM characters or trailing
# spaces, and make list of sitemaps.
[xml]$index = (Invoke-WebRequest $indexurl).content.trimstart("ï»¿")
$locnodes = $index.sitemapindex.sitemap.loc.trimend()

# Function: get status codes and canonical tags for URLs in a sitemap.
function checker
{
	param ($sitemap)
	
	# create list of URLs in sitemap.
	$mapnodes = $sitemap.urlset.url.loc.trimend()
	$num = 1
	
	foreach ($node in $mapnodes)
	{
		# try to download webpage and parse HTML to check canonical tag.
		# return status code, and canonical info.
		try
		{
			$page = Invoke-WebRequest $node -MaximumRedirection 0 `
				-ErrorAction:SilentlyContinue
			$statuscode = $page.StatusCode
			$link = $page.parsedHTML.getElementsByTagName("link") |
				Where-Object -property rel -value canonical -EQ
			$canonical = $link.href
			$iscanonical = $canonical -eq $node
			[PsCustomObject]@{"Num"=$num; "URL"=$node; "Status Code"=$statuscode;
				"Canonical"=$iscanonical; "Canonical URL"=$canonical}
		}
		# If request fails, return error info.
		catch
		{
			$result = $error[0].exception.response.statuscode.value__
			$iscanonical = "N/A"
			[PsCustomObject]@{"Num"=$num; "URL"=$node; "Status Code"=$result;
				"Canonical"=$iscanonical; "Canonical URL"="N/A"}
		}
		[int]$completion = $num/$mapnodes.length*100
		Write-Progress `
			-activity "Getting status codes of sitemap URLs and entering them in CSV" `
			-status "Progress:" -currentoperation $completion% `
			-percentcomplete $completion
		$num += 1
	}
}

# Check status codes and canonical tags of URLs for each sitemap. Save results
# in CSV file in folder created at beginning of program.
foreach ($node in $locnodes)
{
	[xml]$sitemap = (Invoke-WebRequest $node).content.trimstart("ï»¿")
	$mapname = $node.split('/')[-1] + ".csv"
	$savefile = "$savefolder\$mapname"
	checker $sitemap | Export-CSV $savefile -NoTypeInformation
}
