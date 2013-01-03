<?xml version='1.0' encoding='UTF-8'?>
<!-- Style RSS so that it is readable. -->
<xsl:stylesheet
	xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
	version="1.0"

  xmlns:rss="http://purl.org/rss/1.0/"
	xmlns:dc="http://purl.org/dc/elements/1.1/"
	xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
	>

<xsl:template match='/rdf:RDF'>
	<html>
		<head>
			<title>RSS feed for <xsl:value-of select='rss:channel/rss:description'/></title>
			<style type='text/css'>

			body {
				font-family: verdana, sans-serif;
				font-size: 80%; line-height: 1.45em;
			}

			h1, h2 {
				font-size: 100%;
			}

			.box {
				border: .25pt solid;
				border-color: #ccc #999 #999 #CCC;
				padding: .3em .6em;
				background-color: #ffc;
			}

			img {
				border: none;
			}
			</style>
		</head>
		<body>
			<xsl:if test='rss:image/*'>
				<p><img src='{rss:image/rss:url}' /></p>
			</xsl:if>

			<h1>RSS feed for <xsl:value-of select='rss:channel/rss:description'/></h1>

			<p class='box'>
					This is an RSS feed for
					<a href='{rss:channel/rss:link}'><xsl:value-of select='rss:channel/rss:title'/></a>.
					If you don't know what an RSS feed is, read the
					<a href='http://www.nedbatchelder.com/site/whatisrss.html'>What's RSS?</a> page.
					A link at the end of each post takes you to the full entry in the blog.
					If you want to read the whole blog, use the
					<a href='http://www.nedbatchelder.com/blog'>main blog</a> page.
			</p>

			<xsl:apply-templates select='rss:item' />

		</body>
	</html>
</xsl:template>

<xsl:template match='rss:item'>
	<h2>
		<a href='{rss:link}'>
			<xsl:value-of select='rss:title'/>
		</a>
	</h2>
	<xsl:value-of disable-output-escaping='yes' select='rss:description'/>
</xsl:template>

</xsl:stylesheet>
