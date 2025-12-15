# Page Source of finviz.com

This document describes the structure of the HTML source code of [finviz.com](https://finviz.com), a popular financial visualization website. Understanding the page source can help developers and analysts extract data for analysis or build web scraping tools.


<!DOCTYPE html>
<html lang="en" class=" dark">
<head>
<title>Finviz - Stock Screener</title>
<meta charset="UTF-8"><meta name="viewport" content="width=1205"><meta name="description" content="Stock screener for investors and traders, financial visualizations.">

            <link rel="preload" href="/fonts/lato-v17-latin-ext_latin-regular.woff2" as="font" crossorigin>
            <link rel="preload" href="/fonts/lato-v17-latin-ext_latin-700.woff2" as="font" crossorigin>
            <link rel="preload" href="/fonts/lato-v17-latin-ext_latin-900.woff2" as="font" crossorigin>
            <link rel="preload" href="/fonts/finviz-sans-415-normal-latin.woff2" as="font" crossorigin>
            <link rel="preload" href="/fonts/finviz-sans-450-normal-latin.woff2" as="font" crossorigin>
            <link rel="preload" href="/fonts/finviz-sans-500-normal-latin.woff2" as="font" crossorigin>
            <link rel="preload" href="/fonts/finviz-sans-700-normal-latin.woff2" as="font" crossorigin>
        
            <script>
                window.notificationsArray = [];
                window.renderScriptNotLoaded = function () {};
                window.handleScriptNotLoaded = function (element) {
                    window.notificationsArray.push(element);
                    window.sentryDisabled = true;
                    window.handleScriptNotLoaded = function () {};
                };
            </script>
        <link rel="stylesheet" href="/assets/dist/redesign.96c95996.css" type="text/css" onerror="window.handleScriptNotLoaded(this)">
<link rel="stylesheet" href="/assets/dist/main.c6147a33.css" type="text/css" onerror="window.handleScriptNotLoaded(this)">
<link rel="icon" type="image/png" href="/favicon_2x.png" sizes="32x32">
<link rel="icon" type="image/png" href="/favicon.png" sizes="16x16">
<script async=true>
    !(function(q,_name){q[_name]=q[_name]||function k(){(k.q=k.q||[]).push(arguments)},q[_name].v=q[_name].v||2,q[_name].s="1";!(function(q,k,F,H){function m(F,H){try{m=q.localStorage,(F=JSON.parse(m[decodeURI(decodeURI('%67%25%365%25%37%34I%257%34e%6d'))]("_aQS01OUU2MkU1RURCQzRDMzUyMTIwQkM4ODYtMTE0")).lgk||[])&&(H=q[k].pubads())&&F.forEach((function(q){q&&q[0]&&H.setTargeting(q[0],q[1]||"")}))}catch(N){}var m}try{(H=q[k]=q[k]||{}).cmd=H.cmd||[],typeof H.pubads===F?m():typeof H.cmd.unshift===F?H.cmd.unshift(m):H.cmd.push(m)}catch(N){}})(window,decodeURI(decodeURI('%25%367o%25%36fg%256c%25%36%35%2574%256%31%25%36%37')),"function");;!(function(q){q.__admiral_getConsentForGTM=function(k){function F(q,F){k((function(q,k){const F=q&&q.purpose&&q.purpose.consents||{};return{adConsentGranted:k||!!F[1],adUserData:k||!!F[7],adPersonalization:k||!!F[3],analyticsConsentGranted:k||!!F[1],personalizationConsentGranted:k||!!F[5],functionalityConsentGranted:k||!1,securityConsentGranted:k||!0}})(q,!F))}q[_name]("after","cmp.loaded",(function(k){k&&k.tcData&&k.tcData.gdprApplies?(k.consentKnown&&F(k.tcData,!0),q[_name]("after","cmp.updated",(function(q){F(q.tcData,!0)}))):F({},!1)}))}})(window);})(window,decodeURI(decodeURI('a%256%34m%25%369%25%37%32%256%31l')));!(function(q,k,F,H){F=q.createElement(k),q=q.getElementsByTagName(k)[0],F.async=1,F.src="https://urbanlaurel.com/assets/js/q2o3um29vhadcznq.vendor.js",(H=0)&&H(F),q.parentNode.insertBefore(F,q)})(document,"script");;;!(function(q,k,F,H,m){function N(){for(var q=[],F=0;F<arguments.length;F++)q.push(arguments[F]);if(!q.length)return m;"ping"===q[0]?q[2]({gdprAppliesGlobally:!!k[decodeURI(decodeURI('_%25%35%66c%6d%25%37%30%254%37%25%364%25%370%257%32A%2570%25%370%256%63%2569%65%73%2547%256%63o%25%36%32%25%361%25%36%63%6c%79'))],cmpLoaded:!1,cmpStatus:"stub"}):q.length>0&&m.push(q)}function L(q){if(q&&q.data&&q.source){var H,m=q.source,N="__tcfapiCall",L="string"==typeof q.data&&q.data.indexOf(N)>=0;(H=L?((function(q){try{return JSON.parse(q)}catch(k){}})(q.data)||{})[N]:(q.data||{})[N])&&k[F](H.command,H.version,(function(q,k){var F={__tcfapiReturn:{returnValue:q,success:k,callId:H.callId}};m&&m.postMessage(L?JSON.stringify(F):F,"*")}),H.parameter)}}!(function t(){if(!k.frames[H]){var F=q.body;if(F){var m=q.createElement("iframe");m.style.display="none",m.name=H,F.appendChild(m)}else setTimeout(t,5)}})(),N.v=1,"function"!=typeof k[F]&&(k[F]=k[F]||N,k.addEventListener?k.addEventListener("message",L,!1):k.attachEvent&&k.attachEvent("onmessage",L))})(document,window,"__tcfapi","__tcfapiLocator",[]);;;!(function(q,k,F,H,m,N,L,t,A,K,R){function Y(){for(var q=[],k=arguments.length,F=0;F<k;F++)q.push(arguments[F]);var H,m=q[1],N=typeof m===L,t=q[2],Y={gppVersion:"1.1",cmpStatus:"stub",cmpDisplayStatus:"hidden",signalStatus:"not ready",supportedAPIs:["7:usnat"].reduce((function(q,k){return k&&q.push(k),q}),[]),cmpId:9,sectionList:[],applicableSections:[0],gppString:"",parsedSections:{}};function v(q){N&&m(q,!0)}switch(q[0]){case"ping":return v(Y);case"queue":return A;case"events":return K;case"addEventListener":return N&&(H=++R,K.push({id:H,callback:m,parameter:t})),v({eventName:"listenerRegistered",listenerId:H,data:!0,pingData:Y});case"removeEventListener":for(H=!1,F=0;F<K.length;F++)if(K[F].id===t){K.splice(F,1),H=!0;break}return v(H);case"hasSection":case"getSection":case"getField":return v(null);default:return void A.push(q)}}Y.v=2,typeof k[F]!==L&&(k[F]=k[F]||Y,k[t]&&k[t]("message",(function(q,H){var L="string"==typeof q.data;(H=L?((function(q){try{return JSON.parse(q)}catch(k){}})(q.data)||{})[m]:(q.data||{})[m])&&k[F](H.command,(function(k,F){var m={__gppReturn:{returnValue:k,success:F,callId:H.callId}};q.source&&q.source.postMessage(L?JSON.stringify(m):m,"*")}),N in H?H[N]:null,H.version||1)}),!1),(function v(){if(!k.frames[H]){var F=q.body;if(F){var m=q.createElement("iframe");m.style.display="none",m.name=H,F.appendChild(m)}else setTimeout(v,5)}})())})(document,window,"__gpp","__gppLocator","__gppCall","parameter","function","addEventListener",[],[],0);
    ;(function () {
        window.ic_privacySelectorLoaded = false;

        window.admiral("after", "candidate.dismissed", function () {
            if (window.checkBannersLoaded) checkBannersLoaded();
        });

        window.admiral("after", "cmp.loaded", function (eventArg) {
            console.log("Admiral CMP Loaded ", eventArg);
            if (eventArg.euVisitor) return;
            try {
                __gpp("addEventListener", function (tcData) {
                    window.ic_privacySelectorLoaded = true;
                });
            } catch (e) {
                console.error(e)
            }
        });
    })();
</script><script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){dataLayer.push(arguments);}
</script><script>
            FinvizSettings = {
                versionImages: 35,
                hasUserPremium: false,
                name: "",
                email: "",
                nodeChartsDomain: "https://charts2-node.finviz.com",
                hasUserStickyHeader: false,
                adsProvider: 1,
                hasRedesignEnabled: true,
                hasRedesignPortfolio: false,
                hasDarkTheme: true,
                quoteSearchExt: '',
                isJoinBannerVisible: false,
                hasKnowledgeBase: false,
                hasNewComparePerf: false,
                hasCustomColumns: false,
                hasBFPromo: false,
                featureFlags: {"redesign":true,"stockswhymoving":true}
            };
        </script><script src="/assets/dist/script/browser_check.v1.7d9dede5.js"></script><script src="/assets/dist/script/notice.v1.ae659f43.js" onerror="window.handleScriptNotLoaded(this)"></script><script src="/assets/dist/script/vendor/boxover.v1.202b25a7.js" defer></script>
<script src="/assets/dist/runtime.v1.448bed6c.js" onerror="window.handleScriptNotLoaded(this)"></script><script src="/assets/dist/libs_init.v1.d9a4b671.js" onerror="window.handleScriptNotLoaded(this)"></script><script src="/assets/dist/7470.v1.3421c138.js" onerror="window.handleScriptNotLoaded(this)"></script><script src="/assets/dist/3772.v1.b198d5a5.js" onerror="window.handleScriptNotLoaded(this)"></script><script src="/assets/dist/877.v1.3af58ae5.js" onerror="window.handleScriptNotLoaded(this)"></script><script src="/assets/dist/8949.v1.494e6780.js" onerror="window.handleScriptNotLoaded(this)"></script><script src="/assets/dist/7052.v1.828e2e50.js" onerror="window.handleScriptNotLoaded(this)"></script><script src="/assets/dist/2698.v1.5f6434e5.js" onerror="window.handleScriptNotLoaded(this)"></script><script src="/assets/dist/header.v1.7e8eaf94.js" onerror="window.handleScriptNotLoaded(this)"></script><script id="refresh-init" type="application/json">{ "userId": "-1", "version": 16, "interval": 60, "hasGeoMaps": false }</script><script src="/assets/dist/script/recent_quotes_skeleton.v1.9193896e.js" onerror="window.handleScriptNotLoaded(this)"></script><link rel="preload" as="script" href="/assets/dist/map_base_index_redesign.v1.1efffbf6.js" data-chunk-id="map_base_index_redesign"><script type="text/javascript">
                if (window.location.search.indexOf('do_not_sell') >= 0) {
                  window.__tcfapi('addEventListener', 2, function (tcData) {
                    if (tcData.eventStatus === 'useractioncomplete' || tcData.eventStatus === 'tcloaded') {
                      window.__uspapi('displayUspUi')
                    }
                  })
                }
            </script><script type="text/javascript">
            function handleCloseGuidedTourClick(input) {
                fetch('/api/set_cookie.ashx?cookie=guidedTourSeenAt')
                    .catch(function(){})
                    .then(function(){ location.reload() })
            }
        </script></head>

          <script>
            const channelIdToLabel = {
                '1': 'MarketWatch',
                '2': 'WSJ',
                '3': 'Reuters',
                '4': 'Yahoo Finance',
                '5': 'CNN',
                '6': 'The New York Times',
                '7': 'Bloomberg',
                '9': 'BBC',
                '10': 'CNBC',
                '11': 'Fox Business',
                '102': 'Mish\'s Global Economic Trend Analysis',
                '105': 'Trader Feed',
                '113': 'Howard Lindzon',
                '114': 'Seeking Alpha',
                '123': 'Fallond Stock Picks',
                '132': 'Zero Hedge',
                '133': 'market folly',
                '136': 'Daily Reckoning',
                '141': 'Abnormal Returns',
                '142': 'Calculated Risk',
            }
            function trackAndOpenNews(event, channel, url) {
              event.preventDefault()
              window.open(url, '_blank')

              let channelLabel
              if (typeof channel === 'string') {
                const isInternalNewsUrl = url.startsWith('/news/')
                channelLabel = isInternalNewsUrl ? 'internal-' + channel : channel
              } else {
                const label = channelIdToLabel[channel]
                channelLabel = label !== undefined ? label : channel
              }
              window.gtag && window.gtag('event', 'click', {
                send_to: 'G-ZT9VQEWD4N',
                non_interaction: true,
                event_category: 'news',
                event_label: channelLabel,
                value: 1 });
            }
          </script>
          <body class="m-0 is-index chart-tooltip">
            <script>
                window.adLayoutVersion = 'control';
                window.adLoggedIn = 'NotLoggedIn';

                var cookieName = 'fv_block';
                var selector = '[data-google-query-id]';
                var selectorFrame = selector + ' iframe, ' + selector + ' [id*=aax]';
                var cookieExpiry = 5 * 60 * 1000; // 5min
                var checkTimeout = 20 * 1000; // 20sec

                function getCookie(value) {
                    var expiration = +new Date() + cookieExpiry;
                    return cookieName + '=' + value + '; expires=' + (new Date(expiration)).toUTCString() + '; path=/';
                }

                var finvizBannersLoaded = false;
                function loadFinvizBanners(setCookie) {
                    
                    if (setCookie) document.cookie = getCookie('block');
                    finvizBannersLoaded = true;
                    var s = document.createElement('script');
                    s.type = 'text/javascript';
                    s.async = true;
                    s.src = '/assets/dist/script/finviz_b.v1.d6c84ef3.js';
                    document.head.appendChild(s);
                }

                function checkBannersLoaded() {
                    var checkEnd = +new Date() + checkTimeout;
                    function asyncCheckIfExists(selector, resolve) {
                        var now = +new Date();
                        var container = document.querySelector(selector);
                        if (!container && checkEnd > now) return setTimeout(function () { asyncCheckIfExists(selector, resolve) }, 1000)
                        resolve(!!container);
                    }

                    asyncCheckIfExists(selector, function (exists) {
                        if (!exists) return loadFinvizBanners(true);

                        asyncCheckIfExists(selectorFrame, function (hasIframe) {
                            if (!hasIframe) return loadFinvizBanners(true);
                        })
                    })
                }

                if (document.cookie.indexOf(cookieName) >= 0) {
                    loadFinvizBanners(false);
                } else {
                    var s = document.createElement('script');
                    s.type = 'text/javascript';
                    s.async = true;
                    s.onerror = loadFinvizBanners;
                    s.src = 'https://u5.investingchannel.com/static/uat.js';
                    document.head.appendChild(s);

                    InvestingChannelQueue = window.InvestingChannelQueue || [];
                    var ic_page;

                    function refreshAd(container, refreshes) {
                        var placementTag, adslot;
                        window.InvestingChannelQueue.push(function () {
                            var pubTags = ic_page.getPubTag.call(ic_page, container.id);
                            if (!pubTags) return;
                            var pubTag = pubTags[0];
                            placementTag = pubTag.mPlacements[0].mTagToRender;
                            adslot = pubTag.mPlacements[0].mPublisherKval.adslot[0];
                            // Update div ID
                            var id = container.id.split('_');
                            var numberOfDivs = document.querySelectorAll('[id*=' + id.slice(0, id.length - 1).join('_') + ']').length;
                            var newDivNumber = Number(id.pop()) + numberOfDivs * refreshes;
                            container.setAttribute('id', id.join('_') + '_' + newDivNumber);
                            // Destroy previous pubtag & reset container html (loading span)
                            pubTag.destroy();
                            container.innerHTML = '';
                        });
                        window.InvestingChannelQueue.push(function () {
                            if (!placementTag || !adslot) return
                            // Create new pub tag
                            var newTag;
                            var layoutId = placementTag.mNativeLayout ? placementTag.mNativeLayout.nativelayoutid : null;
                            if (layoutId) {
                                newTag = ic_page.defineNativeTag('finviz/' + placementTag.mTarget.dfpkeyname, placementTag.mAdSize, container.id, layoutId);
                                var nativeLayout, layoutData

                                try {
                                  nativeLayout = newTag.mPlacements[0].mTags[0].mNativeLayout;
                                } catch (e) {
                                    console.log(e.message)
                                }

                                try {
                                  layoutData = newTag.mTemplate.mNativeLayout[layoutId].Data
                                  if (layoutData && nativeLayout && !nativeLayout.layout) {
                                    newTag.mPlacements[0].mTags[0].mNativeLayout = layoutData
                                  }
                                } catch (e) {
                                    console.log(e.message)
                                }
                            } else {
                                newTag = ic_page.defineTag('finviz/' + placementTag.mTarget.dfpkeyname, placementTag.mAdSize, container.id);
                            }
                            // Set adslot param
                            newTag.setKval({ adslot: adslot });
                            newTag.setKval({ kw: 'ajax' });
                            newTag.render();
                        });
                    }

                    var refreshCount = 1;
                    function refreshAds(selectors) {
                        if (window.ic_page) {
                            document.querySelectorAll(selectors).forEach(function (element) {
                                try {
                                    refreshAd(element, refreshCount);
                                } catch (e) {
                                    console.log('Ad refresh error for:', element, e);
                                }
                            });
                            window.ic_page.loadMore();
                            refreshCount++;
                        }
                    }


                    InvestingChannelQueue.push(function() {
                        var icConfig = window['FINVIZ_IC_UAT_CONFIG'] = {};
                        
                        ic_page = InvestingChannel.UAT.Run('df0d0d52-cc7f-11e8-82a5-0abbb61c4a6a', icConfig);
                    });

                    var hash = null;
                    if (typeof hash === 'string') {
                      InvestingChannelQueue.push(function() {
                          if (ic_page) {
                              ic_page.setUser({'SHA256': hash}, 'hash', '');
                          }
                      });
                    }
                }
            </script>
            <script>
                (function () {
                    var detectionEl = document.createElement('div');
                    detectionEl.style.position='absolute';
                    detectionEl.style.overflow='scroll';
                    document.body.appendChild(detectionEl);
                    document.documentElement.style.setProperty('--fv-scrollbar-width', `${detectionEl.offsetWidth}px`);
                    document.body.removeChild(detectionEl);
                })()
            </script>
        <div id="notifications-container"></div><table class="header">
    <tr class="align-top">
        <td>
            <table class="header-container">
                <tr>
                    <td class="w-[30%]">
                        <table class="w-full">
                            <tr>
                                <td class="h-[50px] align-middle">
                                    <a href="/" class="logo"><svg width="225" height="32" class="block">
  <use href="/img/logo.svg#free" class="dark:hidden" />
  <use href="/img/logo.svg#free-dark" class="hidden dark:block" />
</svg></a>
                                </td>
                            </tr>
                            <tr>
                                <td id="search" style="padding-top: 7px">
                                    <div class="navbar-search-placeholder">
    <span class="icon-wrapper">
        <svg xmlns="http://www.w3.org/2000/svg" class="icon" fill="none" viewBox="0 0 24 24">
            <path d="M16.9 15.5l4 4c.2.2.1.5 0 .7l-.7.7a.5.5 0 01-.8 0l-4-4c0-.2-.2-.3-.3-.4l-.7-1a7 7 0 01-11.2-4 7 7 0 1112.2 3l1 .6.5.4zM5 10a5 5 0 1010 0 5 5 0 00-10 0z" />
        </svg>
    </span>
    <input placeholder="Search ticker, company or profile" class="search-input is-free"/>
</div>
                                </td>
                            </tr>
                        </table>
                    </td>
                    <td class="align-bottom pb-1">
                        <div id="microbar_position" class="hidden xl:flex items-center h-[37px] pl-2"><div>
                        <div id="IC_D_88x31_1"class="relative overflow-hidden flex items-center justify-center w-full mx-auto" style="width:88px;height:31px;max-height:31px"></div>
                        </div></div>
                    </td>
                    <td class="relative w-[730px] text-right">
                        <div id="banner_position" class="overflow-hidden absolute top-0 right-0 w-full h-[96px]">
                        <div id="IC_D_728x90_1"class="relative overflow-hidden flex items-center justify-center w-full mx-auto" style="width:728px;height:90px;max-height:90px"></div>
                        </div>
                    </td>
                </tr>
            </table>
        </td>
    </tr>
    <tr>
        <td class="w-[994px] leading-none" style="font-size:0">
            <img src="/gfx/nic2x2.gif" class="w-[994px] h-px" alt="">
        </td>
    </tr>
</table>
            <table class="navbar">
                <tr>
                    <td class="h-[30px]">
                        <table class="header-container">
                            <tr><td><a class="nav-link is-active is-first" href="/">Home</a></td><td><a class="nav-link" href="/news.ashx">News</a></td><td><a class="nav-link" href="/screener.ashx">Screener</a></td><td><a class="nav-link" href="/map.ashx">Maps</a></td><td><a class="nav-link" href="/groups.ashx">Groups</a></td><td><a class="nav-link" href="/portfolio.ashx">Portfolio</a></td><td><a class="nav-link" href="/insidertrading">Insider</a></td><td><a class="nav-link" href="/futures.ashx">Futures</a></td><td><a class="nav-link" href="/forex.ashx">Forex</a></td><td><a class="nav-link" href="/crypto.ashx">Crypto</a></td><td><a class="nav-link" href="/calendar/economic">Calendar</a></td><td class="hidden [@media(min-width:1150px)]:table-cell"><a class="nav-link" href="/elite?utm_source=finviz&utm_medium=banner&utm_campaign=main-navbar-backtests">Backtests</a></td><td><a class="nav-link is-elite" href="/elite">Pricing</a></td><td class="w-full relative"><div class="absolute bottom-0 left-0 right-0 top-0"><div id="time" class="pr-1"></div></div></td>
                    <td class="nav relative">
        <a data-testid="chart-layout-theme" href="#" class="!flex !bg-transparent !border-b-0 mt-1 !py-0 !px-1" style='border-left: 1px solid #444a57' title="Toggle Light/Dark mode" onclick="setChartThemeCookie('light', true)">
            <div class='relative box-content flex rounded-full w-10 h-5 border border-gray-750 bg-gray-800 text-white justify-end'>
                <div class='box-border w-1/2 rounded-full p-px border border-gray-800 bg-[#4c5261] flex justify-center items-center'>
                    <svg width="16" height="16" class="fill-current text-white inline-block -ml-px">
    <use href="/assets/dist-icons/icons.svg?rev=35#moonOutlined"/>
</svg>
                </div>
            </div>
            <span class='ml-1 select-none font-medium text-xs text-white'>Theme</span>
        </a>
    </td>
    
                <td>
                    <a href="/help/screener.ashx" class="nav-link is-help border-l border-[#444a57]"><span class="fa fa-question-circle"></span>Help</a>
                </td>
                <td><a href="/login" class="nav-link sign-in">Login</a></td>
                <td><a href="/register" class="nav-link sign-up">Register</a></td>
            
                            </tr>
                        </table>
                    </td>
                </tr>
            </table>
        
          <script>
            function reloadPage () { location.reload() }
            function setChartThemeCookie(chartsTheme) {
              fetch('/api/set_cookie.ashx?cookie=chartsTheme&value=' + chartsTheme ).catch(function(){}).then(function(){
                window.gtag && window.gtag('event', 'click', { event_category: 'theme', event_label: 'toggle', value: chartsTheme, event_callback: reloadPage });
                setTimeout(reloadPage,1000);
              })
            }
          </script><div class="content is-index"><div class="fv-container "><table width="100%" cellpadding="0" cellspacing="0" border="0">
<tr>
<td width="100%" style="position: relative">
<div id="scam-notice"></div>
<script id="why-stock-moving-init-data" type="application/json">{"whyMoving":{"id":72309,"ticker":"$MARKET","dateTime":"2025-12-12T20:45:37.65","headline":"Tech and AI stocks tumble as Broadcom warning sparks bubble fears, dragging Nasdaq to worst week in months","summary":null,"source":"market_summary","sentiment":"bad","catalyst":false,"bulletPointsList":["Nasdaq plunged 1.9%, marking its steepest weekly loss in months amid a broad tech and AI selloff","Broadcom dropped $219 billion in value after weak margin guidance and delayed AI revenue, triggering sector-wide declines","Semiconductors and megacaps including Nvidia, AMD, Palantir, and Micron led the downturn","S\u0026P 500 fell 1.1%, Dow lost 0.5%, and Russell 2000 slid 1.5% as investors rotated into value sectors like financials, industrials, and health care","Cannabis stocks such as Tilray surged 30-40% on reports of potential easing of federal marijuana restrictions","Lululemon and Rivian posted double-digit gains but failed to offset broad market weakness","Renewed AI bubble concerns and rising US yields fueled volatility, with traders eyeing next week\u0027s jobs, CPI, and central bank decisions"]},"whyMovingRatings":null}</script>

<div class="js-why-stock-moving-static fv-container flex items-center mb-2 mt-4">
    <div class="relative flex w-full flex-col border border-primary bg-primary p-1.5 text-sm rounded-md">
        <div class="flex items-start justify-between">
            <div class="inline-block pr-5 leading-relaxed"><span class="relative -top-px pr-1"><span><svg width="16" height="16" class="!inline-block text-muted-2">
    <use href="/assets/dist-icons/icons.svg?rev=35#aiGenerated"/>
</svg></span></span><span class="text-negative whitespace-nowrap pr-2">Dec 12, 8:45 PM</span><span>Tech and AI stocks tumble as Broadcom warning sparks bubble fears, dragging Nasdaq to worst week in months</span></div>
            <div class="mr-1 mt-[0.336rem] flex items-center gap-3 flex-shrink-0"><span style="width: 16px; height: 16px; display: inline-block;"></span><span style="width: 16px; height: 16px; display: inline-block;"></span></div>
        </div>
    </div>
</div>
<div class="js-why-stock-moving-root hidden mb-2"></div>
<div id="home_indexes" data-has-why-stock-moving="true" class="flex justify-around ml-[5%] mr-[5%] 3xl:justify-between 3xl:m-0  h-[220px]"></div>
<div id="homepage">
<script id="js-indices" type="application/json">{"^DJI":{"ticker":"^DJI","timeframe":"i10","volume":[-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1],"date":[1765549800,1765550400,1765551000,1765551600,1765552200,1765552800,1765553400,1765554000,1765554600,1765555200,1765555800,1765556400,1765557000,1765557600,1765558200,1765558800,1765559400,1765560000,1765560600,1765561200,1765561800,1765562400,1765563000,1765563600,1765564200,1765564800,1765565400,1765566000,1765566600,1765567200,1765567800,1765568400,1765569000,1765569600,1765570200,1765570800,1765571400,1765572000,1765572600],"open":[48788.219,48805.781,48859.191,48819.16,48771.941,48767.25,48668.441,48766.781,48753.391,48533.719,48470.52,48470.129,48470.191,48353.48,48407.641,48426.48,48470.352,48550.762,48470.199,48537.781,48550.012,48548.922,48539.039,48585.27,48560.219,48541.941,48542.059,48530.109,48469.922,48462.172,48457.281,48474.68,48488.711,48494.57,48526.051,48486.43,48449.422,48393.41,48453.609],"high":[48834.98,48886.859,48881.84,48846.328,48806.301,48777.031,48770.379,48798.98,48768.129,48572.879,48501.59,48484.672,48470.191,48446.469,48426.48,48504.691,48550.762,48573.43,48540.73,48566.641,48567.559,48555.32,48607.648,48585.27,48568.801,48560.898,48568.891,48530.109,48493.73,48474.922,48495.219,48497.84,48512.32,48528.672,48537.91,48500.02,48450.648,48486.281,48483.25],"low":[48755.84,48753.898,48818.922,48761.012,48710.129,48663.43,48652.211,48723.75,48513.422,48470.02,48429.672,48391.172,48335.68,48339.93,48362.41,48422.219,48466.609,48458.98,48447.52,48518.641,48513.148,48524.43,48532.59,48520.309,48516.789,48506.281,48515.539,48466.309,48450.48,48440.539,48457.281,48455.801,48479.48,48470.828,48481.27,48435.262,48376.441,48393.41,48436.262],"close":[48805.781,48859.191,48819.16,48771.941,48767.25,48668.441,48766.781,48753.391,48533.719,48470.52,48470.129,48470.191,48353.48,48407.641,48426.48,48470.352,48550.762,48470.199,48537.781,48550.012,48548.922,48539.039,48585.27,48560.219,48541.941,48542.059,48530.109,48469.922,48462.172,48457.281,48474.68,48488.711,48494.57,48526.051,48486.43,48449.422,48393.41,48453.609,48458.051],"lastOpen":null,"lastHigh":null,"lastLow":null,"lastClose":48458.051,"lastVolume":null,"dataId":null,"lastDate":20251212,"lastTime":null,"prevClose":48704.01171875,"afterClose":null,"afterChange":null,"afterTime":null,"relativeVolume":0.9407788667317818},"^GSPC":{"ticker":"^GSPC","timeframe":"i10","volume":[-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1],"date":[1765549800,1765550400,1765551000,1765551600,1765552200,1765552800,1765553400,1765554000,1765554600,1765555200,1765555800,1765556400,1765557000,1765557600,1765558200,1765558800,1765559400,1765560000,1765560600,1765561200,1765561800,1765562400,1765563000,1765563600,1765564200,1765564800,1765565400,1765566000,1765566600,1765567200,1765567800,1765568400,1765569000,1765569600,1765570200,1765570800,1765571400,1765572000,1765572600],"open":[6891.43,6898.83,6884.19,6886.34,6868.73,6869.92,6847.94,6859.84,6862.25,6828.25,6820.08,6817.4,6823.28,6806.01,6812.51,6814.88,6826.33,6839.05,6824.65,6836.75,6841.07,6836.99,6839.08,6850.14,6848.28,6846.83,6841.75,6836.06,6830.06,6826.96,6824.82,6826.64,6828.7,6829.97,6833.73,6828.43,6823.77,6813.73,6823.47],"high":[6899.55,6899.22,6890.69,6886.34,6875.35,6871,6861.53,6865.56,6864.13,6834.04,6826.74,6823.28,6823.28,6817.08,6814.91,6831.44,6839.05,6839.82,6836.81,6842.69,6841.55,6841.63,6853.69,6850.14,6849.02,6847.85,6845.48,6836.7,6832.68,6828.77,6830.42,6832.76,6831.72,6833.76,6834.8,6829.7,6824.52,6828.36,6827.76],"low":[6887.76,6884.19,6882.71,6866.42,6864.61,6847.24,6844.15,6854.19,6824.56,6816.87,6811.98,6807.16,6802.08,6802.48,6806.96,6814.45,6826.33,6824.28,6820.48,6835.17,6834.4,6834.3,6838.45,6842.22,6841.85,6837.81,6835.29,6830.06,6825.95,6822.79,6824.82,6826.39,6827.21,6825.84,6827.29,6821.75,6811.53,6813.73,6818.93],"close":[6898.83,6884.19,6886.34,6868.73,6869.92,6847.94,6859.84,6862.25,6828.25,6820.08,6817.4,6823.28,6806.01,6812.51,6814.88,6826.33,6839.05,6824.65,6836.75,6841.07,6836.99,6839.08,6850.14,6848.28,6846.83,6841.75,6836.06,6830.06,6826.96,6824.82,6826.64,6828.7,6829.97,6833.73,6828.43,6823.77,6813.73,6823.47,6827.41],"lastOpen":null,"lastHigh":null,"lastLow":null,"lastClose":6827.41,"lastVolume":null,"dataId":null,"lastDate":20251212,"lastTime":null,"prevClose":6901,"afterClose":null,"afterChange":null,"afterTime":null,"relativeVolume":0.9549940452658181},"^IXIC":{"ticker":"^IXIC","timeframe":"i10","volume":[-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1],"date":[1765549800,1765550400,1765551000,1765551600,1765552200,1765552800,1765553400,1765554000,1765554600,1765555200,1765555800,1765556400,1765557000,1765557600,1765558200,1765558800,1765559400,1765560000,1765560600,1765561200,1765561800,1765562400,1765563000,1765563600,1765564200,1765564800,1765565400,1765566000,1765566600,1765567200,1765567800,1765568400,1765569000,1765569600,1765570200,1765570800,1765571400,1765572000,1765572600],"open":[23489.127,23546.229,23450.781,23497.57,23389.805,23405.211,23299.137,23336.775,23357.064,23215.859,23177.467,23158.461,23182.498,23106.93,23141.596,23145.338,23206.078,23259.664,23196.598,23246.686,23274.949,23254.48,23264.871,23316.664,23305.035,23307.078,23285.051,23257.779,23233.297,23218.699,23209.691,23216.732,23223.322,23229.023,23239.105,23218.268,23197.516,23148.84,23182.727],"high":[23553.568,23546.229,23504.516,23497.57,23425.998,23408.42,23346.229,23369.469,23362.617,23239.834,23189.383,23183.613,23182.914,23156.602,23148.807,23225.199,23259.664,23260.982,23246.688,23279.107,23276.82,23272.971,23331.244,23316.664,23308.283,23310.895,23296.502,23261.656,23243.057,23228.104,23235.938,23244.207,23234.271,23239.105,23242.133,23220.924,23200.877,23204.555,23195.977],"low":[23486.146,23447.969,23446.402,23379.361,23385.359,23297.574,23281.766,23316.158,23199.406,23162.145,23137.645,23116.422,23106.93,23096.74,23121.076,23142.846,23206.078,23195.359,23176.539,23242.455,23249.471,23244.904,23264.119,23286.033,23283.941,23270.977,23254.678,23233.172,23215.447,23201.342,23209.691,23215.996,23217.643,23212.428,23210.756,23191.891,23141.309,23148.84,23157.086],"close":[23546.229,23450.781,23497.57,23389.805,23405.211,23299.137,23336.775,23357.064,23215.859,23177.467,23158.461,23182.498,23106.93,23141.596,23145.338,23206.078,23259.664,23196.598,23246.686,23274.949,23254.48,23264.871,23316.664,23305.035,23307.078,23285.051,23257.779,23233.297,23218.699,23209.691,23216.732,23223.322,23229.023,23239.105,23218.268,23197.516,23148.84,23182.727,23195.17],"lastOpen":null,"lastHigh":null,"lastLow":null,"lastClose":23195.17,"lastVolume":null,"dataId":null,"lastDate":20251212,"lastTime":null,"prevClose":23593.85546875,"afterClose":null,"afterChange":null,"afterTime":null,"relativeVolume":0.9761486674210605},"^RUT":{"ticker":"^RUT","timeframe":"i10","volume":[-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1],"date":[1765549800,1765550400,1765551000,1765551600,1765552200,1765552800,1765553400,1765554000,1765554600,1765555200,1765555800,1765556400,1765557000,1765557600,1765558200,1765558800,1765559400,1765560000,1765560600,1765561200,1765561800,1765562400,1765563000,1765563600,1765564200,1765564800,1765565400,1765566000,1765566600,1765567200,1765567800,1765568400,1765569000,1765569600,1765570200,1765570800,1765571400,1765572000,1765572600],"open":[257.95,257.78,257.46,257.29,256.99,257,256.22,256.22,256.66,255.32,254.75,254.54,254.82,253.69,254.07,253.86,254.4,255.1,254.33,254.89,255.31,255.18,255.265,255.69,255.46,255.38,255.36,255.14,254.72,254.62,254.54,254.46,254.53,254.45,254.505,254.36,253.895,253.44,254.01],"high":[258.2,258.044,257.9,257.345,257.48,257.09,256.57,256.81,256.72,255.75,255.11,254.835,254.82,254.25,254.09,254.71,255.155,255.25,254.9,255.43,255.4,255.33,255.9,255.69,255.57,255.46,255.52,255.21,254.92,254.79,254.77,254.79,254.63,254.51,254.57,254.455,253.93,254.33,254.12],"low":[257.5,257.44,257.19,256.685,256.49,256.19,256.05,255.815,254.94,254.72,254.36,254.12,253.585,253.51,253.55,253.73,254.38,254.255,254.095,254.8,255,254.99,255.22,255.285,255.25,255.05,255.07,254.705,254.55,254.38,254.42,254.395,254.32,254.25,254.275,253.84,253.45,253.44,253.67],"close":[257.775,257.47,257.3,257.02,257.02,256.23,256.22,256.62,255.33,254.75,254.54,254.82,253.69,254.08,253.9,254.41,255.08,254.36,254.885,255.304,255.16,255.275,255.685,255.46,255.37,255.37,255.15,254.715,254.62,254.54,254.42,254.54,254.41,254.5,254.345,253.9,253.45,253.99,253.85],"lastOpen":null,"lastHigh":null,"lastLow":null,"lastClose":253.85,"lastVolume":null,"dataId":null,"lastDate":20251212,"lastTime":null,"prevClose":257.79998779296875,"afterClose":null,"afterChange":null,"afterTime":null,"relativeVolume":0.8317238922894108}}</script><table width="100%" cellpadding="0" cellspacing="0" border="0">
<tr>
<td>
<table  width="100%" cellpadding="0" cellspacing="0" border="0">
<tr><td class="w-1/5" align="center" valign="top"><div class="market-stats" data-boxover="cssbody=[tooltip_short_bdy] cssheader=[tooltip_short_hdr] body=[Total <b>Advancing / Declining</b> issues on NYSE, Nasdaq and AMEX] offsetx=[0] offsety=[20] delay=[100]">
            <div class="market-stats_labels">
                <div class="market-stats_labels_left"><p>Advancing</p><p>33.0% (1832)</p></div>
                
                <div class="market-stats_labels_right"><p>Declining</p><p>(3490) 62.8%</p></div>
            </div>
            <div class="market-stats_bar">
                <div class="market-stats_bar_left-bar" style="width: 33.0%"></div>
                <div class="market-stats_bar_center-bar" style="width: 4.2%"></div>
                <div class="market-stats_bar_right-bar" style="width: 62.8%"></div>
            </div>
        </div></td>
<td class="w-1/5" align="center" valign="top"><div class="market-stats" data-boxover="cssbody=[tooltip_short_bdy] cssheader=[tooltip_short_hdr] body=[Total <b>New High / New Low</b> issues on NYSE, Nasdaq and AMEX] offsetx=[0] offsety=[20] delay=[100]">
            <div class="market-stats_labels">
                <div class="market-stats_labels_left"><p>New High</p><p>72.0% (299)</p></div>
                
                <div class="market-stats_labels_right"><p>New Low</p><p>(116) 28.0%</p></div>
            </div>
            <div class="market-stats_bar">
                <div class="market-stats_bar_left-bar" style="width: 72.0%"></div>
                <div class="market-stats_bar_center-bar" style="width: 0.0%"></div>
                <div class="market-stats_bar_right-bar" style="width: 28.0%"></div>
            </div>
        </div></td>
<td class="w-1/5" align="center" valign="top"><div class="market-stats" data-boxover="cssbody=[tooltip_short_bdy] cssheader=[tooltip_short_hdr] body=[Total <b>Above SMA50 / Below SMA50</b> issues on NYSE, Nasdaq and AMEX] offsetx=[0] offsety=[20] delay=[100]">
            <div class="market-stats_labels">
                <div class="market-stats_labels_left"><p>Above</p><p>52.1% (2888)</p></div>
                SMA50
                <div class="market-stats_labels_right"><p>Below</p><p>(2650) 47.9%</p></div>
            </div>
            <div class="market-stats_bar">
                <div class="market-stats_bar_left-bar" style="width: 52.1%"></div>
                <div class="market-stats_bar_center-bar" style="width: 0.0%"></div>
                <div class="market-stats_bar_right-bar" style="width: 47.9%"></div>
            </div>
        </div></td>
<td class="w-1/5" align="center" valign="top"><div class="market-stats" data-boxover="cssbody=[tooltip_short_bdy] cssheader=[tooltip_short_hdr] body=[Total <b>Above SMA200 / Below SMA200</b> issues on NYSE, Nasdaq and AMEX] offsetx=[0] offsety=[20] delay=[100]">
            <div class="market-stats_labels">
                <div class="market-stats_labels_left"><p>Above</p><p>54.7% (3028)</p></div>
                SMA200
                <div class="market-stats_labels_right"><p>Below</p><p>(2510) 45.3%</p></div>
            </div>
            <div class="market-stats_bar">
                <div class="market-stats_bar_left-bar" style="width: 54.7%"></div>
                <div class="market-stats_bar_center-bar" style="width: 0.0%"></div>
                <div class="market-stats_bar_right-bar" style="width: 45.3%"></div>
            </div>
        </div></td>
<td class="w-1/5" valign="top" align="center" height="40"><div id="js-market-sentiment" class="market-sentiment"></div></td>
</tr>
</table>
</td>
</tr>
<tr>
<div id="js-switches-root"></div><td style="padding-top: 2px" align="center">
<table width="100%" cellpadding="0" cellspacing="0" border="0" class="table-fixed">
<tr>
<td width="50%" valign="top">
<table width="100%" cellpadding="1" cellspacing="0" class="styled-table-new is-rounded is-condensed is-tabular-nums" border="0">
<thead>
<tr>
<th class="text-left">Ticker</th><th align="right">Last</th><th align="right">Change</th><th align="right">Volume</th><th><img src="gfx/nic2x2.gif" style="width:4px;height:2px" alt="" border="0"></th><th class="text-left" style="width: 35%;"><div class="flex justify-between items-center"><span>Signal</span><span class="js-signal-switch"><button class="fv-button js-signal-switch-button ml-1 is-xsmall is-border is-link">
    Daily
    <svg width="16" height="16" class="ml-0.5 -mr-0.5">
    <use href="/assets/dist-icons/icons.svg?rev=35#chevronDown"/>
</svg>
</button</span></div></th>
</tr></thead>
<tbody id="js-signals_1">
<tr class="styled-row is-hoverable is-bordered is-rounded has-color-text cursor-pointer" onclick="window.location='screener.ashx?v=340&s=ta_topgainers'">
<td data-boxover="cssbody=[hoverchart] cssheader=[tabchrthdr] body=[<img  srcset='https://charts2-node.finviz.com/chart.ashx?cs=m&t=YCBD&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d 1x, https://charts2-node.finviz.com/chart.ashx?cs=m&t=YCBD&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&sf=2 2x' width='324' height='180' alt='' loading='lazy'><div><b>cbdMD Inc</b>Drug Manufacturers - Specialty & Generic <span>•</span> USA <span>•</span> 10.70M </div>] offsetx=[200] offsety=[-95] delay=[250]"><a href="quote.ashx?t=YCBD" class="tab-link">YCBD</a></td><td align="right">1.20</td><td align="right" style="white-space:nowrap"><span class="color-text is-positive">90.17%</span></td><td align="right">299.04M</td><td></td><td data-boxover="cssbody=[tooltip_short_bdy] cssheader=[tooltip_short_hdr] body=[Stocks with the highest price gain today] offsetx=[10] offsety=[20] delay=[300]"><a href="screener.ashx?v=340&s=ta_topgainers" class="tab-link-nw">Top Gainers</a></td>
</tr>
<tr class="styled-row is-hoverable is-bordered is-rounded has-color-text cursor-pointer" onclick="window.location='screener.ashx?v=340&s=ta_topgainers'">
<td data-boxover="cssbody=[hoverchart] cssheader=[tabchrthdr] body=[<img  srcset='https://charts2-node.finviz.com/chart.ashx?cs=m&t=THH&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d 1x, https://charts2-node.finviz.com/chart.ashx?cs=m&t=THH&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&sf=2 2x' width='324' height='180' alt='' loading='lazy'><div><b>TryHard Holdings Ltd</b>Specialty Business Services <span>•</span> Japan <span>•</span> 776.78M </div>] offsetx=[200] offsety=[-95] delay=[250]"><a href="quote.ashx?t=THH" class="tab-link">THH</a></td><td align="right">15.52</td><td align="right" style="white-space:nowrap"><span class="color-text is-positive">57.72%</span></td><td align="right">473.36K</td><td></td><td data-boxover="cssbody=[tooltip_short_bdy] cssheader=[tooltip_short_hdr] body=[Stocks with the highest price gain today] offsetx=[10] offsety=[20] delay=[300]"><a href="screener.ashx?v=340&s=ta_topgainers" class="tab-link-nw">Top Gainers</a></td>
</tr>
<tr class="styled-row is-hoverable is-bordered is-rounded has-color-text cursor-pointer" onclick="window.location='screener.ashx?v=340&s=ta_topgainers'">
<td data-boxover="cssbody=[hoverchart] cssheader=[tabchrthdr] body=[<img  srcset='https://charts2-node.finviz.com/chart.ashx?cs=m&t=NCI&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d 1x, https://charts2-node.finviz.com/chart.ashx?cs=m&t=NCI&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&sf=2 2x' width='324' height='180' alt='' loading='lazy'><div><b>Neo Concept International Group Holdings Ltd</b>Apparel Manufacturing <span>•</span> Hong Kong <span>•</span> 7.80M </div>] offsetx=[200] offsety=[-95] delay=[250]"><a href="quote.ashx?t=NCI" class="tab-link">NCI</a></td><td align="right">1.92</td><td align="right" style="white-space:nowrap"><span class="color-text is-positive">54.84%</span></td><td align="right">33.75M</td><td></td><td data-boxover="cssbody=[tooltip_short_bdy] cssheader=[tooltip_short_hdr] body=[Stocks with the highest price gain today] offsetx=[10] offsety=[20] delay=[300]"><a href="screener.ashx?v=340&s=ta_topgainers" class="tab-link-nw">Top Gainers</a></td>
</tr>
<tr class="styled-row is-hoverable is-bordered is-rounded has-color-text cursor-pointer" onclick="window.location='screener.ashx?v=340&s=ta_topgainers'">
<td data-boxover="cssbody=[hoverchart] cssheader=[tabchrthdr] body=[<img  srcset='https://charts2-node.finviz.com/chart.ashx?cs=m&t=CGC&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d 1x, https://charts2-node.finviz.com/chart.ashx?cs=m&t=CGC&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&sf=2 2x' width='324' height='180' alt='' loading='lazy'><div><b>Canopy Growth Corporation</b>Drug Manufacturers - Specialty & Generic <span>•</span> Canada <span>•</span> 595.43M </div>] offsetx=[200] offsety=[-95] delay=[250]"><a href="quote.ashx?t=CGC" class="tab-link">CGC</a></td><td align="right">1.74</td><td align="right" style="white-space:nowrap"><span class="color-text is-positive">53.98%</span></td><td align="right">159.37M</td><td></td><td data-boxover="cssbody=[tooltip_short_bdy] cssheader=[tooltip_short_hdr] body=[Stocks with the highest price gain today] offsetx=[10] offsety=[20] delay=[300]"><a href="screener.ashx?v=340&s=ta_topgainers" class="tab-link-nw">Top Gainers</a></td>
</tr>
<tr class="styled-row is-hoverable is-bordered is-rounded has-color-text cursor-pointer" onclick="window.location='screener.ashx?v=340&s=ta_topgainers'">
<td data-boxover="cssbody=[hoverchart] cssheader=[tabchrthdr] body=[<img  srcset='https://charts2-node.finviz.com/chart.ashx?cs=m&t=RYM&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d 1x, https://charts2-node.finviz.com/chart.ashx?cs=m&t=RYM&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&sf=2 2x' width='324' height='180' alt='' loading='lazy'><div><b>RYTHM Inc</b>Tobacco <span>•</span> USA <span>•</span> 47.66M </div>] offsetx=[200] offsety=[-95] delay=[250]"><a href="quote.ashx?t=RYM" class="tab-link">RYM</a></td><td align="right">23.80</td><td align="right" style="white-space:nowrap"><span class="color-text is-positive">47.73%</span></td><td align="right">3.29M</td><td></td><td data-boxover="cssbody=[tooltip_short_bdy] cssheader=[tooltip_short_hdr] body=[Stocks with the highest price gain today] offsetx=[10] offsety=[20] delay=[300]"><a href="screener.ashx?v=340&s=ta_topgainers" class="tab-link-nw">Top Gainers</a></td>
</tr>
<tr class="styled-row is-hoverable is-bordered is-rounded has-color-text cursor-pointer" onclick="window.location='screener.ashx?v=340&s=ta_topgainers'">
<td data-boxover="cssbody=[hoverchart] cssheader=[tabchrthdr] body=[<img  srcset='https://charts2-node.finviz.com/chart.ashx?cs=m&t=TLRY&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d 1x, https://charts2-node.finviz.com/chart.ashx?cs=m&t=TLRY&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&sf=2 2x' width='324' height='180' alt='' loading='lazy'><div><b>Tilray Brands Inc</b>Drug Manufacturers - Specialty & Generic <span>•</span> Canada <span>•</span> 1.41B </div>] offsetx=[200] offsety=[-95] delay=[250]"><a href="quote.ashx?t=TLRY" class="tab-link">TLRY</a></td><td align="right">12.15</td><td align="right" style="white-space:nowrap"><span class="color-text is-positive">44.13%</span></td><td align="right">80.74M</td><td></td><td data-boxover="cssbody=[tooltip_short_bdy] cssheader=[tooltip_short_hdr] body=[Stocks with the highest price gain today] offsetx=[10] offsety=[20] delay=[300]"><a href="screener.ashx?v=340&s=ta_topgainers" class="tab-link-nw">Top Gainers</a></td>
</tr>
<tr class="styled-row is-hoverable is-bordered is-rounded has-color-text cursor-pointer" onclick="window.location='screener.ashx?v=340&s=ta_newhigh'">
<td data-boxover="cssbody=[hoverchart] cssheader=[tabchrthdr] body=[<img  srcset='https://charts2-node.finviz.com/chart.ashx?cs=m&t=FEIM&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d 1x, https://charts2-node.finviz.com/chart.ashx?cs=m&t=FEIM&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&sf=2 2x' width='324' height='180' alt='' loading='lazy'><div><b>Frequency Electronics, Inc</b>Communication Equipment <span>•</span> USA <span>•</span> 452.85M </div>] offsetx=[200] offsety=[-95] delay=[250]"><a href="quote.ashx?t=FEIM" class="tab-link">FEIM</a></td><td align="right">46.45</td><td align="right" style="white-space:nowrap"><span class="color-text is-positive">28.81%</span></td><td align="right">1.18M</td><td></td><td data-boxover="cssbody=[tooltip_short_bdy] cssheader=[tooltip_short_hdr] body=[Stocks making new 52 weeks high today] offsetx=[10] offsety=[20] delay=[300]"><a href="screener.ashx?v=340&s=ta_newhigh" class="tab-link-nw">New High</a></td>
</tr>
<tr class="styled-row is-hoverable is-bordered is-rounded has-color-text cursor-pointer" onclick="window.location='screener.ashx?v=340&s=ta_newhigh'">
<td data-boxover="cssbody=[hoverchart] cssheader=[tabchrthdr] body=[<img  srcset='https://charts2-node.finviz.com/chart.ashx?cs=m&t=KYTX&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d 1x, https://charts2-node.finviz.com/chart.ashx?cs=m&t=KYTX&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&sf=2 2x' width='324' height='180' alt='' loading='lazy'><div><b>Kyverna Therapeutics Inc</b>Biotechnology <span>•</span> USA <span>•</span> 384.53M </div>] offsetx=[200] offsety=[-95] delay=[250]"><a href="quote.ashx?t=KYTX" class="tab-link">KYTX</a></td><td align="right">8.78</td><td align="right" style="white-space:nowrap"><span class="color-text is-positive">5.02%</span></td><td align="right">1.10M</td><td></td><td data-boxover="cssbody=[tooltip_short_bdy] cssheader=[tooltip_short_hdr] body=[Stocks making new 52 weeks high today] offsetx=[10] offsety=[20] delay=[300]"><a href="screener.ashx?v=340&s=ta_newhigh" class="tab-link-nw">New High</a></td>
</tr>
<tr class="styled-row is-hoverable is-bordered is-rounded has-color-text cursor-pointer" onclick="window.location='screener.ashx?v=340&s=ta_newhigh'">
<td data-boxover="cssbody=[hoverchart] cssheader=[tabchrthdr] body=[<img  srcset='https://charts2-node.finviz.com/chart.ashx?cs=m&t=CDNL&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d 1x, https://charts2-node.finviz.com/chart.ashx?cs=m&t=CDNL&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&sf=2 2x' width='324' height='180' alt='' loading='lazy'><div><b>Cardinal Infrastructure Group Inc</b>Engineering & Construction <span>•</span> USA <span>•</span> - </div>] offsetx=[200] offsety=[-95] delay=[250]"><a href="quote.ashx?t=CDNL" class="tab-link">CDNL</a></td><td align="right">29.65</td><td align="right" style="white-space:nowrap"><span class="color-text is-positive">17.15%</span></td><td align="right">837.93K</td><td></td><td data-boxover="cssbody=[tooltip_short_bdy] cssheader=[tooltip_short_hdr] body=[Stocks making new 52 weeks high today] offsetx=[10] offsety=[20] delay=[300]"><a href="screener.ashx?v=340&s=ta_newhigh" class="tab-link-nw">New High</a></td>
</tr>
<tr class="styled-row is-hoverable is-bordered is-rounded has-color-text cursor-pointer" onclick="window.location='screener.ashx?v=340&s=ta_newhigh'">
<td data-boxover="cssbody=[hoverchart] cssheader=[tabchrthdr] body=[<img  srcset='https://charts2-node.finviz.com/chart.ashx?cs=m&t=PPIH&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d 1x, https://charts2-node.finviz.com/chart.ashx?cs=m&t=PPIH&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&sf=2 2x' width='324' height='180' alt='' loading='lazy'><div><b>Perma-Pipe International Holdings Inc</b>Building Products & Equipment <span>•</span> USA <span>•</span> 263.78M </div>] offsetx=[200] offsety=[-95] delay=[250]"><a href="quote.ashx?t=PPIH" class="tab-link">PPIH</a></td><td align="right">32.59</td><td align="right" style="white-space:nowrap"><span class="color-text is-positive">11.27%</span></td><td align="right">286.06K</td><td></td><td data-boxover="cssbody=[tooltip_short_bdy] cssheader=[tooltip_short_hdr] body=[Stocks making new 52 weeks high today] offsetx=[10] offsety=[20] delay=[300]"><a href="screener.ashx?v=340&s=ta_newhigh" class="tab-link-nw">New High</a></td>
</tr>
<tr class="styled-row is-hoverable is-bordered is-rounded has-color-text cursor-pointer" onclick="window.location='screener.ashx?v=210&s=ta_overbought'">
<td data-boxover="cssbody=[hoverchart] cssheader=[tabchrthdr] body=[<img  srcset='https://charts2-node.finviz.com/chart.ashx?cs=m&t=EXAS&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d 1x, https://charts2-node.finviz.com/chart.ashx?cs=m&t=EXAS&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&sf=2 2x' width='324' height='180' alt='' loading='lazy'><div><b>Exact Sciences Corp</b>Diagnostics & Research <span>•</span> USA <span>•</span> 19.26B </div>] offsetx=[200] offsety=[-95] delay=[250]"><a href="quote.ashx?t=EXAS" class="tab-link">EXAS</a></td><td align="right">101.50</td><td align="right" style="white-space:nowrap"><span class="color-text is-positive">0.14%</span></td><td align="right">2.73M</td><td></td><td data-boxover="cssbody=[tooltip_short_bdy] cssheader=[tooltip_short_hdr] body=[Stocks with extreme price increase over past two weeks,<br>calculated by RSI(14) indicator] offsetx=[10] offsety=[20] delay=[300]"><a href="screener.ashx?v=210&s=ta_overbought" class="tab-link-nw">Overbought</a></td>
</tr>
<tr class="styled-row is-hoverable is-bordered is-rounded has-color-text cursor-pointer" onclick="window.location='screener.ashx?v=210&s=ta_overbought'">
<td data-boxover="cssbody=[hoverchart] cssheader=[tabchrthdr] body=[<img  srcset='https://charts2-node.finviz.com/chart.ashx?cs=m&t=SATS&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d 1x, https://charts2-node.finviz.com/chart.ashx?cs=m&t=SATS&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&sf=2 2x' width='324' height='180' alt='' loading='lazy'><div><b>EchoStar Corp</b>Telecom Services <span>•</span> USA <span>•</span> 30.91B </div>] offsetx=[200] offsety=[-95] delay=[250]"><a href="quote.ashx?t=SATS" class="tab-link">SATS</a></td><td align="right">107.37</td><td align="right" style="white-space:nowrap"><span class="color-text is-positive">2.85%</span></td><td align="right">7.64M</td><td></td><td data-boxover="cssbody=[tooltip_short_bdy] cssheader=[tooltip_short_hdr] body=[Stocks with extreme price increase over past two weeks,<br>calculated by RSI(14) indicator] offsetx=[10] offsety=[20] delay=[300]"><a href="screener.ashx?v=210&s=ta_overbought" class="tab-link-nw">Overbought</a></td>
</tr>
<tr class="styled-row is-hoverable is-bordered is-rounded has-color-text cursor-pointer" onclick="window.location='screener.ashx?v=320&s=ta_unusualvolume'">
<td data-boxover="cssbody=[hoverchart] cssheader=[tabchrthdr] body=[<img  srcset='https://charts2-node.finviz.com/chart.ashx?cs=m&t=LRND&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d 1x, https://charts2-node.finviz.com/chart.ashx?cs=m&t=LRND&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&sf=2 2x' width='324' height='180' alt='' loading='lazy'><div><b>NYLI U.S. Large Cap R&D Leaders ETF</b>Exchange Traded Fund <span>•</span> USA <span>•</span> AUM: 10.11M </div>] offsetx=[200] offsety=[-95] delay=[250]"><a href="quote.ashx?t=LRND" class="tab-link">LRND</a></td><td align="right">40.44</td><td align="right" style="white-space:nowrap"><span class="color-text is-negative">-1.73%</span></td><td align="right">2.17M</td><td></td><td data-boxover="cssbody=[tooltip_short_bdy] cssheader=[tooltip_short_hdr] body=[Stocks with unusually high volume today] offsetx=[10] offsety=[20] delay=[300]"><a href="screener.ashx?v=320&s=ta_unusualvolume" class="tab-link-nw">Unusual Volume</a></td>
</tr>
<tr class="styled-row is-hoverable is-bordered is-rounded has-color-text cursor-pointer" onclick="window.location='screener.ashx?v=320&s=ta_unusualvolume'">
<td data-boxover="cssbody=[hoverchart] cssheader=[tabchrthdr] body=[<img  srcset='https://charts2-node.finviz.com/chart.ashx?cs=m&t=AREA&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d 1x, https://charts2-node.finviz.com/chart.ashx?cs=m&t=AREA&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&sf=2 2x' width='324' height='180' alt='' loading='lazy'><div><b>Harbor AlphaEdge Next Generation REITs ETF</b>Exchange Traded Fund <span>•</span> USA <span>•</span> AUM: 1.86M </div>] offsetx=[200] offsety=[-95] delay=[250]"><a href="quote.ashx?t=AREA" class="tab-link">AREA</a></td><td align="right">18.58</td><td align="right" style="white-space:nowrap"><span class="color-text is-positive">0.24%</span></td><td align="right">318.73K</td><td></td><td data-boxover="cssbody=[tooltip_short_bdy] cssheader=[tooltip_short_hdr] body=[Stocks with unusually high volume today] offsetx=[10] offsety=[20] delay=[300]"><a href="screener.ashx?v=320&s=ta_unusualvolume" class="tab-link-nw">Unusual Volume</a></td>
</tr>
<tr class="styled-row is-hoverable is-bordered is-rounded has-color-text cursor-pointer" onclick="window.location='screener.ashx?v=320&s=ta_unusualvolume'">
<td data-boxover="cssbody=[hoverchart] cssheader=[tabchrthdr] body=[<img  srcset='https://charts2-node.finviz.com/chart.ashx?cs=m&t=CSTK&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d 1x, https://charts2-node.finviz.com/chart.ashx?cs=m&t=CSTK&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&sf=2 2x' width='324' height='180' alt='' loading='lazy'><div><b>Invesco Comstock Contrarian Equity ETF</b>Exchange Traded Fund <span>•</span> USA <span>•</span> AUM: 115.53M </div>] offsetx=[200] offsety=[-95] delay=[250]"><a href="quote.ashx?t=CSTK" class="tab-link">CSTK</a></td><td align="right">29.32</td><td align="right" style="white-space:nowrap"><span class="color-text is-negative">-0.44%</span></td><td align="right">177.23K</td><td></td><td data-boxover="cssbody=[tooltip_short_bdy] cssheader=[tooltip_short_hdr] body=[Stocks with unusually high volume today] offsetx=[10] offsety=[20] delay=[300]"><a href="screener.ashx?v=320&s=ta_unusualvolume" class="tab-link-nw">Unusual Volume</a></td>
</tr>
<tr class="styled-row is-hoverable is-bordered is-rounded has-color-text cursor-pointer" onclick="window.location='screener.ashx?v=320&s=ta_unusualvolume'">
<td data-boxover="cssbody=[hoverchart] cssheader=[tabchrthdr] body=[<img  srcset='https://charts2-node.finviz.com/chart.ashx?cs=m&t=FFUT&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d 1x, https://charts2-node.finviz.com/chart.ashx?cs=m&t=FFUT&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&sf=2 2x' width='324' height='180' alt='' loading='lazy'><div><b>Fidelity Managed Futures ETF</b>Exchange Traded Fund <span>•</span> USA <span>•</span> AUM: 128.28M </div>] offsetx=[200] offsety=[-95] delay=[250]"><a href="quote.ashx?t=FFUT" class="tab-link">FFUT</a></td><td align="right">54.10</td><td align="right" style="white-space:nowrap"><span class="color-text is-positive">0.40%</span></td><td align="right">1.86M</td><td></td><td data-boxover="cssbody=[tooltip_short_bdy] cssheader=[tooltip_short_hdr] body=[Stocks with unusually high volume today] offsetx=[10] offsety=[20] delay=[300]"><a href="screener.ashx?v=320&s=ta_unusualvolume" class="tab-link-nw">Unusual Volume</a></td>
</tr>
<tr class="styled-row is-hoverable is-bordered is-rounded has-color-text cursor-pointer" onclick="window.location='screener.ashx?v=340&s=n_upgrades'">
<td data-boxover="cssbody=[hoverchart] cssheader=[tabchrthdr] body=[<img  srcset='https://charts2-node.finviz.com/chart.ashx?cs=m&t=ALGT&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d 1x, https://charts2-node.finviz.com/chart.ashx?cs=m&t=ALGT&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&sf=2 2x' width='324' height='180' alt='' loading='lazy'><div><b>Allegiant Travel</b>Airlines <span>•</span> USA <span>•</span> 1.57B </div>] offsetx=[200] offsety=[-95] delay=[250]"><a href="quote.ashx?t=ALGT" class="tab-link">ALGT</a></td><td align="right">85.86</td><td align="right" style="white-space:nowrap"><span class="color-text is-positive">2.02%</span></td><td align="right">651.75K</td><td></td><td data-boxover="cssbody=[tooltip_short_bdy] cssheader=[tooltip_short_hdr] body=[Stocks upgraded by analyst today] offsetx=[10] offsety=[20] delay=[300]"><a href="screener.ashx?v=340&s=n_upgrades" class="tab-link-nw">Upgrades</a></td>
</tr>
<tr class="styled-row is-hoverable is-bordered is-rounded has-color-text cursor-pointer" onclick="window.location='screener.ashx?v=340&s=n_earningsbefore'">
<td data-boxover="cssbody=[hoverchart] cssheader=[tabchrthdr] body=[<img  srcset='https://charts2-node.finviz.com/chart.ashx?cs=m&t=JOUT&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d 1x, https://charts2-node.finviz.com/chart.ashx?cs=m&t=JOUT&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&sf=2 2x' width='324' height='180' alt='' loading='lazy'><div><b>Johnson Outdoors Inc</b>Leisure <span>•</span> USA <span>•</span> 431.54M </div>] offsetx=[200] offsety=[-95] delay=[250]"><a href="quote.ashx?t=JOUT" class="tab-link">JOUT</a></td><td align="right">42.05</td><td align="right" style="white-space:nowrap"><span class="color-text is-negative">-2.21%</span></td><td align="right">147.82K</td><td></td><td data-boxover="cssbody=[tooltip_short_bdy] cssheader=[tooltip_short_hdr] body=[Companies reporting earnings today, before market open] offsetx=[10] offsety=[20] delay=[300]"><a href="screener.ashx?v=340&s=n_earningsbefore" class="tab-link-nw">Earnings Before</a></td>
</tr>
<tr class="styled-row is-hoverable is-bordered is-rounded has-color-text cursor-pointer" onclick="window.location='screener.ashx?v=340&s=it_latestbuys'">
<td data-boxover="cssbody=[hoverchart] cssheader=[tabchrthdr] body=[<img  srcset='https://charts2-node.finviz.com/chart.ashx?cs=m&t=CRMT&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d 1x, https://charts2-node.finviz.com/chart.ashx?cs=m&t=CRMT&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&sf=2 2x' width='324' height='180' alt='' loading='lazy'><div><b>Americas Car Mart, Inc</b>Auto & Truck Dealerships <span>•</span> USA <span>•</span> 200.73M </div>] offsetx=[200] offsety=[-95] delay=[250]"><a href="quote.ashx?t=CRMT" class="tab-link">CRMT</a></td><td align="right">24.20</td><td align="right" style="white-space:nowrap"><span class="color-text is-negative">-4.54%</span></td><td align="right">130.26K</td><td></td><td data-boxover="cssbody=[tooltip_short_bdy] cssheader=[tooltip_short_hdr] body=[Stocks with recent insider buying] offsetx=[10] offsety=[20] delay=[300]"><a href="screener.ashx?v=340&s=it_latestbuys" class="tab-link-nw">Insider Buying</a></td>
</tr>
</tbody>
</table>
</td>
<td class="hp_spacer w-4"><img src="gfx/nic2x2.gif" style="width:16px;height:2px" alt="" border="0"></td>
<td width="50%" valign="top">
<table width="100%" cellpadding="1" cellspacing="0" class="styled-table-new is-rounded is-condensed is-tabular-nums" border="0">
<thead><tr>
<th class="text-left">Ticker</th><th align="right">Last</th><th align="right">Change</th><th align="right">Volume</th><th><img src="gfx/nic2x2.gif" style="width:4px;height:2px" alt="" border="0"></th><th class="text-left" style="width: 35%;"><div class="flex justify-between items-center"><span>Signal</span><span class="js-signal-switch"><button class="fv-button js-signal-switch-button ml-1 is-xsmall is-border is-link">
    Daily
    <svg width="16" height="16" class="ml-0.5 -mr-0.5">
    <use href="/assets/dist-icons/icons.svg?rev=35#chevronDown"/>
</svg>
</button</span></div></th>
</tr></thead><tbody id="js-signals_2"><tr class="styled-row is-hoverable is-bordered is-rounded has-color-text cursor-pointer" onclick="window.location='screener.ashx?v=340&s=ta_toplosers'">
<td data-boxover="cssbody=[hoverchart] cssheader=[tabchrthdr] body=[<img  srcset='https://charts2-node.finviz.com/chart.ashx?cs=m&t=CCHH&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d 1x, https://charts2-node.finviz.com/chart.ashx?cs=m&t=CCHH&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&sf=2 2x' width='324' height='180' alt='' loading='lazy'><div><b>CCH Holdings Ltd</b>Restaurants <span>•</span> Malaysia <span>•</span> 51.01M </div>] offsetx=[200] offsety=[-95] delay=[250]"><a href="quote.ashx?t=CCHH" class="tab-link">CCHH</a></td><td align="right">2.65</td><td align="right" style="white-space:nowrap"><span class="color-text is-negative">-82.47%</span></td><td align="right">6.70M</td><td></td><td data-boxover="cssbody=[tooltip_short_bdy] cssheader=[tooltip_short_hdr] body=[Stocks with the highest price loss today] offsetx=[10] offsety=[20] delay=[300]"><a href="screener.ashx?v=340&s=ta_toplosers" class="tab-link-nw">Top Losers</a></td>
</tr>
<tr class="styled-row is-hoverable is-bordered is-rounded has-color-text cursor-pointer" onclick="window.location='screener.ashx?v=340&s=ta_toplosers'">
<td data-boxover="cssbody=[hoverchart] cssheader=[tabchrthdr] body=[<img  srcset='https://charts2-node.finviz.com/chart.ashx?cs=m&t=ARBK&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d 1x, https://charts2-node.finviz.com/chart.ashx?cs=m&t=ARBK&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&sf=2 2x' width='324' height='180' alt='' loading='lazy'><div><b>Argo Blockchain Plc ADR</b>Capital Markets <span>•</span> United Kingdom <span>•</span> 16.84M </div>] offsetx=[200] offsety=[-95] delay=[250]"><a href="quote.ashx?t=ARBK" class="tab-link">ARBK</a></td><td align="right">6.87</td><td align="right" style="white-space:nowrap"><span class="color-text is-negative">-77.60%</span></td><td align="right">1.97M</td><td></td><td data-boxover="cssbody=[tooltip_short_bdy] cssheader=[tooltip_short_hdr] body=[Stocks with the highest price loss today] offsetx=[10] offsety=[20] delay=[300]"><a href="screener.ashx?v=340&s=ta_toplosers" class="tab-link-nw">Top Losers</a></td>
</tr>
<tr class="styled-row is-hoverable is-bordered is-rounded has-color-text cursor-pointer" onclick="window.location='screener.ashx?v=340&s=ta_toplosers'">
<td data-boxover="cssbody=[hoverchart] cssheader=[tabchrthdr] body=[<img  srcset='https://charts2-node.finviz.com/chart.ashx?cs=m&t=OCG&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d 1x, https://charts2-node.finviz.com/chart.ashx?cs=m&t=OCG&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&sf=2 2x' width='324' height='180' alt='' loading='lazy'><div><b>Oriental Culture Holding Ltd</b>Internet Retail <span>•</span> Hong Kong <span>•</span> 4.67M </div>] offsetx=[200] offsety=[-95] delay=[250]"><a href="quote.ashx?t=OCG" class="tab-link">OCG</a></td><td align="right">0.22</td><td align="right" style="white-space:nowrap"><span class="color-text is-negative">-75.85%</span></td><td align="right">328.84M</td><td></td><td data-boxover="cssbody=[tooltip_short_bdy] cssheader=[tooltip_short_hdr] body=[Stocks with the highest price loss today] offsetx=[10] offsety=[20] delay=[300]"><a href="screener.ashx?v=340&s=ta_toplosers" class="tab-link-nw">Top Losers</a></td>
</tr>
<tr class="styled-row is-hoverable is-bordered is-rounded has-color-text cursor-pointer" onclick="window.location='screener.ashx?v=340&s=ta_toplosers'">
<td data-boxover="cssbody=[hoverchart] cssheader=[tabchrthdr] body=[<img  srcset='https://charts2-node.finviz.com/chart.ashx?cs=m&t=JZXN&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d 1x, https://charts2-node.finviz.com/chart.ashx?cs=m&t=JZXN&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&sf=2 2x' width='324' height='180' alt='' loading='lazy'><div><b>Jiuzi Holdings Inc</b>Auto & Truck Dealerships <span>•</span> China <span>•</span> 3.39M </div>] offsetx=[200] offsety=[-95] delay=[250]"><a href="quote.ashx?t=JZXN" class="tab-link">JZXN</a></td><td align="right">2.70</td><td align="right" style="white-space:nowrap"><span class="color-text is-negative">-52.04%</span></td><td align="right">10.75M</td><td></td><td data-boxover="cssbody=[tooltip_short_bdy] cssheader=[tooltip_short_hdr] body=[Stocks with the highest price loss today] offsetx=[10] offsety=[20] delay=[300]"><a href="screener.ashx?v=340&s=ta_toplosers" class="tab-link-nw">Top Losers</a></td>
</tr>
<tr class="styled-row is-hoverable is-bordered is-rounded has-color-text cursor-pointer" onclick="window.location='screener.ashx?v=340&s=ta_toplosers'">
<td data-boxover="cssbody=[hoverchart] cssheader=[tabchrthdr] body=[<img  srcset='https://charts2-node.finviz.com/chart.ashx?cs=m&t=AMCI&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d 1x, https://charts2-node.finviz.com/chart.ashx?cs=m&t=AMCI&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&sf=2 2x' width='324' height='180' alt='' loading='lazy'><div><b>AMC Robotics Corp</b>Computer Hardware <span>•</span> USA <span>•</span> 8.73M </div>] offsetx=[200] offsety=[-95] delay=[250]"><a href="quote.ashx?t=AMCI" class="tab-link">AMCI</a></td><td align="right">2.71</td><td align="right" style="white-space:nowrap"><span class="color-text is-negative">-44.47%</span></td><td align="right">502.47K</td><td></td><td data-boxover="cssbody=[tooltip_short_bdy] cssheader=[tooltip_short_hdr] body=[Stocks with the highest price loss today] offsetx=[10] offsety=[20] delay=[300]"><a href="screener.ashx?v=340&s=ta_toplosers" class="tab-link-nw">Top Losers</a></td>
</tr>
<tr class="styled-row is-hoverable is-bordered is-rounded has-color-text cursor-pointer" onclick="window.location='screener.ashx?v=340&s=ta_toplosers'">
<td data-boxover="cssbody=[hoverchart] cssheader=[tabchrthdr] body=[<img  srcset='https://charts2-node.finviz.com/chart.ashx?cs=m&t=TNYA&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d 1x, https://charts2-node.finviz.com/chart.ashx?cs=m&t=TNYA&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&sf=2 2x' width='324' height='180' alt='' loading='lazy'><div><b>Tenaya Therapeutics Inc</b>Biotechnology <span>•</span> USA <span>•</span> 141.53M </div>] offsetx=[200] offsety=[-95] delay=[250]"><a href="quote.ashx?t=TNYA" class="tab-link">TNYA</a></td><td align="right">0.85</td><td align="right" style="white-space:nowrap"><span class="color-text is-negative">-37.50%</span></td><td align="right">66.48M</td><td></td><td data-boxover="cssbody=[tooltip_short_bdy] cssheader=[tooltip_short_hdr] body=[Stocks with the highest price loss today] offsetx=[10] offsety=[20] delay=[300]"><a href="screener.ashx?v=340&s=ta_toplosers" class="tab-link-nw">Top Losers</a></td>
</tr>
<tr class="styled-row is-hoverable is-bordered is-rounded has-color-text cursor-pointer" onclick="window.location='screener.ashx?v=340&s=ta_toplosers'">
<td data-boxover="cssbody=[hoverchart] cssheader=[tabchrthdr] body=[<img  srcset='https://charts2-node.finviz.com/chart.ashx?cs=m&t=WOK&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d 1x, https://charts2-node.finviz.com/chart.ashx?cs=m&t=WOK&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&sf=2 2x' width='324' height='180' alt='' loading='lazy'><div><b>Work Medical Technology Group Ltd</b>Medical Devices <span>•</span> China <span>•</span> 0.11M </div>] offsetx=[200] offsety=[-95] delay=[250]"><a href="quote.ashx?t=WOK" class="tab-link">WOK</a></td><td align="right">0.11</td><td align="right" style="white-space:nowrap"><span class="color-text is-negative">-35.75%</span></td><td align="right">121.03M</td><td></td><td data-boxover="cssbody=[tooltip_short_bdy] cssheader=[tooltip_short_hdr] body=[Stocks with the highest price loss today] offsetx=[10] offsety=[20] delay=[300]"><a href="screener.ashx?v=340&s=ta_toplosers" class="tab-link-nw">Top Losers</a></td>
</tr>
<tr class="styled-row is-hoverable is-bordered is-rounded has-color-text cursor-pointer" onclick="window.location='screener.ashx?v=340&s=ta_newlow'">
<td data-boxover="cssbody=[hoverchart] cssheader=[tabchrthdr] body=[<img  srcset='https://charts2-node.finviz.com/chart.ashx?cs=m&t=OCG&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d 1x, https://charts2-node.finviz.com/chart.ashx?cs=m&t=OCG&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&sf=2 2x' width='324' height='180' alt='' loading='lazy'><div><b>Oriental Culture Holding Ltd</b>Internet Retail <span>•</span> Hong Kong <span>•</span> 4.67M </div>] offsetx=[200] offsety=[-95] delay=[250]"><a href="quote.ashx?t=OCG" class="tab-link">OCG</a></td><td align="right">0.22</td><td align="right" style="white-space:nowrap"><span class="color-text is-negative">-75.85%</span></td><td align="right">328.84M</td><td></td><td data-boxover="cssbody=[tooltip_short_bdy] cssheader=[tooltip_short_hdr] body=[Stocks making new 52 weeks low today] offsetx=[10] offsety=[20] delay=[300]"><a href="screener.ashx?v=340&s=ta_newlow" class="tab-link-nw">New Low</a></td>
</tr>
<tr class="styled-row is-hoverable is-bordered is-rounded has-color-text cursor-pointer" onclick="window.location='screener.ashx?v=340&s=ta_newlow'">
<td data-boxover="cssbody=[hoverchart] cssheader=[tabchrthdr] body=[<img  srcset='https://charts2-node.finviz.com/chart.ashx?cs=m&t=ARBK&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d 1x, https://charts2-node.finviz.com/chart.ashx?cs=m&t=ARBK&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&sf=2 2x' width='324' height='180' alt='' loading='lazy'><div><b>Argo Blockchain Plc ADR</b>Capital Markets <span>•</span> United Kingdom <span>•</span> 16.84M </div>] offsetx=[200] offsety=[-95] delay=[250]"><a href="quote.ashx?t=ARBK" class="tab-link">ARBK</a></td><td align="right">6.87</td><td align="right" style="white-space:nowrap"><span class="color-text is-negative">-77.60%</span></td><td align="right">1.97M</td><td></td><td data-boxover="cssbody=[tooltip_short_bdy] cssheader=[tooltip_short_hdr] body=[Stocks making new 52 weeks low today] offsetx=[10] offsety=[20] delay=[300]"><a href="screener.ashx?v=340&s=ta_newlow" class="tab-link-nw">New Low</a></td>
</tr>
<tr class="styled-row is-hoverable is-bordered is-rounded has-color-text cursor-pointer" onclick="window.location='screener.ashx?v=340&s=ta_newlow'">
<td data-boxover="cssbody=[hoverchart] cssheader=[tabchrthdr] body=[<img  srcset='https://charts2-node.finviz.com/chart.ashx?cs=m&t=BLMZ&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d 1x, https://charts2-node.finviz.com/chart.ashx?cs=m&t=BLMZ&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&sf=2 2x' width='324' height='180' alt='' loading='lazy'><div><b>Harrison Global Holdings Inc</b>Entertainment <span>•</span> Japan <span>•</span> 70.03M </div>] offsetx=[200] offsety=[-95] delay=[250]"><a href="quote.ashx?t=BLMZ" class="tab-link">BLMZ</a></td><td align="right">0.13</td><td align="right" style="white-space:nowrap"><span class="color-text is-negative">-65.40%</span></td><td align="right">8.38M</td><td></td><td data-boxover="cssbody=[tooltip_short_bdy] cssheader=[tooltip_short_hdr] body=[Stocks making new 52 weeks low today] offsetx=[10] offsety=[20] delay=[300]"><a href="screener.ashx?v=340&s=ta_newlow" class="tab-link-nw">New Low</a></td>
</tr>
<tr class="styled-row is-hoverable is-bordered is-rounded has-color-text cursor-pointer" onclick="window.location='screener.ashx?v=340&s=ta_newlow'">
<td data-boxover="cssbody=[hoverchart] cssheader=[tabchrthdr] body=[<img  srcset='https://charts2-node.finviz.com/chart.ashx?cs=m&t=JZXN&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d 1x, https://charts2-node.finviz.com/chart.ashx?cs=m&t=JZXN&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&sf=2 2x' width='324' height='180' alt='' loading='lazy'><div><b>Jiuzi Holdings Inc</b>Auto & Truck Dealerships <span>•</span> China <span>•</span> 3.39M </div>] offsetx=[200] offsety=[-95] delay=[250]"><a href="quote.ashx?t=JZXN" class="tab-link">JZXN</a></td><td align="right">2.70</td><td align="right" style="white-space:nowrap"><span class="color-text is-negative">-52.04%</span></td><td align="right">10.75M</td><td></td><td data-boxover="cssbody=[tooltip_short_bdy] cssheader=[tooltip_short_hdr] body=[Stocks making new 52 weeks low today] offsetx=[10] offsety=[20] delay=[300]"><a href="screener.ashx?v=340&s=ta_newlow" class="tab-link-nw">New Low</a></td>
</tr>
<tr class="styled-row is-hoverable is-bordered is-rounded has-color-text cursor-pointer" onclick="window.location='screener.ashx?v=210&s=ta_oversold'">
<td data-boxover="cssbody=[hoverchart] cssheader=[tabchrthdr] body=[<img  srcset='https://charts2-node.finviz.com/chart.ashx?cs=m&t=DYOR&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d 1x, https://charts2-node.finviz.com/chart.ashx?cs=m&t=DYOR&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&sf=2 2x' width='324' height='180' alt='' loading='lazy'><div><b>Insight Digital Partners II</b>Shell Companies <span>•</span> USA <span>•</span> 227.70M </div>] offsetx=[200] offsety=[-95] delay=[250]"><a href="quote.ashx?t=DYOR" class="tab-link">DYOR</a></td><td align="right">9.90</td><td align="right" style="white-space:nowrap">0.00%</td><td align="right">23.06K</td><td></td><td data-boxover="cssbody=[tooltip_short_bdy] cssheader=[tooltip_short_hdr] body=[Stocks with extreme price decrease over past two weeks,<br>calculated by RSI(14) indicator] offsetx=[10] offsety=[20] delay=[300]"><a href="screener.ashx?v=210&s=ta_oversold" class="tab-link-nw">Oversold</a></td>
</tr>
<tr class="styled-row is-hoverable is-bordered is-rounded has-color-text cursor-pointer" onclick="window.location='screener.ashx?v=210&s=ta_oversold'">
<td data-boxover="cssbody=[hoverchart] cssheader=[tabchrthdr] body=[<img  srcset='https://charts2-node.finviz.com/chart.ashx?cs=m&t=BRR&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d 1x, https://charts2-node.finviz.com/chart.ashx?cs=m&t=BRR&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&sf=2 2x' width='324' height='180' alt='' loading='lazy'><div><b>ProCap Financial Inc</b>Shell Companies <span>•</span> USA <span>•</span> 114.03M </div>] offsetx=[200] offsety=[-95] delay=[250]"><a href="quote.ashx?t=BRR" class="tab-link">BRR</a></td><td align="right">3.35</td><td align="right" style="white-space:nowrap"><span class="color-text is-negative">-12.53%</span></td><td align="right">3.35M</td><td></td><td data-boxover="cssbody=[tooltip_short_bdy] cssheader=[tooltip_short_hdr] body=[Stocks with extreme price decrease over past two weeks,<br>calculated by RSI(14) indicator] offsetx=[10] offsety=[20] delay=[300]"><a href="screener.ashx?v=210&s=ta_oversold" class="tab-link-nw">Oversold</a></td>
</tr>
<tr class="styled-row is-hoverable is-bordered is-rounded has-color-text cursor-pointer" onclick="window.location='screener.ashx?v=320&s=ta_mostvolatile'">
<td data-boxover="cssbody=[hoverchart] cssheader=[tabchrthdr] body=[<img  srcset='https://charts2-node.finviz.com/chart.ashx?cs=m&t=ARBK&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d 1x, https://charts2-node.finviz.com/chart.ashx?cs=m&t=ARBK&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&sf=2 2x' width='324' height='180' alt='' loading='lazy'><div><b>Argo Blockchain Plc ADR</b>Capital Markets <span>•</span> United Kingdom <span>•</span> 16.84M </div>] offsetx=[200] offsety=[-95] delay=[250]"><a href="quote.ashx?t=ARBK" class="tab-link">ARBK</a></td><td align="right">6.87</td><td align="right" style="white-space:nowrap"><span class="color-text is-negative">-77.60%</span></td><td align="right">1.97M</td><td></td><td data-boxover="cssbody=[tooltip_short_bdy] cssheader=[tooltip_short_hdr] body=[Stocks with the widest high/low trading range today] offsetx=[10] offsety=[20] delay=[300]"><a href="screener.ashx?v=320&s=ta_mostvolatile" class="tab-link-nw">Most Volatile</a></td>
</tr>
<tr class="styled-row is-hoverable is-bordered is-rounded has-color-text cursor-pointer" onclick="window.location='screener.ashx?v=320&s=ta_mostvolatile'">
<td data-boxover="cssbody=[hoverchart] cssheader=[tabchrthdr] body=[<img  srcset='https://charts2-node.finviz.com/chart.ashx?cs=m&t=JZXN&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d 1x, https://charts2-node.finviz.com/chart.ashx?cs=m&t=JZXN&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&sf=2 2x' width='324' height='180' alt='' loading='lazy'><div><b>Jiuzi Holdings Inc</b>Auto & Truck Dealerships <span>•</span> China <span>•</span> 3.39M </div>] offsetx=[200] offsety=[-95] delay=[250]"><a href="quote.ashx?t=JZXN" class="tab-link">JZXN</a></td><td align="right">2.70</td><td align="right" style="white-space:nowrap"><span class="color-text is-negative">-52.04%</span></td><td align="right">10.75M</td><td></td><td data-boxover="cssbody=[tooltip_short_bdy] cssheader=[tooltip_short_hdr] body=[Stocks with the widest high/low trading range today] offsetx=[10] offsety=[20] delay=[300]"><a href="screener.ashx?v=320&s=ta_mostvolatile" class="tab-link-nw">Most Volatile</a></td>
</tr>
<tr class="styled-row is-hoverable is-bordered is-rounded has-color-text cursor-pointer" onclick="window.location='screener.ashx?v=320&s=ta_mostactive'">
<td data-boxover="cssbody=[hoverchart] cssheader=[tabchrthdr] body=[<img  srcset='https://charts2-node.finviz.com/chart.ashx?cs=m&t=SOXS&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d 1x, https://charts2-node.finviz.com/chart.ashx?cs=m&t=SOXS&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&sf=2 2x' width='324' height='180' alt='' loading='lazy'><div><b>Direxion Daily Semiconductor Bear 3X Shares</b>Exchange Traded Fund <span>•</span> USA <span>•</span> AUM: 1.22B </div>] offsetx=[200] offsety=[-95] delay=[250]"><a href="quote.ashx?t=SOXS" class="tab-link">SOXS</a></td><td align="right">3.29</td><td align="right" style="white-space:nowrap"><span class="color-text is-positive">14.63%</span></td><td align="right">529.44M</td><td></td><td data-boxover="cssbody=[tooltip_short_bdy] cssheader=[tooltip_short_hdr] body=[Stocks with highest trading volume today] offsetx=[10] offsety=[20] delay=[300]"><a href="screener.ashx?v=320&s=ta_mostactive" class="tab-link-nw">Most Active</a></td>
</tr>
<tr class="styled-row is-hoverable is-bordered is-rounded has-color-text cursor-pointer" onclick="window.location='screener.ashx?v=320&s=ta_mostactive'">
<td data-boxover="cssbody=[hoverchart] cssheader=[tabchrthdr] body=[<img  srcset='https://charts2-node.finviz.com/chart.ashx?cs=m&t=PAVS&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d 1x, https://charts2-node.finviz.com/chart.ashx?cs=m&t=PAVS&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&sf=2 2x' width='324' height='180' alt='' loading='lazy'><div><b>Paranovus Entertainment Technology Ltd</b>Packaged Foods <span>•</span> USA <span>•</span> 2.77M </div>] offsetx=[200] offsety=[-95] delay=[250]"><a href="quote.ashx?t=PAVS" class="tab-link">PAVS</a></td><td align="right">0.04</td><td align="right" style="white-space:nowrap"><span class="color-text is-positive">19.13%</span></td><td align="right">507.88M</td><td></td><td data-boxover="cssbody=[tooltip_short_bdy] cssheader=[tooltip_short_hdr] body=[Stocks with highest trading volume today] offsetx=[10] offsety=[20] delay=[300]"><a href="screener.ashx?v=320&s=ta_mostactive" class="tab-link-nw">Most Active</a></td>
</tr>
<tr class="styled-row is-hoverable is-bordered is-rounded has-color-text cursor-pointer" onclick="window.location='screener.ashx?v=340&s=n_downgrades'">
<td data-boxover="cssbody=[hoverchart] cssheader=[tabchrthdr] body=[<img  srcset='https://charts2-node.finviz.com/chart.ashx?cs=m&t=APD&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d 1x, https://charts2-node.finviz.com/chart.ashx?cs=m&t=APD&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&sf=2 2x' width='324' height='180' alt='' loading='lazy'><div><b>Air Products & Chemicals Inc</b>Specialty Chemicals <span>•</span> USA <span>•</span> 54.09B </div>] offsetx=[200] offsety=[-95] delay=[250]"><a href="quote.ashx?t=APD" class="tab-link">APD</a></td><td align="right">243.00</td><td align="right" style="white-space:nowrap"><span class="color-text is-negative">-0.30%</span></td><td align="right">3.05M</td><td></td><td data-boxover="cssbody=[tooltip_short_bdy] cssheader=[tooltip_short_hdr] body=[Stocks downgraded by analyst today] offsetx=[10] offsety=[20] delay=[300]"><a href="screener.ashx?v=340&s=n_downgrades" class="tab-link-nw">Downgrades</a></td>
</tr>
<tr class="styled-row is-hoverable is-bordered is-rounded has-color-text cursor-pointer" onclick="window.location='screener.ashx?v=340&s=it_latestsales'">
<td data-boxover="cssbody=[hoverchart] cssheader=[tabchrthdr] body=[<img  srcset='https://charts2-node.finviz.com/chart.ashx?cs=m&t=TLS&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d 1x, https://charts2-node.finviz.com/chart.ashx?cs=m&t=TLS&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&sf=2 2x' width='324' height='180' alt='' loading='lazy'><div><b>Telos Corp</b>Software - Infrastructure <span>•</span> USA <span>•</span> 418.56M </div>] offsetx=[200] offsety=[-95] delay=[250]"><a href="quote.ashx?t=TLS" class="tab-link">TLS</a></td><td align="right">5.68</td><td align="right" style="white-space:nowrap"><span class="color-text is-negative">-10.63%</span></td><td align="right">1.17M</td><td></td><td data-boxover="cssbody=[tooltip_short_bdy] cssheader=[tooltip_short_hdr] body=[Stocks with recent insider selling] offsetx=[10] offsety=[20] delay=[300]"><a href="screener.ashx?v=340&s=it_latestsales" class="tab-link-nw">Insider Selling</a></td>
</tr>
</tbody>
</table>
</td>
<td class="hp_spacer w-4"><img src="gfx/nic2x2.gif" style="width:16px;height:2px" alt="" border="0"></td>
<td align="right" valign="top" style="width: 414px;"><div class="hp_map-wrapper"><a href="map.ashx?t=sec" id="treemap-small" class="block w-[400px]" style="height: 368px;"></a></div></td>
</tr>
</table>
</td>
</tr>
</table>
</div>
<div id="js-homepage_bottom">
<table width="100%" cellpadding="0" cellspacing="0" border="0">
<tr>
<td style="font-size: 0; line-height: 0"><img src="gfx/nic2x2.gif" style="width:10px;height:12px" alt="" border="0"></td>
</tr>
<tr>
<td align="center">
<table width="100%" cellpadding="0" cellspacing="0" border="0">
<tr>
<td width="100%" valign="top">
<table width="100%" border="0" cellpadding="0" cellspacing="0">
<tr>
<td width="50%" valign="top">
<table class="styled-table-new is-rounded is-condensed hp_signal-table" width="100%" cellpadding="1" cellspacing="0" border="0">
<thead><tr>
<th class="text-left" colspan="4">Tickers</th><th class="text-left"> Signal</th>
</tr></thead><tr class="styled-row is-hoverable is-bordered is-rounded cursor-pointer" onclick="window.location='screener.ashx?v=210&s=ta_p_tlsupport'">
<td data-boxover="cssbody=[hoverchart] cssheader=[tabchrthdr] body=[<img  srcset='https://charts2-node.finviz.com/chart.ashx?cs=m&t=SOFR&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&o[[0]][[ot]]=sma&o[[0]][[op]]=50&o[[0]][[oc]]=FF8F33C6&o[[1]][[ot]]=sma&o[[1]][[op]]=200&o[[1]][[oc]]=DCB3326D&o[[2]][[ot]]=patterns&o[[2]][[op]]=&o[[2]][[oc]]=000 1x, https://charts2-node.finviz.com/chart.ashx?cs=m&t=SOFR&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&o[[0]][[ot]]=sma&o[[0]][[op]]=50&o[[0]][[oc]]=FF8F33C6&o[[1]][[ot]]=sma&o[[1]][[op]]=200&o[[1]][[oc]]=DCB3326D&o[[2]][[ot]]=patterns&o[[2]][[op]]=&o[[2]][[oc]]=000&sf=2 2x' width='464' height='230' alt='' loading='lazy'><div><b>Amplify Samsung SOFR ETF</b>Exchange Traded Fund <span>•</span> USA <span>•</span> AUM: 355.93M </div>] offsetx=[20] offsety=[-280] delay=[250]"><a href="quote.ashx?t=SOFR" class="tab-link">SOFR</a></td>
<td data-boxover="cssbody=[hoverchart] cssheader=[tabchrthdr] body=[<img  srcset='https://charts2-node.finviz.com/chart.ashx?cs=m&t=PMMF&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&o[[0]][[ot]]=sma&o[[0]][[op]]=50&o[[0]][[oc]]=FF8F33C6&o[[1]][[ot]]=sma&o[[1]][[op]]=200&o[[1]][[oc]]=DCB3326D&o[[2]][[ot]]=patterns&o[[2]][[op]]=&o[[2]][[oc]]=000 1x, https://charts2-node.finviz.com/chart.ashx?cs=m&t=PMMF&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&o[[0]][[ot]]=sma&o[[0]][[op]]=50&o[[0]][[oc]]=FF8F33C6&o[[1]][[ot]]=sma&o[[1]][[op]]=200&o[[1]][[oc]]=DCB3326D&o[[2]][[ot]]=patterns&o[[2]][[op]]=&o[[2]][[oc]]=000&sf=2 2x' width='464' height='230' alt='' loading='lazy'><div><b>iShares Prime Money Market ETF</b>Exchange Traded Fund <span>•</span> USA <span>•</span> AUM: 419.51M </div>] offsetx=[20] offsety=[-280] delay=[250]"><a href="quote.ashx?t=PMMF" class="tab-link">PMMF</a></td>
<td data-boxover="cssbody=[hoverchart] cssheader=[tabchrthdr] body=[<img  srcset='https://charts2-node.finviz.com/chart.ashx?cs=m&t=TRSY&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&o[[0]][[ot]]=sma&o[[0]][[op]]=50&o[[0]][[oc]]=FF8F33C6&o[[1]][[ot]]=sma&o[[1]][[op]]=200&o[[1]][[oc]]=DCB3326D&o[[2]][[ot]]=patterns&o[[2]][[op]]=&o[[2]][[oc]]=000 1x, https://charts2-node.finviz.com/chart.ashx?cs=m&t=TRSY&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&o[[0]][[ot]]=sma&o[[0]][[op]]=50&o[[0]][[oc]]=FF8F33C6&o[[1]][[ot]]=sma&o[[1]][[op]]=200&o[[1]][[oc]]=DCB3326D&o[[2]][[ot]]=patterns&o[[2]][[op]]=&o[[2]][[oc]]=000&sf=2 2x' width='464' height='230' alt='' loading='lazy'><div><b>Xtrackers US 0-1 Year Treasury ETF</b>Exchange Traded Fund <span>•</span> USA <span>•</span> AUM: 21.69M </div>] offsetx=[20] offsety=[-280] delay=[250]"><a href="quote.ashx?t=TRSY" class="tab-link">TRSY</a></td>
<td data-boxover="cssbody=[hoverchart] cssheader=[tabchrthdr] body=[<img  srcset='https://charts2-node.finviz.com/chart.ashx?cs=m&t=VGUS&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&o[[0]][[ot]]=sma&o[[0]][[op]]=50&o[[0]][[oc]]=FF8F33C6&o[[1]][[ot]]=sma&o[[1]][[op]]=200&o[[1]][[oc]]=DCB3326D&o[[2]][[ot]]=patterns&o[[2]][[op]]=&o[[2]][[oc]]=000 1x, https://charts2-node.finviz.com/chart.ashx?cs=m&t=VGUS&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&o[[0]][[ot]]=sma&o[[0]][[op]]=50&o[[0]][[oc]]=FF8F33C6&o[[1]][[ot]]=sma&o[[1]][[op]]=200&o[[1]][[oc]]=DCB3326D&o[[2]][[ot]]=patterns&o[[2]][[op]]=&o[[2]][[oc]]=000&sf=2 2x' width='464' height='230' alt='' loading='lazy'><div><b>Vanguard Ultra-Short Treasury ETF</b>Exchange Traded Fund <span>•</span> USA <span>•</span> AUM: 521.16M </div>] offsetx=[20] offsety=[-280] delay=[250]"><a href="quote.ashx?t=VGUS" class="tab-link">VGUS</a></td>
<td data-boxover="cssbody=[tooltip_short_bdy] cssheader=[tooltip_short_hdr] body=[Stocks with the current price near strong trendline support] offsetx=[10] offsety=[20] delay=[300]"><svg width="16" height="16">
    <rect x="0" y="0" width="16" height="16" rx="2" ry="2" class="fill-gray-50 dark:fill-gray-700" />
<use href="/assets/dist-icons/icons_signals.svg?rev=35#trendline-support-1" class="fill-blue-600 dark:fill-blue-300" />
<use href="/assets/dist-icons/icons_signals.svg?rev=35#trendline-support-2" class="fill-pink-400 dark:fill-pink-300" />
</svg><a href="screener.ashx?v=210&s=ta_p_tlsupport" class="tab-link-nw"><span class="signal-big-screen">Trendline</span><span class="signal-small-screen">TL</span> Supp.</a></td>
</tr>
<tr class="styled-row is-hoverable is-bordered is-rounded cursor-pointer" onclick="window.location='screener.ashx?v=210&s=ta_p_tlresistance'">
<td data-boxover="cssbody=[hoverchart] cssheader=[tabchrthdr] body=[<img  srcset='https://charts2-node.finviz.com/chart.ashx?cs=m&t=CSHI&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&o[[0]][[ot]]=sma&o[[0]][[op]]=50&o[[0]][[oc]]=FF8F33C6&o[[1]][[ot]]=sma&o[[1]][[op]]=200&o[[1]][[oc]]=DCB3326D&o[[2]][[ot]]=patterns&o[[2]][[op]]=&o[[2]][[oc]]=000 1x, https://charts2-node.finviz.com/chart.ashx?cs=m&t=CSHI&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&o[[0]][[ot]]=sma&o[[0]][[op]]=50&o[[0]][[oc]]=FF8F33C6&o[[1]][[ot]]=sma&o[[1]][[op]]=200&o[[1]][[oc]]=DCB3326D&o[[2]][[ot]]=patterns&o[[2]][[op]]=&o[[2]][[oc]]=000&sf=2 2x' width='464' height='230' alt='' loading='lazy'><div><b>NEOS Enhanced Income 1-3 Month T-Bill ETF</b>Exchange Traded Fund <span>•</span> USA <span>•</span> AUM: 765.02M </div>] offsetx=[20] offsety=[-280] delay=[250]"><a href="quote.ashx?t=CSHI" class="tab-link">CSHI</a></td>
<td data-boxover="cssbody=[hoverchart] cssheader=[tabchrthdr] body=[<img  srcset='https://charts2-node.finviz.com/chart.ashx?cs=m&t=IDUB&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&o[[0]][[ot]]=sma&o[[0]][[op]]=50&o[[0]][[oc]]=FF8F33C6&o[[1]][[ot]]=sma&o[[1]][[op]]=200&o[[1]][[oc]]=DCB3326D&o[[2]][[ot]]=patterns&o[[2]][[op]]=&o[[2]][[oc]]=000 1x, https://charts2-node.finviz.com/chart.ashx?cs=m&t=IDUB&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&o[[0]][[ot]]=sma&o[[0]][[op]]=50&o[[0]][[oc]]=FF8F33C6&o[[1]][[ot]]=sma&o[[1]][[op]]=200&o[[1]][[oc]]=DCB3326D&o[[2]][[ot]]=patterns&o[[2]][[op]]=&o[[2]][[oc]]=000&sf=2 2x' width='464' height='230' alt='' loading='lazy'><div><b>Aptus International Enhanced Yield ETF</b>Exchange Traded Fund <span>•</span> USA <span>•</span> AUM: 390.87M </div>] offsetx=[20] offsety=[-280] delay=[250]"><a href="quote.ashx?t=IDUB" class="tab-link">IDUB</a></td>
<td data-boxover="cssbody=[hoverchart] cssheader=[tabchrthdr] body=[<img  srcset='https://charts2-node.finviz.com/chart.ashx?cs=m&t=BSJP&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&o[[0]][[ot]]=sma&o[[0]][[op]]=50&o[[0]][[oc]]=FF8F33C6&o[[1]][[ot]]=sma&o[[1]][[op]]=200&o[[1]][[oc]]=DCB3326D&o[[2]][[ot]]=patterns&o[[2]][[op]]=&o[[2]][[oc]]=000 1x, https://charts2-node.finviz.com/chart.ashx?cs=m&t=BSJP&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&o[[0]][[ot]]=sma&o[[0]][[op]]=50&o[[0]][[oc]]=FF8F33C6&o[[1]][[ot]]=sma&o[[1]][[op]]=200&o[[1]][[oc]]=DCB3326D&o[[2]][[ot]]=patterns&o[[2]][[op]]=&o[[2]][[oc]]=000&sf=2 2x' width='464' height='230' alt='' loading='lazy'><div><b>Invesco BulletShares 2025 High Yield Corporate Bond ETF</b>Exchange Traded Fund <span>•</span> USA <span>•</span> AUM: 537.75M </div>] offsetx=[20] offsety=[-280] delay=[250]"><a href="quote.ashx?t=BSJP" class="tab-link">BSJP</a></td>
<td data-boxover="cssbody=[hoverchart] cssheader=[tabchrthdr] body=[<img  srcset='https://charts2-node.finviz.com/chart.ashx?cs=m&t=BKUI&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&o[[0]][[ot]]=sma&o[[0]][[op]]=50&o[[0]][[oc]]=FF8F33C6&o[[1]][[ot]]=sma&o[[1]][[op]]=200&o[[1]][[oc]]=DCB3326D&o[[2]][[ot]]=patterns&o[[2]][[op]]=&o[[2]][[oc]]=000 1x, https://charts2-node.finviz.com/chart.ashx?cs=m&t=BKUI&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&o[[0]][[ot]]=sma&o[[0]][[op]]=50&o[[0]][[oc]]=FF8F33C6&o[[1]][[ot]]=sma&o[[1]][[op]]=200&o[[1]][[oc]]=DCB3326D&o[[2]][[ot]]=patterns&o[[2]][[op]]=&o[[2]][[oc]]=000&sf=2 2x' width='464' height='230' alt='' loading='lazy'><div><b>BNY Mellon Ultra Short Income ETF</b>Exchange Traded Fund <span>•</span> USA <span>•</span> AUM: 231.71M </div>] offsetx=[20] offsety=[-280] delay=[250]"><a href="quote.ashx?t=BKUI" class="tab-link">BKUI</a></td>
<td data-boxover="cssbody=[tooltip_short_bdy] cssheader=[tooltip_short_hdr] body=[Stocks with the current price near strong trendline resistance] offsetx=[10] offsety=[20] delay=[300]"><svg width="16" height="16">
    <rect x="0" y="0" width="16" height="16" rx="2" ry="2" class="fill-gray-50 dark:fill-gray-700" />
<use href="/assets/dist-icons/icons_signals.svg?rev=35#trendline-resistance-1" class="fill-blue-600 dark:fill-blue-300" />
<use href="/assets/dist-icons/icons_signals.svg?rev=35#trendline-resistance-2" class="fill-pink-400 dark:fill-pink-300" />
</svg><a href="screener.ashx?v=210&s=ta_p_tlresistance" class="tab-link-nw"><span class="signal-big-screen">Trendline</span><span class="signal-small-screen">TL</span> Resist.</a></td>
</tr>
<tr class="styled-row is-hoverable is-bordered is-rounded cursor-pointer" onclick="window.location='screener.ashx?v=210&s=ta_p_horizontal'">
<td data-boxover="cssbody=[hoverchart] cssheader=[tabchrthdr] body=[<img  srcset='https://charts2-node.finviz.com/chart.ashx?cs=m&t=SOFR&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&o[[0]][[ot]]=sma&o[[0]][[op]]=50&o[[0]][[oc]]=FF8F33C6&o[[1]][[ot]]=sma&o[[1]][[op]]=200&o[[1]][[oc]]=DCB3326D&o[[2]][[ot]]=patterns&o[[2]][[op]]=&o[[2]][[oc]]=000 1x, https://charts2-node.finviz.com/chart.ashx?cs=m&t=SOFR&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&o[[0]][[ot]]=sma&o[[0]][[op]]=50&o[[0]][[oc]]=FF8F33C6&o[[1]][[ot]]=sma&o[[1]][[op]]=200&o[[1]][[oc]]=DCB3326D&o[[2]][[ot]]=patterns&o[[2]][[op]]=&o[[2]][[oc]]=000&sf=2 2x' width='464' height='230' alt='' loading='lazy'><div><b>Amplify Samsung SOFR ETF</b>Exchange Traded Fund <span>•</span> USA <span>•</span> AUM: 355.93M </div>] offsetx=[20] offsety=[-280] delay=[250]"><a href="quote.ashx?t=SOFR" class="tab-link">SOFR</a></td>
<td data-boxover="cssbody=[hoverchart] cssheader=[tabchrthdr] body=[<img  srcset='https://charts2-node.finviz.com/chart.ashx?cs=m&t=CSHI&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&o[[0]][[ot]]=sma&o[[0]][[op]]=50&o[[0]][[oc]]=FF8F33C6&o[[1]][[ot]]=sma&o[[1]][[op]]=200&o[[1]][[oc]]=DCB3326D&o[[2]][[ot]]=patterns&o[[2]][[op]]=&o[[2]][[oc]]=000 1x, https://charts2-node.finviz.com/chart.ashx?cs=m&t=CSHI&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&o[[0]][[ot]]=sma&o[[0]][[op]]=50&o[[0]][[oc]]=FF8F33C6&o[[1]][[ot]]=sma&o[[1]][[op]]=200&o[[1]][[oc]]=DCB3326D&o[[2]][[ot]]=patterns&o[[2]][[op]]=&o[[2]][[oc]]=000&sf=2 2x' width='464' height='230' alt='' loading='lazy'><div><b>NEOS Enhanced Income 1-3 Month T-Bill ETF</b>Exchange Traded Fund <span>•</span> USA <span>•</span> AUM: 765.02M </div>] offsetx=[20] offsety=[-280] delay=[250]"><a href="quote.ashx?t=CSHI" class="tab-link">CSHI</a></td>
<td data-boxover="cssbody=[hoverchart] cssheader=[tabchrthdr] body=[<img  srcset='https://charts2-node.finviz.com/chart.ashx?cs=m&t=PCLO&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&o[[0]][[ot]]=sma&o[[0]][[op]]=50&o[[0]][[oc]]=FF8F33C6&o[[1]][[ot]]=sma&o[[1]][[op]]=200&o[[1]][[oc]]=DCB3326D&o[[2]][[ot]]=patterns&o[[2]][[op]]=&o[[2]][[oc]]=000 1x, https://charts2-node.finviz.com/chart.ashx?cs=m&t=PCLO&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&o[[0]][[ot]]=sma&o[[0]][[op]]=50&o[[0]][[oc]]=FF8F33C6&o[[1]][[ot]]=sma&o[[1]][[op]]=200&o[[1]][[oc]]=DCB3326D&o[[2]][[ot]]=patterns&o[[2]][[op]]=&o[[2]][[oc]]=000&sf=2 2x' width='464' height='230' alt='' loading='lazy'><div><b>VIRTUS SEIX AAA Private Credit CLO ETF</b>Exchange Traded Fund <span>•</span> USA <span>•</span> AUM: 17.51M </div>] offsetx=[20] offsety=[-280] delay=[250]"><a href="quote.ashx?t=PCLO" class="tab-link">PCLO</a></td>
<td data-boxover="cssbody=[hoverchart] cssheader=[tabchrthdr] body=[<img  srcset='https://charts2-node.finviz.com/chart.ashx?cs=m&t=TRSY&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&o[[0]][[ot]]=sma&o[[0]][[op]]=50&o[[0]][[oc]]=FF8F33C6&o[[1]][[ot]]=sma&o[[1]][[op]]=200&o[[1]][[oc]]=DCB3326D&o[[2]][[ot]]=patterns&o[[2]][[op]]=&o[[2]][[oc]]=000 1x, https://charts2-node.finviz.com/chart.ashx?cs=m&t=TRSY&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&o[[0]][[ot]]=sma&o[[0]][[op]]=50&o[[0]][[oc]]=FF8F33C6&o[[1]][[ot]]=sma&o[[1]][[op]]=200&o[[1]][[oc]]=DCB3326D&o[[2]][[ot]]=patterns&o[[2]][[op]]=&o[[2]][[oc]]=000&sf=2 2x' width='464' height='230' alt='' loading='lazy'><div><b>Xtrackers US 0-1 Year Treasury ETF</b>Exchange Traded Fund <span>•</span> USA <span>•</span> AUM: 21.69M </div>] offsetx=[20] offsety=[-280] delay=[250]"><a href="quote.ashx?t=TRSY" class="tab-link">TRSY</a></td>
<td data-boxover="cssbody=[tooltip_short_bdy] cssheader=[tooltip_short_hdr] body=[Stocks with the current price near strong horizontal support/resistance] offsetx=[10] offsety=[20] delay=[300]"><svg width="16" height="16">
    <rect x="0" y="0" width="16" height="16" rx="2" ry="2" class="fill-gray-50 dark:fill-gray-700" />
<use href="/assets/dist-icons/icons_signals.svg?rev=35#horizontal-sr-1" class="fill-blue-600 dark:fill-blue-300" />
<use href="/assets/dist-icons/icons_signals.svg?rev=35#horizontal-sr-2" class="fill-pink-400 dark:fill-pink-300" />
</svg><a href="screener.ashx?v=210&s=ta_p_horizontal" class="tab-link-nw">Horizontal S/R</a></td>
</tr>
<tr class="styled-row is-hoverable is-bordered is-rounded cursor-pointer" onclick="window.location='screener.ashx?v=210&s=ta_p_wedgeup'">
<td data-boxover="cssbody=[hoverchart] cssheader=[tabchrthdr] body=[<img  srcset='https://charts2-node.finviz.com/chart.ashx?cs=m&t=DCRE&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&o[[0]][[ot]]=sma&o[[0]][[op]]=50&o[[0]][[oc]]=FF8F33C6&o[[1]][[ot]]=sma&o[[1]][[op]]=200&o[[1]][[oc]]=DCB3326D&o[[2]][[ot]]=patterns&o[[2]][[op]]=&o[[2]][[oc]]=000 1x, https://charts2-node.finviz.com/chart.ashx?cs=m&t=DCRE&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&o[[0]][[ot]]=sma&o[[0]][[op]]=50&o[[0]][[oc]]=FF8F33C6&o[[1]][[ot]]=sma&o[[1]][[op]]=200&o[[1]][[oc]]=DCB3326D&o[[2]][[ot]]=patterns&o[[2]][[op]]=&o[[2]][[oc]]=000&sf=2 2x' width='464' height='230' alt='' loading='lazy'><div><b>DoubleLine Commercial Real Estate ETF</b>Exchange Traded Fund <span>•</span> USA <span>•</span> AUM: 334.99M </div>] offsetx=[20] offsety=[-280] delay=[250]"><a href="quote.ashx?t=DCRE" class="tab-link">DCRE</a></td>
<td data-boxover="cssbody=[hoverchart] cssheader=[tabchrthdr] body=[<img  srcset='https://charts2-node.finviz.com/chart.ashx?cs=m&t=EWK&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&o[[0]][[ot]]=sma&o[[0]][[op]]=50&o[[0]][[oc]]=FF8F33C6&o[[1]][[ot]]=sma&o[[1]][[op]]=200&o[[1]][[oc]]=DCB3326D&o[[2]][[ot]]=patterns&o[[2]][[op]]=&o[[2]][[oc]]=000 1x, https://charts2-node.finviz.com/chart.ashx?cs=m&t=EWK&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&o[[0]][[ot]]=sma&o[[0]][[op]]=50&o[[0]][[oc]]=FF8F33C6&o[[1]][[ot]]=sma&o[[1]][[op]]=200&o[[1]][[oc]]=DCB3326D&o[[2]][[ot]]=patterns&o[[2]][[op]]=&o[[2]][[oc]]=000&sf=2 2x' width='464' height='230' alt='' loading='lazy'><div><b>iShares MSCI Belgium ETF</b>Exchange Traded Fund <span>•</span> USA <span>•</span> AUM: 31.08M </div>] offsetx=[20] offsety=[-280] delay=[250]"><a href="quote.ashx?t=EWK" class="tab-link">EWK</a></td>
<td data-boxover="cssbody=[hoverchart] cssheader=[tabchrthdr] body=[<img  srcset='https://charts2-node.finviz.com/chart.ashx?cs=m&t=FTS&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&o[[0]][[ot]]=sma&o[[0]][[op]]=50&o[[0]][[oc]]=FF8F33C6&o[[1]][[ot]]=sma&o[[1]][[op]]=200&o[[1]][[oc]]=DCB3326D&o[[2]][[ot]]=patterns&o[[2]][[op]]=&o[[2]][[oc]]=000 1x, https://charts2-node.finviz.com/chart.ashx?cs=m&t=FTS&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&o[[0]][[ot]]=sma&o[[0]][[op]]=50&o[[0]][[oc]]=FF8F33C6&o[[1]][[ot]]=sma&o[[1]][[op]]=200&o[[1]][[oc]]=DCB3326D&o[[2]][[ot]]=patterns&o[[2]][[op]]=&o[[2]][[oc]]=000&sf=2 2x' width='464' height='230' alt='' loading='lazy'><div><b>Fortis Inc</b>Utilities - Regulated Electric <span>•</span> Canada <span>•</span> 25.76B </div>] offsetx=[20] offsety=[-280] delay=[250]"><a href="quote.ashx?t=FTS" class="tab-link">FTS</a></td>
<td data-boxover="cssbody=[hoverchart] cssheader=[tabchrthdr] body=[<img  srcset='https://charts2-node.finviz.com/chart.ashx?cs=m&t=TM&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&o[[0]][[ot]]=sma&o[[0]][[op]]=50&o[[0]][[oc]]=FF8F33C6&o[[1]][[ot]]=sma&o[[1]][[op]]=200&o[[1]][[oc]]=DCB3326D&o[[2]][[ot]]=patterns&o[[2]][[op]]=&o[[2]][[oc]]=000 1x, https://charts2-node.finviz.com/chart.ashx?cs=m&t=TM&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&o[[0]][[ot]]=sma&o[[0]][[op]]=50&o[[0]][[oc]]=FF8F33C6&o[[1]][[ot]]=sma&o[[1]][[op]]=200&o[[1]][[oc]]=DCB3326D&o[[2]][[ot]]=patterns&o[[2]][[op]]=&o[[2]][[oc]]=000&sf=2 2x' width='464' height='230' alt='' loading='lazy'><div><b>Toyota Motor Corporation ADR</b>Auto Manufacturers <span>•</span> Japan <span>•</span> 271.25B </div>] offsetx=[20] offsety=[-280] delay=[250]"><a href="quote.ashx?t=TM" class="tab-link">TM</a></td>
<td data-boxover="cssbody=[tooltip_short_bdy] cssheader=[tooltip_short_hdr] body=[Stocks with the current price near strong wedge-up pattern] offsetx=[10] offsety=[20] delay=[300]"><svg width="16" height="16">
    <rect x="0" y="0" width="16" height="16" rx="2" ry="2" class="fill-gray-50 dark:fill-gray-700" />
<use href="/assets/dist-icons/icons_signals.svg?rev=35#wedge-up-1" class="fill-blue-600 dark:fill-blue-300" />
<use href="/assets/dist-icons/icons_signals.svg?rev=35#wedge-up-2" class="fill-pink-400 dark:fill-pink-300" />
</svg><a href="screener.ashx?v=210&s=ta_p_wedgeup" class="tab-link-nw">Wedge Up</a></td>
</tr>
<tr class="styled-row is-hoverable is-bordered is-rounded cursor-pointer" onclick="window.location='screener.ashx?v=210&s=ta_p_wedge'">
<td data-boxover="cssbody=[hoverchart] cssheader=[tabchrthdr] body=[<img  srcset='https://charts2-node.finviz.com/chart.ashx?cs=m&t=BSJX&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&o[[0]][[ot]]=sma&o[[0]][[op]]=50&o[[0]][[oc]]=FF8F33C6&o[[1]][[ot]]=sma&o[[1]][[op]]=200&o[[1]][[oc]]=DCB3326D&o[[2]][[ot]]=patterns&o[[2]][[op]]=&o[[2]][[oc]]=000 1x, https://charts2-node.finviz.com/chart.ashx?cs=m&t=BSJX&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&o[[0]][[ot]]=sma&o[[0]][[op]]=50&o[[0]][[oc]]=FF8F33C6&o[[1]][[ot]]=sma&o[[1]][[op]]=200&o[[1]][[oc]]=DCB3326D&o[[2]][[ot]]=patterns&o[[2]][[op]]=&o[[2]][[oc]]=000&sf=2 2x' width='464' height='230' alt='' loading='lazy'><div><b>Invesco BulletShares 2033 High Yield Corporate Bond ETF</b>Exchange Traded Fund <span>•</span> USA <span>•</span> AUM: 5.11M </div>] offsetx=[20] offsety=[-280] delay=[250]"><a href="quote.ashx?t=BSJX" class="tab-link">BSJX</a></td>
<td data-boxover="cssbody=[hoverchart] cssheader=[tabchrthdr] body=[<img  srcset='https://charts2-node.finviz.com/chart.ashx?cs=m&t=SPCE&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&o[[0]][[ot]]=sma&o[[0]][[op]]=50&o[[0]][[oc]]=FF8F33C6&o[[1]][[ot]]=sma&o[[1]][[op]]=200&o[[1]][[oc]]=DCB3326D&o[[2]][[ot]]=patterns&o[[2]][[op]]=&o[[2]][[oc]]=000 1x, https://charts2-node.finviz.com/chart.ashx?cs=m&t=SPCE&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&o[[0]][[ot]]=sma&o[[0]][[op]]=50&o[[0]][[oc]]=FF8F33C6&o[[1]][[ot]]=sma&o[[1]][[op]]=200&o[[1]][[oc]]=DCB3326D&o[[2]][[ot]]=patterns&o[[2]][[op]]=&o[[2]][[oc]]=000&sf=2 2x' width='464' height='230' alt='' loading='lazy'><div><b>Virgin Galactic Holdings Inc</b>Aerospace & Defense <span>•</span> USA <span>•</span> 204.77M </div>] offsetx=[20] offsety=[-280] delay=[250]"><a href="quote.ashx?t=SPCE" class="tab-link">SPCE</a></td>
<td data-boxover="cssbody=[hoverchart] cssheader=[tabchrthdr] body=[<img  srcset='https://charts2-node.finviz.com/chart.ashx?cs=m&t=DNUT&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&o[[0]][[ot]]=sma&o[[0]][[op]]=50&o[[0]][[oc]]=FF8F33C6&o[[1]][[ot]]=sma&o[[1]][[op]]=200&o[[1]][[oc]]=DCB3326D&o[[2]][[ot]]=patterns&o[[2]][[op]]=&o[[2]][[oc]]=000 1x, https://charts2-node.finviz.com/chart.ashx?cs=m&t=DNUT&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&o[[0]][[ot]]=sma&o[[0]][[op]]=50&o[[0]][[oc]]=FF8F33C6&o[[1]][[ot]]=sma&o[[1]][[op]]=200&o[[1]][[oc]]=DCB3326D&o[[2]][[ot]]=patterns&o[[2]][[op]]=&o[[2]][[oc]]=000&sf=2 2x' width='464' height='230' alt='' loading='lazy'><div><b>Krispy Kreme Inc</b>Grocery Stores <span>•</span> USA <span>•</span> 753.72M </div>] offsetx=[20] offsety=[-280] delay=[250]"><a href="quote.ashx?t=DNUT" class="tab-link">DNUT</a></td>
<td data-boxover="cssbody=[hoverchart] cssheader=[tabchrthdr] body=[<img  srcset='https://charts2-node.finviz.com/chart.ashx?cs=m&t=VEGI&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&o[[0]][[ot]]=sma&o[[0]][[op]]=50&o[[0]][[oc]]=FF8F33C6&o[[1]][[ot]]=sma&o[[1]][[op]]=200&o[[1]][[oc]]=DCB3326D&o[[2]][[ot]]=patterns&o[[2]][[op]]=&o[[2]][[oc]]=000 1x, https://charts2-node.finviz.com/chart.ashx?cs=m&t=VEGI&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&o[[0]][[ot]]=sma&o[[0]][[op]]=50&o[[0]][[oc]]=FF8F33C6&o[[1]][[ot]]=sma&o[[1]][[op]]=200&o[[1]][[oc]]=DCB3326D&o[[2]][[ot]]=patterns&o[[2]][[op]]=&o[[2]][[oc]]=000&sf=2 2x' width='464' height='230' alt='' loading='lazy'><div><b>iShares MSCI Agriculture Producers ETF</b>Exchange Traded Fund <span>•</span> USA <span>•</span> AUM: 87.24M </div>] offsetx=[20] offsety=[-280] delay=[250]"><a href="quote.ashx?t=VEGI" class="tab-link">VEGI</a></td>
<td data-boxover="cssbody=[tooltip_short_bdy] cssheader=[tooltip_short_hdr] body=[Stocks with the current price near strong wedge pattern] offsetx=[10] offsety=[20] delay=[300]"><svg width="16" height="16">
    <rect x="0" y="0" width="16" height="16" rx="2" ry="2" class="fill-gray-50 dark:fill-gray-700" />
<use href="/assets/dist-icons/icons_signals.svg?rev=35#wedge-1" class="fill-blue-600 dark:fill-blue-300" />
<use href="/assets/dist-icons/icons_signals.svg?rev=35#wedge-2" class="fill-pink-400 dark:fill-pink-300" />
</svg><a href="screener.ashx?v=210&s=ta_p_wedge" class="tab-link-nw">Wedge</a></td>
</tr>
<tr class="styled-row is-hoverable is-bordered is-rounded cursor-pointer" onclick="window.location='screener.ashx?v=210&s=ta_p_wedgedown'">
<td data-boxover="cssbody=[hoverchart] cssheader=[tabchrthdr] body=[<img  srcset='https://charts2-node.finviz.com/chart.ashx?cs=m&t=EXFY&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&o[[0]][[ot]]=sma&o[[0]][[op]]=50&o[[0]][[oc]]=FF8F33C6&o[[1]][[ot]]=sma&o[[1]][[op]]=200&o[[1]][[oc]]=DCB3326D&o[[2]][[ot]]=patterns&o[[2]][[op]]=&o[[2]][[oc]]=000 1x, https://charts2-node.finviz.com/chart.ashx?cs=m&t=EXFY&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&o[[0]][[ot]]=sma&o[[0]][[op]]=50&o[[0]][[oc]]=FF8F33C6&o[[1]][[ot]]=sma&o[[1]][[op]]=200&o[[1]][[oc]]=DCB3326D&o[[2]][[ot]]=patterns&o[[2]][[op]]=&o[[2]][[oc]]=000&sf=2 2x' width='464' height='230' alt='' loading='lazy'><div><b>Expensify Inc</b>Software - Application <span>•</span> USA <span>•</span> 149.79M </div>] offsetx=[20] offsety=[-280] delay=[250]"><a href="quote.ashx?t=EXFY" class="tab-link">EXFY</a></td>
<td data-boxover="cssbody=[hoverchart] cssheader=[tabchrthdr] body=[<img  srcset='https://charts2-node.finviz.com/chart.ashx?cs=m&t=SKYQ&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&o[[0]][[ot]]=sma&o[[0]][[op]]=50&o[[0]][[oc]]=FF8F33C6&o[[1]][[ot]]=sma&o[[1]][[op]]=200&o[[1]][[oc]]=DCB3326D&o[[2]][[ot]]=patterns&o[[2]][[op]]=&o[[2]][[oc]]=000 1x, https://charts2-node.finviz.com/chart.ashx?cs=m&t=SKYQ&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&o[[0]][[ot]]=sma&o[[0]][[op]]=50&o[[0]][[oc]]=FF8F33C6&o[[1]][[ot]]=sma&o[[1]][[op]]=200&o[[1]][[oc]]=DCB3326D&o[[2]][[ot]]=patterns&o[[2]][[op]]=&o[[2]][[oc]]=000&sf=2 2x' width='464' height='230' alt='' loading='lazy'><div><b>Sky Quarry Inc</b>Oil & Gas Integrated <span>•</span> USA <span>•</span> 8.99M </div>] offsetx=[20] offsety=[-280] delay=[250]"><a href="quote.ashx?t=SKYQ" class="tab-link">SKYQ</a></td>
<td data-boxover="cssbody=[hoverchart] cssheader=[tabchrthdr] body=[<img  srcset='https://charts2-node.finviz.com/chart.ashx?cs=m&t=WXET&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&o[[0]][[ot]]=sma&o[[0]][[op]]=50&o[[0]][[oc]]=FF8F33C6&o[[1]][[ot]]=sma&o[[1]][[op]]=200&o[[1]][[oc]]=DCB3326D&o[[2]][[ot]]=patterns&o[[2]][[op]]=&o[[2]][[oc]]=000 1x, https://charts2-node.finviz.com/chart.ashx?cs=m&t=WXET&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&o[[0]][[ot]]=sma&o[[0]][[op]]=50&o[[0]][[oc]]=FF8F33C6&o[[1]][[ot]]=sma&o[[1]][[op]]=200&o[[1]][[oc]]=DCB3326D&o[[2]][[ot]]=patterns&o[[2]][[op]]=&o[[2]][[oc]]=000&sf=2 2x' width='464' height='230' alt='' loading='lazy'><div><b>Teucrium 2x Daily Wheat ETF</b>Exchange Traded Fund <span>•</span> USA <span>•</span> AUM: 0.64M </div>] offsetx=[20] offsety=[-280] delay=[250]"><a href="quote.ashx?t=WXET" class="tab-link">WXET</a></td>
<td data-boxover="cssbody=[hoverchart] cssheader=[tabchrthdr] body=[<img  srcset='https://charts2-node.finviz.com/chart.ashx?cs=m&t=XOMO&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&o[[0]][[ot]]=sma&o[[0]][[op]]=50&o[[0]][[oc]]=FF8F33C6&o[[1]][[ot]]=sma&o[[1]][[op]]=200&o[[1]][[oc]]=DCB3326D&o[[2]][[ot]]=patterns&o[[2]][[op]]=&o[[2]][[oc]]=000 1x, https://charts2-node.finviz.com/chart.ashx?cs=m&t=XOMO&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&o[[0]][[ot]]=sma&o[[0]][[op]]=50&o[[0]][[oc]]=FF8F33C6&o[[1]][[ot]]=sma&o[[1]][[op]]=200&o[[1]][[oc]]=DCB3326D&o[[2]][[ot]]=patterns&o[[2]][[op]]=&o[[2]][[oc]]=000&sf=2 2x' width='464' height='230' alt='' loading='lazy'><div><b>YieldMax XOM Option Income Strategy ETF</b>Exchange Traded Fund <span>•</span> USA <span>•</span> AUM: 41.83M </div>] offsetx=[20] offsety=[-280] delay=[250]"><a href="quote.ashx?t=XOMO" class="tab-link">XOMO</a></td>
<td data-boxover="cssbody=[tooltip_short_bdy] cssheader=[tooltip_short_hdr] body=[Stocks with the current price near strong wedge-down pattern] offsetx=[10] offsety=[20] delay=[300]"><svg width="16" height="16">
    <rect x="0" y="0" width="16" height="16" rx="2" ry="2" class="fill-gray-50 dark:fill-gray-700" />
<use href="/assets/dist-icons/icons_signals.svg?rev=35#wedge-down-1" class="fill-blue-600 dark:fill-blue-300" />
<use href="/assets/dist-icons/icons_signals.svg?rev=35#wedge-down-2" class="fill-pink-400 dark:fill-pink-300" />
</svg><a href="screener.ashx?v=210&s=ta_p_wedgedown" class="tab-link-nw">Wedge Down</a></td>
</tr>
<tr class="styled-row is-hoverable is-bordered is-rounded cursor-pointer" onclick="window.location='screener.ashx?v=210&s=ta_p_wedgeresistance'">
<td data-boxover="cssbody=[hoverchart] cssheader=[tabchrthdr] body=[<img  srcset='https://charts2-node.finviz.com/chart.ashx?cs=m&t=VRIG&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&o[[0]][[ot]]=sma&o[[0]][[op]]=50&o[[0]][[oc]]=FF8F33C6&o[[1]][[ot]]=sma&o[[1]][[op]]=200&o[[1]][[oc]]=DCB3326D&o[[2]][[ot]]=patterns&o[[2]][[op]]=&o[[2]][[oc]]=000 1x, https://charts2-node.finviz.com/chart.ashx?cs=m&t=VRIG&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&o[[0]][[ot]]=sma&o[[0]][[op]]=50&o[[0]][[oc]]=FF8F33C6&o[[1]][[ot]]=sma&o[[1]][[op]]=200&o[[1]][[oc]]=DCB3326D&o[[2]][[ot]]=patterns&o[[2]][[op]]=&o[[2]][[oc]]=000&sf=2 2x' width='464' height='230' alt='' loading='lazy'><div><b>Invesco Variable Rate Investment Grade ETF</b>Exchange Traded Fund <span>•</span> USA <span>•</span> AUM: 1.36B </div>] offsetx=[20] offsety=[-280] delay=[250]"><a href="quote.ashx?t=VRIG" class="tab-link">VRIG</a></td>
<td data-boxover="cssbody=[hoverchart] cssheader=[tabchrthdr] body=[<img  srcset='https://charts2-node.finviz.com/chart.ashx?cs=m&t=RFMZ&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&o[[0]][[ot]]=sma&o[[0]][[op]]=50&o[[0]][[oc]]=FF8F33C6&o[[1]][[ot]]=sma&o[[1]][[op]]=200&o[[1]][[oc]]=DCB3326D&o[[2]][[ot]]=patterns&o[[2]][[op]]=&o[[2]][[oc]]=000 1x, https://charts2-node.finviz.com/chart.ashx?cs=m&t=RFMZ&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&o[[0]][[ot]]=sma&o[[0]][[op]]=50&o[[0]][[oc]]=FF8F33C6&o[[1]][[ot]]=sma&o[[1]][[op]]=200&o[[1]][[oc]]=DCB3326D&o[[2]][[ot]]=patterns&o[[2]][[op]]=&o[[2]][[oc]]=000&sf=2 2x' width='464' height='230' alt='' loading='lazy'><div><b>RiverNorth Flexible Municipal Income Fund II Inc</b>Asset Management <span>•</span> USA <span>•</span> - </div>] offsetx=[20] offsety=[-280] delay=[250]"><a href="quote.ashx?t=RFMZ" class="tab-link">RFMZ</a></td>
<td data-boxover="cssbody=[hoverchart] cssheader=[tabchrthdr] body=[<img  srcset='https://charts2-node.finviz.com/chart.ashx?cs=m&t=XRMI&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&o[[0]][[ot]]=sma&o[[0]][[op]]=50&o[[0]][[oc]]=FF8F33C6&o[[1]][[ot]]=sma&o[[1]][[op]]=200&o[[1]][[oc]]=DCB3326D&o[[2]][[ot]]=patterns&o[[2]][[op]]=&o[[2]][[oc]]=000 1x, https://charts2-node.finviz.com/chart.ashx?cs=m&t=XRMI&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&o[[0]][[ot]]=sma&o[[0]][[op]]=50&o[[0]][[oc]]=FF8F33C6&o[[1]][[ot]]=sma&o[[1]][[op]]=200&o[[1]][[oc]]=DCB3326D&o[[2]][[ot]]=patterns&o[[2]][[op]]=&o[[2]][[oc]]=000&sf=2 2x' width='464' height='230' alt='' loading='lazy'><div><b>Global X S&P 500 Risk Managed Income ETF</b>Exchange Traded Fund <span>•</span> USA <span>•</span> AUM: 43.71M </div>] offsetx=[20] offsety=[-280] delay=[250]"><a href="quote.ashx?t=XRMI" class="tab-link">XRMI</a></td>
<td data-boxover="cssbody=[hoverchart] cssheader=[tabchrthdr] body=[<img  srcset='https://charts2-node.finviz.com/chart.ashx?cs=m&t=DWX&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&o[[0]][[ot]]=sma&o[[0]][[op]]=50&o[[0]][[oc]]=FF8F33C6&o[[1]][[ot]]=sma&o[[1]][[op]]=200&o[[1]][[oc]]=DCB3326D&o[[2]][[ot]]=patterns&o[[2]][[op]]=&o[[2]][[oc]]=000 1x, https://charts2-node.finviz.com/chart.ashx?cs=m&t=DWX&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&o[[0]][[ot]]=sma&o[[0]][[op]]=50&o[[0]][[oc]]=FF8F33C6&o[[1]][[ot]]=sma&o[[1]][[op]]=200&o[[1]][[oc]]=DCB3326D&o[[2]][[ot]]=patterns&o[[2]][[op]]=&o[[2]][[oc]]=000&sf=2 2x' width='464' height='230' alt='' loading='lazy'><div><b>SPDR S&P International Dividend ETF</b>Exchange Traded Fund <span>•</span> USA <span>•</span> AUM: 496.62M </div>] offsetx=[20] offsety=[-280] delay=[250]"><a href="quote.ashx?t=DWX" class="tab-link">DWX</a></td>
<td data-boxover="cssbody=[tooltip_short_bdy] cssheader=[tooltip_short_hdr] body=[Stocks with the current price near strong ascending triangle pattern] offsetx=[10] offsety=[20] delay=[300]"><svg width="16" height="16">
    <rect x="0" y="0" width="16" height="16" rx="2" ry="2" class="fill-gray-50 dark:fill-gray-700" />
<use href="/assets/dist-icons/icons_signals.svg?rev=35#triangle-asc-1" class="fill-blue-600 dark:fill-blue-300" />
<use href="/assets/dist-icons/icons_signals.svg?rev=35#triangle-asc-2" class="fill-pink-400 dark:fill-pink-300" />
</svg><a href="screener.ashx?v=210&s=ta_p_wedgeresistance" class="tab-link-nw">Triangle <span class="signal-big-screen">Asc.</span><span class="signal-small-screen">Asc.</span></a></td>
</tr>
<tr class="styled-row is-hoverable is-bordered is-rounded cursor-pointer" onclick="window.location='screener.ashx?v=210&s=ta_p_wedgesupport'">
<td data-boxover="cssbody=[hoverchart] cssheader=[tabchrthdr] body=[<img  srcset='https://charts2-node.finviz.com/chart.ashx?cs=m&t=FWRG&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&o[[0]][[ot]]=sma&o[[0]][[op]]=50&o[[0]][[oc]]=FF8F33C6&o[[1]][[ot]]=sma&o[[1]][[op]]=200&o[[1]][[oc]]=DCB3326D&o[[2]][[ot]]=patterns&o[[2]][[op]]=&o[[2]][[oc]]=000 1x, https://charts2-node.finviz.com/chart.ashx?cs=m&t=FWRG&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&o[[0]][[ot]]=sma&o[[0]][[op]]=50&o[[0]][[oc]]=FF8F33C6&o[[1]][[ot]]=sma&o[[1]][[op]]=200&o[[1]][[oc]]=DCB3326D&o[[2]][[ot]]=patterns&o[[2]][[op]]=&o[[2]][[oc]]=000&sf=2 2x' width='464' height='230' alt='' loading='lazy'><div><b>First Watch Restaurant Group Inc</b>Restaurants <span>•</span> USA <span>•</span> 998.49M </div>] offsetx=[20] offsety=[-280] delay=[250]"><a href="quote.ashx?t=FWRG" class="tab-link">FWRG</a></td>
<td data-boxover="cssbody=[hoverchart] cssheader=[tabchrthdr] body=[<img  srcset='https://charts2-node.finviz.com/chart.ashx?cs=m&t=IRET&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&o[[0]][[ot]]=sma&o[[0]][[op]]=50&o[[0]][[oc]]=FF8F33C6&o[[1]][[ot]]=sma&o[[1]][[op]]=200&o[[1]][[oc]]=DCB3326D&o[[2]][[ot]]=patterns&o[[2]][[op]]=&o[[2]][[oc]]=000 1x, https://charts2-node.finviz.com/chart.ashx?cs=m&t=IRET&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&o[[0]][[ot]]=sma&o[[0]][[op]]=50&o[[0]][[oc]]=FF8F33C6&o[[1]][[ot]]=sma&o[[1]][[op]]=200&o[[1]][[oc]]=DCB3326D&o[[2]][[ot]]=patterns&o[[2]][[op]]=&o[[2]][[oc]]=000&sf=2 2x' width='464' height='230' alt='' loading='lazy'><div><b>iREIT - MarketVector Quality REIT Index ETF</b>Exchange Traded Fund <span>•</span> USA <span>•</span> AUM: 3.32M </div>] offsetx=[20] offsety=[-280] delay=[250]"><a href="quote.ashx?t=IRET" class="tab-link">IRET</a></td>
<td data-boxover="cssbody=[hoverchart] cssheader=[tabchrthdr] body=[<img  srcset='https://charts2-node.finviz.com/chart.ashx?cs=m&t=IPHA&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&o[[0]][[ot]]=sma&o[[0]][[op]]=50&o[[0]][[oc]]=FF8F33C6&o[[1]][[ot]]=sma&o[[1]][[op]]=200&o[[1]][[oc]]=DCB3326D&o[[2]][[ot]]=patterns&o[[2]][[op]]=&o[[2]][[oc]]=000 1x, https://charts2-node.finviz.com/chart.ashx?cs=m&t=IPHA&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&o[[0]][[ot]]=sma&o[[0]][[op]]=50&o[[0]][[oc]]=FF8F33C6&o[[1]][[ot]]=sma&o[[1]][[op]]=200&o[[1]][[oc]]=DCB3326D&o[[2]][[ot]]=patterns&o[[2]][[op]]=&o[[2]][[oc]]=000&sf=2 2x' width='464' height='230' alt='' loading='lazy'><div><b>Innate Pharma ADR</b>Biotechnology <span>•</span> France <span>•</span> 171.44M </div>] offsetx=[20] offsety=[-280] delay=[250]"><a href="quote.ashx?t=IPHA" class="tab-link">IPHA</a></td>
<td data-boxover="cssbody=[hoverchart] cssheader=[tabchrthdr] body=[<img  srcset='https://charts2-node.finviz.com/chart.ashx?cs=m&t=FNKO&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&o[[0]][[ot]]=sma&o[[0]][[op]]=50&o[[0]][[oc]]=FF8F33C6&o[[1]][[ot]]=sma&o[[1]][[op]]=200&o[[1]][[oc]]=DCB3326D&o[[2]][[ot]]=patterns&o[[2]][[op]]=&o[[2]][[oc]]=000 1x, https://charts2-node.finviz.com/chart.ashx?cs=m&t=FNKO&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&o[[0]][[ot]]=sma&o[[0]][[op]]=50&o[[0]][[oc]]=FF8F33C6&o[[1]][[ot]]=sma&o[[1]][[op]]=200&o[[1]][[oc]]=DCB3326D&o[[2]][[ot]]=patterns&o[[2]][[op]]=&o[[2]][[oc]]=000&sf=2 2x' width='464' height='230' alt='' loading='lazy'><div><b>Funko Inc</b>Leisure <span>•</span> USA <span>•</span> 178.36M </div>] offsetx=[20] offsety=[-280] delay=[250]"><a href="quote.ashx?t=FNKO" class="tab-link">FNKO</a></td>
<td data-boxover="cssbody=[tooltip_short_bdy] cssheader=[tooltip_short_hdr] body=[Stocks with the current price near strong descending triangle pattern] offsetx=[10] offsety=[20] delay=[300]"><svg width="16" height="16">
    <rect x="0" y="0" width="16" height="16" rx="2" ry="2" class="fill-gray-50 dark:fill-gray-700" />
<use href="/assets/dist-icons/icons_signals.svg?rev=35#triangle-desc-1" class="fill-blue-600 dark:fill-blue-300" />
<use href="/assets/dist-icons/icons_signals.svg?rev=35#triangle-desc-2" class="fill-pink-400 dark:fill-pink-300" />
</svg><a href="screener.ashx?v=210&s=ta_p_wedgesupport" class="tab-link-nw">Triangle <span class="signal-big-screen">Desc.</span><span class="signal-small-screen">Desc.</span></a></td>
</tr>
</table>
</td>
<td class="hp_spacer"><img src="gfx/nic2x2.gif" style="width:16px;height:2px" alt="" border="0"></td>
<td width="50%" valign="top">
<table class="styled-table-new is-rounded is-condensed hp_signal-table" width="100%" cellpadding="1" cellspacing="0" border="0">
<thead><tr>
<th class="text-left" colspan="4">Tickers</th><th class="text-left"> Signal</th>
</tr></thead><tr class="styled-row is-hoverable is-bordered is-rounded cursor-pointer" onclick="window.location='screener.ashx?v=210&s=ta_p_channelup'">
<td data-boxover="cssbody=[hoverchart] cssheader=[tabchrthdr] body=[<img  srcset='https://charts2-node.finviz.com/chart.ashx?cs=m&t=PMMF&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&o[[0]][[ot]]=sma&o[[0]][[op]]=50&o[[0]][[oc]]=FF8F33C6&o[[1]][[ot]]=sma&o[[1]][[op]]=200&o[[1]][[oc]]=DCB3326D&o[[2]][[ot]]=patterns&o[[2]][[op]]=&o[[2]][[oc]]=000 1x, https://charts2-node.finviz.com/chart.ashx?cs=m&t=PMMF&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&o[[0]][[ot]]=sma&o[[0]][[op]]=50&o[[0]][[oc]]=FF8F33C6&o[[1]][[ot]]=sma&o[[1]][[op]]=200&o[[1]][[oc]]=DCB3326D&o[[2]][[ot]]=patterns&o[[2]][[op]]=&o[[2]][[oc]]=000&sf=2 2x' width='464' height='230' alt='' loading='lazy'><div><b>iShares Prime Money Market ETF</b>Exchange Traded Fund <span>•</span> USA <span>•</span> AUM: 419.51M </div>] offsetx=[20] offsety=[-280] delay=[250]"><a href="quote.ashx?t=PMMF" class="tab-link">PMMF</a></td>
<td data-boxover="cssbody=[hoverchart] cssheader=[tabchrthdr] body=[<img  srcset='https://charts2-node.finviz.com/chart.ashx?cs=m&t=EVSB&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&o[[0]][[ot]]=sma&o[[0]][[op]]=50&o[[0]][[oc]]=FF8F33C6&o[[1]][[ot]]=sma&o[[1]][[op]]=200&o[[1]][[oc]]=DCB3326D&o[[2]][[ot]]=patterns&o[[2]][[op]]=&o[[2]][[oc]]=000 1x, https://charts2-node.finviz.com/chart.ashx?cs=m&t=EVSB&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&o[[0]][[ot]]=sma&o[[0]][[op]]=50&o[[0]][[oc]]=FF8F33C6&o[[1]][[ot]]=sma&o[[1]][[op]]=200&o[[1]][[oc]]=DCB3326D&o[[2]][[ot]]=patterns&o[[2]][[op]]=&o[[2]][[oc]]=000&sf=2 2x' width='464' height='230' alt='' loading='lazy'><div><b>Eaton Vance Ultra-Short Income ETF</b>Exchange Traded Fund <span>•</span> USA <span>•</span> AUM: 252.65M </div>] offsetx=[20] offsety=[-280] delay=[250]"><a href="quote.ashx?t=EVSB" class="tab-link">EVSB</a></td>
<td data-boxover="cssbody=[hoverchart] cssheader=[tabchrthdr] body=[<img  srcset='https://charts2-node.finviz.com/chart.ashx?cs=m&t=JPST&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&o[[0]][[ot]]=sma&o[[0]][[op]]=50&o[[0]][[oc]]=FF8F33C6&o[[1]][[ot]]=sma&o[[1]][[op]]=200&o[[1]][[oc]]=DCB3326D&o[[2]][[ot]]=patterns&o[[2]][[op]]=&o[[2]][[oc]]=000 1x, https://charts2-node.finviz.com/chart.ashx?cs=m&t=JPST&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&o[[0]][[ot]]=sma&o[[0]][[op]]=50&o[[0]][[oc]]=FF8F33C6&o[[1]][[ot]]=sma&o[[1]][[op]]=200&o[[1]][[oc]]=DCB3326D&o[[2]][[ot]]=patterns&o[[2]][[op]]=&o[[2]][[oc]]=000&sf=2 2x' width='464' height='230' alt='' loading='lazy'><div><b>JPMorgan Ultra-Short Income ETF</b>Exchange Traded Fund <span>•</span> USA <span>•</span> AUM: 35.39B </div>] offsetx=[20] offsety=[-280] delay=[250]"><a href="quote.ashx?t=JPST" class="tab-link">JPST</a></td>
<td data-boxover="cssbody=[hoverchart] cssheader=[tabchrthdr] body=[<img  srcset='https://charts2-node.finviz.com/chart.ashx?cs=m&t=VBIL&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&o[[0]][[ot]]=sma&o[[0]][[op]]=50&o[[0]][[oc]]=FF8F33C6&o[[1]][[ot]]=sma&o[[1]][[op]]=200&o[[1]][[oc]]=DCB3326D&o[[2]][[ot]]=patterns&o[[2]][[op]]=&o[[2]][[oc]]=000 1x, https://charts2-node.finviz.com/chart.ashx?cs=m&t=VBIL&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&o[[0]][[ot]]=sma&o[[0]][[op]]=50&o[[0]][[oc]]=FF8F33C6&o[[1]][[ot]]=sma&o[[1]][[op]]=200&o[[1]][[oc]]=DCB3326D&o[[2]][[ot]]=patterns&o[[2]][[op]]=&o[[2]][[oc]]=000&sf=2 2x' width='464' height='230' alt='' loading='lazy'><div><b>Vanguard 0-3 Month Treasury Bill ETF</b>Exchange Traded Fund <span>•</span> USA <span>•</span> AUM: 4.39B </div>] offsetx=[20] offsety=[-280] delay=[250]"><a href="quote.ashx?t=VBIL" class="tab-link">VBIL</a></td>
<td data-boxover="cssbody=[tooltip_short_bdy] cssheader=[tooltip_short_hdr] body=[Stocks with the current price near strong channel-up pattern] offsetx=[10] offsety=[20] delay=[300]"><svg width="16" height="16">
    <rect x="0" y="0" width="16" height="16" rx="2" ry="2" class="fill-gray-50 dark:fill-gray-700" />
<use href="/assets/dist-icons/icons_signals.svg?rev=35#channel-up-1" class="fill-blue-600 dark:fill-blue-300" />
<use href="/assets/dist-icons/icons_signals.svg?rev=35#channel-up-2" class="fill-pink-400 dark:fill-pink-300" />
</svg><a href="screener.ashx?v=210&s=ta_p_channelup" class="tab-link-nw">Channel Up</a></td>
</tr>
<tr class="styled-row is-hoverable is-bordered is-rounded cursor-pointer" onclick="window.location='screener.ashx?v=210&s=ta_p_channel'">
<td data-boxover="cssbody=[hoverchart] cssheader=[tabchrthdr] body=[<img  srcset='https://charts2-node.finviz.com/chart.ashx?cs=m&t=TRSY&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&o[[0]][[ot]]=sma&o[[0]][[op]]=50&o[[0]][[oc]]=FF8F33C6&o[[1]][[ot]]=sma&o[[1]][[op]]=200&o[[1]][[oc]]=DCB3326D&o[[2]][[ot]]=patterns&o[[2]][[op]]=&o[[2]][[oc]]=000 1x, https://charts2-node.finviz.com/chart.ashx?cs=m&t=TRSY&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&o[[0]][[ot]]=sma&o[[0]][[op]]=50&o[[0]][[oc]]=FF8F33C6&o[[1]][[ot]]=sma&o[[1]][[op]]=200&o[[1]][[oc]]=DCB3326D&o[[2]][[ot]]=patterns&o[[2]][[op]]=&o[[2]][[oc]]=000&sf=2 2x' width='464' height='230' alt='' loading='lazy'><div><b>Xtrackers US 0-1 Year Treasury ETF</b>Exchange Traded Fund <span>•</span> USA <span>•</span> AUM: 21.69M </div>] offsetx=[20] offsety=[-280] delay=[250]"><a href="quote.ashx?t=TRSY" class="tab-link">TRSY</a></td>
<td data-boxover="cssbody=[hoverchart] cssheader=[tabchrthdr] body=[<img  srcset='https://charts2-node.finviz.com/chart.ashx?cs=m&t=BKUI&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&o[[0]][[ot]]=sma&o[[0]][[op]]=50&o[[0]][[oc]]=FF8F33C6&o[[1]][[ot]]=sma&o[[1]][[op]]=200&o[[1]][[oc]]=DCB3326D&o[[2]][[ot]]=patterns&o[[2]][[op]]=&o[[2]][[oc]]=000 1x, https://charts2-node.finviz.com/chart.ashx?cs=m&t=BKUI&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&o[[0]][[ot]]=sma&o[[0]][[op]]=50&o[[0]][[oc]]=FF8F33C6&o[[1]][[ot]]=sma&o[[1]][[op]]=200&o[[1]][[oc]]=DCB3326D&o[[2]][[ot]]=patterns&o[[2]][[op]]=&o[[2]][[oc]]=000&sf=2 2x' width='464' height='230' alt='' loading='lazy'><div><b>BNY Mellon Ultra Short Income ETF</b>Exchange Traded Fund <span>•</span> USA <span>•</span> AUM: 231.71M </div>] offsetx=[20] offsety=[-280] delay=[250]"><a href="quote.ashx?t=BKUI" class="tab-link">BKUI</a></td>
<td data-boxover="cssbody=[hoverchart] cssheader=[tabchrthdr] body=[<img  srcset='https://charts2-node.finviz.com/chart.ashx?cs=m&t=DFAR&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&o[[0]][[ot]]=sma&o[[0]][[op]]=50&o[[0]][[oc]]=FF8F33C6&o[[1]][[ot]]=sma&o[[1]][[op]]=200&o[[1]][[oc]]=DCB3326D&o[[2]][[ot]]=patterns&o[[2]][[op]]=&o[[2]][[oc]]=000 1x, https://charts2-node.finviz.com/chart.ashx?cs=m&t=DFAR&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&o[[0]][[ot]]=sma&o[[0]][[op]]=50&o[[0]][[oc]]=FF8F33C6&o[[1]][[ot]]=sma&o[[1]][[op]]=200&o[[1]][[oc]]=DCB3326D&o[[2]][[ot]]=patterns&o[[2]][[op]]=&o[[2]][[oc]]=000&sf=2 2x' width='464' height='230' alt='' loading='lazy'><div><b>Dimensional US Real Estate ETF</b>Exchange Traded Fund <span>•</span> USA <span>•</span> AUM: 1.43B </div>] offsetx=[20] offsety=[-280] delay=[250]"><a href="quote.ashx?t=DFAR" class="tab-link">DFAR</a></td>
<td data-boxover="cssbody=[hoverchart] cssheader=[tabchrthdr] body=[<img  srcset='https://charts2-node.finviz.com/chart.ashx?cs=m&t=PCLO&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&o[[0]][[ot]]=sma&o[[0]][[op]]=50&o[[0]][[oc]]=FF8F33C6&o[[1]][[ot]]=sma&o[[1]][[op]]=200&o[[1]][[oc]]=DCB3326D&o[[2]][[ot]]=patterns&o[[2]][[op]]=&o[[2]][[oc]]=000 1x, https://charts2-node.finviz.com/chart.ashx?cs=m&t=PCLO&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&o[[0]][[ot]]=sma&o[[0]][[op]]=50&o[[0]][[oc]]=FF8F33C6&o[[1]][[ot]]=sma&o[[1]][[op]]=200&o[[1]][[oc]]=DCB3326D&o[[2]][[ot]]=patterns&o[[2]][[op]]=&o[[2]][[oc]]=000&sf=2 2x' width='464' height='230' alt='' loading='lazy'><div><b>VIRTUS SEIX AAA Private Credit CLO ETF</b>Exchange Traded Fund <span>•</span> USA <span>•</span> AUM: 17.51M </div>] offsetx=[20] offsety=[-280] delay=[250]"><a href="quote.ashx?t=PCLO" class="tab-link">PCLO</a></td>
<td data-boxover="cssbody=[tooltip_short_bdy] cssheader=[tooltip_short_hdr] body=[Stocks with the current price near strong channel] offsetx=[10] offsety=[20] delay=[300]"><svg width="16" height="16">
    <rect x="0" y="0" width="16" height="16" rx="2" ry="2" class="fill-gray-50 dark:fill-gray-700" />
<use href="/assets/dist-icons/icons_signals.svg?rev=35#channel-1" class="fill-blue-600 dark:fill-blue-300" />
<use href="/assets/dist-icons/icons_signals.svg?rev=35#channel-2" class="fill-pink-400 dark:fill-pink-300" />
</svg><a href="screener.ashx?v=210&s=ta_p_channel" class="tab-link-nw">Channel</a></td>
</tr>
<tr class="styled-row is-hoverable is-bordered is-rounded cursor-pointer" onclick="window.location='screener.ashx?v=210&s=ta_p_channeldown'">
<td data-boxover="cssbody=[hoverchart] cssheader=[tabchrthdr] body=[<img  srcset='https://charts2-node.finviz.com/chart.ashx?cs=m&t=TKC&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&o[[0]][[ot]]=sma&o[[0]][[op]]=50&o[[0]][[oc]]=FF8F33C6&o[[1]][[ot]]=sma&o[[1]][[op]]=200&o[[1]][[oc]]=DCB3326D&o[[2]][[ot]]=patterns&o[[2]][[op]]=&o[[2]][[oc]]=000 1x, https://charts2-node.finviz.com/chart.ashx?cs=m&t=TKC&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&o[[0]][[ot]]=sma&o[[0]][[op]]=50&o[[0]][[oc]]=FF8F33C6&o[[1]][[ot]]=sma&o[[1]][[op]]=200&o[[1]][[oc]]=DCB3326D&o[[2]][[ot]]=patterns&o[[2]][[op]]=&o[[2]][[oc]]=000&sf=2 2x' width='464' height='230' alt='' loading='lazy'><div><b>Turkcell Iletisim Hizmetleri A.S. ADR</b>Telecom Services <span>•</span> Turkey <span>•</span> 5.29B </div>] offsetx=[20] offsety=[-280] delay=[250]"><a href="quote.ashx?t=TKC" class="tab-link">TKC</a></td>
<td data-boxover="cssbody=[hoverchart] cssheader=[tabchrthdr] body=[<img  srcset='https://charts2-node.finviz.com/chart.ashx?cs=m&t=WEN&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&o[[0]][[ot]]=sma&o[[0]][[op]]=50&o[[0]][[oc]]=FF8F33C6&o[[1]][[ot]]=sma&o[[1]][[op]]=200&o[[1]][[oc]]=DCB3326D&o[[2]][[ot]]=patterns&o[[2]][[op]]=&o[[2]][[oc]]=000 1x, https://charts2-node.finviz.com/chart.ashx?cs=m&t=WEN&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&o[[0]][[ot]]=sma&o[[0]][[op]]=50&o[[0]][[oc]]=FF8F33C6&o[[1]][[ot]]=sma&o[[1]][[op]]=200&o[[1]][[oc]]=DCB3326D&o[[2]][[ot]]=patterns&o[[2]][[op]]=&o[[2]][[oc]]=000&sf=2 2x' width='464' height='230' alt='' loading='lazy'><div><b>Wendy's Co</b>Restaurants <span>•</span> USA <span>•</span> 1.64B </div>] offsetx=[20] offsety=[-280] delay=[250]"><a href="quote.ashx?t=WEN" class="tab-link">WEN</a></td>
<td data-boxover="cssbody=[hoverchart] cssheader=[tabchrthdr] body=[<img  srcset='https://charts2-node.finviz.com/chart.ashx?cs=m&t=OOMA&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&o[[0]][[ot]]=sma&o[[0]][[op]]=50&o[[0]][[oc]]=FF8F33C6&o[[1]][[ot]]=sma&o[[1]][[op]]=200&o[[1]][[oc]]=DCB3326D&o[[2]][[ot]]=patterns&o[[2]][[op]]=&o[[2]][[oc]]=000 1x, https://charts2-node.finviz.com/chart.ashx?cs=m&t=OOMA&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&o[[0]][[ot]]=sma&o[[0]][[op]]=50&o[[0]][[oc]]=FF8F33C6&o[[1]][[ot]]=sma&o[[1]][[op]]=200&o[[1]][[oc]]=DCB3326D&o[[2]][[ot]]=patterns&o[[2]][[op]]=&o[[2]][[oc]]=000&sf=2 2x' width='464' height='230' alt='' loading='lazy'><div><b>Ooma Inc</b>Software - Application <span>•</span> USA <span>•</span> 327.89M </div>] offsetx=[20] offsety=[-280] delay=[250]"><a href="quote.ashx?t=OOMA" class="tab-link">OOMA</a></td>
<td data-boxover="cssbody=[hoverchart] cssheader=[tabchrthdr] body=[<img  srcset='https://charts2-node.finviz.com/chart.ashx?cs=m&t=ITRM&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&o[[0]][[ot]]=sma&o[[0]][[op]]=50&o[[0]][[oc]]=FF8F33C6&o[[1]][[ot]]=sma&o[[1]][[op]]=200&o[[1]][[oc]]=DCB3326D&o[[2]][[ot]]=patterns&o[[2]][[op]]=&o[[2]][[oc]]=000 1x, https://charts2-node.finviz.com/chart.ashx?cs=m&t=ITRM&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&o[[0]][[ot]]=sma&o[[0]][[op]]=50&o[[0]][[oc]]=FF8F33C6&o[[1]][[ot]]=sma&o[[1]][[op]]=200&o[[1]][[oc]]=DCB3326D&o[[2]][[ot]]=patterns&o[[2]][[op]]=&o[[2]][[oc]]=000&sf=2 2x' width='464' height='230' alt='' loading='lazy'><div><b>Iterum Therapeutics Plc</b>Biotechnology <span>•</span> Ireland <span>•</span> 23.75M </div>] offsetx=[20] offsety=[-280] delay=[250]"><a href="quote.ashx?t=ITRM" class="tab-link">ITRM</a></td>
<td data-boxover="cssbody=[tooltip_short_bdy] cssheader=[tooltip_short_hdr] body=[Stocks with the current price near strong channel-down pattern] offsetx=[10] offsety=[20] delay=[300]"><svg width="16" height="16">
    <rect x="0" y="0" width="16" height="16" rx="2" ry="2" class="fill-gray-50 dark:fill-gray-700" />
<use href="/assets/dist-icons/icons_signals.svg?rev=35#channel-down-1" class="fill-blue-600 dark:fill-blue-300" />
<use href="/assets/dist-icons/icons_signals.svg?rev=35#channel-down-2" class="fill-pink-400 dark:fill-pink-300" />
</svg><a href="screener.ashx?v=210&s=ta_p_channeldown" class="tab-link-nw">Channel Down</a></td>
</tr>
<tr class="styled-row is-hoverable is-bordered is-rounded cursor-pointer" onclick="window.location='screener.ashx?v=210&s=ta_p_doubletop'">
<td data-boxover="cssbody=[hoverchart] cssheader=[tabchrthdr] body=[<img  srcset='https://charts2-node.finviz.com/chart.ashx?cs=m&t=NSEP&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&o[[0]][[ot]]=sma&o[[0]][[op]]=50&o[[0]][[oc]]=FF8F33C6&o[[1]][[ot]]=sma&o[[1]][[op]]=200&o[[1]][[oc]]=DCB3326D&o[[2]][[ot]]=patterns&o[[2]][[op]]=&o[[2]][[oc]]=000 1x, https://charts2-node.finviz.com/chart.ashx?cs=m&t=NSEP&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&o[[0]][[ot]]=sma&o[[0]][[op]]=50&o[[0]][[oc]]=FF8F33C6&o[[1]][[ot]]=sma&o[[1]][[op]]=200&o[[1]][[oc]]=DCB3326D&o[[2]][[ot]]=patterns&o[[2]][[op]]=&o[[2]][[oc]]=000&sf=2 2x' width='464' height='230' alt='' loading='lazy'><div><b>Innovator Growth-100 Power Buffer ETF - September</b>Exchange Traded Fund <span>•</span> USA <span>•</span> AUM: 49.44M </div>] offsetx=[20] offsety=[-280] delay=[250]"><a href="quote.ashx?t=NSEP" class="tab-link">NSEP</a></td>
<td data-boxover="cssbody=[hoverchart] cssheader=[tabchrthdr] body=[<img  srcset='https://charts2-node.finviz.com/chart.ashx?cs=m&t=MTUL&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&o[[0]][[ot]]=sma&o[[0]][[op]]=50&o[[0]][[oc]]=FF8F33C6&o[[1]][[ot]]=sma&o[[1]][[op]]=200&o[[1]][[oc]]=DCB3326D&o[[2]][[ot]]=patterns&o[[2]][[op]]=&o[[2]][[oc]]=000 1x, https://charts2-node.finviz.com/chart.ashx?cs=m&t=MTUL&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&o[[0]][[ot]]=sma&o[[0]][[op]]=50&o[[0]][[oc]]=FF8F33C6&o[[1]][[ot]]=sma&o[[1]][[op]]=200&o[[1]][[oc]]=DCB3326D&o[[2]][[ot]]=patterns&o[[2]][[op]]=&o[[2]][[oc]]=000&sf=2 2x' width='464' height='230' alt='' loading='lazy'><div><b>ETRACS 2x Leveraged MSCI US Momentum Factor TR ETN</b>Exchange Traded Fund <span>•</span> USA <span>•</span> AUM: 7.50M </div>] offsetx=[20] offsety=[-280] delay=[250]"><a href="quote.ashx?t=MTUL" class="tab-link">MTUL</a></td>
<td data-boxover="cssbody=[hoverchart] cssheader=[tabchrthdr] body=[<img  srcset='https://charts2-node.finviz.com/chart.ashx?cs=m&t=MI&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&o[[0]][[ot]]=sma&o[[0]][[op]]=50&o[[0]][[oc]]=FF8F33C6&o[[1]][[ot]]=sma&o[[1]][[op]]=200&o[[1]][[oc]]=DCB3326D&o[[2]][[ot]]=patterns&o[[2]][[op]]=&o[[2]][[oc]]=000 1x, https://charts2-node.finviz.com/chart.ashx?cs=m&t=MI&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&o[[0]][[ot]]=sma&o[[0]][[op]]=50&o[[0]][[oc]]=FF8F33C6&o[[1]][[ot]]=sma&o[[1]][[op]]=200&o[[1]][[oc]]=DCB3326D&o[[2]][[ot]]=patterns&o[[2]][[op]]=&o[[2]][[oc]]=000&sf=2 2x' width='464' height='230' alt='' loading='lazy'><div><b>NFT Ltd</b>Internet Retail <span>•</span> Hong Kong <span>•</span> 20.54M </div>] offsetx=[20] offsety=[-280] delay=[250]"><a href="quote.ashx?t=MI" class="tab-link">MI</a></td>
<td data-boxover="cssbody=[hoverchart] cssheader=[tabchrthdr] body=[<img  srcset='https://charts2-node.finviz.com/chart.ashx?cs=m&t=HEQQ&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&o[[0]][[ot]]=sma&o[[0]][[op]]=50&o[[0]][[oc]]=FF8F33C6&o[[1]][[ot]]=sma&o[[1]][[op]]=200&o[[1]][[oc]]=DCB3326D&o[[2]][[ot]]=patterns&o[[2]][[op]]=&o[[2]][[oc]]=000 1x, https://charts2-node.finviz.com/chart.ashx?cs=m&t=HEQQ&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&o[[0]][[ot]]=sma&o[[0]][[op]]=50&o[[0]][[oc]]=FF8F33C6&o[[1]][[ot]]=sma&o[[1]][[op]]=200&o[[1]][[oc]]=DCB3326D&o[[2]][[ot]]=patterns&o[[2]][[op]]=&o[[2]][[oc]]=000&sf=2 2x' width='464' height='230' alt='' loading='lazy'><div><b>JPMorgan Nasdaq Hedged Equity Laddered Overlay ETF</b>Exchange Traded Fund <span>•</span> USA <span>•</span> AUM: 32.05M </div>] offsetx=[20] offsety=[-280] delay=[250]"><a href="quote.ashx?t=HEQQ" class="tab-link">HEQQ</a></td>
<td data-boxover="cssbody=[tooltip_short_bdy] cssheader=[tooltip_short_hdr] body=[Stocks with strong double-top pattern] offsetx=[10] offsety=[20] delay=[300]"><svg width="16" height="16">
    <rect x="0" y="0" width="16" height="16" rx="2" ry="2" class="fill-gray-50 dark:fill-gray-700" />
<use href="/assets/dist-icons/icons_signals.svg?rev=35#double-top-1" class="fill-blue-600 dark:fill-blue-300" />
<use href="/assets/dist-icons/icons_signals.svg?rev=35#double-top-2" class="fill-pink-400 dark:fill-pink-300" />
</svg><a href="screener.ashx?v=210&s=ta_p_doubletop" class="tab-link-nw">Double Top</a></td>
</tr>
<tr class="styled-row is-hoverable is-bordered is-rounded cursor-pointer" onclick="window.location='screener.ashx?v=210&s=ta_p_multipletop'">
<td data-boxover="cssbody=[hoverchart] cssheader=[tabchrthdr] body=[<img  srcset='https://charts2-node.finviz.com/chart.ashx?cs=m&t=DDLS&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&o[[0]][[ot]]=sma&o[[0]][[op]]=50&o[[0]][[oc]]=FF8F33C6&o[[1]][[ot]]=sma&o[[1]][[op]]=200&o[[1]][[oc]]=DCB3326D&o[[2]][[ot]]=patterns&o[[2]][[op]]=&o[[2]][[oc]]=000 1x, https://charts2-node.finviz.com/chart.ashx?cs=m&t=DDLS&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&o[[0]][[ot]]=sma&o[[0]][[op]]=50&o[[0]][[oc]]=FF8F33C6&o[[1]][[ot]]=sma&o[[1]][[op]]=200&o[[1]][[oc]]=DCB3326D&o[[2]][[ot]]=patterns&o[[2]][[op]]=&o[[2]][[oc]]=000&sf=2 2x' width='464' height='230' alt='' loading='lazy'><div><b>WisdomTree Dynamic International SmallCap Equity Fund</b>Exchange Traded Fund <span>•</span> USA <span>•</span> AUM: 425.67M </div>] offsetx=[20] offsety=[-280] delay=[250]"><a href="quote.ashx?t=DDLS" class="tab-link">DDLS</a></td>
<td data-boxover="cssbody=[hoverchart] cssheader=[tabchrthdr] body=[<img  srcset='https://charts2-node.finviz.com/chart.ashx?cs=m&t=BEEX&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&o[[0]][[ot]]=sma&o[[0]][[op]]=50&o[[0]][[oc]]=FF8F33C6&o[[1]][[ot]]=sma&o[[1]][[op]]=200&o[[1]][[oc]]=DCB3326D&o[[2]][[ot]]=patterns&o[[2]][[op]]=&o[[2]][[oc]]=000 1x, https://charts2-node.finviz.com/chart.ashx?cs=m&t=BEEX&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&o[[0]][[ot]]=sma&o[[0]][[op]]=50&o[[0]][[oc]]=FF8F33C6&o[[1]][[ot]]=sma&o[[1]][[op]]=200&o[[1]][[oc]]=DCB3326D&o[[2]][[ot]]=patterns&o[[2]][[op]]=&o[[2]][[oc]]=000&sf=2 2x' width='464' height='230' alt='' loading='lazy'><div><b>The Beehive ETF</b>Exchange Traded Fund <span>•</span> USA <span>•</span> AUM: 184.97M </div>] offsetx=[20] offsety=[-280] delay=[250]"><a href="quote.ashx?t=BEEX" class="tab-link">BEEX</a></td>
<td data-boxover="cssbody=[hoverchart] cssheader=[tabchrthdr] body=[<img  srcset='https://charts2-node.finviz.com/chart.ashx?cs=m&t=MGYR&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&o[[0]][[ot]]=sma&o[[0]][[op]]=50&o[[0]][[oc]]=FF8F33C6&o[[1]][[ot]]=sma&o[[1]][[op]]=200&o[[1]][[oc]]=DCB3326D&o[[2]][[ot]]=patterns&o[[2]][[op]]=&o[[2]][[oc]]=000 1x, https://charts2-node.finviz.com/chart.ashx?cs=m&t=MGYR&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&o[[0]][[ot]]=sma&o[[0]][[op]]=50&o[[0]][[oc]]=FF8F33C6&o[[1]][[ot]]=sma&o[[1]][[op]]=200&o[[1]][[oc]]=DCB3326D&o[[2]][[ot]]=patterns&o[[2]][[op]]=&o[[2]][[oc]]=000&sf=2 2x' width='464' height='230' alt='' loading='lazy'><div><b>Magyar Bancorp Inc</b>Banks - Regional <span>•</span> USA <span>•</span> 111.21M </div>] offsetx=[20] offsety=[-280] delay=[250]"><a href="quote.ashx?t=MGYR" class="tab-link">MGYR</a></td>
<td data-boxover="cssbody=[hoverchart] cssheader=[tabchrthdr] body=[<img  srcset='https://charts2-node.finviz.com/chart.ashx?cs=m&t=NVS&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&o[[0]][[ot]]=sma&o[[0]][[op]]=50&o[[0]][[oc]]=FF8F33C6&o[[1]][[ot]]=sma&o[[1]][[op]]=200&o[[1]][[oc]]=DCB3326D&o[[2]][[ot]]=patterns&o[[2]][[op]]=&o[[2]][[oc]]=000 1x, https://charts2-node.finviz.com/chart.ashx?cs=m&t=NVS&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&o[[0]][[ot]]=sma&o[[0]][[op]]=50&o[[0]][[oc]]=FF8F33C6&o[[1]][[ot]]=sma&o[[1]][[op]]=200&o[[1]][[oc]]=DCB3326D&o[[2]][[ot]]=patterns&o[[2]][[op]]=&o[[2]][[oc]]=000&sf=2 2x' width='464' height='230' alt='' loading='lazy'><div><b>Novartis AG ADR</b>Drug Manufacturers - General <span>•</span> Switzerland <span>•</span> 251.56B </div>] offsetx=[20] offsety=[-280] delay=[250]"><a href="quote.ashx?t=NVS" class="tab-link">NVS</a></td>
<td data-boxover="cssbody=[tooltip_short_bdy] cssheader=[tooltip_short_hdr] body=[Stocks with strong multiple-top pattern] offsetx=[10] offsety=[20] delay=[300]"><svg width="16" height="16">
    <rect x="0" y="0" width="16" height="16" rx="2" ry="2" class="fill-gray-50 dark:fill-gray-700" />
<use href="/assets/dist-icons/icons_signals.svg?rev=35#multiple-top-1" class="fill-blue-600 dark:fill-blue-300" />
<use href="/assets/dist-icons/icons_signals.svg?rev=35#multiple-top-2" class="fill-pink-400 dark:fill-pink-300" />
</svg><a href="screener.ashx?v=210&s=ta_p_multipletop" class="tab-link-nw">Multiple Top</a></td>
</tr>
<tr class="styled-row is-hoverable is-bordered is-rounded cursor-pointer" onclick="window.location='screener.ashx?v=210&s=ta_p_doublebottom'">
<td data-boxover="cssbody=[hoverchart] cssheader=[tabchrthdr] body=[<img  srcset='https://charts2-node.finviz.com/chart.ashx?cs=m&t=VGHY&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&o[[0]][[ot]]=sma&o[[0]][[op]]=50&o[[0]][[oc]]=FF8F33C6&o[[1]][[ot]]=sma&o[[1]][[op]]=200&o[[1]][[oc]]=DCB3326D&o[[2]][[ot]]=patterns&o[[2]][[op]]=&o[[2]][[oc]]=000 1x, https://charts2-node.finviz.com/chart.ashx?cs=m&t=VGHY&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&o[[0]][[ot]]=sma&o[[0]][[op]]=50&o[[0]][[oc]]=FF8F33C6&o[[1]][[ot]]=sma&o[[1]][[op]]=200&o[[1]][[oc]]=DCB3326D&o[[2]][[ot]]=patterns&o[[2]][[op]]=&o[[2]][[oc]]=000&sf=2 2x' width='464' height='230' alt='' loading='lazy'><div><b>Vanguard High-Yield Active ETF</b>Exchange Traded Fund <span>•</span> USA <span>•</span> AUM: 118.95M </div>] offsetx=[20] offsety=[-280] delay=[250]"><a href="quote.ashx?t=VGHY" class="tab-link">VGHY</a></td>
<td data-boxover="cssbody=[hoverchart] cssheader=[tabchrthdr] body=[<img  srcset='https://charts2-node.finviz.com/chart.ashx?cs=m&t=BABW&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&o[[0]][[ot]]=sma&o[[0]][[op]]=50&o[[0]][[oc]]=FF8F33C6&o[[1]][[ot]]=sma&o[[1]][[op]]=200&o[[1]][[oc]]=DCB3326D&o[[2]][[ot]]=patterns&o[[2]][[op]]=&o[[2]][[oc]]=000 1x, https://charts2-node.finviz.com/chart.ashx?cs=m&t=BABW&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&o[[0]][[ot]]=sma&o[[0]][[op]]=50&o[[0]][[oc]]=FF8F33C6&o[[1]][[ot]]=sma&o[[1]][[op]]=200&o[[1]][[oc]]=DCB3326D&o[[2]][[ot]]=patterns&o[[2]][[op]]=&o[[2]][[oc]]=000&sf=2 2x' width='464' height='230' alt='' loading='lazy'><div><b>Roundhill BABA WeeklyPay ETF</b>Exchange Traded Fund <span>•</span> USA <span>•</span> AUM: 26.73M </div>] offsetx=[20] offsety=[-280] delay=[250]"><a href="quote.ashx?t=BABW" class="tab-link">BABW</a></td>
<td data-boxover="cssbody=[hoverchart] cssheader=[tabchrthdr] body=[<img  srcset='https://charts2-node.finviz.com/chart.ashx?cs=m&t=VGAS&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&o[[0]][[ot]]=sma&o[[0]][[op]]=50&o[[0]][[oc]]=FF8F33C6&o[[1]][[ot]]=sma&o[[1]][[op]]=200&o[[1]][[oc]]=DCB3326D&o[[2]][[ot]]=patterns&o[[2]][[op]]=&o[[2]][[oc]]=000 1x, https://charts2-node.finviz.com/chart.ashx?cs=m&t=VGAS&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&o[[0]][[ot]]=sma&o[[0]][[op]]=50&o[[0]][[oc]]=FF8F33C6&o[[1]][[ot]]=sma&o[[1]][[op]]=200&o[[1]][[oc]]=DCB3326D&o[[2]][[ot]]=patterns&o[[2]][[op]]=&o[[2]][[oc]]=000&sf=2 2x' width='464' height='230' alt='' loading='lazy'><div><b>Verde Clean Fuels Inc</b>Utilities - Renewable <span>•</span> USA <span>•</span> 121.62M </div>] offsetx=[20] offsety=[-280] delay=[250]"><a href="quote.ashx?t=VGAS" class="tab-link">VGAS</a></td>
<td data-boxover="cssbody=[hoverchart] cssheader=[tabchrthdr] body=[<img  srcset='https://charts2-node.finviz.com/chart.ashx?cs=m&t=UBEW&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&o[[0]][[ot]]=sma&o[[0]][[op]]=50&o[[0]][[oc]]=FF8F33C6&o[[1]][[ot]]=sma&o[[1]][[op]]=200&o[[1]][[oc]]=DCB3326D&o[[2]][[ot]]=patterns&o[[2]][[op]]=&o[[2]][[oc]]=000 1x, https://charts2-node.finviz.com/chart.ashx?cs=m&t=UBEW&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&o[[0]][[ot]]=sma&o[[0]][[op]]=50&o[[0]][[oc]]=FF8F33C6&o[[1]][[ot]]=sma&o[[1]][[op]]=200&o[[1]][[oc]]=DCB3326D&o[[2]][[ot]]=patterns&o[[2]][[op]]=&o[[2]][[oc]]=000&sf=2 2x' width='464' height='230' alt='' loading='lazy'><div><b>Roundhill UBER WeeklyPay ETF</b>Exchange Traded Fund <span>•</span> USA <span>•</span> AUM: 26.84M </div>] offsetx=[20] offsety=[-280] delay=[250]"><a href="quote.ashx?t=UBEW" class="tab-link">UBEW</a></td>
<td data-boxover="cssbody=[tooltip_short_bdy] cssheader=[tooltip_short_hdr] body=[Stocks with strong double-bottom pattern] offsetx=[10] offsety=[20] delay=[300]"><svg width="16" height="16">
    <rect x="0" y="0" width="16" height="16" rx="2" ry="2" class="fill-gray-50 dark:fill-gray-700" />
<use href="/assets/dist-icons/icons_signals.svg?rev=35#double-bottom-1" class="fill-blue-600 dark:fill-blue-300" />
<use href="/assets/dist-icons/icons_signals.svg?rev=35#double-bottom-2" class="fill-pink-400 dark:fill-pink-300" />
</svg><a href="screener.ashx?v=210&s=ta_p_doublebottom" class="tab-link-nw">Double Bottom</a></td>
</tr>
<tr class="styled-row is-hoverable is-bordered is-rounded cursor-pointer" onclick="window.location='screener.ashx?v=210&s=ta_p_multiplebottom'">
<td data-boxover="cssbody=[hoverchart] cssheader=[tabchrthdr] body=[<img  srcset='https://charts2-node.finviz.com/chart.ashx?cs=m&t=TELO&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&o[[0]][[ot]]=sma&o[[0]][[op]]=50&o[[0]][[oc]]=FF8F33C6&o[[1]][[ot]]=sma&o[[1]][[op]]=200&o[[1]][[oc]]=DCB3326D&o[[2]][[ot]]=patterns&o[[2]][[op]]=&o[[2]][[oc]]=000 1x, https://charts2-node.finviz.com/chart.ashx?cs=m&t=TELO&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&o[[0]][[ot]]=sma&o[[0]][[op]]=50&o[[0]][[oc]]=FF8F33C6&o[[1]][[ot]]=sma&o[[1]][[op]]=200&o[[1]][[oc]]=DCB3326D&o[[2]][[ot]]=patterns&o[[2]][[op]]=&o[[2]][[oc]]=000&sf=2 2x' width='464' height='230' alt='' loading='lazy'><div><b>Telomir Pharmaceuticals Inc</b>Biotechnology <span>•</span> USA <span>•</span> 49.85M </div>] offsetx=[20] offsety=[-280] delay=[250]"><a href="quote.ashx?t=TELO" class="tab-link">TELO</a></td>
<td data-boxover="cssbody=[hoverchart] cssheader=[tabchrthdr] body=[<img  srcset='https://charts2-node.finviz.com/chart.ashx?cs=m&t=RYAN&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&o[[0]][[ot]]=sma&o[[0]][[op]]=50&o[[0]][[oc]]=FF8F33C6&o[[1]][[ot]]=sma&o[[1]][[op]]=200&o[[1]][[oc]]=DCB3326D&o[[2]][[ot]]=patterns&o[[2]][[op]]=&o[[2]][[oc]]=000 1x, https://charts2-node.finviz.com/chart.ashx?cs=m&t=RYAN&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&o[[0]][[ot]]=sma&o[[0]][[op]]=50&o[[0]][[oc]]=FF8F33C6&o[[1]][[ot]]=sma&o[[1]][[op]]=200&o[[1]][[oc]]=DCB3326D&o[[2]][[ot]]=patterns&o[[2]][[op]]=&o[[2]][[oc]]=000&sf=2 2x' width='464' height='230' alt='' loading='lazy'><div><b>Ryan Specialty Holdings Inc</b>Insurance - Specialty <span>•</span> USA <span>•</span> 14.31B </div>] offsetx=[20] offsety=[-280] delay=[250]"><a href="quote.ashx?t=RYAN" class="tab-link">RYAN</a></td>
<td data-boxover="cssbody=[hoverchart] cssheader=[tabchrthdr] body=[<img  srcset='https://charts2-node.finviz.com/chart.ashx?cs=m&t=SAM&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&o[[0]][[ot]]=sma&o[[0]][[op]]=50&o[[0]][[oc]]=FF8F33C6&o[[1]][[ot]]=sma&o[[1]][[op]]=200&o[[1]][[oc]]=DCB3326D&o[[2]][[ot]]=patterns&o[[2]][[op]]=&o[[2]][[oc]]=000 1x, https://charts2-node.finviz.com/chart.ashx?cs=m&t=SAM&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&o[[0]][[ot]]=sma&o[[0]][[op]]=50&o[[0]][[oc]]=FF8F33C6&o[[1]][[ot]]=sma&o[[1]][[op]]=200&o[[1]][[oc]]=DCB3326D&o[[2]][[ot]]=patterns&o[[2]][[op]]=&o[[2]][[oc]]=000&sf=2 2x' width='464' height='230' alt='' loading='lazy'><div><b>Boston Beer Co., Inc</b>Beverages - Brewers <span>•</span> USA <span>•</span> 2.16B </div>] offsetx=[20] offsety=[-280] delay=[250]"><a href="quote.ashx?t=SAM" class="tab-link">SAM</a></td>
<td data-boxover="cssbody=[hoverchart] cssheader=[tabchrthdr] body=[<img  srcset='https://charts2-node.finviz.com/chart.ashx?cs=m&t=TROX&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&o[[0]][[ot]]=sma&o[[0]][[op]]=50&o[[0]][[oc]]=FF8F33C6&o[[1]][[ot]]=sma&o[[1]][[op]]=200&o[[1]][[oc]]=DCB3326D&o[[2]][[ot]]=patterns&o[[2]][[op]]=&o[[2]][[oc]]=000 1x, https://charts2-node.finviz.com/chart.ashx?cs=m&t=TROX&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&o[[0]][[ot]]=sma&o[[0]][[op]]=50&o[[0]][[oc]]=FF8F33C6&o[[1]][[ot]]=sma&o[[1]][[op]]=200&o[[1]][[oc]]=DCB3326D&o[[2]][[ot]]=patterns&o[[2]][[op]]=&o[[2]][[oc]]=000&sf=2 2x' width='464' height='230' alt='' loading='lazy'><div><b>Tronox Holdings plc</b>Chemicals <span>•</span> USA <span>•</span> 740.44M </div>] offsetx=[20] offsety=[-280] delay=[250]"><a href="quote.ashx?t=TROX" class="tab-link">TROX</a></td>
<td data-boxover="cssbody=[tooltip_short_bdy] cssheader=[tooltip_short_hdr] body=[Stocks with strong multiple-bottom pattern] offsetx=[10] offsety=[20] delay=[300]"><svg width="16" height="16">
    <rect x="0" y="0" width="16" height="16" rx="2" ry="2" class="fill-gray-50 dark:fill-gray-700" />
<use href="/assets/dist-icons/icons_signals.svg?rev=35#multiple-bottom-1" class="fill-blue-600 dark:fill-blue-300" />
<use href="/assets/dist-icons/icons_signals.svg?rev=35#multiple-bottom-2" class="fill-pink-400 dark:fill-pink-300" />
</svg><a href="screener.ashx?v=210&s=ta_p_multiplebottom" class="tab-link-nw">Multiple Bottom</a></td>
</tr>
<tr class="styled-row is-hoverable is-bordered is-rounded cursor-pointer" onclick="window.location='screener.ashx?v=210&s=ta_p_headandshoulders'">
<td data-boxover="cssbody=[hoverchart] cssheader=[tabchrthdr] body=[<img  srcset='https://charts2-node.finviz.com/chart.ashx?cs=m&t=GABC&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&o[[0]][[ot]]=sma&o[[0]][[op]]=50&o[[0]][[oc]]=FF8F33C6&o[[1]][[ot]]=sma&o[[1]][[op]]=200&o[[1]][[oc]]=DCB3326D&o[[2]][[ot]]=patterns&o[[2]][[op]]=&o[[2]][[oc]]=000 1x, https://charts2-node.finviz.com/chart.ashx?cs=m&t=GABC&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&o[[0]][[ot]]=sma&o[[0]][[op]]=50&o[[0]][[oc]]=FF8F33C6&o[[1]][[ot]]=sma&o[[1]][[op]]=200&o[[1]][[oc]]=DCB3326D&o[[2]][[ot]]=patterns&o[[2]][[op]]=&o[[2]][[oc]]=000&sf=2 2x' width='464' height='230' alt='' loading='lazy'><div><b>German American Bancorp Inc</b>Banks - Regional <span>•</span> USA <span>•</span> 1.53B </div>] offsetx=[20] offsety=[-280] delay=[250]"><a href="quote.ashx?t=GABC" class="tab-link">GABC</a></td>
<td data-boxover="cssbody=[hoverchart] cssheader=[tabchrthdr] body=[<img  srcset='https://charts2-node.finviz.com/chart.ashx?cs=m&t=ATHE&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&o[[0]][[ot]]=sma&o[[0]][[op]]=50&o[[0]][[oc]]=FF8F33C6&o[[1]][[ot]]=sma&o[[1]][[op]]=200&o[[1]][[oc]]=DCB3326D&o[[2]][[ot]]=patterns&o[[2]][[op]]=&o[[2]][[oc]]=000 1x, https://charts2-node.finviz.com/chart.ashx?cs=m&t=ATHE&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&o[[0]][[ot]]=sma&o[[0]][[op]]=50&o[[0]][[oc]]=FF8F33C6&o[[1]][[ot]]=sma&o[[1]][[op]]=200&o[[1]][[oc]]=DCB3326D&o[[2]][[ot]]=patterns&o[[2]][[op]]=&o[[2]][[oc]]=000&sf=2 2x' width='464' height='230' alt='' loading='lazy'><div><b>Alterity Therapeutics Ltd ADR</b>Biotechnology <span>•</span> Australia <span>•</span> 59.65M </div>] offsetx=[20] offsety=[-280] delay=[250]"><a href="quote.ashx?t=ATHE" class="tab-link">ATHE</a></td>
<td data-boxover="cssbody=[hoverchart] cssheader=[tabchrthdr] body=[<img  srcset='https://charts2-node.finviz.com/chart.ashx?cs=m&t=TRU&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&o[[0]][[ot]]=sma&o[[0]][[op]]=50&o[[0]][[oc]]=FF8F33C6&o[[1]][[ot]]=sma&o[[1]][[op]]=200&o[[1]][[oc]]=DCB3326D&o[[2]][[ot]]=patterns&o[[2]][[op]]=&o[[2]][[oc]]=000 1x, https://charts2-node.finviz.com/chart.ashx?cs=m&t=TRU&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&o[[0]][[ot]]=sma&o[[0]][[op]]=50&o[[0]][[oc]]=FF8F33C6&o[[1]][[ot]]=sma&o[[1]][[op]]=200&o[[1]][[oc]]=DCB3326D&o[[2]][[ot]]=patterns&o[[2]][[op]]=&o[[2]][[oc]]=000&sf=2 2x' width='464' height='230' alt='' loading='lazy'><div><b>TransUnion</b>Financial Data & Stock Exchanges <span>•</span> USA <span>•</span> 16.44B </div>] offsetx=[20] offsety=[-280] delay=[250]"><a href="quote.ashx?t=TRU" class="tab-link">TRU</a></td>
<td data-boxover="cssbody=[hoverchart] cssheader=[tabchrthdr] body=[<img  srcset='https://charts2-node.finviz.com/chart.ashx?cs=m&t=SMCX&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&o[[0]][[ot]]=sma&o[[0]][[op]]=50&o[[0]][[oc]]=FF8F33C6&o[[1]][[ot]]=sma&o[[1]][[op]]=200&o[[1]][[oc]]=DCB3326D&o[[2]][[ot]]=patterns&o[[2]][[op]]=&o[[2]][[oc]]=000 1x, https://charts2-node.finviz.com/chart.ashx?cs=m&t=SMCX&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&o[[0]][[ot]]=sma&o[[0]][[op]]=50&o[[0]][[oc]]=FF8F33C6&o[[1]][[ot]]=sma&o[[1]][[op]]=200&o[[1]][[oc]]=DCB3326D&o[[2]][[ot]]=patterns&o[[2]][[op]]=&o[[2]][[oc]]=000&sf=2 2x' width='464' height='230' alt='' loading='lazy'><div><b>Defiance Daily Target 2x Long SMCI ETF</b>Exchange Traded Fund <span>•</span> USA <span>•</span> AUM: 200.99M </div>] offsetx=[20] offsety=[-280] delay=[250]"><a href="quote.ashx?t=SMCX" class="tab-link">SMCX</a></td>
<td data-boxover="cssbody=[tooltip_short_bdy] cssheader=[tooltip_short_hdr] body=[Stocks with strong head & shoulders pattern] offsetx=[10] offsety=[20] delay=[300]"><svg width="16" height="16">
    <rect x="0" y="0" width="16" height="16" rx="2" ry="2" class="fill-gray-50 dark:fill-gray-700" />
<use href="/assets/dist-icons/icons_signals.svg?rev=35#head-shoulders-1" class="fill-blue-600 dark:fill-blue-300" />
<use href="/assets/dist-icons/icons_signals.svg?rev=35#head-shoulders-2" class="fill-pink-400 dark:fill-pink-300" />
</svg><a href="screener.ashx?v=210&s=ta_p_headandshoulders" class="tab-link-nw">Head&Shoulders</a></td>
</tr>
</table>
</td>
</tr>
<tr>
<td style="font-size: 0; line-height: 0" width="100%" colspan="3"><img src="gfx/nic2x2.gif" alt="" style="width:12px;height:12px" border="0"></td></tr>
<tr>
<td width="100%" colspan="3">
<table class="styled-table-new is-rounded is-condensed hp_news-table table-fixed" border="0" cellpadding="1" cellspacing="0" width="100%">
<thead>
<tr>
<th width="26" align="left">Headlines</th><th width="60" class="nn-date"></th><th></th>
</tr>
</thead>
<tr class="styled-row is-hoverable is-bordered is-rounded cursor-pointer" onclick="trackAndOpenNews(event, 4, 'https://finance.yahoo.com/news/trump-has-suggested-his-now-dwindling-tariff-revenues-could-pay-for-at-least-9-different-things-150008773.html')"><td><svg width="18" height="18">
    <rect x="0" y="0" width="18" height="18" rx="2" ry="2" class="fill-white dark:fill-gray-800" />
<use href="/assets/dist-icons/icons_news.svg?rev=35#yahoo-light" class="dark:hidden" />
<use href="/assets/dist-icons/icons_news.svg?rev=35#yahoo-dark" class="hidden dark:block" />
</svg></td>
<td class="nn-date text-center">12:37PM</td><td><a class="nn-tab-link" href="https://finance.yahoo.com/news/trump-has-suggested-his-now-dwindling-tariff-revenues-could-pay-for-at-least-9-different-things-150008773.html" target="_blank" rel="nofollow">From $2k dividend checks to tax cuts: What Trump says tariffs will pay for</a></td></tr><tr class="styled-row is-hoverable is-bordered is-rounded cursor-pointer" onclick="trackAndOpenNews(event, 1, 'https://www.marketwatch.com/story/investors-are-dumping-stock-market-winners-and-buying-almost-everything-else-why-thats-a-good-sign-16728702')"><td><svg width="18" height="18">
    <rect x="0" y="0" width="18" height="18" rx="2" ry="2" class="fill-white dark:fill-gray-800" />
<use href="/assets/dist-icons/icons_news.svg?rev=35#market-watch-light" class="dark:hidden" />
<use href="/assets/dist-icons/icons_news.svg?rev=35#market-watch-dark" class="hidden dark:block" />
</svg></td>
<td class="nn-date text-center">09:55AM</td><td><a class="nn-tab-link" href="https://www.marketwatch.com/story/investors-are-dumping-stock-market-winners-and-buying-almost-everything-else-why-thats-a-good-sign-16728702" target="_blank" rel="nofollow">Investors are dumping stock-market winners and buying almost everything else. Why that’s a good sign.</a></td></tr>
                            <tr class="styled-row is-hoverable is-bordered is-rounded cursor-pointer">
                                <td class="news_source_icon js-ic-icon">
                                    <img src="https://dggaenaawxe8z.cloudfront.net/images/favicon.ico" width="16" height="16" />
                                </td>
                                <td class="nn-date text-center">Dec-12</td>
                                <td id="IC_D_3x1_1">
                                    <span class="banner-loading block text-3xs text-gray-500 leading-none">Loading…</span>
                                </td>
                            </tr>
                        <tr class="styled-row is-hoverable is-bordered is-rounded cursor-pointer" onclick="trackAndOpenNews(event, 2, 'https://www.wsj.com/livecoverage/stock-market-today-dow-sp-500-nasdaq-12-12-2025')"><td><svg width="18" height="18">
    <rect x="0" y="0" width="18" height="18" rx="2" ry="2" class="fill-white dark:fill-gray-800" />
<use href="/assets/dist-icons/icons_news.svg?rev=35#wsj-light" class="dark:hidden" />
<use href="/assets/dist-icons/icons_news.svg?rev=35#wsj-dark" class="hidden dark:block" />
</svg></td>
<td class="nn-date text-center">Dec-12</td><td><a class="nn-tab-link" href="https://www.wsj.com/livecoverage/stock-market-today-dow-sp-500-nasdaq-12-12-2025" target="_blank" rel="nofollow">Stock Market News, Dec. 12, 2025: Broadcom Slide Fuels Nasdaq Decline</a></td></tr><tr class="styled-row is-hoverable is-bordered is-rounded cursor-pointer" onclick="trackAndOpenNews(event, 10, 'https://www.cnbc.com/2025/12/11/stock-market-today-live-updates.html')"><td><svg width="18" height="18">
    <rect x="0" y="0" width="18" height="18" rx="2" ry="2" class="fill-white dark:fill-gray-800" />
<use href="/assets/dist-icons/icons_news.svg?rev=35#cnbc-light" class="dark:hidden" />
<use href="/assets/dist-icons/icons_news.svg?rev=35#cnbc-dark" class="hidden dark:block" />
</svg></td>
<td class="nn-date text-center">Dec-12</td><td><a class="nn-tab-link" href="https://www.cnbc.com/2025/12/11/stock-market-today-live-updates.html" target="_blank" rel="nofollow">S&P 500 retreats from record Friday, closes down for week as investors rush out of AI trade</a></td></tr><tr class="styled-row is-hoverable is-bordered is-rounded cursor-pointer" onclick="trackAndOpenNews(event, 3, 'https://www.reuters.com/business/finance/oracles-stumble-hits-ai-trade-many-remain-bullish-2025-12-12/')"><td><svg width="18" height="18">
    <rect x="0" y="0" width="18" height="18" rx="2" ry="2" class="fill-white dark:fill-gray-800" />
<use href="/assets/dist-icons/icons_news.svg?rev=35#reuters-light" class="dark:hidden" />
<use href="/assets/dist-icons/icons_news.svg?rev=35#reuters-dark" class="hidden dark:block" />
</svg></td>
<td class="nn-date text-center">Dec-12</td><td><a class="nn-tab-link" href="https://www.reuters.com/business/finance/oracles-stumble-hits-ai-trade-many-remain-bullish-2025-12-12/" target="_blank" rel="nofollow">Oracle-Broadcom one-two punch hits AI trade, but investor optimism persists</a></td></tr><tr class="styled-row is-hoverable is-bordered is-rounded cursor-pointer" onclick="trackAndOpenNews(event, 7, 'https://www.bloomberg.com/news/articles/2025-12-11/stock-market-today-dow-s-p-live-updates')"><td><svg width="18" height="18">
    <rect x="0" y="0" width="18" height="18" rx="2" ry="2" class="fill-white dark:fill-gray-800" />
<use href="/assets/dist-icons/icons_news.svg?rev=35#bloomberg-light" class="dark:hidden" />
<use href="/assets/dist-icons/icons_news.svg?rev=35#bloomberg-dark" class="hidden dark:block" />
</svg></td>
<td class="nn-date text-center">Dec-12</td><td><a class="nn-tab-link" href="https://www.bloomberg.com/news/articles/2025-12-11/stock-market-today-dow-s-p-live-updates" target="_blank" rel="nofollow">Stocks Tumble as Year’s Winning AI Bets Take a Hit: Markets Wrap</a></td></tr></table></td>
</tr>
</table>
</td>
<td class="hp_spacer"><img src="gfx/nic2x2.gif" style="width:16px;height:2px" alt="" border="0"></td>
<td width="414" valign="top">
<table width="414" class="t-home-table" border="0" cellpadding="0" cellspacing="0">
<tr>
<td valign="top">
<table width="100%" border="0" cellpadding="1" cellspacing="0">
<tr>
<td class="ticker-with-change-grid-body" colspan="100%">
<table class="styled-table-new is-rounded ticker-with-change-grid-table" width="100%" cellpadding="1" cellspacing="0" border="0">
<thead><tr class="t-home-table-top" id="major-news"><th class="ticker-with-change-grid-header text-left" colspan="100%"><a href="screener.ashx?v=320&s=n_majornews" class="tab-link"><b>Major News</b></a></td></tr>
</thead><tr class="styled-row is-bordered is-rounded"><td width="25%" class="table-light-cell-cp has-label"data-boxover="cssbody=[hoverchart] cssheader=[tabchrthdr] body=[<img  srcset='https://charts2-node.finviz.com/chart.ashx?cs=m&t=ORCL&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d 1x, https://charts2-node.finviz.com/chart.ashx?cs=m&t=ORCL&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&sf=2 2x' width='324' height='180' alt='' loading='lazy'><div><b>Oracle Corp</b>Software - Infrastructure <span>•</span> USA <span>•</span> 545.81B </div>] offsetx=[-369] offsety=[-275] delay=[250]"><div class="hp_label-container is-single-column "><a href="quote.ashx?t=ORCL" class="tab-link">ORCL</a> <span class="negative-50 fv-label is-negative-50 hp_label ">-4.47%</span></div></td>
</tr><tr class="styled-row is-bordered is-rounded"><td width="25%" class="table-light-cell-cp has-label"data-boxover="cssbody=[hoverchart] cssheader=[tabchrthdr] body=[<img  srcset='https://charts2-node.finviz.com/chart.ashx?cs=m&t=AVGO&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d 1x, https://charts2-node.finviz.com/chart.ashx?cs=m&t=AVGO&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&sf=2 2x' width='324' height='180' alt='' loading='lazy'><div><b>Broadcom Inc</b>Semiconductors <span>•</span> USA <span>•</span> 1699.72B </div>] offsetx=[-369] offsety=[-275] delay=[250]"><div class="hp_label-container is-single-column "><a href="quote.ashx?t=AVGO" class="tab-link">AVGO</a> <span class="negative-200 fv-label is-negative-200 hp_label ">-11.43%</span></div></td>
</tr><tr class="styled-row is-bordered is-rounded"><td width="25%" class="table-light-cell-cp has-label"data-boxover="cssbody=[hoverchart] cssheader=[tabchrthdr] body=[<img  srcset='https://charts2-node.finviz.com/chart.ashx?cs=m&t=NVDA&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d 1x, https://charts2-node.finviz.com/chart.ashx?cs=m&t=NVDA&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&sf=2 2x' width='324' height='180' alt='' loading='lazy'><div><b>NVIDIA Corp</b>Semiconductors <span>•</span> USA <span>•</span> 4252.99B </div>] offsetx=[-369] offsety=[-275] delay=[250]"><div class="hp_label-container is-single-column "><a href="quote.ashx?t=NVDA" class="tab-link">NVDA</a> <span class="negative-50 fv-label is-negative-50 hp_label ">-3.27%</span></div></td>
</tr><tr class="styled-row is-bordered is-rounded"><td width="25%" class="table-light-cell-cp has-label"data-boxover="cssbody=[hoverchart] cssheader=[tabchrthdr] body=[<img  srcset='https://charts2-node.finviz.com/chart.ashx?cs=m&t=LULU&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d 1x, https://charts2-node.finviz.com/chart.ashx?cs=m&t=LULU&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&sf=2 2x' width='324' height='180' alt='' loading='lazy'><div><b>Lululemon Athletica inc</b>Apparel Retail <span>•</span> Canada <span>•</span> 25.09B </div>] offsetx=[-369] offsety=[-275] delay=[250]"><div class="hp_label-container is-single-column "><a href="quote.ashx?t=LULU" class="tab-link">LULU</a> <span class="positive-100 fv-label is-positive-100 hp_label ">+9.60%</span></div></td>
</tr><tr class="styled-row is-bordered is-rounded"><td width="25%" class="table-light-cell-cp has-label"data-boxover="cssbody=[hoverchart] cssheader=[tabchrthdr] body=[<img  srcset='https://charts2-node.finviz.com/chart.ashx?cs=m&t=COST&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d 1x, https://charts2-node.finviz.com/chart.ashx?cs=m&t=COST&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&sf=2 2x' width='324' height='180' alt='' loading='lazy'><div><b>Costco Wholesale Corp</b>Discount Stores <span>•</span> USA <span>•</span> 392.67B </div>] offsetx=[-369] offsety=[-275] delay=[250]"><div class="hp_label-container is-single-column "><a href="quote.ashx?t=COST" class="tab-link">COST</a> <span class="negative-50 fv-label is-negative-50 hp_label ">-0.00%</span></div></td>
</tr><tr class="styled-row is-bordered is-rounded"><td width="25%" class="table-light-cell-cp has-label"data-boxover="cssbody=[hoverchart] cssheader=[tabchrthdr] body=[<img  srcset='https://charts2-node.finviz.com/chart.ashx?cs=m&t=GOOGL&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d 1x, https://charts2-node.finviz.com/chart.ashx?cs=m&t=GOOGL&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&sf=2 2x' width='324' height='180' alt='' loading='lazy'><div><b>Alphabet Inc</b>Internet Content & Information <span>•</span> USA <span>•</span> 3738.85B </div>] offsetx=[-369] offsety=[-275] delay=[250]"><div class="hp_label-container is-single-column "><a href="quote.ashx?t=GOOGL" class="tab-link">GOOGL</a> <span class="negative-50 fv-label is-negative-50 hp_label ">-1.01%</span></div></td>
</tr><tr class="styled-row is-bordered is-rounded"><td width="25%" class="table-light-cell-cp has-label"data-boxover="cssbody=[hoverchart] cssheader=[tabchrthdr] body=[<img  srcset='https://charts2-node.finviz.com/chart.ashx?cs=m&t=GOOG&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d 1x, https://charts2-node.finviz.com/chart.ashx?cs=m&t=GOOG&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&sf=2 2x' width='324' height='180' alt='' loading='lazy'><div><b>Alphabet Inc</b>Internet Content & Information <span>•</span> USA <span>•</span> 3738.85B </div>] offsetx=[-369] offsety=[-275] delay=[250]"><div class="hp_label-container is-single-column "><a href="quote.ashx?t=GOOG" class="tab-link">GOOG</a> <span class="negative-50 fv-label is-negative-50 hp_label ">-1.01%</span></div></td>
</tr><tr class="styled-row is-bordered is-rounded"><td width="25%" class="table-light-cell-cp has-label"data-boxover="cssbody=[hoverchart] cssheader=[tabchrthdr] body=[<img  srcset='https://charts2-node.finviz.com/chart.ashx?cs=m&t=RIVN&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d 1x, https://charts2-node.finviz.com/chart.ashx?cs=m&t=RIVN&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&sf=2 2x' width='324' height='180' alt='' loading='lazy'><div><b>Rivian Automotive Inc</b>Auto Manufacturers <span>•</span> USA <span>•</span> 22.58B </div>] offsetx=[-369] offsety=[-275] delay=[250]"><div class="hp_label-container is-single-column "><a href="quote.ashx?t=RIVN" class="tab-link">RIVN</a> <span class="positive-200 fv-label is-positive-200 hp_label ">+12.11%</span></div></td>
</tr><tr class="styled-row is-bordered is-rounded"><td width="25%" class="table-light-cell-cp has-label"data-boxover="cssbody=[hoverchart] cssheader=[tabchrthdr] body=[<img  srcset='https://charts2-node.finviz.com/chart.ashx?cs=m&t=TLRY&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d 1x, https://charts2-node.finviz.com/chart.ashx?cs=m&t=TLRY&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&sf=2 2x' width='324' height='180' alt='' loading='lazy'><div><b>Tilray Brands Inc</b>Drug Manufacturers - Specialty & Generic <span>•</span> Canada <span>•</span> 1.41B </div>] offsetx=[-369] offsety=[-275] delay=[250]"><div class="hp_label-container is-single-column "><a href="quote.ashx?t=TLRY" class="tab-link">TLRY</a> <span class="positive-200 fv-label is-positive-200 hp_label ">+44.13%</span></div></td>
</tr><tr class="styled-row is-bordered is-rounded"><td width="25%" class="table-light-cell-cp has-label"data-boxover="cssbody=[hoverchart] cssheader=[tabchrthdr] body=[<img  srcset='https://charts2-node.finviz.com/chart.ashx?cs=m&t=CRCL&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d 1x, https://charts2-node.finviz.com/chart.ashx?cs=m&t=CRCL&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&sf=2 2x' width='324' height='180' alt='' loading='lazy'><div><b>Circle Internet Group Inc</b>Capital Markets <span>•</span> USA <span>•</span> 19.66B </div>] offsetx=[-369] offsety=[-275] delay=[250]"><div class="hp_label-container is-single-column "><a href="quote.ashx?t=CRCL" class="tab-link">CRCL</a> <span class="negative-100 fv-label is-negative-100 hp_label ">-5.76%</span></div></td>
</tr><tr class="styled-row is-bordered is-rounded"><td width="25%" class="table-light-cell-cp has-label"data-boxover="cssbody=[hoverchart] cssheader=[tabchrthdr] body=[<img  srcset='https://charts2-node.finviz.com/chart.ashx?cs=m&t=MU&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d 1x, https://charts2-node.finviz.com/chart.ashx?cs=m&t=MU&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&sf=2 2x' width='324' height='180' alt='' loading='lazy'><div><b>Micron Technology Inc</b>Semiconductors <span>•</span> USA <span>•</span> 271.37B </div>] offsetx=[-369] offsety=[-275] delay=[250]"><div class="hp_label-container is-single-column "><a href="quote.ashx?t=MU" class="tab-link">MU</a> <span class="negative-100 fv-label is-negative-100 hp_label ">-6.70%</span></div></td>
</tr><tr class="styled-row is-bordered is-rounded"><td width="25%" class="table-light-cell-cp has-label"data-boxover="cssbody=[hoverchart] cssheader=[tabchrthdr] body=[<img  srcset='https://charts2-node.finviz.com/chart.ashx?cs=m&t=HOOD&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d 1x, https://charts2-node.finviz.com/chart.ashx?cs=m&t=HOOD&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&sf=2 2x' width='324' height='180' alt='' loading='lazy'><div><b>Robinhood Markets Inc</b>Capital Markets <span>•</span> USA <span>•</span> 107.45B </div>] offsetx=[-369] offsety=[-275] delay=[250]"><div class="hp_label-container is-single-column "><a href="quote.ashx?t=HOOD" class="tab-link">HOOD</a> <span class="negative-50 fv-label is-negative-50 hp_label ">-3.14%</span></div></td>
</tr><tr class="styled-row is-bordered is-rounded"><td width="25%" class="table-light-cell-cp has-label"data-boxover="cssbody=[hoverchart] cssheader=[tabchrthdr] body=[<img  srcset='https://charts2-node.finviz.com/chart.ashx?cs=m&t=CGC&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d 1x, https://charts2-node.finviz.com/chart.ashx?cs=m&t=CGC&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&sf=2 2x' width='324' height='180' alt='' loading='lazy'><div><b>Canopy Growth Corporation</b>Drug Manufacturers - Specialty & Generic <span>•</span> Canada <span>•</span> 595.43M </div>] offsetx=[-369] offsety=[-275] delay=[250]"><div class="hp_label-container is-single-column "><a href="quote.ashx?t=CGC" class="tab-link">CGC</a> <span class="positive-200 fv-label is-positive-200 hp_label ">+53.98%</span></div></td>
</tr><tr class="styled-row is-bordered is-rounded"><td width="25%" class="table-light-cell-cp has-label"data-boxover="cssbody=[hoverchart] cssheader=[tabchrthdr] body=[<img  srcset='https://charts2-node.finviz.com/chart.ashx?cs=m&t=META&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d 1x, https://charts2-node.finviz.com/chart.ashx?cs=m&t=META&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&sf=2 2x' width='324' height='180' alt='' loading='lazy'><div><b>Meta Platforms Inc</b>Internet Content & Information <span>•</span> USA <span>•</span> 1623.80B </div>] offsetx=[-369] offsety=[-275] delay=[250]"><div class="hp_label-container is-single-column "><a href="quote.ashx?t=META" class="tab-link">META</a> <span class="negative-50 fv-label is-negative-50 hp_label ">-1.30%</span></div></td>
</tr><tr class="styled-row is-bordered is-rounded"><td width="25%" class="table-light-cell-cp has-label"data-boxover="cssbody=[hoverchart] cssheader=[tabchrthdr] body=[<img  srcset='https://charts2-node.finviz.com/chart.ashx?cs=m&t=AMZN&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d 1x, https://charts2-node.finviz.com/chart.ashx?cs=m&t=AMZN&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&sf=2 2x' width='324' height='180' alt='' loading='lazy'><div><b>Amazon.com Inc</b>Internet Retail <span>•</span> USA <span>•</span> 2418.02B </div>] offsetx=[-369] offsety=[-275] delay=[250]"><div class="hp_label-container is-single-column "><a href="quote.ashx?t=AMZN" class="tab-link">AMZN</a> <span class="negative-50 fv-label is-negative-50 hp_label ">-1.78%</span></div></td>
</tr><tr class="styled-row is-bordered is-rounded"><td width="25%" class="table-light-cell-cp has-label"data-boxover="cssbody=[hoverchart] cssheader=[tabchrthdr] body=[<img  srcset='https://charts2-node.finviz.com/chart.ashx?cs=m&t=MSFT&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d 1x, https://charts2-node.finviz.com/chart.ashx?cs=m&t=MSFT&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&sf=2 2x' width='324' height='180' alt='' loading='lazy'><div><b>Microsoft Corporation</b>Software - Infrastructure <span>•</span> USA <span>•</span> 3556.62B </div>] offsetx=[-369] offsety=[-275] delay=[250]"><div class="hp_label-container is-single-column "><a href="quote.ashx?t=MSFT" class="tab-link">MSFT</a> <span class="negative-50 fv-label is-negative-50 hp_label ">-1.02%</span></div></td>
</tr></table>
</td>
</tr>
</table>
</td>
<td class="hp_spacer" width="6.5">&nbsp;</td>
<td width="300" valign="top" align="right"><table id="js-small-recent-quotes-table" width="100%" cellpadding="0" cellspacing="0" border="0" style="margin-top: 278px;">
<tr class="t-home-table-top hidden" id="recent-quotes-heading"><td class="ticker-with-change-grid-header"><a href="javascript:void(0)" id="recent-quotes-anchor" class="tab-link"><b>Recent Quotes</b></a></td></tr>
</table>
<script>window.renderRecentQuotesSkeletonSimple();</script></td>
</tr>
</table>
</td>
</tr>
</table>
</td>
</tr>
<tr>
<td style="font-size: 0; line-height: 0"><img src="gfx/nic2x2.gif" style="width:10px;height:10px" alt="" border="0"></td>
</tr>
<tr>
<td align="center">
<table width="100%" cellpadding="0" cellspacing="0" border="0">
<tr>
<td valign="top">
<table class="styled-table-new is-rounded is-condensed is-tabular-nums calendar_table " border="0" cellpadding="1" cellspacing="0" width="100%">
<thead>
<tr>
<th width="8%" align="right">Date</th>
<th width="10%" align="right">Time</th>
<th width="2%" align="center"><img src="gfx/nic2x2.gif" alt="" border="0" style="width:2px;height:2px"></th>
<th width="22%" align="left">Release</th>
<th width="8%" align="left">Impact</th>
<th width="8%" align="left">For</th>
<th width="8%" align="right">Actual</th>
<th width="8%" align="right">Expected</th>
<th width="8%" align="right">Prior</th>
</tr>
</thead>
<tr class="styled-row is-bordered is-rounded is-hoverable cursor-pointer" onclick="window.location='/calendar/economic'">
<td align="right">Dec 13</td>
<td align="center" colspan="7">No economic releases today</td>
<td><img src="gfx/nic2x2.gif" alt="" border="0" style="width:2px;height:2px;"></td>
</tr></table>
</td>
<td class="hp_spacer" width="16"><img src="gfx/nic2x2.gif" alt="" border="0" style="width:16px;height:2px"></td>
<td width="414" class="t-home-table" valign="top">
<table class="styled-table-new is-rounded is-condensed hp_table-earnings" border="0" cellpadding="1" cellspacing="0" width="100%">
<thead>
<tr class="t-home-table-top">
<th width="18%" class="text-left">Date</th>
<th class="text-left" colspan="8" width="78%">Earnings Release</th>
</tr>
</thead>
<tr class="styled-row is-hoverable is-bordered is-rounded cursor-pointer" onclick="window.location='screener.ashx?v=161&f=earningsdate_yesterdayafter&o=-marketcap'">
<td style="white-space:nowrap" valign="top" title="After Market Close"><a href="screener.ashx?v=161&f=earningsdate_yesterdayafter&o=-marketcap" class="hover:underline">Dec 12/a</a></td>
<td data-boxover="cssbody=[hoverchart] cssheader=[tabchrthdr] body=[<img  srcset='https://charts2-node.finviz.com/chart.ashx?cs=m&t=AXR&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d 1x, https://charts2-node.finviz.com/chart.ashx?cs=m&t=AXR&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&sf=2 2x' width='324' height='180' alt='' loading='lazy'><div><b>AMREP Corp</b>Real Estate - Development <span>•</span> USA <span>•</span> 106.97M </div>] offsetx=[-369] offsety=[-275] delay=[250]"><a href="quote.ashx?t=AXR" class="tab-link">AXR</a></td>
<td data-boxover="cssbody=[hoverchart] cssheader=[tabchrthdr] body=[<img  srcset='https://charts2-node.finviz.com/chart.ashx?cs=m&t=EDSA&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d 1x, https://charts2-node.finviz.com/chart.ashx?cs=m&t=EDSA&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&sf=2 2x' width='324' height='180' alt='' loading='lazy'><div><b>Edesa Biotech Inc</b>Biotechnology <span>•</span> Canada <span>•</span> 12.25M </div>] offsetx=[-369] offsety=[-275] delay=[250]"><a href="quote.ashx?t=EDSA" class="tab-link">EDSA</a></td>
<td>&nbsp;&nbsp;&nbsp;</td><td>&nbsp;&nbsp;&nbsp;</td><td>&nbsp;&nbsp;&nbsp;</td><td>&nbsp;&nbsp;&nbsp;</td><td>&nbsp;&nbsp;&nbsp;</td><td>&nbsp;&nbsp;&nbsp;</td></tr><tr class="styled-row is-hoverable is-bordered is-rounded cursor-pointer" onclick="window.location='screener.ashx?v=161&f=earningsdate_todaybefore&o=-marketcap'">
<td style="white-space:nowrap" valign="top" title="Before Market Open"><a href="screener.ashx?v=161&f=earningsdate_todaybefore&o=-marketcap" class="hover:underline">Dec 15/b</a></td>
<td data-boxover="cssbody=[hoverchart] cssheader=[tabchrthdr] body=[<img  srcset='https://charts2-node.finviz.com/chart.ashx?cs=m&t=HYFT&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d 1x, https://charts2-node.finviz.com/chart.ashx?cs=m&t=HYFT&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&sf=2 2x' width='324' height='180' alt='' loading='lazy'><div><b>MindWalk Holdings Corp</b>Biotechnology <span>•</span> USA <span>•</span> 81.70M </div>] offsetx=[-369] offsety=[-275] delay=[250]"><a href="quote.ashx?t=HYFT" class="tab-link">HYFT</a></td>
<td data-boxover="cssbody=[hoverchart] cssheader=[tabchrthdr] body=[<img  srcset='https://charts2-node.finviz.com/chart.ashx?cs=m&t=OPTT&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d 1x, https://charts2-node.finviz.com/chart.ashx?cs=m&t=OPTT&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&sf=2 2x' width='324' height='180' alt='' loading='lazy'><div><b>Ocean Power Technologies</b>Specialty Industrial Machinery <span>•</span> USA <span>•</span> 81.31M </div>] offsetx=[-369] offsety=[-275] delay=[250]"><a href="quote.ashx?t=OPTT" class="tab-link">OPTT</a></td>
<td>&nbsp;&nbsp;&nbsp;</td><td>&nbsp;&nbsp;&nbsp;</td><td>&nbsp;&nbsp;&nbsp;</td><td>&nbsp;&nbsp;&nbsp;</td><td>&nbsp;&nbsp;&nbsp;</td><td>&nbsp;&nbsp;&nbsp;</td></tr><tr class="styled-row is-hoverable is-bordered is-rounded cursor-pointer" onclick="window.location='screener.ashx?v=161&f=earningsdate_todayafter&o=-marketcap'">
<td style="white-space:nowrap" valign="top" title="After Market Close"><a href="screener.ashx?v=161&f=earningsdate_todayafter&o=-marketcap" class="hover:underline">Dec 15/a</a></td>
<td data-boxover="cssbody=[hoverchart] cssheader=[tabchrthdr] body=[<img  srcset='https://charts2-node.finviz.com/chart.ashx?cs=m&t=ABVX&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d 1x, https://charts2-node.finviz.com/chart.ashx?cs=m&t=ABVX&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&sf=2 2x' width='324' height='180' alt='' loading='lazy'><div><b>Abivax ADR</b>Biotechnology <span>•</span> France <span>•</span> 9.78B </div>] offsetx=[-369] offsety=[-275] delay=[250]"><a href="quote.ashx?t=ABVX" class="tab-link">ABVX</a></td>
<td data-boxover="cssbody=[hoverchart] cssheader=[tabchrthdr] body=[<img  srcset='https://charts2-node.finviz.com/chart.ashx?cs=m&t=NAVN&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d 1x, https://charts2-node.finviz.com/chart.ashx?cs=m&t=NAVN&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&sf=2 2x' width='324' height='180' alt='' loading='lazy'><div><b>Navan Inc</b>Software - Application <span>•</span> USA <span>•</span> 3.61B </div>] offsetx=[-369] offsety=[-275] delay=[250]"><a href="quote.ashx?t=NAVN" class="tab-link">NAVN</a></td>
<td data-boxover="cssbody=[hoverchart] cssheader=[tabchrthdr] body=[<img  srcset='https://charts2-node.finviz.com/chart.ashx?cs=m&t=CSBR&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d 1x, https://charts2-node.finviz.com/chart.ashx?cs=m&t=CSBR&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&sf=2 2x' width='324' height='180' alt='' loading='lazy'><div><b>Champions Oncology Inc</b>Biotechnology <span>•</span> USA <span>•</span> 92.66M </div>] offsetx=[-369] offsety=[-275] delay=[250]"><a href="quote.ashx?t=CSBR" class="tab-link">CSBR</a></td>
<td data-boxover="cssbody=[hoverchart] cssheader=[tabchrthdr] body=[<img  srcset='https://charts2-node.finviz.com/chart.ashx?cs=m&t=OTH&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d 1x, https://charts2-node.finviz.com/chart.ashx?cs=m&t=OTH&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&sf=2 2x' width='324' height='180' alt='' loading='lazy'><div><b>Off The Hook YS Inc</b>Auto & Truck Dealerships <span>•</span> USA <span>•</span> 70.75M </div>] offsetx=[-369] offsety=[-275] delay=[250]"><a href="quote.ashx?t=OTH" class="tab-link">OTH</a></td>
<td>&nbsp;&nbsp;&nbsp;</td><td>&nbsp;&nbsp;&nbsp;</td><td>&nbsp;&nbsp;&nbsp;</td><td>&nbsp;&nbsp;&nbsp;</td></tr></table>
</td>
</tr>
</table>
</td>
</tr>
<tr>
<td style="font-size: 0; line-height: 0"><img src="gfx/nic2x2.gif" style="width:10px;height:12px" alt="" border="0"></td>
</tr>
<tr>
<td align="center">
<table border="0" cellpadding="0" cellspacing="0" width="100%">
<tr>
<td valign="top">
<table class="styled-table-new is-rounded is-condensed" border="0" cellpadding="1" cellspacing="0" width="100%">
<thead>
<tr">
<th align="left">Ticker</th>
<th align="left">Latest Insider Trading</th>
<th align="left">Relationship</th>
<th align="left">Date</th>
<th align="center">Transaction</th>
<th align="right">Cost</th>
<th align="right">#Shares</th>
<th align="right">Value($)</th>
</tr>
</thead>
<tr class="fv-insider-row cursor-pointer is-proposedSale-2" onclick="window.location='insidertrading'" valign="top"><td data-boxover="cssbody=[hoverchart] cssheader=[tabchrthdr] body=[<img  srcset='https://charts2-node.finviz.com/chart.ashx?cs=m&t=TLS&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d 1x, https://charts2-node.finviz.com/chart.ashx?cs=m&t=TLS&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&sf=2 2x' width='324' height='180' alt='' loading='lazy'><div><b>Telos Corp</b>Software - Infrastructure <span>•</span> USA <span>•</span> 418.56M </div>] offsetx=[20] offsety=[-280] delay=[300]"><a href="quote.ashx?t=TLS" class="tab-link">TLS</a></td><td><a href="insidertrading?oc=1831624&tc=7" class="tab-link-nw">Frederick D.  Schauf</a></td><td style="white-space:nowrap">Affiliate</td><td style="white-space:nowrap">Dec 12</td><td align="center">Proposed Sale</td><td align="right">5.68</td><td align="right">100,000</td><td align="right">568,000</td></tr><tr class="fv-insider-row cursor-pointer is-option" onclick="window.location='insidertrading'" valign="top"><td data-boxover="cssbody=[hoverchart] cssheader=[tabchrthdr] body=[<img  srcset='https://charts2-node.finviz.com/chart.ashx?cs=m&t=IONQ&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d 1x, https://charts2-node.finviz.com/chart.ashx?cs=m&t=IONQ&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&sf=2 2x' width='324' height='180' alt='' loading='lazy'><div><b>IonQ Inc</b>Computer Hardware <span>•</span> USA <span>•</span> 17.84B </div>] offsetx=[20] offsety=[-280] delay=[300]"><a href="quote.ashx?t=IONQ" class="tab-link">IONQ</a></td><td><a href="insidertrading?oc=1935209&tc=7" class="tab-link-nw">Chou Kathryn K.</a></td><td style="white-space:nowrap">Director</td><td style="white-space:nowrap">Dec 11</td><td align="center">Option Exercise</td><td align="right">4.61</td><td align="right">20,000</td><td align="right">92,200</td></tr><tr class="fv-insider-row cursor-pointer is-sale-2" onclick="window.location='insidertrading'" valign="top"><td data-boxover="cssbody=[hoverchart] cssheader=[tabchrthdr] body=[<img  srcset='https://charts2-node.finviz.com/chart.ashx?cs=m&t=IONQ&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d 1x, https://charts2-node.finviz.com/chart.ashx?cs=m&t=IONQ&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&sf=2 2x' width='324' height='180' alt='' loading='lazy'><div><b>IonQ Inc</b>Computer Hardware <span>•</span> USA <span>•</span> 17.84B </div>] offsetx=[20] offsety=[-280] delay=[300]"><a href="quote.ashx?t=IONQ" class="tab-link">IONQ</a></td><td><a href="insidertrading?oc=1935209&tc=7" class="tab-link-nw">Chou Kathryn K.</a></td><td style="white-space:nowrap">Director</td><td style="white-space:nowrap">Dec 11</td><td align="center">Sale</td><td align="right">51.40</td><td align="right">20,000</td><td align="right">1,027,980</td></tr><tr class="fv-insider-row cursor-pointer is-proposedSale-2" onclick="window.location='insidertrading'" valign="top"><td data-boxover="cssbody=[hoverchart] cssheader=[tabchrthdr] body=[<img  srcset='https://charts2-node.finviz.com/chart.ashx?cs=m&t=IRON&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d 1x, https://charts2-node.finviz.com/chart.ashx?cs=m&t=IRON&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&sf=2 2x' width='324' height='180' alt='' loading='lazy'><div><b>Disc Medicine Inc</b>Biotechnology <span>•</span> USA <span>•</span> 3.47B </div>] offsetx=[20] offsety=[-280] delay=[300]"><a href="quote.ashx?t=IRON" class="tab-link">IRON</a></td><td><a href="insidertrading?oc=1890993&tc=7" class="tab-link-nw">AI DMI LLC</a></td><td style="white-space:nowrap">Affiliate</td><td style="white-space:nowrap">Dec 12</td><td align="center">Proposed Sale</td><td align="right">91.85</td><td align="right">29,388</td><td align="right">2,699,288</td></tr><tr class="fv-insider-row cursor-pointer is-sale-2" onclick="window.location='insidertrading'" valign="top"><td data-boxover="cssbody=[hoverchart] cssheader=[tabchrthdr] body=[<img  srcset='https://charts2-node.finviz.com/chart.ashx?cs=m&t=LQDT&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d 1x, https://charts2-node.finviz.com/chart.ashx?cs=m&t=LQDT&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&sf=2 2x' width='324' height='180' alt='' loading='lazy'><div><b>Liquidity Services Inc</b>Internet Retail <span>•</span> USA <span>•</span> 974.96M </div>] offsetx=[20] offsety=[-280] delay=[300]"><a href="quote.ashx?t=LQDT" class="tab-link">LQDT</a></td><td><a href="insidertrading?oc=1797913&tc=7" class="tab-link-nw">Dyer Katharin S</a></td><td style="white-space:nowrap">Director</td><td style="white-space:nowrap">Dec 11</td><td align="center">Sale</td><td align="right">31.62</td><td align="right">8,196</td><td align="right">259,158</td></tr><tr class="fv-insider-row cursor-pointer is-proposedSale-2" onclick="window.location='insidertrading'" valign="top"><td data-boxover="cssbody=[hoverchart] cssheader=[tabchrthdr] body=[<img  srcset='https://charts2-node.finviz.com/chart.ashx?cs=m&t=MELI&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d 1x, https://charts2-node.finviz.com/chart.ashx?cs=m&t=MELI&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&sf=2 2x' width='324' height='180' alt='' loading='lazy'><div><b>MercadoLibre Inc</b>Internet Retail <span>•</span> USA <span>•</span> 102.20B </div>] offsetx=[20] offsety=[-280] delay=[300]"><a href="quote.ashx?t=MELI" class="tab-link">MELI</a></td><td><a href="insidertrading?oc=1866429&tc=7" class="tab-link-nw">Dubugras Henrique Va</a></td><td style="white-space:nowrap">Affiliate</td><td style="white-space:nowrap">Dec 12</td><td align="center">Proposed Sale</td><td align="right">2019.81</td><td align="right">845</td><td align="right">1,706,739</td></tr></table>
</td>
<td class="hp_spacer" width="16"><img src="gfx/nic2x2.gif" alt="" border="0" style="width:16px;height:2px"></td>
<td class="t-home-table table-insider-right" valign="top" width="414">
<table class="styled-table-new is-rounded is-condensed" border="0" cellpadding="1" cellspacing="0" width="100%">
<thead>
<tr">
<th style="padding-right: 8px" align="left">Ticker</th>
<th align="left">Top Insider Trading</th>
<th style="padding-left: 4px" align="left">Date</th>
<th align="center">Transaction</th>
<th align="right">Value($)</th>
</tr>
</thead>
<tr class="fv-insider-row cursor-pointer is-buy-2" onclick="window.location='insidertrading?or=-10&tv=100000&tc=1&o=-transactionValue'" valign="top"><td width="1%" data-boxover="cssbody=[hoverchart] cssheader=[tabchrthdr] body=[<img  srcset='https://charts2-node.finviz.com/chart.ashx?cs=m&t=IMVT&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d 1x, https://charts2-node.finviz.com/chart.ashx?cs=m&t=IMVT&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&sf=2 2x' width='324' height='180' alt='' loading='lazy'><div><b>Immunovant Inc</b>Biotechnology <span>•</span> USA <span>•</span> 4.63B </div>] offsetx=[-300] offsety=[-280] delay=[300]"><a href="quote.ashx?t=IMVT" class="tab-link">IMVT</a></td><td style="width:1px;max-width:1px"><div style="display: flex"><a style="overflow: hidden;text-overflow: ellipsis;white-space: nowrap;" href="insidertrading?oc=1635088&tc=7" class="tab-link-nw">Roivant Sciences Ltd.</div></td><td width="1%" style="white-space:nowrap; padding-left: 4px; padding-right: 2px">Dec 12</td><td width="1%" align="center" style="white-space:nowrap; padding-left: 4px; padding-right: 4px">Buy</td><td width="1%" style="padding-left: 2px" align="right">349,999,986</td></tr><tr class="fv-insider-row cursor-pointer is-buy-2" onclick="window.location='insidertrading?or=-10&tv=100000&tc=1&o=-transactionValue'" valign="top"><td width="1%" data-boxover="cssbody=[hoverchart] cssheader=[tabchrthdr] body=[<img  srcset='https://charts2-node.finviz.com/chart.ashx?cs=m&t=ROIV&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d 1x, https://charts2-node.finviz.com/chart.ashx?cs=m&t=ROIV&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&sf=2 2x' width='324' height='180' alt='' loading='lazy'><div><b>Roivant Sciences Ltd</b>Biotechnology <span>•</span> United Kingdom <span>•</span> 15.37B </div>] offsetx=[-300] offsety=[-280] delay=[300]"><a href="quote.ashx?t=ROIV" class="tab-link">ROIV</a></td><td style="width:1px;max-width:1px"><div style="display: flex"><a style="overflow: hidden;text-overflow: ellipsis;white-space: nowrap;" href="insidertrading?oc=1635088&tc=7" class="tab-link-nw">Roivant Sciences Ltd.</div></td><td width="1%" style="white-space:nowrap; padding-left: 4px; padding-right: 2px">Dec 12</td><td width="1%" align="center" style="white-space:nowrap; padding-left: 4px; padding-right: 4px">Buy</td><td width="1%" style="padding-left: 2px" align="right">349,999,986</td></tr><tr class="fv-insider-row cursor-pointer is-buy-2" onclick="window.location='insidertrading?or=-10&tv=100000&tc=1&o=-transactionValue'" valign="top"><td width="1%" data-boxover="cssbody=[hoverchart] cssheader=[tabchrthdr] body=[<img  srcset='https://charts2-node.finviz.com/chart.ashx?cs=m&t=KYMR&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d 1x, https://charts2-node.finviz.com/chart.ashx?cs=m&t=KYMR&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&sf=2 2x' width='324' height='180' alt='' loading='lazy'><div><b>Kymera Therapeutics Inc</b>Biotechnology <span>•</span> USA <span>•</span> 7.08B </div>] offsetx=[-300] offsety=[-280] delay=[300]"><a href="quote.ashx?t=KYMR" class="tab-link">KYMR</a></td><td style="width:1px;max-width:1px"><div style="display: flex"><a style="overflow: hidden;text-overflow: ellipsis;white-space: nowrap;" href="insidertrading?oc=1263508&tc=7" class="tab-link-nw">BAKER BROS. ADVISORS LP</div></td><td width="1%" style="white-space:nowrap; padding-left: 4px; padding-right: 2px">Dec 11</td><td width="1%" align="center" style="white-space:nowrap; padding-left: 4px; padding-right: 4px">Buy</td><td width="1%" style="padding-left: 2px" align="right">172,499,918</td></tr><tr class="fv-insider-row cursor-pointer is-proposedSale-2" onclick="window.location='insidertrading?or=-10&tv=100000&tc=2&o=-transactionValue'" valign="top"><td width="1%" data-boxover="cssbody=[hoverchart] cssheader=[tabchrthdr] body=[<img  srcset='https://charts2-node.finviz.com/chart.ashx?cs=m&t=COHR&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d 1x, https://charts2-node.finviz.com/chart.ashx?cs=m&t=COHR&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&sf=2 2x' width='324' height='180' alt='' loading='lazy'><div><b>Coherent Corp</b>Scientific & Technical Instruments <span>•</span> USA <span>•</span> 28.03B </div>] offsetx=[-300] offsety=[-280] delay=[300]"><a href="quote.ashx?t=COHR" class="tab-link">COHR</a></td><td style="width:1px;max-width:1px"><div style="display: flex"><a style="overflow: hidden;text-overflow: ellipsis;white-space: nowrap;" href="insidertrading?oc=1910890&tc=7" class="tab-link-nw">BCPE Watson (DE) BML, LP</div></td><td width="1%" style="white-space:nowrap; padding-left: 4px; padding-right: 2px">Dec 10</td><td width="1%" align="center" style="white-space:nowrap; padding-left: 4px; padding-right: 4px">Proposed Sale</td><td width="1%" style="padding-left: 2px" align="right">947,750,000</td></tr><tr class="fv-insider-row cursor-pointer is-proposedSale-2" onclick="window.location='insidertrading?or=-10&tv=100000&tc=2&o=-transactionValue'" valign="top"><td width="1%" data-boxover="cssbody=[hoverchart] cssheader=[tabchrthdr] body=[<img  srcset='https://charts2-node.finviz.com/chart.ashx?cs=m&t=PRMB&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d 1x, https://charts2-node.finviz.com/chart.ashx?cs=m&t=PRMB&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&sf=2 2x' width='324' height='180' alt='' loading='lazy'><div><b>Primo Brands Corp</b>Beverages - Non-Alcoholic <span>•</span> USA <span>•</span> 6.01B </div>] offsetx=[-300] offsety=[-280] delay=[300]"><a href="quote.ashx?t=PRMB" class="tab-link">PRMB</a></td><td style="width:1px;max-width:1px"><div style="display: flex"><a style="overflow: hidden;text-overflow: ellipsis;white-space: nowrap;" href="insidertrading?oc=2042697&tc=7" class="tab-link-nw">Triton Water Parent Holdings, LP</div></td><td width="1%" style="white-space:nowrap; padding-left: 4px; padding-right: 2px">Dec 08</td><td width="1%" align="center" style="white-space:nowrap; padding-left: 4px; padding-right: 4px">Proposed Sale</td><td width="1%" style="padding-left: 2px" align="right">295,082,479</td></tr><tr class="fv-insider-row cursor-pointer is-sale-2" onclick="window.location='insidertrading?or=-10&tv=100000&tc=2&o=-transactionValue'" valign="top"><td width="1%" data-boxover="cssbody=[hoverchart] cssheader=[tabchrthdr] body=[<img  srcset='https://charts2-node.finviz.com/chart.ashx?cs=m&t=RYAN&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d 1x, https://charts2-node.finviz.com/chart.ashx?cs=m&t=RYAN&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&sf=2 2x' width='324' height='180' alt='' loading='lazy'><div><b>Ryan Specialty Holdings Inc</b>Insurance - Specialty <span>•</span> USA <span>•</span> 14.31B </div>] offsetx=[-300] offsety=[-280] delay=[300]"><a href="quote.ashx?t=RYAN" class="tab-link">RYAN</a></td><td style="width:1px;max-width:1px"><div style="display: flex"><a style="overflow: hidden;text-overflow: ellipsis;white-space: nowrap;" href="insidertrading?oc=937226&tc=7" class="tab-link-nw">ONEX CORP</div></td><td width="1%" style="white-space:nowrap; padding-left: 4px; padding-right: 2px">Dec 05</td><td width="1%" align="center" style="white-space:nowrap; padding-left: 4px; padding-right: 4px">Sale</td><td width="1%" style="padding-left: 2px" align="right">225,936,344</td></tr></table>
</td>
</tr>
</table>
</td>
</tr>
<tr>
<td style="font-size: 0; line-height: 0"><img src="gfx/nic2x2.gif" style="width:10px;height:12px" alt="" border="0"></td>
</tr>
<tr>
<td align="center">
<table width="100%" cellpadding="0" cellspacing="0" border="0">
<tr>
<td class="quote-table-container whitespace-nowrap " width="414">
<table width="100%" cellpadding="1" cellspacing="0" class="styled-table-new is-rounded is-condensed is-tabular-nums" border="0">
<thead><tr class="">
<th class="text-left"><b>Futures</b></th>
<th width="90" align="right">Last</th>
<th width="90" align="right">Change</th>
<th width="90" align="right">Change %</th>
</tr>
</thead><tr class="styled-row is-hoverable is-bordered is-rounded has-color-text cursor-pointer" onclick="window.location='futures_charts.ashx?t=CL'" data-boxover="cssbody=[hoverchart] cssheader=[tabchrthdr] body=[<img  srcset='https://charts2-node.finviz.com/chart.ashx?cs=m&t=@cl&tf=i5&s=linear&pm=0&am=0&ct=candle_stick&tm=d 1x, https://charts2-node.finviz.com/chart.ashx?cs=m&t=@cl&tf=i5&s=linear&pm=0&am=0&ct=candle_stick&tm=d&sf=2 2x' width='324' height='180' alt='' loading='lazy'>] offsetx=[0] offsety=[-220] delay=[0]">
<td><a href="futures_charts.ashx?t=CL" class="tab-link">Crude Oil</a></td>
<td align="right"><span class="color-text is-negative">57.53</span></td>
<td align="right"><span class="color-text is-negative">-0.07</span></td>
<td align="right"><span class="color-text is-negative">-0.12%</span></td>
</tr>
<tr class="styled-row is-hoverable is-bordered is-rounded has-color-text cursor-pointer" onclick="window.location='futures_charts.ashx?t=NG'" data-boxover="cssbody=[hoverchart] cssheader=[tabchrthdr] body=[<img  srcset='https://charts2-node.finviz.com/chart.ashx?cs=m&t=@ng&tf=i5&s=linear&pm=0&am=0&ct=candle_stick&tm=d 1x, https://charts2-node.finviz.com/chart.ashx?cs=m&t=@ng&tf=i5&s=linear&pm=0&am=0&ct=candle_stick&tm=d&sf=2 2x' width='324' height='180' alt='' loading='lazy'>] offsetx=[0] offsety=[-220] delay=[0]">
<td><a href="futures_charts.ashx?t=NG" class="tab-link">Natural Gas</a></td>
<td align="right"><span class="color-text is-negative">4.1010</span></td>
<td align="right"><span class="color-text is-negative">-0.1300</span></td>
<td align="right"><span class="color-text is-negative">-3.07%</span></td>
</tr>
<tr class="styled-row is-hoverable is-bordered is-rounded has-color-text cursor-pointer" onclick="window.location='futures_charts.ashx?t=GC'" data-boxover="cssbody=[hoverchart] cssheader=[tabchrthdr] body=[<img  srcset='https://charts2-node.finviz.com/chart.ashx?cs=m&t=@gc&tf=i5&s=linear&pm=0&am=0&ct=candle_stick&tm=d 1x, https://charts2-node.finviz.com/chart.ashx?cs=m&t=@gc&tf=i5&s=linear&pm=0&am=0&ct=candle_stick&tm=d&sf=2 2x' width='324' height='180' alt='' loading='lazy'>] offsetx=[0] offsety=[-220] delay=[0]">
<td><a href="futures_charts.ashx?t=GC" class="tab-link">Gold</a></td>
<td align="right"><span class="color-text is-positive">4329.80</span></td>
<td align="right"><span class="color-text is-positive">+16.80</span></td>
<td align="right"><span class="color-text is-positive">+0.39%</span></td>
</tr>
<tr class="styled-row is-hoverable is-bordered is-rounded has-color-text cursor-pointer" onclick="window.location='futures_charts.ashx?t=YM'" data-boxover="cssbody=[hoverchart] cssheader=[tabchrthdr] body=[<img  srcset='https://charts2-node.finviz.com/chart.ashx?cs=m&t=@ym&tf=i5&s=linear&pm=0&am=0&ct=candle_stick&tm=d 1x, https://charts2-node.finviz.com/chart.ashx?cs=m&t=@ym&tf=i5&s=linear&pm=0&am=0&ct=candle_stick&tm=d&sf=2 2x' width='324' height='180' alt='' loading='lazy'>] offsetx=[0] offsety=[-220] delay=[0]">
<td><a href="futures_charts.ashx?t=YM" class="tab-link">Dow</a></td>
<td align="right"><span class="color-text is-negative">48517.00</span></td>
<td align="right"><span class="color-text is-negative">-615.00</span></td>
<td align="right"><span class="color-text is-negative">-1.25%</span></td>
</tr>
<tr class="styled-row is-hoverable is-bordered is-rounded has-color-text cursor-pointer" onclick="window.location='futures_charts.ashx?t=ES'" data-boxover="cssbody=[hoverchart] cssheader=[tabchrthdr] body=[<img  srcset='https://charts2-node.finviz.com/chart.ashx?cs=m&t=@es&tf=i5&s=linear&pm=0&am=0&ct=candle_stick&tm=d 1x, https://charts2-node.finviz.com/chart.ashx?cs=m&t=@es&tf=i5&s=linear&pm=0&am=0&ct=candle_stick&tm=d&sf=2 2x' width='324' height='180' alt='' loading='lazy'>] offsetx=[0] offsety=[-220] delay=[0]">
<td><a href="futures_charts.ashx?t=ES" class="tab-link">S&P 500</a></td>
<td align="right"><span class="color-text is-negative">6833.50</span></td>
<td align="right"><span class="color-text is-negative">-133.50</span></td>
<td align="right"><span class="color-text is-negative">-1.92%</span></td>
</tr>
<tr class="styled-row is-hoverable is-bordered is-rounded has-color-text cursor-pointer" onclick="window.location='futures_charts.ashx?t=NQ'" data-boxover="cssbody=[hoverchart] cssheader=[tabchrthdr] body=[<img  srcset='https://charts2-node.finviz.com/chart.ashx?cs=m&t=@nq&tf=i5&s=linear&pm=0&am=0&ct=candle_stick&tm=d 1x, https://charts2-node.finviz.com/chart.ashx?cs=m&t=@nq&tf=i5&s=linear&pm=0&am=0&ct=candle_stick&tm=d&sf=2 2x' width='324' height='180' alt='' loading='lazy'>] offsetx=[0] offsety=[-220] delay=[0]">
<td><a href="futures_charts.ashx?t=NQ" class="tab-link">Nasdaq 100</a></td>
<td align="right"><span class="color-text is-negative">25202.50</span></td>
<td align="right"><span class="color-text is-negative">-767.00</span></td>
<td align="right"><span class="color-text is-negative">-2.95%</span></td>
</tr>
<tr class="styled-row is-hoverable is-bordered is-rounded has-color-text cursor-pointer" onclick="window.location='futures_charts.ashx?t=ER2'" data-boxover="cssbody=[hoverchart] cssheader=[tabchrthdr] body=[<img  srcset='https://charts2-node.finviz.com/chart.ashx?cs=m&t=@er2&tf=i5&s=linear&pm=0&am=0&ct=candle_stick&tm=d 1x, https://charts2-node.finviz.com/chart.ashx?cs=m&t=@er2&tf=i5&s=linear&pm=0&am=0&ct=candle_stick&tm=d&sf=2 2x' width='324' height='180' alt='' loading='lazy'>] offsetx=[0] offsety=[-220] delay=[0]">
<td><a href="futures_charts.ashx?t=ER2" class="tab-link">Russell 2000</a></td>
<td align="right"><span class="color-text is-negative">2553.80</span></td>
<td align="right"><span class="color-text is-negative">-59.70</span></td>
<td align="right"><span class="color-text is-negative">-2.28%</span></td>
</tr>
</table>
</td>
<td class="hp_spacer" width="16"><img src="gfx/nic2x2.gif" style="width:16px;height:2px" alt="" border="0"></td>
<td>
<table width="100%" cellpadding="0" cellspacing="0" border="0">
<tr><td colspan="3" class="h-12 p-2.5 text-2xs text-center text-link"><div id="IC_D_234x20_1"class="relative overflow-hidden flex items-center justify-center w-full mx-auto" style="width:234px;height:40px;max-height:40px"></div></td></tr><tr>
<td class="hidden xl:table-cell text-center w-1/4 align-middle"><div id="IC_D_88x31_2"class="relative overflow-hidden flex items-center justify-center w-full mx-auto" style="width:88px;height:31px;max-height:31px"></div></td>
<td align="center" valign="middle">
<div class="flex flex-col">
<span class="text-base font-bold leading-5 text-gray-600 dark:text-gray-200">First Time Here?</span>
    <div class="mt-1 flex justify-center space-x-2">
        <a href="help/guided-tour.ashx" class="gt-button fv-button is-medium is-primary">
            <svg width="16" height="16">
    <use href="/assets/dist-icons/icons.svg?rev=35#videoHorizontal"/>
</svg>
            <div class="ml-2 whitespace-nowrap">Watch the Guided Tour</div>
        </a>
        <button class="gt-button fv-button is-medium" onclick="handleCloseGuidedTourClick()">Close</button>
    </div></div>
</td>
<td class="hidden xl:table-cell text-center w-1/4 align-middle"><div id="IC_D_88x31_3"class="relative overflow-hidden flex items-center justify-center w-full mx-auto" style="width:88px;height:31px;max-height:31px"></div></td>
</tr>
</table>
</td>
<td class="hp_spacer" width="16"><img src="gfx/nic2x2.gif" style="width:16px;height:2px" alt="" border="0"></td>
<td class="quote-table-container whitespace-nowrap " width="414">
<table width="100%" cellpadding="1" cellspacing="0" class="styled-table-new is-rounded is-condensed is-tabular-nums" border="0">
<thead><tr class="">
<th class="text-left"><b>Forex & Bonds</b></th>
<th width="90" align="right">Last</th>
<th width="90" align="right">Change</th>
<th width="90" align="right">Change %</th>
</tr>
</thead><tr class="styled-row is-hoverable is-bordered is-rounded has-color-text cursor-pointer" onclick="window.location='forex_charts.ashx?t=EURUSD'" data-boxover="cssbody=[hoverchart] cssheader=[tabchrthdr] body=[<img  srcset='https://charts2-node.finviz.com/chart.ashx?cs=m&t=@eurusd&tf=i5&s=linear&pm=0&am=0&ct=candle_stick&tm=d 1x, https://charts2-node.finviz.com/chart.ashx?cs=m&t=@eurusd&tf=i5&s=linear&pm=0&am=0&ct=candle_stick&tm=d&sf=2 2x' width='324' height='180' alt='' loading='lazy'>] offsetx=[-370] offsety=[-220] delay=[0]">
<td><a href="forex_charts.ashx?t=EURUSD" class="tab-link">EUR/USD</a></td>
<td align="right"><span class="color-text is-positive">1.1738</span></td>
<td align="right"><span class="color-text is-positive">+0.0000</span></td>
<td align="right"><span class="color-text is-positive">+0.00%</span></td>
</tr>
<tr class="styled-row is-hoverable is-bordered is-rounded has-color-text cursor-pointer" onclick="window.location='forex_charts.ashx?t=USDJPY'" data-boxover="cssbody=[hoverchart] cssheader=[tabchrthdr] body=[<img  srcset='https://charts2-node.finviz.com/chart.ashx?cs=m&t=@usdjpy&tf=i5&s=linear&pm=0&am=0&ct=candle_stick&tm=d 1x, https://charts2-node.finviz.com/chart.ashx?cs=m&t=@usdjpy&tf=i5&s=linear&pm=0&am=0&ct=candle_stick&tm=d&sf=2 2x' width='324' height='180' alt='' loading='lazy'>] offsetx=[-370] offsety=[-220] delay=[0]">
<td><a href="forex_charts.ashx?t=USDJPY" class="tab-link">USD/JPY</a></td>
<td align="right"><span class="color-text is-positive">155.80</span></td>
<td align="right"><span class="color-text is-positive">+0.22</span></td>
<td align="right"><span class="color-text is-positive">+0.14%</span></td>
</tr>
<tr class="styled-row is-hoverable is-bordered is-rounded has-color-text cursor-pointer" onclick="window.location='forex_charts.ashx?t=GBPUSD'" data-boxover="cssbody=[hoverchart] cssheader=[tabchrthdr] body=[<img  srcset='https://charts2-node.finviz.com/chart.ashx?cs=m&t=@gbpusd&tf=i5&s=linear&pm=0&am=0&ct=candle_stick&tm=d 1x, https://charts2-node.finviz.com/chart.ashx?cs=m&t=@gbpusd&tf=i5&s=linear&pm=0&am=0&ct=candle_stick&tm=d&sf=2 2x' width='324' height='180' alt='' loading='lazy'>] offsetx=[-370] offsety=[-220] delay=[0]">
<td><a href="forex_charts.ashx?t=GBPUSD" class="tab-link">GBP/USD</a></td>
<td align="right"><span class="color-text is-negative">1.3364</span></td>
<td align="right"><span class="color-text is-negative">-0.0019</span></td>
<td align="right"><span class="color-text is-negative">-0.14%</span></td>
</tr>
<tr class="styled-row is-hoverable is-bordered is-rounded has-color-text cursor-pointer" onclick="window.location='crypto_charts.ashx?t=BTCUSD'" data-boxover="cssbody=[hoverchart] cssheader=[tabchrthdr] body=[<img  srcset='https://charts2-node.finviz.com/chart.ashx?cs=m&t=@btcusd&tf=i5&s=linear&pm=0&am=0&ct=candle_stick&tm=d 1x, https://charts2-node.finviz.com/chart.ashx?cs=m&t=@btcusd&tf=i5&s=linear&pm=0&am=0&ct=candle_stick&tm=d&sf=2 2x' width='324' height='180' alt='' loading='lazy'>] offsetx=[-370] offsety=[-220] delay=[0]">
<td><a href="crypto_charts.ashx?t=BTCUSD" class="tab-link">BTC/USD</a></td>
<td align="right"><span class="color-text is-negative">90278.40</span></td>
<td align="right"><span class="color-text is-negative">-67.70</span></td>
<td align="right"><span class="color-text is-negative">-0.07%</span></td>
</tr>
<tr class="styled-row is-hoverable is-bordered is-rounded has-color-text">
<td class="whitespace-nowrap">5-Year Treasury</td>
<td align="right"><span class="color-text is-positive">3.751</span></td>
<td align="right"><span class="color-text is-positive">+0.036</span></td>
<td align="right"><span class="color-text is-positive">+0.97%</span></td>
</tr>
<tr class="styled-row is-hoverable is-bordered is-rounded has-color-text">
<td class="whitespace-nowrap">10-Year Treasury</td>
<td align="right"><span class="color-text is-positive">4.194</span></td>
<td align="right"><span class="color-text is-positive">+0.053</span></td>
<td align="right"><span class="color-text is-positive">+1.28%</span></td>
</tr>
<tr class="styled-row is-hoverable is-bordered is-rounded has-color-text">
<td class="whitespace-nowrap">30-Year Treasury</td>
<td align="right"><span class="color-text is-positive">4.858</span></td>
<td align="right"><span class="color-text is-positive">+0.068</span></td>
<td align="right"><span class="color-text is-positive">+1.42%</span></td>
</tr>
</table>
</td>
</tr>
</table>
</td>
</tr>
</table>
</div>
<script src="/assets/dist/9215.v1.4186333b.js" onerror="window.handleScriptNotLoaded(this)"></script><script src="/assets/dist/2332.v1.8cced348.js" onerror="window.handleScriptNotLoaded(this)"></script><script src="/assets/dist/4417.v1.de0121af.js" onerror="window.handleScriptNotLoaded(this)"></script><script src="/assets/dist/463.v1.81aa98cd.js" onerror="window.handleScriptNotLoaded(this)"></script><script src="/assets/dist/3404.v1.fd2315ec.js" onerror="window.handleScriptNotLoaded(this)"></script><script src="/assets/dist/6769.v1.7571a412.js" onerror="window.handleScriptNotLoaded(this)"></script><script src="/assets/dist/3654.v1.696c68cc.js" onerror="window.handleScriptNotLoaded(this)"></script><script src="/assets/dist/6019.v1.f4bb9181.js" onerror="window.handleScriptNotLoaded(this)"></script><script src="/assets/dist/4927.v1.fc34b9ec.js" onerror="window.handleScriptNotLoaded(this)"></script><script src="/assets/dist/2239.v1.e6d117fd.js" onerror="window.handleScriptNotLoaded(this)"></script><script src="/assets/dist/home.v1.5fb1ce0e.js" onerror="window.handleScriptNotLoaded(this)"></script><link rel="preload" as="script" href="/assets/dist/recent_quotes.v1.c908db63.js" data-chunk-id="recent_quotes"><script id="map-data" type="application/json">{ "perfDataSec": {"nodes":{"CF":0.674,"CTVA":0.121,"MOS":4.049,"MLM":-0.606,"VMC":-1.113,"DOW":-2.482,"FCX":-1.517,"NEM":-1.287,"ALB":-1.375,"APD":-0.3,"DD":-1.35,"ECL":0.869,"IFF":0.016,"LIN":3.209,"LYB":-1.596,"PPG":0.759,"SHW":-0.185,"SOLS":-0.577,"NUE":-0.877,"STLD":-0.601,"APP":-6.459,"OMC":0.225,"TTD":-0.999,"EA":0.034,"TTWO":-0.388,"DIS":0.126,"FOX":-0.567,"FOXA":-1.003,"LYV":0.895,"NFLX":1.169,"NWS":0.338,"NWSA":0.46,"PSKY":-2.691,"TKO":2.017,"WBD":1.662,"GOOG":-1.014,"GOOGL":-1.005,"META":-1.299,"MTCH":0.03,"CHTR":-2.575,"CMCSA":-1.341,"T":1.152,"TMUS":-0.087,"VZ":1.666,"RL":0.707,"LULU":9.604,"ROST":-0.568,"TJX":0.36,"F":0.954,"GM":0.049,"TSLA":2.701,"APTV":-1.402,"AZO":-0.674,"GPC":-1.799,"LKQ":-0.161,"ORLY":0.16,"DECK":-0.178,"NKE":-0.399,"MHK":-0.151,"HD":0.613,"LOW":-0.318,"AMZN":-1.776,"DASH":1.323,"EBAY":1.137,"HAS":-2.87,"HLT":0.741,"MAR":0.762,"TPR":-0.227,"AMCR":-1.2,"AVY":0.517,"BALL":3.455,"IP":-1.306,"PKG":-0.112,"SW":-2.157,"ROL":0.941,"DHI":0.805,"LEN":0.185,"NVR":0.089,"PHM":-0.894,"LVS":-1.45,"MGM":-0.107,"WYNN":-0.953,"CMG":3.642,"DPZ":-0.447,"DRI":-0.556,"MCD":2.263,"SBUX":0.72,"YUM":1.985,"BBY":-2.014,"TSCO":0.309,"ULTA":1.378,"WSM":-0.893,"ABNB":0.305,"BKNG":0.416,"CCL":-0.79,"EXPE":-2.468,"NCLH":1.509,"RCL":-0.3,"STZ":-1.424,"TAP":1.147,"KDP":0.136,"KO":2.04,"MNST":2.042,"PEP":1.08,"BF-B":-0.389,"HSY":0.138,"MDLZ":0.465,"COST":-0.001,"DG":0.399,"DLTR":-0.077,"TGT":0.124,"WMT":1.021,"ADM":0.15,"BG":-0.461,"TSN":0.588,"SYY":0.148,"KR":1.575,"CHD":1.244,"CL":1.411,"CLX":1.148,"EL":-1.383,"KMB":-0.29,"KVUE":0.058,"PG":1.478,"CAG":0.852,"CPB":1.09,"GIS":0.995,"HRL":1.434,"KHC":0.246,"LW":0.303,"MKC":1.304,"SJM":0.654,"MO":0.051,"PM":1.789,"APA":-0.077,"COP":-1.21,"CTRA":-0.83,"DVN":-0.053,"EOG":-1.37,"EQT":-0.892,"EXE":-1.347,"FANG":-0.229,"OXY":-0.316,"TPL":-5.803,"BKR":-1.264,"HAL":-1.717,"SLB":-2.206,"CVX":-0.484,"XOM":-0.602,"KMI":-0.336,"OKE":-0.041,"TRGP":-1.368,"WMB":-1.937,"MPC":-0.716,"PSX":-1.387,"VLO":-2.1,"AMP":-0.999,"APO":-1.517,"BEN":0.043,"BLK":-1.157,"BX":-1.901,"IVZ":-2.741,"KKR":-4.322,"NTRS":-1.121,"PFG":-1.748,"RJF":-0.037,"STT":-1.489,"TROW":-0.057,"BAC":1.063,"BK":-1.39,"C":0.054,"JPM":0.359,"WFC":0.184,"CFG":0.069,"FITB":-0.496,"HBAN":-0.503,"KEY":-0.145,"MTB":-0.928,"PNC":-0.426,"RF":-0.862,"TFC":0.382,"USB":-0.299,"GS":-2.532,"HOOD":-3.145,"IBKR":-2.891,"MS":-1.043,"SCHW":-0.412,"AXP":-0.605,"COF":-0.593,"MA":1.519,"PYPL":-0.049,"SYF":-1.681,"V":0.637,"CBOE":0.765,"CME":0.42,"COIN":-0.58,"FDS":0.316,"ICE":0.067,"MCO":0.225,"MSCI":0.269,"NDAQ":-0.298,"SPGI":0.697,"ACGL":0.299,"AIG":2.474,"BRK-B":0.74,"AFL":1.102,"GL":0.302,"MET":-0.109,"PRU":-0.077,"AIZ":0.561,"ALL":0.174,"CB":0.814,"CINF":0.509,"HIG":0.007,"L":-0.325,"PGR":1.914,"TRV":0.859,"WRB":-0.014,"EG":0.857,"AJG":3.134,"AON":1.839,"BRO":2.602,"ERIE":3,"MMC":1.493,"WTW":0.415,"INCY":-0.718,"MRNA":-0.574,"REGN":-0.738,"TECH":-2.904,"VRTX":1.37,"A":-2.233,"CRL":-0.72,"DGX":0.545,"DHR":-2.599,"IDXX":-0.466,"IQV":-1.646,"LH":-0.208,"MTD":-1.965,"RVTY":-3.301,"TMO":-1.144,"WAT":-1.754,"ABBV":-0.295,"AMGN":0.113,"BIIB":0.928,"BMY":2.363,"GILD":-2.281,"JNJ":0.748,"LLY":1.796,"MRK":1.303,"PFE":0.194,"VTRS":0.518,"ZTS":0.85,"CI":0.896,"CNC":0.964,"CVS":-1.744,"ELV":-0.319,"HUM":0.735,"MOH":0.959,"UNH":1.518,"DVA":0.848,"HCA":0.502,"UHS":-0.882,"ABT":1.768,"BSX":0.905,"DXCM":-2.872,"EW":-1.377,"GEHC":-2.429,"MDT":0.12,"PODD":0.52,"STE":-0.277,"SYK":0.317,"ZBH":-0.93,"CAH":-0.071,"COR":0.435,"HSIC":0.407,"MCK":-0.213,"ALGN":0.952,"BAX":1.323,"BDX":0.23,"COO":-0.037,"HOLX":0.227,"ISRG":-0.921,"RMD":-0.048,"SOLV":0.229,"WST":-1.827,"AXON":-2.883,"BA":1.829,"GD":-1.168,"GE":3.949,"HII":0.061,"HWM":1.235,"LHX":-1.004,"LMT":1.131,"NOC":1.736,"RTX":0.699,"TDG":-1.734,"TXT":0.368,"DAL":-1.063,"LUV":1.055,"UAL":-1.43,"BLDR":-1.265,"CARR":-2.235,"JCI":-2.795,"LII":-1.767,"MAS":-1.159,"TT":-3.022,"HON":-0.098,"MMM":0.178,"EFX":0.104,"VRSK":0.393,"HUBB":-3.202,"EME":-2.491,"J":-0.739,"PWR":-6.168,"CAT":-4.431,"DE":1.862,"PCAR":-1.091,"FAST":0.623,"GWW":-0.954,"POOL":-0.008,"CHRW":-1.696,"EXPD":-0.823,"FDX":-0.155,"JBHT":-0.436,"UPS":0.438,"VLTO":-0.02,"CSX":0.646,"NSC":0.993,"UNP":1.622,"WAB":-1.543,"URI":-1.864,"ALLE":-2.356,"CPRT":-0.052,"CTAS":-0.688,"AME":-1.03,"AOS":0.204,"CMI":-2.552,"DOV":-1.073,"EMR":-2.099,"ETN":-5.246,"GEV":-4.614,"GNRC":-4.116,"IEX":-1.275,"IR":-2.013,"ITW":0.237,"NDSN":0.435,"OTIS":0.467,"PH":-1.586,"PNR":0.113,"ROK":-1.905,"XYL":-2.113,"SNA":-0.188,"SWK":-1.124,"ODFL":0.359,"RSG":1.17,"WM":1.679,"CBRE":-0.548,"CSGP":1.126,"VICI":1.92,"DOC":-0.36,"VTR":0.764,"WELL":0.952,"HST":1.269,"EXR":1.098,"PLD":-0.291,"PSA":0.46,"ARE":2.348,"BXP":-0.293,"AVB":0.471,"CPT":0.058,"EQR":0.528,"ESS":-0.198,"INVH":-0.753,"MAA":-0.639,"UDR":-0.253,"FRT":0.81,"KIM":0.149,"O":0.874,"REG":0,"SPG":0.093,"AMT":-0.556,"CCI":-0.958,"DLR":-3.268,"EQIX":-0.505,"IRM":-5.316,"SBAC":-0.607,"WY":0.819,"CSCO":-1.854,"HPE":-2.73,"MSI":-0.91,"ZBRA":-1.883,"ANET":-7.166,"DELL":-6.219,"HPQ":-2.637,"SMCI":-4.968,"SNDK":-14.664,"STX":-6.563,"WDC":-5.801,"AAPL":0.09,"APH":-7.082,"GLW":-7.971,"JBL":-5.072,"TEL":-5.784,"ACN":0.44,"BR":-0.626,"CDW":-3.29,"CTSH":0.143,"EPAM":-0.701,"FIS":-0.193,"FISV":0.866,"IBM":-0.483,"IT":0.529,"JKHY":0.171,"LDOS":-0.42,"FTV":-0.956,"GRMN":-1.153,"KEYS":-2.489,"TDY":-0.935,"TRMB":-3.696,"AMAT":-4.035,"KLAC":-4.194,"LRCX":-4.854,"Q":-6.91,"TER":-5.197,"ADI":-1.436,"AMD":-4.81,"AVGO":-11.428,"INTC":-4.303,"MCHP":-2.765,"MPWR":-3.563,"MU":-6.701,"NVDA":-3.266,"NXPI":-1.583,"ON":-1.805,"QCOM":-1.644,"SWKS":-1.875,"TXN":-1.239,"ADBE":1.712,"ADP":0.533,"ADSK":-1.092,"CDNS":-3.64,"CRM":-0.046,"DAY":0.145,"DDOG":-2.602,"FICO":1.049,"INTU":-0.752,"NOW":-0.28,"PAYC":0.319,"PAYX":0.715,"PTC":-1.124,"ROP":0.004,"TYL":0.421,"UBER":-0.386,"WDAY":0.201,"AKAM":0.503,"CPAY":-0.066,"CRWD":-2.486,"FFIV":-0.673,"FTNT":-0.303,"GDDY":-0.992,"GEN":-0.396,"GPN":0.159,"MSFT":-1.022,"NTAP":-2.896,"ORCL":-4.466,"PANW":0.699,"PLTR":-2.117,"SNPS":-5.094,"VRSN":-0.848,"XYZ":1.792,"FSLR":-6.609,"AES":-1.214,"SRE":-0.54,"CEG":-7.031,"NRG":-5.391,"VST":-2.577,"AEE":0.021,"AEP":-0.114,"CMS":0.143,"CNP":1.366,"D":1.994,"DTE":-0.727,"DUK":0.796,"ED":1.976,"EIX":0.656,"ES":0.904,"ETR":-1.039,"EVRG":0.586,"EXC":1.114,"FE":0.408,"LNT":0.616,"NEE":0.542,"PCG":2.225,"PEG":-0.089,"PNW":1.222,"PPL":1.584,"SO":-0.342,"WEC":0.387,"XEL":0.629,"ATO":0.766,"NI":-0.672,"AWK":1.122},"additional":{},"subtype":"d1","version":11,"hash":"FDC1CF07F630699761A822D3F495FC141722EB15A4B84D79CDD2A83AF4475D9E"}, "perfDataGeo": null }</script><script src="/assets/dist/9215.v1.4186333b.js" onerror="window.handleScriptNotLoaded(this)"></script><script src="/assets/dist/2332.v1.8cced348.js" onerror="window.handleScriptNotLoaded(this)"></script><script src="/assets/dist/4417.v1.de0121af.js" onerror="window.handleScriptNotLoaded(this)"></script><script src="/assets/dist/463.v1.81aa98cd.js" onerror="window.handleScriptNotLoaded(this)"></script><script src="/assets/dist/3404.v1.fd2315ec.js" onerror="window.handleScriptNotLoaded(this)"></script><script src="/assets/dist/6019.v1.f4bb9181.js" onerror="window.handleScriptNotLoaded(this)"></script><script src="/assets/dist/7402.v1.3a9b98eb.js" onerror="window.handleScriptNotLoaded(this)"></script><script src="/assets/dist/map.v1.a4616cdb.js" onerror="window.handleScriptNotLoaded(this)"></script><div id="rectangle_position" style="position:absolute;right:0;display:none;margin-top:20px;"><div id="IC_D_300x250_1"class="relative overflow-hidden flex items-center justify-center w-full mx-auto" style="width:300px;height:250px;max-height:250px"></div></div></table></div></div>
<div class="flex justify-center my-8" data-fv-notice="promo-trial-banner">
    <div class="pt-[3px] px-[3px] pb-0 rounded-t-[15px] max-w-[1425px] w-full trial-banner-bg">
        <div class="relative flex rounded-t-[12px] font-sm font-sans bg-primary bg-gradient-to-b from-gray-50 to-white dark:from-gray-900 dark:to-gray-800">
            <div class="p-3 w-full text-left">
                <div class="text-center flex flex-col items-center pt-8">
                    <h3 class="font-bold text-3xl m-0">Smarter, Faster Stock Research Starts with Elite</h3>
                    <p class="text-lg font-normal mt-6">
                        Unlock real-time market data, fullscreen multi-layout charts, custom alerts,<br/>
                        advanced screening filters, ETF insights, seamless exports/API,<br />
                        and an ad-free experience—all in one powerful platform.
                    </p>
                    <div class="mt-3">
                            <a href="/register?poster=trial&utm_source=finviz&utm_medium=banner&utm_campaign=trial-banner" onclick="window.gtag && window.gtag('event', 'click', { event_category: 'bannerTrial' });" class="inline-flex items-center justify-center rounded-md border-none font-sans outline-none ring-gray-200 font-medium focus-visible:ring-2 dark:ring-gray-500 bg-violet-500 hover:bg-violet-600 shadow-sm shadow-gray-900 h-auto mt-3 p-4 text-lg leading-snug flex-col tabular-nums !text-white">
                                Start Your Free 7-Day Elite Trial
                            </a>
                        <p class="text-sm dark:text-muted text-muted-2 mt-4">
                            No credit card required.
                        </p>
                    </div>
                </div>
            </div>
            <a title="Close" class="absolute right-2.5 top-2.5 flex h-6 w-6 items-center justify-center trial-banner-close" href="javascript:void(0)" onclick="window.FinvizCloseNotice('promo-trial-banner');">
                <svg width="28" height="28" class="shrink-0">
    <use href="/assets/dist-icons/icons.svg?rev=35#clear"/>
</svg>
            </a>
        </div>
    </div>
</div>

            <div class="footer" style="margin-top: 20px;padding-bottom: 115px">
                <div class="footer_links">
                    <a class="tab-link" href="/affiliate.ashx">Affiliate</a>
                    <span class="footer_dot"> • </span>
                    <a class="tab-link" href="/advertise.ashx">Advertise</a>
                    <span class="footer_dot"> • </span>
                    <a class="tab-link" href="/careers">Careers</a>
                    <span class="footer_dot"> • </span>
                    <a class="tab-link" href="/contact.ashx">Contact</a>
                    <span class="footer_dot"> • </span>
                    <a class="tab-link" href="/blog">Blog</a>
                    <span class="footer_dot"> • </span>
                    <a class="tab-link" href="/help/screener.ashx">Help</a>
                    <span class="footer_dot"> • </span>
                    <a class="tab-link" href="/privacy.ashx">Privacy</a>
                    <span class="footer_dot"> • </span>
                    <a class="tab-link" href="https://x.com/finviz_com" target="_blank">Follow us on X</a><span class="footer_dot"> • </span> <a id="ic_us_privacy" class="tab-link relative overflow-hidden [&>a]:absolute [&>a]:inset-0 [&>a]:-indent-[9999em]" href="#">Do Not Sell My Personal Information</a>    </div>
    Quotes delayed 15 minutes for NASDAQ, NYSE and AMEX.
    <br>
    Copyright © 2007-2025 Finviz.com. All Rights Reserved.
    <div class="mt-4">
    <div id="IC_M_3x6_1"class="relative overflow-hidden flex items-center justify-center w-full mx-auto"></div>
</div>
</div><script>SearchFocus();</script>
            <script>(function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':
            new Date().getTime(),event:'gtm.js'});var f=d.getElementsByTagName(s)[0],
            j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src=
            'https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);
            })(window,document,'script','dataLayer','GTM-537M973G');</script>
            <script>
              function getSystemTheme() {
                if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
                  return 'Dark';
                }
                else if (window.matchMedia && window.matchMedia('(prefers-color-scheme: light)').matches) {
                  return 'Light';
                }
                return 'No Preference';
              }

              var systemTheme = getSystemTheme()

              const headlessChrome = navigator.userAgent.includes('HeadlessChrome')
              const webdriver = navigator.webdriver

              let cdp = false
              try {
                let accessed = false
                const e = new window.Error('ignore')
                window.Object.defineProperty(e, 'stack', {
                  configurable: false,
                  enumerable: false,
                  get: function () {
                    accessed = true
                    return ''
                  },
                })
                // This is part of the detection and shouldn't be deleted
                window.console.debug(e)
                cdp = accessed
              } catch {}

              gtag('js', new Date());

              var fGaM = {
                'dimension1': 'NotLoggedIn',
                'dimension3': window.devicePixelRatio,
                'layoutTheme': 'dark',
                'systemTheme': systemTheme,
                'bundle': 'modern',
                'prefTheme': 'dark',
                'themeFlag': 'modern',
                innerWidth: window.innerWidth,
                innerHeight: window.innerHeight,
                webdriver: webdriver,
                cdp: cdp,
                isBot: headlessChrome || webdriver || cdp,
                icAdsVariant: 'control',
              };

              gtag('config', 'G-ZT9VQEWD4N', fGaM);
              
            </script>
            <script type="text/javascript">
        window._qevents = window._qevents || [];

        (function() {
            var elem = document.createElement('script');
            elem.src = (document.location.protocol == "https:" ? "https://secure" : "http://edge") + ".quantserve.com/quant.js";
            elem.async = true;
            elem.type = "text/javascript";
            var scpt = document.getElementsByTagName('script')[0];
            scpt.parentNode.insertBefore(elem, scpt);
        })();

        window._qevents.push({
            qacct:"p-c2W8esUZ6Q8oA"
        });
    </script>
    <noscript>
        <div style="display:none;">
            <img src="//pixel.quantserve.com/pixel/p-c2W8esUZ6Q8oA.gif" border="0" height="1" width="1" alt="Quantcast"/>
        </div>
    </noscript><div id="IC_D_1x1_1"class="relative overflow-hidden flex items-center justify-center w-full mx-auto"></div><div id="rectangle" style="position:absolute;display:none"></div>

                <script>
                    (function() {
                        var element = document.getElementById('major-news');
                        var top = 0;
                        while(element && element.style.position !== 'relative') {
                            top += element.offsetTop;
                            element = element.offsetParent;
                        }
                        var rectangle = document.getElementById('rectangle_position');
                        rectangle.style.top = top + 'px';
                        rectangle.style.display = 'block';
                    })();
                </script>
            <div id="modal-elite-ad" class="modal-elite-ad">
                            <div id="modal-elite-ad_content" class="modal-elite-ad_content">
			                    <button id="modal-elite-ad-close" type="button" class="modal-elite-ad_close">×</button>

                                <!--<div id="modal-elite-ad-content-0" style="display: none">
			                        <h2>Ever heard of Finviz*Elite?</h2>
                                    <p>
                                        Our premium service offers you real-time quotes, advanced visualizations, technical studies, and much more.<br>
                                        Become Elite and make informed financial decisions.
                                    </p>
                                    <a href="/elite?utm_source=finviz&utm_medium=banner&utm_campaign=modal-0" id="modal-elite-ad-btn-0" class="" target="_blank">Find out more</a>
                                </div>-->

                                <div id="modal-elite-ad-content-1" style="display: block">
			                        <h2>Upgrade your FINVIZ experience</h2>
                                    <p>
                                        Join thousands of traders who make more informed decisions with&nbsp;our&nbsp;premium features.
                                        Real-time quotes, advanced&nbsp;visualizations, backtesting, and much more.
                                    </p>
                                    <a href="/elite?utm_source=finviz&utm_medium=banner&utm_campaign=modal-1" id="modal-elite-ad-btn-1" class="modal-elite_button" target="_blank">Learn more about FINVIZ*Elite</a>
                                </div>
                            </div>
                         </div><script src="/assets/dist/script/pv.v1.27fa030f.js" async></script><script defer>window.renderScriptNotLoaded();</script>
<script defer src="https://static.cloudflareinsights.com/beacon.min.js/vcd15cbe7772f49c399c6a5babf22c1241717689176015" integrity="sha512-ZpsOmlRQV6y907TI0dKBHq9Md29nnaEIPlkf84rnaERnq6zvWvPUqr2ft8M1aS28oN72PdrCzSjY4U6VaAw1EQ==" data-cf-beacon='{"version":"2024.11.0","token":"e53f08f6c9e04bfd9760701085ec93b4","server_timing":{"name":{"cfCacheStatus":true,"cfEdge":true,"cfExtPri":true,"cfL4":true,"cfOrigin":true,"cfSpeedBrain":true},"location_startswith":null}}' crossorigin="anonymous"></script>
</body>
</html>


# Page source of https://finviz.com/quote.ashx?t=AAPL&p=d


<!DOCTYPE html>
<html lang="en" class=" dark">
<head>
<title>AAPL - Apple Inc Stock Price and Quote</title>
<meta charset="UTF-8"><meta name="viewport" content="width=1024"><meta name="description" content="AAPL - Apple Inc - Stock screener for investors and traders, financial visualizations.">

            <link rel="preload" href="/fonts/lato-v17-latin-ext_latin-regular.woff2" as="font" crossorigin>
            <link rel="preload" href="/fonts/lato-v17-latin-ext_latin-700.woff2" as="font" crossorigin>
            <link rel="preload" href="/fonts/lato-v17-latin-ext_latin-900.woff2" as="font" crossorigin>
            <link rel="preload" href="/fonts/finviz-sans-415-normal-latin.woff2" as="font" crossorigin>
            <link rel="preload" href="/fonts/finviz-sans-450-normal-latin.woff2" as="font" crossorigin>
            <link rel="preload" href="/fonts/finviz-sans-500-normal-latin.woff2" as="font" crossorigin>
            <link rel="preload" href="/fonts/finviz-sans-700-normal-latin.woff2" as="font" crossorigin>
        
            <script>
                window.notificationsArray = [];
                window.renderScriptNotLoaded = function () {};
                window.handleScriptNotLoaded = function (element) {
                    window.notificationsArray.push(element);
                    window.sentryDisabled = true;
                    window.handleScriptNotLoaded = function () {};
                };
            </script>
        <link rel="stylesheet" href="/assets/dist/redesign.96c95996.css" type="text/css" onerror="window.handleScriptNotLoaded(this)">
<link rel="stylesheet" href="/assets/dist/main.c6147a33.css" type="text/css" onerror="window.handleScriptNotLoaded(this)">
<link rel="icon" type="image/png" href="/favicon_2x.png" sizes="32x32">
<link rel="icon" type="image/png" href="/favicon.png" sizes="16x16">
<link rel="canonical" href="/quote.ashx?t=AAPL">
<script async=true>
    !(function(q,_name){q[_name]=q[_name]||function k(){(k.q=k.q||[]).push(arguments)},q[_name].v=q[_name].v||2,q[_name].s="1";!(function(q,k,F,H){function m(F,H){try{m=q.localStorage,(F=JSON.parse(m[decodeURI(decodeURI('%67%25%365%25%37%34I%257%34e%6d'))]("_aQS01OUU2MkU1RURCQzRDMzUyMTIwQkM4ODYtMTE0")).lgk||[])&&(H=q[k].pubads())&&F.forEach((function(q){q&&q[0]&&H.setTargeting(q[0],q[1]||"")}))}catch(N){}var m}try{(H=q[k]=q[k]||{}).cmd=H.cmd||[],typeof H.pubads===F?m():typeof H.cmd.unshift===F?H.cmd.unshift(m):H.cmd.push(m)}catch(N){}})(window,decodeURI(decodeURI('%25%367o%25%36fg%256c%25%36%35%2574%256%31%25%36%37')),"function");;!(function(q){q.__admiral_getConsentForGTM=function(k){function F(q,F){k((function(q,k){const F=q&&q.purpose&&q.purpose.consents||{};return{adConsentGranted:k||!!F[1],adUserData:k||!!F[7],adPersonalization:k||!!F[3],analyticsConsentGranted:k||!!F[1],personalizationConsentGranted:k||!!F[5],functionalityConsentGranted:k||!1,securityConsentGranted:k||!0}})(q,!F))}q[_name]("after","cmp.loaded",(function(k){k&&k.tcData&&k.tcData.gdprApplies?(k.consentKnown&&F(k.tcData,!0),q[_name]("after","cmp.updated",(function(q){F(q.tcData,!0)}))):F({},!1)}))}})(window);})(window,decodeURI(decodeURI('a%256%34m%25%369%25%37%32%256%31l')));!(function(q,k,F,H){F=q.createElement(k),q=q.getElementsByTagName(k)[0],F.async=1,F.src="https://urbanlaurel.com/assets/js/q2o3um29vhadcznq.vendor.js",(H=0)&&H(F),q.parentNode.insertBefore(F,q)})(document,"script");;;!(function(q,k,F,H,m){function N(){for(var q=[],F=0;F<arguments.length;F++)q.push(arguments[F]);if(!q.length)return m;"ping"===q[0]?q[2]({gdprAppliesGlobally:!!k[decodeURI(decodeURI('_%25%35%66c%6d%25%37%30%254%37%25%364%25%370%257%32A%2570%25%370%256%63%2569%65%73%2547%256%63o%25%36%32%25%361%25%36%63%6c%79'))],cmpLoaded:!1,cmpStatus:"stub"}):q.length>0&&m.push(q)}function L(q){if(q&&q.data&&q.source){var H,m=q.source,N="__tcfapiCall",L="string"==typeof q.data&&q.data.indexOf(N)>=0;(H=L?((function(q){try{return JSON.parse(q)}catch(k){}})(q.data)||{})[N]:(q.data||{})[N])&&k[F](H.command,H.version,(function(q,k){var F={__tcfapiReturn:{returnValue:q,success:k,callId:H.callId}};m&&m.postMessage(L?JSON.stringify(F):F,"*")}),H.parameter)}}!(function t(){if(!k.frames[H]){var F=q.body;if(F){var m=q.createElement("iframe");m.style.display="none",m.name=H,F.appendChild(m)}else setTimeout(t,5)}})(),N.v=1,"function"!=typeof k[F]&&(k[F]=k[F]||N,k.addEventListener?k.addEventListener("message",L,!1):k.attachEvent&&k.attachEvent("onmessage",L))})(document,window,"__tcfapi","__tcfapiLocator",[]);;;!(function(q,k,F,H,m,N,L,t,A,K,R){function Y(){for(var q=[],k=arguments.length,F=0;F<k;F++)q.push(arguments[F]);var H,m=q[1],N=typeof m===L,t=q[2],Y={gppVersion:"1.1",cmpStatus:"stub",cmpDisplayStatus:"hidden",signalStatus:"not ready",supportedAPIs:["7:usnat"].reduce((function(q,k){return k&&q.push(k),q}),[]),cmpId:9,sectionList:[],applicableSections:[0],gppString:"",parsedSections:{}};function v(q){N&&m(q,!0)}switch(q[0]){case"ping":return v(Y);case"queue":return A;case"events":return K;case"addEventListener":return N&&(H=++R,K.push({id:H,callback:m,parameter:t})),v({eventName:"listenerRegistered",listenerId:H,data:!0,pingData:Y});case"removeEventListener":for(H=!1,F=0;F<K.length;F++)if(K[F].id===t){K.splice(F,1),H=!0;break}return v(H);case"hasSection":case"getSection":case"getField":return v(null);default:return void A.push(q)}}Y.v=2,typeof k[F]!==L&&(k[F]=k[F]||Y,k[t]&&k[t]("message",(function(q,H){var L="string"==typeof q.data;(H=L?((function(q){try{return JSON.parse(q)}catch(k){}})(q.data)||{})[m]:(q.data||{})[m])&&k[F](H.command,(function(k,F){var m={__gppReturn:{returnValue:k,success:F,callId:H.callId}};q.source&&q.source.postMessage(L?JSON.stringify(m):m,"*")}),N in H?H[N]:null,H.version||1)}),!1),(function v(){if(!k.frames[H]){var F=q.body;if(F){var m=q.createElement("iframe");m.style.display="none",m.name=H,F.appendChild(m)}else setTimeout(v,5)}})())})(document,window,"__gpp","__gppLocator","__gppCall","parameter","function","addEventListener",[],[],0);
    ;(function () {
        window.ic_privacySelectorLoaded = false;

        window.admiral("after", "candidate.dismissed", function () {
            if (window.checkBannersLoaded) checkBannersLoaded();
        });

        window.admiral("after", "cmp.loaded", function (eventArg) {
            console.log("Admiral CMP Loaded ", eventArg);
            if (eventArg.euVisitor) return;
            try {
                __gpp("addEventListener", function (tcData) {
                    window.ic_privacySelectorLoaded = true;
                });
            } catch (e) {
                console.error(e)
            }
        });
    })();
</script><script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){dataLayer.push(arguments);}
</script><script>
            FinvizSettings = {
                versionImages: 35,
                hasUserPremium: false,
                name: "",
                email: "",
                nodeChartsDomain: "https://charts2-node.finviz.com",
                hasUserStickyHeader: false,
                adsProvider: 1,
                hasRedesignEnabled: true,
                hasRedesignPortfolio: false,
                hasDarkTheme: true,
                quoteSearchExt: '',
                isJoinBannerVisible: false,
                hasKnowledgeBase: false,
                hasNewComparePerf: false,
                hasCustomColumns: false,
                hasBFPromo: false,
                featureFlags: {"redesign":true,"stockswhymoving":true}
            };
        </script><script src="/assets/dist/script/browser_check.v1.7d9dede5.js"></script><script src="/assets/dist/script/notice.v1.ae659f43.js" onerror="window.handleScriptNotLoaded(this)"></script><script src="/assets/dist/script/vendor/boxover.v1.202b25a7.js" defer></script>
<script src="/assets/dist/runtime.v1.448bed6c.js" onerror="window.handleScriptNotLoaded(this)"></script><script src="/assets/dist/libs_init.v1.d9a4b671.js" onerror="window.handleScriptNotLoaded(this)"></script><script src="/assets/dist/7470.v1.3421c138.js" onerror="window.handleScriptNotLoaded(this)"></script><script src="/assets/dist/3772.v1.b198d5a5.js" onerror="window.handleScriptNotLoaded(this)"></script><script src="/assets/dist/877.v1.3af58ae5.js" onerror="window.handleScriptNotLoaded(this)"></script><script src="/assets/dist/8949.v1.494e6780.js" onerror="window.handleScriptNotLoaded(this)"></script><script src="/assets/dist/7052.v1.828e2e50.js" onerror="window.handleScriptNotLoaded(this)"></script><script src="/assets/dist/2698.v1.5f6434e5.js" onerror="window.handleScriptNotLoaded(this)"></script><script src="/assets/dist/header.v1.7e8eaf94.js" onerror="window.handleScriptNotLoaded(this)"></script><link rel="preload" as="script" href="/assets/dist/2332.v1.8cced348.js" data-chunk-id="quote-portal-components"><link rel="preload" as="script" href="/assets/dist/7833.v1.bf11d17f.js" data-chunk-id="quote-portal-components"><link rel="preload" as="script" href="/assets/dist/6769.v1.7571a412.js" data-chunk-id="quote-portal-components"><link rel="preload" as="script" href="/assets/dist/6195.v1.c33098bf.js" data-chunk-id="quote-portal-components"><link rel="preload" as="script" href="/assets/dist/9240.v1.0c126643.js" data-chunk-id="quote-portal-components"><link rel="preload" as="script" href="/assets/dist/3160.v1.63d87267.js" data-chunk-id="quote-portal-components"><link rel="preload" as="script" href="/assets/dist/4927.v1.fc34b9ec.js" data-chunk-id="quote-portal-components"><link rel="preload" as="script" href="/assets/dist/5064.v1.67aaf856.js" data-chunk-id="quote-portal-components"><link rel="preload" as="script" href="/assets/dist/quote-portal-components.v1.609bb017.js" data-chunk-id="quote-portal-components"><link rel="stylesheet" href="/assets/dist/charts_layout.70be5beb.css" onerror="window.handleScriptNotLoaded(this)"></head>

          <script>
            const channelIdToLabel = {
                '1': 'MarketWatch',
                '2': 'WSJ',
                '3': 'Reuters',
                '4': 'Yahoo Finance',
                '5': 'CNN',
                '6': 'The New York Times',
                '7': 'Bloomberg',
                '9': 'BBC',
                '10': 'CNBC',
                '11': 'Fox Business',
                '102': 'Mish\'s Global Economic Trend Analysis',
                '105': 'Trader Feed',
                '113': 'Howard Lindzon',
                '114': 'Seeking Alpha',
                '123': 'Fallond Stock Picks',
                '132': 'Zero Hedge',
                '133': 'market folly',
                '136': 'Daily Reckoning',
                '141': 'Abnormal Returns',
                '142': 'Calculated Risk',
            }
            function trackAndOpenNews(event, channel, url) {
              event.preventDefault()
              window.open(url, '_blank')

              let channelLabel
              if (typeof channel === 'string') {
                const isInternalNewsUrl = url.startsWith('/news/')
                channelLabel = isInternalNewsUrl ? 'internal-' + channel : channel
              } else {
                const label = channelIdToLabel[channel]
                channelLabel = label !== undefined ? label : channel
              }
              window.gtag && window.gtag('event', 'click', {
                send_to: 'G-ZT9VQEWD4N',
                non_interaction: true,
                event_category: 'news',
                event_label: channelLabel,
                value: 1 });
            }
          </script>
          <body class="m-0 yellow-tooltip is-quote min-w-[1009px] chart-tooltip table w-full">
            <script>
                window.adLayoutVersion = 'control';
                window.adLoggedIn = 'NotLoggedIn';

                var cookieName = 'fv_block';
                var selector = '[data-google-query-id]';
                var selectorFrame = selector + ' iframe, ' + selector + ' [id*=aax]';
                var cookieExpiry = 5 * 60 * 1000; // 5min
                var checkTimeout = 20 * 1000; // 20sec

                function getCookie(value) {
                    var expiration = +new Date() + cookieExpiry;
                    return cookieName + '=' + value + '; expires=' + (new Date(expiration)).toUTCString() + '; path=/';
                }

                var finvizBannersLoaded = false;
                function loadFinvizBanners(setCookie) {
                    
                    if (setCookie) document.cookie = getCookie('block');
                    finvizBannersLoaded = true;
                    var s = document.createElement('script');
                    s.type = 'text/javascript';
                    s.async = true;
                    s.src = '/assets/dist/script/finviz_b.v1.d6c84ef3.js';
                    document.head.appendChild(s);
                }

                function checkBannersLoaded() {
                    var checkEnd = +new Date() + checkTimeout;
                    function asyncCheckIfExists(selector, resolve) {
                        var now = +new Date();
                        var container = document.querySelector(selector);
                        if (!container && checkEnd > now) return setTimeout(function () { asyncCheckIfExists(selector, resolve) }, 1000)
                        resolve(!!container);
                    }

                    asyncCheckIfExists(selector, function (exists) {
                        if (!exists) return loadFinvizBanners(true);

                        asyncCheckIfExists(selectorFrame, function (hasIframe) {
                            if (!hasIframe) return loadFinvizBanners(true);
                        })
                    })
                }

                if (document.cookie.indexOf(cookieName) >= 0) {
                    loadFinvizBanners(false);
                } else {
                    var s = document.createElement('script');
                    s.type = 'text/javascript';
                    s.async = true;
                    s.onerror = loadFinvizBanners;
                    s.src = 'https://u5.investingchannel.com/static/uat.js';
                    document.head.appendChild(s);

                    InvestingChannelQueue = window.InvestingChannelQueue || [];
                    var ic_page;

                    function refreshAd(container, refreshes) {
                        var placementTag, adslot;
                        window.InvestingChannelQueue.push(function () {
                            var pubTags = ic_page.getPubTag.call(ic_page, container.id);
                            if (!pubTags) return;
                            var pubTag = pubTags[0];
                            placementTag = pubTag.mPlacements[0].mTagToRender;
                            adslot = pubTag.mPlacements[0].mPublisherKval.adslot[0];
                            // Update div ID
                            var id = container.id.split('_');
                            var numberOfDivs = document.querySelectorAll('[id*=' + id.slice(0, id.length - 1).join('_') + ']').length;
                            var newDivNumber = Number(id.pop()) + numberOfDivs * refreshes;
                            container.setAttribute('id', id.join('_') + '_' + newDivNumber);
                            // Destroy previous pubtag & reset container html (loading span)
                            pubTag.destroy();
                            container.innerHTML = '';
                        });
                        window.InvestingChannelQueue.push(function () {
                            if (!placementTag || !adslot) return
                            // Create new pub tag
                            var newTag;
                            var layoutId = placementTag.mNativeLayout ? placementTag.mNativeLayout.nativelayoutid : null;
                            if (layoutId) {
                                newTag = ic_page.defineNativeTag('finviz/' + placementTag.mTarget.dfpkeyname, placementTag.mAdSize, container.id, layoutId);
                                var nativeLayout, layoutData

                                try {
                                  nativeLayout = newTag.mPlacements[0].mTags[0].mNativeLayout;
                                } catch (e) {
                                    console.log(e.message)
                                }

                                try {
                                  layoutData = newTag.mTemplate.mNativeLayout[layoutId].Data
                                  if (layoutData && nativeLayout && !nativeLayout.layout) {
                                    newTag.mPlacements[0].mTags[0].mNativeLayout = layoutData
                                  }
                                } catch (e) {
                                    console.log(e.message)
                                }
                            } else {
                                newTag = ic_page.defineTag('finviz/' + placementTag.mTarget.dfpkeyname, placementTag.mAdSize, container.id);
                            }
                            // Set adslot param
                            newTag.setKval({ adslot: adslot });
                            newTag.setKval({ kw: 'ajax' });
                            newTag.render();
                        });
                    }

                    var refreshCount = 1;
                    function refreshAds(selectors) {
                        if (window.ic_page) {
                            document.querySelectorAll(selectors).forEach(function (element) {
                                try {
                                    refreshAd(element, refreshCount);
                                } catch (e) {
                                    console.log('Ad refresh error for:', element, e);
                                }
                            });
                            window.ic_page.loadMore();
                            refreshCount++;
                        }
                    }


                    InvestingChannelQueue.push(function() {
                        var icConfig = window['FINVIZ_IC_UAT_CONFIG'] = {};
                        
                        ic_page = InvestingChannel.UAT.Run('df0d0d52-cc7f-11e8-82a5-0abbb61c4a6a', icConfig);
                    });

                    var hash = null;
                    if (typeof hash === 'string') {
                      InvestingChannelQueue.push(function() {
                          if (ic_page) {
                              ic_page.setUser({'SHA256': hash}, 'hash', '');
                          }
                      });
                    }
                }
            </script>
            <script>
                (function () {
                    var detectionEl = document.createElement('div');
                    detectionEl.style.position='absolute';
                    detectionEl.style.overflow='scroll';
                    document.body.appendChild(detectionEl);
                    document.documentElement.style.setProperty('--fv-scrollbar-width', `${detectionEl.offsetWidth}px`);
                    document.body.removeChild(detectionEl);
                })()
            </script>
        <div id="notifications-container"></div><table class="header">
    <tr class="align-top">
        <td>
            <table class="header-container">
                <tr>
                    <td class="w-[30%]">
                        <table class="w-full">
                            <tr>
                                <td class="h-[50px] align-middle">
                                    <a href="/" class="logo"><svg width="225" height="32" class="block">
  <use href="/img/logo.svg#free" class="dark:hidden" />
  <use href="/img/logo.svg#free-dark" class="hidden dark:block" />
</svg></a>
                                </td>
                            </tr>
                            <tr>
                                <td id="search" style="padding-top: 7px">
                                    <div class="navbar-search-placeholder">
    <span class="icon-wrapper">
        <svg xmlns="http://www.w3.org/2000/svg" class="icon" fill="none" viewBox="0 0 24 24">
            <path d="M16.9 15.5l4 4c.2.2.1.5 0 .7l-.7.7a.5.5 0 01-.8 0l-4-4c0-.2-.2-.3-.3-.4l-.7-1a7 7 0 01-11.2-4 7 7 0 1112.2 3l1 .6.5.4zM5 10a5 5 0 1010 0 5 5 0 00-10 0z" />
        </svg>
    </span>
    <input placeholder="Search ticker, company or profile" class="search-input is-free"/>
</div>
                                </td>
                            </tr>
                        </table>
                    </td>
                    <td class="align-bottom pb-1">
                        <div id="microbar_position" class="hidden xl:flex items-center h-[37px] pl-2"><div>
                        <div id="IC_D_88x31_1"class="relative overflow-hidden flex items-center justify-center w-full mx-auto" style="width:88px;height:31px;max-height:31px"></div>
                        </div></div>
                    </td>
                    <td class="relative w-[730px] text-right">
                        <div id="banner_position" class="overflow-hidden absolute top-0 right-0 w-full h-[96px]">
                        <div id="IC_D_728x90_1"class="relative overflow-hidden flex items-center justify-center w-full mx-auto" style="width:728px;height:90px;max-height:90px"></div>
                        </div>
                    </td>
                </tr>
            </table>
        </td>
    </tr>
    <tr>
        <td class="w-[994px] leading-none" style="font-size:0">
            <img src="/gfx/nic2x2.gif" class="w-[994px] h-px" alt="">
        </td>
    </tr>
</table>
            <table class="navbar">
                <tr>
                    <td class="h-[30px]">
                        <table class="header-container">
                            <tr><td><a class="nav-link is-first" href="/">Home</a></td><td><a class="nav-link" href="/news.ashx">News</a></td><td><a class="nav-link" href="/screener.ashx">Screener</a></td><td><a class="nav-link" href="/map.ashx">Maps</a></td><td><a class="nav-link" href="/groups.ashx">Groups</a></td><td><a class="nav-link" href="/portfolio.ashx">Portfolio</a></td><td><a class="nav-link" href="/insidertrading">Insider</a></td><td><a class="nav-link" href="/futures.ashx">Futures</a></td><td><a class="nav-link" href="/forex.ashx">Forex</a></td><td><a class="nav-link" href="/crypto.ashx">Crypto</a></td><td><a class="nav-link" href="/calendar/economic">Calendar</a></td><td class="hidden [@media(min-width:1150px)]:table-cell"><a class="nav-link" href="/elite?utm_source=finviz&utm_medium=banner&utm_campaign=main-navbar-backtests">Backtests</a></td><td><a class="nav-link is-elite" href="/elite">Pricing</a></td><td class="w-full relative"><div class="absolute bottom-0 left-0 right-0 top-0"><div id="time" class="pr-1"></div></div></td>
                    <td class="nav relative">
        <a data-testid="chart-layout-theme" href="#" class="!flex !bg-transparent !border-b-0 mt-1 !py-0 !px-1" style='border-left: 1px solid #444a57' title="Toggle Light/Dark mode" onclick="setChartThemeCookie('light', true)">
            <div class='relative box-content flex rounded-full w-10 h-5 border border-gray-750 bg-gray-800 text-white justify-end'>
                <div class='box-border w-1/2 rounded-full p-px border border-gray-800 bg-[#4c5261] flex justify-center items-center'>
                    <svg width="16" height="16" class="fill-current text-white inline-block -ml-px">
    <use href="/assets/dist-icons/icons.svg?rev=35#moonOutlined"/>
</svg>
                </div>
            </div>
            <span class='ml-1 select-none font-medium text-xs text-white'>Theme</span>
        </a>
    </td>
    
                <td>
                    <a href="/help/screener.ashx" class="nav-link is-help border-l border-[#444a57]"><span class="fa fa-question-circle"></span>Help</a>
                </td>
                <td><a href="/login" class="nav-link sign-in">Login</a></td>
                <td><a href="/register" class="nav-link sign-up">Register</a></td>
            
                            </tr>
                        </table>
                    </td>
                </tr>
            </table>
        
          <script>
            function reloadPage () { location.reload() }
            function setChartThemeCookie(chartsTheme) {
              fetch('/api/set_cookie.ashx?cookie=chartsTheme&value=' + chartsTheme ).catch(function(){}).then(function(){
                window.gtag && window.gtag('event', 'click', { event_category: 'theme', event_label: 'toggle', value: chartsTheme, event_callback: reloadPage });
                setTimeout(reloadPage,1000);
              })
            }
          </script><div class="content "><div class="ticker-wrapper gradient-fade" data-ticker="AAPL">
<div class="js-ticker-header-container bg-secondary sticky sticky-0 z-sticky bg-opacity-80 backdrop-blur-md"><div class="fv-container py-2.5 has-responsive-padding">    <div class="quote-header-wrapper">
        <div class="quote-header">
            <div class="quote-header_left">
                
                <div class="quote-header_ticker-wrapper">
                    <h1 class="js-recent-quote-ticker quote-header_ticker-wrapper_ticker" data-ticker="AAPL">AAPL</h1>
                    <h2 class="quote-header_ticker-wrapper_company text-xl">
                        <a class="tab-link block truncate" href="http://www.apple.com" target="_blank" rel="nofollow">
                        Apple Inc
                        </a>
                    </h2>
                </div>
            </div>
                <div class="quote-header_right js-quote-price-static">
            <div class="quote-price">
        <div class="sr-only">Last Close</div>
          <span class="quote-price_date flex items-center">
      Dec 12
      <span class="text-muted-3">&nbsp;•&nbsp;</span> 04:00PM ET
  </span>
        <div class="quote-price_wrapper">
            <strong class="quote-price_wrapper_price">278.28</strong>
                <div class="quote-price_wrapper_change">
        <div class="table w-full">
            <span class="table-row w-full items-baseline justify-end whitespace-nowrap text-muted-2 text-positive">
                <span><div class="sr-only">Dollar change</div>+0.25</span>
                <span class="table-cell align-middle w-0 text-center pl-px">
                    <svg width="12" height="12" class="fill-current">
    <use href="/assets/dist-icons/icons.svg?rev=35#arrowUpShort"/>
</svg>
                </span>
            </span>
            <span class="table-row w-full items-baseline justify-end whitespace-nowrap text-muted-2 text-positive">
                <span><div class="sr-only">Percentage change</div>0.09</span>
                <span class="table-cell align-middle w-0 text-center pl-px">
                    <span class="font-normal">%</span>
                </span>
            </span>
        </div>
    </div>
        </div>
    </div>
        
    </div>
            <div class="js-quote-price-root quote-header_right hidden"></div>
        </div>
        <div class="quote-links whitespace-nowrap gap-8">
            <div class="flex space-x-0.5 overflow-hidden">
                <a href="screener.ashx?v=111&f=sec_technology" class="tab-link">Technology</a>
                <span class="text-muted-3">•</span>
                <a href="screener.ashx?v=111&f=ind_consumerelectronics" class="tab-link truncate" title="Consumer Electronics">Consumer Electronics</a>
                <span class="text-muted-3">•</span>
                <a href="screener.ashx?v=111&f=geo_usa" class="tab-link">USA</a>
                <span class="text-muted-3">•</span>
                <a href="screener.ashx?v=111&f=exch_nasd" class="tab-link">NASD</a>
            </div>
            <div>
                <div class="js-quote-navigation-static flex space-x-0.5 shrink-0">
                    <a href="/quote.ashx?t=AAPL&ta=1&p=d" class="tab-link font-semibold">
                        <span class="xl:hidden">Chart</span>
                        <span class="hidden xl:inline">Stock Detail</span>
                    </a>
                    <span class="text-muted-3">•</span>
                    <a href="/elite?utm_source=finviz&utm_medium=banner&utm_campaign=quote-compare-perf" class="tab-link" data-testid="quote-compare-perf-link-static">
                        Compare
                    </a>
                        <span class="text-muted-3">•</span>
    <a href="quote.ashx?t=AAPL&ta=1&p=d&ty=si" class="tab-link">Short Interest</a>
                    <span class="text-muted-3">•</span>
                    <a href="quote.ashx?t=AAPL&ta=1&p=d&ty=ea" class="tab-link">Financials</a>
                    <span class="text-muted-3">•</span>
                    <a data-testid="options-chain-link-static" href="quote.ashx?t=AAPL&ta=1&p=d&ty=oc" class="tab-link">Options</a>
                    <span class="text-muted-3">•</span>
                    <a href="quote.ashx?t=AAPL&ta=1&p=d&ty=lf" class="tab-link">
                        <span class="xl:hidden">Filings</span>
                        <span class="hidden xl:inline">Latest Filings</span>
                    </a>
                    <span class="text-muted-3">•</span>
                    <a href="/save_to_portfolio.ashx?t=AAPL" class="tab-link">Add to Portfolio</a>
                    <span class="text-muted-3">•</span>
                    <a href="/elite?utm_source=finviz&utm_medium=banner&utm_campaign=quote-create-alert" class="tab-link">Set Alert</a>
                </div>
                <div class="js-quote-navigation-root hidden flex space-x-0.5 shrink-0 whitespace-nowrap" data-shortinterest="true" data-isfund="false"></div>
            </div>
        </div>
    </div></div></div><div class="js-why-stock-moving-root hidden mb-2"></div><div id="root"></div>
<script>
            FinvizSettings.TA = {"style":"candlestick","overlays":[{"name":"sma","parameters":"20","color":"rgba(220,  50, 179, 0.39)"},{"name":"sma","parameters":"50","color":"rgba(255, 143,  51, 0.78)"},{"name":"sma","parameters":"200","color":"rgba(220, 179,  50, 0.43)"},{"name":"patterns","parameters":"","color":"rgba(135, 206, 239, 1)|rgba(220, 159, 229, 1)"}],"indicators":[]};
            window.FinvizQuoteTypeCurrent = FinvizSettings.TA.style;
        </script><div class="flex flex-col items-center min-w-[1009px]">
            <div id="app" class="interactive-chart">
                <div id="chart" style="opacity: 0;min-width: 990px; position: relative; min-height: 446px;"></div>
            </div>
            <div id="js-charts-modal"><div class="overlay modal hidden has-footer"></div></div>
            <div class="context-menu hidden"></div>
            <script type="text/javascript">
                    window.globalChartConfig = {
          "layout":"1h1v",
          "height": 400,
          "scrollable": true,
          "colors": undefined,
          "ideas": true,
          "editable": false,
          "editors": ['tools', 'ideas', 'publish', 'timeframe', 'settings'],
          "charts":[{
                "height": 400,
                "timeframe": "d",
                "dateRange": "",
                "scale": "linear",
                "ticker": "AAPL",
                "instrument": "stock",
                "refreshData": true,
                "premarket": 0,
                "aftermarket": 0,
                "hasChartEvents": true,
                "panes": []
              }],
        };
                    
                    window.FinvizQuoteTypeCurrent = FinvizSettings.TA.style;
                </script><script>
                        var data = {"ticker":"AAPL","timeframe":"d","volume":[75604184,55215244,53423104,106181272,71160136,54288328,57388448,60273264,65672688,46240500,49329480,47691716,53704384,42104824,37425512,42451208,49709336,91070272,101670888,73531776,73711232,50901208,43122904,68149376,48116444,49537760,48251836,50558328,44838352,68169416,65934776,50383148,94214912,163224112,78569664,77305768,45057088,48982972,50759496,72044808,52393620,70399984,52845232,41282924,44361276,42309400,34648548,51005924,36326976,52280052,53068016,49947940,75158280,50080540,47471444,54156784,41181752,53103912,97262080,172373296,198134288,97862728,70122752,93728304,79943256,86172448,246421360,80727008,56713868,66213184,49772708,82542720,60402928,58046176,37369800,60412408,59085860,48169824,62627688,64710616,53046528,62631252,43234280,57345884,66034584,49151452,48201836,39960260,61777576,51391200,41601344,36311776,41643840,50036264,62500996,105568560,119548592,69660488,63516416,47161148,42201648,38028092,44155332,41960576,46414012,44340240,40687812,30299032,34765480,43695320,38677248,30602208,35934560,38052168,51906296,52990768,50190576,43840196,36615400,48423012,67179968,51591032,44587072,37498224,36766620,59357428,45519340,59894928,66781316,318679872,54146024,43556068,42308716,36636708,34025968,54793392,63285048,32880604,34044160,37345096,39505352,31855692,33591092,28183544,31759188,39882084,64751368,34082240,32993810,46431472,36254472,38846576,52286980,31109504,38802304,36087136,35417248,47070908,64370088,65276740,44944468,28111338,54561120,42137692,38328824,42005600,40398300,48566216,44923940,47923696,44686020,36211776,35169568,42108328,38168252,90152832,45986188,33498440,28481376,48137104,38861016,44383936,40033880,36870620,44649232,36914808,45205816,32777532,33155290,51694752,51356360,56774100,60882264,147495264,40858776,23234704,27262984,42355320,35557544,39480720,55740732,40244112,45045572,40855960,37628940,61710856,49630724,39435296,39831968,71759056,68488304,98070432,64126500,60234760,54697908,94863416,75707568,45486100,55658280,101075128,73063304,45067300,39664988,29925348,39707224,33115644,53718360,45243292,53614056,40896228,48822492,32204216,32316908,53197432,51326396,48013272,44433564,41153640,56833360,47183984,53798064,47227644,45170420,46273564,72071200,76137408,62547468,61368328,60107584,48073424,42432424,54385392,48862948,94127768,44299484,34493584,34532656,37094776,39818616,65299320,36412740,35905904,103419008,125910912,160466288,120859488,184395888,121879984,87435328,101352912,51343872,59732424,52164676,46742536,52976372,52929164,47310988,38222256,38743072,36827632,52286456,57365676,101010624,69018448,51216480,68616944,50478872,36453924,63775816,51909332,49325824,45029472,54737848,46140528,42496636,59211776,46742408,78432920,56288476,45339680,51477936,70819944,35423296,46381568,43603984,55221236,46607692,72862560,54672608,60989856,43904636,51447348,43020692,38856152,45394688,96813544,55814272,54064032,39525728,50799120,73188568,91912816,78788864,67941808,34955836,50228984,42848928,48749368,44443636,39765812,38840112,42296340,47490532,48068140,48974592,51377432,46404072,46989300,46022620,40268780,37858016,51411724,45512512,80698432,104434472,75109296,44155080,108483104,90224832,113853968,61806132,55672300,69878544,51916276,56038656,37476188,39402564,42263864,30621248,42477812,30983132,54575108,31259512,38074700,39418436,44075640,66427836,47549428,54870396,48999496,66313920,83440808,50208576,55824216,42699524,63421100,46508016,44249576,163741312,105517416,60275188,42303712,55202076,46076256,40127688,37704260,48713940,42630240,49155616,44664120,31955776,36496896,38322012,61999096,38142944,35477984,33893612,39776976,49146960,90483032,46695948,45015256,32754940,38253716,44888152,41534760,51086744,69886536,86167120,50194584,49274848,43683072,51204044,48227364,41312412,46208320,48397984,49602792,47431332,45018260,45677280,40424492,45823568,59030832,65585796,46914220,33431424,20135620,46587720,53669532,43538688,43989056,47265844,38211832,32193256,33038318,33247986,38442981],"date":[1710766800,1710853200,1710939600,1711026000,1711112400,1711371600,1711458000,1711544400,1711630800,1711976400,1712062800,1712149200,1712235600,1712322000,1712581200,1712667600,1712754000,1712840400,1712926800,1713186000,1713272400,1713358800,1713445200,1713531600,1713790800,1713877200,1713963600,1714050000,1714136400,1714395600,1714482000,1714568400,1714654800,1714741200,1715000400,1715086800,1715173200,1715259600,1715346000,1715605200,1715691600,1715778000,1715864400,1715950800,1716210000,1716296400,1716382800,1716469200,1716555600,1716901200,1716987600,1717074000,1717160400,1717419600,1717506000,1717592400,1717678800,1717765200,1718024400,1718110800,1718197200,1718283600,1718370000,1718629200,1718715600,1718888400,1718974800,1719234000,1719320400,1719406800,1719493200,1719579600,1719838800,1719925200,1720011600,1720184400,1720443600,1720530000,1720616400,1720702800,1720789200,1721048400,1721134800,1721221200,1721307600,1721394000,1721653200,1721739600,1721826000,1721912400,1721998800,1722258000,1722344400,1722430800,1722517200,1722603600,1722862800,1722949200,1723035600,1723122000,1723208400,1723467600,1723554000,1723640400,1723726800,1723813200,1724072400,1724158800,1724245200,1724331600,1724418000,1724677200,1724763600,1724850000,1724936400,1725022800,1725368400,1725454800,1725541200,1725627600,1725886800,1725973200,1726059600,1726146000,1726232400,1726491600,1726578000,1726664400,1726750800,1726837200,1727096400,1727182800,1727269200,1727355600,1727442000,1727701200,1727787600,1727874000,1727960400,1728046800,1728306000,1728392400,1728478800,1728565200,1728651600,1728910800,1728997200,1729083600,1729170000,1729256400,1729515600,1729602000,1729688400,1729774800,1729861200,1730120400,1730206800,1730293200,1730379600,1730466000,1730728800,1730815200,1730901600,1730988000,1731074400,1731333600,1731420000,1731506400,1731592800,1731679200,1731938400,1732024800,1732111200,1732197600,1732284000,1732543200,1732629600,1732716000,1732888800,1733148000,1733234400,1733320800,1733407200,1733493600,1733752800,1733839200,1733925600,1734012000,1734098400,1734357600,1734444000,1734530400,1734616800,1734703200,1734962400,1735048800,1735221600,1735308000,1735567200,1735653600,1735826400,1735912800,1736172000,1736258400,1736344800,1736517600,1736776800,1736863200,1736949600,1737036000,1737122400,1737468000,1737554400,1737640800,1737727200,1737986400,1738072800,1738159200,1738245600,1738332000,1738591200,1738677600,1738764000,1738850400,1738936800,1739196000,1739282400,1739368800,1739455200,1739541600,1739887200,1739973600,1740060000,1740146400,1740405600,1740492000,1740578400,1740664800,1740751200,1741010400,1741096800,1741183200,1741269600,1741356000,1741611600,1741698000,1741784400,1741870800,1741957200,1742216400,1742302800,1742389200,1742475600,1742562000,1742821200,1742907600,1742994000,1743080400,1743166800,1743426000,1743512400,1743598800,1743685200,1743771600,1744030800,1744117200,1744203600,1744290000,1744376400,1744635600,1744722000,1744808400,1744894800,1745240400,1745326800,1745413200,1745499600,1745586000,1745845200,1745931600,1746018000,1746104400,1746190800,1746450000,1746536400,1746622800,1746709200,1746795600,1747054800,1747141200,1747227600,1747314000,1747400400,1747659600,1747746000,1747832400,1747918800,1748005200,1748350800,1748437200,1748523600,1748610000,1748869200,1748955600,1749042000,1749128400,1749214800,1749474000,1749560400,1749646800,1749733200,1749819600,1750078800,1750165200,1750251600,1750424400,1750683600,1750770000,1750856400,1750942800,1751029200,1751288400,1751374800,1751461200,1751547600,1751893200,1751979600,1752066000,1752152400,1752238800,1752498000,1752584400,1752670800,1752757200,1752843600,1753102800,1753189200,1753275600,1753362000,1753448400,1753707600,1753794000,1753880400,1753966800,1754053200,1754312400,1754398800,1754485200,1754571600,1754658000,1754917200,1755003600,1755090000,1755176400,1755262800,1755522000,1755608400,1755694800,1755781200,1755867600,1756126800,1756213200,1756299600,1756386000,1756472400,1756818000,1756904400,1756990800,1757077200,1757336400,1757422800,1757509200,1757595600,1757682000,1757941200,1758027600,1758114000,1758200400,1758286800,1758546000,1758632400,1758718800,1758805200,1758891600,1759150800,1759237200,1759323600,1759410000,1759496400,1759755600,1759842000,1759928400,1760014800,1760101200,1760360400,1760446800,1760533200,1760619600,1760706000,1760965200,1761051600,1761138000,1761224400,1761310800,1761570000,1761656400,1761742800,1761829200,1761915600,1762178400,1762264800,1762351200,1762437600,1762524000,1762783200,1762869600,1762956000,1763042400,1763128800,1763388000,1763474400,1763560800,1763647200,1763733600,1763992800,1764079200,1764165600,1764338400,1764597600,1764684000,1764770400,1764856800,1764943200,1765202400,1765288800,1765375200,1765461600,1765548000],"open":[175.57,174.34,175.72,177.05,171.76,170.565,170,170.41,171.75,171.19,169.08,168.79,170.29,169.59,169.03,168.7,168.8,168.34,174.26,175.36,171.75,169.61,168.03,166.21,165.515,165.35,166.54,169.525,169.88,173.37,173.33,169.58,172.51,186.645,182.354,183.45,182.85,182.56,184.9,185.435,187.51,187.91,190.47,189.51,189.325,191.09,192.265,190.98,188.82,191.51,189.61,190.76,191.44,192.9,194.635,195.4,195.685,194.65,196.9,193.65,207.37,214.74,213.85,213.37,217.59,213.93,210.39,207.72,209.15,211.5,214.69,215.77,212.09,216.15,220,221.65,227.09,227.93,229.3,231.39,228.92,236.48,235,229.45,230.28,224.82,227.01,224.365,224,218.93,218.7,216.96,219.19,221.44,224.37,219.15,199.09,205.3,206.9,213.11,212.1,216.07,219.01,220.57,224.6,223.92,225.72,225.77,226.52,227.79,225.659,226.76,225.995,227.92,230.1,230.19,228.55,221.66,221.625,223.95,220.82,218.92,221.455,222.5,223.58,216.54,215.75,217.55,224.99,229.97,227.34,228.645,224.93,227.3,228.46,230.04,229.52,225.89,225.14,227.9,224.5,224.3,225.23,227.78,229.3,228.7,233.61,231.6,233.43,236.18,234.45,233.885,234.08,229.98,229.74,233.32,233.1,232.61,229.34,220.965,220.99,221.795,222.61,224.625,227.17,225,224.55,224.01,225.02,226.4,225.25,226.98,228.06,228.88,228.06,231.46,233.33,234.465,234.805,237.27,239.81,242.87,243.99,242.905,241.83,246.89,247.96,246.89,247.815,247.99,250.08,252.16,247.5,248.04,254.77,255.49,258.19,257.83,252.23,252.44,248.93,243.36,244.31,242.98,241.92,240.01,233.53,234.75,234.635,237.35,232.115,224,219.79,224.74,224.78,224.02,230.85,234.12,238.665,247.19,229.99,227.25,228.53,231.285,232.6,229.57,228.2,231.2,236.91,241.25,244.15,244.66,244.94,245.95,244.925,248,244.33,239.41,236.95,241.79,237.705,235.42,234.435,235.105,235.54,223.805,220.14,215.95,211.25,213.31,214.16,214.22,213.99,211.56,221,220.77,223.51,221.39,221.67,217.005,219.805,221.315,205.54,193.89,177.2,186.7,171.95,189.065,186.1,211.44,201.855,198.36,197.2,193.265,196.12,206,204.89,206.365,210,208.693,209.3,209.08,206.09,203.1,198.21,199.17,197.72,199,210.97,210.43,212.43,210.95,212.36,207.91,207.67,205.17,200.71,193.665,198.3,200.59,203.575,199.37,200.28,201.35,202.91,203.5,203,204.39,200.6,203.5,199.08,199.73,197.3,197.2,195.94,198.235,201.625,202.59,201.45,201.43,201.89,202.01,206.665,208.91,212.145,212.68,210.1,209.53,210.505,210.565,209.925,209.22,210.295,210.57,210.87,212.1,213.14,215,213.9,214.7,214.03,214.175,211.895,208.49,210.865,204.505,203.4,205.63,218.875,220.83,227.92,228.005,231.07,234.055,234,231.7,231.275,229.98,226.27,226.17,226.48,226.87,228.61,230.82,232.51,229.25,237.21,238.45,239.995,239.3,237,232.185,226.875,229.22,237,237.175,238.97,239.97,241.225,248.3,255.875,255.22,253.205,254.095,254.56,254.855,255.04,256.575,254.665,257.99,256.805,256.52,257.805,254.94,249.38,246.6,249.485,248.25,248.02,255.885,261.88,262.65,259.94,261.19,264.88,268.985,269.275,271.99,276.99,270.42,268.325,268.61,267.89,269.795,268.96,269.81,275,274.11,271.05,268.815,269.99,265.525,270.83,265.95,270.9,275.27,276.96,277.26,278.01,283,286.2,284.095,280.54,278.13,278.16,277.75,279.095,277.91],"high":[177.71,176.605,178.67,177.49,173.05,171.94,171.42,173.6,172.23,171.25,169.34,170.68,171.92,170.39,169.2,170.08,169.09,175.46,178.36,176.63,173.76,170.65,168.64,166.4,167.26,167.05,169.3,170.61,171.34,176.03,174.99,172.705,173.415,187,184.2,184.9,183.07,184.66,185.09,187.1,188.3,190.65,191.095,190.81,191.92,192.73,192.823,191,190.58,193,192.247,192.18,192.57,194.99,195.32,196.9,196.5,196.94,197.3,207.16,220.2,216.75,215.17,218.95,218.63,214.24,211.89,212.7,211.38,214.86,215.74,216.07,217.51,220.38,221.55,226.45,227.85,229.4,233.08,232.39,232.64,237.23,236.27,231.46,230.44,226.8,227.78,226.94,224.8,220.85,219.49,219.3,220.325,223.82,224.48,225.6,213.5,209.99,213.64,214.2,216.78,219.51,221.89,223.03,225.35,226.827,225.99,227.17,227.98,228.34,228.22,227.28,228.85,229.86,232.92,230.4,229,221.78,225.48,225.24,221.27,221.48,223.09,223.55,224.04,217.22,216.9,222.71,229.82,233.09,229.45,229.35,227.29,228.5,229.52,233,229.65,227.37,226.805,228,225.69,225.98,229.75,229.5,229.41,231.73,237.49,232.12,233.85,236.18,236.85,236.22,235.144,230.82,233.22,234.73,234.325,233.47,229.83,225.35,222.79,223.95,226.065,227.875,228.66,225.7,225.59,226.65,228.87,226.92,229.74,230.16,229.93,230.155,230.72,233.245,235.57,235.69,237.81,240.79,242.76,244.11,244.54,244.63,247.24,248.21,250.8,248.74,249.29,251.38,253.83,254.28,252,255,255.65,258.21,260.1,258.7,253.5,253.28,249.1,244.18,247.33,245.55,243.712,240.16,234.67,236.12,238.96,238.01,232.29,224.42,224.12,227.03,225.63,232.15,240.19,239.855,240.79,247.19,231.83,233.13,232.67,233.8,234,230.585,235.23,236.96,242.34,245.55,245.18,246.01,246.78,248.69,248.86,250,244.98,242.46,242.09,244.027,240.07,236.55,237.86,241.37,236.16,225.84,221.75,216.839,213.95,215.22,215.15,218.76,217.49,218.84,221.48,224.1,225.02,224.99,223.81,225.62,223.68,225.19,207.49,199.88,194.15,190.335,200.61,194.78,199.54,212.94,203.51,200.7,198.833,193.8,201.59,208,208.83,209.75,211.5,212.24,213.58,214.56,206.99,204.1,200.65,199.44,200.05,200.54,211.268,213.4,213.94,212.96,212.57,209.48,208.47,207.04,202.75,197.7,200.74,202.73,203.81,201.96,202.13,203.77,206.24,204.75,205.7,206,204.35,204.5,199.68,200.37,198.685,198.39,197.57,201.7,202.3,203.44,203.67,202.64,203.22,207.39,210.186,213.34,214.65,216.23,211.43,211.33,213.48,212.13,210.91,211.89,212.4,211.8,211.79,215.78,214.95,215.15,215.69,215.24,214.845,214.81,212.39,209.84,213.58,207.88,205.34,215.38,220.85,231,229.56,230.8,235,235.12,234.28,233.12,232.87,230.47,226.52,229.09,229.3,229.49,230.9,233.41,233.38,230.85,238.85,239.9,241.32,240.15,238.781,232.42,230.45,234.51,238.19,241.22,240.1,241.2,246.3,256.64,257.34,255.74,257.17,257.6,255,255.919,258.79,258.18,259.24,259.07,257.4,258.52,258,256.38,249.69,248.845,251.82,249.04,253.38,264.375,265.29,262.85,260.62,264.13,269.12,269.89,271.41,274.14,277.32,270.85,271.486,271.7,273.4,272.29,273.73,275.91,275.73,276.699,275.96,270.49,270.71,272.21,275.43,273.33,277,280.38,279.53,279,283.42,287.4,288.62,284.73,281.14,279.669,280.03,279.75,279.59,279.22],"low":[173.52,173.03,175.09,170.84,170.06,169.45,169.58,170.11,170.51,169.475,168.23,168.58,168.82,168.95,168.24,168.35,167.11,168.16,174.21,172.5,168.27,168,166.55,164.075,164.77,164.92,166.21,168.151,169.18,173.1,170,169.11,170.89,182.66,180.42,181.32,181.45,182.11,182.13,184.62,186.29,187.37,189.66,189.18,189.01,190.92,190.27,186.625,188.04,189.1,189.51,190.63,189.91,192.52,193.034,194.87,194.17,194.14,192.15,193.63,206.9,211.6,211.3,212.72,213,208.85,207.11,206.59,208.61,210.64,212.35,210.3,211.92,215.1,219.03,221.65,223.25,226.372,229.25,225.77,228.68,233.09,232.33,226.64,222.27,223.275,223.09,222.68,217.13,214.62,216.01,215.75,216.12,220.63,217.02,217.71,196,201.07,206.39,208.83,211.97,215.6,219.01,219.7,222.76,223.65,223.04,225.45,225.05,223.9,224.33,223.891,224.89,225.68,228.88,227.48,221.17,217.48,221.52,219.77,216.71,216.73,217.89,219.82,221.91,213.92,214.5,217.54,224.63,227.62,225.81,225.73,224.02,225.41,227.3,229.65,223.74,223.02,223.32,224.13,221.33,223.25,224.83,227.17,227.34,228.6,232.37,229.84,230.52,234.01,234.45,232.6,227.76,228.41,229.57,232.55,232.32,229.55,225.37,220.27,219.71,221.14,221.19,224.57,226.405,221.5,223.355,222.76,225,224.27,225.17,226.66,225.89,225.71,228.06,229.74,233.33,233.81,233.97,237.16,238.9,241.25,242.13,242.08,241.75,245.34,246.26,245.68,246.24,247.65,249.78,247.74,247.095,245.69,253.45,255.29,257.63,253.06,250.75,249.43,241.82,241.89,243.2,241.35,240.05,233,229.72,232.472,234.43,228.03,228.48,219.38,219.79,222.3,221.41,223.98,230.81,234.01,237.21,233.44,225.7,226.65,228.27,230.425,227.26,227.2,228.13,230.68,235.57,240.99,241.84,243.16,244.29,245.22,244.42,244.91,239.13,237.06,230.2,236.112,234.68,229.23,233.158,234.76,224.22,217.45,214.91,208.42,209.58,209.97,211.49,213.75,212.22,211.28,218.58,220.08,220.47,220.56,217.68,216.23,218.9,221.02,201.25,187.34,174.62,169.21,171.89,183,186.06,201.162,199.8,192.37,194.42,189.811,195.97,202.799,202.94,206.2,207.46,208.37,206.671,208.9,202.16,198.21,197.02,193.25,194.68,197.535,206.75,209,210.58,209.54,209.77,204.26,205.03,200.71,199.7,193.46,197.43,199.9,198.51,196.78,200.12,200.955,202.1,200.15,202.05,200.02,200.57,198.41,197.36,195.7,196.564,195.21,195.07,196.855,198.96,200.2,200.62,199.46,200,199.261,206.14,208.14,211.81,208.8,208.45,207.22,210.03,209.86,207.54,208.92,208.64,209.59,209.704,211.63,212.23,212.41,213.53,213.4,213.06,210.82,207.72,207.16,201.5,201.675,202.16,205.59,216.58,219.25,224.76,227.07,230.43,230.85,229.335,230.11,229.35,225.77,223.78,225.41,226.23,224.69,228.26,229.335,231.37,226.97,234.36,236.74,238.49,236.34,233.36,225.95,226.65,229.02,235.03,236.324,237.73,236.65,240.211,248.12,253.58,251.04,251.712,253.78,253.01,253.11,254.93,254.15,253.95,255.05,255.43,256.11,253.14,244,245.56,244.7,247.47,245.13,247.27,255.63,261.83,255.43,258.01,259.18,264.65,268.15,267.11,268.48,269.16,266.25,267.615,266.93,267.89,266.77,267.455,269.8,271.7,272.09,269.6,265.73,265.32,265.5,265.92,265.67,270.9,275.25,276.63,275.987,276.14,282.63,283.3,278.59,278.05,276.15,276.92,276.44,273.81,276.82],"close":[173.72,176.08,178.67,171.37,172.28,170.85,169.71,173.31,171.48,170.03,168.84,169.65,168.82,169.58,168.45,169.67,167.78,175.04,176.55,172.69,169.38,168,167.04,165,165.84,166.9,169.02,169.89,169.3,173.5,170.33,169.3,173.03,183.38,181.71,182.4,182.74,184.57,183.05,186.28,187.43,189.72,189.84,189.87,191.04,192.35,190.9,186.88,189.98,189.99,190.29,191.29,192.25,194.03,194.35,195.87,194.48,196.89,193.12,207.15,213.07,214.24,212.49,216.67,214.29,209.68,207.49,208.14,209.07,213.25,214.1,210.62,216.75,220.27,221.55,226.34,227.82,228.68,232.98,227.57,230.54,234.4,234.82,228.88,224.18,224.31,223.96,225.01,218.54,217.49,217.96,218.24,218.8,222.08,218.36,219.86,209.27,207.23,209.82,213.31,216.24,217.53,221.27,221.72,224.72,226.05,225.89,226.51,226.4,224.53,226.84,227.18,228.03,226.49,229.79,229,222.77,220.85,222.38,220.82,220.91,220.11,222.66,222.77,222.5,216.32,216.79,220.69,228.87,228.2,226.47,227.37,226.37,227.52,227.79,233,226.21,226.78,225.67,226.8,221.69,225.77,229.54,229.04,227.55,231.3,233.85,231.78,232.15,235,236.48,235.86,230.76,230.57,231.41,233.4,233.67,230.1,225.91,222.91,222.01,223.45,222.72,227.48,226.96,224.23,224.23,225.12,228.22,225,228.02,228.28,229,228.52,229.87,232.87,235.06,234.93,237.33,239.59,242.65,243.01,243.04,242.84,246.75,247.77,246.49,247.96,248.13,251.04,253.48,248.05,249.79,254.49,255.27,258.2,259.02,255.59,252.2,250.42,243.85,243.36,245,242.21,242.7,236.85,234.4,233.28,237.87,228.26,229.98,222.64,223.83,223.66,222.78,229.86,238.26,239.36,237.59,236,228.01,232.8,232.47,233.22,227.63,227.65,232.62,236.87,241.53,244.6,244.47,244.87,245.83,245.55,247.1,247.04,240.36,237.3,241.84,238.03,235.93,235.74,235.33,239.07,227.48,220.84,216.98,209.68,213.49,214,212.69,215.24,214.1,218.27,220.73,223.75,221.53,223.85,217.9,222.13,223.19,223.89,203.19,188.38,181.46,172.42,198.85,190.42,198.15,202.52,202.14,194.27,196.98,193.16,199.74,204.6,208.37,209.28,210.14,211.21,212.5,213.32,205.35,198.89,198.51,196.25,197.49,198.53,210.79,212.93,212.33,211.45,211.26,208.78,206.86,202.09,201.36,195.27,200.21,200.42,199.95,200.85,201.7,203.27,202.82,200.63,203.92,201.45,202.67,198.78,199.2,196.45,198.42,195.64,196.58,201,201.5,200.3,201.56,201,201.08,205.17,207.82,212.44,213.55,209.95,210.01,211.14,212.41,211.16,208.62,209.11,210.16,210.02,211.18,212.48,214.4,214.15,213.76,213.88,214.05,211.27,209.05,207.57,202.38,203.35,202.92,213.25,220.03,229.35,227.18,229.65,233.33,232.78,231.59,230.89,230.56,226.01,224.9,227.76,227.16,229.31,230.49,232.56,232.14,229.72,238.47,239.78,239.69,237.88,234.35,226.79,230.03,234.07,236.7,238.15,238.99,237.88,245.5,256.08,254.43,252.31,256.87,255.46,254.43,254.63,255.45,257.13,258.02,256.69,256.48,258.06,254.04,245.27,247.66,247.77,249.34,247.45,252.29,262.24,262.77,258.45,259.58,262.82,268.81,269,269.7,271.4,270.37,269.05,270.04,270.14,269.77,268.47,269.43,275.25,273.47,272.95,272.41,267.46,267.44,268.56,266.25,271.49,275.92,276.97,277.55,278.85,283.1,286.19,284.15,280.7,278.78,277.89,277.18,278.78,278.03,278.28],"lastOpen":277.9100036621094,"lastHigh":279.2200012207031,"lastLow":276.82000732421875,"lastClose":278.2799987792969,"lastVolume":38442981,"dataId":"38442981|278.28","lastDate":20251212,"lastTime":1765573200,"prevClose":278.0299987792969,"afterClose":null,"afterChange":null,"afterTime":null,"updateOhlcVersion":244,"chartEvents":[{"dateTimestamp":1714681800,"eventType":"chartEvent/earnings","fiscalPeriod":"2024Q2","fiscalEndDate":1711857600,"epsActual":1.53,"epsEstimate":1.5051,"epsReportedActual":1.53,"epsReportedEstimate":1.5051,"salesActual":90753,"salesEstimate":90366.1059},{"dateTimestamp":1722544200,"eventType":"chartEvent/earnings","fiscalPeriod":"2024Q3","fiscalEndDate":1719720000,"epsActual":1.4,"epsEstimate":1.3446,"epsReportedActual":1.4,"epsReportedEstimate":1.3446,"salesActual":85777,"salesEstimate":84432.5395},{"dateTimestamp":1730406600,"eventType":"chartEvent/earnings","fiscalPeriod":"2024Q4","fiscalEndDate":1727668800,"epsActual":0.97,"epsEstimate":1.6004,"epsReportedActual":0.97,"epsReportedEstimate":1.6004,"salesActual":94930,"salesEstimate":94511.9533},{"dateTimestamp":1738272600,"eventType":"chartEvent/earnings","fiscalPeriod":"2025Q1","fiscalEndDate":1735621200,"epsActual":2.4,"epsEstimate":2.3477,"epsReportedActual":2.4,"epsReportedEstimate":2.3477,"salesActual":124300,"salesEstimate":124257.3932},{"dateTimestamp":1746131400,"eventType":"chartEvent/earnings","fiscalPeriod":"2025Q2","fiscalEndDate":1743393600,"epsActual":1.65,"epsEstimate":1.6273,"epsReportedActual":1.65,"epsReportedEstimate":1.6273,"salesActual":95359,"salesEstimate":94542.1815},{"dateTimestamp":1753993800,"eventType":"chartEvent/earnings","fiscalPeriod":"2025Q3","fiscalEndDate":1751256000,"epsActual":1.57,"epsEstimate":1.438,"epsReportedActual":1.57,"epsReportedEstimate":1.438,"salesActual":94036,"salesEstimate":89562.7364},{"dateTimestamp":1761856200,"eventType":"chartEvent/earnings","fiscalPeriod":"2025Q4","fiscalEndDate":1759204800,"epsActual":1.85,"epsEstimate":1.7771,"epsReportedActual":1.85,"epsReportedEstimate":1.7771,"salesActual":102466,"salesEstimate":102227.0746},{"dateTimestamp":1762750800,"eventType":"chartEvent/dividends","ordinary":0.26,"special":0},{"dateTimestamp":1754884800,"eventType":"chartEvent/dividends","ordinary":0.26,"special":0},{"dateTimestamp":1747022400,"eventType":"chartEvent/dividends","ordinary":0.26,"special":0},{"dateTimestamp":1739163600,"eventType":"chartEvent/dividends","ordinary":0.25,"special":0},{"dateTimestamp":1731042000,"eventType":"chartEvent/dividends","ordinary":0.25,"special":0},{"dateTimestamp":1723435200,"eventType":"chartEvent/dividends","ordinary":0.25,"special":0},{"dateTimestamp":1715313600,"eventType":"chartEvent/dividends","ordinary":0.25,"special":0}],"patterns":[{"kind":1,"strength":2063.2693,"status":2,"bounces":0,"x1":0,"y1":192,"x2":600,"y2":192,"x3":0,"y3":0,"x4":0,"y4":0,"ticker":""},{"kind":2,"strength":503.42264,"status":1,"bounces":3,"x1":93,"y1":193,"x2":600,"y2":17,"x3":0,"y3":0,"x4":0,"y4":0,"ticker":""},{"kind":3,"strength":64.981255,"status":1,"bounces":2,"x1":84,"y1":269,"x2":600,"y2":88,"x3":0,"y3":0,"x4":0,"y4":0,"ticker":""},{"kind":9,"strength":180.86745,"status":1,"bounces":3,"x1":93,"y1":193,"x2":600,"y2":17,"x3":84,"y3":269,"x4":600,"y4":88,"ticker":""}],"patternsMinRange":160,"patternsMaxRange":300};
                        data.instrument = 'stock';
                        data.premarket = 0;
                        data.aftermarket = 0;
                        data.hasPatterns = true;
                        data.events = true;
                        data.financialAttachments = [];
                        window.globalChartConfig.quoteData = data;
                    </script></div><div class="fv-container">
<table width="100%" cellpadding="0" cellspacing="0" border="0">
<tr>
<td align="center" valign="top">
<div class="content" data-testid="quote-data-content"><table style="table-layout:fixed" width="100%"><tr>
<td align="center" valign="top">
<div class="mt-1"><div id="IC_D_970x91_1"class="relative overflow-hidden flex items-center justify-center w-full mx-auto" style="width:970px;height:100px;max-height:100px"></div></div><table width="100%" cellpding="0" cellspacing="0" class="fullview-links table-fixed">
<tbody>
<tr>
<td class="js-quote-correlation-links-container" align="left" height="20">
<div class="flex">
<div class="flex-1 max-w-max truncate">
<a class="tab-link" href="screener.ashx?t=MSFT,SONY,DELL,GOOGL,HPQ,AMZN,NVDA,IBM,META,NFLX">Peers</a>:<span style="font-size:11px"> <span class="inline-flex" data-boxover="cssbody=[hoverchart] cssheader=[tabchrthdr] body=[<img  srcset='https://charts2-node.finviz.com/chart.ashx?cs=m&t=MSFT&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d 1x, https://charts2-node.finviz.com/chart.ashx?cs=m&t=MSFT&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&sf=2 2x' width='324' height='180' alt='' loading='lazy'><div><b>Microsoft Corporation</b>Software - Infrastructure <span>•</span> USA <span>•</span> 3556.62B </div>] offsetx=[0] offsety=[0] delay=[250]""><a href="quote.ashx?t=MSFT&ty=c&ta=1&p=d" class="tab-link">MSFT</a></span> <span class="inline-flex" data-boxover="cssbody=[hoverchart] cssheader=[tabchrthdr] body=[<img  srcset='https://charts2-node.finviz.com/chart.ashx?cs=m&t=SONY&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d 1x, https://charts2-node.finviz.com/chart.ashx?cs=m&t=SONY&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&sf=2 2x' width='324' height='180' alt='' loading='lazy'><div><b>Sony Group Corporation ADR</b>Consumer Electronics <span>•</span> Japan <span>•</span> 160.01B </div>] offsetx=[0] offsety=[0] delay=[250]""><a href="quote.ashx?t=SONY&ty=c&ta=1&p=d" class="tab-link">SONY</a></span> <span class="inline-flex" data-boxover="cssbody=[hoverchart] cssheader=[tabchrthdr] body=[<img  srcset='https://charts2-node.finviz.com/chart.ashx?cs=m&t=DELL&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d 1x, https://charts2-node.finviz.com/chart.ashx?cs=m&t=DELL&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&sf=2 2x' width='324' height='180' alt='' loading='lazy'><div><b>Dell Technologies Inc</b>Computer Hardware <span>•</span> USA <span>•</span> 86.14B </div>] offsetx=[0] offsety=[0] delay=[250]""><a href="quote.ashx?t=DELL&ty=c&ta=1&p=d" class="tab-link">DELL</a></span> <span class="inline-flex" data-boxover="cssbody=[hoverchart] cssheader=[tabchrthdr] body=[<img  srcset='https://charts2-node.finviz.com/chart.ashx?cs=m&t=GOOGL&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d 1x, https://charts2-node.finviz.com/chart.ashx?cs=m&t=GOOGL&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&sf=2 2x' width='324' height='180' alt='' loading='lazy'><div><b>Alphabet Inc</b>Internet Content & Information <span>•</span> USA <span>•</span> 3738.85B </div>] offsetx=[0] offsety=[0] delay=[250]""><a href="quote.ashx?t=GOOGL&ty=c&ta=1&p=d" class="tab-link">GOOGL</a></span> <span class="inline-flex" data-boxover="cssbody=[hoverchart] cssheader=[tabchrthdr] body=[<img  srcset='https://charts2-node.finviz.com/chart.ashx?cs=m&t=HPQ&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d 1x, https://charts2-node.finviz.com/chart.ashx?cs=m&t=HPQ&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&sf=2 2x' width='324' height='180' alt='' loading='lazy'><div><b>HP Inc</b>Computer Hardware <span>•</span> USA <span>•</span> 22.71B </div>] offsetx=[0] offsety=[0] delay=[250]""><a href="quote.ashx?t=HPQ&ty=c&ta=1&p=d" class="tab-link">HPQ</a></span> <span class="inline-flex" data-boxover="cssbody=[hoverchart] cssheader=[tabchrthdr] body=[<img  srcset='https://charts2-node.finviz.com/chart.ashx?cs=m&t=AMZN&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d 1x, https://charts2-node.finviz.com/chart.ashx?cs=m&t=AMZN&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&sf=2 2x' width='324' height='180' alt='' loading='lazy'><div><b>Amazon.com Inc</b>Internet Retail <span>•</span> USA <span>•</span> 2418.02B </div>] offsetx=[0] offsety=[0] delay=[250]""><a href="quote.ashx?t=AMZN&ty=c&ta=1&p=d" class="tab-link">AMZN</a></span> <span class="inline-flex" data-boxover="cssbody=[hoverchart] cssheader=[tabchrthdr] body=[<img  srcset='https://charts2-node.finviz.com/chart.ashx?cs=m&t=NVDA&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d 1x, https://charts2-node.finviz.com/chart.ashx?cs=m&t=NVDA&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&sf=2 2x' width='324' height='180' alt='' loading='lazy'><div><b>NVIDIA Corp</b>Semiconductors <span>•</span> USA <span>•</span> 4252.99B </div>] offsetx=[0] offsety=[0] delay=[250]""><a href="quote.ashx?t=NVDA&ty=c&ta=1&p=d" class="tab-link">NVDA</a></span> <span class="inline-flex" data-boxover="cssbody=[hoverchart] cssheader=[tabchrthdr] body=[<img  srcset='https://charts2-node.finviz.com/chart.ashx?cs=m&t=IBM&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d 1x, https://charts2-node.finviz.com/chart.ashx?cs=m&t=IBM&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&sf=2 2x' width='324' height='180' alt='' loading='lazy'><div><b>International Business Machines Corp</b>Information Technology Services <span>•</span> USA <span>•</span> 289.06B </div>] offsetx=[0] offsety=[0] delay=[250]""><a href="quote.ashx?t=IBM&ty=c&ta=1&p=d" class="tab-link">IBM</a></span> <span class="inline-flex" data-boxover="cssbody=[hoverchart] cssheader=[tabchrthdr] body=[<img  srcset='https://charts2-node.finviz.com/chart.ashx?cs=m&t=META&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d 1x, https://charts2-node.finviz.com/chart.ashx?cs=m&t=META&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&sf=2 2x' width='324' height='180' alt='' loading='lazy'><div><b>Meta Platforms Inc</b>Internet Content & Information <span>•</span> USA <span>•</span> 1623.80B </div>] offsetx=[0] offsety=[0] delay=[250]""><a href="quote.ashx?t=META&ty=c&ta=1&p=d" class="tab-link">META</a></span> <span class="inline-flex" data-boxover="cssbody=[hoverchart] cssheader=[tabchrthdr] body=[<img  srcset='https://charts2-node.finviz.com/chart.ashx?cs=m&t=NFLX&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d 1x, https://charts2-node.finviz.com/chart.ashx?cs=m&t=NFLX&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&sf=2 2x' width='324' height='180' alt='' loading='lazy'><div><b>Netflix Inc</b>Entertainment <span>•</span> USA <span>•</span> 434.97B </div>] offsetx=[0] offsety=[0] delay=[250]""><a href="quote.ashx?t=NFLX&ty=c&ta=1&p=d" class="tab-link">NFLX</a></span></span></div><div class="flex-1 max-w-max truncate">
&nbsp;|&nbsp;<a class="tab-link" href="screener.ashx?t=VTI,VOO,SPY,IVV,VUG,QQQ,VGT,IWF,XLK,SPYM">Held by</a>:<span style="font-size:11px"> <span class="inline-flex" data-boxover="cssbody=[hoverchart] cssheader=[tabchrthdr] body=[<img  srcset='https://charts2-node.finviz.com/chart.ashx?cs=m&t=VTI&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d 1x, https://charts2-node.finviz.com/chart.ashx?cs=m&t=VTI&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&sf=2 2x' width='324' height='180' alt='' loading='lazy'><div><b>Vanguard Total Stock Market ETF</b>Exchange Traded Fund <span>•</span> USA <span>•</span> AUM: 575.77B </div>] offsetx=[-470] offsety=[0] delay=[250]""><a href="quote.ashx?t=VTI&ty=c&ta=1&p=d" class="tab-link">VTI</a></span> <span class="inline-flex" data-boxover="cssbody=[hoverchart] cssheader=[tabchrthdr] body=[<img  srcset='https://charts2-node.finviz.com/chart.ashx?cs=m&t=VOO&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d 1x, https://charts2-node.finviz.com/chart.ashx?cs=m&t=VOO&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&sf=2 2x' width='324' height='180' alt='' loading='lazy'><div><b>Vanguard S&P 500 ETF</b>Exchange Traded Fund <span>•</span> USA <span>•</span> AUM: 832.46B </div>] offsetx=[-470] offsety=[0] delay=[250]""><a href="quote.ashx?t=VOO&ty=c&ta=1&p=d" class="tab-link">VOO</a></span> <span class="inline-flex" data-boxover="cssbody=[hoverchart] cssheader=[tabchrthdr] body=[<img  srcset='https://charts2-node.finviz.com/chart.ashx?cs=m&t=SPY&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d 1x, https://charts2-node.finviz.com/chart.ashx?cs=m&t=SPY&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&sf=2 2x' width='324' height='180' alt='' loading='lazy'><div><b>SPDR S&P 500 ETF Trust</b>Exchange Traded Fund <span>•</span> USA <span>•</span> AUM: 718.02B </div>] offsetx=[-470] offsety=[0] delay=[250]""><a href="quote.ashx?t=SPY&ty=c&ta=1&p=d" class="tab-link">SPY</a></span> <span class="inline-flex" data-boxover="cssbody=[hoverchart] cssheader=[tabchrthdr] body=[<img  srcset='https://charts2-node.finviz.com/chart.ashx?cs=m&t=IVV&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d 1x, https://charts2-node.finviz.com/chart.ashx?cs=m&t=IVV&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&sf=2 2x' width='324' height='180' alt='' loading='lazy'><div><b>iShares Core S&P 500 ETF</b>Exchange Traded Fund <span>•</span> USA <span>•</span> AUM: 675.59B </div>] offsetx=[-470] offsety=[0] delay=[250]""><a href="quote.ashx?t=IVV&ty=c&ta=1&p=d" class="tab-link">IVV</a></span> <span class="inline-flex" data-boxover="cssbody=[hoverchart] cssheader=[tabchrthdr] body=[<img  srcset='https://charts2-node.finviz.com/chart.ashx?cs=m&t=VUG&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d 1x, https://charts2-node.finviz.com/chart.ashx?cs=m&t=VUG&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&sf=2 2x' width='324' height='180' alt='' loading='lazy'><div><b>Vanguard Growth ETF</b>Exchange Traded Fund <span>•</span> USA <span>•</span> AUM: 204.49B </div>] offsetx=[-470] offsety=[0] delay=[250]""><a href="quote.ashx?t=VUG&ty=c&ta=1&p=d" class="tab-link">VUG</a></span> <span class="inline-flex" data-boxover="cssbody=[hoverchart] cssheader=[tabchrthdr] body=[<img  srcset='https://charts2-node.finviz.com/chart.ashx?cs=m&t=QQQ&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d 1x, https://charts2-node.finviz.com/chart.ashx?cs=m&t=QQQ&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&sf=2 2x' width='324' height='180' alt='' loading='lazy'><div><b>Invesco QQQ Trust Series 1</b>Exchange Traded Fund <span>•</span> USA <span>•</span> AUM: 401.00B </div>] offsetx=[-470] offsety=[0] delay=[250]""><a href="quote.ashx?t=QQQ&ty=c&ta=1&p=d" class="tab-link">QQQ</a></span> <span class="inline-flex" data-boxover="cssbody=[hoverchart] cssheader=[tabchrthdr] body=[<img  srcset='https://charts2-node.finviz.com/chart.ashx?cs=m&t=VGT&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d 1x, https://charts2-node.finviz.com/chart.ashx?cs=m&t=VGT&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&sf=2 2x' width='324' height='180' alt='' loading='lazy'><div><b>Vanguard Information Technology ETF</b>Exchange Traded Fund <span>•</span> USA <span>•</span> AUM: 115.85B </div>] offsetx=[-470] offsety=[0] delay=[250]""><a href="quote.ashx?t=VGT&ty=c&ta=1&p=d" class="tab-link">VGT</a></span> <span class="inline-flex" data-boxover="cssbody=[hoverchart] cssheader=[tabchrthdr] body=[<img  srcset='https://charts2-node.finviz.com/chart.ashx?cs=m&t=IWF&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d 1x, https://charts2-node.finviz.com/chart.ashx?cs=m&t=IWF&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&sf=2 2x' width='324' height='180' alt='' loading='lazy'><div><b>iShares Russell 1000 Growth ETF</b>Exchange Traded Fund <span>•</span> USA <span>•</span> AUM: 124.79B </div>] offsetx=[-470] offsety=[0] delay=[250]""><a href="quote.ashx?t=IWF&ty=c&ta=1&p=d" class="tab-link">IWF</a></span> <span class="inline-flex" data-boxover="cssbody=[hoverchart] cssheader=[tabchrthdr] body=[<img  srcset='https://charts2-node.finviz.com/chart.ashx?cs=m&t=XLK&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d 1x, https://charts2-node.finviz.com/chart.ashx?cs=m&t=XLK&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&sf=2 2x' width='324' height='180' alt='' loading='lazy'><div><b>State Street Technology Select Sector SPDR ETF</b>Exchange Traded Fund <span>•</span> USA <span>•</span> AUM: 92.84B </div>] offsetx=[-470] offsety=[0] delay=[250]""><a href="quote.ashx?t=XLK&ty=c&ta=1&p=d" class="tab-link">XLK</a></span> <span class="inline-flex" data-boxover="cssbody=[hoverchart] cssheader=[tabchrthdr] body=[<img  srcset='https://charts2-node.finviz.com/chart.ashx?cs=m&t=SPYM&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d 1x, https://charts2-node.finviz.com/chart.ashx?cs=m&t=SPYM&tf=d&s=linear&pm=0&am=0&ct=candle_stick&tm=d&sf=2 2x' width='324' height='180' alt='' loading='lazy'><div><b>State Street SPDR Portfolio S&P 500 ETF</b>Exchange Traded Fund <span>•</span> USA <span>•</span> AUM: 99.58B </div>] offsetx=[-470] offsety=[0] delay=[250]""><a href="quote.ashx?t=SPYM&ty=c&ta=1&p=d" class="tab-link">SPYM</a></span></span></div><div class="ml-auto flex-none pl-2">
    <a class="tab-link whitespace-nowrap" href="#statements">Scroll to Statements<svg width="12" height="12" class="fill-current inline-block ml-0.5">
    <use href="/assets/dist-icons/icons.svg?rev=35#arrowDown"/>
</svg></a></div>
</div>
</td>
</tr>
</tbody>
</table>
<div style="overflow:hidden;" class="screener_snapshot-table-wrapper js-snapshot-table-wrapper"><table width="100%" cellpadding="3" cellspacing="0" border="0" class="js-snapshot-table snapshot-table2 screener_snapshot-table-body">
<tr class="table-dark-row">
<td class="snapshot-td2 cursor-pointer w-[7%]" align="left" data-boxover="cssbody=[tooltip_short_bdy] cssheader=[tooltip_short_hdr] body=[Major index membership] offsetx=[10] offsety=[20] delay=[300]">Index</td><td class="snapshot-td2 w-[8%] " align="left" style=""><b><small class="xl:text-2xs">DJIA, NDX, S&P 500</small></b></td>
<td class="snapshot-td2 cursor-pointer w-[7%]" align="left" data-boxover="cssbody=[tooltip_short_bdy] cssheader=[tooltip_short_hdr] body=[Price-to-Earnings (ttm)] offsetx=[10] offsety=[20] delay=[300]">P/E</td><td class="snapshot-td2 w-[8%] " align="left" style=""><b>37.31</b></td>
<td class="snapshot-td2 cursor-pointer w-[7%]" align="left" data-boxover="cssbody=[tooltip_short_bdy] cssheader=[tooltip_short_hdr] body=[Diluted EPS (ttm)] offsetx=[10] offsety=[20] delay=[300]">EPS (ttm)</td><td class="snapshot-td2 w-[8%] " align="left" style=""><b>7.46</b></td>
<td class="snapshot-td2 cursor-pointer w-[7%]" align="left" data-boxover="cssbody=[tooltip_short_bdy] cssheader=[tooltip_short_hdr] body=[Insider ownership] offsetx=[10] offsety=[20] delay=[300]">Insider Own</td><td class="snapshot-td2 w-[8%] " align="left" style=""><b>0.10%</b></td>
<td class="snapshot-td2 cursor-pointer w-[7%]" align="left" data-boxover="cssbody=[tooltip_short_bdy] cssheader=[tooltip_short_hdr] body=[Shares outstanding] offsetx=[10] offsety=[20] delay=[300]">Shs Outstand</td><td class="snapshot-td2 w-[8%] " align="left" style=""><b>14.77B</b></td>
<td class="snapshot-td2 cursor-pointer w-[7%]" align="left" data-boxover="cssbody=[tooltip_short_bdy] cssheader=[tooltip_short_hdr] body=[Performance (Week, Excl. Dividends)] offsetx=[10] offsety=[20] delay=[300]">Perf Week</td><td class="snapshot-td2 w-[8%] " align="left" style=""><b><span class="color-text is-negative">-0.18%</span></b></td>
</tr>
<tr class="table-dark-row">
<td class="snapshot-td2 cursor-pointer w-[7%]" align="left" data-boxover="cssbody=[tooltip_short_bdy] cssheader=[tooltip_short_hdr] body=[Market capitalization] offsetx=[10] offsety=[20] delay=[300]">Market Cap</td><td class="snapshot-td2 w-[8%] " align="left" style=""><b>4111.96B</b></td>
<td class="snapshot-td2 cursor-pointer w-[7%]" align="left" data-boxover="cssbody=[tooltip_short_bdy] cssheader=[tooltip_short_hdr] body=[Forward Price-to-Earnings (next fiscal year)] offsetx=[10] offsety=[20] delay=[300]">Forward P/E</td><td class="snapshot-td2 w-[8%] " align="left" style=""><b>30.54</b></td>
<td class="snapshot-td2 cursor-pointer w-[7%]" align="left" data-boxover="cssbody=[tooltip_short_bdy] cssheader=[tooltip_short_hdr] body=[EPS estimate for next year] offsetx=[10] offsety=[20] delay=[300]">EPS next Y</td><td class="snapshot-td2 w-[8%] " align="left" style=""><b>9.11</b></td>
<td class="snapshot-td2 cursor-pointer w-[7%]" align="left" data-boxover="cssbody=[tooltip_short_bdy] cssheader=[tooltip_short_hdr] body=[Insider transactions (6-Month change in Insider Ownership)] offsetx=[10] offsety=[20] delay=[300]">Insider Trans</td><td class="snapshot-td2 w-[8%] " align="left" style=""><b>-2.33%</b></td>
<td class="snapshot-td2 cursor-pointer w-[7%]" align="left" data-boxover="cssbody=[tooltip_short_bdy] cssheader=[tooltip_short_hdr] body=[Shares float] offsetx=[10] offsety=[20] delay=[300]">Shs Float</td><td class="snapshot-td2 w-[8%] " align="left" style=""><b>14.76B</b></td>
<td class="snapshot-td2 cursor-pointer w-[7%]" align="left" data-boxover="cssbody=[tooltip_short_bdy] cssheader=[tooltip_short_hdr] body=[Performance (Month, Excl. Dividends)] offsetx=[10] offsety=[20] delay=[300]">Perf Month</td><td class="snapshot-td2 w-[8%] " align="left" style=""><b><span class="color-text is-positive">1.76%</span></b></td>
</tr>
<tr class="table-dark-row">
<td class="snapshot-td2 cursor-pointer w-[7%]" align="left" data-boxover="cssbody=[tooltip_short_bdy] cssheader=[tooltip_short_hdr] body=[Enterprise Value] offsetx=[10] offsety=[20] delay=[300]">Enterprise Value</td><td class="snapshot-td2 w-[8%] " align="left" style=""><b>4169.64B</b></td>
<td class="snapshot-td2 cursor-pointer w-[7%]" align="left" data-boxover="cssbody=[tooltip_short_bdy] cssheader=[tooltip_short_hdr] body=[Price-to-Earnings-to-Growth] offsetx=[10] offsety=[20] delay=[300]">PEG</td><td class="snapshot-td2 w-[8%] " align="left" style=""><b><span class="color-text is-negative">2.95</span></b></td>
<td class="snapshot-td2 cursor-pointer w-[7%]" align="left" data-boxover="cssbody=[tooltip_short_bdy] cssheader=[tooltip_short_hdr] body=[EPS estimate for next quarter] offsetx=[10] offsety=[20] delay=[300]">EPS next Q</td><td class="snapshot-td2 w-[8%] " align="left" style=""><b>2.67</b></td>
<td class="snapshot-td2 cursor-pointer w-[7%]" align="left" data-boxover="cssbody=[tooltip_short_bdy] cssheader=[tooltip_short_hdr] body=[Institutional ownership] offsetx=[10] offsety=[20] delay=[300]">Inst Own</td><td class="snapshot-td2 w-[8%] " align="left" style=""><b>64.89%</b></td>
<td class="snapshot-td2 cursor-pointer w-[7%]" align="left" data-boxover="cssbody=[tooltip_short_bdy] cssheader=[tooltip_short_hdr] body=[Short interest share] offsetx=[10] offsety=[20] delay=[300]"><a href="quote.ashx?t=AAPL&ta=1&p=d&ty=si" class="hover:underline">Short Float</a></td><td class="snapshot-td2 w-[8%] " align="left" style=""><a href="quote.ashx?t=AAPL&ta=1&p=d&ty=si" class="hover:underline"><b>0.88%</b></a></td>
<td class="snapshot-td2 cursor-pointer w-[7%]" align="left" data-boxover="cssbody=[tooltip_short_bdy] cssheader=[tooltip_short_hdr] body=[Performance (Quarter, Excl. Dividends)] offsetx=[10] offsety=[20] delay=[300]">Perf Quarter</td><td class="snapshot-td2 w-[8%] " align="left" style=""><b><span class="color-text is-positive">17.57%</span></b></td>
</tr>
<tr class="table-dark-row">
<td class="snapshot-td2 cursor-pointer w-[7%]" align="left" data-boxover="cssbody=[tooltip_short_bdy] cssheader=[tooltip_short_hdr] body=[Income (ttm)] offsetx=[10] offsety=[20] delay=[300]">Income</td><td class="snapshot-td2 w-[8%] " align="left" style=""><b>112.01B</b></td>
<td class="snapshot-td2 cursor-pointer w-[7%]" align="left" data-boxover="cssbody=[tooltip_short_bdy] cssheader=[tooltip_short_hdr] body=[Price-to-Sales (ttm)] offsetx=[10] offsety=[20] delay=[300]">P/S</td><td class="snapshot-td2 w-[8%] " align="left" style=""><b>9.88</b></td>
<td class="snapshot-td2 cursor-pointer w-[7%]" align="left" data-boxover="cssbody=[tooltip_short_bdy] cssheader=[tooltip_short_hdr] body=[EPS growth this year] offsetx=[10] offsety=[20] delay=[300]">EPS this Y</td><td class="snapshot-td2 w-[8%] " align="left" style=""><b>10.48%</b></td>
<td class="snapshot-td2 cursor-pointer w-[7%]" align="left" data-boxover="cssbody=[tooltip_short_bdy] cssheader=[tooltip_short_hdr] body=[Institutional transactions (3-Month change in Institutional Ownership)] offsetx=[10] offsety=[20] delay=[300]">Inst Trans</td><td class="snapshot-td2 w-[8%] " align="left" style=""><b>-0.15%</b></td>
<td class="snapshot-td2 cursor-pointer w-[7%]" align="left" data-boxover="cssbody=[tooltip_short_bdy] cssheader=[tooltip_short_hdr] body=[Short interest ratio] offsetx=[10] offsety=[20] delay=[300]"><a href="quote.ashx?t=AAPL&ta=1&p=d&ty=si" class="hover:underline">Short Ratio</a></td><td class="snapshot-td2 w-[8%] " align="left" style=""><a href="quote.ashx?t=AAPL&ta=1&p=d&ty=si" class="hover:underline"><b>2.63</b></a></td>
<td class="snapshot-td2 cursor-pointer w-[7%]" align="left" data-boxover="cssbody=[tooltip_short_bdy] cssheader=[tooltip_short_hdr] body=[Performance (Half Year, Excl. Dividends)] offsetx=[10] offsety=[20] delay=[300]">Perf Half Y</td><td class="snapshot-td2 w-[8%] " align="left" style=""><b><span class="color-text is-positive">41.65%</span></b></td>
</tr>
<tr class="table-dark-row">
<td class="snapshot-td2 cursor-pointer w-[7%]" align="left" data-boxover="cssbody=[tooltip_short_bdy] cssheader=[tooltip_short_hdr] body=[Revenue (ttm)] offsetx=[10] offsety=[20] delay=[300]">Sales</td><td class="snapshot-td2 w-[8%] " align="left" style=""><b>416.16B</b></td>
<td class="snapshot-td2 cursor-pointer w-[7%]" align="left" data-boxover="cssbody=[tooltip_short_bdy] cssheader=[tooltip_short_hdr] body=[Price-to-Book (mrq)] offsetx=[10] offsety=[20] delay=[300]">P/B</td><td class="snapshot-td2 w-[8%] " align="left" style=""><b><span class="color-text is-negative">55.76</span></b></td>
<td class="snapshot-td2 cursor-pointer w-[7%]" align="left" data-boxover="cssbody=[tooltip_short_bdy] cssheader=[tooltip_short_hdr] body=[EPS growth next year] offsetx=[10] offsety=[20] delay=[300]">EPS next Y</td><td class="snapshot-td2 w-[8%] " align="left" style=""><b>10.56%</b></td>
<td class="snapshot-td2 cursor-pointer w-[7%]" align="left" data-boxover="cssbody=[tooltip_short_bdy] cssheader=[tooltip_short_hdr] body=[Return on Assets (ttm)] offsetx=[10] offsety=[20] delay=[300]">ROA</td><td class="snapshot-td2 w-[8%] " align="left" style=""><b><span class="color-text is-positive">30.93%</span></b></td>
<td class="snapshot-td2 cursor-pointer w-[7%]" align="left" data-boxover="cssbody=[tooltip_short_bdy] cssheader=[tooltip_short_hdr] body=[Short interest] offsetx=[10] offsety=[20] delay=[300]"><a href="quote.ashx?t=AAPL&ta=1&p=d&ty=si" class="hover:underline">Short Interest</a></td><td class="snapshot-td2 w-[8%] " align="left" style=""><a href="quote.ashx?t=AAPL&ta=1&p=d&ty=si" class="hover:underline"><b data-boxover="cssbody=[tooltip_short_bdy] cssheader=[tooltip_short_hdr] body=[Settlement Date: 11/28/2025] offsetx=[10] offsety=[20] delay=[500]">129.46M</b></a></td>
<td class="snapshot-td2 cursor-pointer w-[7%]" align="left" data-boxover="cssbody=[tooltip_short_bdy] cssheader=[tooltip_short_hdr] body=[Performance (Year To Date, Excl. Dividends)] offsetx=[10] offsety=[20] delay=[300]">Perf YTD</td><td class="snapshot-td2 w-[8%] " align="left" style=""><b><span class="color-text is-positive">11.13%</span></b></td>
</tr>
<tr class="table-dark-row">
<td class="snapshot-td2 cursor-pointer w-[7%]" align="left" data-boxover="cssbody=[tooltip_short_bdy] cssheader=[tooltip_short_hdr] body=[Book value per share (mrq)] offsetx=[10] offsety=[20] delay=[300]">Book/sh</td><td class="snapshot-td2 w-[8%] " align="left" style=""><b>4.99</b></td>
<td class="snapshot-td2 cursor-pointer w-[7%]" align="left" data-boxover="cssbody=[tooltip_short_bdy] cssheader=[tooltip_short_hdr] body=[Price to cash per share (mrq)] offsetx=[10] offsety=[20] delay=[300]">P/C</td><td class="snapshot-td2 w-[8%] " align="left" style=""><b><span class="color-text is-negative">75.18</span></b></td>
<td class="snapshot-td2 cursor-pointer w-[7%]" align="left" data-boxover="cssbody=[tooltip_short_bdy] cssheader=[tooltip_short_hdr] body=[Long term annual growth estimate (5 years)] offsetx=[10] offsety=[20] delay=[300]">EPS next 5Y</td><td class="snapshot-td2 w-[8%] " align="left" style=""><b>10.36%</b></td>
<td class="snapshot-td2 cursor-pointer w-[7%]" align="left" data-boxover="cssbody=[tooltip_short_bdy] cssheader=[tooltip_short_hdr] body=[Return on Equity (ttm)] offsetx=[10] offsety=[20] delay=[300]">ROE</td><td class="snapshot-td2 w-[8%] " align="left" style=""><b><span class="color-text is-positive">171.42%</span></b></td>
<td class="snapshot-td2 cursor-pointer w-[7%]" align="left" data-boxover="cssbody=[tooltip_short_bdy] cssheader=[tooltip_short_hdr] body=[Distance from 52-Week High] offsetx=[10] offsety=[20] delay=[300]">52W High</td><td class="snapshot-td2 w-[8%] " align="left" style=""><b>288.62 <small class="xl:text-2xs"><span class="color-text is-negative">-3.58%</span></small></b></td>
<td class="snapshot-td2 cursor-pointer w-[7%]" align="left" data-boxover="cssbody=[tooltip_short_bdy] cssheader=[tooltip_short_hdr] body=[Performance (Year, Excl. Dividends)] offsetx=[10] offsety=[20] delay=[300]">Perf Year</td><td class="snapshot-td2 w-[8%] " align="left" style=""><b><span class="color-text is-positive">12.31%</span></b></td>
</tr>
<tr class="table-dark-row">
<td class="snapshot-td2 cursor-pointer w-[7%]" align="left" data-boxover="cssbody=[tooltip_short_bdy] cssheader=[tooltip_short_hdr] body=[Cash per share (mrq)] offsetx=[10] offsety=[20] delay=[300]">Cash/sh</td><td class="snapshot-td2 w-[8%] " align="left" style=""><b>3.70</b></td>
<td class="snapshot-td2 cursor-pointer w-[7%]" align="left" data-boxover="cssbody=[tooltip_short_bdy] cssheader=[tooltip_short_hdr] body=[Price to Free Cash Flow (ttm)] offsetx=[10] offsety=[20] delay=[300]">P/FCF</td><td class="snapshot-td2 w-[8%] " align="left" style=""><b>41.63</b></td>
<td class="snapshot-td2 cursor-pointer w-[7%]" align="left" data-boxover="cssbody=[tooltip_short_bdy] cssheader=[tooltip_short_hdr] body=[Annual EPS growth past 3 and 5 years] offsetx=[10] offsety=[20] delay=[300]">EPS past 3/5Y</td><td class="snapshot-td2 w-[8%] " align="left" style=""><b><small class="xl:text-2xs">6.89% 17.91%</small></b></td>
<td class="snapshot-td2 cursor-pointer w-[7%]" align="left" data-boxover="cssbody=[tooltip_short_bdy] cssheader=[tooltip_short_hdr] body=[Return on Invested Capital (ttm)] offsetx=[10] offsety=[20] delay=[300]">ROIC</td><td class="snapshot-td2 w-[8%] " align="left" style=""><b><span class="color-text is-positive">68.44%</span></b></td>
<td class="snapshot-td2 cursor-pointer w-[7%]" align="left" data-boxover="cssbody=[tooltip_short_bdy] cssheader=[tooltip_short_hdr] body=[Distance from 52-Week Low] offsetx=[10] offsety=[20] delay=[300]">52W Low</td><td class="snapshot-td2 w-[8%] " align="left" style=""><b>169.21 <small class="xl:text-2xs"><span class="color-text is-positive">64.46%</span></small></b></td>
<td class="snapshot-td2 cursor-pointer w-[7%]" align="left" data-boxover="cssbody=[tooltip_short_bdy] cssheader=[tooltip_short_hdr] body=[Performance (3 Years, Excl. Dividends)] offsetx=[10] offsety=[20] delay=[300]">Perf 3Y</td><td class="snapshot-td2 w-[8%] " align="left" style=""><b><span class="color-text is-positive">97.45%</span></b></td>
</tr>
<tr class="table-dark-row">
<td class="snapshot-td2 cursor-pointer w-[7%]" align="left" data-boxover="cssbody=[tooltip_short_bdy] cssheader=[tooltip_short_hdr] body=[Analysts' Dividend Estimate (Fiscal Year)] offsetx=[10] offsety=[20] delay=[300]"><a href="quote.ashx?t=AAPL&ta=1&p=d&ty=dv" class="hover:underline">Dividend Est.</a></td><td class="snapshot-td2 w-[8%] " align="left" style=""><a href="quote.ashx?t=AAPL&ta=1&p=d&ty=dv" class="hover:underline"><b>1.08 (0.39%)</b></a></td>
<td class="snapshot-td2 cursor-pointer w-[7%]" align="left" data-boxover="cssbody=[tooltip_short_bdy] cssheader=[tooltip_short_hdr] body=[Enterprise Value to EBITDA] offsetx=[10] offsety=[20] delay=[300]">EV/EBITDA</td><td class="snapshot-td2 w-[8%] " align="left" style=""><b>28.81</b></td>
<td class="snapshot-td2 cursor-pointer w-[7%]" align="left" data-boxover="cssbody=[tooltip_short_bdy] cssheader=[tooltip_short_hdr] body=[Annual sales growth past 3 and 5 years] offsetx=[10] offsety=[20] delay=[300]">Sales past 3/5Y</td><td class="snapshot-td2 w-[8%] " align="left" style=""><b><small class="xl:text-2xs">1.81% 8.71%</small></b></td>
<td class="snapshot-td2 cursor-pointer w-[7%]" align="left" data-boxover="cssbody=[tooltip_short_bdy] cssheader=[tooltip_short_hdr] body=[Gross Margin (ttm)] offsetx=[10] offsety=[20] delay=[300]">Gross Margin</td><td class="snapshot-td2 w-[8%] " align="left" style=""><b>46.91%</b></td>
<td class="snapshot-td2 cursor-pointer w-[7%]" align="left" data-boxover="cssbody=[tooltip_short_bdy] cssheader=[tooltip_short_hdr] body=[Volatility (Week, Month)] offsetx=[10] offsety=[20] delay=[300]">Volatility</td><td class="snapshot-td2 w-[8%] " align="left" style=""><b><small class="xl:text-2xs">1.31% 1.87%</small></b></td>
<td class="snapshot-td2 cursor-pointer w-[7%]" align="left" data-boxover="cssbody=[tooltip_short_bdy] cssheader=[tooltip_short_hdr] body=[Performance (5 Years, Excl. Dividends)] offsetx=[10] offsety=[20] delay=[300]">Perf 5Y</td><td class="snapshot-td2 w-[8%] " align="left" style=""><b><span class="color-text is-positive">124.87%</span></b></td>
</tr>
<tr class="table-dark-row">
<td class="snapshot-td2 cursor-pointer w-[7%]" align="left" data-boxover="cssbody=[tooltip_short_bdy] cssheader=[tooltip_short_hdr] body=[Trailing 12 Months Dividend] offsetx=[10] offsety=[20] delay=[300]"><a href="quote.ashx?t=AAPL&ta=1&p=d&ty=dv" class="hover:underline">Dividend TTM</a></td><td class="snapshot-td2 w-[8%] " align="left" style=""><a href="quote.ashx?t=AAPL&ta=1&p=d&ty=dv" class="hover:underline"><b>1.03 (0.37%)</b></a></td>
<td class="snapshot-td2 cursor-pointer w-[7%]" align="left" data-boxover="cssbody=[tooltip_short_bdy] cssheader=[tooltip_short_hdr] body=[Enterprise Value to Revenues] offsetx=[10] offsety=[20] delay=[300]">EV/Sales</td><td class="snapshot-td2 w-[8%] " align="left" style=""><b><span class="color-text is-negative">10.02</span></b></td>
<td class="snapshot-td2 cursor-pointer w-[7%]" align="left" data-boxover="cssbody=[tooltip_short_bdy] cssheader=[tooltip_short_hdr] body=[EPS growth TTM] offsetx=[10] offsety=[20] delay=[300]">EPS Y/Y TTM</td><td class="snapshot-td2 w-[8%] " align="left" style=""><b>22.85%</b></td>
<td class="snapshot-td2 cursor-pointer w-[7%]" align="left" data-boxover="cssbody=[tooltip_short_bdy] cssheader=[tooltip_short_hdr] body=[Operating Margin (ttm)] offsetx=[10] offsety=[20] delay=[300]">Oper. Margin</td><td class="snapshot-td2 w-[8%] " align="left" style=""><b><span class="color-text is-positive">31.97%</span></b></td>
<td class="snapshot-td2 cursor-pointer w-[7%]" align="left" data-boxover="cssbody=[tooltip_short_bdy] cssheader=[tooltip_short_hdr] body=[Average True Range (14)] offsetx=[10] offsety=[20] delay=[300]">ATR (14)</td><td class="snapshot-td2 w-[8%] " align="left" style=""><b>4.83</b></td>
<td class="snapshot-td2 cursor-pointer w-[7%]" align="left" data-boxover="cssbody=[tooltip_short_bdy] cssheader=[tooltip_short_hdr] body=[Performance (10 Years, Excl. Dividends)] offsetx=[10] offsety=[20] delay=[300]">Perf 10Y</td><td class="snapshot-td2 w-[8%] " align="left" style=""><b><span class="color-text is-positive">835.16%</span></b></td>
</tr>
<tr class="table-dark-row">
<td class="snapshot-td2 cursor-pointer w-[7%]" align="left" data-boxover="cssbody=[tooltip_short_bdy] cssheader=[tooltip_short_hdr] body=[Ex-Dividend Date] offsetx=[10] offsety=[20] delay=[300]"><a href="quote.ashx?t=AAPL&ta=1&p=d&ty=dv" class="hover:underline">Dividend Ex-Date</a></td><td class="snapshot-td2 w-[8%] " align="left" style=""><a href="quote.ashx?t=AAPL&ta=1&p=d&ty=dv" class="hover:underline"><b>Nov 10, 2025</b></a></td>
<td class="snapshot-td2 cursor-pointer w-[7%]" align="left" data-boxover="cssbody=[tooltip_short_bdy] cssheader=[tooltip_short_hdr] body=[Quick Ratio (mrq)] offsetx=[10] offsety=[20] delay=[300]">Quick Ratio</td><td class="snapshot-td2 w-[8%] " align="left" style=""><b>0.86</b></td>
<td class="snapshot-td2 cursor-pointer w-[7%]" align="left" data-boxover="cssbody=[tooltip_short_bdy] cssheader=[tooltip_short_hdr] body=[Sales growth TTM] offsetx=[10] offsety=[20] delay=[300]">Sales Y/Y TTM</td><td class="snapshot-td2 w-[8%] " align="left" style=""><b>6.43%</b></td>
<td class="snapshot-td2 cursor-pointer w-[7%]" align="left" data-boxover="cssbody=[tooltip_short_bdy] cssheader=[tooltip_short_hdr] body=[Net Profit Margin (ttm)] offsetx=[10] offsety=[20] delay=[300]">Profit Margin</td><td class="snapshot-td2 w-[8%] " align="left" style=""><b><span class="color-text is-positive">26.92%</span></b></td>
<td class="snapshot-td2 cursor-pointer w-[7%]" align="left" data-boxover="cssbody=[tooltip_short_bdy] cssheader=[tooltip_short_hdr] body=[Relative Strength Index] offsetx=[10] offsety=[20] delay=[300]">RSI (14)</td><td class="snapshot-td2 w-[8%] " align="left" style=""><b>57.58</b></td>
<td class="snapshot-td2 cursor-pointer w-[7%]" align="left" data-boxover="cssbody=[tooltip_short_bdy] cssheader=[tooltip_short_hdr] body=[Analysts' mean recommendation (1=Buy 5=Sell)] offsetx=[10] offsety=[20] delay=[300]"><a href="quote.ashx?t=AAPL&ta=1&p=d&ty=fc" class="hover:underline">Recom</a></td><td class="snapshot-td2 w-[8%] " align="left" style=""><a href="quote.ashx?t=AAPL&ta=1&p=d&ty=fc" class="hover:underline"><b>2.04</b></a></td>
</tr>
<tr class="table-dark-row">
<td class="snapshot-td2 cursor-pointer w-[7%]" align="left" data-boxover="cssbody=[tooltip_short_bdy] cssheader=[tooltip_short_hdr] body=[Dividend growth over 3 and 5 years] offsetx=[10] offsety=[20] delay=[300]"><a href="quote.ashx?t=AAPL&ta=1&p=d&ty=dv" class="hover:underline">Dividend Gr. 3/5Y</a></td><td class="snapshot-td2 w-[8%] " align="left" style=""><a href="quote.ashx?t=AAPL&ta=1&p=d&ty=dv" class="hover:underline"><b><small class="xl:text-2xs">4.26% 4.98%</small></b></a></td>
<td class="snapshot-td2 cursor-pointer w-[7%]" align="left" data-boxover="cssbody=[tooltip_short_bdy] cssheader=[tooltip_short_hdr] body=[Current Ratio (mrq)] offsetx=[10] offsety=[20] delay=[300]">Current Ratio</td><td class="snapshot-td2 w-[8%] " align="left" style=""><b><span class="color-text is-negative">0.89</span></b></td>
<td class="snapshot-td2 cursor-pointer w-[7%]" align="left" data-boxover="cssbody=[tooltip_short_bdy] cssheader=[tooltip_short_hdr] body=[Quarterly earnings growth (YoY)] offsetx=[10] offsety=[20] delay=[300]">EPS Q/Q</td><td class="snapshot-td2 w-[8%] " align="left" style=""><b><span class="color-text is-positive">91.14%</span></b></td>
<td class="snapshot-td2 cursor-pointer w-[7%]" align="left" data-boxover="cssbody=[tooltip_short_bdy] cssheader=[tooltip_short_hdr] body=[Distance from 20-Day Simple Moving Average] offsetx=[10] offsety=[20] delay=[300]">SMA20</td><td class="snapshot-td2 w-[8%] " align="left" style=""><b><span class="color-text is-positive">0.72%</span></b></td>
<td class="snapshot-td2 cursor-pointer w-[7%]" align="left" data-boxover="cssbody=[tooltip_short_bdy] cssheader=[tooltip_short_hdr] body=[Beta] offsetx=[10] offsety=[20] delay=[300]">Beta</td><td class="snapshot-td2 w-[8%] " align="left" style=""><b>1.09</b></td>
<td class="snapshot-td2 cursor-pointer w-[7%]" align="left" data-boxover="cssbody=[tooltip_short_bdy] cssheader=[tooltip_short_hdr] body=[Analysts' mean target price] offsetx=[10] offsety=[20] delay=[300]"><a href="quote.ashx?t=AAPL&ta=1&p=d&ty=fc" class="hover:underline">Target Price</a></td><td class="snapshot-td2 w-[8%] " align="left" style=""><a href="quote.ashx?t=AAPL&ta=1&p=d&ty=fc" class="hover:underline"><b><span class="color-text is-positive">290.38</span></b></a></td>
</tr>
<tr class="table-dark-row">
<td class="snapshot-td2 cursor-pointer w-[7%]" align="left" data-boxover="cssbody=[tooltip_short_bdy] cssheader=[tooltip_short_hdr] body=[Dividend Payout Ratio (ttm)] offsetx=[10] offsety=[20] delay=[300]"><a href="quote.ashx?t=AAPL&ta=1&p=d&ty=dv" class="hover:underline">Payout</a></td><td class="snapshot-td2 w-[8%] " align="left" style=""><a href="quote.ashx?t=AAPL&ta=1&p=d&ty=dv" class="hover:underline"><b>13.66%</b></a></td>
<td class="snapshot-td2 cursor-pointer w-[7%]" align="left" data-boxover="cssbody=[tooltip_short_bdy] cssheader=[tooltip_short_hdr] body=[Total Debt to Equity (mrq)] offsetx=[10] offsety=[20] delay=[300]">Debt/Eq</td><td class="snapshot-td2 w-[8%] " align="left" style=""><b><span class="color-text is-negative">1.52</span></b></td>
<td class="snapshot-td2 cursor-pointer w-[7%]" align="left" data-boxover="cssbody=[tooltip_short_bdy] cssheader=[tooltip_short_hdr] body=[Quarterly revenue growth (YoY)] offsetx=[10] offsety=[20] delay=[300]">Sales Q/Q</td><td class="snapshot-td2 w-[8%] " align="left" style=""><b>7.94%</b></td>
<td class="snapshot-td2 cursor-pointer w-[7%]" align="left" data-boxover="cssbody=[tooltip_short_bdy] cssheader=[tooltip_short_hdr] body=[Distance from 50-Day Simple Moving Average] offsetx=[10] offsety=[20] delay=[300]">SMA50</td><td class="snapshot-td2 w-[8%] " align="left" style=""><b><span class="color-text is-positive">3.89%</span></b></td>
<td class="snapshot-td2 cursor-pointer w-[7%]" align="left" data-boxover="cssbody=[tooltip_short_bdy] cssheader=[tooltip_short_hdr] body=[Relative volume] offsetx=[10] offsety=[20] delay=[300]">Rel Volume</td><td class="snapshot-td2 w-[8%] " align="left" style=""><b>0.78</b></td>
<td class="snapshot-td2 cursor-pointer w-[7%]" align="left" data-boxover="cssbody=[tooltip_short_bdy] cssheader=[tooltip_short_hdr] body=[Previous close] offsetx=[10] offsety=[20] delay=[300]">Prev Close</td><td class="snapshot-td2 w-[8%] " align="left" style=""><b>278.03</b></td>
</tr>
<tr class="table-dark-row">
<td class="snapshot-td2 cursor-pointer w-[7%]" align="left" data-boxover="cssbody=[tooltip_short_bdy] cssheader=[tooltip_short_hdr] body=[Full time employees] offsetx=[10] offsety=[20] delay=[300]">Employees</td><td class="snapshot-td2 w-[8%] " align="left" style=""><b>166000</b></td>
<td class="snapshot-td2 cursor-pointer w-[7%]" align="left" data-boxover="cssbody=[tooltip_short_bdy] cssheader=[tooltip_short_hdr] body=[Long Term Debt to Equity (mrq)] offsetx=[10] offsety=[20] delay=[300]">LT Debt/Eq</td><td class="snapshot-td2 w-[8%] " align="left" style=""><b><span class="color-text is-negative">1.22</span></b></td>
<td class="snapshot-td2 cursor-pointer w-[7%]" align="left" data-boxover="cssbody=[tooltip_short_bdy] cssheader=[tooltip_short_hdr] body=[Earnings date<br><br>BMO = Before Market Open<br>AMC = After Market Close] offsetx=[10] offsety=[20] delay=[300]"><a href="quote.ashx?t=AAPL&ta=1&p=d&ty=ea" class="hover:underline">Earnings</a></td><td class="snapshot-td2 w-[8%] " align="left" style=""><a href="quote.ashx?t=AAPL&ta=1&p=d&ty=ea" class="hover:underline"><b><small class="xl:text-2xs">Oct 30 AMC</small></b></a></td>
<td class="snapshot-td2 cursor-pointer w-[7%]" align="left" data-boxover="cssbody=[tooltip_short_bdy] cssheader=[tooltip_short_hdr] body=[Distance from 200-Day Simple Moving Average] offsetx=[10] offsety=[20] delay=[300]">SMA200</td><td class="snapshot-td2 w-[8%] " align="left" style=""><b><span class="color-text is-positive">21.51%</span></b></td>
<td class="snapshot-td2 cursor-pointer w-[7%]" align="left" data-boxover="cssbody=[tooltip_short_bdy] cssheader=[tooltip_short_hdr] body=[Average volume (3 month)] offsetx=[10] offsety=[20] delay=[300]">Avg Volume</td><td class="snapshot-td2 w-[8%] " align="left" style=""><b>49.22M</b></td>
<td class="snapshot-td2 cursor-pointer w-[7%]" align="left" data-boxover="cssbody=[tooltip_short_bdy] cssheader=[tooltip_short_hdr] body=[Current stock price] offsetx=[10] offsety=[20] delay=[300]">Price</td><td class="snapshot-td2 w-[8%] " align="left" style=""><b>278.28</b></td>
</tr>
<tr class="table-dark-row">
<td class="snapshot-td2 cursor-pointer w-[7%]" align="left" data-boxover="cssbody=[tooltip_short_bdy] cssheader=[tooltip_short_hdr] body=[IPO Date] offsetx=[10] offsety=[20] delay=[300]">IPO</td><td class="snapshot-td2 w-[8%] " align="left" style=""><b>Dec 12, 1980</b></td>
<td class="snapshot-td2 cursor-pointer w-[7%]" align="left" data-boxover="cssbody=[tooltip_short_bdy] cssheader=[tooltip_short_hdr] body=[Stock has options trading on a market exchange / Stock is avaiable to sell short] offsetx=[10] offsety=[20] delay=[300]">Option/Short</td><td class="snapshot-td2 w-[8%] " align="left" style=""><b><small class="xl:text-2xs">Yes / Yes</small></b></td>
<td class="snapshot-td2 cursor-pointer w-[7%]" align="left" data-boxover="cssbody=[tooltip_short_bdy] cssheader=[tooltip_short_hdr] body=[Last quarter EPS and Revenue surprise] offsetx=[10] offsety=[20] delay=[300]"><a href="quote.ashx?t=AAPL&ta=1&p=d&ty=ea" class="hover:underline">EPS/Sales Surpr.</a></td><td class="snapshot-td2 w-[8%] " align="left" style=""><a href="quote.ashx?t=AAPL&ta=1&p=d&ty=ea" class="hover:underline"><b><small class="xl:text-2xs"><span class="color-text is-positive">4.10%</span> <span class="color-text is-positive">0.23%</span></small></b></a></td>
<td class="snapshot-td2 cursor-pointer w-[7%]" align="left" data-boxover="cssbody=[tooltip_short_bdy] cssheader=[tooltip_short_hdr] body=[Trades] offsetx=[10] offsety=[20] delay=[300]">Trades</td><td class="snapshot-td2 w-[8%] " align="left" style=""><a href="/elite?utm_source=finviz&utm_medium=banner&utm_campaign=etf-fundamentals"><svg width="16" height="16" class="text-muted -ml-0.5">
    <use href="/assets/dist-icons/icons.svg?rev=35#lockOutline"/>
</svg></a></td>
<td class="snapshot-td2 cursor-pointer w-[7%]" align="left" data-boxover="cssbody=[tooltip_short_bdy] cssheader=[tooltip_short_hdr] body=[Volume] offsetx=[10] offsety=[20] delay=[300]">Volume</td><td class="snapshot-td2 w-[8%] " align="left" style=""><b>38,442,981</b></td>
<td class="snapshot-td2 cursor-pointer w-[7%]" align="left" data-boxover="cssbody=[tooltip_short_bdy] cssheader=[tooltip_short_hdr] body=[Performance (today)] offsetx=[10] offsety=[20] delay=[300]">Change</td><td class="snapshot-td2 w-[8%] " align="left" style=""><b><span class="color-text is-positive">0.09%</span></b></td>
</tr>
</table>
</div>
</td>
</tr>
</table>
<table width="100%" cellpadding="0" cellspacing="0" border="0">
<tr><td style="height:10px;font-size:0"><img src="gfx/nic2x2.gif" style="width:685px;height:10px"></td></tr>
<tr><td align="center"><div id="IC_D_3x6_1"class="relative overflow-hidden flex items-center justify-center w-full mx-auto" style="width:970px;height:315px;max-height:315px"></div></td></tr><tr><td style="height:10px;font-size:0"><img src="gfx/nic2x2.gif" style="width:685px;height:10px"></td></tr>
<tr class="js-ratings-row">
<td>
<table width="100%" class="js-table-ratings styled-table-new is-rounded is-small" cellpadding="0" cellspacing="0" border="0">
<thead>
                <tr>
                    <th width="140" align="left">Date</th>
                    <th width="320" align="left">Action</th>
                    <th width="320" align="left">Analyst</th>
                    <th width="320" align="left">Rating Change</th>
                    <th width="320" align="left">Price Target Change</th>
                </tr>
            </thead><tr class="styled-row is-hoverable is-bordered is-rounded is-border-top is-hover-borders has-label has-color-text"><td  width="140" align="left">Dec-09-25</td><td width="320" align="left"><span class="fv-label is-small is-neutral">Reiterated</span></td>
<td class="text-left" width="320" align="left">Citigroup</td>
<td class="text-left" width="320" align="left">Buy</td>
<td class="text-left tabular-nums" width="320" align="left">$315 &rarr; $330</td>
</tr>
<tr class="styled-row is-hoverable is-bordered is-rounded is-border-top is-hover-borders has-label has-color-text"><td  width="140" align="left">Dec-08-25</td><td width="320" align="left"><span class="fv-label is-small is-neutral">Reiterated</span></td>
<td class="text-left" width="320" align="left">Wedbush</td>
<td class="text-left" width="320" align="left">Outperform</td>
<td class="text-left tabular-nums" width="320" align="left">$320 &rarr; $350</td>
</tr>
<tr class="styled-row is-hoverable is-bordered is-rounded is-border-top is-hover-borders has-label has-color-text"><td  width="140" align="left">Dec-08-25</td><td width="320" align="left"><span class="fv-label is-small is-neutral">Reiterated</span></td>
<td class="text-left" width="320" align="left">Evercore ISI</td>
<td class="text-left" width="320" align="left">Outperform</td>
<td class="text-left tabular-nums" width="320" align="left">$300 &rarr; $325</td>
</tr>
<tr class="styled-row is-hoverable is-bordered is-rounded is-border-top is-hover-borders has-label has-color-text"><td  width="140" align="left">Dec-05-25</td><td width="320" align="left"><span class="fv-label is-small is-neutral">Reiterated</span></td>
<td class="text-left" width="320" align="left">CLSA</td>
<td class="text-left" width="320" align="left">Outperform</td>
<td class="text-left tabular-nums" width="320" align="left">$265 &rarr; $330</td>
</tr>
<tr class="styled-row is-hoverable is-bordered is-rounded is-border-top is-hover-borders has-label has-color-text"><td  width="140" align="left">Dec-02-25</td><td width="320" align="left"><span class="fv-label is-small is-neutral">Reiterated</span></td>
<td class="text-left" width="320" align="left">Loop Capital</td>
<td class="text-left" width="320" align="left">Buy</td>
<td class="text-left tabular-nums" width="320" align="left">$315 &rarr; $325</td>
</tr>
<tr class="styled-row is-hoverable is-bordered is-rounded is-border-top is-hover-borders has-label has-color-text"><td  width="140" align="left">Nov-04-25</td><td width="320" align="left"><span class="fv-label is-small is-positive-200">Upgrade</span></td>
<td class="text-left color-text is-positive" width="320" align="left">DZ Bank</td>
<td class="text-left color-text is-positive" width="320" align="left">Hold &rarr; Buy</td>
<td class="text-left tabular-nums color-text is-positive" width="320" align="left">$300</td>
</tr>
<tr class="styled-row is-hoverable is-bordered is-rounded is-border-top is-hover-borders has-label has-color-text"><td  width="140" align="left">Nov-03-25</td><td width="320" align="left"><span class="fv-label is-small is-neutral">Reiterated</span></td>
<td class="text-left" width="320" align="left">Barclays</td>
<td class="text-left" width="320" align="left">Underweight</td>
<td class="text-left tabular-nums" width="320" align="left">$180 &rarr; $230</td>
</tr>
<tr class="styled-row is-hoverable is-bordered is-rounded is-border-top is-hover-borders has-label has-color-text"><td  width="140" align="left">Oct-31-25</td><td width="320" align="left"><span class="fv-label is-small is-positive-200">Upgrade</span></td>
<td class="text-left color-text is-positive" width="320" align="left">Jefferies</td>
<td class="text-left color-text is-positive" width="320" align="left">Underperform &rarr; Hold</td>
<td class="text-left tabular-nums color-text is-positive" width="320" align="left">$246.99</td>
</tr>
<tr class="styled-row is-hoverable is-bordered is-rounded is-border-top is-hover-borders has-label has-color-text"><td  width="140" align="left">Oct-31-25</td><td width="320" align="left"><span class="fv-label is-small is-neutral">Reiterated</span></td>
<td class="text-left" width="320" align="left">Wells Fargo</td>
<td class="text-left" width="320" align="left">Overweight</td>
<td class="text-left tabular-nums" width="320" align="left">$290 &rarr; $300</td>
</tr>
<tr class="styled-row is-hoverable is-bordered is-rounded is-border-top is-hover-borders has-label has-color-text is-last"><td  width="140" align="left">Oct-31-25</td><td width="320" align="left"><span class="fv-label is-small is-neutral">Reiterated</span></td>
<td class="text-left" width="320" align="left">UBS</td>
<td class="text-left" width="320" align="left">Neutral</td>
<td class="text-left tabular-nums" width="320" align="left">$220 &rarr; $280</td>
</tr>
<tr class="styled-row is-hoverable is-bordered is-rounded is-border-top is-hover-borders has-label has-color-text hidden"><td  width="140" align="left">Oct-31-25</td><td width="320" align="left"><span class="fv-label is-small is-neutral">Reiterated</span></td>
<td class="text-left" width="320" align="left">TD Cowen</td>
<td class="text-left" width="320" align="left">Buy</td>
<td class="text-left tabular-nums" width="320" align="left">$275 &rarr; $325</td>
</tr>
<tr class="styled-row is-hoverable is-bordered is-rounded is-border-top is-hover-borders has-label has-color-text hidden"><td  width="140" align="left">Oct-31-25</td><td width="320" align="left"><span class="fv-label is-small is-neutral">Reiterated</span></td>
<td class="text-left" width="320" align="left">Robert W. Baird</td>
<td class="text-left" width="320" align="left">Outperform</td>
<td class="text-left tabular-nums" width="320" align="left">$280 &rarr; $300</td>
</tr>
<tr class="styled-row is-hoverable is-bordered is-rounded is-border-top is-hover-borders has-label has-color-text hidden"><td  width="140" align="left">Oct-31-25</td><td width="320" align="left"><span class="fv-label is-small is-neutral">Reiterated</span></td>
<td class="text-left" width="320" align="left">Morgan Stanley</td>
<td class="text-left" width="320" align="left">Overweight</td>
<td class="text-left tabular-nums" width="320" align="left">$298 &rarr; $305</td>
</tr>
<tr class="styled-row is-hoverable is-bordered is-rounded is-border-top is-hover-borders has-label has-color-text hidden"><td  width="140" align="left">Oct-31-25</td><td width="320" align="left"><span class="fv-label is-small is-neutral">Reiterated</span></td>
<td class="text-left" width="320" align="left">Monness Crespi &amp; Hardt</td>
<td class="text-left" width="320" align="left">Buy</td>
<td class="text-left tabular-nums" width="320" align="left">$270 &rarr; $300</td>
</tr>
<tr class="styled-row is-hoverable is-bordered is-rounded is-border-top is-hover-borders has-label has-color-text hidden"><td  width="140" align="left">Oct-31-25</td><td width="320" align="left"><span class="fv-label is-small is-neutral">Reiterated</span></td>
<td class="text-left" width="320" align="left">Melius</td>
<td class="text-left" width="320" align="left">Buy</td>
<td class="text-left tabular-nums" width="320" align="left">$290 &rarr; $345</td>
</tr>
<tr class="styled-row is-hoverable is-bordered is-rounded is-border-top is-hover-borders has-label has-color-text hidden"><td  width="140" align="left">Oct-31-25</td><td width="320" align="left"><span class="fv-label is-small is-neutral">Reiterated</span></td>
<td class="text-left" width="320" align="left">JP Morgan</td>
<td class="text-left" width="320" align="left">Overweight</td>
<td class="text-left tabular-nums" width="320" align="left">$290 &rarr; $305</td>
</tr>
<tr class="styled-row is-hoverable is-bordered is-rounded is-border-top is-hover-borders has-label has-color-text hidden"><td  width="140" align="left">Oct-31-25</td><td width="320" align="left"><span class="fv-label is-small is-neutral">Reiterated</span></td>
<td class="text-left" width="320" align="left">Goldman</td>
<td class="text-left" width="320" align="left">Buy</td>
<td class="text-left tabular-nums" width="320" align="left">$279 &rarr; $320</td>
</tr>
<tr class="styled-row is-hoverable is-bordered is-rounded is-border-top is-hover-borders has-label has-color-text hidden"><td  width="140" align="left">Oct-31-25</td><td width="320" align="left"><span class="fv-label is-small is-neutral">Reiterated</span></td>
<td class="text-left" width="320" align="left">Evercore ISI</td>
<td class="text-left" width="320" align="left">Outperform</td>
<td class="text-left tabular-nums" width="320" align="left">$290 &rarr; $300</td>
</tr>
<tr class="styled-row is-hoverable is-bordered is-rounded is-border-top is-hover-borders has-label has-color-text hidden"><td  width="140" align="left">Oct-31-25</td><td width="320" align="left"><span class="fv-label is-small is-neutral">Reiterated</span></td>
<td class="text-left" width="320" align="left">DA Davidson</td>
<td class="text-left" width="320" align="left">Neutral</td>
<td class="text-left tabular-nums" width="320" align="left">$250 &rarr; $270</td>
</tr>
<tr class="styled-row is-hoverable is-bordered is-rounded is-border-top is-hover-borders has-label has-color-text hidden"><td  width="140" align="left">Oct-31-25</td><td width="320" align="left"><span class="fv-label is-small is-neutral">Reiterated</span></td>
<td class="text-left" width="320" align="left">Citigroup</td>
<td class="text-left" width="320" align="left">Buy</td>
<td class="text-left tabular-nums" width="320" align="left">$245 &rarr; $315</td>
</tr>
</table>
</td>
</tr>
<tr class="js-reveal-ratings-button">
    <td class="fullview-links">
        <a href="" class="tab-link">
            <svg width="16" height="16" class="fill-current inline-block mb-0.5">
    <use href="/assets/dist-icons/icons.svg?rev=35#chevronDown"/>
</svg>
            Show Previous Ratings
        </a>
    </td>
</tr><tr><td style="height:10px;font-size:0"><img src="gfx/nic2x2.gif" style="width:685px;height:10px"></td></tr>
<tr>
<td>
<table width="100%" cellpadding="0" cellspacing="0"><tr><td><div class="body-table-news-wrapper news-table_wrapper"><table width="100%" cellpadding="1" cellspacing="0" border="0" id="news-table" class="fullview-news-outer news-table" data-ticker="AAPL">
    <tr class="cursor-pointer has-label" onclick="trackAndOpenNews(event, 'Motley Fool', '/news/253523/2-stocks-that-turned-1000-into-1-million-or-more');">
        <td width="130" align="right">
            Today 02:25PM
        </td>
        <td align="left">
            <div class="news-link-container">
                <div class="news-link-left">
                    <a class="tab-link-news" href="/news/253523/2-stocks-that-turned-1000-into-1-million-or-more" target="_blank" >2 Stocks That Turned $1,000 Into $1 Million (or More)</a>
                </div>
                <div class="news-link-right">
                    <span>(Motley Fool)</span></div></div></td></tr>
    <tr class="cursor-pointer has-label" onclick="trackAndOpenNews(event, 'Insider Monkey', '/news/253474/jim-explains-why-apple-simply-is-not-a-beneficiary-of-lower-rates');">
        <td width="130" align="right">
            11:17AM
        </td>
        <td align="left">
            <div class="news-link-container">
                <div class="news-link-left">
                    <a class="tab-link-news" href="/news/253474/jim-explains-why-apple-simply-is-not-a-beneficiary-of-lower-rates" target="_blank" >Jim Explains Why "Apple Simply is Not a Beneficiary of Lower Rates"</a>
                </div>
                <div class="news-link-right">
                    <span>(Insider Monkey)</span></div></div></td></tr>
    <tr class="cursor-pointer has-label" onclick="trackAndOpenNews(event, 'MarketBeat', '/news/253397/marketbeat-week-in-review-128-1212');">
        <td width="130" align="right">
            07:00AM
        </td>
        <td align="left">
            <div class="news-link-container">
                <div class="news-link-left">
                    <a class="tab-link-news" href="/news/253397/marketbeat-week-in-review-128-1212" target="_blank" >MarketBeat Week in Review - 12/8 - 12/12</a>
                </div>
                <div class="news-link-right">
                    <span>(MarketBeat)</span></div></div></td></tr>
    <tr class="cursor-pointer has-label" onclick="trackAndOpenNews(event, 'Motley Fool', '/news/253389/warren-buffetts-biggest-artificial-intelligence-bets-in-2026-23-of-berkshire-hathaways-311-billion-stock-portfolio-is-in-these-2-ai-stocks');">
        <td width="130" align="right">
            05:50AM
        </td>
        <td align="left">
            <div class="news-link-container">
                <div class="news-link-left">
                    <a class="tab-link-news" href="/news/253389/warren-buffetts-biggest-artificial-intelligence-bets-in-2026-23-of-berkshire-hathaways-311-billion-stock-portfolio-is-in-these-2-ai-stocks" target="_blank" >Warren Buffett's Biggest Artificial Intelligence Bets in 2026: 23% of Berkshire Hathaway's $311 Billion Stock Portfolio Is in These 2 AI Stocks</a>
                </div>
                <div class="news-link-right">
                    <span>(Motley Fool)</span></div></div></td></tr>
    <tr class="cursor-pointer has-label" onclick="trackAndOpenNews(event, 'Motley Fool', '/news/253374/these-3-warren-buffett-ai-stocks-could-be-big-winners-in-2026');">
        <td width="130" align="right">
            04:03AM
        </td>
        <td align="left">
            <div class="news-link-container">
                <div class="news-link-left">
                    <a class="tab-link-news" href="/news/253374/these-3-warren-buffett-ai-stocks-could-be-big-winners-in-2026" target="_blank" >These 3 Warren Buffett AI Stocks Could Be Big Winners in 2026</a>
                </div>
                <div class="news-link-right">
                    <span>(Motley Fool)</span></div></div></td></tr>

                    <tr>
                        <td width="130" align="right">01:20AM</td>
                        <td align="left" id="IC_D_3x8_1"><span class="block text-2xs text-gray-500 leading-none">Loading…</span></td>
                    </tr>
                  <tr class="cursor-pointer has-label" onclick="trackAndOpenNews(event, 'Motley Fool', '/news/253370/heres-my-top-magnificent-seven-stock-to-buy-for-2026');">
        <td width="130" align="right">
            01:20AM
        </td>
        <td align="left">
            <div class="news-link-container">
                <div class="news-link-left">
                    <a class="tab-link-news" href="/news/253370/heres-my-top-magnificent-seven-stock-to-buy-for-2026" target="_blank" >Here's My Top "Magnificent Seven" Stock to Buy for 2026</a>
                </div>
                <div class="news-link-right">
                    <span>(Motley Fool)</span></div></div></td></tr>
    <tr class="cursor-pointer has-label" onclick="trackAndOpenNews(event, 'TechCrunch', 'https://finance.yahoo.com/news/comprehensive-list-2025-tech-layoffs-134836336.html');">
        <td width="130" align="right">
            Dec-12-25 07:11PM
        </td>
        <td align="left">
            <div class="news-link-container">
                <div class="news-link-left">
                    <a class="tab-link-news" href="https://finance.yahoo.com/news/comprehensive-list-2025-tech-layoffs-134836336.html" target="_blank" rel="nofollow">A comprehensive list of 2025 tech layoffs</a>
                </div>
                <div class="news-link-right">
                    <span>(TechCrunch)</span></div></div></td></tr>
    <tr class="cursor-pointer has-label" onclick="trackAndOpenNews(event, '24/7 Wall St.', 'https://finance.yahoo.com/m/6f0cc380-bee8-3127-99a9-ae88432c2eab/my-tune-is-changing-on-apple.html');">
        <td width="130" align="right">
            07:05PM
        </td>
        <td align="left">
            <div class="news-link-container">
                <div class="news-link-left">
                    <a class="tab-link-news" href="https://finance.yahoo.com/m/6f0cc380-bee8-3127-99a9-ae88432c2eab/my-tune-is-changing-on-apple.html" target="_blank" rel="nofollow">My Tune Is Changing On Apple In 2026: Heres Why</a>
                </div>
                <div class="news-link-right">
                    <span>(24/7 Wall St.)</span></div></div></td></tr>
    <tr class="cursor-pointer has-label" onclick="trackAndOpenNews(event, 'Barrons.com', 'https://www.barrons.com/articles/best-dividend-etf-2026-9008a2c1?mod=bar_FV');">
        <td width="130" align="right">
            03:45PM
        </td>
        <td align="left">
            <div class="news-link-container">
                <div class="news-link-left">
                    <a class="tab-link-news" href="https://www.barrons.com/articles/best-dividend-etf-2026-9008a2c1?mod=bar_FV" target="_blank" rel="nofollow">The Best Dividend ETF for Right Now-and 2026</a>
                </div>
                <div class="news-link-right">
                    <span>(Barrons.com)</span></div></div></td></tr>
    <tr class="cursor-pointer has-label" onclick="trackAndOpenNews(event, 'GuruFocus.com', 'https://finance.yahoo.com/news/apple-wins-partial-reversal-sanctions-185907720.html');">
        <td width="130" align="right">
            01:59PM
        </td>
        <td align="left">
            <div class="news-link-container">
                <div class="news-link-left">
                    <a class="tab-link-news" href="https://finance.yahoo.com/news/apple-wins-partial-reversal-sanctions-185907720.html" target="_blank" rel="nofollow">Apple Wins Partial Reversal of Sanctions in Epic Games Antitrust Case</a>
                </div>
                <div class="news-link-right">
                    <span>(GuruFocus.com)</span></div></div></td></tr>
    <tr class="cursor-pointer has-label" onclick="trackAndOpenNews(event, 'Barrons.com', 'https://finance.yahoo.com/m/3ea5aaef-7ef1-32f3-90c1-2957098bd7de/who-is-broadcom%E2%80%99s-mystery.html');">
        <td width="130" align="right">
            12:39PM
        </td>
        <td align="left">
            <div class="news-link-container">
                <div class="news-link-left">
                    <a class="tab-link-news" href="https://finance.yahoo.com/m/3ea5aaef-7ef1-32f3-90c1-2957098bd7de/who-is-broadcom%E2%80%99s-mystery.html" target="_blank" rel="nofollow">Who Is Broadcoms Mystery Customer? Wall Street Has Some Guesses.</a>
                </div>
                <div class="news-link-right">
                    <span>(Barrons.com)</span></div></div></td></tr>
    <tr class="cursor-pointer has-label" onclick="trackAndOpenNews(event, 'Barrons.com', 'https://www.barrons.com/articles/broadcom-stock-earnings-ai-chips-customer-d15c2da8?mod=bar_FV');">
        <td width="130" align="right">
            12:39PM
        </td>
        <td align="left">
            <div class="news-link-container">
                <div class="news-link-left">
                    <a class="tab-link-news" href="https://www.barrons.com/articles/broadcom-stock-earnings-ai-chips-customer-d15c2da8?mod=bar_FV" target="_blank" rel="nofollow">Broadcom Stock Crumbles as Wall Street Makes Guesses About Mystery Customer</a>
                </div>
                <div class="news-link-right">
                    <span>(Barrons.com)</span></div></div></td></tr>
    <tr class="cursor-pointer has-label" onclick="trackAndOpenNews(event, 'MarketWatch', 'https://www.marketwatch.com/livecoverage/stock-market-today-dow-set-to-rise-as-investors-eye-value-over-growth-after-fed-cut/card/big-tech-etf-falls-on-pace-for-weekly-slump-Fd3u855v3tMw2rncN8qV?mod=mw_FV');">
        <td width="130" align="right">
            12:29PM
        </td>
        <td align="left">
            <div class="news-link-container">
                <div class="news-link-left">
                    <a class="tab-link-news" href="https://www.marketwatch.com/livecoverage/stock-market-today-dow-set-to-rise-as-investors-eye-value-over-growth-after-fed-cut/card/big-tech-etf-falls-on-pace-for-weekly-slump-Fd3u855v3tMw2rncN8qV?mod=mw_FV" target="_blank" rel="nofollow">Big Tech ETF falls, on pace for weekly slump</a>
                </div>
                <div class="news-link-right">
                    <span>(MarketWatch)</span></div></div></td></tr>
    <tr class="cursor-pointer has-label" onclick="trackAndOpenNews(event, 'Fortune', 'https://finance.yahoo.com/news/apple-ceo-tim-cook-earns-162949480.html');">
        <td width="130" align="right">
            11:29AM
        </td>
        <td align="left">
            <div class="news-link-container">
                <div class="news-link-left">
                    <a class="tab-link-news" href="https://finance.yahoo.com/news/apple-ceo-tim-cook-earns-162949480.html" target="_blank" rel="nofollow">Apple CEO Tim Cook out-earns the average Americans salary in just 7 hoursto put that into context, he could buy a new $439,000 home in just 2 days</a>
                </div>
                <div class="news-link-right">
                    <span>(Fortune)</span></div></div></td></tr>
    <tr class="cursor-pointer has-label" onclick="trackAndOpenNews(event, 'GuruFocus.com', 'https://finance.yahoo.com/news/inside-asmls-430-billion-ai-161944689.html');">
        <td width="130" align="right">
            11:19AM
        </td>
        <td align="left">
            <div class="news-link-container">
                <div class="news-link-left">
                    <a class="tab-link-news" href="https://finance.yahoo.com/news/inside-asmls-430-billion-ai-161944689.html" target="_blank" rel="nofollow">Inside ASML's $430 Billion AI Monopoly: The Chipmaker Even Nvidia Can't Live Without</a>
                </div>
                <div class="news-link-right">
                    <span>(GuruFocus.com)</span></div></div></td></tr>

                    <tr>
                        <td width="130" align="right">11:08AM</td>
                        <td align="left" id="IC_D_3x8_2"><span class="block text-2xs text-gray-500 leading-none">Loading…</span></td>
                    </tr>
                  <tr class="cursor-pointer has-label" onclick="trackAndOpenNews(event, 'Investor\u0027s Business Daily', 'https://finance.yahoo.com/m/4205eaa9-f620-3a0b-a81a-0e82c7c9fd0b/magnificent-seven-stocks%3A.html');">
        <td width="130" align="right">
            11:08AM
        </td>
        <td align="left">
            <div class="news-link-container">
                <div class="news-link-left">
                    <a class="tab-link-news" href="https://finance.yahoo.com/m/4205eaa9-f620-3a0b-a81a-0e82c7c9fd0b/magnificent-seven-stocks%3A.html" target="_blank" rel="nofollow">Magnificent Seven Stocks: Nvidia Sells Off; Tesla Reverses Lower</a>
                </div>
                <div class="news-link-right">
                    <span>(Investor's Business Daily)</span></div></div></td></tr>
    <tr class="cursor-pointer has-label" onclick="trackAndOpenNews(event, 'GuruFocus.com', 'https://finance.yahoo.com/news/apple-wins-partial-relief-epic-160107107.html');">
        <td width="130" align="right">
            11:01AM
        </td>
        <td align="left">
            <div class="news-link-container">
                <div class="news-link-left">
                    <a class="tab-link-news" href="https://finance.yahoo.com/news/apple-wins-partial-relief-epic-160107107.html" target="_blank" rel="nofollow">Apple Wins Partial Relief in Epic Appeals Ruling</a>
                </div>
                <div class="news-link-right">
                    <span>(GuruFocus.com)</span></div></div></td></tr>
    <tr class="cursor-pointer has-label" onclick="trackAndOpenNews(event, 'Fortune', 'https://finance.yahoo.com/news/apple-cofounder-ronald-wayne-sold-145828967.html');">
        <td width="130" align="right">
            09:58AM
        </td>
        <td align="left">
            <div class="news-link-container">
                <div class="news-link-left">
                    <a class="tab-link-news" href="https://finance.yahoo.com/news/apple-cofounder-ronald-wayne-sold-145828967.html" target="_blank" rel="nofollow">Apple cofounder Ronald Wayne sold his 10% stake for $800 in 1976today itd be worth up to $400 billion</a>
                </div>
                <div class="news-link-right">
                    <span>(Fortune)</span></div></div></td></tr>
    <tr class="cursor-pointer has-label" onclick="trackAndOpenNews(event, 'Zacks', '/news/252981/after-a-42-six-month-rally-whats-next-for-apple-stock-in-2026');">
        <td width="130" align="right">
            09:57AM
        </td>
        <td align="left">
            <div class="news-link-container">
                <div class="news-link-left">
                    <a class="tab-link-news" href="/news/252981/after-a-42-six-month-rally-whats-next-for-apple-stock-in-2026" target="_blank" >After a 42% Six-Month Rally, What's Next for Apple Stock in 2026?</a>
                </div>
                <div class="news-link-right">
                    <span>(Zacks)</span></div></div></td></tr>
    <tr class="cursor-pointer has-label" onclick="trackAndOpenNews(event, 'Investor\u0027s Business Daily', 'https://finance.yahoo.com/m/d47724df-cef1-316a-90ff-29627f1cafc9/stock-market-today%3A-dow-rises.html');">
        <td width="130" align="right">
            08:47AM
        </td>
        <td align="left">
            <div class="news-link-container">
                <div class="news-link-left">
                    <a class="tab-link-news" href="https://finance.yahoo.com/m/d47724df-cef1-316a-90ff-29627f1cafc9/stock-market-today%3A-dow-rises.html" target="_blank" rel="nofollow">Stock Market Today: Dow Rises But Nasdaq, AI Stocks Falter As Broadcom Plunges On Earnings (Live Coverage)</a>
                </div>
                <div class="news-link-right">
                    <span>(Investor's Business Daily)</span></div></div></td></tr>
    <tr class="cursor-pointer has-label" onclick="trackAndOpenNews(event, 'Barrons.com', 'https://finance.yahoo.com/m/8136fc55-1905-3a16-a312-d2acb868099e/magnificent-7-dominance.html');">
        <td width="130" align="right">
            07:29AM
        </td>
        <td align="left">
            <div class="news-link-container">
                <div class="news-link-left">
                    <a class="tab-link-news" href="https://finance.yahoo.com/m/8136fc55-1905-3a16-a312-d2acb868099e/magnificent-7-dominance.html" target="_blank" rel="nofollow">Magnificent 7 Dominance Expected Again in 2026, Goldman Says, but a  Broadening Trade Is Starting</a>
                </div>
                <div class="news-link-right">
                    <span>(Barrons.com)</span></div></div></td></tr>
    <tr class="cursor-pointer has-label" onclick="trackAndOpenNews(event, 'Barrons.com', 'https://www.barrons.com/articles/mag-7-stock-trade-goldman-forecast-afcb6146?mod=bar_FV');">
        <td width="130" align="right">
            07:29AM
        </td>
        <td align="left">
            <div class="news-link-container">
                <div class="news-link-left">
                    <a class="tab-link-news" href="https://www.barrons.com/articles/mag-7-stock-trade-goldman-forecast-afcb6146?mod=bar_FV" target="_blank" rel="nofollow">Mag 7 Stocks Still Dominate, Goldman Says. That Could Change Soon.</a>
                </div>
                <div class="news-link-right">
                    <span>(Barrons.com)</span></div></div></td></tr>
    <tr class="cursor-pointer has-label" onclick="trackAndOpenNews(event, 'CoinDesk', 'https://finance.yahoo.com/m/fa4265a5-a841-3b37-97aa-d7aaea29cb93/youtube-now-allows-u.s..html');">
        <td width="130" align="right">
            07:05AM
        </td>
        <td align="left">
            <div class="news-link-container">
                <div class="news-link-left">
                    <a class="tab-link-news" href="https://finance.yahoo.com/m/fa4265a5-a841-3b37-97aa-d7aaea29cb93/youtube-now-allows-u.s..html" target="_blank" rel="nofollow">YouTube Now Allows U.S. Content Creators to Get Paid in PayPals Stablecoin: Fortune</a>
                </div>
                <div class="news-link-right">
                    <span>(CoinDesk)</span></div></div></td></tr>
    <tr class="cursor-pointer has-label" onclick="trackAndOpenNews(event, 'Yahoo Finance Video', 'https://finance.yahoo.com/video/big-tech-stocks-even-bigger-120009049.html');">
        <td width="130" align="right">
            07:00AM
        </td>
        <td align="left">
            <div class="news-link-container">
                <div class="news-link-left">
                    <a class="tab-link-news" href="https://finance.yahoo.com/video/big-tech-stocks-even-bigger-120009049.html" target="_blank" rel="nofollow">Which Big Tech stocks will be even bigger winners in 10 years?</a>
                </div>
                <div class="news-link-right">
                    <span>(Yahoo Finance Video)</span></div></div></td></tr>
    <tr class="cursor-pointer has-label" onclick="trackAndOpenNews(event, 'Bloomberg', 'https://finance.yahoo.com/news/goldman-snider-sees-ai-strong-104637063.html');">
        <td width="130" align="right">
            05:46AM
        </td>
        <td align="left">
            <div class="news-link-container">
                <div class="news-link-left">
                    <a class="tab-link-news" href="https://finance.yahoo.com/news/goldman-snider-sees-ai-strong-104637063.html" target="_blank" rel="nofollow">Goldmans Snider Sees AI, Strong Macro Driving 12% Earnings Jump</a>
                </div>
                <div class="news-link-right">
                    <span>(Bloomberg)</span></div></div></td></tr>
    <tr class="cursor-pointer has-label" onclick="trackAndOpenNews(event, 'Motley Fool', '/news/252503/3-brilliant-growth-stocks-to-buy-now-and-hold-for-the-long-term');">
        <td width="130" align="right">
            03:04AM
        </td>
        <td align="left">
            <div class="news-link-container">
                <div class="news-link-left">
                    <a class="tab-link-news" href="/news/252503/3-brilliant-growth-stocks-to-buy-now-and-hold-for-the-long-term" target="_blank" >3 Brilliant Growth Stocks to Buy Now and Hold for the Long Term</a>
                </div>
                <div class="news-link-right">
                    <span>(Motley Fool)</span></div></div></td></tr>
    <tr class="cursor-pointer has-label" onclick="trackAndOpenNews(event, 'Motley Fool', '/news/252498/prediction-this-could-be-the-worlds-most-valuable-stock-in-2026-according-to-1-wall-street-analyst-hint-not-nvidia');">
        <td width="130" align="right">
            02:20AM
        </td>
        <td align="left">
            <div class="news-link-container">
                <div class="news-link-left">
                    <a class="tab-link-news" href="/news/252498/prediction-this-could-be-the-worlds-most-valuable-stock-in-2026-according-to-1-wall-street-analyst-hint-not-nvidia" target="_blank" >Prediction: This Could Be the World's Most Valuable Stock in 2026, According to 1 Wall Street Analyst (Hint: Not Nvidia)</a>
                </div>
                <div class="news-link-right">
                    <span>(Motley Fool)</span></div></div></td></tr>
    <tr class="cursor-pointer has-label" onclick="trackAndOpenNews(event, 'StockStory', '/news/252926/2-sp-500-stocks-with-competitive-advantages-and-1-we-question');">
        <td width="130" align="right">
            Dec-11-25 11:32PM
        </td>
        <td align="left">
            <div class="news-link-container">
                <div class="news-link-left">
                    <a class="tab-link-news" href="/news/252926/2-sp-500-stocks-with-competitive-advantages-and-1-we-question" target="_blank" >2 S&amp;P 500 Stocks with Competitive Advantages and 1 We Question</a>
                </div>
                <div class="news-link-right">
                    <span>(StockStory)</span></div></div></td></tr>
    <tr class="cursor-pointer has-label" onclick="trackAndOpenNews(event, 'Motley Fool', '/news/252471/warren-buffett-is-dumping-apple-and-bank-of-america-shares-and-buying-this-red-hot-ai-stock-to-end-2025');">
        <td width="130" align="right">
            10:50PM
        </td>
        <td align="left">
            <div class="news-link-container">
                <div class="news-link-left">
                    <a class="tab-link-news" href="/news/252471/warren-buffett-is-dumping-apple-and-bank-of-america-shares-and-buying-this-red-hot-ai-stock-to-end-2025" target="_blank" >Warren Buffett Is Dumping Apple and Bank of America Shares and Buying This Red-Hot AI Stock to End 2025</a>
                </div>
                <div class="news-link-right">
                    <span>(Motley Fool)</span></div></div></td></tr>
    <tr class="cursor-pointer has-label" onclick="trackAndOpenNews(event, 'Associated Press Finance', 'https://finance.yahoo.com/news/appeals-court-backs-contempt-finding-011715250.html');">
        <td width="130" align="right">
            08:17PM
        </td>
        <td align="left">
            <div class="news-link-container">
                <div class="news-link-left">
                    <a class="tab-link-news" href="https://finance.yahoo.com/news/appeals-court-backs-contempt-finding-011715250.html" target="_blank" rel="nofollow">Appeals court backs contempt finding against Apple, but reopens a door for iPhone app fees</a>
                </div>
                <div class="news-link-right">
                    <span>(Associated Press Finance)</span></div></div></td></tr>

                    <tr>
                        <td width="130" align="right">05:39PM</td>
                        <td align="left" id="IC_D_3x8_3"><span class="block text-2xs text-gray-500 leading-none">Loading…</span></td>
                    </tr>
                  <tr class="cursor-pointer has-label" onclick="trackAndOpenNews(event, 'MarketBeat', '/news/252365/the-chip-boom-is-back-3-stocks-positioned-for-huge-gains');">
        <td width="130" align="right">
            05:39PM
        </td>
        <td align="left">
            <div class="news-link-container">
                <div class="news-link-left">
                    <a class="tab-link-news" href="/news/252365/the-chip-boom-is-back-3-stocks-positioned-for-huge-gains" target="_blank" >The Chip Boom Is Back: 3 Stocks Positioned for Huge Gains</a>
                </div>
                <div class="news-link-right">
                    <span>(MarketBeat)</span></div></div></td></tr>
    <tr class="cursor-pointer has-label" onclick="trackAndOpenNews(event, 'Barrons.com', 'https://www.barrons.com/articles/s-p-500-market-cap-revenue-etf-f079e636?mod=bar_FV');">
        <td width="130" align="right">
            02:50PM
        </td>
        <td align="left">
            <div class="news-link-container">
                <div class="news-link-left">
                    <a class="tab-link-news" href="https://www.barrons.com/articles/s-p-500-market-cap-revenue-etf-f079e636?mod=bar_FV" target="_blank" rel="nofollow">Look Past the S&amp;P 500's Market Cap and Focus on Revenue Instead</a>
                </div>
                <div class="news-link-right">
                    <span>(Barrons.com)</span></div></div></td></tr>
    <tr class="cursor-pointer has-label" onclick="trackAndOpenNews(event, 'Investing.com', 'https://finance.yahoo.com/news/deepwater-ai-bull-run-continues-190025339.html');">
        <td width="130" align="right">
            02:00PM
        </td>
        <td align="left">
            <div class="news-link-container">
                <div class="news-link-left">
                    <a class="tab-link-news" href="https://finance.yahoo.com/news/deepwater-ai-bull-run-continues-190025339.html" target="_blank" rel="nofollow">Deepwater: AI bull run continues in 2026; small cap tech to outperform</a>
                </div>
                <div class="news-link-right">
                    <span>(Investing.com)</span></div></div></td></tr>
    <tr class="cursor-pointer has-label" onclick="trackAndOpenNews(event, 'Insider Monkey', '/news/251974/ubs-reiterates-neutral-on-apple-aapl-as-app-store-growth-slows');">
        <td width="130" align="right">
            11:23AM
        </td>
        <td align="left">
            <div class="news-link-container">
                <div class="news-link-left">
                    <a class="tab-link-news" href="/news/251974/ubs-reiterates-neutral-on-apple-aapl-as-app-store-growth-slows" target="_blank" >UBS Reiterates Neutral on Apple (AAPL) as App Store Growth Slows</a>
                </div>
                <div class="news-link-right">
                    <span>(Insider Monkey)</span></div></div></td></tr>
    <tr class="cursor-pointer has-label" onclick="trackAndOpenNews(event, 'Motley Fool', '/news/251842/market-volatility-and-opportunities');">
        <td width="130" align="right">
            10:19AM
        </td>
        <td align="left">
            <div class="news-link-container">
                <div class="news-link-left">
                    <a class="tab-link-news" href="/news/251842/market-volatility-and-opportunities" target="_blank" >Market Volatility and Opportunities</a>
                </div>
                <div class="news-link-right">
                    <span>(Motley Fool)</span></div></div></td></tr>
    <tr class="cursor-pointer has-label" onclick="trackAndOpenNews(event, 'Zacks', '/news/251958/is-mp-stock-a-buy-hold-or-sell-after-its-989-six-month-rally');">
        <td width="130" align="right">
            10:05AM
        </td>
        <td align="left">
            <div class="news-link-container">
                <div class="news-link-left">
                    <a class="tab-link-news" href="/news/251958/is-mp-stock-a-buy-hold-or-sell-after-its-989-six-month-rally" target="_blank" >Is MP Stock a Buy, Hold or Sell After Its 98.9% Six-Month Rally?</a>
                </div>
                <div class="news-link-right">
                    <span>(Zacks)</span></div></div></td></tr>
    <tr class="cursor-pointer has-label" onclick="trackAndOpenNews(event, 'Insider Monkey', '/news/251531/jim-cramer-on-apple-bulls-like-me-were-considered-dreamers-or-even-heretics');">
        <td width="130" align="right">
            07:56AM
        </td>
        <td align="left">
            <div class="news-link-container">
                <div class="news-link-left">
                    <a class="tab-link-news" href="/news/251531/jim-cramer-on-apple-bulls-like-me-were-considered-dreamers-or-even-heretics" target="_blank" >Jim Cramer on Apple: "Bulls Like Me Were Considered Dreamers or Even Heretics"</a>
                </div>
                <div class="news-link-right">
                    <span>(Insider Monkey)</span></div></div></td></tr>
    <tr class="cursor-pointer has-label" onclick="trackAndOpenNews(event, 'GuruFocus.com', 'https://finance.yahoo.com/news/apples-tim-cook-urges-lawmakers-114310535.html');">
        <td width="130" align="right">
            06:43AM
        </td>
        <td align="left">
            <div class="news-link-container">
                <div class="news-link-left">
                    <a class="tab-link-news" href="https://finance.yahoo.com/news/apples-tim-cook-urges-lawmakers-114310535.html" target="_blank" rel="nofollow">Apple's Tim Cook Urges Lawmakers to Rethink App Store Accountability Act</a>
                </div>
                <div class="news-link-right">
                    <span>(GuruFocus.com)</span></div></div></td></tr>
    <tr class="cursor-pointer has-label" onclick="trackAndOpenNews(event, 'Fortune', 'https://finance.yahoo.com/news/business-leaders-2026-predictions-magnificent-105810045.html');">
        <td width="130" align="right">
            05:58AM
        </td>
        <td align="left">
            <div class="news-link-container">
                <div class="news-link-left">
                    <a class="tab-link-news" href="https://finance.yahoo.com/news/business-leaders-2026-predictions-magnificent-105810045.html" target="_blank" rel="nofollow">Business leaders make their 2026 predictions for the Magnificent 7: Id rather be in Jensens seat than anywhere else</a>
                </div>
                <div class="news-link-right">
                    <span>(Fortune)</span></div></div></td></tr>
    <tr class="cursor-pointer has-label" onclick="trackAndOpenNews(event, 'Insider Monkey', '/news/251296/ubs-reiterates-neutral-on-apple-aapl-as-interest-in-apple-intelligence-and-foldables-rises');">
        <td width="130" align="right">
            04:38AM
        </td>
        <td align="left">
            <div class="news-link-container">
                <div class="news-link-left">
                    <a class="tab-link-news" href="/news/251296/ubs-reiterates-neutral-on-apple-aapl-as-interest-in-apple-intelligence-and-foldables-rises" target="_blank" >UBS Reiterates Neutral on Apple (AAPL) as Interest in Apple Intelligence and Foldables Rises</a>
                </div>
                <div class="news-link-right">
                    <span>(Insider Monkey)</span></div></div></td></tr>
    <tr class="cursor-pointer has-label" onclick="trackAndOpenNews(event, 'South China Morning Post', 'https://finance.yahoo.com/news/apple-takes-chinas-smartphone-battle-093000380.html');">
        <td width="130" align="right">
            04:30AM
        </td>
        <td align="left">
            <div class="news-link-container">
                <div class="news-link-left">
                    <a class="tab-link-news" href="https://finance.yahoo.com/news/apple-takes-chinas-smartphone-battle-093000380.html" target="_blank" rel="nofollow">Apple takes China's smartphone battle house to house with free 3-hour iPhone delivery</a>
                </div>
                <div class="news-link-right">
                    <span>(South China Morning Post)</span></div></div></td></tr>
    <tr class="cursor-pointer has-label" onclick="trackAndOpenNews(event, 'Motley Fool', '/news/251262/the-best-warren-buffett-stocks-to-buy-with-10000-right-now');">
        <td width="130" align="right">
            02:25AM
        </td>
        <td align="left">
            <div class="news-link-container">
                <div class="news-link-left">
                    <a class="tab-link-news" href="/news/251262/the-best-warren-buffett-stocks-to-buy-with-10000-right-now" target="_blank" >The Best Warren Buffett Stocks to Buy With $10,000 Right Now</a>
                </div>
                <div class="news-link-right">
                    <span>(Motley Fool)</span></div></div></td></tr>
    <tr class="cursor-pointer has-label" onclick="trackAndOpenNews(event, 'CorpGov.com', 'https://finance.yahoo.com/m/3eb44b04-a32d-36e0-8cee-e857da7e75ab/the-dealmaking-3-%E2%80%93.html');">
        <td width="130" align="right">
            Dec-10-25 05:58PM
        </td>
        <td align="left">
            <div class="news-link-container">
                <div class="news-link-left">
                    <a class="tab-link-news" href="https://finance.yahoo.com/m/3eb44b04-a32d-36e0-8cee-e857da7e75ab/the-dealmaking-3-%E2%80%93.html" target="_blank" rel="nofollow">The Dealmaking 3  GameChangers, Track Titan, Surging Sports-Tech Industry</a>
                </div>
                <div class="news-link-right">
                    <span>(CorpGov.com)</span></div></div></td></tr>
    <tr class="cursor-pointer has-label" onclick="trackAndOpenNews(event, 'Investor\u0027s Business Daily', 'https://finance.yahoo.com/m/6a8dc9d7-e276-3ac9-802b-3345cd107149/taiwan-semiconductor-stock.html');">
        <td width="130" align="right">
            05:36PM
        </td>
        <td align="left">
            <div class="news-link-container">
                <div class="news-link-left">
                    <a class="tab-link-news" href="https://finance.yahoo.com/m/6a8dc9d7-e276-3ac9-802b-3345cd107149/taiwan-semiconductor-stock.html" target="_blank" rel="nofollow">Taiwan Semiconductor Stock Hits Buy Point After Sales Report</a>
                </div>
                <div class="news-link-right">
                    <span>(Investor's Business Daily)</span></div></div></td></tr>
    <tr class="cursor-pointer has-label" onclick="trackAndOpenNews(event, 'CNBC TV', 'https://www.youtube.com/shorts/VHXiUr47LKY');">
        <td width="130" align="right">
            04:28PM
        </td>
        <td align="left">
            <div class="news-link-container">
                <div class="news-link-left">
                    <a class="tab-link-news" href="https://www.youtube.com/shorts/VHXiUr47LKY" target="_blank" rel="nofollow">Apple CEO Tim Cook meets lawmakers to discuss online safety bill for kids</a>
                </div>
                <div class="news-link-right">
                    <span>(CNBC TV)</span></div></div></td></tr>
    <tr class="cursor-pointer has-label" onclick="trackAndOpenNews(event, 'Barchart', 'https://finance.yahoo.com/m/20ce1dc6-0884-32ec-a20b-0dc19cff105b/evercore-analysts-are.html');">
        <td width="130" align="right">
            03:17PM
        </td>
        <td align="left">
            <div class="news-link-container">
                <div class="news-link-left">
                    <a class="tab-link-news" href="https://finance.yahoo.com/m/20ce1dc6-0884-32ec-a20b-0dc19cff105b/evercore-analysts-are.html" target="_blank" rel="nofollow">Evercore Analysts Are Pounding the Table on Apple Stock Ahead of a Sizable Catalyst Coming in 2026</a>
                </div>
                <div class="news-link-right">
                    <span>(Barchart)</span></div></div></td></tr>
    <tr class="cursor-pointer has-label" onclick="trackAndOpenNews(event, 'Fortune', 'https://finance.yahoo.com/news/jeff-williams-retired-apple-27-192406268.html');">
        <td width="130" align="right">
            02:24PM
        </td>
        <td align="left">
            <div class="news-link-container">
                <div class="news-link-left">
                    <a class="tab-link-news" href="https://finance.yahoo.com/news/jeff-williams-retired-apple-27-192406268.html" target="_blank" rel="nofollow">Jeff Williams, who retired from Apple after 27 years less than a month ago, just got called up by Disney to join its board of directors</a>
                </div>
                <div class="news-link-right">
                    <span>(Fortune)</span></div></div></td></tr>
    <tr class="cursor-pointer has-label" onclick="trackAndOpenNews(event, 'Above Avalon', 'https://www.aboveavalon.com/notes/2025/12/10/is-that-a-case-on-your-iphone-avalon-podcast-episode');">
        <td width="130" align="right">
            02:11PM
        </td>
        <td align="left">
            <div class="news-link-container">
                <div class="news-link-left">
                    <a class="tab-link-news" href="https://www.aboveavalon.com/notes/2025/12/10/is-that-a-case-on-your-iphone-avalon-podcast-episode" target="_blank" rel="nofollow">Is That a Case on Your iPhone? (AVALON Podcast Episode)</a>
                </div>
                <div class="news-link-right">
                    <span>(Above Avalon)</span></div></div></td></tr>
    <tr class="cursor-pointer has-label" onclick="trackAndOpenNews(event, 'Above Avalon', 'https://www.aboveavalon.com/notes/2025/11/19/what-if-we-spread-this-process-out');">
        <td width="130" align="right">
            02:05PM
        </td>
        <td align="left">
            <div class="news-link-container">
                <div class="news-link-left">
                    <a class="tab-link-news" href="https://www.aboveavalon.com/notes/2025/11/19/what-if-we-spread-this-process-out" target="_blank" rel="nofollow">What if We Spread This Process Out (AVALON Podcast Episode)</a>
                </div>
                <div class="news-link-right">
                    <span>(Above Avalon)</span></div></div></td></tr>
    <tr class="cursor-pointer has-label" onclick="trackAndOpenNews(event, 'Bloomberg', 'https://finance.yahoo.com/news/apple-cook-presses-us-lawmakers-175644735.html');">
        <td width="130" align="right">
            01:52PM
        </td>
        <td align="left">
            <div class="news-link-container">
                <div class="news-link-left">
                    <a class="tab-link-news" href="https://finance.yahoo.com/news/apple-cook-presses-us-lawmakers-175644735.html" target="_blank" rel="nofollow">Apples Cook Presses Congress Over Child Online Safety Bill</a>
                </div>
                <div class="news-link-right">
                    <span>(Bloomberg)</span></div></div></td></tr>
    <tr class="cursor-pointer has-label" onclick="trackAndOpenNews(event, '24/7 Wall St.', 'https://finance.yahoo.com/m/06520e0c-21ae-385c-808c-9cd85771546e/forget-monthly-dividends%2C.html');">
        <td width="130" align="right">
            01:26PM
        </td>
        <td align="left">
            <div class="news-link-container">
                <div class="news-link-left">
                    <a class="tab-link-news" href="https://finance.yahoo.com/m/06520e0c-21ae-385c-808c-9cd85771546e/forget-monthly-dividends%2C.html" target="_blank" rel="nofollow">Forget Monthly Dividends, These 5 ETFs Pay Investors Every Week</a>
                </div>
                <div class="news-link-right">
                    <span>(24/7 Wall St.)</span></div></div></td></tr>
    <tr class="cursor-pointer has-label" onclick="trackAndOpenNews(event, 'Yahoo Finance Video', 'https://finance.yahoo.com/video/apples-tim-cook-reportedly-capitol-181349594.html');">
        <td width="130" align="right">
            01:13PM
        </td>
        <td align="left">
            <div class="news-link-container">
                <div class="news-link-left">
                    <a class="tab-link-news" href="https://finance.yahoo.com/video/apples-tim-cook-reportedly-capitol-181349594.html" target="_blank" rel="nofollow">Apple's Tim Cook reportedly on Capitol Hill, Oracle earnings watch</a>
                </div>
                <div class="news-link-right">
                    <span>(Yahoo Finance Video)</span></div></div></td></tr>
    <tr class="cursor-pointer has-label" onclick="trackAndOpenNews(event, 'Zacks', '/news/251015/dell-gains-traction-in-ai-pc-market-can-it-drive-csg-revenue');">
        <td width="130" align="right">
            01:08PM
        </td>
        <td align="left">
            <div class="news-link-container">
                <div class="news-link-left">
                    <a class="tab-link-news" href="/news/251015/dell-gains-traction-in-ai-pc-market-can-it-drive-csg-revenue" target="_blank" >DELL Gains Traction in AI PC Market: Can It Drive CSG Revenue?</a>
                </div>
                <div class="news-link-right">
                    <span>(Zacks)</span></div></div></td></tr>
    <tr class="cursor-pointer has-label" onclick="trackAndOpenNews(event, 'Barchart', 'https://finance.yahoo.com/m/0098f64c-fb56-3596-a457-a6ef5882d584/could-meta-stock-skyrocket-in.html');">
        <td width="130" align="right">
            12:24PM
        </td>
        <td align="left">
            <div class="news-link-container">
                <div class="news-link-left">
                    <a class="tab-link-news" href="https://finance.yahoo.com/m/0098f64c-fb56-3596-a457-a6ef5882d584/could-meta-stock-skyrocket-in.html" target="_blank" rel="nofollow">Could Meta Stock Skyrocket in 2026 If Mark Zuckerberg Declares Another Year of Efficiency?</a>
                </div>
                <div class="news-link-right">
                    <span>(Barchart)</span></div></div></td></tr>
    <tr class="cursor-pointer has-label" onclick="trackAndOpenNews(event, 'Yahoo Finance Video', 'https://finance.yahoo.com/video/talk-ai-bubble-just-ridiculous-171039241.html');">
        <td width="130" align="right">
            12:10PM
        </td>
        <td align="left">
            <div class="news-link-container">
                <div class="news-link-left">
                    <a class="tab-link-news" href="https://finance.yahoo.com/video/talk-ai-bubble-just-ridiculous-171039241.html" target="_blank" rel="nofollow">Talk of an AI bubble is just 'ridiculous,' this strategist says</a>
                </div>
                <div class="news-link-right">
                    <span>(Yahoo Finance Video)</span></div></div></td></tr>
    <tr class="cursor-pointer has-label" onclick="trackAndOpenNews(event, 'MarketBeat', '/news/250827/apple-stock-could-surge-on-record-iphone-sales-and-bold-ai-strategy');">
        <td width="130" align="right">
            11:07AM
        </td>
        <td align="left">
            <div class="news-link-container">
                <div class="news-link-left">
                    <a class="tab-link-news" href="/news/250827/apple-stock-could-surge-on-record-iphone-sales-and-bold-ai-strategy" target="_blank" >Apple Stock Could Surge on Record iPhone Sales and Bold AI Strategy</a>
                </div>
                <div class="news-link-right">
                    <span>(MarketBeat)</span></div></div></td></tr>
    <tr class="cursor-pointer has-label" onclick="trackAndOpenNews(event, 'GuruFocus.com', 'https://finance.yahoo.com/news/apples-foldable-iphone-expected-land-155153304.html');">
        <td width="130" align="right">
            10:51AM
        </td>
        <td align="left">
            <div class="news-link-container">
                <div class="news-link-left">
                    <a class="tab-link-news" href="https://finance.yahoo.com/news/apples-foldable-iphone-expected-land-155153304.html" target="_blank" rel="nofollow">Apple's Foldable iPhone Expected to Land Well with Consumers</a>
                </div>
                <div class="news-link-right">
                    <span>(GuruFocus.com)</span></div></div></td></tr>
    <tr class="cursor-pointer has-label" onclick="trackAndOpenNews(event, 'Yahoo Finance Video', 'https://finance.yahoo.com/video/big-techs-ai-build-mostly-153717614.html');">
        <td width="130" align="right">
            10:37AM
        </td>
        <td align="left">
            <div class="news-link-container">
                <div class="news-link-left">
                    <a class="tab-link-news" href="https://finance.yahoo.com/video/big-techs-ai-build-mostly-153717614.html" target="_blank" rel="nofollow">How Big Tech's AI build-out is 'mostly' a private credit story</a>
                </div>
                <div class="news-link-right">
                    <span>(Yahoo Finance Video)</span></div></div></td></tr>
    <tr class="cursor-pointer has-label" onclick="trackAndOpenNews(event, '24/7 Wall St.', 'https://finance.yahoo.com/m/bb4e411b-a660-3182-8703-8d783e28abde/qyld-turns-mag-7-tech-stocks.html');">
        <td width="130" align="right">
            09:48AM
        </td>
        <td align="left">
            <div class="news-link-container">
                <div class="news-link-left">
                    <a class="tab-link-news" href="https://finance.yahoo.com/m/bb4e411b-a660-3182-8703-8d783e28abde/qyld-turns-mag-7-tech-stocks.html" target="_blank" rel="nofollow">QYLD Turns Mag 7 Tech Stocks Into an 11% Dividend Yield</a>
                </div>
                <div class="news-link-right">
                    <span>(24/7 Wall St.)</span></div></div></td></tr>
    <tr class="cursor-pointer has-label" onclick="trackAndOpenNews(event, 'Reuters', 'https://finance.yahoo.com/news/sales-foreign-branded-phones-china-142749797.html');">
        <td width="130" align="right">
            09:27AM
        </td>
        <td align="left">
            <div class="news-link-container">
                <div class="news-link-left">
                    <a class="tab-link-news" href="https://finance.yahoo.com/news/sales-foreign-branded-phones-china-142749797.html" target="_blank" rel="nofollow">Sales of foreign-branded phones in China up 13.0% in October, data shows</a>
                </div>
                <div class="news-link-right">
                    <span>(Reuters)</span></div></div></td></tr>
    <tr class="cursor-pointer has-label" onclick="trackAndOpenNews(event, 'Investor\u0027s Business Daily', 'https://finance.yahoo.com/m/6a8dc9d7-e276-3ac9-802b-3345cd107149/taiwan-semiconductor-nears.html');">
        <td width="130" align="right">
            07:41AM
        </td>
        <td align="left">
            <div class="news-link-container">
                <div class="news-link-left">
                    <a class="tab-link-news" href="https://finance.yahoo.com/m/6a8dc9d7-e276-3ac9-802b-3345cd107149/taiwan-semiconductor-nears.html" target="_blank" rel="nofollow">Taiwan Semiconductor Nears Buy Point After Sales Report</a>
                </div>
                <div class="news-link-right">
                    <span>(Investor's Business Daily)</span></div></div></td></tr>
    <tr class="cursor-pointer has-label" onclick="trackAndOpenNews(event, 'Investor\u0027s Business Daily', 'https://finance.yahoo.com/m/bc03797f-2a79-3250-8abc-cb1a0a21e133/at%26t-joins-t-mobile-in.html');">
        <td width="130" align="right">
            07:19AM
        </td>
        <td align="left">
            <div class="news-link-container">
                <div class="news-link-left">
                    <a class="tab-link-news" href="https://finance.yahoo.com/m/bc03797f-2a79-3250-8abc-cb1a0a21e133/at%26t-joins-t-mobile-in.html" target="_blank" rel="nofollow">AT&amp;T Joins T-Mobile In Digital Switching. Verizon Adds To Holiday Promotional War.</a>
                </div>
                <div class="news-link-right">
                    <span>(Investor's Business Daily)</span></div></div></td></tr>
    <tr class="cursor-pointer has-label" onclick="trackAndOpenNews(event, 'GuruFocus.com', 'https://finance.yahoo.com/news/disney-nominates-former-apple-executive-121000365.html');">
        <td width="130" align="right">
            07:10AM
        </td>
        <td align="left">
            <div class="news-link-container">
                <div class="news-link-left">
                    <a class="tab-link-news" href="https://finance.yahoo.com/news/disney-nominates-former-apple-executive-121000365.html" target="_blank" rel="nofollow">Disney Nominates Former Apple Executive Jeff Williams to Its Board</a>
                </div>
                <div class="news-link-right">
                    <span>(GuruFocus.com)</span></div></div></td></tr>
    <tr class="cursor-pointer has-label" onclick="trackAndOpenNews(event, 'GuruFocus.com', 'https://finance.yahoo.com/news/apple-expands-fitness-28-markets-115217584.html');">
        <td width="130" align="right">
            06:52AM
        </td>
        <td align="left">
            <div class="news-link-container">
                <div class="news-link-left">
                    <a class="tab-link-news" href="https://finance.yahoo.com/news/apple-expands-fitness-28-markets-115217584.html" target="_blank" rel="nofollow">Apple Expands Fitness+ To 28 New Markets</a>
                </div>
                <div class="news-link-right">
                    <span>(GuruFocus.com)</span></div></div></td></tr>
    <tr class="cursor-pointer has-label" onclick="trackAndOpenNews(event, 'GuruFocus.com', 'https://finance.yahoo.com/news/why-tsmc-powering-next-wave-113102409.html');">
        <td width="130" align="right">
            06:31AM
        </td>
        <td align="left">
            <div class="news-link-container">
                <div class="news-link-left">
                    <a class="tab-link-news" href="https://finance.yahoo.com/news/why-tsmc-powering-next-wave-113102409.html" target="_blank" rel="nofollow">Why TSMC Is Powering the Next Wave of AI Innovation</a>
                </div>
                <div class="news-link-right">
                    <span>(GuruFocus.com)</span></div></div></td></tr>
    <tr class="cursor-pointer has-label" onclick="trackAndOpenNews(event, 'CCN', 'https://finance.yahoo.com/m/b76adbae-c484-3118-9932-d5e6ba9cbd51/donald-trump-crypto-video.html');">
        <td width="130" align="right">
            06:30AM
        </td>
        <td align="left">
            <div class="news-link-container">
                <div class="news-link-left">
                    <a class="tab-link-news" href="https://finance.yahoo.com/m/b76adbae-c484-3118-9932-d5e6ba9cbd51/donald-trump-crypto-video.html" target="_blank" rel="nofollow">Donald Trump Crypto Video Game Is Almost Here   Can It Revive His Dying Memecoin?</a>
                </div>
                <div class="news-link-right">
                    <span>(CCN)</span></div></div></td></tr>
    <tr class="cursor-pointer has-label" onclick="trackAndOpenNews(event, 'Moneywise', 'https://finance.yahoo.com/news/ma-couples-life-savings-wiped-110000870.html');">
        <td width="130" align="right">
            06:00AM
        </td>
        <td align="left">
            <div class="news-link-container">
                <div class="news-link-left">
                    <a class="tab-link-news" href="https://finance.yahoo.com/news/ma-couples-life-savings-wiped-110000870.html" target="_blank" rel="nofollow">MA couple's life savings wiped out after scam involving Apple gift cards. Now, they're doing gig work just 'to survive'</a>
                </div>
                <div class="news-link-right">
                    <span>(Moneywise)</span></div></div></td></tr>
    <tr class="cursor-pointer has-label" onclick="trackAndOpenNews(event, 'Bloomberg', 'https://finance.yahoo.com/news/pictet-head-multi-asset-says-102813848.html');">
        <td width="130" align="right">
            05:28AM
        </td>
        <td align="left">
            <div class="news-link-container">
                <div class="news-link-left">
                    <a class="tab-link-news" href="https://finance.yahoo.com/news/pictet-head-multi-asset-says-102813848.html" target="_blank" rel="nofollow">Pictets Head of Multi Asset Says Chase US Stock Rally</a>
                </div>
                <div class="news-link-right">
                    <span>(Bloomberg)</span></div></div></td></tr>
    <tr class="cursor-pointer has-label" onclick="trackAndOpenNews(event, 'Zacks', '/news/250390/bull-of-the-day-coherent-cohr');">
        <td width="130" align="right">
            05:20AM
        </td>
        <td align="left">
            <div class="news-link-container">
                <div class="news-link-left">
                    <a class="tab-link-news" href="/news/250390/bull-of-the-day-coherent-cohr" target="_blank" >Bull of the Day: Coherent (COHR)</a>
                </div>
                <div class="news-link-right">
                    <span>(Zacks)</span></div></div></td></tr>
    <tr class="cursor-pointer has-label" onclick="trackAndOpenNews(event, 'Motley Fool', '/news/250220/billionaire-warren-buffett-offers-184-billion-reasons-for-investors-to-be-fearful-in-the-new-year');">
        <td width="130" align="right">
            03:26AM
        </td>
        <td align="left">
            <div class="news-link-container">
                <div class="news-link-left">
                    <a class="tab-link-news" href="/news/250220/billionaire-warren-buffett-offers-184-billion-reasons-for-investors-to-be-fearful-in-the-new-year" target="_blank" >Billionaire Warren Buffett Offers 184 Billion Reasons for Investors to Be Fearful in the New Year</a>
                </div>
                <div class="news-link-right">
                    <span>(Motley Fool)</span></div></div></td></tr>
    <tr class="cursor-pointer has-label" onclick="trackAndOpenNews(event, 'TheStreet', 'https://finance.yahoo.com/m/3103be22-9022-3518-8658-d9899e263d21/apple-analyst-sets-bold-stock.html');">
        <td width="130" align="right">
            Dec-09-25 11:07PM
        </td>
        <td align="left">
            <div class="news-link-container">
                <div class="news-link-left">
                    <a class="tab-link-news" href="https://finance.yahoo.com/m/3103be22-9022-3518-8658-d9899e263d21/apple-analyst-sets-bold-stock.html" target="_blank" rel="nofollow">Apple analyst sets bold stock target for 2026</a>
                </div>
                <div class="news-link-right">
                    <span>(TheStreet)</span></div></div></td></tr>
    <tr class="cursor-pointer has-label" onclick="trackAndOpenNews(event, 'CNBC TV', 'https://www.youtube.com/watch?v=XSm719gKg-k');">
        <td width="130" align="right">
            08:25PM
        </td>
        <td align="left">
            <div class="news-link-container">
                <div class="news-link-left">
                    <a class="tab-link-news" href="https://www.youtube.com/watch?v=XSm719gKg-k" target="_blank" rel="nofollow">'Own it, don't trade it,' says Jim Cramer on Nvidia</a>
                </div>
                <div class="news-link-right">
                    <span>(CNBC TV)</span></div></div></td></tr>
    <tr class="cursor-pointer has-label" onclick="trackAndOpenNews(event, 'Above Avalon', 'https://www.aboveavalon.com/notes/2025/12/9/apple-poaches-metas-top-lawyer-lisa-jackson-to-retire-apple-streamlines-hierarchy');">
        <td width="130" align="right">
            07:27PM
        </td>
        <td align="left">
            <div class="news-link-container">
                <div class="news-link-left">
                    <a class="tab-link-news" href="https://www.aboveavalon.com/notes/2025/12/9/apple-poaches-metas-top-lawyer-lisa-jackson-to-retire-apple-streamlines-hierarchy" target="_blank" rel="nofollow">Apple Poaches Meta's Top Lawyer, Lisa Jackson to Retire, Apple Streamlines Hierarchy</a>
                </div>
                <div class="news-link-right">
                    <span>(Above Avalon)</span></div></div></td></tr>
    <tr class="cursor-pointer has-label" onclick="trackAndOpenNews(event, 'Above Avalon', 'https://www.aboveavalon.com/notes/2025/12/9/alan-dye-leaves-apple-formeta-poaching-apple-employees-nuisance-or-big-problem');">
        <td width="130" align="right">
            07:23PM
        </td>
        <td align="left">
            <div class="news-link-container">
                <div class="news-link-left">
                    <a class="tab-link-news" href="https://www.aboveavalon.com/notes/2025/12/9/alan-dye-leaves-apple-formeta-poaching-apple-employees-nuisance-or-big-problem" target="_blank" rel="nofollow">Alan Dye Leaves Apple for Meta, Poaching Apple Employees: Nuisance or Big Problem?</a>
                </div>
                <div class="news-link-right">
                    <span>(Above Avalon)</span></div></div></td></tr>
    <tr class="cursor-pointer has-label" onclick="trackAndOpenNews(event, 'Reuters', 'https://finance.yahoo.com/news/disney-nominates-former-apple-coo-223437961.html');">
        <td width="130" align="right">
            05:34PM
        </td>
        <td align="left">
            <div class="news-link-container">
                <div class="news-link-left">
                    <a class="tab-link-news" href="https://finance.yahoo.com/news/disney-nominates-former-apple-coo-223437961.html" target="_blank" rel="nofollow">Disney nominates former Apple COO to its board</a>
                </div>
                <div class="news-link-right">
                    <span>(Reuters)</span></div></div></td></tr>
    <tr class="cursor-pointer has-label" onclick="trackAndOpenNews(event, 'Investor\u0027s Business Daily', 'https://www.investors.com/news/technology/apple-stock-3-price-target-hikes?mod=IBD_FV');">
        <td width="130" align="right">
            04:51PM
        </td>
        <td align="left">
            <div class="news-link-container">
                <div class="news-link-left">
                    <a class="tab-link-news" href="https://www.investors.com/news/technology/apple-stock-3-price-target-hikes?mod=IBD_FV" target="_blank" rel="nofollow">Apple Stock Gets Three Price-Target Hikes. Here's Why.</a>
                </div>
                <div class="news-link-right">
                    <span>(Investor's Business Daily)</span></div></div></td></tr>
    <tr class="cursor-pointer has-label" onclick="trackAndOpenNews(event, 'Barchart', 'https://finance.yahoo.com/m/35345531-e670-3ab8-8701-b413cf0b03d2/apple-stock-marks-a-solid.html');">
        <td width="130" align="right">
            04:24PM
        </td>
        <td align="left">
            <div class="news-link-container">
                <div class="news-link-left">
                    <a class="tab-link-news" href="https://finance.yahoo.com/m/35345531-e670-3ab8-8701-b413cf0b03d2/apple-stock-marks-a-solid.html" target="_blank" rel="nofollow">Apple Stock Marks a Solid Comeback. Is AAPL a Buy, Sell, or Hold for 2026?</a>
                </div>
                <div class="news-link-right">
                    <span>(Barchart)</span></div></div></td></tr>
    <tr class="cursor-pointer has-label" onclick="trackAndOpenNews(event, 'Barrons.com', 'https://finance.yahoo.com/m/02fc2e14-3c6c-3811-98f9-a83b8e0db61f/2-reasons-tech-stocks-are.html');">
        <td width="130" align="right">
            03:59PM
        </td>
        <td align="left">
            <div class="news-link-container">
                <div class="news-link-left">
                    <a class="tab-link-news" href="https://finance.yahoo.com/m/02fc2e14-3c6c-3811-98f9-a83b8e0db61f/2-reasons-tech-stocks-are.html" target="_blank" rel="nofollow">2 Reasons Tech Stocks Are Rising Past AI Worries</a>
                </div>
                <div class="news-link-right">
                    <span>(Barrons.com)</span></div></div></td></tr>
    <tr class="cursor-pointer has-label" onclick="trackAndOpenNews(event, 'Barrons.com', 'https://www.barrons.com/articles/tech-stocks-buy-ai-meta-47d11a3a?mod=bar_FV');">
        <td width="130" align="right">
            03:48PM
        </td>
        <td align="left">
            <div class="news-link-container">
                <div class="news-link-left">
                    <a class="tab-link-news" href="https://www.barrons.com/articles/tech-stocks-buy-ai-meta-47d11a3a?mod=bar_FV" target="_blank" rel="nofollow">2 Reasons Tech Stocks Are Rise Past AI Worries</a>
                </div>
                <div class="news-link-right">
                    <span>(Barrons.com)</span></div></div></td></tr>
    <tr class="cursor-pointer has-label" onclick="trackAndOpenNews(event, 'Barrons.com', 'https://www.barrons.com/articles/meta-stock-price-tech-ai-buy-47d11a3a?mod=bar_FV');">
        <td width="130" align="right">
            02:00PM
        </td>
        <td align="left">
            <div class="news-link-container">
                <div class="news-link-left">
                    <a class="tab-link-news" href="https://www.barrons.com/articles/meta-stock-price-tech-ai-buy-47d11a3a?mod=bar_FV" target="_blank" rel="nofollow">2 Reasons Meta and Other Tech Stocks Can Rise Past AI Worries</a>
                </div>
                <div class="news-link-right">
                    <span>(Barrons.com)</span></div></div></td></tr>
    <tr class="cursor-pointer has-label" onclick="trackAndOpenNews(event, 'Insider Monkey', '/news/249835/apple-aapl-lands-330-target-as-clsa-turns-more-bullish-on-iphone-momentum');">
        <td width="130" align="right">
            01:19PM
        </td>
        <td align="left">
            <div class="news-link-container">
                <div class="news-link-left">
                    <a class="tab-link-news" href="/news/249835/apple-aapl-lands-330-target-as-clsa-turns-more-bullish-on-iphone-momentum" target="_blank" >Apple (AAPL) Lands $330 Target as CLSA Turns More Bullish on iPhone Momentum</a>
                </div>
                <div class="news-link-right">
                    <span>(Insider Monkey)</span></div></div></td></tr>
    <tr class="cursor-pointer has-label" onclick="trackAndOpenNews(event, 'Barrons.com', 'https://www.barrons.com/articles/tech-stocks-ai-rebound-analysts-47d11a3a?mod=bar_FV');">
        <td width="130" align="right">
            12:52PM
        </td>
        <td align="left">
            <div class="news-link-container">
                <div class="news-link-left">
                    <a class="tab-link-news" href="https://www.barrons.com/articles/tech-stocks-ai-rebound-analysts-47d11a3a?mod=bar_FV" target="_blank" rel="nofollow">Tech Stocks Are Rebounding. Two Reasons It Can Continue.</a>
                </div>
                <div class="news-link-right">
                    <span>(Barrons.com)</span></div></div></td></tr>
    <tr class="cursor-pointer has-label" onclick="trackAndOpenNews(event, '24/7 Wall St.', 'https://finance.yahoo.com/m/a9c6ad45-7e22-3a0e-8f64-6aab70517489/openai%E2%80%99s-new-ai-gadget-might.html');">
        <td width="130" align="right">
            12:49PM
        </td>
        <td align="left">
            <div class="news-link-container">
                <div class="news-link-left">
                    <a class="tab-link-news" href="https://finance.yahoo.com/m/a9c6ad45-7e22-3a0e-8f64-6aab70517489/openai%E2%80%99s-new-ai-gadget-might.html" target="_blank" rel="nofollow">OpenAIs New AI Gadget Might Be an iPhone Disruptor. But Apple Wont Be Standing Still</a>
                </div>
                <div class="news-link-right">
                    <span>(24/7 Wall St.)</span></div></div></td></tr>
    <tr class="cursor-pointer has-label" onclick="trackAndOpenNews(event, '24/7 Wall St.', 'https://finance.yahoo.com/m/15a20bc8-cf4e-399a-a39e-183a256de831/3-monthly-paying-dividend.html');">
        <td width="130" align="right">
            12:47PM
        </td>
        <td align="left">
            <div class="news-link-container">
                <div class="news-link-left">
                    <a class="tab-link-news" href="https://finance.yahoo.com/m/15a20bc8-cf4e-399a-a39e-183a256de831/3-monthly-paying-dividend.html" target="_blank" rel="nofollow">3 Monthly-Paying Dividend ETFs Perfect for Retirement Income</a>
                </div>
                <div class="news-link-right">
                    <span>(24/7 Wall St.)</span></div></div></td></tr>
    <tr class="cursor-pointer has-label" onclick="trackAndOpenNews(event, 'GuruFocus.com', 'https://finance.yahoo.com/news/apples-4-trillion-comeback-why-171503306.html');">
        <td width="130" align="right">
            12:15PM
        </td>
        <td align="left">
            <div class="news-link-container">
                <div class="news-link-left">
                    <a class="tab-link-news" href="https://finance.yahoo.com/news/apples-4-trillion-comeback-why-171503306.html" target="_blank" rel="nofollow">Apple's $4 Trillion Comeback: Why It's Now Beating Nvidia, Microsoft, and Meta at Their Own Game</a>
                </div>
                <div class="news-link-right">
                    <span>(GuruFocus.com)</span></div></div></td></tr>
    <tr class="cursor-pointer has-label" onclick="trackAndOpenNews(event, 'Zacks', '/news/249833/googl-rises-79-in-a-year-on-ai-push-will-the-rally-continue-in-2026');">
        <td width="130" align="right">
            12:12PM
        </td>
        <td align="left">
            <div class="news-link-container">
                <div class="news-link-left">
                    <a class="tab-link-news" href="/news/249833/googl-rises-79-in-a-year-on-ai-push-will-the-rally-continue-in-2026" target="_blank" >GOOGL Rises 79% in a Year on AI Push: Will the Rally Continue in 2026?</a>
                </div>
                <div class="news-link-right">
                    <span>(Zacks)</span></div></div></td></tr>
    <tr class="cursor-pointer has-label" onclick="trackAndOpenNews(event, 'Motley Fool', '/news/249675/3-stocks-that-could-skyrocket-before-the-end-of-2025');">
        <td width="130" align="right">
            11:25AM
        </td>
        <td align="left">
            <div class="news-link-container">
                <div class="news-link-left">
                    <a class="tab-link-news" href="/news/249675/3-stocks-that-could-skyrocket-before-the-end-of-2025" target="_blank" >3 Stocks That Could Skyrocket Before the End of 2025</a>
                </div>
                <div class="news-link-right">
                    <span>(Motley Fool)</span></div></div></td></tr>
    <tr class="cursor-pointer has-label" onclick="trackAndOpenNews(event, 'Reuters', 'https://finance.yahoo.com/news/ray-ban-meta-glasses-off-161424567.html');">
        <td width="130" align="right">
            11:14AM
        </td>
        <td align="left">
            <div class="news-link-container">
                <div class="news-link-left">
                    <a class="tab-link-news" href="https://finance.yahoo.com/news/ray-ban-meta-glasses-off-161424567.html" target="_blank" rel="nofollow">Ray-Ban Meta glasses take off but face privacy and competition test</a>
                </div>
                <div class="news-link-right">
                    <span>(Reuters)</span></div></div></td></tr>
    <tr class="cursor-pointer has-label" onclick="trackAndOpenNews(event, 'Yahoo Finance Video', 'https://finance.yahoo.com/video/trumps-nvidia-china-sales-approval-160000783.html');">
        <td width="130" align="right">
            11:00AM
        </td>
        <td align="left">
            <div class="news-link-container">
                <div class="news-link-left">
                    <a class="tab-link-news" href="https://finance.yahoo.com/video/trumps-nvidia-china-sales-approval-160000783.html" target="_blank" rel="nofollow">What Trump's Nvidia China sales approval means for the Mag 7</a>
                </div>
                <div class="news-link-right">
                    <span>(Yahoo Finance Video)</span></div></div></td></tr>
    <tr class="cursor-pointer has-label" onclick="trackAndOpenNews(event, '24/7 Wall St.', 'https://finance.yahoo.com/m/b3bcad38-5f48-3fd1-b3d4-d0f01d498dc7/it%E2%80%99s-warren-buffett%E2%80%99s-last.html');">
        <td width="130" align="right">
            10:30AM
        </td>
        <td align="left">
            <div class="news-link-container">
                <div class="news-link-left">
                    <a class="tab-link-news" href="https://finance.yahoo.com/m/b3bcad38-5f48-3fd1-b3d4-d0f01d498dc7/it%E2%80%99s-warren-buffett%E2%80%99s-last.html" target="_blank" rel="nofollow">Its Warren Buffetts Last Month at Berkshire. Should Investors Buy Before the Big Transition?</a>
                </div>
                <div class="news-link-right">
                    <span>(24/7 Wall St.)</span></div></div></td></tr>
    <tr class="cursor-pointer has-label" onclick="trackAndOpenNews(event, 'Bloomberg', 'https://finance.yahoo.com/news/apple-slow-ai-pace-becomes-104658095.html');">
        <td width="130" align="right">
            09:47AM
        </td>
        <td align="left">
            <div class="news-link-container">
                <div class="news-link-left">
                    <a class="tab-link-news" href="https://finance.yahoo.com/news/apple-slow-ai-pace-becomes-104658095.html" target="_blank" rel="nofollow">Apples Slow AI Pace Becomes a Strength as Market Grows Weary of Spending</a>
                </div>
                <div class="news-link-right">
                    <span>(Bloomberg)</span></div></div></td></tr>
    <tr class="cursor-pointer has-label" onclick="trackAndOpenNews(event, 'Investor\u0027s Business Daily', 'https://finance.yahoo.com/m/a9cd4bbd-10af-3983-a2e2-dbfacb3eb22c/nvidia-eyes-key-level-as.html');">
        <td width="130" align="right">
            09:46AM
        </td>
        <td align="left">
            <div class="news-link-container">
                <div class="news-link-left">
                    <a class="tab-link-news" href="https://finance.yahoo.com/m/a9cd4bbd-10af-3983-a2e2-dbfacb3eb22c/nvidia-eyes-key-level-as.html" target="_blank" rel="nofollow">Nvidia Eyes Key Level As Trumps Gives China Chip Green Signal; Is Nvidia A Buy Now?</a>
                </div>
                <div class="news-link-right">
                    <span>(Investor's Business Daily)</span></div></div></td></tr>
    <tr class="cursor-pointer has-label" onclick="trackAndOpenNews(event, 'Investor\u0027s Business Daily', 'https://finance.yahoo.com/m/af97029d-ae07-38bf-867e-c1a30a058f75/stock-market-today%3A-dow.html');">
        <td width="130" align="right">
            08:35AM
        </td>
        <td align="left">
            <div class="news-link-container">
                <div class="news-link-left">
                    <a class="tab-link-news" href="https://finance.yahoo.com/m/af97029d-ae07-38bf-867e-c1a30a058f75/stock-market-today%3A-dow.html" target="_blank" rel="nofollow">Stock Market Today: Dow Wobbles Ahead Of Fed Meeting; Nvidia Rallies On Trump Comments (Live Coverage)</a>
                </div>
                <div class="news-link-right">
                    <span>(Investor's Business Daily)</span></div></div></td></tr>
    <tr class="cursor-pointer has-label" onclick="trackAndOpenNews(event, 'Barrons.com', 'https://www.barrons.com/articles/walmart-stock-price-nasdaq-listing-tech-0b703456?mod=bar_FV');">
        <td width="130" align="right">
            08:17AM
        </td>
        <td align="left">
            <div class="news-link-container">
                <div class="news-link-left">
                    <a class="tab-link-news" href="https://www.barrons.com/articles/walmart-stock-price-nasdaq-listing-tech-0b703456?mod=bar_FV" target="_blank" rel="nofollow">Walmart Stock Now Trades on the Nasdaq. Its Tech Transformation Is Real.</a>
                </div>
                <div class="news-link-right">
                    <span>(Barrons.com)</span></div></div></td></tr>
    <tr class="cursor-pointer has-label" onclick="trackAndOpenNews(event, 'Barrons.com', 'https://www.barrons.com/articles/walmart-stock-nasdaq-listing-0b703456?mod=bar_FV');">
        <td width="130" align="right">
            07:21AM
        </td>
        <td align="left">
            <div class="news-link-container">
                <div class="news-link-left">
                    <a class="tab-link-news" href="https://www.barrons.com/articles/walmart-stock-nasdaq-listing-0b703456?mod=bar_FV" target="_blank" rel="nofollow">Walmart Completes Move to Nasdaq, Sealing Its Tech Transformation</a>
                </div>
                <div class="news-link-right">
                    <span>(Barrons.com)</span></div></div></td></tr>
    <tr class="cursor-pointer has-label" onclick="trackAndOpenNews(event, 'Yahoo Finance Video', 'https://finance.yahoo.com/video/mag-7s-lead-over-other-120052402.html');">
        <td width="130" align="right">
            07:00AM
        </td>
        <td align="left">
            <div class="news-link-container">
                <div class="news-link-left">
                    <a class="tab-link-news" href="https://finance.yahoo.com/video/mag-7s-lead-over-other-120052402.html" target="_blank" rel="nofollow">How Mag 7's lead over other stocks could shrink in 2026</a>
                </div>
                <div class="news-link-right">
                    <span>(Yahoo Finance Video)</span></div></div></td></tr>
    <tr class="cursor-pointer has-label" onclick="trackAndOpenNews(event, 'GuruFocus.com', 'https://finance.yahoo.com/news/evercore-says-apple-exec-exits-112216758.html');">
        <td width="130" align="right">
            06:22AM
        </td>
        <td align="left">
            <div class="news-link-container">
                <div class="news-link-left">
                    <a class="tab-link-news" href="https://finance.yahoo.com/news/evercore-says-apple-exec-exits-112216758.html" target="_blank" rel="nofollow">Evercore Says Apple Exec Exits Not A Crisis</a>
                </div>
                <div class="news-link-right">
                    <span>(GuruFocus.com)</span></div></div></td></tr>
    <tr class="cursor-pointer has-label" onclick="trackAndOpenNews(event, 'Verdict', 'https://finance.yahoo.com/m/89a50805-244e-32bc-ab54-6a0951f114bd/meta-to-introduce-new-ad.html');">
        <td width="130" align="right">
            04:34AM
        </td>
        <td align="left">
            <div class="news-link-container">
                <div class="news-link-left">
                    <a class="tab-link-news" href="https://finance.yahoo.com/m/89a50805-244e-32bc-ab54-6a0951f114bd/meta-to-introduce-new-ad.html" target="_blank" rel="nofollow">Meta to introduce new ad choices for Facebook and Instagram in EU</a>
                </div>
                <div class="news-link-right">
                    <span>(Verdict)</span></div></div></td></tr>
    <tr class="cursor-pointer has-label" onclick="trackAndOpenNews(event, 'Bloomberg', 'https://finance.yahoo.com/news/google-hit-eu-abuse-dominance-083158203.html');">
        <td width="130" align="right">
            03:31AM
        </td>
        <td align="left">
            <div class="news-link-container">
                <div class="news-link-left">
                    <a class="tab-link-news" href="https://finance.yahoo.com/news/google-hit-eu-abuse-dominance-083158203.html" target="_blank" rel="nofollow">Google Hit by EU Abuse of Dominance Probe Over AI Tools</a>
                </div>
                <div class="news-link-right">
                    <span>(Bloomberg)</span></div></div></td></tr>
    <tr class="cursor-pointer has-label" onclick="trackAndOpenNews(event, 'Motley Fool', '/news/249023/this-tech-company-is-one-of-the-largest-by-market-capitalization-but-is-its-stock-a-buy');">
        <td width="130" align="right">
            02:50AM
        </td>
        <td align="left">
            <div class="news-link-container">
                <div class="news-link-left">
                    <a class="tab-link-news" href="/news/249023/this-tech-company-is-one-of-the-largest-by-market-capitalization-but-is-its-stock-a-buy" target="_blank" >This Tech Company is One of the Largest by Market Capitalization. But Is Its Stock a Buy?</a>
                </div>
                <div class="news-link-right">
                    <span>(Motley Fool)</span></div></div></td></tr>
</table>
</div>
</td><td width="300" valign="top" style="padding-left: 10px"><div id="IC_D_300x250_1"class="relative overflow-hidden flex items-center justify-center w-full mx-auto" style="width:300px;height:250px;max-height:250px"></div><div id="stocktwits-widget-news" class="fullview-news-outer quote_stocktwits box-content w-[300px]" data-testid="quote-stocktwits-widget-news-container">
    <div class="quote_stocktwits-bottom-cover"></div>
    <div class="quote_stocktwits-right-cover"></div>
</div>
<script type="text/javascript">
    function StocktwitsInit() {
        var StocktwitsHeight = document.getElementById('news-table').clientHeight - 500;
        if(typeof STWT !== 'undefined') {
            var isNewLayout = true;
            var isDarkTheme = true;
            var MIN_TWIT_HEIGHT = 71;
            var quoteTicker = 'AAPL';
            var bgColor = isNewLayout ? (isDarkTheme ? '22262F' : 'FFFFFF') : 'transparent';
            var text_color = isNewLayout ? (isDarkTheme ? 'C3C6D0' : '4C5263') : '000000';
            var link_color = isNewLayout ? (isDarkTheme ? '57aefb' : '306DCA') : '4871a8';
            var divider_color = isNewLayout ? (isDarkTheme ? '353945' : 'DEDFE5') : 'd3d3d3';
            var time_color = isNewLayout ? '868EA5' : '999999';
            var username_color = isNewLayout ? (isDarkTheme ? 'F3F3F5' : '22262F') : '600D0B';
            var font_size = isNewLayout ? 12 : 11;
            STWT.Widget({
                container: 'stocktwits-widget-news',
                symbol: quoteTicker,
                width: '300',
                height: StocktwitsHeight,
                limit: Math.ceil(StocktwitsHeight / MIN_TWIT_HEIGHT),
                scrollbars: 0,
                header: 0,
                streaming: 'true',
                style: { link_color, link_hover_color: link_color, header_text_color: text_color, border_color: bgColor, border_color_2: bgColor, divider_color, divider_type: 'solid', box_color: bgColor, stream_color: bgColor, text_color, time_color, font: 'Verdana, Arial, Tahoma', font_size, time_font_size: 10, username_font: 'Verdana, Arial, Tahoma', username_size: font_size, username_color, username_hover_color: username_color }
            });
        }
    }

    function loadStocktwitsScript() {
        var s = document.createElement('script');
        s.addEventListener('load', StocktwitsInit)
        s.setAttribute('async', true)
        s.src = '//api.stocktwits.com/addon/widget/2/widget-loader.min.js'
        document.body.appendChild(s)
    }

    if (document.readyState != 'loading'){
        loadStocktwitsScript();
    } else {
        document.addEventListener('DOMContentLoaded', loadStocktwitsScript);
    }
</script><div id="IC_D_300x250_2"class="relative overflow-hidden flex items-center justify-center w-full mx-auto" style="width:300px;height:250px;max-height:250px"></div></td></tr></table></td>
</tr>
<tr><td style="height:10px;font-size:0"><img src="gfx/nic2x2.gif" style="width:685px;height:10px"></td></tr>
<tr><td><table cellspacing="0" cellpading="0" border="0" width="100%" class="h-px">
<tr class="table-light3-row" height="1px">
<td class="fullview-profile quote_profile" align="left" valign="top"><div class="quote_profile-bio">Apple, Inc. engages in the design, manufacture, and sale of smartphones, personal computers, tablets, wearables and accessories, and other varieties of related services. It operates through the following geographical segments: Americas, Europe, Greater China, Japan, and Rest of Asia Pacific. The Americas segment includes North and South America. The Europe segment consists of European countries, as well as India, the Middle East, and Africa. The Greater China segment comprises China, Hong Kong, and Taiwan. The Rest of Asia Pacific segment includes Australia and Asian countries. Its products and services include iPhone, Mac, iPad, AirPods, Apple TV, Apple Watch, Beats products, AppleCare, iCloud, digital content stores, streaming, and licensing services. The company was founded by Steven Paul Jobs, Ronald Gerald Wayne, and Stephen G. Wozniak in April 1976 and is headquartered in Cupertino, CA.</div></td><td width="8"><img src="gfx/nic2x2.gif" style="width:8px;height:1px"></td><td class="fullview-profile quote_profile" align="left" valign="top" width="302" style="max-width: 302px;padding: 0;"><div class="managers-and-funds h-full"></div>
</td>
<script id="institutional-ownership-init-data-0" type="application/json">{"managersOwnership":[{"investorId":"102909","name":"VANGUARD GROUP INC","slug":"vanguard-group-inc-102909","percOwnership":9.429847996010889},{"investorId":"2012383","name":"BlackRock, Inc.","slug":"blackrock-inc-2012383","percOwnership":7.7244028058542895},{"investorId":"93751","name":"STATE STREET CORP","slug":"state-street-corp-93751","percOwnership":4.026179301097005},{"investorId":"19617","name":"JPMORGAN CHASE \u0026 CO","slug":"jpmorgan-chase-co-19617","percOwnership":3.189341675426538},{"investorId":"1214717","name":"GEODE CAPITAL MANAGEMENT, LLC","slug":"geode-capital-management-llc-1214717","percOwnership":2.399978531575968},{"investorId":"315066","name":"FMR LLC","slug":"fmr-llc-315066","percOwnership":2.0434360327214898},{"investorId":"1067983","name":"BERKSHIRE HATHAWAY INC","slug":"berkshire-hathaway-inc-1067983","percOwnership":1.6051640387051562},{"investorId":"895421","name":"MORGAN STANLEY","slug":"morgan-stanley-895421","percOwnership":1.543781730950648},{"investorId":"80255","name":"PRICE T ROWE ASSOCIATES INC /MD/","slug":"price-t-rowe-associates-inc-md-80255","percOwnership":1.4336207447238618},{"investorId":"73124","name":"NORTHERN TRUST CORP","slug":"northern-trust-corp-73124","percOwnership":1.1095841284601493}],"fundsOwnership":[{"investorId":"S000002848","name":"VANGUARD TOTAL STOCK MARKET INDEX FUND","slug":"vanguard-total-stock-market-index-fund-S000002848","percOwnership":3.147729993800706},{"investorId":"S000002839","name":"VANGUARD 500 INDEX FUND","slug":"vanguard-500-index-fund-S000002839","percOwnership":2.4672240640414005},{"investorId":"S000006027","name":"Fidelity 500 Index Fund","slug":"fidelity-500-index-fund-S000006027","percOwnership":1.2778855825988518},{"investorId":"S000004310","name":"iShares Core S\u0026P 500 ETF","slug":"ishares-core-sp-500-etf-S000004310","percOwnership":1.2273041427454785},{"investorId":"0000884394","name":"SPDR S\u0026P 500 ETF TRUST","slug":"spdr-sp-500-etf-trust-0000884394","percOwnership":1.1791200304574},{"investorId":"S000002842","name":"VANGUARD GROWTH INDEX FUND","slug":"vanguard-growth-index-fund-S000002842","percOwnership":0.9494666316271798},{"investorId":"S000009231","name":"Bond Fund of America","slug":"bond-fund-of-america-S000009231","percOwnership":0.8422953559203256},{"investorId":"0001067839","name":"Invesco QQQ Trust, Series 1","slug":"invesco-qqq-trust-series-1-0001067839","percOwnership":0.8407714819007573},{"investorId":"S000026863","name":"VANGUARD INTERMEDIATE-TERM CORPORATE BOND INDEX FUND","slug":"vanguard-intermediate-term-corporate-bond-index-fund-S000026863","percOwnership":0.6779197326217622},{"investorId":"S000002853","name":"VANGUARD INSTITUTIONAL INDEX FUND","slug":"vanguard-institutional-index-fund-S000002853","percOwnership":0.5829434112288078}]}</script></tr>
</table>
</td>
</tr>
<tr><td style="height:10px;font-size:0"><img src="gfx/nic2x2.gif" style="width:685px;height:10px"></td></tr>
<tr><td width="100%"><div id="statements"></div></td></tr><tr><td style="height:10px;font-size:0"><img src="gfx/nic2x2.gif" style="width:685px;height:10px"></td></tr>

            <tr><td>
                <script id="insider-init-data-0" type="application/json">[{"date":1734238800000,"saleAggregated":24997395.27,"saleTransactionCount":1,"buyAggregated":0,"buyTransactionCount":0},{"date":1736917200000,"saleAggregated":0,"saleTransactionCount":0,"buyAggregated":0,"buyTransactionCount":0},{"date":1739595600000,"saleAggregated":343146.7516,"saleTransactionCount":1,"buyAggregated":0,"buyTransactionCount":0},{"date":1742011200000,"saleAggregated":0,"saleTransactionCount":0,"buyAggregated":0,"buyTransactionCount":0},{"date":1744689600000,"saleAggregated":41760021.69,"saleTransactionCount":4,"buyAggregated":0,"buyTransactionCount":0},{"date":1747281600000,"saleAggregated":933955.1438,"saleTransactionCount":1,"buyAggregated":0,"buyTransactionCount":0},{"date":1749960000000,"saleAggregated":0,"saleTransactionCount":0,"buyAggregated":0,"buyTransactionCount":0},{"date":1752552000000,"saleAggregated":0,"saleTransactionCount":0,"buyAggregated":0,"buyTransactionCount":0},{"date":1755230400000,"saleAggregated":28658347.2,"saleTransactionCount":2,"buyAggregated":0,"buyTransactionCount":0},{"date":1757908800000,"saleAggregated":0,"saleTransactionCount":0,"buyAggregated":0,"buyTransactionCount":0},{"date":1760500800000,"saleAggregated":57586743.12,"saleTransactionCount":4,"buyAggregated":0,"buyTransactionCount":0},{"date":1763182800000,"saleAggregated":1017654.9600000001,"saleTransactionCount":1,"buyAggregated":0,"buyTransactionCount":0},{"date":1765774800000,"saleAggregated":0,"saleTransactionCount":0,"buyAggregated":0,"buyTransactionCount":0}]</script>
                <div class="insider-trading-chart"></div>
            </td></tr>
        <tr>
<td>
<table cellpadding="0" cellspacing="0" width="100%" class="body-table styled-table-new is-rounded p-0 mt-2">
<thead>
<tr>
<th class="" align="left">Insider Trading</th>
<th class="" align="left">Relationship</th>
<th class="" align="left">Date</th>
<th class="" align="center">Transaction</th>
<th class="" align="right">Cost</th>
<th class="" align="right">#Shares</th>
<th class="" align="right">Value ($)</th>
<th class="" align="right">#Shares Total</th>
<th class="" align="center">SEC Form 4</th>
</tr>
</thead>
<tr class="fv-insider-row is-sale-2" valign="top"><td><a href="insidertrading?oc=1631982&tc=7" class="tab-link">KONDO CHRIS</td><td style="white-space:nowrap">Principal Accounting Officer</td><td>Nov 07 '25</td><td class="transaction" style="white-space:nowrap" align="center"><span>Sale</span></td><td class="value" align="right">271.23</td><td class="value" align="right">3,752</td><td class="value" align="right">1,017,655</td><td class="value" align="right">15,098</td><td class="whitespace-nowrap tabular-nums" align="center"><a href="http://www.sec.gov/Archives/edgar/data/320193/000163198225000011/xslF345X05/wk-form4_1762990206.xml" class="tab-link" target="_blank">Nov 12 06:30 PM</a></td></tr><tr class="fv-insider-row is-sale-2" valign="top"><td><a href="insidertrading?oc=2050912&tc=7" class="tab-link">Parekh Kevan</td><td style="white-space:nowrap">Senior Vice President, CFO</td><td>Oct 16 '25</td><td class="transaction" style="white-space:nowrap" align="center"><span>Sale</span></td><td class="value" align="right">247.39</td><td class="value" align="right">4,199</td><td class="value" align="right">1,038,787</td><td class="value" align="right">8,765</td><td class="whitespace-nowrap tabular-nums" align="center"><a href="http://www.sec.gov/Archives/edgar/data/320193/000205091225000008/xslF345X05/wk-form4_1760740266.xml" class="tab-link" target="_blank">Oct 17 06:31 PM</a></td></tr><tr class="fv-insider-row is-proposedSale-2" valign="top"><td><a href="insidertrading?oc=2050912&tc=7" class="tab-link">KEVAN PAREKH</td><td style="white-space:nowrap">Officer</td><td>Oct 16 '25</td><td class="transaction" style="white-space:nowrap" align="center"><span>Proposed Sale</span></td><td class="value" align="right">249.34</td><td class="value" align="right">4,199</td><td class="value" align="right">1,046,979</td><td class="value" align="right"></td><td class="whitespace-nowrap tabular-nums" align="center"><a href="http://www.sec.gov/Archives/edgar/data/320193/000195004725008030/xsl144X01/primary_doc.xml" class="tab-link" target="_blank">Oct 16 04:23 PM</a></td></tr><tr class="fv-insider-row is-sale-2" valign="top"><td><a href="insidertrading?oc=1214156&tc=7" class="tab-link">COOK TIMOTHY D</td><td style="white-space:nowrap">Chief Executive Officer</td><td>Oct 02 '25</td><td class="transaction" style="white-space:nowrap" align="center"><span>Sale</span></td><td class="value" align="right">256.81</td><td class="value" align="right">129,963</td><td class="value" align="right">33,375,723</td><td class="value" align="right">3,280,295</td><td class="whitespace-nowrap tabular-nums" align="center"><a href="http://www.sec.gov/Archives/edgar/data/320193/000121415625000011/xslF345X05/wk-form4_1759530830.xml" class="tab-link" target="_blank">Oct 03 06:33 PM</a></td></tr><tr class="fv-insider-row is-sale-2" valign="top"><td><a href="insidertrading?oc=1767094&tc=7" class="tab-link">O'BRIEN DEIRDRE</td><td style="white-space:nowrap">Senior Vice President</td><td>Oct 02 '25</td><td class="transaction" style="white-space:nowrap" align="center"><span>Sale</span></td><td class="value" align="right">257.39</td><td class="value" align="right">43,013</td><td class="value" align="right">11,071,078</td><td class="value" align="right">136,687</td><td class="whitespace-nowrap tabular-nums" align="center"><a href="http://www.sec.gov/Archives/edgar/data/320193/000176709425000009/xslF345X05/wk-form4_1759530744.xml" class="tab-link" target="_blank">Oct 03 06:32 PM</a></td></tr><tr class="fv-insider-row is-sale-2" valign="top"><td><a href="insidertrading?oc=1462356&tc=7" class="tab-link">Adams Katherine L.</td><td style="white-space:nowrap">SVP, GC and Secretary</td><td>Oct 02 '25</td><td class="transaction" style="white-space:nowrap" align="center"><span>Sale</span></td><td class="value" align="right">256.79</td><td class="value" align="right">47,125</td><td class="value" align="right">12,101,154</td><td class="value" align="right">179,158</td><td class="whitespace-nowrap tabular-nums" align="center"><a href="http://www.sec.gov/Archives/edgar/data/320193/000146235625000010/xslF345X05/wk-form4_1759530624.xml" class="tab-link" target="_blank">Oct 03 06:30 PM</a></td></tr><tr class="fv-insider-row is-proposedSale-2" valign="top"><td><a href="insidertrading?oc=1462356&tc=7" class="tab-link">KATHERINE L ADAMS</td><td style="white-space:nowrap">Officer</td><td>Oct 02 '25</td><td class="transaction" style="white-space:nowrap" align="center"><span>Proposed Sale</span></td><td class="value" align="right">255.45</td><td class="value" align="right">47,125</td><td class="value" align="right">12,038,081</td><td class="value" align="right"></td><td class="whitespace-nowrap tabular-nums" align="center"><a href="http://www.sec.gov/Archives/edgar/data/320193/000195004725007713/xsl144X01/primary_doc.xml" class="tab-link" target="_blank">Oct 02 04:25 PM</a></td></tr><tr class="fv-insider-row is-proposedSale-2" valign="top"><td><a href="insidertrading?oc=1767094&tc=7" class="tab-link">O'BRIEN DEIRDRE</td><td style="white-space:nowrap">Officer</td><td>Oct 02 '25</td><td class="transaction" style="white-space:nowrap" align="center"><span>Proposed Sale</span></td><td class="value" align="right">257.38</td><td class="value" align="right">43,013</td><td class="value" align="right">11,070,897</td><td class="value" align="right"></td><td class="whitespace-nowrap tabular-nums" align="center"><a href="http://www.sec.gov/Archives/edgar/data/320193/000196922325000824/xsl144X01/primary_doc.xml" class="tab-link" target="_blank">Oct 02 04:10 PM</a></td></tr><tr class="fv-insider-row is-proposedSale-2" valign="top"><td><a href="insidertrading?oc=1214156&tc=7" class="tab-link">COOK TIMOTHY D</td><td style="white-space:nowrap">Officer</td><td>Oct 02 '25</td><td class="transaction" style="white-space:nowrap" align="center"><span>Proposed Sale</span></td><td class="value" align="right">256.81</td><td class="value" align="right">129,962</td><td class="value" align="right">33,375,268</td><td class="value" align="right"></td><td class="whitespace-nowrap tabular-nums" align="center"><a href="http://www.sec.gov/Archives/edgar/data/320193/000195917325006307/xsl144X01/primary_doc.xml" class="tab-link" target="_blank">Oct 02 04:09 PM</a></td></tr><tr class="fv-insider-row is-proposedSale-2" valign="top"><td><a href="insidertrading?oc=1496686&tc=7" class="tab-link">WILLIAMS JEFFREY E</td><td style="white-space:nowrap">Officer</td><td>Oct 02 '25</td><td class="transaction" style="white-space:nowrap" align="center"><span>Proposed Sale</span></td><td class="value" align="right">256.58</td><td class="value" align="right">43,013</td><td class="value" align="right">11,036,060</td><td class="value" align="right"></td><td class="whitespace-nowrap tabular-nums" align="center"><a href="http://www.sec.gov/Archives/edgar/data/320193/000196922325000822/xsl144X01/primary_doc.xml" class="tab-link" target="_blank">Oct 02 04:04 PM</a></td></tr><tr class="fv-insider-row is-sale-2" valign="top"><td><a href="insidertrading?oc=1214128&tc=7" class="tab-link">LEVINSON ARTHUR D</td><td style="white-space:nowrap">Director</td><td>Aug 28 '25</td><td class="transaction" style="white-space:nowrap" align="center"><span>Sale</span></td><td class="value" align="right">232.07</td><td class="value" align="right">90,000</td><td class="value" align="right">20,886,300</td><td class="value" align="right">4,069,576</td><td class="whitespace-nowrap tabular-nums" align="center"><a href="http://www.sec.gov/Archives/edgar/data/320193/000121412825000005/xslF345X05/wk-form4_1756506606.xml" class="tab-link" target="_blank">Aug 29 06:30 PM</a></td></tr><tr class="fv-insider-row is-proposedSale-2" valign="top"><td><a href="insidertrading?oc=1214128&tc=7" class="tab-link">LEVINSON ARTHUR D</td><td style="white-space:nowrap">Director</td><td>Aug 28 '25</td><td class="transaction" style="white-space:nowrap" align="center"><span>Proposed Sale</span></td><td class="value" align="right">232.07</td><td class="value" align="right">90,000</td><td class="value" align="right">20,885,966</td><td class="value" align="right"></td><td class="whitespace-nowrap tabular-nums" align="center"><a href="http://www.sec.gov/Archives/edgar/data/320193/000192109425001042/xsl144X01/primary_doc.xml" class="tab-link" target="_blank">Aug 28 04:03 PM</a></td></tr><tr class="fv-insider-row is-sale-2" valign="top"><td><a href="insidertrading?oc=1767094&tc=7" class="tab-link">O'BRIEN DEIRDRE</td><td style="white-space:nowrap">Senior Vice President</td><td>Aug 08 '25</td><td class="transaction" style="white-space:nowrap" align="center"><span>Sale</span></td><td class="value" align="right">223.20</td><td class="value" align="right">34,821</td><td class="value" align="right">7,772,047</td><td class="value" align="right">136,687</td><td class="whitespace-nowrap tabular-nums" align="center"><a href="http://www.sec.gov/Archives/edgar/data/320193/000176709425000005/xslF345X05/wk-form4_1755037816.xml" class="tab-link" target="_blank">Aug 12 06:30 PM</a></td></tr><tr class="fv-insider-row is-proposedSale-2" valign="top"><td><a href="insidertrading?oc=1767094&tc=7" class="tab-link">O'BRIEN DEIRDRE</td><td style="white-space:nowrap">Officer</td><td>Aug 08 '25</td><td class="transaction" style="white-space:nowrap" align="center"><span>Proposed Sale</span></td><td class="value" align="right">223.20</td><td class="value" align="right">34,821</td><td class="value" align="right">7,772,065</td><td class="value" align="right"></td><td class="whitespace-nowrap tabular-nums" align="center"><a href="http://www.sec.gov/Archives/edgar/data/320193/000196922325000586/xsl144X01/primary_doc.xml" class="tab-link" target="_blank">Aug 08 04:07 PM</a></td></tr><tr class="fv-insider-row is-sale-2" valign="top"><td><a href="insidertrading?oc=1631982&tc=7" class="tab-link">KONDO CHRIS</td><td style="white-space:nowrap">Principal Accounting Officer</td><td>May 12 '25</td><td class="transaction" style="white-space:nowrap" align="center"><span>Sale</span></td><td class="value" align="right">208.19</td><td class="value" align="right">4,486</td><td class="value" align="right">933,955</td><td class="value" align="right">15,533</td><td class="whitespace-nowrap tabular-nums" align="center"><a href="http://www.sec.gov/Archives/edgar/data/320193/000032019325000059/xslF345X05/wk-form4_1747261821.xml" class="tab-link" target="_blank">May 14 06:30 PM</a></td></tr><tr class="fv-insider-row is-sale-2" valign="top"><td><a href="insidertrading?oc=2050912&tc=7" class="tab-link">Parekh Kevan</td><td style="white-space:nowrap">Senior Vice President, CFO</td><td>Apr 23 '25</td><td class="transaction" style="white-space:nowrap" align="center"><span>Sale</span></td><td class="value" align="right">206.00</td><td class="value" align="right">4,570</td><td class="value" align="right">941,420</td><td class="value" align="right">4,569</td><td class="whitespace-nowrap tabular-nums" align="center"><a href="http://www.sec.gov/Archives/edgar/data/320193/000032019325000051/xslF345X05/wk-form4_1745620207.xml" class="tab-link" target="_blank">Apr 25 06:30 PM</a></td></tr><tr class="fv-insider-row is-proposedSale-2" valign="top"><td><a href="insidertrading?oc=2050912&tc=7" class="tab-link">KEVAN PAREKH</td><td style="white-space:nowrap">Officer</td><td>Apr 23 '25</td><td class="transaction" style="white-space:nowrap" align="center"><span>Proposed Sale</span></td><td class="value" align="right">199.74</td><td class="value" align="right">4,570</td><td class="value" align="right">912,812</td><td class="value" align="right"></td><td class="whitespace-nowrap tabular-nums" align="center"><a href="http://www.sec.gov/Archives/edgar/data/320193/000195004725002536/xsl144X01/primary_doc.xml" class="tab-link" target="_blank">Apr 23 04:22 PM</a></td></tr><tr class="fv-insider-row is-sale-2" valign="top"><td><a href="insidertrading?oc=1496686&tc=7" class="tab-link">WILLIAMS JEFFREY E</td><td style="white-space:nowrap">COO</td><td>Apr 02 '25</td><td class="transaction" style="white-space:nowrap" align="center"><span>Sale</span></td><td class="value" align="right">224.01</td><td class="value" align="right">35,493</td><td class="value" align="right">7,950,691</td><td class="value" align="right">390,059</td><td class="whitespace-nowrap tabular-nums" align="center"><a href="http://www.sec.gov/Archives/edgar/data/320193/000032019325000045/xslF345X05/wk-form4_1743719610.xml" class="tab-link" target="_blank">Apr 03 06:33 PM</a></td></tr><tr class="fv-insider-row is-sale-2" valign="top"><td><a href="insidertrading?oc=1214156&tc=7" class="tab-link">COOK TIMOTHY D</td><td style="white-space:nowrap">Chief Executive Officer</td><td>Apr 02 '25</td><td class="transaction" style="white-space:nowrap" align="center"><span>Sale</span></td><td class="value" align="right">223.65</td><td class="value" align="right">108,136</td><td class="value" align="right">24,184,658</td><td class="value" align="right">3,280,295</td><td class="whitespace-nowrap tabular-nums" align="center"><a href="http://www.sec.gov/Archives/edgar/data/320193/000032019325000043/xslF345X05/wk-form4_1743719531.xml" class="tab-link" target="_blank">Apr 03 06:32 PM</a></td></tr><tr class="fv-insider-row is-sale-2" valign="top"><td><a href="insidertrading?oc=1462356&tc=7" class="tab-link">Adams Katherine L.</td><td style="white-space:nowrap">SVP, GC and Secretary</td><td>Apr 02 '25</td><td class="transaction" style="white-space:nowrap" align="center"><span>Sale</span></td><td class="value" align="right">223.67</td><td class="value" align="right">38,822</td><td class="value" align="right">8,683,252</td><td class="value" align="right">179,158</td><td class="whitespace-nowrap tabular-nums" align="center"><a href="http://www.sec.gov/Archives/edgar/data/320193/000032019325000042/xslF345X05/wk-form4_1743719480.xml" class="tab-link" target="_blank">Apr 03 06:31 PM</a></td></tr><tr class="fv-insider-row is-proposedSale-2" valign="top"><td><a href="insidertrading?oc=1462356&tc=7" class="tab-link">KATHERINE L ADAMS</td><td style="white-space:nowrap">Officer</td><td>Apr 02 '25</td><td class="transaction" style="white-space:nowrap" align="center"><span>Proposed Sale</span></td><td class="value" align="right">223.19</td><td class="value" align="right">38,822</td><td class="value" align="right">8,664,682</td><td class="value" align="right"></td><td class="whitespace-nowrap tabular-nums" align="center"><a href="http://www.sec.gov/Archives/edgar/data/320193/000195004725002338/xsl144X01/primary_doc.xml" class="tab-link" target="_blank">Apr 02 04:26 PM</a></td></tr><tr class="fv-insider-row is-proposedSale-2" valign="top"><td><a href="insidertrading?oc=1496686&tc=7" class="tab-link">WILLIAMS JEFFREY E</td><td style="white-space:nowrap">Officer</td><td>Apr 02 '25</td><td class="transaction" style="white-space:nowrap" align="center"><span>Proposed Sale</span></td><td class="value" align="right">224.01</td><td class="value" align="right">35,493</td><td class="value" align="right">7,950,684</td><td class="value" align="right"></td><td class="whitespace-nowrap tabular-nums" align="center"><a href="http://www.sec.gov/Archives/edgar/data/320193/000196922325000218/xsl144X01/primary_doc.xml" class="tab-link" target="_blank">Apr 02 04:14 PM</a></td></tr><tr class="fv-insider-row is-proposedSale-2" valign="top"><td><a href="insidertrading?oc=1214156&tc=7" class="tab-link">COOK TIMOTHY D</td><td style="white-space:nowrap">Officer</td><td>Apr 02 '25</td><td class="transaction" style="white-space:nowrap" align="center"><span>Proposed Sale</span></td><td class="value" align="right">223.65</td><td class="value" align="right">108,136</td><td class="value" align="right">24,184,498</td><td class="value" align="right"></td><td class="whitespace-nowrap tabular-nums" align="center"><a href="http://www.sec.gov/Archives/edgar/data/320193/000195917325002460/xsl144X01/primary_doc.xml" class="tab-link" target="_blank">Apr 02 04:12 PM</a></td></tr><tr class="fv-insider-row is-sale-2" valign="top"><td><a href="insidertrading?oc=1214128&tc=7" class="tab-link">LEVINSON ARTHUR D</td><td style="white-space:nowrap">Director</td><td>Feb 03 '25</td><td class="transaction" style="white-space:nowrap" align="center"><span>Sale</span></td><td class="value" align="right">226.35</td><td class="value" align="right">1,516</td><td class="value" align="right">343,147</td><td class="value" align="right">4,159,576</td><td class="whitespace-nowrap tabular-nums" align="center"><a href="http://www.sec.gov/Archives/edgar/data/320193/000032019325000019/xslF345X05/wk-form4_1738711997.xml" class="tab-link" target="_blank">Feb 04 06:33 PM</a></td></tr><tr class="fv-insider-row is-proposedSale-2" valign="top"><td><a href="insidertrading?oc=1214128&tc=7" class="tab-link">LEVINSON ARTHUR D</td><td style="white-space:nowrap">Director</td><td>Feb 03 '25</td><td class="transaction" style="white-space:nowrap" align="center"><span>Proposed Sale</span></td><td class="value" align="right">226.35</td><td class="value" align="right">1,516</td><td class="value" align="right">343,147</td><td class="value" align="right"></td><td class="whitespace-nowrap tabular-nums" align="center"><a href="http://www.sec.gov/Archives/edgar/data/320193/000192109425000087/xsl144X01/primary_doc.xml" class="tab-link" target="_blank">Feb 03 04:18 PM</a></td></tr><tr class="fv-insider-row is-sale-2" valign="top"><td><a href="insidertrading?oc=1496686&tc=7" class="tab-link">WILLIAMS JEFFREY E</td><td style="white-space:nowrap">COO</td><td>Dec 16 '24</td><td class="transaction" style="white-space:nowrap" align="center"><span>Sale</span></td><td class="value" align="right">249.97</td><td class="value" align="right">100,000</td><td class="value" align="right">24,997,395</td><td class="value" align="right">389,944</td><td class="whitespace-nowrap tabular-nums" align="center"><a href="http://www.sec.gov/Archives/edgar/data/320193/000032019324000132/xslF345X05/wk-form4_1734564614.xml" class="tab-link" target="_blank">Dec 18 06:30 PM</a></td></tr><tr class="fv-insider-row is-proposedSale-2" valign="top"><td><a href="insidertrading?oc=1496686&tc=7" class="tab-link">WILLIAMS JEFFREY E</td><td style="white-space:nowrap">Officer</td><td>Dec 16 '24</td><td class="transaction" style="white-space:nowrap" align="center"><span>Proposed Sale</span></td><td class="value" align="right">249.97</td><td class="value" align="right">100,000</td><td class="value" align="right">24,997,440</td><td class="value" align="right"></td><td class="whitespace-nowrap tabular-nums" align="center"><a href="http://www.sec.gov/Archives/edgar/data/320193/000197314124000617/xsl144X01/primary_doc.xml" class="tab-link" target="_blank">Dec 16 04:15 PM</a></td></tr></table>
</td>
</tr>
<table style="margin: 21px auto 14px auto" cellpadding="0" cellspacing="0" border="0">
<tr class="flex">
<td class="fullview-links flex items-center" align="left" valign="center">
<a target="_blank" class="tab-link" href="https://finance.yahoo.com/quote/AAPL" rel="nofollow" onclick="window.gtag && window.gtag('event', 'click', { event_category: 'fvlinksQuote', event_label: 'yahoo' });">open in yahoo</a>&nbsp;|&nbsp<a target="_blank" class="tab-link" href="https://www.reuters.com/companies/AAPL.OQ" rel="nofollow" onclick="window.gtag && window.gtag('event', 'click', { event_category: 'fvlinksQuote', event_label: 'reuters' });">open in reuters</a>&nbsp;|&nbsp<a target="_blank" class="tab-link" href="https://www.marketwatch.com/investing/stock/aapl" rel="nofollow" onclick="window.gtag && window.gtag('event', 'click', { event_category: 'fvlinksQuote', event_label: 'marketwatch' });">open in marketwatch</a>&nbsp;|&nbsp<a target="_blank" class="tab-link" href="https://www.google.com/finance/quote/AAPL:NASDAQ" rel="nofollow" onclick="window.gtag && window.gtag('event', 'click', { event_category: 'fvlinksQuote', event_label: 'google' });">open in google</a>&nbsp;|&nbsp<a target="_blank" class="tab-link" href="https://www.sec.gov/edgar/browse/?CIK=320193" rel="nofollow" onclick="window.gtag && window.gtag('event', 'click', { event_category: 'fvlinksQuote', event_label: 'edgar' });">open in EDGAR</a></td>
</tr>
</table>
</table>
</td></tr>
</table>
</div>
</div>
</div><div class="my-3"><div id="IC_D_3x3_1"class="relative overflow-hidden flex items-center justify-center w-full mx-auto" style="width:970px;height:250px;max-height:250px"></div></div>
            <div class="footer" style="margin-top: 20px;padding-bottom: 215px">
                <div class="footer_links">
                    <a class="tab-link" href="/affiliate.ashx">Affiliate</a>
                    <span class="footer_dot"> • </span>
                    <a class="tab-link" href="/advertise.ashx">Advertise</a>
                    <span class="footer_dot"> • </span>
                    <a class="tab-link" href="/careers">Careers</a>
                    <span class="footer_dot"> • </span>
                    <a class="tab-link" href="/contact.ashx">Contact</a>
                    <span class="footer_dot"> • </span>
                    <a class="tab-link" href="/blog">Blog</a>
                    <span class="footer_dot"> • </span>
                    <a class="tab-link" href="/help/screener.ashx">Help</a>
                    <span class="footer_dot"> • </span>
                    <a class="tab-link" href="/privacy.ashx">Privacy</a>
                    <span class="footer_dot"> • </span>
                    <a class="tab-link" href="https://x.com/finviz_com" target="_blank">Follow us on X</a><span class="footer_dot"> • </span> <a id="ic_us_privacy" class="tab-link relative overflow-hidden [&>a]:absolute [&>a]:inset-0 [&>a]:-indent-[9999em]" href="#">Do Not Sell My Personal Information</a>    </div>
    Quotes delayed 15 minutes for NASDAQ, NYSE and AMEX.
    <br>
    Copyright © 2007-2025 Finviz.com. All Rights Reserved.
    
</div><script>SearchFocus();</script><script src="/assets/dist/9215.v1.4186333b.js" onerror="window.handleScriptNotLoaded(this)"></script><script src="/assets/dist/4417.v1.de0121af.js" onerror="window.handleScriptNotLoaded(this)"></script><script src="/assets/dist/463.v1.81aa98cd.js" onerror="window.handleScriptNotLoaded(this)"></script><script src="/assets/dist/3404.v1.fd2315ec.js" onerror="window.handleScriptNotLoaded(this)"></script><script src="/assets/dist/7470.v1.3421c138.js" onerror="window.handleScriptNotLoaded(this)"></script><script src="/assets/dist/3654.v1.696c68cc.js" onerror="window.handleScriptNotLoaded(this)"></script><script src="/assets/dist/3772.v1.b198d5a5.js" onerror="window.handleScriptNotLoaded(this)"></script><script src="/assets/dist/877.v1.3af58ae5.js" onerror="window.handleScriptNotLoaded(this)"></script><script src="/assets/dist/8949.v1.494e6780.js" onerror="window.handleScriptNotLoaded(this)"></script><script src="/assets/dist/7052.v1.828e2e50.js" onerror="window.handleScriptNotLoaded(this)"></script><script src="/assets/dist/2698.v1.5f6434e5.js" onerror="window.handleScriptNotLoaded(this)"></script><script src="/assets/dist/6019.v1.f4bb9181.js" onerror="window.handleScriptNotLoaded(this)"></script><script src="/assets/dist/2239.v1.e6d117fd.js" onerror="window.handleScriptNotLoaded(this)"></script><script src="/assets/dist/main.v1.1f88c5dc.js" onerror="window.handleScriptNotLoaded(this)"></script><link rel="preload" as="script" href="/assets/dist/recent_quotes.v1.c908db63.js" data-chunk-id="recent_quotes"><script>
            function FinvizReady(fn) {
              if (document.readyState != 'loading'){
                fn();
              } else {
                document.addEventListener('DOMContentLoaded', fn);
              }
            }

            (typeof StocktwitsInit === 'function' && FinvizReady(StocktwitsInit));
            (typeof FinvizSettings === 'object' && (FinvizSettings.quoteSearchExt = '&ty=c&ta=1&p=d'));
        </script>
        <div id="js-set-search-ext-argument" class="hidden" data-set-search-ext-argument="&ty=c&ta=1&p=d"></div>
            <script>(function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':
            new Date().getTime(),event:'gtm.js'});var f=d.getElementsByTagName(s)[0],
            j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src=
            'https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);
            })(window,document,'script','dataLayer','GTM-537M973G');</script>
            <script>
              function getSystemTheme() {
                if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
                  return 'Dark';
                }
                else if (window.matchMedia && window.matchMedia('(prefers-color-scheme: light)').matches) {
                  return 'Light';
                }
                return 'No Preference';
              }

              var systemTheme = getSystemTheme()

              const headlessChrome = navigator.userAgent.includes('HeadlessChrome')
              const webdriver = navigator.webdriver

              let cdp = false
              try {
                let accessed = false
                const e = new window.Error('ignore')
                window.Object.defineProperty(e, 'stack', {
                  configurable: false,
                  enumerable: false,
                  get: function () {
                    accessed = true
                    return ''
                  },
                })
                // This is part of the detection and shouldn't be deleted
                window.console.debug(e)
                cdp = accessed
              } catch {}

              gtag('js', new Date());

              var fGaM = {
                'dimension1': 'NotLoggedIn',
                'dimension3': window.devicePixelRatio,
                'layoutTheme': 'dark',
                'systemTheme': systemTheme,
                'bundle': 'modern',
                'prefTheme': 'dark',
                'themeFlag': 'modern',
                innerWidth: window.innerWidth,
                innerHeight: window.innerHeight,
                webdriver: webdriver,
                cdp: cdp,
                isBot: headlessChrome || webdriver || cdp,
                icAdsVariant: 'control',
              };

              gtag('config', 'G-ZT9VQEWD4N', fGaM);
              
            </script>
            <script type="text/javascript">
        window._qevents = window._qevents || [];

        (function() {
            var elem = document.createElement('script');
            elem.src = (document.location.protocol == "https:" ? "https://secure" : "http://edge") + ".quantserve.com/quant.js";
            elem.async = true;
            elem.type = "text/javascript";
            var scpt = document.getElementsByTagName('script')[0];
            scpt.parentNode.insertBefore(elem, scpt);
        })();

        window._qevents.push({
            qacct:"p-c2W8esUZ6Q8oA"
        });
    </script>
    <noscript>
        <div style="display:none;">
            <img src="//pixel.quantserve.com/pixel/p-c2W8esUZ6Q8oA.gif" border="0" height="1" width="1" alt="Quantcast"/>
        </div>
    </noscript><div id="IC_D_1x1_1"class="relative overflow-hidden flex items-center justify-center w-full mx-auto"></div><div id="modal-elite-ad" class="modal-elite-ad">
                            <div id="modal-elite-ad_content" class="modal-elite-ad_content">
			                    <button id="modal-elite-ad-close" type="button" class="modal-elite-ad_close">×</button>

                                <!--<div id="modal-elite-ad-content-0" style="display: none">
			                        <h2>Ever heard of Finviz*Elite?</h2>
                                    <p>
                                        Our premium service offers you real-time quotes, advanced visualizations, technical studies, and much more.<br>
                                        Become Elite and make informed financial decisions.
                                    </p>
                                    <a href="/elite?utm_source=finviz&utm_medium=banner&utm_campaign=modal-0" id="modal-elite-ad-btn-0" class="" target="_blank">Find out more</a>
                                </div>-->

                                <div id="modal-elite-ad-content-1" style="display: block">
			                        <h2>Upgrade your FINVIZ experience</h2>
                                    <p>
                                        Join thousands of traders who make more informed decisions with&nbsp;our&nbsp;premium features.
                                        Real-time quotes, advanced&nbsp;visualizations, backtesting, and much more.
                                    </p>
                                    <a href="/elite?utm_source=finviz&utm_medium=banner&utm_campaign=modal-1" id="modal-elite-ad-btn-1" class="modal-elite_button" target="_blank">Learn more about FINVIZ*Elite</a>
                                </div>
                            </div>
                         </div><script src="/assets/dist/script/pv.v1.27fa030f.js" async></script><script defer>window.renderScriptNotLoaded();</script>
</body>
</html>
