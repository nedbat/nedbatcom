<?xml version='1.0' encoding='UTF-8'?>
<!-- Tools for the body of pages -->
<xsl:stylesheet
	xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
	version="1.0"

	xmlns:xuff='http://www.stellated.com/xuff'
	exclude-result-prefixes='xuff'
	>

<xsl:param name='nophp' />

<xsl:include href='tools.xslt' />

<xsl:output
	method='html'
	indent='no'
	/>

<xsl:template match='body|page|description'>
	<xsl:apply-templates select='*' />
</xsl:template>


<xsl:template match='quick'>
	<p class='quick'>
		&#xb6;&#xa0;&#xa0;<xsl:apply-templates select='text()|*[name()!="via"]'/>
	</p>
</xsl:template>

<!-- A <more> section becomes a link with a count of other content. -->

<xsl:template match='more'>
	<xsl:if test='$blogmode="brief"'>
		<xsl:variable name='census' select='count(p|ul/li|ol/li|code|quote)' />

		<p class='more'>
			&#xbb;
			<a class='s' href='{$permaurl}#more'>
				<xsl:choose>
					<xsl:when test='@text'>
						<xsl:text> </xsl:text>
						<xsl:value-of select='@text'/>
					</xsl:when>
					<xsl:otherwise>
						<xsl:text> read more of: </xsl:text>
						<xsl:value-of select='$title'/>
					</xsl:otherwise>
				</xsl:choose>

				<xsl:text>... (</xsl:text>

				<xsl:choose>
					<xsl:when test='$census = 0'>
						<xsl:text>empty!</xsl:text>
					</xsl:when>
					<xsl:when test='$census = 1'>
						<xsl:text>1 paragraph</xsl:text>
					</xsl:when>
					<xsl:otherwise>
						<xsl:value-of select='$census' />
						<xsl:text> paragraphs</xsl:text>
					</xsl:otherwise>
				</xsl:choose>

				<xsl:text>)</xsl:text>
			</a>
		</p>
	</xsl:if>

	<xsl:if test='$blogmode="full"'>
		<a name='more'/>
		<xsl:apply-templates select='*' />
	</xsl:if>
</xsl:template>

</xsl:stylesheet>
