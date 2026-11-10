"""AI 교육추천 HTML/CSS/JavaScript 화면."""

_RECOMMEND_STYLE = r"""
:root{--ink:#29352b;--muted:#92988b;--line:#e3e5db;--paper:#f9f8f4;--yellow:#facd40;--green:#7d9970;--pale:#edf3e7}
*{box-sizing:border-box}body{margin:0;background:var(--paper);color:var(--ink);font-family:"Malgun Gothic","Apple SD Gothic Neo",sans-serif;font-size:18px;line-height:1.6}
button,input,select{font:inherit;color:inherit}button,select{cursor:pointer}button{touch-action:manipulation}a{color:inherit;text-decoration:none}button:disabled{cursor:default;opacity:.35}
button:focus-visible,a:focus-visible,input:focus-visible,select:focus-visible{outline:3px solid #c99c1c;outline-offset:4px}
.wrap{width:88.8%;max-width:2130px;margin:0 auto}.header{background:#fff;border-bottom:1px solid var(--line);height:104px}
.header .wrap{height:100%;display:flex;align-items:center;gap:40px}.brand{border:0;background:none;padding:0;display:flex;align-items:center;gap:13px;white-space:nowrap;font-size:29px;font-weight:800;letter-spacing:-1.2px}.brand svg{width:44px;height:44px;flex:none}
.nav{display:flex;align-items:stretch;gap:62px;justify-content:center;flex:1;height:100%;padding-left:75px}.nav button{position:relative;background:none;border:0;padding:0;font-size:20px;letter-spacing:1px;color:#858b7e;white-space:nowrap}.nav .active{font-weight:800;color:var(--ink)}.nav .active:after{content:"";position:absolute;height:4px;background:var(--yellow);left:0;right:0;bottom:0}
.account{display:flex;align-items:center;gap:50px;margin-left:auto;white-space:nowrap;color:#92988b;font-size:18px}.mypage{background:#fff;border:1px solid var(--line);border-radius:13px;font-size:21px;padding:10px 41px;min-width:184px;height:53px;color:#42503f}
.hero{padding:33px 0 34px}.eyebrow{font-size:14px;font-weight:700;color:#8b9284;margin:0 0 15px;letter-spacing:.3px}.hero h1{font-size:40px;font-weight:800;letter-spacing:1px;margin:0 0 2px;line-height:1.35}.hero .subtitle{font-size:22px;color:#8c9285;letter-spacing:.3px;margin:0}
.layout{display:grid;grid-template-columns:352px minmax(0,1fr);gap:30px;align-items:start}.sidebar{background:#fff;border:1px solid var(--line);border-radius:20px;padding:26px 28px 36px;min-height:900px}.sidebar-head{display:flex;align-items:center;justify-content:space-between;margin-bottom:30px}.sidebar h2{font-size:27px;font-weight:700;letter-spacing:1px;margin:0}.reset{border:0;background:none;color:#aaaE9f;font-size:16px;padding:0}
.field{min-width:0;display:block;margin:0 0 34px}.field>span{display:block;font-size:19px;font-weight:700;letter-spacing:.3px;margin-bottom:10px}.select-wrap{position:relative}.select-wrap:after{content:"⌄";position:absolute;right:21px;top:12px;color:#64705c;pointer-events:none}
select{width:100%;height:58px;padding:10px 42px 10px 17px;border:1px solid #dfe3d5;border-radius:12px;background:#fff;appearance:none;font-size:20px}.apply{background:var(--yellow);border:0;border-radius:13px;width:100%;height:54px;font-weight:800;font-size:21px;letter-spacing:.7px;margin-top:35px}.sidebar-note{font-size:13px;line-height:1.8;color:#a4a99a;margin:37px 0 0}
.search{height:74px;border:1px solid var(--line);background:#fff;border-radius:20px;display:flex;align-items:center;padding:9px 20px 9px 27px;gap:15px}.search input{border:0;background:none;outline:none;min-width:0;flex:1;font-size:20px;letter-spacing:.5px}.search input::placeholder{color:#aaae9f}.search button{background:var(--yellow);border:0;border-radius:14px;width:122px;height:53px;font-size:21px;font-weight:800}
.results-head{display:flex;align-items:center;justify-content:space-between;margin:29px 0 13px}.results-head h2{font-size:25px;letter-spacing:.7px;margin:0;font-weight:800}.sort{position:relative;margin-right:78px}.sort select{width:120px;height:40px;font-size:18px;border:0;background:transparent;color:#9ba08f;padding:0 25px 0 0;text-align:right}.sort:after{content:"⌄";position:absolute;right:0;top:5px;font-size:17px;color:#9ba08f;pointer-events:none}
.chips{display:flex;gap:47px;flex-wrap:wrap;align-items:center;min-height:35px;margin:0 0 27px}.chip{background:#fff5d7;color:#b0aa88;border-radius:30px;font-size:16px;padding:4px 16px;line-height:1.6}.catalogue-note{font-size:12px;color:#9da590;margin:0 0 15px}.catalogue-note:empty{display:none}
.cards{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:23px 28px;min-height:548px;align-content:start}.card{background:#fff;border:1px solid #e0e3d7;border-radius:20px;padding:20px 23px 22px;min-height:263px;position:relative;display:flex;flex-direction:column}.card-top{display:flex;align-items:center;justify-content:space-between;gap:10px}.badge{background:var(--pale);color:#8aa27b;border-radius:30px;padding:4px 15px;font-size:16px;line-height:1.6;max-width:85%;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.heart{border:0;background:none;color:#929d87;font-size:29px;font-family:Arial,sans-serif;line-height:1.2;padding:0 6px}.heart[aria-pressed="true"]{color:#a75e45}
.card h3{font-size:25px;letter-spacing:.1px;line-height:1.5;margin:18px 0 7px;font-weight:700;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}.provider{color:#9aa08f;font-size:17px;margin:0 0 9px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.card-meta{font-size:18px;margin:0 0 14px;letter-spacing:.2px}.tags{font-size:16px;color:#8ba17d;display:flex;flex-wrap:wrap;gap:10px;padding-right:120px;margin-top:auto}.tags span+span:before{content:"/";margin-right:10px;color:#a6b29b}.details{position:absolute;right:65px;bottom:25px;color:#a8ae9f;border:0;background:none;font-size:17px;padding:0}.details:hover{color:#6a8556}.pagination{display:flex;justify-content:center;align-items:center;gap:9px;min-height:49px;margin:70px 0 14px}.pagination button{border:1px solid var(--line);border-radius:13px;background:#fff;font-size:19px;min-width:50px;height:48px;padding:4px 16px}.pagination .selected{background:var(--yellow);border-color:var(--yellow);font-weight:700}.pagination .dots{padding:0 3px;color:var(--muted);font-size:15px}
footer{display:flex;justify-content:space-between;gap:20px;border-top:1px solid #dfe3d6;padding:20px 0 27px;margin-top:40px;font-size:14px;color:#a2a896;letter-spacing:.4px}footer a{color:#8c9780}
.empty{grid-column:1/-1;min-height:548px;border:1px dashed #d9dfcc;background:#f4f6ed;border-radius:18px;padding:35px;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center}.empty h3{font-size:23px;margin:0 0 9px}.empty p{color:#8f9b83;font-size:16px;max-width:500px;margin:0 0 18px}.empty button{border:1px solid #ccd7bd;background:#fff;border-radius:10px;padding:9px 20px;font-size:16px}.loading{opacity:.55;pointer-events:none}.error-note{color:#ae7551}
dialog{border:1px solid #e0e5d7;background:var(--paper);border-radius:21px;box-shadow:0 20px 80px #22351830;width:min(760px,calc(100% - 35px));max-height:88vh;padding:30px;color:var(--ink)}dialog::backdrop{background:#1a2c2366;backdrop-filter:blur(3px)}.modal-top{display:flex;align-items:center;justify-content:space-between;gap:20px}.modal-top p{font-size:12px;letter-spacing:2px;color:#8e9a80;margin:0}.close{border:0;background:none;font-size:31px;line-height:1;color:#87977b}.modal-title{font-size:26px;line-height:1.5;margin:18px 0 15px}.detail-grid{display:grid;grid-template-columns:120px 1fr;gap:12px;font-size:15px;border-top:1px solid var(--line);padding-top:20px}.detail-grid dt{color:#8b977d}.detail-grid dd{margin:0;overflow-wrap:anywhere}.detail-note{padding:14px;border-radius:10px;background:#f5efd7;color:#8a8060;font-size:13px}.primary-link{display:block;background:var(--yellow);padding:12px;border-radius:12px;text-align:center;font-weight:700;font-size:17px;margin-top:20px}.toast{position:fixed;bottom:30px;left:50%;transform:translate(-50%,15px);background:#35482f;color:white;padding:12px 23px;border-radius:11px;font-size:14px;opacity:0;pointer-events:none;transition:.2s;z-index:5;max-width:90vw}.toast.show{opacity:1;transform:translate(-50%,0)}
@media(min-width:2100px){body{font-size:23px}.header{height:134px}.header .wrap{gap:50px}.brand{font-size:37px;gap:17px}.brand svg{width:56px;height:56px}.nav{gap:79px;padding-left:96px}.nav button{font-size:26px}.account{gap:64px;font-size:23px}.mypage{font-size:27px;height:68px;min-width:236px}.hero{padding:43px 0 44px}.eyebrow{font-size:18px;margin-bottom:19px}.hero h1{font-size:53px}.hero .subtitle{font-size:28px}.layout{grid-template-columns:452px minmax(0,1fr);gap:39px}.sidebar{padding:34px 36px 46px;min-height:962px}.sidebar h2{font-size:35px}.sidebar-head{margin-bottom:39px}.reset{font-size:20px}.field{margin-bottom:44px}.field>span{font-size:24px;margin-bottom:13px}select{height:74px;font-size:26px;padding-left:22px}.select-wrap:after{top:18px;right:26px}.apply{height:69px;font-size:27px;margin-top:45px}.sidebar-note{font-size:16px;margin-top:47px}.search{height:95px;padding:12px 26px 12px 35px}.search input{font-size:26px}.search button{width:156px;height:68px;font-size:27px}.results-head{margin:37px 0 17px}.results-head h2{font-size:32px}.sort{margin-right:100px}.sort select{font-size:23px;width:154px}.chips{gap:60px;min-height:45px;margin-bottom:35px}.chip{font-size:20px;padding:5px 20px}.cards{gap:30px 36px;min-height:702px}.card{padding:26px 30px 28px;min-height:337px}.badge{font-size:20px;padding:5px 19px}.heart{font-size:37px}.card h3{font-size:32px;margin-top:23px}.provider{font-size:22px}.card-meta{font-size:23px;margin-bottom:18px}.tags{font-size:20px;padding-right:154px}.details{font-size:22px;right:83px;bottom:32px}.pagination{margin-top:90px;gap:12px}.pagination button{height:62px;min-width:64px;font-size:24px}footer{font-size:18px;margin-top:51px;padding:26px 0 35px}}
@media(max-width:1550px){.header .wrap{gap:25px}.nav{gap:35px;padding-left:15px}.account{gap:25px}.brand{font-size:25px}.nav button{font-size:17px}.account{font-size:15px}.mypage{font-size:17px;min-width:145px;padding:10px 20px}.layout{grid-template-columns:290px minmax(0,1fr);gap:25px}.sidebar{padding:25px 23px;min-height:690px}.sidebar h2{font-size:23px}.field>span{font-size:17px}select{font-size:17px}.hero h1{font-size:35px}.hero .subtitle{font-size:18px}.card h3{font-size:20px}.provider{font-size:14px}.card-meta{font-size:15px}.badge,.tags{font-size:13px}.details{font-size:14px;right:25px}.card{min-height:245px}.cards{gap:20px;min-height:510px}.sort{margin-right:25px}.search input{font-size:17px}.chips{gap:22px}}
@media(max-width:1120px){.wrap{width:92%}.header{height:auto;min-height:100px}.header .wrap{flex-wrap:wrap;padding-top:18px;gap:10px}.nav{order:3;width:100%;flex:none;padding:0;height:48px;gap:30px;justify-content:center}.nav button{font-size:14px}.account{margin-left:auto}.brand{font-size:23px}.brand svg{height:36px;width:36px}.mypage{height:40px;min-width:120px;font-size:15px}.hero{padding-top:30px}.hero h1{font-size:31px}.hero .subtitle{font-size:16px}.layout{grid-template-columns:235px minmax(0,1fr);gap:20px}.sidebar{padding:20px 18px;min-height:650px}.sidebar h2{font-size:21px}.reset{font-size:13px}.field>span{font-size:15px}select{font-size:14px;height:50px}.apply{font-size:17px}.sidebar-note{font-size:11px}.cards{gap:15px}.card{padding:16px;min-height:260px}.card h3{font-size:18px}.card-meta{font-size:13px}.tags{padding-right:0;margin-bottom:28px;font-size:11px}.details{bottom:15px;font-size:12px;right:20px}.results-head h2{font-size:20px}.chip{font-size:13px}.search{padding-left:17px;height:65px}.search button{height:45px;width:85px;font-size:17px}.search input{font-size:14px}.sort{margin-right:0}.sort select{font-size:14px}.pagination{margin-top:35px}footer{font-size:11px}}
@media(max-width:760px){.wrap{width:92%}.header .wrap{gap:8px}.account{gap:10px;font-size:12px}.mypage{font-size:13px;min-width:90px;padding:5px 12px}.brand{font-size:21px;gap:7px}.nav{gap:22px;justify-content:space-between;overflow-x:auto}.nav button{font-size:12px}.hero{padding:25px 0}.eyebrow{font-size:10px;margin-bottom:10px}.hero h1{font-size:25px;letter-spacing:-.8px}.hero .subtitle{font-size:13px;letter-spacing:0}.layout{display:flex;flex-direction:column;gap:20px}.sidebar{width:100%;min-height:0;padding:18px}.sidebar-head{margin-bottom:16px}.sidebar h2{font-size:20px}.filter-form{display:grid;grid-template-columns:1fr 1fr;gap:12px}.field{margin:0}.field>span{font-size:12px;margin-bottom:5px}select{font-size:13px;height:44px;padding-left:12px}.select-wrap:after{top:9px;right:14px}.apply{margin:0;height:44px;font-size:15px;align-self:end}.sidebar-note{margin:12px 0 0;font-size:10px}.result-area{width:100%}.search{height:58px;border-radius:14px;padding:6px 9px 6px 14px}.search input{font-size:13px}.search button{height:43px;width:67px;font-size:15px}.results-head{margin-top:22px;margin-bottom:9px}.results-head h2{font-size:19px}.chips{gap:9px;margin-bottom:17px;min-height:26px}.chip{font-size:11px;padding:3px 10px}.cards{grid-template-columns:1fr;min-height:0;gap:14px}.card{min-height:240px;padding:18px 20px}.card h3{font-size:20px;margin-top:14px}.provider{font-size:13px}.card-meta{font-size:14px}.badge{font-size:12px}.tags{font-size:12px;margin-bottom:22px}.details{font-size:13px;bottom:17px}.pagination{margin-top:25px}.pagination button{min-width:38px;height:40px;font-size:15px;padding:4px 10px}.empty{min-height:330px;padding:25px}.empty h3{font-size:19px}.empty p{font-size:13px}footer{flex-direction:column;gap:5px;font-size:10px;margin-top:30px}.detail-grid{grid-template-columns:85px 1fr;font-size:12px;gap:10px}.modal-title{font-size:21px}}
@media(prefers-reduced-motion:reduce){*{transition:none!important}}
"""
_RECOMMEND_HEADER = r"""<header class="header"><div class="wrap">
<button class="brand" type="button" aria-label="취준나침반"><svg viewBox="0 0 44 44" aria-hidden="true"><circle cx="22" cy="22" r="22" fill="#facd40"/><path d="M31 8 25 24 13 35 19 19Z" fill="#29392b"/><path d="M19 19 25 24 22 21Z" fill="#fdf9d9"/></svg><span>취준나침반</span></button>
<nav class="nav" aria-label="주 메뉴"><button type="button">메인</button><button type="button">공고모음</button><button type="button" onclick="location.href='/training_posts'">교육모음</button><button type="button">적합도 분석</button><button type="button" class="active" aria-current="page">교육추천</button></nav>
<div class="account"><span>김나침님</span><button class="mypage" type="button">마이페이지</button></div>
</div></header>"""

