from ingestion.metadata_parser import extract_metadata

sample_html = """
<html>
<body>
<table>
    <tr><th>DB Name</th><th>DB Id</th></tr>
    <tr><td>PROD_DB</td><td>12345</td></tr>
</table>
<table>
    <tr><th>Snap Id</th><th>Snap Time</th></tr>
    <tr><td>100</td><td>01-Jan-25 10:00:00</td></tr>
    <tr><td>101</td><td>01-Jan-25 11:00:00</td></tr>
</table>
</body>
</html>
"""

print(extract_metadata(sample_html))
