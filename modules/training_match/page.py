"""AI 교육추천 HTML/CSS/JavaScript 화면."""

_RECOMMEND_STYLE = r"""
.training-match-content{--ink:var(--cc-text);--muted:var(--cc-muted);--line:var(--cc-border);--paper:var(--cc-background);--yellow:var(--cc-yellow);--green:#7d9970;--pale:#edf3e7;box-sizing:border-box}
.training-match-content *{box-sizing:border-box}
.training-match-content button,.training-match-content input,.training-match-content select{font:inherit;color:inherit}
.training-match-content button,.training-match-content select{cursor:pointer}
.training-match-content button{touch-action:manipulation}
.training-match-content a{color:inherit;text-decoration:none}
.training-match-content button:disabled{cursor:default;opacity:.35}
.training-match-content button:focus-visible,.training-match-content a:focus-visible,.training-match-content input:focus-visible,.training-match-content select:focus-visible{outline:3px solid #c99c1c;outline-offset:4px}
.training-match-content .layout{display:grid;grid-template-columns:352px minmax(0,1fr);gap:30px;align-items:start}
.training-match-content .sidebar{background:#fff;border:1px solid var(--line);border-radius:20px;padding:26px 28px 36px;min-height:900px}
.training-match-content .sidebar-head{display:flex;align-items:center;justify-content:space-between;margin-bottom:30px}
.training-match-content .sidebar h2{font-size:27px;letter-spacing:1px;margin:0}
.training-match-content .reset{border:0;background:none;color:#aaaE9f;font-size:16px;padding:0}
.training-match-content .field{min-width:0;display:block;margin:0 0 34px}
.training-match-content .field>span{display:block;font-size:19px;letter-spacing:.3px;margin-bottom:10px}
.training-match-content .select-wrap{position:relative}
.training-match-content .select-wrap:after{content:"⌄";position:absolute;right:21px;top:12px;color:#64705c;pointer-events:none}
.training-match-content select{width:100%;height:58px;padding:10px 42px 10px 17px;border:1px solid #dfe3d5;border-radius:12px;background:#fff;appearance:none;font-size:20px}
.training-match-content .apply{background:var(--yellow);border:0;border-radius:13px;width:100%;height:54px;font-size:21px;letter-spacing:.7px;margin-top:35px}
.training-match-content .sidebar-note{font-size:13px;line-height:1.8;color:#a4a99a;margin:37px 0 0}
.training-match-content .search{height:74px;border:1px solid var(--line);background:#fff;border-radius:20px;display:flex;align-items:center;padding:9px 20px 9px 27px;gap:15px}
.training-match-content .search input{border:0;background:none;outline:none;min-width:0;flex:1;font-size:20px;letter-spacing:.5px}
.training-match-content .search input::placeholder{color:#aaae9f}
.training-match-content .search button{background:var(--yellow);border:0;border-radius:14px;width:122px;height:53px;font-size:21px;}
.training-match-content .results-head{display:flex;align-items:center;justify-content:space-between;margin:29px 0 13px}
.training-match-content .results-head h2{font-size:25px;letter-spacing:.7px;margin:0;}
.training-match-content .sort{position:relative;margin-right:78px}
.training-match-content .sort select{width:120px;height:40px;font-size:18px;border:0;background:transparent;color:#9ba08f;padding:0 25px 0 0;text-align:right}
.training-match-content .sort:after{content:"⌄";position:absolute;right:0;top:5px;font-size:17px;color:#9ba08f;pointer-events:none}
.training-match-content .chips{display:flex;gap:47px;flex-wrap:wrap;align-items:center;min-height:35px;margin:0 0 27px}
.training-match-content .chip{background:#fff5d7;color:#b0aa88;border-radius:30px;font-size:16px;padding:4px 16px;line-height:1.6}
.training-match-content .catalogue-note{font-size:12px;color:#9da590;margin:0 0 15px}
.training-match-content .catalogue-note:empty{display:none}
.training-match-content .cards{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:23px 28px;min-height:548px;align-content:start}
.training-match-content .card{background:#fff;border:1px solid #e0e3d7;border-radius:20px;padding:20px 23px 22px;min-height:263px;position:relative;display:flex;flex-direction:column}
.training-match-content .card-top{display:flex;align-items:center;justify-content:space-between;gap:10px}
.training-match-content .badge{background:var(--pale);color:#8aa27b;border-radius:30px;padding:4px 15px;font-size:16px;line-height:1.6;max-width:85%;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.training-match-content .heart{border:0;background:none;color:#929d87;font-size:29px;line-height:1.2;padding:0 6px}
.training-match-content .heart[aria-pressed="true"]{color:#a75e45}
.training-match-content .card h3{font-size:25px;letter-spacing:.1px;line-height:1.5;margin:18px 0 7px;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
.training-match-content .provider{color:#9aa08f;font-size:17px;margin:0 0 9px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.training-match-content .card-meta{font-size:18px;margin:0 0 14px;letter-spacing:.2px}
.training-match-content .tags{font-size:16px;color:#8ba17d;display:flex;flex-wrap:wrap;gap:10px;padding-right:120px;margin-top:auto}
.training-match-content .tags span+span:before{content:"/";margin-right:10px;color:#a6b29b}
.training-match-content .details{position:absolute;right:65px;bottom:25px;color:#a8ae9f;border:0;background:none;font-size:17px;padding:0}
.training-match-content .details:hover{color:#6a8556}
.training-match-content .pagination{display:flex;justify-content:center;align-items:center;gap:9px;min-height:49px;margin:70px 0 14px}
.training-match-content .pagination button{border:1px solid var(--line);border-radius:13px;background:#fff;font-size:19px;min-width:50px;height:48px;padding:4px 16px}
.training-match-content .pagination .selected{background:var(--yellow);border-color:var(--yellow);}
.training-match-content .pagination .dots{padding:0 3px;color:var(--muted);font-size:15px}
.training-match-content footer{display:flex;justify-content:space-between;gap:20px;border-top:1px solid #dfe3d6;padding:20px 0 27px;margin-top:40px;font-size:14px;color:#a2a896;letter-spacing:.4px}
.training-match-content footer a{color:#8c9780}
.training-match-content .empty{grid-column:1/-1;min-height:548px;border:1px dashed #d9dfcc;background:#f4f6ed;border-radius:18px;padding:35px;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center}
.training-match-content .empty h3{font-size:23px;margin:0 0 9px}
.training-match-content .empty p{color:#8f9b83;font-size:16px;max-width:500px;margin:0 0 18px}
.training-match-content .empty button{border:1px solid #ccd7bd;background:#fff;border-radius:10px;padding:9px 20px;font-size:16px}
.training-match-content .loading{opacity:.55;pointer-events:none}
.training-match-content .error-note{color:#ae7551}
.training-match-content dialog{border:1px solid #e0e5d7;background:var(--paper);border-radius:21px;box-shadow:0 20px 80px #22351830;width:min(760px,calc(100% - 35px));max-height:88vh;padding:30px;color:var(--ink)}
.training-match-content dialog::backdrop{background:#1a2c2366;backdrop-filter:blur(3px)}
.training-match-content .modal-top{display:flex;align-items:center;justify-content:space-between;gap:20px}
.training-match-content .modal-top p{font-size:12px;letter-spacing:2px;color:#8e9a80;margin:0}
.training-match-content .close{border:0;background:none;font-size:31px;line-height:1;color:#87977b}
.training-match-content .modal-title{font-size:26px;line-height:1.5;margin:18px 0 15px}
.training-match-content .detail-grid{display:grid;grid-template-columns:120px 1fr;gap:12px;font-size:15px;border-top:1px solid var(--line);padding-top:20px}
.training-match-content .detail-grid dt{color:#8b977d}
.training-match-content .detail-grid dd{margin:0;overflow-wrap:anywhere}
.training-match-content .detail-note{padding:14px;border-radius:10px;background:#f5efd7;color:#8a8060;font-size:13px}
.training-match-content .primary-link{display:block;background:var(--yellow);padding:12px;border-radius:12px;text-align:center;font-size:17px;margin-top:20px}
.training-match-content .toast{position:fixed;bottom:30px;left:50%;transform:translate(-50%,15px);background:#35482f;color:white;padding:12px 23px;border-radius:11px;font-size:14px;opacity:0;pointer-events:none;transition:.2s;z-index:5;max-width:90vw}
.training-match-content .toast.show{opacity:1;transform:translate(-50%,0)}
@media(min-width:2100px){.training-match-content .layout{grid-template-columns:452px minmax(0,1fr);gap:39px}
.training-match-content .sidebar{padding:34px 36px 46px;min-height:962px}
.training-match-content .sidebar h2{font-size:35px}
.training-match-content .sidebar-head{margin-bottom:39px}
.training-match-content .reset{font-size:20px}
.training-match-content .field{margin-bottom:44px}
.training-match-content .field>span{font-size:24px;margin-bottom:13px}
.training-match-content select{height:74px;font-size:26px;padding-left:22px}
.training-match-content .select-wrap:after{top:18px;right:26px}
.training-match-content .apply{height:69px;font-size:27px;margin-top:45px}
.training-match-content .sidebar-note{font-size:16px;margin-top:47px}
.training-match-content .search{height:95px;padding:12px 26px 12px 35px}
.training-match-content .search input{font-size:26px}
.training-match-content .search button{width:156px;height:68px;font-size:27px}
.training-match-content .results-head{margin:37px 0 17px}
.training-match-content .results-head h2{font-size:32px}
.training-match-content .sort{margin-right:100px}
.training-match-content .sort select{font-size:23px;width:154px}
.training-match-content .chips{gap:60px;min-height:45px;margin-bottom:35px}
.training-match-content .chip{font-size:20px;padding:5px 20px}
.training-match-content .cards{gap:30px 36px;min-height:702px}
.training-match-content .card{padding:26px 30px 28px;min-height:337px}
.training-match-content .badge{font-size:20px;padding:5px 19px}
.training-match-content .heart{font-size:37px}
.training-match-content .card h3{font-size:32px;margin-top:23px}
.training-match-content .provider{font-size:22px}
.training-match-content .card-meta{font-size:23px;margin-bottom:18px}
.training-match-content .tags{font-size:20px;padding-right:154px}
.training-match-content .details{font-size:22px;right:83px;bottom:32px}
.training-match-content .pagination{margin-top:90px;gap:12px}
.training-match-content .pagination button{height:62px;min-width:64px;font-size:24px}
.training-match-content footer{font-size:18px;margin-top:51px;padding:26px 0 35px}}
@media(max-width:1550px){.training-match-content .layout{grid-template-columns:290px minmax(0,1fr);gap:25px}
.training-match-content .sidebar{padding:25px 23px;min-height:690px}
.training-match-content .sidebar h2{font-size:23px}
.training-match-content .field>span{font-size:17px}
.training-match-content select{font-size:17px}
.training-match-content .card h3{font-size:20px}
.training-match-content .provider{font-size:14px}
.training-match-content .card-meta{font-size:15px}
.training-match-content .badge,.training-match-content .tags{font-size:13px}
.training-match-content .details{font-size:14px;right:25px}
.training-match-content .card{min-height:245px}
.training-match-content .cards{gap:20px;min-height:510px}
.training-match-content .sort{margin-right:25px}
.training-match-content .search input{font-size:17px}
.training-match-content .chips{gap:22px}}
@media(max-width:1120px){.training-match-content .layout{grid-template-columns:235px minmax(0,1fr);gap:20px}
.training-match-content .sidebar{padding:20px 18px;min-height:650px}
.training-match-content .sidebar h2{font-size:21px}
.training-match-content .reset{font-size:13px}
.training-match-content .field>span{font-size:15px}
.training-match-content select{font-size:14px;height:50px}
.training-match-content .apply{font-size:17px}
.training-match-content .sidebar-note{font-size:11px}
.training-match-content .cards{gap:15px}
.training-match-content .card{padding:16px;min-height:260px}
.training-match-content .card h3{font-size:18px}
.training-match-content .card-meta{font-size:13px}
.training-match-content .tags{padding-right:0;margin-bottom:28px;font-size:11px}
.training-match-content .details{bottom:15px;font-size:12px;right:20px}
.training-match-content .results-head h2{font-size:20px}
.training-match-content .chip{font-size:13px}
.training-match-content .search{padding-left:17px;height:65px}
.training-match-content .search button{height:45px;width:85px;font-size:17px}
.training-match-content .search input{font-size:14px}
.training-match-content .sort{margin-right:0}
.training-match-content .sort select{font-size:14px}
.training-match-content .pagination{margin-top:35px}
.training-match-content footer{font-size:11px}}
@media(max-width:760px){.training-match-content .layout{display:flex;flex-direction:column;gap:20px}
.training-match-content .sidebar{width:100%;min-height:0;padding:18px}
.training-match-content .sidebar-head{margin-bottom:16px}
.training-match-content .sidebar h2{font-size:20px}
.training-match-content .filter-form{display:grid;grid-template-columns:1fr 1fr;gap:12px}
.training-match-content .field{margin:0}
.training-match-content .field>span{font-size:12px;margin-bottom:5px}
.training-match-content select{font-size:13px;height:44px;padding-left:12px}
.training-match-content .select-wrap:after{top:9px;right:14px}
.training-match-content .apply{margin:0;height:44px;font-size:15px;align-self:end}
.training-match-content .sidebar-note{margin:12px 0 0;font-size:10px}
.training-match-content .result-area{width:100%}
.training-match-content .search{height:58px;border-radius:14px;padding:6px 9px 6px 14px}
.training-match-content .search input{font-size:13px}
.training-match-content .search button{height:43px;width:67px;font-size:15px}
.training-match-content .results-head{margin-top:22px;margin-bottom:9px}
.training-match-content .results-head h2{font-size:19px}
.training-match-content .chips{gap:9px;margin-bottom:17px;min-height:26px}
.training-match-content .chip{font-size:11px;padding:3px 10px}
.training-match-content .cards{grid-template-columns:1fr;min-height:0;gap:14px}
.training-match-content .card{min-height:240px;padding:18px 20px}
.training-match-content .card h3{font-size:20px;margin-top:14px}
.training-match-content .provider{font-size:13px}
.training-match-content .card-meta{font-size:14px}
.training-match-content .badge{font-size:12px}
.training-match-content .tags{font-size:12px;margin-bottom:22px}
.training-match-content .details{font-size:13px;bottom:17px}
.training-match-content .pagination{margin-top:25px}
.training-match-content .pagination button{min-width:38px;height:40px;font-size:15px;padding:4px 10px}
.training-match-content .empty{min-height:330px;padding:25px}
.training-match-content .empty h3{font-size:19px}
.training-match-content .empty p{font-size:13px}
.training-match-content footer{flex-direction:column;gap:5px;font-size:10px;margin-top:30px}
.training-match-content .detail-grid{grid-template-columns:85px 1fr;font-size:12px;gap:10px}
.training-match-content .modal-title{font-size:21px}}
@media(prefers-reduced-motion:reduce){.training-match-content *{transition:none!important}}
"""
RECOMMEND_STYLE = r"""
.cc-training-page #analysisOpen{font-size:calc(11px + 4pt);border:1px solid #ebc03f;background:#fff;color:var(--cc-text);padding:9px 19px}

.training-match-content .rec-panel{position:relative;min-height:158px;border-radius:24px;background:#f5efd0;padding:26px 34px;display:flex;align-items:center;justify-content:space-between;gap:25px}
.training-match-content .rec-intro{margin:0 0 12px;font-size:16px;line-height:1.8;color:var(--ink);word-break:keep-all}
.training-match-content .rec-panel h2{font-size:25px;letter-spacing:.5px;margin:0 0 12px;}
.training-match-content .gap-line{display:flex;align-items:center;gap:15px;flex-wrap:wrap;font-size:17px;color:#8d947f}
.training-match-content .gap-label{margin-right:45px}
.training-match-content .gap-pill{background:white;border-radius:30px;padding:4px 26px;min-width:138px;text-align:center;font-size:16px;color:#909889}
.training-match-content .analysis-button{background:none;border:0;color:#607b4d;font-size:21px;white-space:nowrap;letter-spacing:.5px;margin-right:275px}
.training-match-content .analysis-button span{margin-left:12px}
.training-match-content .rec-heading{display:flex;align-items:center;gap:60px;margin:32px 0 26px;min-height:42px}
.training-match-content .rec-heading h2{font-size:28px;letter-spacing:.8px;margin:0;white-space:nowrap}
.training-match-content .rec-conditions{display:flex;gap:74px;flex:1;align-items:center}
.training-match-content .rec-condition{border:0;background:#fff5d7;color:#a9a683;font-size:16px;border-radius:30px;padding:4px 16px}
.training-match-content .rec-sort{margin-left:auto;margin-right:140px}
.training-match-content .rec-sort select{height:40px;border:0;background:none;width:130px;padding:0 20px 0 0;font-size:18px;color:#909985;text-align:right}
.training-match-content .rec-sort:after{right:0}
.training-match-content .rec-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:24px}
.training-match-content .rec-card{background:#fff;border:1px solid #e0e3d7;border-radius:20px;min-height:410px;padding:24px 28px;display:flex;flex-direction:column}
.training-match-content .rec-card-top{display:flex;align-items:center;justify-content:space-between}
.training-match-content .rec-rank{font-size:32px;color:#5b7849;line-height:1.6}
.training-match-content .rec-card h3{font-size:24px;line-height:1.5;letter-spacing:.1px;margin:17px 0 8px;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
.training-match-content .rec-card .provider{font-size:17px;margin:0 0 20px}
.training-match-content .learning-badge{align-self:flex-start;background:#edf3e7;color:#879f78;border-radius:30px;padding:4px 14px;font-size:16px;line-height:1.6}
.training-match-content .rec-reason{font-size:18px;line-height:1.8;color:#939b8a;margin:15px 0 23px;flex:1;display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden}
.training-match-content .rec-meta{font-size:18px;margin:0 0 19px}
.training-match-content .rec-detail{align-self:flex-start;background:none;border:0;padding:0;color:#698453;font-size:18px;letter-spacing:.1px}
.training-match-content .rec-placeholder{background:#fdfdf9}
.training-match-content .rec-placeholder h3{color:#86917c}
.training-match-content .rec-placeholder .rec-reason{color:#a3aa99}
.training-match-content .rec-placeholder .rec-detail{font-size:16px}
.training-match-content .rec-certificates{margin-top:39px}
.training-match-content .rec-certificates h2{font-size:28px;margin:0 0 16px;letter-spacing:.4px}
.training-match-content .certificate-grid{display:grid;grid-template-columns:1fr 1fr;gap:24px}
.training-match-content .certificate-card{border:1px solid #e0e3d7;border-radius:20px;background:#fff;padding:25px 28px;min-height:130px;text-align:left;position:relative;width:100%}
.training-match-content .certificate-card h3{font-size:25px;margin:0 160px 8px 0;line-height:1.5}
.training-match-content .certificate-card p{font-size:17px;color:#959e8b;margin:0;max-width:80%}
.training-match-content .certificate-label{position:absolute;right:28px;top:28px;background:#fff5d7;color:#b0aa88;border-radius:30px;padding:4px 34px;font-size:16px}
.training-match-content .rec-footnote{color:#9ba48f;font-size:12px;margin:12px 0 0;min-height:18px}
.training-match-content .ai-form label{display:block;font-size:14px;margin-top:16px}
.training-match-content .ai-form input,.training-match-content .ai-form textarea,.training-match-content .ai-form select{display:block;width:100%;border:1px solid #dce2d3;border-radius:10px;background:white;padding:10px 12px;font-size:14px;margin-top:6px;min-height:44px;height:auto}
.training-match-content .ai-form textarea{resize:vertical;min-height:110px;line-height:1.6}
.training-match-content .ai-row{display:grid;grid-template-columns:1fr 1fr;gap:15px}
.training-match-content .ai-form .input-hint{font-size:12px;line-height:1.7;color:#8b967f;margin:10px 0}
.training-match-content .ai-submit{background:var(--yellow);border:0;border-radius:12px;width:100%;padding:12px;margin-top:15px;font-size:17px}
.training-match-content .example-fill{border:1px solid #dce2d3;border-radius:9px;background:white;padding:7px 12px;font-size:12px;margin-top:14px}
.training-match-content .form-error{font-size:13px;color:#a1643b;line-height:1.7;margin-top:12px}
.training-match-content .form-error:empty{display:none}
.training-match-content .analysis-summary{font-size:15px;line-height:1.8}
.training-match-content .gap-explanation{padding:12px 0;border-top:1px solid var(--line);font-size:14px}
.training-match-content .gap-explanation strong{color:#607b4d}
.training-match-content .gap-explanation p{color:#87927c;margin:5px 0}
.training-match-content .analysis-source{white-space:pre-wrap;border-radius:10px;background:#f0f3e9;padding:13px;font-size:12px;color:#7e8a73;max-height:220px;overflow:auto}
.training-match-content .rec-explanation{flex:1;margin:15px 0 23px}
.training-match-content .reason-label{display:block;font-size:13px;color:#698453;margin-bottom:5px;}
.training-match-content .rec-explanation .rec-reason{margin:0;flex:none;-webkit-line-clamp:2}
@media(min-width:2100px){.training-match-content .rec-panel{min-height:203px;padding:33px 44px}
.training-match-content .rec-panel h2{font-size:32px}
.training-match-content .gap-line{font-size:22px;gap:19px}
.training-match-content .gap-pill{font-size:20px;padding:5px 33px;min-width:177px}
.training-match-content .gap-label{margin-right:58px}
.training-match-content .analysis-button{font-size:27px;margin-right:352px}
.training-match-content .rec-heading{margin:41px 0 33px;gap:77px}
.training-match-content .rec-heading h2{font-size:36px}
.training-match-content .rec-conditions{gap:95px}
.training-match-content .rec-condition{font-size:20px;padding:5px 20px}
.training-match-content .rec-sort{margin-right:180px}
.training-match-content .rec-sort select{font-size:23px;width:166px}
.training-match-content .rec-grid{gap:31px}
.training-match-content .rec-card{min-height:525px;padding:31px 36px}
.training-match-content .rec-rank{font-size:41px}
.training-match-content .rec-card h3{font-size:31px;margin-top:22px}
.training-match-content .rec-card .provider{font-size:22px;margin-bottom:26px}
.training-match-content .learning-badge{font-size:20px}
.training-match-content .rec-reason{font-size:23px;margin:19px 0 29px}
.training-match-content .rec-meta{font-size:23px;margin-bottom:24px}
.training-match-content .rec-detail{font-size:23px}
.training-match-content .rec-certificates{margin-top:50px}
.training-match-content .rec-certificates h2{font-size:36px;margin-bottom:20px}
.training-match-content .certificate-grid{gap:31px}
.training-match-content .certificate-card{padding:32px 36px;min-height:167px}
.training-match-content .certificate-card h3{font-size:32px}
.training-match-content .certificate-card p{font-size:22px}
.training-match-content .certificate-label{font-size:20px;right:36px;top:36px}}
@media(max-width:1550px){.training-match-content .analysis-button{margin-right:80px;font-size:18px}
.training-match-content .rec-panel h2{font-size:22px}
.training-match-content .gap-label{margin-right:20px}
.training-match-content .rec-heading{gap:35px}
.training-match-content .rec-heading h2{font-size:25px}
.training-match-content .rec-conditions{gap:25px}
.training-match-content .rec-sort{margin-right:40px}
.training-match-content .rec-card{padding:23px;min-height:420px}
.training-match-content .rec-card h3{font-size:21px}
.training-match-content .rec-card .provider{font-size:15px}
.training-match-content .rec-reason{font-size:16px}
.training-match-content .rec-meta,.training-match-content .rec-detail{font-size:16px}
.training-match-content .learning-badge{font-size:14px}
.training-match-content .certificate-card h3{font-size:21px;margin-right:130px}
.training-match-content .certificate-card p{font-size:15px}
.training-match-content .certificate-label{font-size:14px;padding:4px 22px}}
@media(max-width:1120px){.training-match-content .rec-panel{padding:23px}
.training-match-content .rec-panel h2{font-size:20px}
.training-match-content .analysis-button{margin-right:0;font-size:15px}
.training-match-content .gap-line{font-size:13px;gap:8px}
.training-match-content .gap-label{margin-right:10px}
.training-match-content .gap-pill{font-size:12px;min-width:100px;padding:3px 14px}
.training-match-content .rec-heading{gap:20px}
.training-match-content .rec-heading h2{font-size:22px}
.training-match-content .rec-condition{font-size:12px}
.training-match-content .rec-conditions{gap:14px}
.training-match-content .rec-sort{margin-right:0}
.training-match-content .rec-sort select{font-size:14px;width:100px}
.training-match-content .rec-grid{gap:16px}
.training-match-content .rec-card{padding:19px;min-height:430px}
.training-match-content .rec-card h3{font-size:19px}
.training-match-content .rec-card .provider{font-size:13px}
.training-match-content .rec-reason{font-size:14px}
.training-match-content .rec-meta,.training-match-content .rec-detail{font-size:13px}
.training-match-content .learning-badge{font-size:12px}
.training-match-content .rec-certificates h2{font-size:23px}
.training-match-content .certificate-card{padding:20px}
.training-match-content .certificate-card h3{font-size:18px;margin-right:95px}
.training-match-content .certificate-card p{font-size:12px;max-width:90%}
.training-match-content .certificate-label{font-size:11px;padding:4px 13px;right:20px;top:23px}}
@media(max-width:760px){.training-match-content .rec-panel{display:block;padding:20px;min-height:170px;border-radius:18px}
.training-match-content .rec-panel h2{font-size:18px;margin-bottom:12px}
.training-match-content .gap-line{gap:7px}
.training-match-content .gap-label{flex-basis:100%;margin-right:0;font-size:11px}
.training-match-content .analysis-button{margin:15px 0 0;padding:0;font-size:13px}
.training-match-content .rec-heading{flex-wrap:wrap;gap:13px;margin:24px 0 18px}
.training-match-content .rec-heading h2{font-size:22px;flex-basis:100%}
.training-match-content .rec-conditions{gap:9px}
.training-match-content .rec-condition{font-size:11px;padding:4px 10px}
.training-match-content .rec-sort select{font-size:12px;width:90px}
.training-match-content .rec-grid{grid-template-columns:1fr;gap:15px}
.training-match-content .rec-card{min-height:365px;padding:22px}
.training-match-content .rec-rank{font-size:29px}
.training-match-content .rec-card h3{font-size:22px;margin-top:15px}
.training-match-content .rec-card .provider{font-size:14px;margin-bottom:17px}
.training-match-content .learning-badge{font-size:13px}
.training-match-content .rec-reason{font-size:15px;margin:15px 0 20px}
.training-match-content .rec-meta{font-size:15px}
.training-match-content .rec-detail{font-size:15px}
.training-match-content .rec-certificates{margin-top:28px}
.training-match-content .rec-certificates h2{font-size:22px}
.training-match-content .certificate-grid{grid-template-columns:1fr;gap:13px}
.training-match-content .certificate-card h3{font-size:18px}
.training-match-content .certificate-card p{font-size:12px}
.training-match-content .rec-footnote{font-size:10px}
.training-match-content .ai-row{grid-template-columns:1fr;gap:0}
.training-match-content .analysis-summary{font-size:13px}}
.cc-training-page .training-match-content #recommendSort{font-size:calc(12px + 2pt);width:156px;height:46px;padding:8px 24px;text-align:center;text-align-last:center;color:#9ba08f}
.cc-training-page .training-match-content #recommendSort option{text-align:center}
@supports (appearance:base-select){
  .cc-training-page .training-match-content #recommendSort,
  .cc-training-page .training-match-content #recommendSort::picker(select){appearance:base-select}
  .cc-training-page .training-match-content #recommendSort{display:flex;align-items:center;justify-content:center;anchor-name:--recommend-sort}
  .cc-training-page .training-match-content #recommendSort::picker-icon{display:none}
  .cc-training-page .training-match-content #recommendSort::picker(select){font-family:inherit;font-size:calc(12px + 2pt);color:#9ba08f;background:#fff;border:1px solid var(--cc-border);border-radius:12px;padding:4px 0;position:fixed;position-anchor:--recommend-sort;inset:auto;top:anchor(--recommend-sort bottom);left:anchor(--recommend-sort left);margin:4px 0 0;position-area:none;position-try-fallbacks:none;min-width:anchor-size(--recommend-sort width);max-height:240px;overflow-y:auto}
  .cc-training-page .training-match-content #recommendSort option{display:flex;justify-content:center;padding:10px 12px;min-height:40px}
  .cc-training-page .training-match-content #recommendSort option::checkmark{display:none}
  .cc-training-page .training-match-content #recommendSort option:checked{background:#fff5d7;color:var(--cc-text)}
  .cc-training-page .training-match-content #recommendSort option:hover,
  .cc-training-page .training-match-content #recommendSort option:focus{background:var(--cc-yellow);color:var(--cc-text)}
}
.cc-training-page .training-match-content .rec-sort:after{right:8px;top:50%;transform:translateY(-50%)}
"""
RECOMMEND_BODY = r"""
<div class="training-match-content" data-member-content>
<main class="cc-page">
<section class="cc-page-heading"><p class="eyebrow">YOUR NEXT DIRECTION</p><h1>지금 내게 필요한 다음 배움을 찾아요</h1><p class="subtitle">내 이력과 선택한 공고에서 확인한 보완 역량을 교육·자격증과 연결했어요.</p></section>
<section class="rec-panel" aria-label="분석 기준"><div><p class="rec-intro">AI가 내 프로필과 저장한 채용공고를 비교해 보완할 역량과 관련 교육을 추천해요.</p><div class="gap-line"><span class="gap-label">보완할 역량</span><span id="gapPills" style="display:contents"><span class="gap-pill">AI 분석 전</span></span></div></div><button class="analysis-button cc-top-button cc-main-button" id="analysisOpen" type="button" disabled>AI 맞춤 교육 추천 받기</button></section>
<section aria-labelledby="recommendTitle">
<div class="rec-heading"><h2 id="recommendTitle">AI 추천 맞춤 교육과정 목록</h2><div class="sort rec-sort"><select id="recommendSort" aria-label="추천 정렬"><option value="latest">최신순</option><option value="recommended" disabled>AI 추천순</option><option value="cost_low">교육비 낮은순</option><option value="cost_high">교육비 높은순</option></select></div></div>
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
  rEl("gapPills").innerHTML=data.analysis.gaps.length?data.analysis.gaps.map(g=>'<span class="gap-pill" title="'+rEsc(g.status)+'">'+rEsc(g.skill)+'</span>').join(""):'<span class="gap-pill">역량 정보 확인 필요</span>';
  rEl("analysisOpen").textContent="AI 맞춤 교육 추천 받기";
  let items=[...data.items];
  const sort=rEl("recommendSort").value;
  if(sort==="cost_low")items.sort((a,b)=>(a.cost??Infinity)-(b.cost??Infinity));
  if(sort==="cost_high")items.sort((a,b)=>(b.cost??-1)-(a.cost??-1));
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
    rState.result=result;rState.preferences=data;rEl("recommendSort").value="latest";
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
</div>
__CC_SCRIPT__
</body></html>
"""

RECOMMEND_PAGE = (
    '<!doctype html><html lang="ko"><head><meta charset="utf-8">'
    '<meta name="viewport" content="width=device-width, initial-scale=1">'
    '<title>AI 교육추천 · 취준나침반</title><style>'
    + _RECOMMEND_STYLE + RECOMMEND_STYLE + '</style><style>__CC_CSS__</style></head><body class="cc-member-page cc-training-page">'
    + '__CC_HEADER____CC_MENU__' + RECOMMEND_BODY
)


