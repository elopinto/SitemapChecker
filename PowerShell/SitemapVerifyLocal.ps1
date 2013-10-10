param ($sitemapfile = $(throw "sitemap file path required"),
	$target = $(throw "Save As file path required"))

# Open sitemap saved on PC. Make list of URLs and trim trailing spaces.
[xml]$sitemap = Get-Content $sitemapfile
$locnodes = $sitemap.urlset.url.loc.trimend()

# Function: For each URL in sitemap, return status code and canonical tag.
function checker
{
	$num = 1
	
	foreach ($node in $locnodes)
	{
		# try to download page and get status code and canonical tag
		try
		{
			$page = Invoke-WebRequest $node -MaximumRedirection 0 `
				-ErrorAction:SilentlyContinue
			$statuscode = $page.StatusCode
			$links = $page.parsedHTML.getElementsByTagName("link") |
				Where-Object -property rel -value canonical -EQ
			$canonical = $links.href
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
		[int]$completion = $num/$locnodes.length*100
		Write-Progress `
			-activity "Getting status codes of sitemap URLs and entering them in CSV" `
			-status "Progress:" -currentoperation $completion% `
			-percentcomplete $completion
		$num += 1
	}
}

# Run program, save results in CSV file.
checker | Export-CSV $target -NoTypeInformation
