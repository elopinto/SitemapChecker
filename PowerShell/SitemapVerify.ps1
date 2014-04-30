param(
    [Parameter(Mandatory=$true, Position=0)]
    [String]$Sitemapurl,
    [Parameter(Mandatory=$true, Position=1)]
    [String]$Target
    )

# Download and parse XML sitemap. Make list of URLs and trim trailing spaces.
[xml]$sitemap = (Invoke-WebRequest $Sitemapurl).Content.TrimStart("ï»¿")
$locnodes = $sitemap.urlset.url.loc.TrimEnd()

# Function: For each URL in sitemap, return status code and canonical tag.
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

# Run program, save results in CSV file.
$locnodes | Check-Sitemap | Export-CSV $target -NoTypeInformation
