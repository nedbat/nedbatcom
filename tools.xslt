<?xml version='1.0' encoding='UTF-8'?>
<!-- Tools for the body of pages -->
<xsl:stylesheet
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    version="1.0"

    xmlns:xuff='http://www.stellated.com/xuff'
    exclude-result-prefixes='xuff'
    >

<!-- Pinpoint an element. -->
<xsl:template name='pinpoint'>
    <xsl:for-each select='ancestor::*'>
        <xsl:if test='position() &gt; 1'>/</xsl:if>
        <xsl:value-of select='name()'/>
        <xsl:if test='@name|@title|title|@id|@class'>
            <xsl:text>(</xsl:text>
            <xsl:value-of select='@name|@title|title|@id|@class'/>
            <xsl:text>)</xsl:text>
        </xsl:if>
    </xsl:for-each>
</xsl:template>

<!-- Check that we are in a block context. -->
<xsl:template name='checkblock'>
    <xsl:if test='parent::p'>
        <xsl:message>
            <xsl:text>Block element inside p: &lt;</xsl:text>
            <xsl:value-of select='name()'/>
            <xsl:text>&gt; at </xsl:text>
            <xsl:call-template name='pinpoint'/>
        </xsl:message>
    </xsl:if>
</xsl:template>

<!-- Make a URI from a potentially relative URI. -->
<xsl:template name='makeuri'>
    <xsl:param name='uri' />
    <xsl:value-of select='xuff:makeuri($base, string($uri), string($dpath))'/>
</xsl:template>

<!--
  - Tools for the bodies of pages.
  -->

<xsl:template match='@*'>
    <xsl:copy-of select='.' />
</xsl:template>

<!-- Inline HTML elements: copied through. -->
<xsl:template match='
        a|b|i|u|em|strong|br|sup|sub|tt|cite|
        table|tr|td|th|
        li|dt|dd|
        span|font|
        nobr|wbr|
        small|big|
        script|input|button|
        object|param|embed|iframe|
        style
        '>
    <xsl:copy>
        <xsl:apply-templates select='*|@*|text()' />
    </xsl:copy>
</xsl:template>

<!-- Block HTML elements: copied through. -->
<xsl:template match='
        p|ul|ol|dl|
        div|
        h1|h2|h3|h4|h5|h6|
        blockquote|form
        '>
    <xsl:call-template name='checkblock' />

    <xsl:copy>
        <!-- If we're the first p or h1 in a page and don't have a class, then add class='first'. -->
        <xsl:if test='parent::page'>
            <xsl:if test='not(@class)'>
                <xsl:if test='not(preceding-sibling::p|preceding-sibling::h1)'>
                    <xsl:attribute name='class'>first</xsl:attribute>
                </xsl:if>
            </xsl:if>
        </xsl:if>

        <!-- Give header tags an id as well. -->
        <xsl:if test='self::h1|self::h2|self::h3'>
            <xsl:if test='not(@id)'>
                <xsl:attribute name='id'>
                    <xsl:text>h_</xsl:text>
                    <xsl:value-of select='xuff:idfromtext(string(descendant-or-self::*))'/>
                </xsl:attribute>
            </xsl:if>
        </xsl:if>

        <xsl:apply-templates select='*|@*|text()' />
    </xsl:copy>
</xsl:template>

<xsl:template match='img'>
    <xsl:call-template name='do_img' />
</xsl:template>