RECOMMEND_STYLE = r"""
.rec-panel{position:relative;min-height:158px;border-radius:24px;background:#f5efd0;padding:26px 34px;display:flex;align-items:center;justify-content:space-between;gap:25px}
.rec-panel h2{font-size:25px;letter-spacing:.5px;margin:0 0 12px;font-weight:700}.gap-line{display:flex;align-items:center;gap:15px;flex-wrap:wrap;font-size:17px;color:#8d947f}.gap-label{margin-right:45px}.gap-pill{background:white;border-radius:30px;padding:4px 26px;min-width:138px;text-align:center;font-size:16px;color:#909889}.analysis-button{background:none;border:0;color:#607b4d;font-size:21px;white-space:nowrap;letter-spacing:.5px;font-weight:700;margin-right:275px}.analysis-button span{margin-left:12px}
.rec-heading{display:flex;align-items:center;gap:60px;margin:32px 0 26px;min-height:42px}.rec-heading h2{font-size:28px;letter-spacing:.8px;margin:0;white-space:nowrap}.rec-conditions{display:flex;gap:74px;flex:1;align-items:center}.rec-condition{border:0;background:#fff5d7;color:#a9a683;font-size:16px;border-radius:30px;padding:4px 16px}.rec-sort{margin-left:auto;margin-right:140px}.rec-sort select{height:40px;border:0;background:none;width:130px;padding:0 20px 0 0;font-size:18px;color:#909985;text-align:right}.rec-sort:after{right:0}
.rec-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:24px}.rec-card{background:#fff;border:1px solid #e0e3d7;border-radius:20px;min-height:410px;padding:24px 28px;display:flex;flex-direction:column}.rec-card-top{display:flex;align-items:center;justify-content:space-between}.rec-rank{font-size:32px;font-weight:700;color:#5b7849;line-height:1.6}.rec-card h3{font-size:24px;line-height:1.5;letter-spacing:.1px;margin:17px 0 8px;font-weight:700;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}.rec-card .provider{font-size:17px;margin:0 0 20px}.learning-badge{align-self:flex-start;background:#edf3e7;color:#879f78;border-radius:30px;padding:4px 14px;font-size:16px;line-height:1.6}.rec-reason{font-size:18px;line-height:1.8;color:#939b8a;margin:15px 0 23px;flex:1;display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden}.rec-meta{font-size:18px;margin:0 0 19px}.rec-detail{align-self:flex-start;background:none;border:0;padding:0;color:#698453;font-size:18px;font-weight:700;letter-spacing:.1px}.rec-placeholder{background:#fdfdf9}.rec-placeholder h3{color:#86917c}.rec-placeholder .rec-reason{color:#a3aa99}.rec-placeholder .rec-detail{font-size:16px}
.rec-certificates{margin-top:39px}.rec-certificates h2{font-size:28px;margin:0 0 16px;letter-spacing:.4px}.certificate-grid{display:grid;grid-template-columns:1fr 1fr;gap:24px}.certificate-card{border:1px solid #e0e3d7;border-radius:20px;background:#fff;padding:25px 28px;min-height:130px;text-align:left;position:relative;width:100%}.certificate-card h3{font-size:25px;margin:0 160px 8px 0;line-height:1.5}.certificate-card p{font-size:17px;color:#959e8b;margin:0;max-width:80%}.certificate-label{position:absolute;right:28px;top:28px;background:#fff5d7;color:#b0aa88;border-radius:30px;padding:4px 34px;font-size:16px}.rec-footnote{color:#9ba48f;font-size:12px;margin:12px 0 0;min-height:18px}
.ai-form label{display:block;font-size:14px;font-weight:700;margin-top:16px}.ai-form input,.ai-form textarea,.ai-form select{display:block;width:100%;border:1px solid #dce2d3;border-radius:10px;background:white;padding:10px 12px;font-size:14px;margin-top:6px;min-height:44px;height:auto}.ai-form textarea{resize:vertical;min-height:110px;line-height:1.6}.ai-row{display:grid;grid-template-columns:1fr 1fr;gap:15px}.ai-form .input-hint{font-size:12px;line-height:1.7;color:#8b967f;font-weight:400;margin:10px 0}.ai-submit{background:var(--yellow);border:0;border-radius:12px;width:100%;padding:12px;font-weight:700;margin-top:15px;font-size:17px}.example-fill{border:1px solid #dce2d3;border-radius:9px;background:white;padding:7px 12px;font-size:12px;margin-top:14px}.form-error{font-size:13px;color:#a1643b;line-height:1.7;margin-top:12px}.form-error:empty{display:none}.analysis-summary{font-size:15px;line-height:1.8}.gap-explanation{padding:12px 0;border-top:1px solid var(--line);font-size:14px}.gap-explanation strong{color:#607b4d}.gap-explanation p{color:#87927c;margin:5px 0}.analysis-source{white-space:pre-wrap;border-radius:10px;background:#f0f3e9;padding:13px;font-size:12px;color:#7e8a73;max-height:220px;overflow:auto}
.rec-explanation{flex:1;margin:15px 0 23px}.reason-label{display:block;font-size:13px;color:#698453;margin-bottom:5px;font-weight:700}.rec-explanation .rec-reason{margin:0;flex:none;-webkit-line-clamp:2}
@media(min-width:2100px){.rec-panel{min-height:203px;padding:33px 44px}.rec-panel h2{font-size:32px}.gap-line{font-size:22px;gap:19px}.gap-pill{font-size:20px;padding:5px 33px;min-width:177px}.gap-label{margin-right:58px}.analysis-button{font-size:27px;margin-right:352px}.rec-heading{margin:41px 0 33px;gap:77px}.rec-heading h2{font-size:36px}.rec-conditions{gap:95px}.rec-condition{font-size:20px;padding:5px 20px}.rec-sort{margin-right:180px}.rec-sort select{font-size:23px;width:166px}.rec-grid{gap:31px}.rec-card{min-height:525px;padding:31px 36px}.rec-rank{font-size:41px}.rec-card h3{font-size:31px;margin-top:22px}.rec-card .provider{font-size:22px;margin-bottom:26px}.learning-badge{font-size:20px}.rec-reason{font-size:23px;margin:19px 0 29px}.rec-meta{font-size:23px;margin-bottom:24px}.rec-detail{font-size:23px}.rec-certificates{margin-top:50px}.rec-certificates h2{font-size:36px;margin-bottom:20px}.certificate-grid{gap:31px}.certificate-card{padding:32px 36px;min-height:167px}.certificate-card h3{font-size:32px}.certificate-card p{font-size:22px}.certificate-label{font-size:20px;right:36px;top:36px}}
@media(max-width:1550px){.analysis-button{margin-right:80px;font-size:18px}.rec-panel h2{font-size:22px}.gap-label{margin-right:20px}.rec-heading{gap:35px}.rec-heading h2{font-size:25px}.rec-conditions{gap:25px}.rec-sort{margin-right:40px}.rec-card{padding:23px;min-height:420px}.rec-card h3{font-size:21px}.rec-card .provider{font-size:15px}.rec-reason{font-size:16px}.rec-meta,.rec-detail{font-size:16px}.learning-badge{font-size:14px}.certificate-card h3{font-size:21px;margin-right:130px}.certificate-card p{font-size:15px}.certificate-label{font-size:14px;padding:4px 22px}}
@media(max-width:1120px){.rec-panel{padding:23px}.rec-panel h2{font-size:20px}.analysis-button{margin-right:0;font-size:15px}.gap-line{font-size:13px;gap:8px}.gap-label{margin-right:10px}.gap-pill{font-size:12px;min-width:100px;padding:3px 14px}.rec-heading{gap:20px}.rec-heading h2{font-size:22px}.rec-condition{font-size:12px}.rec-conditions{gap:14px}.rec-sort{margin-right:0}.rec-sort select{font-size:14px;width:100px}.rec-grid{gap:16px}.rec-card{padding:19px;min-height:430px}.rec-card h3{font-size:19px}.rec-card .provider{font-size:13px}.rec-reason{font-size:14px}.rec-meta,.rec-detail{font-size:13px}.learning-badge{font-size:12px}.rec-certificates h2{font-size:23px}.certificate-card{padding:20px}.certificate-card h3{font-size:18px;margin-right:95px}.certificate-card p{font-size:12px;max-width:90%}.certificate-label{font-size:11px;padding:4px 13px;right:20px;top:23px}}
@media(max-width:760px){.rec-panel{display:block;padding:20px;min-height:170px;border-radius:18px}.rec-panel h2{font-size:18px;margin-bottom:12px}.gap-line{gap:7px}.gap-label{flex-basis:100%;margin-right:0;font-size:11px}.analysis-button{margin:15px 0 0;padding:0;font-size:13px}.rec-heading{flex-wrap:wrap;gap:13px;margin:24px 0 18px}.rec-heading h2{font-size:22px;flex-basis:100%}.rec-conditions{gap:9px}.rec-condition{font-size:11px;padding:4px 10px}.rec-sort select{font-size:12px;width:90px}.rec-grid{grid-template-columns:1fr;gap:15px}.rec-card{min-height:365px;padding:22px}.rec-rank{font-size:29px}.rec-card h3{font-size:22px;margin-top:15px}.rec-card .provider{font-size:14px;margin-bottom:17px}.learning-badge{font-size:13px}.rec-reason{font-size:15px;margin:15px 0 20px}.rec-meta{font-size:15px}.rec-detail{font-size:15px}.rec-certificates{margin-top:28px}.rec-certificates h2{font-size:22px}.certificate-grid{grid-template-columns:1fr;gap:13px}.certificate-card h3{font-size:18px}.certificate-card p{font-size:12px}.rec-footnote{font-size:10px}.ai-row{grid-template-columns:1fr;gap:0}.analysis-summary{font-size:13px}}
"""
RECOMMEND_BODY = r"""
<main class="wrap">
<section class="hero"><p class="eyebrow">YOUR NEXT DIRECTION</p><h1>지금 내게 필요한 다음 배움을 찾아요</h1><p class="subtitle">내 이력과 선택한 공고에서 확인한 보완 역량을 교육·자격증과 연결했어요.</p></section>
<section class="rec-panel" aria-label="분석 기준"><div><h2 id="analysisTitle">분석 기준 &nbsp; 채용공고를 선택해 주세요</h2><div class="gap-line"><span class="gap-label">보완할 역량</span><span id="gapPills" style="display:contents"><span class="gap-pill">AI 분석 전</span></span></div></div><button class="analysis-button" id="analysisOpen" type="button">공고 선택·추천받기 <span>↗</span></button></section>
<section aria-labelledby="recommendTitle">
<div class="rec-heading"><h2 id="recommendTitle">맞춤 교육과정</h2><div class="rec-conditions"><button type="button" class="rec-condition" id="budgetChip">교육비 제한 없음</button><button type="button" class="rec-condition" id="modeChip">전체 방식</button></div><div class="sort rec-sort"><select id="recommendSort" aria-label="추천 정렬"><option value="recommended">추천순</option><option value="cost">교육비순</option><option value="latest">최신순</option></select></div></div>
<div class="rec-grid" id="recommendCards" aria-live="polite"></div>
</section>
<section class="rec-certificates"><h2>함께 살펴볼 자격증</h2><div class="certificate-grid" id="certificateCards"></div><p class="rec-footnote" id="recommendNote">선택한 공고와 내 프로필을 비교해 저장된 교육 중에서 Groq AI가 추천해요.</p></section>
<footer><span>취준나침반 · 한 번에 찾고, 한 걸음씩 준비해요.</span><span id="recommendSource">교육추천 · Groq AI · 고용24 교육 정보</span></footer>
</main>
<dialog id="settingsDialog" aria-labelledby="settingsTitle"><div class="modal-top"><p>MY NEXT LEARNING</p><button class="close" id="settingsClose" type="button" aria-label="학습 정보 닫기">×</button></div><h2 class="modal-title" id="settingsTitle">채용공고와 내 프로필을 비교해요</h2>
<form class="ai-form" id="recommendForm">
<label>비교할 채용공고<select name="job_id" id="jobSelect" required><option value="">공고를 불러오는 중…</option></select></label>
<p class="input-hint" id="jobPreview" style="white-space:pre-wrap"></p>
<div class="analysis-source"><strong>마이페이지에 등록한 내 프로필</strong><p id="profilePreview" style="white-space:pre-wrap">로그인한 회원의 프로필을 불러오고 있어요.</p><a href="/mypage" style="text-decoration:underline">프로필 확인·수정 →</a></div>
<label>보완하고 싶은 역량 (선택)<input name="goals" maxlength="300" placeholder="예: SQL, Excel 데이터 실무"></label>
<p class="input-hint">저장 자료에는 교육비·교육 방식이 없습니다. 비용 제한이나 온라인만 조건을 선택하면 후보가 제외됩니다.</p><div class="ai-row"><label>교육비 (미제공)<select name="budget"><option value="">제한 없음</option><option value="0">무료</option><option value="100000">무료·10만원 이하</option><option value="300000">30만원 이하</option><option value="500000">50만원 이하</option></select></label><label>교육 방식<select name="mode"><option value="online_first">온라인 우선</option><option value="online_only">온라인만</option><option value="all" selected>전체 방식</option></select></label></div>
<p class="input-hint">추천받기를 누르면 선택한 공고의 업무·자격요건과 내 자격증명·이수 교육명·희망 직무가 Groq로 전송됩니다. 회원 ID·이름·이메일은 보내지 않습니다. 프로필과 공고 원본은 수정하지 않고, 추천 결과는 DB에 저장하지 않습니다.</p>
<div class="form-error" id="recommendError" role="alert"></div><button type="submit" class="ai-submit" id="runRecommendation">AI 교육 추천받기</button>
</form></dialog>
<dialog id="analysisDialog" aria-labelledby="analysisDialogTitle"><div class="modal-top"><p>MY LEARNING ANALYSIS</p><button class="close" id="analysisClose" type="button" aria-label="분석 결과 닫기">×</button></div><div id="analysisBody"></div><button type="button" class="ai-submit" id="editInputs">공고·조건 바꾸고 다시 추천받기</button></dialog>
<dialog id="recommendDetailDialog" aria-labelledby="recommendDetailTitle"><div class="modal-top"><p>COURSE DETAILS</p><button class="close" id="recommendDetailClose" type="button" aria-label="추천 교육 상세 닫기">×</button></div><div id="recommendDetailBody"></div></dialog>
<div class="toast" id="aiToast" role="status"></div>
<script>
"use strict";
const rEl=id=>document.getElementById(id);
const rEsc=value=>String(value??"").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
const rMode=value=>({online:"온라인",offline:"오프라인",mixed:"혼합",unknown:"방식 확인 필요"}[value]||"방식 확인 필요");
const rCost=value=>value==null?"원문 확인":value===0?"무료":value.toLocaleString("ko-KR")+"원";
const rState={result:null,preferences:null,saved:[],busy:false,context:null,contextPromise:null};
try{const keys=JSON.parse(localStorage.getItem("training-collection-favorites")||"[]");if(Array.isArray(keys))rState.saved=keys.filter(k=>typeof k==="string");}catch{}
const certInfo={sqld:{name:"SQL 개발자 (SQLD)",description:"SQL 기초와 데이터 이해 학습에 참고"},computer1:{name:"컴퓨터활용능력 1급",description:"스프레드시트 활용 역량 확장에 참고"}};
let rToastTimer;
function rToast(message){rEl("aiToast").textContent=message;rEl("aiToast").classList.add("show");clearTimeout(rToastTimer);rToastTimer=setTimeout(()=>rEl("aiToast").classList.remove("show"),2800);}
function openSettings(focusName){
  if(!rEl("settingsDialog").open)rEl("settingsDialog").showModal();
  loadMatchContext();
  if(focusName)rEl("recommendForm").elements[focusName].focus();
}
function placeholder(rank,text){return '<article class="rec-card rec-placeholder"><div class="rec-card-top"><span class="rec-rank">'+String(rank).padStart(2,"0")+'</span><span style="color:#a3ad99">♡</span></div><h3>'+rEsc(text)+'</h3><p class="provider">저장된 고용24 교육에서 선택해요</p><span class="learning-badge">AI 맞춤 학습</span><p class="rec-reason">채용공고를 선택하면 마이페이지의 자격증·이수 교육과 비교해 필요한 다음 배움을 추천해요.</p><button class="rec-detail" type="button" data-open-settings>공고 선택하고 추천받기 →</button></article>';}
function renderRecommendations(){
  const data=rState.result;
  if(!data){
    rEl("recommendCards").innerHTML=[placeholder(1,"나에게 필요한 교육"),placeholder(2,"역량을 넓히는 다음 배움"),placeholder(3,"직무 목표와 연결한 학습")].join("");
    rEl("certificateCards").innerHTML=Object.values(certInfo).map(c=>'<article class="certificate-card"><span class="certificate-label">학습 참고</span><h3>'+rEsc(c.name)+'</h3><p>분석 후 관련 학습 정보를 안내해요.</p></article>').join("");
    return;
  }
  rEl("analysisTitle").textContent="분석 기준  "+data.job_title;
  rEl("gapPills").innerHTML=data.analysis.gaps.length?data.analysis.gaps.map(g=>'<span class="gap-pill" title="'+rEsc(g.status)+'">'+rEsc(g.skill)+'</span>').join(""):'<span class="gap-pill">역량 정보 확인 필요</span>';
  rEl("analysisOpen").innerHTML='분석 결과 다시 보기 <span>↗</span>';
  const prefs=data.preferences;
  rEl("budgetChip").textContent=prefs.budget==null?"교육비 제한 없음":prefs.budget===0?"무료":"무료·"+(prefs.budget/10000)+"만원 이하";
  rEl("modeChip").textContent={online_first:"온라인 우선",online_only:"온라인만",all:"전체 방식"}[prefs.mode];
  let items=[...data.items];
  const sort=rEl("recommendSort").value;
  if(sort==="cost")items.sort((a,b)=>(a.cost??Infinity)-(b.cost??Infinity));
  if(sort==="latest")items.sort((a,b)=>b.start.localeCompare(a.start));
  let cards=items.map((c,i)=>{
    const saved=rState.saved.includes(c.key);
    return '<article class="rec-card"><div class="rec-card-top"><span class="rec-rank">'+String(i+1).padStart(2,"0")+'</span><button type="button" class="heart" data-ai-save="'+rEsc(c.key)+'" aria-label="'+rEsc(c.title)+' 관심 '+(saved?'해제':'저장')+'" aria-pressed="'+saved+'">'+(saved?'♥':'♡')+'</button></div><h3 title="'+rEsc(c.title)+'">'+rEsc(c.title)+'</h3><p class="provider">'+rEsc(c.provider)+'</p><span class="learning-badge">'+rEsc(c.skill_label)+'</span><div class="rec-explanation"><strong class="reason-label">AI 추천 이유</strong><p class="rec-reason" title="'+rEsc(c.ai_reason)+'">'+rEsc(c.ai_reason)+'</p></div><p class="rec-meta">'+rEsc(rCost(c.cost))+' · '+rEsc(rMode(c.mode))+' · '+(c.weeks?c.weeks+'주':'기간 확인')+'</p><button type="button" class="rec-detail" data-ai-detail="'+rEsc(c.key)+'">교육 상세 / 원문 보기 →</button></article>';
  });
  if(!cards.length)cards=[placeholder(1,"조건과 연결되는 교육을 찾지 못했어요")];
  rEl("recommendCards").innerHTML=cards.join("");
  rEl("certificateCards").innerHTML=data.certificates.length?data.certificates.map(c=>'<button type="button" class="certificate-card" data-certificate="'+rEsc(c.id)+'"><span class="certificate-label">선택 준비</span><h3>'+rEsc(c.name)+'</h3><p>'+rEsc(c.ai_reason)+'</p></button>').join(""):'<article class="certificate-card"><h3>관련 자격증은 별도 확인이 필요해요</h3><p>현재 참고 목록에서 연결할 자격증을 선택하지 않았어요.</p></article>';
  rEl("recommendNote").textContent="Groq AI 추천 · "+data.meta.fetched_count+"개 저장 교육 · "+data.meta.candidate_count+"개 후보 비교 · 교육비·교육 방식·분야는 미제공이며 원문 확인 필요"+(data.meta.failed_categories?" · 일부 분야 조회 실패":"");
  rEl("recommendSource").textContent="Supabase 저장 자료 · "+data.meta.fetchedAt+" · "+data.meta.model;
}
function showAnalysis(){
  if(!rState.result){openSettings();return;}
  const d=rState.result;
  rEl("analysisBody").innerHTML='<h2 class="modal-title" id="analysisDialogTitle">'+rEsc(d.job_title)+'</h2><p class="analysis-summary">'+rEsc(d.analysis.summary)+'</p>'+d.analysis.gaps.map(g=>'<div class="gap-explanation"><strong>'+rEsc(g.skill)+' · '+rEsc(g.status)+'</strong><p>'+rEsc(g.basis)+'</p></div>').join("")+'<p class="detail-note">프로필에 없는 역량을 부족하다고 단정하지 않으며, 공고·역량 비교는 학습 참고용입니다.</p>';
  rEl("analysisDialog").showModal();
}
function showRecommendedDetail(c){
  const fields=[["교육기관",c.provider],["분야",c.categoryName],["교육 방식",rMode(c.mode)],["기간",(c.start||"미정")+" ~ "+(c.end||"미정")],["API 수강비",rCost(c.cost)],["개인 본인부담금","고용24 원문 확인"],["훈련 회차",c.round?c.round+"회차":"미제공"],["추천 이유",c.ai_reason],["과정 ID",c.courseId]];
  rEl("recommendDetailBody").innerHTML='<h2 class="modal-title" id="recommendDetailTitle">'+rEsc(c.title)+'</h2><dl class="detail-grid">'+fields.map(([k,v])=>'<dt>'+rEsc(k)+'</dt><dd>'+rEsc(v)+'</dd>').join("")+'</dl><p class="detail-note">교육의 지원 자격·본인부담금과 상세 내용은 고용24 원문에서 확인해 주세요. AI 추천 이유는 입력 정보와 과정명에 근거한 학습 참고 의견입니다.</p>'+(c.url?'<a class="primary-link" href="'+rEsc(c.url)+'" target="_blank" rel="noopener noreferrer">고용24 원문 보기 ↗</a>':'');
  rEl("recommendDetailDialog").showModal();
}
rEl("recommendForm").addEventListener("submit",async event=>{
  event.preventDefault();if(rState.busy)return;
  const form=event.currentTarget;
  const data={job_id:form.elements.job_id.value,goals:form.elements.goals.value.trim(),budget:form.elements.budget.value===""?null:Number(form.elements.budget.value),mode:form.elements.mode.value};
  rState.busy=true;rEl("runRecommendation").disabled=true;rEl("runRecommendation").textContent="교육 조회 후 AI가 비교하고 있어요…";rEl("recommendError").textContent="";
  try{
    const response=await fetch("/training_match/api/recommendations",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(data),cache:"no-store"});
    const result=await response.json();
    if(response.status===401){location.assign("/signin");return;}
    if(!response.ok)throw new Error(result.error||result.detail||"저장된 공고와 프로필을 확인해 주세요.");
    rState.result=result;rState.preferences=data;rEl("recommendSort").value="recommended";
    renderRecommendations();rEl("settingsDialog").close();rToast("AI가 실제 교육 "+result.items.length+"개를 추천했어요.");
  }catch(error){rEl("recommendError").textContent=error.message||"추천을 완료하지 못했어요. 잠시 후 다시 시도해 주세요.";}
  finally{rState.busy=false;rEl("runRecommendation").disabled=false;rEl("runRecommendation").textContent="AI 교육 추천받기";}
});

function updateJobPreview(){
  const id=rEl("jobSelect").value,job=rState.context?.jobs.find(job=>job.id===id);
  rEl("jobPreview").textContent=job?[job.company_name+" · "+job.title,"상태: "+job.status+" · 마감일: "+(job.deadline_date||"원문 확인"),"주요 업무: "+(job.main_tasks||"미기재"),"자격요건: "+(job.qualifications||"미기재"),"우대사항: "+(job.preferred_qualifications||"미기재")].join("\n"):"비교할 채용공고를 선택해 주세요.";
}
async function loadMatchContext(){
  if(rState.context)return;
  if(rState.contextPromise)return rState.contextPromise;
  rState.contextPromise=(async()=>{
    rEl("runRecommendation").disabled=true;rEl("recommendError").textContent="";
    try{
      const response=await fetch("/training_match/api/context",{cache:"no-store"});
      const data=await response.json();
      if(response.status===401){location.assign("/signin");return;}
      if(!response.ok)throw new Error(data.error||data.detail||"공고와 프로필을 불러오지 못했습니다.");
      rState.context=data;
      const select=rEl("jobSelect");select.replaceChildren(new Option("비교할 채용공고를 선택해 주세요", ""));
      for(const job of data.jobs)select.add(new Option(job.company_name+" · "+job.title,job.id));
      const selected=new URLSearchParams(location.search).get("job_id");
      if(selected&&data.jobs.some(job=>job.id===selected))select.value=selected;
      const p=data.profile;
      rEl("profilePreview").textContent=["희망 직무: "+(p.target_role||"미등록"),"자격증: "+(p.certificates.join(", ")||"미등록"),"이수 교육: "+(p.courses.join(", ")||"미등록")].join("\n");
      if(!p.available)rEl("recommendError").textContent="마이페이지에 희망 직무·자격증·이수 교육 중 하나 이상 등록해 주세요.";
      else if(!data.jobs.length)rEl("recommendError").textContent="저장된 채용공고가 없습니다.";
      rEl("runRecommendation").disabled=!p.available||!data.jobs.length;
      updateJobPreview();
    }catch(error){rEl("recommendError").textContent=error.message;rEl("jobSelect").replaceChildren(new Option("닫은 후 다시 시도해 주세요", ""));}
    finally{rState.contextPromise=null;}
  })();
  return rState.contextPromise;
}
rEl("jobSelect").addEventListener("change",updateJobPreview);

rEl("analysisOpen").addEventListener("click",showAnalysis);
rEl("budgetChip").addEventListener("click",()=>openSettings("budget"));
rEl("modeChip").addEventListener("click",()=>openSettings("mode"));
rEl("settingsClose").addEventListener("click",()=>rEl("settingsDialog").close());
rEl("analysisClose").addEventListener("click",()=>rEl("analysisDialog").close());
rEl("editInputs").addEventListener("click",()=>{rEl("analysisDialog").close();openSettings();});
rEl("recommendDetailClose").addEventListener("click",()=>rEl("recommendDetailDialog").close());
rEl("recommendSort").addEventListener("change",renderRecommendations);
rEl("recommendCards").addEventListener("click",event=>{
  const save=event.target.closest("[data-ai-save]"),detail=event.target.closest("[data-ai-detail]"),setup=event.target.closest("[data-open-settings]");
  if(setup)openSettings();
  if(save){
    const key=save.dataset.aiSave;
    rState.saved=rState.saved.includes(key)?rState.saved.filter(k=>k!==key):[...rState.saved,key];
    try{localStorage.setItem("training-collection-favorites",JSON.stringify(rState.saved));rToast("관심목록을 변경했어요.");}catch{rToast("이번 화면에서만 관심 정보가 유지돼요.");}
    renderRecommendations();
  }
  if(detail){const c=rState.result?.items.find(c=>c.key===detail.dataset.aiDetail);if(c)showRecommendedDetail(c);}
});
rEl("certificateCards").addEventListener("click",event=>{
  const button=event.target.closest("[data-certificate]");
  if(!button||!rState.result)return;
  const cert=rState.result.certificates.find(c=>c.id===button.dataset.certificate);
  if(!cert)return;
  rEl("recommendDetailBody").innerHTML='<h2 class="modal-title" id="recommendDetailTitle">'+rEsc(cert.name)+'</h2><p class="analysis-summary">'+rEsc(cert.ai_reason)+'</p><p class="detail-note">학습 참고용 자격증입니다. 채용 필수 여부는 공고에서, 시험 일정·응시 조건은 공식 사이트에서 확인해 주세요.</p><a class="primary-link" href="'+rEsc(cert.url)+'" target="_blank" rel="noopener noreferrer">자격시험 공식 사이트 ↗</a>';
  rEl("recommendDetailDialog").showModal();
});
renderRecommendations();
if(new URLSearchParams(location.search).has("job_id"))openSettings();
</script>
</body></html>
"""

RECOMMEND_PAGE = (
    '<!doctype html><html lang="ko"><head><meta charset="utf-8">'
    '<meta name="viewport" content="width=device-width, initial-scale=1">'
    '<title>AI 교육추천 · 취준나침반</title><style>'
    + _RECOMMEND_STYLE + RECOMMEND_STYLE + '</style></head><body>'
    + _RECOMMEND_HEADER + RECOMMEND_BODY
)


