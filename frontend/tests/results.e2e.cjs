const {chromium}=require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const assert=require('node:assert/strict');
const path=require('node:path');
(async()=>{const browser=await chromium.launch({headless:true,channel:'msedge'});try{
const page=await browser.newPage({viewport:{width:1280,height:1000}});const errors=[];page.on('pageerror',e=>errors.push(e.message));let solves=0;
await page.route('**/api/v1/**',async route=>{const url=new URL(route.request().url());if(url.pathname.endsWith('/solve'))solves++;url.port='8011';await route.continue({url:url.href});});
const api='http://127.0.0.1:8011/api/v1';
const data={name:'Validação dos resultados',objective_type:'max',variables:[{name:'Reformas',objective_coefficient:2,lower_bound:0}],constraints:[{name:'Horas disponíveis',operator:'<=',rhs:10,terms:[{variable_name:'Reformas',coefficient:1}]},{name:'Demanda mínima',operator:'>=',rhs:2,terms:[{variable_name:'Reformas',coefficient:1}]},{name:'Quantidade contratada',operator:'=',rhs:4,terms:[{variable_name:'Reformas',coefficient:1}]}]};
async function create(body){const p=await(await page.request.post(`${api}/problems`,{data:body})).json();const e=await(await page.request.post(`${api}/problems/${p.id}/solve`)).json();return {p,e};}
const {p,e}=await create(data);
await page.goto(`http://127.0.0.1:5173/problems/${p.id}/executions?execution=${e.execution_id}`);
await page.getByRole('heading',{name:'Análise de recursos',exact:true}).waitFor();await page.getByText('Ainda há capacidade disponível em', {exact:false}).waitFor();
assert.equal(await page.locator('.result-utilization progress').count(),1);assert.equal(await page.locator('.result-utilization progress').getAttribute('value'),'40');assert.equal(await page.locator('.result-objective strong').innerText(),'8');
await page.getByRole('button',{name:'Visualizar detalhes técnicos'}).click();assert.equal(await page.locator('.result-technical').getAttribute('open'),'');await page.getByRole('table').filter({has:page.getByText('Análise de recursos da execução',{exact:false})}).count();
await page.getByText('Criar cenário a partir do modelo executado',{exact:true}).click();await page.getByLabel('Nome do cenário').fill('Cópia do resultado');await page.getByRole('button',{name:'Criar cenário',exact:true}).click();await page.getByText(/Cenário #\d+ criado/).waitFor();
const scenarios=await(await page.request.get(`${api}/problems/${p.id}/scenarios`)).json();assert.equal(scenarios.length,1);assert.equal(scenarios[0].model_snapshot.constraints[0].rhs,10);assert.equal((await(await page.request.get(`${api}/problems/${p.id}/executions`)).json()).length,1);
await page.locator('.result-technical').evaluate(el=>el.open=false);await page.screenshot({path:path.join(process.env.WIZARD_TEST_OUTPUT||__dirname,'results-desktop.png'),fullPage:true});await page.setViewportSize({width:390,height:844});assert.ok(await page.locator('.execution-result').evaluate(el=>el.scrollWidth<=el.clientWidth));await page.screenshot({path:path.join(process.env.WIZARD_TEST_OUTPUT||__dirname,'results-mobile.png'),fullPage:true});
for(const [status,operator,rhs] of [['infeasible','<=',-1],['unbounded','>=',1]]){const body={...data,constraints:[{...data.constraints[0],operator,rhs}]};const run=await create(body);assert.equal(run.e.status,status);await page.goto(`http://127.0.0.1:5173/problems/${run.p.id}/executions?execution=${run.e.execution_id}`);await page.getByText(status==='infeasible'?'Problema inviável':'Problema ilimitado',{exact:true}).first().waitFor();assert.equal(await page.locator('.result-utilization progress').count(),0);assert.equal(await page.locator('.result-objective strong').innerText(),'—');}
assert.equal(solves,0);assert.deepEqual(errors,[]);console.log('PASS: ótimo, inviável, ilimitado, ≤ ≥ =, barra aplicável, síntese, snapshot copiado, histórico sem reexecução e mobile.');
}finally{await browser.close();}})().catch(e=>{console.error(e);process.exit(1)});
