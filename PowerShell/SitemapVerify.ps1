param ($sitemapurl = $(throw "sitemap file path required"),
	$target = $(throw "Save As file path required"))


[xml]$sitemap = (invoke-webrequest $sitemapurl).content
$locnodes = $sitemap.urlset.url.loc.trimend()


function checker
{
	$num = 1
	
	foreach ($node in $locnodes)
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
		[int]$completion = $num/$locnodes.length*100
		write-progress -activity "Getting status codes of sitemap URLs and entering them in CSV" -status "Progress:" -currentoperation $completion% -percentcomplete ($completion)
		$num += 1
	}
}


checker | export-csv $target -notypeinformation
