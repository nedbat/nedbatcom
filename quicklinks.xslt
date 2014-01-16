<?xml version='1.0' encoding='UTF-8'?>
<!-- Convert quick.qx to a blog entry. -->
<xsl:stylesheet
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    version="1.0"

    xmlns:xuff='http://www.stellated.com/xuff'
    exclude-result-prefixes='xuff'
    >

    <xsl:output method='xml' indent='yes' />

    <xsl:template match='quickentries'>
        <file name='quick_{xuff:now()}.bx'>
            <blog>
                <entry when='{xuff:now()}'>
                    <title>
                        <xsl:text>Quick links: </xsl:text>
                        <xsl:for-each select='entry/@titleword'>
                            <xsl:if test='position() &gt; 1'>, </xsl:if>
                            <xsl:value-of select='.' />
                        </xsl:for-each>
                    </title>
                    <category>quick</category>
                    <body>
                        <xsl:for-each select='entry'>
                            <quick>
                                <a href='{@href}'><xsl:value-of select='@text' /></a>
                                <xsl:if test='@comment'>: </xsl:if>
                                <xsl:value-of select='@comment' />
                            </quick>
                        </xsl:for-each>
                    </body>
                </entry>
            </blog>
        </file>
    </xsl:template>

</xsl:stylesheet>
