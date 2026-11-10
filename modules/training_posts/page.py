"""교육목록 HTML/CSS/JavaScript 화면."""

PAGE = r"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>교육모음 · 취준나침반</title>
<meta name="description" content="고용24 내일배움 교육을 분야, 방식, 교육비로 찾아보고 관심목록에 저장하세요.">
<style>
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
</style>
</head>
<body>
<header class="header"><div class="wrap">
<button class="brand" type="button" aria-label="취준나침반"><svg viewBox="0 0 44 44" aria-hidden="true"><circle cx="22" cy="22" r="22" fill="#facd40"/><path d="M31 8 25 24 13 35 19 19Z" fill="#29392b"/><path d="M19 19 25 24 22 21Z" fill="#fdf9d9"/></svg><span>취준나침반</span></button>
<nav class="nav" aria-label="주 메뉴"><button type="button">메인</button><button type="button">공고모음</button><button type="button" class="active" aria-current="page">교육모음</button><button type="button">적합도 분석</button><button type="button" onclick="location.href='/training_match'">교육추천</button></nav>
<div class="account"><span>김나침님</span><button class="mypage" type="button">마이페이지</button></div>
</div></header>
<main class="wrap">
<section class="hero"><p class="eyebrow">YOUR NEXT DIRECTION</p><h1>다음 성장을 위한 교육을 찾아보세요</h1><p class="subtitle">직무에 필요한 교육을 조건별로 살펴보고 관심목록에 저장하세요.</p></section>
<div class="layout">
<aside class="sidebar" aria-label="검색 조건">
<div class="sidebar-head"><h2>검색 조건</h2><button type="button" class="reset" id="resetButton">초기화</button></div>
<form id="filterForm" class="filter-form">
<label class="field"><span>직무 / 분야</span><div class="select-wrap"><select id="category" aria-label="직무 / 분야"><option value="">전체 분야</option><option value="hr" selected>인사·HR</option>__CATEGORY_OPTIONS__</select></div></label>
<label class="field"><span>교육 방식</span><div class="select-wrap"><select id="mode" aria-label="교육 방식"><option value="all">전체 방식</option><option value="online" selected>온라인</option><option value="offline">오프라인</option><option value="mixed">혼합</option><option value="unknown">방식 확인 필요</option></select></div></label>
<label class="field"><span>교육비</span><div class="select-wrap"><select id="budget" aria-label="교육비"><option value="">전체 금액</option><option value="0">무료</option><option value="100000" selected>무료·10만원 이하</option><option value="300000">30만원 이하</option><option value="500000">50만원 이하</option></select></div></label>
<button type="submit" class="apply" id="applyButton">조건 적용</button>
</form>
<p class="sidebar-note">표시 금액은 API 수강비입니다.<br>본인부담금·지원 자격은 원문에서 확인해 주세요.</p>
</aside>
<section class="result-area" aria-label="교육 검색 결과">
<form class="search" id="searchForm"><input id="searchInput" type="search" aria-label="교육 검색" placeholder="교육명, 교육기관 또는 기술 검색" maxlength="200"><button type="submit" id="searchButton">검색</button></form>
<div class="results-head"><h2 id="resultsTitle" aria-live="polite">검색된 교육</h2><div class="sort"><select id="sort" aria-label="교육 정렬"><option value="latest">최신순</option><option value="cost_low">교육비 낮은순</option><option value="cost_high">교육비 높은순</option><option value="title">교육명순</option></select></div></div>
<div id="chips" class="chips" aria-label="적용된 검색 조건"></div>
<p id="dataNote" class="catalogue-note" role="status"></p>
<div id="cards" class="cards" aria-live="polite"></div>
<nav id="pagination" class="pagination" aria-label="교육 페이지"></nav>
</section>
</div>
<footer><span>취준나침반 · 한 번에 찾고, 한 걸음씩 준비해요.</span><span id="sourceNote">교육모음 · 고용24 실제 교육 정보</span></footer>
</main>
<dialog id="detailDialog" aria-labelledby="detailTitle"><div class="modal-top"><p>COURSE DETAILS</p><button class="close" type="button" id="closeDetail" aria-label="교육 상세 닫기">×</button></div><div id="detailBody"></div></dialog>
<div class="toast" id="toast" role="status"></div>
<script id="initial-data" type="application/json">__INITIAL_DATA__</script>
<script>
"use strict";
const el = (id) => document.getElementById(id);
const PAGE_SIZE = 4;
const state = {data:JSON.parse(el("initial-data").textContent),filtered:[],page:0,saved:[],filter:{category:"hr",mode:"online",budget:"100000",query:""},controller:null,generation:0};
try { const saved=JSON.parse(localStorage.getItem("training-collection-favorites")||"[]"); if(Array.isArray(saved))state.saved=saved.filter(k=>typeof k==="string"); } catch {}
const esc=(value)=>String(value??"").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
const modeName=(value)=>({online:"온라인",offline:"오프라인",mixed:"혼합",unknown:"방식 확인 필요",all:"전체 방식"}[value]||"방식 확인 필요");
const costText=(value)=>value==null?"교육비 원문 확인":value===0?"무료":value.toLocaleString("ko-KR")+"원";
const safeUrl=(value)=>{try{const u=new URL(value);return ["https:","http:"].includes(u.protocol)&&["www.work24.go.kr","work24.go.kr","hrd.work24.go.kr","www.hrd.go.kr"].includes(u.hostname)?u.href:"";}catch{return "";}};
let toastTimer;
function toast(message){el("toast").textContent=message;el("toast").classList.add("show");clearTimeout(toastTimer);toastTimer=setTimeout(()=>el("toast").classList.remove("show"),2800);}
function pendingFilter(){return {category:el("category").value,mode:el("mode").value,budget:el("budget").value,query:el("searchInput").value.trim()};}
function categoryMatch(course,value){
  if(!value)return true;
  if(value==="hr")return course.category==="02"&&/인사|인적|노무|급여|\bhr\b|excel|엑셀|sql|사무|행정|보고서/i.test(course.title);
  return course.category===value;
}
function applyFilters(){
  const f=state.filter;
  state.filtered=state.data.courses.filter(c=>{
    if(!categoryMatch(c,f.category))return false;
    if(f.mode!=="all"&&c.mode!==f.mode)return false;
    if(f.budget!==""&&(c.cost==null||c.cost>Number(f.budget)))return false;
    if(f.query){const haystack=[c.title,c.provider,c.categoryName,...c.tags].join(" ").toLocaleLowerCase();const terms=f.query.toLocaleLowerCase().split(/\s+/).filter(Boolean);if(!terms.every(t=>haystack.includes(t)))return false;}
    return true;
  });
  const sort=el("sort").value;
  state.filtered.sort((a,b)=>b.start.localeCompare(a.start)||a.key.localeCompare(b.key));
  if(sort==="cost_low")state.filtered.sort((a,b)=>(a.cost??Infinity)-(b.cost??Infinity));
  if(sort==="cost_high")state.filtered.sort((a,b)=>(b.cost??-1)-(a.cost??-1));
  if(sort==="title")state.filtered.sort((a,b)=>a.title.localeCompare(b.title,"ko"));
  state.page=0;render();
}
function render(){
  const total=state.filtered.length;
  const pages=Math.ceil(total/PAGE_SIZE);
  state.page=Math.max(0,Math.min(state.page,Math.max(0,pages-1)));
  el("resultsTitle").textContent="검색된 교육 "+total+"개";
  const f=state.filter,chips=[];
  if(f.category)chips.push(f.category==="hr"?"인사·HR":state.data.categories.find(c=>c.code===f.category)?.name||f.category);
  if(f.mode!=="all")chips.push(modeName(f.mode));
  if(f.budget!=="")chips.push(f.budget==="0"?"무료":"무료·"+(Number(f.budget)/10000)+"만원 이하");
  if(f.query)chips.push("검색: "+f.query);
  el("chips").innerHTML=chips.map(text=>'<span class="chip">'+esc(text)+'</span>').join("");
  el("dataNote").textContent=state.data.errors.length?state.data.errors.map(item=>item.message).join(" "):"";
  el("dataNote").classList.toggle("error-note",state.data.errors.length>0);
  el("sourceNote").textContent="고용24 · Supabase 저장 자료 · "+state.data.fetchedAt+" 저장";
  const visible=state.filtered.slice(state.page*PAGE_SIZE,(state.page+1)*PAGE_SIZE);
  el("cards").innerHTML=visible.length?visible.map(c=>{
    const saved=state.saved.includes(c.key);
    const tags=c.tags.length?c.tags:[c.categoryName];
    return '<article class="card"><div class="card-top"><span class="badge">'+esc(c.badge)+'</span><button class="heart" type="button" data-save="'+esc(c.key)+'" aria-label="'+esc(c.title)+' 관심 '+(saved?'해제':'저장')+'" aria-pressed="'+saved+'">'+(saved?'♥':'♡')+'</button></div><h3 title="'+esc(c.title)+'">'+esc(c.title)+'</h3><p class="provider">'+esc(c.provider)+'</p><p class="card-meta">'+esc(costText(c.cost))+' · '+esc(modeName(c.mode))+' · '+(c.weeks?c.weeks+'주':'기간 확인')+'</p><div class="tags">'+tags.map(t=>'<span>'+esc(t)+'</span>').join("")+'</div><button class="details" type="button" data-detail="'+esc(c.key)+'">상세 보기 →</button></article>';
  }).join(""):'<div class="empty"><h3>조건에 맞는 교육이 없어요</h3><p>검색어나 분야·교육 방식·교육비 조건을 넓혀서 다시 찾아보세요. 금액이 확인되지 않은 교육은 교육비 제한에서 제외됩니다.</p><button id="emptyReset" type="button">조건 초기화</button></div>';
  el("emptyReset")?.addEventListener("click",reset);
  if(pages<=1){el("pagination").innerHTML="";return;}
  const indexes=new Set([0,pages-1]);
  for(let p=Math.max(0,state.page-1);p<=Math.min(pages-1,state.page+2);p++)indexes.add(p);
  let html="",previous=-1;
  if(state.page>0)html+='<button type="button" data-page="'+(state.page-1)+'" aria-label="이전 페이지">이전</button>';
  for(const p of [...indexes].sort((a,b)=>a-b)){
    if(previous>=0&&p-previous>1)html+='<span class="dots">…</span>';
    html+='<button type="button" data-page="'+p+'" class="'+(p===state.page?'selected':'')+'" '+(p===state.page?'aria-current="page"':'')+' aria-label="'+(p+1)+'페이지">'+(p+1)+'</button>';
    previous=p;
  }
  if(state.page<pages-1)html+='<button type="button" data-page="'+(state.page+1)+'" aria-label="다음 페이지">다음</button>';
  el("pagination").innerHTML=html;
}
async function reloadAndApply(){
  state.controller?.abort();state.controller=new AbortController();
  const generation=++state.generation,nextFilter=pendingFilter();
  el("cards").classList.add("loading");el("cards").setAttribute("aria-busy","true");
  el("applyButton").disabled=true;el("searchButton").disabled=true;el("dataNote").textContent="저장된 교육목록을 불러오고 있어요…";
  try{
    const response=await fetch("/training_posts?data=1",{signal:state.controller.signal,cache:"no-store"});
    if(!response.ok)throw new Error("조회 실패");
    const data=await response.json();
    if(generation!==state.generation)return;
    state.data=data;state.filter=nextFilter;applyFilters();
  }catch(error){
    if(error.name==="AbortError"||generation!==state.generation)return;
    el("dataNote").textContent="새 조회에 실패했습니다. 현재 화면을 유지하며, 검색 또는 조건 적용으로 다시 시도할 수 있어요.";el("dataNote").classList.add("error-note");
  }finally{
    if(generation===state.generation){el("cards").classList.remove("loading");el("cards").setAttribute("aria-busy","false");el("applyButton").disabled=false;el("searchButton").disabled=false;}
  }
}
function reset(){el("category").value="";el("mode").value="all";el("budget").value="";el("searchInput").value="";el("sort").value="latest";reloadAndApply();}
function showDetails(c){
  const url=safeUrl(c.url);
  const fields=[["교육기관",c.provider],["분야",c.categoryName],["교육 방식",modeName(c.mode)+(c.modeEvidence?" · "+c.modeEvidence:"")],["교육 기간",(c.start||"미정")+" ~ "+(c.end||"미정")],["API 수강비",costText(c.cost)],["실제 훈련비",c.rawRealCost?c.rawRealCost+"원":"원문 확인"],["개인 본인부담금","고용24 원문에서 확인"],["지역",c.address||"원문 확인"],["과정 ID",c.courseId],["훈련 회차",c.round+"회차"],["NCS 코드",c.ncsCode||"미제공"]];
  el("detailBody").innerHTML='<h2 class="modal-title" id="detailTitle">'+esc(c.title)+'</h2><dl class="detail-grid">'+fields.map(([label,value])=>'<dt>'+esc(label)+'</dt><dd>'+esc(value)+'</dd>').join("")+'</dl><p class="detail-note">교육 방식은 API에 명시된 근거로 분류하며, 확인되지 않은 경우 별도 표시합니다. 표시 금액은 개인별 본인부담금이 아니므로 원문에서 확인해 주세요.</p>'+(url?'<a class="primary-link" href="'+esc(url)+'" target="_blank" rel="noopener noreferrer">고용24 원문 보기 ↗</a>':'');
  el("detailDialog").showModal();
}
el("filterForm").addEventListener("submit",e=>{e.preventDefault();reloadAndApply();});
el("searchForm").addEventListener("submit",e=>{e.preventDefault();reloadAndApply();});
el("resetButton").addEventListener("click",reset);
el("sort").addEventListener("change",applyFilters);
el("cards").addEventListener("click",e=>{
  const save=e.target.closest("[data-save]"),detail=e.target.closest("[data-detail]");
  if(save){
    const key=save.dataset.save,already=state.saved.includes(key);
    state.saved=already?state.saved.filter(k=>k!==key):[...state.saved,key];
    try{localStorage.setItem("training-collection-favorites",JSON.stringify(state.saved));toast(already?"관심목록에서 해제했어요.":"관심목록에 저장했어요.");}catch{toast("브라우저 저장을 사용할 수 없어 이번 화면에서만 유지됩니다.");}
    render();
  }
  if(detail){const c=state.data.courses.find(c=>c.key===detail.dataset.detail);if(c)showDetails(c);}
});
el("pagination").addEventListener("click",e=>{const button=e.target.closest("[data-page]");if(button){state.page=Number(button.dataset.page);render();}});
el("closeDetail").addEventListener("click",()=>el("detailDialog").close());
el("detailDialog").addEventListener("click",e=>{if(e.target===el("detailDialog")){const box=e.target.getBoundingClientRect();if(e.clientX<box.left||e.clientX>box.right||e.clientY<box.top||e.clientY>box.bottom)e.target.close();}});
applyFilters();
</script>
</body></html>
"""
