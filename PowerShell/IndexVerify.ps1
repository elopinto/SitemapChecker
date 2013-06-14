param ($indexurl = $(throw "sitemap file path required"),
	[int]$start = $(throw "starting node required"))

	
[xml]$index = (Invoke-WebRequest $indexurl).content.trimstart("ï»¿")
$locnodes = $index.sitemapindex.sitemap.loc.trimend()


function checker
{
	param ($sitemap)
	
	$mapnodes = $sitemap.urlset.url.loc.trimend()
	$num = 1
	
	foreach ($node in $mapnodes)
	{
		try
		{
			$page = (Invoke-WebRequest $node -MaximumRedirection 0 -ErrorAction:SilentlyContinue)
			$statuscode = $page.StatusCode
			$canonical = ($page.parsedHTML.getElementsByTagName("link") | Where-Object -property rel -eq -value canonical).href
			$iscanonical = $canonical -eq $node
			[PsCustomObject]@{"Num"=$num; "URL"=$node; "Status Code"=$statuscode; "Canonical"=$iscanonical; "Canonical URL"=$canonical}
		}
		catch
		{
			$result = $error[0].exception.response.statuscode.value__
			$iscanonical = "N/A"
			[PsCustomObject]@{"Num"=$num; "URL"=$node; "Status Code"=$result; "Canonical"=$iscanonical; "Canonical URL"="N/A"}
		}
		[int]$completion = $num/$mapnodes.length*100
		Write-Progress -activity "Getting status codes of sitemap URLs and entering them in CSV" -status "Progress:" -currentoperation $completion% -percentcomplete ($completion)
		$num += 1
	}
}

$num = 1
foreach ($node in $locnodes)
{
	[xml]$sitemap = (Invoke-WebRequest $node).content.trimstart("ï»¿")
	$mapname = $node.split('/')[-1] + ".csv"
	checker $sitemap | Export-CSV $mapname -NoTypeInformation
	$num += 1
}
