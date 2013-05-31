param ($indexurl = $(throw "sitemap file path required"),
	$target = $(throw "saveas file path required"))

	
[xml]$index = (invoke-webrequest $indexurl).content.trimstart("ï»¿")
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
			$page = (invoke-webrequest $node -maximumredirect 0)
			$statuscode = $page.statuscode
			$canonical = ($page.parsedHTML.getElementsByTagName("link") | where-object -property rel -eq -value canonical).href
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
		write-progress -activity "Getting status codes of sitemap URLs and entering them in CSV" -status "Progress:" -currentoperation $completion% -percentcomplete ($completion)
		$num += 1
	}
}

$num = 1
foreach ($node in $locnodes)
{
	[xml]$sitemap = (invoke-webrequest $node).content.trimstart("ï»¿")
	checker $sitemap | export-csv $target -append -notypeinformation
	$num += 1
}