<!-- <a> tags: Various link munging. -->
<xsl:template match='a'>
    <xsl:choose>
        <xsl:when test='@href'>
            <xsl:if test='string(@href)=""'>
                <xsl:message>
                    <xsl:text>Empty href on &lt;a&gt; tag at </xsl:text>
                    <xsl:call-template name='pinpoint'/>
                </xsl:message>
            </xsl:if>
            <xsl:if test='not(text()|*)'>
                <xsl:message>
                    <xsl:text>&lt;a&gt; tag with no content at </xsl:text>
                    <xsl:call-template name='pinpoint'/>
                </xsl:message>
            </xsl:if>

            <a>
                <xsl:choose>
                    <xsl:when test='starts-with(@href,"mailto:")'>
                        <xsl:attribute name='href'>
                            <xsl:text>javascript:nospam("</xsl:text>
                            <xsl:value-of select='substring-before(substring-after(@href, ":"), "@")' />
                            <xsl:text>","</xsl:text>
                            <xsl:value-of select='substring-after(@href, "@")' />
                            <xsl:text>");</xsl:text>
                        </xsl:attribute>
                    </xsl:when>
        
                    <xsl:when test='starts-with(@href,"http://") or starts-with(@href,"ftp://")'>
                        <xsl:attribute name='class'>offsite</xsl:attribute>
                        <xsl:attribute name='rel'>external</xsl:attribute>
                        <xsl:attribute name='href'><xsl:value-of select='@href'/></xsl:attribute>
                    </xsl:when>
        
                    <xsl:otherwise>
                        <xsl:attribute name='href'>
                            <xsl:call-template name='makeuri'>
                                <xsl:with-param name='uri' select='@href' />
                            </xsl:call-template>
                        </xsl:attribute>
                    </xsl:otherwise>
        
                </xsl:choose>
        
                <xsl:apply-templates select='*|@*[name()!="href"]|text()'/>
            </a>
        </xsl:when>

        <xsl:when test='@pref'>
            <a>
                <xsl:attribute name='href'>
                    <xsl:call-template name='makeuri'>
                        <xsl:with-param name='uri' select='concat(substring-before(@pref, ".px"), ".html")' />
                    </xsl:call-template>
                </xsl:attribute>
                <xsl:choose>
                    <xsl:when test='text()'>
                        <xsl:value-of select='text()'/>
                    </xsl:when>
                    <xsl:otherwise>
                        <xsl:value-of select='xuff:pathtitle(current()/@pref)' />
                    </xsl:otherwise>
                </xsl:choose>
            </a>
        </xsl:when>

        <xsl:otherwise>
            <xsl:message>
                <xsl:text>&lt;a&gt; tag with no known link at </xsl:text>
                <xsl:call-template name='pinpoint'/>
            </xsl:message>
        </xsl:otherwise>
    </xsl:choose>
</xsl:template>

<!-- Structural stuff: no-ops at this stage. -->
<xsl:template match='section|pagemenu'/>

<!-- Meta and pagelink tags should have been copied to the top. -->
<xsl:template match='meta|pagelink'/>

<!-- Not doing anything with these yet. -->
<xsl:template match='history|copyright'/>

<!-- A link to another of our own pages. -->
<xsl:template match='apage'>
    <a>
        <xsl:attribute name='href'>
            <xsl:call-template name='makeuri'>
                <xsl:with-param name='uri' select='concat(substring-before(@pref, ".px"), ".html")' />
            </xsl:call-template>
        </xsl:attribute>
        <xsl:choose>
            <xsl:when test='text()'>
                <xsl:value-of select='text()'/>
            </xsl:when>
            <xsl:otherwise>
                <xsl:value-of select='xuff:pathtitle(current()/@pref)' />
            </xsl:otherwise>
        </xsl:choose>
    </a>
</xsl:template>

<!-- Placeholders for later. -->
<xsl:template match='pagecomments'>
    <!--
    <xsl:choose>
        <xsl:when test='$nophp'>
            <div class='comments'>
                <h1>Comments (placeholder)</h1>
            </div>
        </xsl:when>
        <xsl:otherwise>
            <xsl:call-template name='php'>
                <xsl:with-param name='code'>
                    require_once('inc/reactor_class.php');
                    $ror = new Reactor();
                    $entryinfo = array();
                    $entryinfo["title"] = "<xsl:value-of select='xuff:phpquote(string(parent::page/@title))'/>";
                    $entryinfo["url"] = "<xsl:value-of select='xuff:phpquote(concat($base,$dpath))'/>";
                    $ror->HandlePostedComment($entryinfo);
                    echo $ror->RenderComments("<xsl:value-of select='$dpath'/>", 'inc/inlinecomment.html', $entryinfo);
                </xsl:with-param>
            </xsl:call-template>
        </xsl:otherwise>
    </xsl:choose>
    -->
</xsl:template>

<!-- Google ads, disabled for now. -->
<xsl:template match='googleads'>
    <xsl:variable name='channelname'>
        <xsl:choose>
            <xsl:when test='@channel'><xsl:value-of select='@channel' /></xsl:when>
            <xsl:otherwise>other</xsl:otherwise>
        </xsl:choose>
    </xsl:variable>

    <xsl:variable name='channelcode'>
        <xsl:value-of select='document("googlechannels.xml")//channel[@name=$channelname]/@code' />
    </xsl:variable>

    <xsl:if test='$channelcode=""'>
        <xsl:message>
            <xsl:text>Unknown google channel: </xsl:text>
            <xsl:value-of select='$channelname' />
            <xsl:text> at </xsl:text>
            <xsl:call-template name='pinpoint'/>
        </xsl:message>
    </xsl:if>

    <div class='googleads'>
        <!--
        <xsl:choose>
            <xsl:when test='$nophp'>
                (channel <xsl:value-of select='$channelname' />, <xsl:value-of select='$channelcode'/>)<br/>
                <img src='file:///c:/ned/web/stellated/googlead-placeholder.png' />
            </xsl:when>
            <xsl:otherwise>
                <script type="text/javascript">
                    google_ad_client = "pub-0161795002156348";
                    google_ad_width = 468;
                    google_ad_height = 60;
                    google_ad_format = "468x60_as";
                    google_ad_channel ="<xsl:value-of select='$channelcode'/>";
                    google_color_border = "2D5893";
                    google_color_bg = "99AACC";
                    google_color_link = "000000";
                    google_color_url = "000099";
                    google_color_text = "003366";
                </script>
                <script type='text/javascript' src='http://pagead2.googlesyndication.com/pagead/show_ads.js'/>
            </xsl:otherwise>
        </xsl:choose>
        -->
    </div>
</xsl:template>

<!-- Default: print a message. -->
<xsl:template match='*'>
    <xsl:message>Strange tag: <xsl:value-of select='name()'/></xsl:message>
</xsl:template>

<!-- Custom "symbols" -->
<xsl:template match='permalinksym'>(&#164;)</xsl:template>
<xsl:template match='nbsp'>&#160;</xsl:template>
<xsl:template match='chev'>&#187;</xsl:template>
<xsl:template match='middot'>&#183;</xsl:template>
<xsl:template match='space'><xsl:text> </xsl:text></xsl:template>
<xsl:template match='bullet'>&#x2022;</xsl:template>
<xsl:template match='times'>&#xd7;</xsl:template>
<xsl:template match='divide'>&#xf7;</xsl:template>
<xsl:template match='minus'>&#x2212;</xsl:template>
<xsl:template match='ltlt'>&#xab;</xsl:template>
<xsl:template match='gtgt'>&#xbb;</xsl:template>
<xsl:template match='emdash'>&#x2014;</xsl:template>
<xsl:template match='pilcrow'>&#xb6;</xsl:template>
<xsl:template match='degree'>&#xB0;</xsl:template>
<xsl:template match='logand'>&#8743;</xsl:template>
<xsl:template match='logor'>&#8744;</xsl:template>
<xsl:template match='logimpl'>&#8658;</xsl:template>
<xsl:template match='lognot'>&#172;</xsl:template>
<xsl:template match='half'>&#189;</xsl:template>
<xsl:template match='sup1'><sup>1</sup></xsl:template>
<xsl:template match='sup2'><sup>2</sup></xsl:template>
<xsl:template match='sup3'><sup>3</sup></xsl:template>

<xsl:template match='bulletsep'>
    <!-- Todo: how do I make this work with <bullet/> below instead of entities? -->
    <p class='bulletsep'>&#x2022;&#160;&#160;&#160;&#160;&#x2022;&#160;&#160;&#160;&#160;&#x2022;</p>
</xsl:template>

<!-- Includes -->
<xsl:template match='include'>
    <xsl:apply-templates select='document(@file)/*'/>
</xsl:template>

<!-- Code chunks: \n becomes <br/>, space becomes nbsp. -->
<xsl:template match='code'>
    <xsl:call-template name='checkblock'/>
    <blockquote class='code'>
        <xsl:if test='@name'>
            <p class='name'><xsl:value-of select='@name'/></p>
        </xsl:if>
        <code>
            <xsl:choose>
            <xsl:when test='@lang'>
                <xsl:value-of
                    disable-output-escaping='yes'
                    select='xuff:lexcode(string(text()), string(@lang), string(@number))'/>
            </xsl:when>
            <xsl:when test='starts-with(text(), "&#10;")'>
                <xsl:call-template name='code-replace'>
                    <xsl:with-param name='code' select='translate(substring-after(text(), "&#10;"), " ", "&#160;")'/>
                </xsl:call-template>
            </xsl:when>
            <xsl:otherwise>
                <xsl:call-template name='code-replace'>
                    <xsl:with-param name='code' select='translate(text(), " ", "&#160;")'/>
                </xsl:call-template>
            </xsl:otherwise>
            </xsl:choose>
        </code>
    </blockquote>
</xsl:template>

<xsl:template match='codeword'>
    <span class='codeword'>
        <xsl:call-template name='code-replace'>
            <xsl:with-param name='code' select='translate(text(), " ", "&#160;")'/>
        </xsl:call-template>
    </span>
</xsl:template>

<xsl:template name='code-replace'>
    <xsl:param name='code'/>

    <xsl:choose>
    <xsl:when test='contains($code,"&#10;")'>
        <!--<nobr>-->
        <xsl:value-of select='substring-before($code,"&#10;")'/>
        <!--</nobr>-->
        <br/>
        <xsl:call-template name='code-replace'>
            <xsl:with-param name='code'
                select='substring-after($code,"&#10;")'/>
        </xsl:call-template>
    </xsl:when>
    <xsl:otherwise>
        <!--<nobr>--><xsl:value-of select='$code'/><!--</nobr>-->
    </xsl:otherwise>
    </xsl:choose>
</xsl:template>

<xsl:template match='quotep'>
    <xsl:call-template name='checkblock'/>
    <blockquote><div><p>
        <xsl:apply-templates select='*|@style|text()'/>
    </p></div></blockquote>
</xsl:template>

<xsl:template match='quote'>
    <xsl:call-template name='checkblock'/>
    <blockquote><div>
        <xsl:apply-templates select='*|text()'/>
    </div></blockquote>
</xsl:template>

<xsl:template match='figurep'>
    <xsl:call-template name='checkblock'/>
    <p class='figure'>
        <xsl:choose>
            <xsl:when test='thumbnail|object|iframe'>
                <xsl:apply-templates select='*' />
            </xsl:when>
            <xsl:when test='@href'>
                <a href='{@href}'>
                    <xsl:call-template name='figurep_img'/>
                </a>
            </xsl:when>
            <xsl:when test='@isbn'>
                <a href='http://www.amazon.com/exec/obidos/redirect?tag=nedbatchelder-20&amp;path=tg/detail/-/{@isbn}'>
                    <xsl:call-template name='figurep_img'/>
                </a>
            </xsl:when>
            <xsl:otherwise>
                <xsl:call-template name='figurep_img'/>
            </xsl:otherwise>
        </xsl:choose>
    </p>
</xsl:template>

<xsl:template name='figurep_img'>
    <xsl:for-each select='img'>
        <xsl:call-template name='do_img' />
    </xsl:for-each>
</xsl:template>

<xsl:template name='do_img'>
    <xsl:param name='src' select='@src' />
    <xsl:param name='alt' select='@alt' />
    <xsl:param name='scale' select='@scale' />

    <!-- All <img> tags should have an alt= attribute. -->
    <xsl:if test='string(@alt)=""'>
        <xsl:message>
            <xsl:text>&lt;img&gt; tag with no alt at </xsl:text>
            <xsl:call-template name='pinpoint'/>
        </xsl:message>
    </xsl:if>

    <img>
        <xsl:attribute name='src'>
            <xsl:call-template name='makeuri'>
                <xsl:with-param name='uri' select='$src' />
            </xsl:call-template>
        </xsl:attribute>
        <xsl:attribute name='alt'>
            <xsl:value-of select='$alt' />
        </xsl:attribute>
        <xsl:if test='string(@width)=""'>
            <xsl:variable name='width' select='xuff:imgwidth(string($src), string($scale))' />
            <xsl:variable name='height' select='xuff:imgheight(string($src), string($scale))' />

            <xsl:if test='$width'>
                <xsl:attribute name='width'>
                    <xsl:value-of select='$width' />
                </xsl:attribute>
                <xsl:attribute name='height'>
                    <xsl:value-of select='$height' />
                </xsl:attribute>
            </xsl:if>
        </xsl:if>
        <!-- Copy other stuff that may already be on the tag. -->
        <xsl:apply-templates select='@align|@border|@width|@height|@class|@id|@title|@hspace|@vspace|@style' />
    </img>
</xsl:template>

<xsl:template match='box'>
    <xsl:call-template name='checkblock'/>
    <blockquote class='box'>
        <xsl:apply-templates select='*|@*|text()'/>
    </blockquote>
</xsl:template>

<xsl:template match='li/h'>
    <b><xsl:apply-templates/></b>
</xsl:template>

<xsl:template match='docinfo'>
    <xsl:call-template name='checkblock'/>
    <p class='docinfo'>
        <xsl:apply-templates select='*|text()'/>
    </p>
</xsl:template>

<xsl:template match='term'>
    <b class='term'><xsl:apply-templates select='*|text()'/></b>
</xsl:template>

<!--
  - PHP code (to execute, not display).
  -->

<xsl:template match='php'>
    <xsl:call-template name='php'>
        <xsl:with-param name='code' select='text()'/>
    </xsl:call-template>
</xsl:template>

<xsl:template name='php'>
    <xsl:param name='code'/>
    <xsl:choose>
        <xsl:when test='$nophp'>
            <xsl:comment>[PHP] <xsl:value-of select='$code'/></xsl:comment>
            <xsl:value-of select='@ifnot'/>
        </xsl:when>
        <xsl:otherwise>
            <xsl:text disable-output-escaping='yes'>&lt;?php </xsl:text>
            <xsl:value-of disable-output-escaping='yes' select='$code'/>
            <xsl:text disable-output-escaping='yes'> ?&gt;</xsl:text>
        </xsl:otherwise>
    </xsl:choose>
</xsl:template>

<!--
  - Links.  Convert .lx to .px
  -->

<xsl:template match='link'>
    <p><b><a href='{@href}'><xsl:copy-of select='title/*|title/text()'/></a></b>
    <xsl:if test='comment/*|comment/text()'>
        <xsl:text> - </xsl:text>
        <xsl:apply-templates select='comment/*|comment/text()' />
    </xsl:if>
    </p>
</xsl:template>

<!--
  - Thumbnails, linked to the picture.
  -->

<xsl:template match='thumbnail'>
    <xsl:if test='string(@alt)=""'>
        <xsl:message>
            <xsl:text>Missing alt on &lt;thumbnail&gt; tag at </xsl:text>
            <xsl:call-template name='pinpoint'/>
        </xsl:message>
    </xsl:if>

    <a>
        <xsl:attribute name='href'>
            <xsl:call-template name='makeuri'>
                <xsl:with-param name='uri' select='@href' />
            </xsl:call-template>
        </xsl:attribute>

        <xsl:call-template name='do_img'>
            <xsl:with-param name='src'>
                <xsl:value-of select='substring-before(@href,".")' />
                <xsl:text>_thumb.</xsl:text>
                <xsl:value-of select='substring-after(@href,".")' />
            </xsl:with-param>
        </xsl:call-template>

    </a>
</xsl:template>

<!--
  - Links to downloadable files.
  -->

<xsl:template match='download'>
    <i><xsl:text>Download:&#160;</xsl:text></i>
    <a href='{@path}'>
        <xsl:choose>
            <xsl:when test='@file'>
                <xsl:value-of select='@file'/>
            </xsl:when>
            <!-- A lame XSLT way to find the last component of the path... -->
            <xsl:when test='substring-after(substring-after(@path,"/"),"/")'>
                <xsl:value-of select='substring-after(substring-after(@path,"/"),"/")'/>
            </xsl:when>
            <xsl:when test='substring-after(@path,"/")'>
                <xsl:value-of select='substring-after(@path,"/")'/>
            </xsl:when>
            <xsl:otherwise>???</xsl:otherwise>
        </xsl:choose>
    </a>
    <br/>
</xsl:template>

<!--
  - Amazon links.
  -->

<xsl:template match='amusicsearch'>
    <a href='http://www.amazon.com/exec/obidos/redirect?link_code=ur2&amp;camp=1789&amp;tag=nedbatchelder-20&amp;creative=9325&amp;path=external-search%3Fsearch-type=ss%26keyword={text()}%26index=music'>
        <xsl:apply-templates />
    </a>
</xsl:template>

<xsl:template match='aartistglance'>
    <a href='http://www.amazon.com/exec/obidos/redirect?link_code=ur2&amp;camp=1789&amp;tag=nedbatchelder-20&amp;creative=9325&amp;path=tg/stores/artist/glance/-/{@amid}'>
        <xsl:apply-templates />
    </a>
</xsl:template>


<xsl:template match='abook'>
    <a href='http://www.amazon.com/exec/obidos/redirect?tag=nedbatchelder-20&amp;path=tg/detail/-/{@isbn}'>
        <xsl:apply-templates />
    </a>
</xsl:template>

<!-- Blog tools -->

<xsl:template name='catname'>

    <xsl:variable name='catid' select='text()' />
    <xsl:variable name='cat' select='$cats[@id=$catid]' />
    <xsl:variable name='tag'>
        <xsl:choose>
            <xsl:when test='$cat/tag'>
                <xsl:value-of select='$cat/tag' />
            </xsl:when>
            <xsl:otherwise>
                <xsl:value-of select='translate($cat/name, "ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz")' />
            </xsl:otherwise>
        </xsl:choose>
    </xsl:variable>

    <xsl:value-of select='$tag' />

</xsl:template>

<xsl:template name='cattag'>

    <xsl:variable name='catid' select='text()' />

    <a href='blog/tag_{$catid}.html'>
        <xsl:call-template name='catname'/>
    </a>

</xsl:template>

<!--
  - Insert a table of in-document links to the <h1> elements on the page.
  -->
<xsl:template match='h1links'>
    <ul>
        <xsl:for-each select='ancestor::page/h1'>
            <li>
                <a>
                    <xsl:attribute name='href'>
                        <xsl:value-of select='$dpath' />
                        <xsl:text>#h_</xsl:text>
                        <xsl:value-of select='xuff:idfromtext(string(descendant-or-self::*))'/>
                    </xsl:attribute>
                    <xsl:value-of select='text()' />
                </a>
            </li>
        </xsl:for-each>
    </ul>
</xsl:template>

<!--
  - Compute the least and greatest string
  -->
<xsl:template name='string_min'>
    <xsl:param name='nodes' select='/..' />
    <xsl:param name='default' select='"??"' />
    <xsl:choose>
            <xsl:when test='not($nodes)'><xsl:value-of select='$default'/></xsl:when>
            <xsl:otherwise>
                <xsl:for-each select='$nodes'>
                        <xsl:sort />
                        <xsl:if test='position() = 1'>
                            <xsl:value-of select='.' />
                        </xsl:if>
                </xsl:for-each>
            </xsl:otherwise>
    </xsl:choose>
</xsl:template>

<xsl:template name='string_max'>
    <xsl:param name='nodes' select='/..' />
    <xsl:param name='default' select='"??"' />
    <xsl:choose>
            <xsl:when test='not($nodes)'><xsl:value-of select='$default'/></xsl:when>
            <xsl:otherwise>
                <xsl:for-each select='$nodes'>
                        <xsl:sort order='descending'/>
                        <xsl:if test='position() = 1'>
                            <xsl:value-of select='.' />
                        </xsl:if>
                </xsl:for-each>
            </xsl:otherwise>
    </xsl:choose>
</xsl:template>

</xsl:stylesheet>
