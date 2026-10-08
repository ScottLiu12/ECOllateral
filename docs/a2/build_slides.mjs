// Execute a copy in data/processed/a2-build/slides, linked to bundled node_modules.
// Required environment: SKILL_DIR, WORKSPACE_DIR, RUNTIME_PYTHON, RUNTIME_NODE,
// RUNTIME_NODE_MODULES, TMP_DIR. FINAL_NAME must be unused for each finalization.
import fs from 'node:fs/promises';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
import {Presentation, PresentationFile, FileBlob} from '@oai/artifact-tool';

const {SKILL_DIR, WORKSPACE_DIR, RUNTIME_PYTHON, TMP_DIR} = process.env;
for (const value of [SKILL_DIR, WORKSPACE_DIR, RUNTIME_PYTHON, TMP_DIR]) {
  if (!path.isAbsolute(value ?? '')) throw new Error('Set absolute runtime and workspace paths');
}
const {resolvePresentationFont, applyPresentationChartFont, finalizePresentation} =
  await import(pathToFileURL(path.join(SKILL_DIR, 'container_tools/artifact_tool_utils.mjs')));
// Georgia is one of the user's requested editorial serif examples. Arial provides
// a clean sans-serif counterpart; both are verified in the Windows font inventory.
const family = resolvePresentationFont({fontFamily:'Arial'});
const headingFamily = resolvePresentationFont({fontFamily:'Georgia'});
const p = Presentation.create({slideSize: {width: 1280, height: 720}});
const navy = '#111827', lavender = '#B8ADF3', gray = '#6B7280';
const canvas = '#F9FAFB', ruleColor = '#E5E7EB';
const out = path.join(WORKSPACE_DIR, 'docs/a2');
await fs.mkdir(TMP_DIR, {recursive: true});

function text(s, value, x, y, w, h, size = 27, bold = false, color = navy, font = family) {
  const shape = s.shapes.add({geometry: 'textbox',
    position: {left: x, top: y, width: w, height: h},
    fill: 'none', line: {fill: 'none', width: 0}});
  shape.text = value;
  shape.text.style = {typeface: font, fontSize: size, bold, color, autoFit: 'none',
    insets:{left:0,right:0,top:0,bottom:0}};
  return shape;
}
function rule(s,x,y,w,color=ruleColor) {
  return s.shapes.add({geometry:'rect',position:{left:x,top:y,width:w,height:1},
    fill:color,line:{fill:'none',width:0}});
}
function slide(title, source, cover=false) {
  const s = p.slides.add();
  s.background.fill = canvas;
  text(s, 'E C O L L A T E R A L   /   C S C I  4 1 5 0  A 2', 80, 36, 1000, 22, 14, false, gray);
  const titleY=cover?143:91, titleH=cover?180:110;
  s.shapes.add({geometry:'rect',position:{left:66,top:titleY+2,width:1.5,height:titleH-7},
    fill:navy,line:{fill:'none',width:0}});
  text(s, title.toUpperCase(), 85, titleY, cover?1060:1105, titleH, cover?58:43, false, navy, headingFamily);
  const sourceLabel = /^E[1-5]/.test(source) ? 'Evidence: '+source : source;
  text(s, sourceLabel, 80, 664, 1070, 35, 13, false, gray);
  text(s, String(p.slides.items.length).padStart(2,'0'), 1180, 664, 36, 24, 14, false, gray);
  return s;
}
const supportingNotes = [];
function note(s, content) {supportingNotes[p.slides.items.length-1] = content;}
function chart(s, categories, series, yTitle, yMax, format,
  frame={left:76,top:248,width:700,height:292}) {
  // Ten significant digits preserve display accuracy and fit Excel's numeric limit.
  // The evidence CSVs retain full precision; chart workbooks are intentional snapshots.
  series = series.map(item => ({...item, values:item.values.map(v=>Number(v.toPrecision(10)))}));
  const c = s.charts.add('bar', {
    position: frame, categories, series,
    barOptions: {direction: 'column', grouping: 'clustered', gapWidth: 100},
    hasLegend: series.length > 1,
    legend: {position: 'bottom', textStyle: {fontSize: 19, fill: gray}},
    xAxis: {textStyle: {fontSize: 20, fill: navy}},
    yAxis: {min: 0, max: yMax, numberFormatCode: format,
      title: {text: yTitle, textStyle: {fontSize: 17, fill: gray}},
      textStyle: {fontSize: 17, fill: gray},
      majorGridlines: {fill: ruleColor, width: 1}},
    chartFill: canvas, plotAreaFill: canvas,
    dataLabels: {showValue: false, textStyle: {fontSize: 23}},
  });
  applyPresentationChartFont(c, {fontFamily: family});
  return c;
}

