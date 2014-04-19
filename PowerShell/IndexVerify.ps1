param(
	[Parameter(Mandatory=$true, Position=0)]
	[String]$Indexurl,
	[Parameter(Mandatory=$true, Position=1)]
	[String]$Target
	)

# Create folder to save CSVs. Program produces 1 CSV for each sitemap.
New-Item -Path $savefolder -ItemType Directory

# Download and parse XML sitemap. Trim any leading BOM characters or trailing
# spaces, and make list of sitemaps.
[xml]$index = (Invoke-WebRequest $Indexurl).Content.TrimStart("ï»¿")
$locnodes = $index.sitemapindex.sitemap.loc.TrimEnd()

# Function: get status codes and canonical tags for URLs in a sitemap.
Function Check-Sitemap
{
	param($sitemap)
	
	# create list of URLs in sitemap.
	$mapnodes = $sitemap.urlset.url.loc.TrimEnd()
	$num = 1
	
	ForEach ($node in $mapnodes) {
		# try to download webpage and parse HTML to check canonical tag.
		# return status code, and canonical info.
		Try {
			$page = Invoke-WebRequest $node -MaximumRedirection 0 `
				-ErrorAction:SilentlyContinue
			$statuscode = $page.StatusCode
			$link = $page.ParsedHtml.getElementsByTagName("link") |
				Where-Object -Property rel -EQ -Value canonical
			$canonical = $link.href
			$iscanonical = $canonical -eq $node
			[PsCustomObject]@{"Num"=$num; "URL"=$node; "Status Code"=$statuscode;
				"Canonical"=$iscanonical; "Canonical URL"=$canonical}
		}
		# If request fails, return error info.
		Catch {
			$result = $error[0].Exception.Response.StatusCode.Value__
			$iscanonical = "N/A"
			[PsCustomObject]@{"Num"=$num; "URL"=$node; "Status Code"=$result;
				"Canonical"=$iscanonical; "Canonical URL"="N/A"}
		}
		[int]$completion = $num/$mapnodes.length*100
		Write-Progress `
			-Activity "Getting status codes of sitemap URLs and entering them in CSV" `
			-Status "Progress:" -CurrentOperation $completion% `
			-PercentComplete $completion
		$num += 1
	}
}

# Check status codes and canonical tags of URLs for each sitemap. Save results
# in CSV file in folder created at beginning of program.
ForEach ($node in $locnodes) {
	[xml]$sitemap = (Invoke-WebRequest $node).Content.TrimStart("ï»¿")
	$mapname = $node.Split('/')[-1] + ".csv"
	$savefile = "$savefolder\$mapname"
	Check-Sitemap $sitemap | Export-CSV $savefile -NoTypeInformation
}
