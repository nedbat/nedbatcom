<?xml version='1.0' encoding='UTF-8'?>
<!-- Tools for the body of pages -->
<xsl:stylesheet
	xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
	version="1.0"

	xmlns:xuff='http://www.stellated.com/xuff'
	exclude-result-prefixes='xuff'
	>

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
<!-- This used to be a way to split long blog posts. we don't need it anymore -->

<xsl:template match='more'>
    <xsl:apply-templates select='*' />
</xsl:template>

</xsl:stylesheet>