let s = slide('Problem & users:\necosystems across an area',
  'October 7 test results. Made-up water-use targets. Area impacts still need real-world tests.',true);
text(s, 'Shaun, Troy, Scott', 85, 100, 650, 28, 20, false, gray);
text(s, "How could new development affect an area's water supply and rivers through the year?", 85, 334, 1100, 65, 25);
text(s, 'P R O J E C T  G O A L', 85, 426, 510, 30, 16, false, gray);
rule(s,85,465,435);
text(s, 'Water available each season\nWater used and returned\nTown reserves + local rivers', 85, 483, 530, 115, 25);
text(s, 'W O R K I N G  D E M O', 660, 426, 540, 30, 16, false, gray);
rule(s,660,465,535);
text(s, 'Weather data + cooling-water model\nRules check numbers + permit quotes\nFull area assessment still to build', 660, 483, 535, 115, 25);
text(s, 'Cooling is one example. Users: town planners, researchers, water providers.', 85, 616, 1110, 27, 19, false, gray);
note(s, 'Shaun, 30 seconds. Source: docs/a2/dossier.md section 1; docs/a2/evidence/forecast.json. '
  + 'Synthetic labels and fictional permits. Public ingestion is a parser smoke test. '
  + 'The current collateral stress field is an on-site consumption proxy. Assigned day is pending.');

s = slide('Semantic map: current system',
  'E3/E4: constraint-failure-cases.json; retrieval-cases.json | Diagram shows current prototype');
text(s, 'Demo request: equipment size, cooling type, watershed code, month. Exact location is optional.', 80, 231, 1135, 55, 22);
const xPositions = [80, 313, 546, 779, 1012];
function box(x, y, heading, body) {
  const b = s.shapes.add({geometry: 'rect', position:{left:x, top:y, width:190, height:108},
    fill:'none', line:{fill:'none',width:0}});
  text(s, heading.toUpperCase(), x, y, 190, 28, 20);
  rule(s,x,y+36,190);
  text(s, body, x, y+49, 190, 78, 20, false, gray);
  return b;
}
const top = [
  ['Public data','USGS / NOAA\nunits + dates'], ['6 inputs','size, 2 temperatures\nriver, drought, season'],
  ['AI model','RF / XGBoost\nlearn cooling use'], ['Rules','power + heat limits\ncheck the number'],
  ['Result','water use + range\nwarnings if needed']
];
const lower = [
  ['Permit text','source + section\noriginal words'], ['Doc details','source + section\nwatershed or distance'],
  ['Word search','words as numbers\nfind similar text'], ['Location check','watershed or distance\nkeep local matches'],
  ['Quotes','original words\nwith their sources']
];
const row1=top.map((v,i)=>box(xPositions[i],315,...v));
const row2=lower.map((v,i)=>box(xPositions[i],465,...v));
for (const row of [row1,row2]) for (let i=0;i<4;i++) {
  s.shapes.connect(row[i],row[i+1],{kind:'straight',fromSide:'right',toSide:'left',
    line:{fill:'#9CA3AF',width:1},tail:{type:'arrow',width:'sm',length:'sm'}});
}
s.shapes.connect(row2[4],row1[4],{kind:'straight',fromSide:'top',toSide:'bottom',
  line:{fill:'#9CA3AF',width:1},tail:{type:'arrow',width:'sm',length:'sm'}});
text(s, 'The AI estimates water use. Rules check it. Local permit quotes explain the context.',
  80, 592, 1140, 28, 20);
text(s, 'E3: forced wrong results stay within 0-0.446484 MGD at 40 MW. E4: all 4 location tests pass.',
  80, 625, 1140, 26, 20);
note(s, 'Shaun, 30 seconds. Sources: src/models/regression.py, src/rules/thermodynamic.py, '
  + 'src/grounding/store.py, src/grounding/generator.py; docs/a2/evidence E3/E4 JSON. '
  + 'Rules also use capacity and ambient features. Fault injection -1/1e6 MGD clips to '
  + '0/0.446484 MGD for 40 MW, 30 C dry, 20 C wet. Four fictional retrieval cases pass. '
  + 'No LLM arithmetic or legal compliance decision.');

s = slide('Experiment E1: comparing AI models',
  'E1: regression-comparison.csv. 333 test rows per water-based cooling type. MGD = million US gallons/day.');
chart(s, ['Cooling tower', 'Direct evaporative'], [
  {name:'RandomForest', values:[0.004889693030131237,0.0038419326899621887],fill:'#D1D5DB'},
  {name:'XGBoost',values:[0.003668214892310914,0.0031913200828182888],fill:lavender}
], 'Average error (MAE, MGD)', 0.006, '0.000');
text(s, 'XGBOOST: LOWER ERROR', 850, 253, 350, 34, 24);
rule(s,850,303,345);
text(s, 'Pick using error on\nthe middle date group.\nKeep RF to compare.', 850, 327, 350, 129, 27);
text(s, 'Next: real water use\nand area measurements.', 850, 486, 350, 82, 25);
text(s, 'Dates: train 60% / choose + set ranges 20% / test 20%\nDry air cooling uses zero water here. Its R2 fit score cannot be calculated.',
  80, 593, 1140, 57, 21);
