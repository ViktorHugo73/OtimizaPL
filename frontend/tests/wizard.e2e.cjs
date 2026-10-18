// Requer API isolada em 8011 e Vite em 5173. Não usa o banco de produção.
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const assert = require('node:assert/strict');
const path = require('node:path');
const fs = require('node:fs');
const output = process.env.WIZARD_TEST_OUTPUT || __dirname;
const api = 'http://127.0.0.1:8011/api/v1';
const stamp = Date.now();
(async () => {
  const browser = await chromium.launch({ headless: true, channel: 'msedge' });
  try {
    const page = await browser.newPage({ viewport: { width: 1280, height: 960 } });
    const errors = []; page.on('pageerror', e => errors.push(e.message));
    let createCalls = 0, failSolve = false, failCreate = false;
    await page.route('**/api/v1/**', async route => {
      const request = route.request();
      const url = new URL(request.url());
      if (request.method() === 'POST' && url.pathname === '/api/v1/problems') {
        createCalls++;
        if (failCreate) { failCreate = false; return route.fulfill({status:422, contentType:'application/json', body:JSON.stringify({detail:[{loc:['body','name'],msg:'Nome rejeitado para conferência'}]})}); }
      }
      if (failSolve && url.pathname.endsWith('/solve')) { failSolve = false; return route.fulfill({status:503, contentType:'application/json', body:JSON.stringify({detail:'Falha simulada na resolução'})}); }
      url.port = '8011';
      await route.continue({url:url.href});
    });
    const next = () => page.getByRole('button', {name:'Continuar',exact:true}).click();
    const group = name => page.getByRole('group',{name,exact:true});
    const start = async name => {
      await page.goto('http://127.0.0.1:5173/problems/new');
      await page.getByLabel('Nome do problema',{exact:true}).fill(name);
    };
    page.on('dialog', dialog => dialog.accept());

    // Duas variáveis, retorno às etapas, exclusão e validações próximas aos campos.
    await start(''); await next();
    await page.getByText('Informe o nome do problema.',{exact:true}).waitFor();
    await page.getByLabel('Nome do problema',{exact:true}).fill(`E2E duas decisões ${stamp}`);
    await page.getByLabel('Segmento de aplicação').selectOption('Serviços');
    await next();
    await page.getByRole('button',{name:'＋ Adicionar decisão',exact:true}).click();
    await group('Decisão 2').getByLabel('Nome da decisão',{exact:true}).fill('X1'); await next();
    assert.equal(await page.getByText('Este nome já está em uso.',{exact:true}).count(),2);
    await group('Decisão 2').getByLabel('Nome da decisão',{exact:true}).fill('X2'); await next();
    await page.getByRole('radio',{name:'Maximizar — aumentar lucro, produção ou retorno'}).check();
    await page.getByLabel('X1 — contribuição por unidade',{exact:true}).fill(''); await next();
    await page.getByText('Informe um valor numérico finito.',{exact:true}).waitFor();
    await page.getByLabel('X1 — contribuição por unidade',{exact:true}).fill('3');
    await page.getByLabel('X2 — contribuição por unidade',{exact:true}).fill('2'); await next();
    await next(); await page.getByText('Adicione pelo menos uma condição.',{exact:true}).waitFor();
    await page.getByRole('button',{name:'＋ Adicionar condição',exact:true}).click();
    await group('Condição 1').getByLabel('Nome da condição').fill('Capacidade');
    await group('Condição 1').getByLabel('Limite').fill('4');
    await group('Condição 1').getByLabel('X1',{exact:true}).fill('1');
    await group('Condição 1').getByLabel('X2',{exact:true}).fill('1');
    await page.getByRole('button',{name:'＋ Adicionar condição',exact:true}).click();
    await group('Condição 2').getByLabel('Nome da condição').fill('Limite de X1');
    await group('Condição 2').getByLabel('Limite').fill('2');
    await group('Condição 2').getByLabel('X1',{exact:true}).fill('1');
    // Renomear preserva os coeficientes por ID; remover limpa a matriz.
    await page.getByRole('button',{name:'Decisões',exact:true}).click();
    await group('Decisão 1').getByLabel('Nome da decisão',{exact:true}).fill('REFORMAS');
    await page.getByRole('button',{name:'＋ Adicionar decisão',exact:true}).click();
    await page.getByRole('button',{name:'Excluir decisão 3',exact:true}).click();
    await next(); assert.equal(await page.getByLabel('REFORMAS — contribuição por unidade',{exact:true}).inputValue(),'3'); await next();
    assert.equal(await group('Condição 1').getByLabel('REFORMAS',{exact:true}).inputValue(),'1');
    await page.screenshot({path:path.join(output,'wizard-desktop.png'),fullPage:true});
    await next();
    await page.getByRole('button',{name:'Salvar e resolver',exact:true}).click();
    await page.waitForURL(/\/executions\?execution=/);
    await page.getByRole('heading',{name:/Execução #/}).waitFor();
    const twoId = Number(new URL(page.url()).pathname.split('/')[2]);
    const two = await (await page.request.get(`${api}/problems/${twoId}`)).json();
    assert.equal(two.variables.length,2); assert.ok(two.description.includes('Segmento: Serviços'));
    let history = await (await page.request.get(`${api}/problems/${twoId}/executions`)).json();
    assert.equal(history[0].status,'optimal'); assert.ok(Math.abs(history[0].objective_value-10)<1e-7);
    const scenario = await (await page.request.post(`${api}/problems/${twoId}/scenarios`,{data:{name:'Cenário do formulário'}})).json();
    const scenarioResult = await (await page.request.post(`${api}/scenarios/${scenario.id}/solve`)).json();
    assert.equal(scenarioResult.status,'optimal');
    assert.equal((await (await page.request.get(`${api}/problems/${twoId}/executions`)).json()).length,2);

    // Três variáveis, erro estruturado de cadastro, erro após salvar e retomada sem duplicação.
    await start('');
    await page.getByText('Recuperar rascunho ou carregar exemplo',{exact:true}).click(); await page.getByRole('button',{name:'Carregar exemplo de validação: mix de produção'}).click();
    await page.getByLabel('Nome do problema',{exact:true}).fill(`E2E mix ${stamp}`);
    await next(); await next(); await next();
    await page.setViewportSize({width:390,height:844});
    await page.screenshot({path:path.join(output,'wizard-mobile.png'),fullPage:true});
    assert.equal(await page.locator('main').evaluate(el=>el.scrollWidth>el.clientWidth),false);
    await next();
    failCreate = true;
    await page.getByRole('button',{name:'Salvar e resolver',exact:true}).click();
    await page.getByRole('alert').getByText(/Nome: Nome rejeitado/).waitFor();
    const before = createCalls;
    failSolve = true;
    await page.getByRole('button',{name:'Salvar e resolver',exact:true}).click();
    await page.getByRole('alert').getByText(/Problema #\d+ salvo/).waitFor();
    assert.equal(createCalls,before+1);
    await page.getByRole('button',{name:'Tentar resolver novamente',exact:true}).click();
    await page.waitForURL(/\/executions\?execution=/);
    await page.getByRole('heading',{name:/Execução #/}).waitFor();
    assert.equal(createCalls,before+1);
    const mixId=Number(new URL(page.url()).pathname.split('/')[2]);
    history=await (await page.request.get(`${api}/problems/${mixId}/executions`)).json();
    assert.ok(Math.abs(history[0].objective_value-36)<1e-7);

    // Salvar sem resolver: persistência consultável e histórico vazio.
    await start(''); await page.getByText('Recuperar rascunho ou carregar exemplo',{exact:true}).click(); await page.getByRole('button',{name:'Carregar exemplo de validação: mix de produção'}).click();
    await page.getByLabel('Nome do problema',{exact:true}).fill(`E2E apenas salvar ${stamp}`);
    await next(); await next(); await next(); await next();
    await page.getByRole('button',{name:'Salvar',exact:true}).click();
    await page.waitForURL(/\/problems\/\d+$/);
    const savedId = Number(page.url().split('/').at(-1));
    await page.reload(); await page.getByRole('heading',{name:`E2E apenas salvar ${stamp}`}).waitFor();
    assert.equal((await (await page.request.get(`${api}/problems/${savedId}/executions`)).json()).length,0);

    // Inviabilidade é resultado do solver, não erro de preenchimento.
    await start(''); await page.getByText('Recuperar rascunho ou carregar exemplo',{exact:true}).click(); await page.getByRole('button',{name:'Carregar exemplo de validação: mix de produção'}).click();
    await page.getByLabel('Nome do problema',{exact:true}).fill(`E2E inviável ${stamp}`);
    await next(); await group('Decisão 1').getByText('Descrição e limites opcionais').click(); await group('Decisão 1').getByLabel('Quantidade mínima',{exact:true}).fill('5');
    await next(); await next(); await next();
    await page.getByRole('button',{name:'Salvar e resolver',exact:true}).click(); await page.waitForURL(/\/executions\?execution=/);
    await page.getByRole('heading',{name:/Execução #/}).waitFor();
    const infeasibleId=Number(new URL(page.url()).pathname.split('/')[2]);
    assert.equal((await (await page.request.get(`${api}/problems/${infeasibleId}/executions`)).json())[0].status,'infeasible');

    await start(`E2E ilimitado ${stamp}`); await next(); await next();
    await page.getByRole('radio',{name:'Maximizar — aumentar lucro, produção ou retorno'}).check();
    await page.getByLabel('X1 — contribuição por unidade',{exact:true}).fill('1'); await next();
    await page.getByRole('button',{name:'＋ Adicionar condição',exact:true}).click();
    await group('Condição 1').getByLabel('Condição',{exact:true}).selectOption('>=');
    await group('Condição 1').getByLabel('Limite').fill('1');
    await group('Condição 1').getByLabel('X1',{exact:true}).fill('1'); await next();
    await page.getByRole('button',{name:'Salvar e resolver',exact:true}).click(); await page.waitForURL(/\/executions\?execution=/);
    const unboundedId=Number(new URL(page.url()).pathname.split('/')[2]);
    assert.equal((await (await page.request.get(`${api}/problems/${unboundedId}/executions`)).json())[0].status,'unbounded');
    assert.deepEqual(errors,[]);
    const result={twoId,mixId,savedId,infeasibleId,unboundedId,checks:'Cinco etapas, validação, duas e três variáveis, edição da matriz, persistência, cenários, histórico, salvar, salvar e resolver, retomada sem duplicação, inviável, ilimitado, desktop e mobile.'};
    fs.writeFileSync(path.join(output,'wizard-e2e-results.json'),JSON.stringify(result,null,2));
    console.log(JSON.stringify(result));
  } finally { await browser.close(); }
})().catch(e=>{console.error(e);process.exitCode=1;});
