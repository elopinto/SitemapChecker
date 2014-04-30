param(
    [Parameter(Mandatory=$true, Position=0)]
    [String]$Indexurl,
    [Parameter(Mandatory=$true, Position=1)]
    [String]$Target
    )

# Create folder to save CSVs. Program produces 1 CSV for each sitemap.
New-Item -Path $Target -ItemType Directory

# Download and parse XML sitemap. Trim any leading BOM characters or trailing
# spaces, and make list of sitemaps.
[xml]$index = (Invoke-WebRequest $Indexurl).Content.TrimStart("ï»¿")
$mapnodes = $index.sitemapindex.sitemap.loc.TrimEnd()

# Function: get status codes and canonical tags for URLs in a sitemap.
Function Check-Sitemap
{
    Begin {
        $num = 1
    }
    Process {
        # try to download page and get status code and canonical tag
        $url = $_
        Try {
            $page = Invoke-WebRequest $url -MaximumRedirection 0 `
                -ErrorAction:SilentlyContinue
            $statuscode = $page.StatusCode
            $links = $page.ParsedHtml.getElementsByTagName("link") |
                Where-Object -Property rel -EQ -Value canonical
            $canonical = $links.href
            $iscanonical = $canonical -eq $url
            [PsCustomObject]@{"Num"=$num; "URL"=$url; "Status Code"=$statuscode;
                "Canonical"=$iscanonical; "Canonical URL"=$canonical}
        }
        # If request fails, return error info.
        Catch [System.Net.WebException] {
            $result = $error[0].Exception.Response.StatusCode.Value__
            $iscanonical = "N/A"
            [PsCustomObject]@{"Num"=$num; "URL"=$url; "Status Code"=$result;
                "Canonical"=$iscanonical; "Canonical URL"="N/A"}
        }
        Catch [System.Management.Automation.RuntimeException] {
            $result = (Invoke-WebRequest $url -MaximumRedirection 0 `
                -ErrorAction:SilentlyContinue).StatusCode
            $iscanonical = "N/A"
            [PsCustomObject]@{"Num"=$num; "URL"=$url; "Status Code"=$result;
                "Canonical"=$iscanonical; "Canonical URL"="HMTL error"}
        }
        [int]$completion = $num / $locnodes.length * 100
        Write-Progress `
            -Activity "Getting status codes of sitemap URLs and entering them in CSV" `
            -Status "Progress:" -CurrentOperation $completion% `
            -PercentComplete $completion
        $num += 1
    }
}

# Check status codes and canonical tags of URLs for each sitemap. Save results
# in CSV file in folder created at beginning of program.
$mapnodes | ForEach-Object {
    [xml]$sitemap = (Invoke-WebRequest $_).Content.TrimStart("ï»¿");
    $locnodes = $sitemap.urlset.url.loc.TrimEnd();
    $mapname = $_.Split('/')[-1] + ".csv";
    $savefile = "$Target\$mapname";
    $locnodes | Check-Sitemap | Export-CSV $savefile -NoTypeInformation
}
