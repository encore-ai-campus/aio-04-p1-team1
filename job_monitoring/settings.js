const list=document.getElementById('monitoring-rows'),add=document.getElementById('add-row'),save=document.getElementById('save-settings'),status=document.getElementById('settings-status');
const endpoint='/api/job-monitoring/settings';
function appendRow(item={}){
 const row=document.createElement('div');row.className='monitoring-row';
 if(item.id)row.dataset.id=item.id;
 for(const [key,label,placeholder] of [['platform_name','플랫폼명','잡코리아'],['platform_email','발신 이메일 주소','job-alert@example.com'],['user_email','수신 이메일 주소','me@example.com']]){
  const input=document.createElement('input');input.type=key==='platform_name'?'text':'email';input.dataset.key=key;input.setAttribute('aria-label',label);input.placeholder=placeholder;input.value=item[key]||'';input.required=true;input.maxLength=key==='platform_name'?200:320;row.append(input);
 }
 const remove=document.createElement('button');remove.type='button';remove.textContent='삭제';remove.addEventListener('click',()=>row.remove());row.append(remove);list.append(row);
}
function render(items){list.replaceChildren();items.forEach(appendRow);if(!items.length)appendRow();}
async function request(options){
 const response=await fetch(endpoint,options);
 if(!response.ok)throw new Error(response.status===401?'로그인이 필요합니다. 다시 로그인해주세요.':'설정을 처리하지 못했습니다. 다시 시도해주세요.');
 return response.json();
}
add.disabled=true;
add.addEventListener('click',()=>appendRow());
save.addEventListener('click',async()=>{
 const items=[];
 for(const row of list.children){
  const inputs=[...row.querySelectorAll('input')];
  if(!row.dataset.id&&inputs.every(input=>!input.value.trim()))continue;
  for(const input of inputs){input.value=input.value.trim();if(!input.reportValidity())return;}
  const item=Object.fromEntries(inputs.map(input=>[input.dataset.key,input.value]));if(row.dataset.id)item.id=row.dataset.id;items.push(item);
 }
 save.disabled=true;add.disabled=true;list.inert=true;status.textContent='저장 중입니다…';
 try{const result=await request({method:'PUT',headers:{'Content-Type':'application/json'},body:JSON.stringify({items})});render(result.items);status.textContent='저장했습니다.';}
 catch(error){status.textContent=error.message;}
 finally{save.disabled=false;add.disabled=false;list.inert=false;}
});
(async()=>{status.textContent='설정을 불러오는 중입니다…';try{const result=await request();render(result.items);save.disabled=false;add.disabled=false;status.textContent='';}catch(error){status.textContent=error.message+' 새로고침해주세요.';}})();
