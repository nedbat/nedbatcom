// recipe and code for TPT
function __TABBLO_TPT_LOAD() {
    Tabblo.embedded.sites.SettingsObject.preprocess.apply({
        Properties:
        {
            template: 'blog'
        },

        // content definition:
        Content:
        {
            'menu':        { match: 'css',  selector:'td#menu',             ignore: true },
            'grouping':    { match: 'css',  selector:'div.head',            recurse: true, ignore: true, continueHooks: true },
            'pagetitle':   { match: 'css',  selector:'span.headslug'        },
            'title':       { match: 'css',  selector:'h3.title'             },
            'text':        { match: 'css',  selector:'.blog-entry>p, .blog-entry>ul, .blog-entry>ol, .blog-entry>blockquote', outputTagToo: true, recurse: true },
            'logo':        { match: 'css',  selector:'#logo img',           nodeContentType: 'image' },
            'image':       { match: 'css',  selector:'.blog-entry img',     nodeContentType: 'image' },
            'date':        { match: 'css',  selector:'div.head p.date'      },
            'info':        { match: 'css',  selector:'div.foot span'        },
            'copyright':   { match: 'css',  selector:'p.copyright'          }
        }
    }, []);
    Tabblo.embedded.printabulous();
}

function TptIt() {
    var z=document.createElement('script');
    z.setAttribute('type','text/javascript');
    z.setAttribute('charset','utf-8');
    z.setAttribute('src','http://h30405.www3.hp.com/edit/tptboot/1.0');
    document.getElementsByTagName('body').item(0).appendChild(z);
}