note(s, 'Shaun, 45 seconds. Source: docs/a2/evidence/regression-comparison.csv and benchmark.json. '
  + '1,600 synthetic rows per type, six years, seed 42. Selected tower R2 .99808, direct .99728. '
  + 'No field generalization claim. Model selection and interval sizing reuse calibration partition.');

s = slide('Experiment E2: missing readings',
  'E2: missingness-summary.csv, biased-donor-diagnostic.csv. Main test uses trained AI and made-up river data.');
chart(s, ['10% gaps','25% gaps','40% gaps'], [
  {name:'Nearby station',values:[0.3294740911224772,0.6313760632259535,0.9053629337832835],fill:lavender},
  {name:'Straight line',values:[0.6001259730487575,2.2120857291241645,4.092290509419216],fill:'#D1D5DB'}
], 'Prediction spread (10^-8 MGD2)', 5, '0.0');
text(s, '100%', 850, 233, 350, 96, 84);
rule(s,850,335,345);
text(s, 'All main tests passed', 850, 351, 350, 33, 25);
text(s, 'Change stayed within +/-0.05 MGD\n50 repeats on 121 drought days', 850, 398, 350, 95, 22, false, gray);
rule(s,850,500,345);
text(s, 'FAILURE: neighbors read too high\nonly 60.3% within limits', 850, 514, 350, 67, 24);
text(s, 'Next: test bad neighbor readings and stations losing data together. The bad-reading test uses a simple formula.',
  80, 607, 1140, 43, 21);
note(s, 'Troy, 40 seconds. Main data source: missingness-summary.csv. Bar values are exact variance '
  + 'multiplied by 1e8. Random gaps, fixed trained model, seed 42. Biased diagnostic: +100 MGD '
  + 'donors, 40% gaps, 20 repeats, predictor=.01*flow, spatial coverage .603305785, linear .985950413. '
  + 'Not a fitted-model failure rate. Interpolation is retrospective; sensitivity bands are not forecast intervals.');

s = slide('Experiment E5: prediction ranges',
  'E5: interval-coverage.csv, benchmark.json. Made-up test values, 333 per model.');
chart(s, ['Tower XGB','Direct XGB','Goal'],[
  {name:'Coverage',values:[0.8828828828828829,0.8798798798798799,0.9],fill:lavender,
    points:[{idx:2,fill:'#D1D5DB'}]}
], 'Test values inside range', 1, '0%',{left:660,top:270,width:545,height:295});
text(s, '88.3% / 88.0%', 80, 266, 560, 102, 73);
rule(s,80,375,530);
text(s, 'RELIABILITY ISSUE: below the 90% goal', 80, 393, 550, 32, 23, false, gray);
text(s, 'Tower fit score (R2) = 0.998\nA high score cannot promise a useful range.', 80, 443, 525, 101, 26);
rule(s,80,555,1120);
text(s, 'Improve: use separate data to choose models and set ranges.', 80, 575, 1120, 37, 24);
text(s, 'A small test. We have not checked if the shortfall is more than chance. Real-world range tests are still needed.',
  80, 620, 1140, 34, 19, false, gray);
note(s, 'Troy, 35 seconds. Sources: interval-coverage.csv; src/models/regression.py. '
  + 'Tower 294/333, direct 293/333, nominal .9. Selection and radius share calibration set. '
  + 'Chronological dependence complicates exchangeability. These finite samples do not establish '
  + 'statistical significance. R2 is not confidence; air zero target excluded.');

s = slide('Decisions & next question',
  'Decisions: E1-E5 | Proposed responsibilities: Shaun / Troy / Scott | Presentation day pending');
text(s, 'KEEP (ADOPT)', 80, 234, 605, 23, 17, false, gray);
rule(s,80,260,610);
text(s, 'E1: lower XGBoost error. E3/E4: checks pass.\nKeep the models, limits, and local matches.', 80, 273, 620, 53, 22);
text(s, 'CHANGE (MODIFY)', 80, 333, 605, 23, 17, false, gray);
rule(s,80,360,610);
text(s, 'E2: bad neighbor readings. E5: below 90%.\nImprove gap filling and ranges. Add area water totals.', 80, 373, 620, 53, 22);
text(s, 'DO NOT USE (REJECT)', 80, 438, 605, 23, 17, false, gray);
rule(s,80,464,610);
text(s, 'E5: a fit score cannot promise a right answer.\nCooling use alone cannot show ecosystem health.', 80, 477, 620, 53, 22);
text(s, 'WAIT (DEFER)', 80, 539, 605, 23, 17, false, gray);
rule(s,80,565,610);
text(s, 'Need real area data before testing more AI methods.', 80, 578, 620, 31, 22);
// The user removed circular gradients and the decorative sphere from the design.
// Keep this area open; all evidence remains in the charts and decision text.
text(s, 'Can we test effects on water reserves and rivers in a new area through the year?',
  80, 620, 1130, 33, 24);
