"""선택 공고의 직무 기반 교육추천 화면."""

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
.training-match-content .rec-intro{margin:0 0 26px;font-size:16px;line-height:1.8;color:var(--ink);word-break:keep-all}
.training-match-content .rec-panel h2{font-size:25px;letter-spacing:.5px;margin:0 0 12px;}
.training-match-content .gap-line{display:flex;align-items:center;gap:15px;flex-wrap:wrap;font-size:17px;color:#8d947f}
.training-match-content .gap-label{margin-right:45px}
.training-match-content .gap-pill{background:white;border-radius:30px;padding:4px 26px;min-width:138px;text-align:center;font-size:16px;color:#909889}
.training-match-content button.gap-pill{border:1px solid transparent;cursor:pointer}
.training-match-content button.gap-pill:hover{border-color:var(--cc-yellow);color:var(--cc-text)}
.training-match-content button.gap-pill[aria-pressed="true"]{background:var(--cc-yellow);color:var(--cc-text);border-color:#c99c1c}
.training-match-content button.gap-pill:disabled{cursor:wait;opacity:.6}
.training-match-content .analysis-button{background:none;border:0;color:#607b4d;font-size:21px;white-space:nowrap;letter-spacing:.5px;margin-right:275px}
.training-match-content .analysis-button span{margin-left:12px}
.training-match-content .rec-heading{display:flex;align-items:center;gap:60px;margin:32px 0 26px;min-height:42px}
.training-match-content .rec-heading h2{font-size:28px;letter-spacing:.8px;margin:0;white-space:nowrap}
.training-match-content .rec-conditions{display:flex;gap:74px;flex:1;align-items:center}
.training-match-content .rec-condition{border:0;background:#fff5d7;color:#a9a683;font-size:16px;border-radius:30px;padding:4px 16px}
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
.cc-training-page .training-match-content .rec-panel{display:grid;grid-template-columns:minmax(0,1fr);gap:20px;align-items:start;min-height:0}
.cc-training-page .training-match-content .rec-panel>div{min-width:0;width:100%}
.cc-training-page .training-match-content .gap-line{display:block;max-width:none}
.cc-training-page .keyword-selection-layout{display:grid;grid-template-columns:minmax(0,3fr) minmax(0,1fr);gap:32px}
.cc-training-page .keyword-selection-main{min-width:0}
.cc-training-page .selected-keyword-panel{display:flex;flex-direction:column;gap:24px;min-width:0;padding-top:10px;text-align:center}
.cc-training-page #selectedKeywordList{display:flex;flex:1;flex-wrap:wrap;align-content:center;justify-content:center;gap:8px;min-height:120px;padding:12px 0 12px 24px;border-left:2px solid #b8b18b;overflow-wrap:anywhere}
.cc-training-page .selected-keyword-chip{align-self:center;max-width:100%;padding:6px 12px;border-radius:20px;background:#fff5d7;border:1px solid #e2c96a;font-size:14px;line-height:1.5}
.cc-training-page .selected-keyword-empty{align-self:center;margin:0;color:var(--cc-muted);font-size:14px;line-height:1.7}
.cc-training-page .training-match-content .rec-panel h2{font-size:22px;line-height:1.5;margin:0 0 6px;letter-spacing:0}
.cc-training-page .training-match-content .rec-intro{margin:0 0 20px;font-size:15px;line-height:1.7;color:var(--cc-muted)}
.cc-training-page .training-match-content .gap-label{margin:0;padding-top:8px;font-size:clamp(13px,.9vw,16px);line-height:1.4}
.cc-training-page .gap-keywords{min-width:0}
.cc-training-page #gapPills{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:10px;min-width:0}
.cc-training-page #gapMore{display:block;margin:8px 0 0 auto;padding:4px 0 4px 12px;border:0;background:transparent;color:var(--cc-muted);font-size:13px;cursor:pointer}
.cc-training-page #gapMore[hidden]{display:none}
.cc-training-page .training-match-content .gap-pill{box-sizing:border-box;min-width:0;max-width:100%;width:100%;padding:8px 12px;font-size:clamp(13px,.9vw,16px);line-height:1.4;white-space:normal;overflow-wrap:anywhere}
.cc-training-page #skillRecommendationStatus{margin:14px 0 0;line-height:1.6;overflow-wrap:anywhere;white-space:pre-line}
.cc-training-page #skillRecommendationStatus:empty{display:none}
.cc-training-page .perfect-match{padding:40px 24px;border-radius:24px;background:#f5efd0;text-align:center}
.cc-training-page .perfect-match h2{margin:0 0 18px;font-size:clamp(22px,2vw,30px);line-height:1.5}
.cc-training-page .perfect-match p{margin:0 0 24px;font-size:16px;line-height:1.9;word-break:keep-all}
.cc-training-page .perfect-match a{display:inline-block;position:relative;top:3px;padding:12px 24px;border:1px solid #ebc03f;border-radius:12px;background:#fff;color:var(--cc-text)}
.cc-training-page .training-match-content .rec-heading{justify-content:space-between;flex-wrap:wrap;gap:16px}
.cc-training-page .training-match-content .rec-heading h2{min-width:0;white-space:normal}
.cc-training-page .training-match-content .rec-heading #analysisOpen{margin-left:auto;background:#eeece4;border-color:#fff}
.cc-training-page .recommend-actions{display:flex;justify-content:center;align-items:center;flex-wrap:wrap;gap:12px;padding-top:18px;border-top:1px solid #ded7b2}
.cc-training-page #selectedKeywordCount{margin:0;font-size:15px;color:var(--cc-text)}
.cc-training-page #courseMore{display:block;margin:24px auto 0;padding:10px 28px;border:1px solid var(--cc-border);border-radius:12px;background:#fff;color:var(--cc-text);font-size:15px;cursor:pointer}
.cc-training-page #courseMore[hidden]{display:none}
.cc-training-page .keyword-disclosure>summary{display:inline-flex;align-items:center;gap:12px;list-style:none;padding:11px 20px;border:1px solid var(--cc-border);border-radius:12px;background:#eeece4;color:var(--cc-text);font-size:15px;cursor:pointer}
.cc-training-page .keyword-disclosure>summary::-webkit-details-marker{display:none}
.cc-training-page .keyword-disclosure>summary::after{content:"⌄"}
.cc-training-page .keyword-disclosure[open]>summary{margin-bottom:16px}
.cc-training-page .keyword-disclosure[open]>summary::after{content:"⌃"}
.cc-training-page .keyword-disclosure>summary:focus-visible{outline:3px solid #c99c1c;outline-offset:4px}
.cc-training-page .training-match-content #analysisOpen,
.cc-training-page .training-match-content #selectedRecommendation{max-width:100%;margin:0;padding:12px 24px;white-space:normal;text-align:center;font-size:calc(11px + 4pt);border:1px solid #ebc03f;background:#fff;color:var(--cc-text)}
.cc-training-page .training-match-content #selectedRecommendation{background:var(--cc-yellow);position:relative;top:3px}
@media(max-width:760px){
  .cc-training-page .keyword-selection-layout{grid-template-columns:minmax(0,1fr);gap:18px}
  .cc-training-page .selected-keyword-panel{padding-top:16px;border-top:1px solid #ded7b2;gap:10px;text-align:left}
  .cc-training-page #selectedKeywordList{border-left:0;min-height:0;padding:0;justify-content:flex-start;align-content:start}
  .cc-training-page .training-match-content .gap-line{grid-template-columns:minmax(0,1fr);gap:8px}
  .cc-training-page .training-match-content .gap-label{padding-top:0}
  .cc-training-page #gapPills{gap:6px}
  .cc-training-page .training-match-content .gap-pill{padding:7px 4px}
  .cc-training-page .training-match-content #analysisOpen,
  .cc-training-page .training-match-content #selectedRecommendation{padding:11px 18px;font-size:15px}
}
"""
RECOMMEND_BODY = r"""
<div class="training-match-content" data-member-content>
<main class="cc-page">
<section class="cc-page-heading training-recommend-heading"><div class="ai-course-actions"><div class="ai-action-group"><button id="aiCourseList" class="ai-course-list-button" type="button" aria-pressed="false">AI 맞춤 교육 목록 보기</button><button id="returnRoleCourses" class="ai-course-return-button" type="button" hidden></button></div><div class="ai-action-group"><button id="aiSelectedSkills" class="ai-course-list-button" type="button" aria-pressed="false">선택 역량으로 AI 추천받기</button><button id="returnSelectedRoleCourses" class="ai-course-return-button" type="button" hidden></button></div></div><p class="eyebrow">YOUR NEXT DIRECTION</p><h1>지금 내게 필요한 다음 배움을 찾아요</h1><p class="subtitle">잘하는 것은 이어가고, 필요한 역량은 하나씩 채워보세요.</p></section>
<section id="skillSelectionSection" aria-label="보완할 역량 선택" hidden>
<div id="skillSelectionBody">
<section class="rec-panel" aria-labelledby="keywordSelectionTitle">
<div class="keyword-selection-layout"><div class="keyword-selection-main"><h2 id="keywordSelectionTitle">보완할 역량을 선택해 주세요</h2>
<p class="rec-intro">관심 있는 키워드를 고르면 관련 교육을 추천해 드려요.</p>
<div class="gap-line"><div class="gap-keywords"><div id="gapPills"></div></div></div>
<p id="skillRecommendationStatus" role="status" aria-live="polite"></p></div>
<aside class="selected-keyword-panel" aria-labelledby="selectedKeywordCount"><p id="selectedKeywordCount" role="status" aria-live="polite">선택한 키워드 0개</p><div id="selectedKeywordList"><p class="selected-keyword-empty">키워드를 선택해 주세요.</p></div></aside></div>
<div class="recommend-actions"><button class="cc-top-button cc-main-button" id="selectedRecommendation" type="button">선택 키워드로 교육 추천</button></div>
</section>
</div>
<button id="skillPanelToggle" type="button" aria-controls="skillSelectionBody" aria-expanded="true">접기</button>
</section>
<section aria-labelledby="recommendTitle">
<div class="rec-heading"><h2 id="recommendTitle">직무 관련 교육과정 목록</h2></div>
<p id="aiRecommendationStatus" role="status" aria-live="polite" hidden></p>
<div class="rec-grid" id="recommendCards" aria-live="polite" aria-busy="false"></div>
<button id="courseMore" type="button" aria-controls="recommendCards" aria-expanded="false" hidden>더보기</button>
</section>
<footer><span>취준나침반 · 한 번에 찾고, 한 걸음씩 준비해요.</span><span id="recommendSource">직무 기반 교육추천 · 고용24 교육 정보</span></footer>
</main>
<dialog id="recommendDetailDialog" aria-labelledby="recommendDetailTitle"><div class="modal-top"><p>COURSE DETAILS</p><button class="close" id="recommendDetailClose" type="button" aria-label="추천 교육 상세 닫기">×</button></div><div id="recommendDetailBody"></div></dialog>
<div class="toast" id="aiToast" role="status"></div>
<style>
.cc-training-page .training-recommend-heading{display:grid;grid-template-columns:minmax(0,1fr) auto;column-gap:32px;padding-right:0}
.cc-training-page .training-recommend-heading>.eyebrow{grid-column:1;grid-row:1}
.cc-training-page .training-recommend-heading>h1{grid-column:1;grid-row:2}
.cc-training-page .training-recommend-heading>.subtitle{grid-column:1;grid-row:3}
.cc-training-page .ai-course-actions{grid-column:2;grid-row:1/4;align-self:center;display:flex;align-items:flex-start;gap:12px}
.cc-training-page .ai-action-group{display:flex;flex-direction:column;gap:8px;min-width:210px}
.cc-training-page .ai-course-list-button,.cc-training-page .ai-course-return-button{width:100%;min-height:50px;padding:12px 20px;border:1px solid var(--cc-border);border-radius:11px;background:#eeece4;color:var(--cc-text);font-size:14px;line-height:1.5;text-align:center;white-space:nowrap}
.cc-training-page #aiCourseList:hover:not(:disabled),.cc-training-page #aiSelectedSkills:hover:not(:disabled){background:var(--cc-yellow)}
.cc-training-page .ai-course-list-button.is-active{background:var(--cc-yellow)}
.cc-training-page .ai-course-return-button:hover:not(:disabled){background:#000;color:#fff}
.cc-training-page #skillSelectionSection{clear:both;margin:30px 0}
.cc-training-page #skillPanelToggle{display:block;margin:16px auto 0;padding:10px 28px;border:1px solid var(--cc-border);border-radius:12px;background:#fff;color:var(--cc-text);font-size:15px;cursor:pointer}
@media(max-width:1100px){.cc-training-page .training-recommend-heading{display:flex;flex-direction:column}.cc-training-page .ai-course-actions{align-self:flex-end;order:1;margin-top:20px}}
@media(max-width:600px){.cc-training-page .ai-course-actions{width:100%;flex-wrap:wrap;gap:10px}.cc-training-page .ai-action-group{flex:1 1 210px;min-width:0;max-width:100%}.cc-training-page .ai-course-list-button,.cc-training-page .ai-course-return-button{padding:12px 16px}}
.cc-training-page .rec-empty{grid-column:1/-1;padding:32px;border:1px solid var(--cc-border);border-radius:20px;background:white;font-size:16px;line-height:1.8}
</style>
<script>
"use strict";
const rEl=id=>document.getElementById(id);
const rEsc=value=>String(value??"").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
const rState={jobId:null,result:null,roleResult:null,saved:[],controller:null,visibleCourseCount:3,aiBusy:false,activeAction:null,skillSignature:null,availableSkills:[],selectedSkills:[],excludedCompanyNames:[]};
const rMode=value=>({online:"온라인",offline:"오프라인",mixed:"혼합"}[value]||"방식 원문 확인");
const rCost=value=>value==null?"교육비 원문 확인":value===0?"무료":value.toLocaleString("ko-KR")+"원";
function safeCourseUrl(value){try{const u=new URL(value);return ["https:","http:"].includes(u.protocol)&&["www.work24.go.kr","work24.go.kr","hrd.work24.go.kr","www.hrd.go.kr"].includes(u.hostname)&&!u.username&&!u.password?u.href:"";}catch{return "";}}
try{const keys=JSON.parse(localStorage.getItem("training-collection-favorites")||"[]");if(Array.isArray(keys))rState.saved=keys.filter(k=>typeof k==="string");}catch{}
let rToastTimer;
function rToast(message){rEl("aiToast").textContent=message;rEl("aiToast").classList.add("show");clearTimeout(rToastTimer);rToastTimer=setTimeout(()=>rEl("aiToast").classList.remove("show"),2800);}
function latestJobId(){
  const requested=new URLSearchParams(location.search).get("job_id");
  const uuid=/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
  if(requested&&uuid.test(requested))return requested;
  let latest="",savedAt=-Infinity;
  try{for(const key of Object.keys(localStorage)){
    if(!key.startsWith("jd-match-score:v2:"))continue;
    const id=key.slice("jd-match-score:v2:".length);if(!uuid.test(id))continue;
    try{const cached=JSON.parse(localStorage.getItem(key)||"null"),time=Number(cached?.savedAt)||0;
      if(cached&&time>savedAt){latest=id;savedAt=time;}}catch{}
  }}catch{}
  return latest;
}
function readAnalyzedSkills(){
  const id=latestJobId();
  const cached=id?JSON.parse(localStorage.getItem("jd-match-score:v2:"+id)||"null"):null;
  const score=cached?.score||cached;
  const signature=JSON.stringify([id,cached]);
  if(signature!==rState.skillSignature){rState.skillSignature=signature;rState.selectedSkills=[];rState.excludedCompanyNames=[];}
  const skills=[];
  for(const value of Array.isArray(score?.missing_skills)?score.missing_skills:[]){if(typeof value!=="string")continue;const skill=value.trim();if(skill&&!rState.excludedCompanyNames.includes(skill)&&!skills.some(item=>item.toLocaleLowerCase()===skill.toLocaleLowerCase()))skills.push(skill);}
  rState.availableSkills=skills.slice(0,15);
  rState.selectedSkills=rState.selectedSkills.filter(skill=>rState.availableSkills.includes(skill));
  return {hasAnalysis:Array.isArray(score?.missing_skills),skills};
}
function renderSkillSelection(){
  const skills=rState.availableSkills,visible=skills;
  rEl("selectedKeywordCount").textContent="선택한 키워드 "+rState.selectedSkills.length+"개";
  rEl("selectedKeywordList").innerHTML=rState.selectedSkills.length?rState.selectedSkills.map(skill=>'<span class="selected-keyword-chip">'+rEsc(skill)+'</span>').join(""):'<p class="selected-keyword-empty">키워드를 선택해 주세요.</p>';
  rEl("gapPills").innerHTML=visible.length?visible.map(skill=>'<button type="button" class="gap-pill" data-recommend-skill="'+rEsc(skill)+'" aria-pressed="'+rState.selectedSkills.includes(skill)+'"'+(rState.aiBusy?' disabled':'')+'>'+rEsc(skill)+'</button>').join(""):'<span class="gap-pill">저장된 부족 역량 없음</span>';
  rEl("selectedRecommendation").disabled=rState.aiBusy||!skills.length;
}
function setSkillPanelExpanded(expanded){
  rEl("skillSelectionBody").hidden=!expanded;
  rEl("skillPanelToggle").textContent=expanded?"접기":"펼치기";
  rEl("skillPanelToggle").setAttribute("aria-expanded",String(expanded));
  rEl("aiSelectedSkills").setAttribute("aria-expanded",String(expanded));
}
function roleReturnLabel(){
  const role=rState.roleResult?.job.job_name||rState.result?.job.job_name||rState.result?.roles.join(" · ")||"직무별";
  return (role==="기획자"?"기획":role)+" 교육목록 다시 보기";
}
function updateActionButtons(){
  const allActive=rState.activeAction==="all",selectedActive=rState.activeAction==="selected";
  rEl("aiCourseList").classList.toggle("is-active",allActive);
  rEl("aiSelectedSkills").classList.toggle("is-active",selectedActive);
  rEl("aiCourseList").setAttribute("aria-pressed",String(allActive));
  rEl("aiSelectedSkills").setAttribute("aria-pressed",String(selectedActive));
  rEl("returnRoleCourses").hidden=!allActive;
  rEl("returnSelectedRoleCourses").hidden=!selectedActive;
  rEl("returnRoleCourses").textContent=roleReturnLabel();
  rEl("returnSelectedRoleCourses").textContent=roleReturnLabel();
}
function openSkillSelection(){
  rEl("skillSelectionSection").hidden=false;setSkillPanelExpanded(true);
  rState.activeAction="selected";updateActionButtons();
  try{const analyzed=readAnalyzedSkills();rEl("skillRecommendationStatus").textContent=!analyzed.hasAnalysis?"적합도 분석을 먼저 진행해 주세요.":!analyzed.skills.length?"현재 분석에서 확인된 부족 역량이 없습니다.":"";}
  catch{rState.availableSkills=[];rState.selectedSkills=[];rEl("skillRecommendationStatus").textContent="분석 결과를 읽지 못했어요. 적합도 분석을 다시 진행해 주세요.";}
  renderSkillSelection();
}
function showEmpty(message){rEl("recommendCards").innerHTML='<p class="rec-empty">'+rEsc(message)+'</p>';}
function renderRecommendations(){
  const data=rState.result;if(!data)return;
  const allItems=data.items.slice(0,15);
  const items=allItems.slice(0,rState.visibleCourseCount);
  rEl("courseMore").hidden=allItems.length<=3;
  rEl("courseMore").textContent=rState.visibleCourseCount>3?"접기":"더보기";
  rEl("courseMore").setAttribute("aria-expanded",String(rState.visibleCourseCount>3));
  const isAi=["groq","gemini"].includes(data.meta.source);
  updateActionButtons();
  rEl("recommendTitle").textContent=isAi?"AI 맞춤 교육 "+allItems.length+"개":(data.job.job_name||data.roles.join(" · ")||"선택 공고 직무")+" 관련 교육 "+allItems.length+"개";
  if(!items.length){showEmpty(isAi?"전체 부족 역량과 연결되는 교육을 찾지 못했어요.":data.roles.length?"선택한 직무와 연관된 교육이 없습니다. 다른 공고를 선택하거나 교육모음에서 검색해 주세요.":"선택한 공고의 직무에 해당하는 교육 분류가 없습니다. 교육모음에서 원하는 교육을 검색해 주세요.");return;}
  rEl("recommendCards").innerHTML=items.map((c,i)=>{
    const saved=rState.saved.includes(c.key);
    return '<article class="rec-card"><div class="rec-card-top"><span class="rec-rank">'+String(i+1).padStart(2,"0")+'</span><button type="button" class="heart" data-course-save="'+rEsc(c.key)+'" aria-label="'+rEsc(c.title)+' 관심 '+(saved?'해제':'저장')+'" aria-pressed="'+saved+'">'+(saved?'♥':'♡')+'</button></div><h3 title="'+rEsc(c.title)+'">'+rEsc(c.title)+'</h3><p class="provider">'+rEsc(c.provider)+'</p><span class="learning-badge">'+rEsc(c.skill_label)+'</span><div class="rec-explanation"><strong class="reason-label">'+(isAi?'AI 추천 이유':'직무 관련 정보')+'</strong><p class="rec-reason" title="'+rEsc(c.reason)+'">'+rEsc(c.reason)+'</p></div><p class="rec-meta">'+rEsc(rCost(c.cost))+' · '+rEsc(rMode(c.mode))+'</p><button type="button" class="rec-detail" data-course-detail="'+rEsc(c.key)+'">교육 상세 / 원문 보기 →</button></article>';
  }).join("");
}
async function loadCourses(){
  if(rState.controller)rState.controller.abort();
  const id=rState.jobId=latestJobId();rState.result=null;
  rState.visibleCourseCount=3;rEl("courseMore").hidden=true;
  rState.activeAction=null;updateActionButtons();
  rEl("recommendTitle").textContent="직무 관련 교육과정 목록";
  rEl("recommendSource").textContent="직무 기반 교육추천 · 고용24 교육 정보";
  rEl("recommendCards").setAttribute("aria-busy","false");
  if(!id){showEmpty("적합도 분석에서 공고를 먼저 선택한 뒤 교육추천을 확인해 주세요.");return;}
  const controller=new AbortController();rState.controller=controller;
  showEmpty("직무와 관련된 교육을 불러오고 있어요.");rEl("recommendCards").setAttribute("aria-busy","true");
  try{
    const response=await fetch("/training_match/api/recommendations",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({job_id:id}),cache:"no-store",signal:controller.signal});
    if(response.status===401){location.assign("/signin");return;}
    const data=await response.json();if(!response.ok)throw new Error(data.error||"교육을 불러오지 못했습니다.");
    if(controller.signal.aborted)return;
    rState.roleResult=data;rState.result=data;renderRecommendations();
    rEl("recommendSource").textContent="고용24 저장 자료 · "+data.meta.fetchedAt+" 조회";
  }catch(error){if(error.name!=="AbortError"){showEmpty((error.message||"교육을 불러오지 못했어요.")+" 페이지를 새로고침해 다시 시도해 주세요.");}}
  finally{if(rState.controller===controller){rState.controller=null;rEl("recommendCards").setAttribute("aria-busy","false");}}
}
function showRecommendedDetail(c){
  const isAi=["groq","gemini"].includes(rState.result?.meta.source);
  const fields=[["교육기관",c.provider],["기간",(c.start||"미정")+" ~ "+(c.end||"미정")],["교육비",rCost(c.cost)],["교육 방식",rMode(c.mode)],[isAi?"학습 목표":"관련 직무",isAi?c.skill_label:c.related_roles.join(" · ")],[isAi?"AI 추천 이유":"직무 관련 정보",c.reason]];
  const url=safeCourseUrl(c.url);
  rEl("recommendDetailBody").innerHTML='<h2 class="modal-title" id="recommendDetailTitle">'+rEsc(c.title)+'</h2><dl class="detail-grid">'+fields.map(([label,value])=>'<dt>'+rEsc(label)+'</dt><dd>'+rEsc(value)+'</dd>').join("")+'</dl><p class="detail-note">교육의 지원 자격·본인부담금과 최신 일정은 고용24 원문에서 확인해 주세요.</p>'+(url?'<a class="primary-link" href="'+rEsc(url)+'" target="_blank" rel="noopener noreferrer">고용24 원문 보기 ↗</a>':'');
  rEl("recommendDetailDialog").showModal();
}
async function recommendAllSkills(selectedOnly=false){
  if(rState.aiBusy)return;
  if(!selectedOnly){rEl("skillSelectionSection").hidden=true;setSkillPanelExpanded(false);}
  const button=rEl("aiCourseList"),status=rEl("aiRecommendationStatus");
  status.hidden=false;
  let skills;
  try{
    const analyzed=readAnalyzedSkills();
    if(!analyzed.hasAnalysis){status.textContent="저장된 분석 결과가 없어요. 적합도 분석을 먼저 진행해 주세요.";return;}
    if(selectedOnly&&!rState.selectedSkills.length){rEl("skillRecommendationStatus").textContent="추천받을 키워드를 하나 이상 선택해 주세요.";return;}
    skills=selectedOnly?[...rState.selectedSkills]:analyzed.skills;
    if(!skills.length){status.textContent="분석 결과에 부족 역량이 없어 추천할 항목이 없습니다.";return;}
  }catch{status.textContent="분석 결과를 읽지 못했어요. 적합도 분석을 다시 진행해 주세요.";return;}
  if(rState.controller)rState.controller.abort();
  const previous=rState.result;
  rState.aiBusy=true;button.disabled=true;button.textContent="맞춤 교육을 찾고 있어요…";
  rEl("aiSelectedSkills").disabled=true;
  renderSkillSelection();
  rEl("returnRoleCourses").disabled=true;
  rEl("returnSelectedRoleCourses").disabled=true;
  const target=selectedOnly?"선택한 역량":"전체 부족 역량";
  status.textContent=target+"에 맞는 교육을 AI가 찾고 있어요.";
  if(selectedOnly)rEl("skillRecommendationStatus").textContent=status.textContent;
  try{
    const response=await fetch("/training_match/api/skill-recommendations",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({missing_skills:skills}),cache:"no-store"});
    if(response.status===401){location.assign("/signin");return;}
    const data=await response.json();if(!response.ok)throw new Error(data.error||"AI 교육 추천을 완료하지 못했어요. 다시 시도해 주세요.");
    rState.excludedCompanyNames=[...new Set([...rState.excludedCompanyNames,...(data.excluded_company_names||[])])];
    readAnalyzedSkills();renderSkillSelection();
    rState.result={...data,job:previous?.job||{job_name:""},roles:previous?.roles||[],meta:{...data.meta,source:data.meta.source||"gemini"},items:data.items.map(c=>({...c,reason:c.ai_reason}))};
    rState.activeAction=selectedOnly?"selected":"all";
    rState.visibleCourseCount=3;renderRecommendations();
    status.textContent=data.items.length?target+"에 맞는 교육 "+data.items.length+"개를 추천했어요.":"회사명을 제외한 부족 역량과 관련된 교육을 찾지 못했어요.";
    if(selectedOnly)rEl("skillRecommendationStatus").textContent=status.textContent;
    rEl("recommendSource").textContent="고용24 저장 자료 · "+data.meta.fetchedAt+" · "+data.meta.model;
  }catch(error){status.textContent=error.message||"AI 교육 추천에 실패했습니다. 다시 시도해 주세요.";if(selectedOnly)rEl("skillRecommendationStatus").textContent=status.textContent;}
  finally{rState.aiBusy=false;button.disabled=false;button.textContent="AI 맞춤 교육 목록 보기";rEl("aiSelectedSkills").disabled=false;rEl("returnRoleCourses").disabled=false;rEl("returnSelectedRoleCourses").disabled=false;renderSkillSelection();}
}
rEl("aiCourseList").addEventListener("click",()=>recommendAllSkills());
rEl("aiSelectedSkills").setAttribute("aria-controls","skillSelectionSection");
rEl("aiSelectedSkills").setAttribute("aria-expanded","false");
rEl("aiSelectedSkills").addEventListener("click",()=>{
  if(rState.aiBusy)return;
  openSkillSelection();
});
rEl("skillPanelToggle").addEventListener("click",()=>setSkillPanelExpanded(rEl("skillSelectionBody").hidden));
rEl("gapPills").addEventListener("click",event=>{
  const button=event.target.closest("[data-recommend-skill]");if(!button||rState.aiBusy)return;
  const skill=button.dataset.recommendSkill;if(!rState.availableSkills.includes(skill))return;
  rState.selectedSkills=rState.selectedSkills.includes(skill)?rState.selectedSkills.filter(item=>item!==skill):[...rState.selectedSkills,skill];
  rEl("skillRecommendationStatus").textContent="";renderSkillSelection();
});
rEl("selectedRecommendation").addEventListener("click",()=>recommendAllSkills(true));
function restoreRoleCourses(){
  if(rState.aiBusy)return;
  rEl("aiRecommendationStatus").hidden=true;
  rEl("skillSelectionSection").hidden=true;setSkillPanelExpanded(false);
  rState.activeAction=null;updateActionButtons();
  if(!rState.roleResult){loadCourses();return;}
  rState.result=rState.roleResult;rState.visibleCourseCount=3;
  renderRecommendations();
  rEl("recommendSource").textContent="고용24 저장 자료 · "+rState.roleResult.meta.fetchedAt+" 조회";
}
rEl("returnRoleCourses").addEventListener("click",restoreRoleCourses);
rEl("returnSelectedRoleCourses").addEventListener("click",restoreRoleCourses);
rEl("courseMore").addEventListener("click",()=>{
  if(!rState.result)return;
  rState.visibleCourseCount=rState.visibleCourseCount>3?3:15;
  renderRecommendations();
});
rEl("recommendDetailClose").addEventListener("click",()=>rEl("recommendDetailDialog").close());
rEl("recommendCards").addEventListener("click",event=>{
  const save=event.target.closest("[data-course-save]"),detail=event.target.closest("[data-course-detail]");
  if(save){const key=save.dataset.courseSave;rState.saved=rState.saved.includes(key)?rState.saved.filter(k=>k!==key):[...rState.saved,key];try{localStorage.setItem("training-collection-favorites",JSON.stringify(rState.saved));rToast("관심목록을 변경했어요.");}catch{rToast("이번 화면에서만 관심 정보가 유지돼요.");}renderRecommendations();}
  if(detail){const course=rState.result?.items.find(c=>c.key===detail.dataset.courseDetail);if(course)showRecommendedDetail(course);}
});
loadCourses();
</script>
</div>
__CC_SCRIPT__
</body></html>
"""

RECOMMEND_PAGE = (
    '<!doctype html><html lang="ko"><head><meta charset="utf-8">'
    '<meta name="viewport" content="width=device-width, initial-scale=1">'
    '<title>직무별 교육추천 · 취준나침반</title><style>'
    + _RECOMMEND_STYLE + RECOMMEND_STYLE + '</style><style>__CC_CSS__</style></head><body class="cc-member-page cc-training-page">'
    + '__CC_HEADER____CC_MENU__' + RECOMMEND_BODY
)
