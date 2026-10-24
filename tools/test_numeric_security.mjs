import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import vm from 'node:vm';

// Zeitlimit schützt den Testprozess auch dann, wenn die alte Tick-Schleife wieder eingeführt wird.
const source = readFileSync(process.argv[2] || new URL('../dist/heizungsanlage-card.js', import.meta.url), 'utf8');
function context() {
  const classes = new Map();
  const ctx = vm.createContext({
    HTMLElement: class {},
    customElements: { get: (name) => classes.get(name), define: (name, cls) => classes.set(name, cls) },
    window: {}, console: { info() {}, warn() {} },
  });
  vm.runInContext(source, ctx, { timeout: 1000 });
  ctx.Card = classes.get('heizungsanlage-card');
  ctx.assert = assert;
  vm.runInContext("var card = new Card(); card.setConfig({});", ctx);
  return ctx;
}
let failures = 0;
let count = 0;
async function check(name, code, timeout = 250) {
  count++;
  try {
    await vm.runInContext(code, context(), { timeout });
    console.log('PASS ' + name);
  } catch (error) {
    failures++;
    console.error('FAIL ' + name + ': ' + error.message);
  }
}

await check('Normale Temperaturskala bleibt unverändert', `
  assert.deepEqual(Array.from(card._ticks(0, 100, v => 100 - v)), [0,20,40,60,80,100]);
`);
await check('Extreme Wertebereiche haben eine begrenzte, monotone Skala', `
  for (const [mn,mx] of [[0,1e9],[1e20,1e21],[-1e21,-1e20],[1e20,1e20+16384]]) {
    const ticks = card._ticks(mn,mx,v => 100 - (v-mn)/(mx-mn)*100);
    assert.ok(ticks.length >= 2 && ticks.length <= 66);
    assert.equal(ticks[0],mn); assert.equal(ticks.at(-1),mx);
    assert.ok(ticks.every((v,i) => Number.isFinite(v) && (!i || v > ticks[i-1])));
  }
`);
await check('Ungültige und überlaufende Skalen werden verworfen', `
  for (const [mn,mx] of [[NaN,100],[0,Infinity],[-Infinity,0],[10,10],[10,0],[-1e308,1e308]])
    assert.equal(card._ticks(mn,mx,v => v).length,0);
  assert.equal(card._ticks(0,100,() => Infinity).length,0);
`);
for (const [name, method, node] of [
  ['Speicherdiagramm', '_drawChart', 'chart'],
  ['Brennerdiagramm', '_drawBurnerChart', 'chart-burner'],
]) {
  await check(name + ' blockiert bei extremen Verlaufswerten nicht', `
    card._config.entities = {tank_temp:'sensor.ext',boiler_temp:'sensor.ext'};
    card._hass = {states:{},language:'de'};
    const g = {dataset:{},innerHTML:''};
    card.shadowRoot = {getElementById:id => id === '${node}' ? g : null};
    card._alignUnits = () => {};
    for (const values of [[1e20,1e21],[0,1e9],[-1e308,1e308],[1e20,1e20]]) {
      card._hists = {'sensor.ext':values.map((v,i) => ({t:Date.now()-(1-i)*60000,v}))};
      card.${method}();
      assert.ok(g.innerHTML.length > 0 && g.innerHTML.length < 50000);
      assert.ok(!/NaN|Infinity/.test(g.innerHTML));
    }
  `);
  await check(name + ' verarbeitet 200.000 Recorder-Punkte ohne Argumentüberlauf', `
    card._config.entities = {tank_temp:'sensor.ext',boiler_temp:'sensor.ext'};
    card._hass = {states:{},language:'de'};
    const g = {dataset:{},innerHTML:''};
    card.shadowRoot = {getElementById:id => id === '${node}' ? g : null};
    card._alignUnits = () => {};
    const now = Date.now();
    card._hists = {'sensor.ext':Array.from({length:200000},(_,i) => ({t:now-(200000-i)*400,v:40+i%20}))};
    card.${method}();
    assert.ok(g.innerHTML.includes('<path') && !/NaN|Infinity/.test(g.innerHTML));
  `, 2000);
}
await check('Nicht endliche Livewerte und Umrechnungsüberläufe sind nicht numerisch verwendbar', `
  card._hass = {states:{'sensor.x':{state:'Infinity',attributes:{unit_of_measurement:'l/s'}}},language:'de'};
  for (const state of ['Infinity','-Infinity','NaN','1e999']) {
    card._hass.states['sensor.x'].state = state;
    assert.equal(card._num('sensor.x'),null);
    assert.equal(card._convertTo('sensor.x','l/h'),null);
  }
  card._hass.states['sensor.x'].state = '1e308';
  assert.equal(card._convertTo('sensor.x','l/h'),null);
  assert.equal(card._fmtVal(Infinity,'°C'),'–');
  card._hass.states['sensor.x'].state = '0.1';
  assert.equal(card._convertTo('sensor.x','l/h'),360);
`);
await check('Recorder-Daten verwerfen nicht endliche Messwerte und Zeitpunkte', `
  card._config.entities = {tank_temp:'sensor.x'};
  card._drawChart = () => {}; card._drawBurnerChart = () => {};
  card._hass = {callWS:async () => ({'sensor.x':[
    {s:'44.1',lu:1000},{s:'Infinity',lu:2000},{s:'NaN',lu:3000},
    {s:'50',lu:Infinity},{s:'51',lu:1e308},{s:'45',lu:4000}
  ]})};
  card._loadHistory().then(() => {
    const points = card._hists['sensor.x'];
    assert.equal(points.length,2);
    assert.ok(points.every(p => Number.isFinite(p.v) && Number.isFinite(p.t)));
    assert.equal(points[0].v,44.1); assert.equal(points[1].v,45);
  });
`);
console.log(`\n${count} Prüfungen, ${failures} Fehler`);
process.exitCode = failures ? 1 : 0;
