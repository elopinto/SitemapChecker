param(
	[Parameter(Mandatory=$true, Position=0)]
	[String]$Sitemapurl,
	[Parameter(Mandatory=$true, Position=1)]
	[String]$Target
	)

# Download and parse XML sitemap. Make list of URLs and trim trailing spaces.
[xml]$sitemap = (Invoke-WebRequest $Sitemapurl).Content
$locnodes = $sitemap.urlset.url.loc.TrimEnd()

# Function: For each URL in sitemap, return status code and canonical tag.
Function Check-Sitemap
{
	$num = 1
	
	ForEach ($node in $locnodes) {
		# try to download page and get status code and canonical tag
		Try {
			$page = Invoke-WebRequest $node -MaximumRedirection 0 `
				-ErrorAction:SilentlyContinue
			$statuscode = $page.StatusCode
			$links = $page.ParsedHtml.getElementsByTagName("link") |
				Where-Object -Property rel -EQ -Value canonical
			$canonical = $links.href
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
		[int]$completion = $num/$locnodes.length*100
		Write-Progress `
			-Activity "Getting status codes of sitemap URLs and entering them in CSV" `
			-Status "Progress:" -CurrentOperation $completion% `
			-PercentComplete $completion
		$num += 1
	}
}

# Run program, save results in CSV file.
Check-Sitemap | Export-CSV $target -NoTypeInformation