text(s, 'Shaun: code + connect area data\nTroy: data + source quotes\nScott: tests + results',
  835, 538, 365, 65, 17, false, gray);
note(s, 'Scott, 60 seconds. Source: docs/a2/dossier.md sections 7-8, evidence-summary.csv, '
  + 'team-contributions.md. No neural/LLM comparison run. Shaun majority coding is confirmed; '
  + 'Troy/Scott supporting responsibilities are assigned, not certified completed. Next measured-label '
  + 'study needs facility holdouts, verified station maps, real permit relevance, MAE/RMSE/R2/coverage/width. '
  + 'Course date, deadline, office hours and instructor access remain pending.');

// Keep the exact component methods above and distinguish the broader project goal.
supportingNotes[0] += ('\nRegional framing: ECOllateral is an environmental impact assessment and regional ecosystem forecasting project. '
  + 'Primary question: development demands/cooling/location and seasonal impacts on area municipal reserves and watershed conditions. '
  + 'The cooling model is one pressure component. No regional impact or ecosystem health score is implemented/validated. Source: docs/project-scope.md and user context supplied October 8.');
supportingNotes[1] += ('\nThis map describes current components. Regional balances, ecological flow needs, cumulative demands/returns, verified boundaries, '
  + 'and regional targets remain planned. Current vectors are sparse TF-IDF, not dense learned embeddings. Groundwater depth is not recharge.');
supportingNotes[5] += ('\nPrimary next study: observed regional supply/reserves, demands, returns, ecological baselines and unseen-area tests. '
  + 'Facility holdouts remain a supporting component check. Zero-shot LLM, heatwave validation, EIA/EPA ingestion and historical recharge masking are proposals, not completed benchmarks. '
  + 'Troy supports data/grounding; Scott evaluation/interface/failure evidence; Shaun leads coding.');
// Attach the current simplified spoken script too.
const talk = await fs.readFile(path.join(out, 'presentation-script.md'), 'utf8');
const scriptSections = talk.matchAll(/## Slide ([1-6]):[^\n]*\n([\s\S]*?)(?=\n## |$)/g);
for (const match of scriptSections) {
  const index = Number(match[1])-1;
  p.slides.items[index].speakerNotes.textFrame.setText('Plain-English talk:\n'+match[2].trim()
    +'\n\nExtra details for questions:\n'+supportingNotes[index]);
}
const candidatePath = path.join(TMP_DIR, 'candidate.pptx');
await (await PresentationFile.exportPptx(p)).save(candidatePath);
const finalPath = path.join(out, process.env.FINAL_NAME ?? 'review-slides.pptx');
const result = await finalizePresentation({workspaceDir:WORKSPACE_DIR, candidatePath, finalPath,
  pythonExecutable:RUNTIME_PYTHON,
  integrityValidatorPath:path.join(SKILL_DIR,'container_tools/inspect_presentation_package_integrity.py'),
  layoutValidatorPath:path.join(SKILL_DIR,'container_tools/inspect_presentation_layout_geometry.py'),
  layoutArgs:['--expected-slide-size-emu','12192000,6858000','--validate-bullet-geometry','--validate-heading-fit'],
  explicitTotalSlideCount:6, requiredNativeTableOwnerSlides:[], requiredNativeChartOwnerSlides:[3,4,5],
  materializeLiteralChartWorkbooks:true, fontPolicy:{basis:'design',families:[headingFamily,family]},
  verifyArtifactToolImport:true, receiptPath:path.join(TMP_DIR,path.basename(finalPath)+'.validation.json')});
console.log(JSON.stringify({finalPath, font:family, sha256:result.finalSha256,
  packageStatus:result.packageIntegrity.status, slideCount:6, nativeCharts:3}));
const finalDeck = await PresentationFile.importPptx(await FileBlob.load(finalPath));
const renderDir = path.join(TMP_DIR,'final-render');
await fs.mkdir(renderDir,{recursive:true});
for (let i=0;i<finalDeck.slides.items.length;i++) {
  const slide = finalDeck.slides.items[i];
  const png = await finalDeck.export({slide,format:'png',scale:1.5});
  await fs.writeFile(path.join(renderDir,`slide-${i+1}.png`),new Uint8Array(await png.arrayBuffer()));
}
console.log('Rendered all six finalized slides.');
