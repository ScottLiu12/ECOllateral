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
const navy = '#111827', lavender = '#9382FF', gray = '#6B7280';
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
function glow(s,x,y,w=580,h=450) {
  return s.shapes.add({geometry:'ellipse',position:{left:x,top:y,width:w,height:h},
    fill:'radial(#9382FF/45 0%, #9382FF/18 35%, #9382FF/4 65%, #9382FF/0 100%)',
    line:{fill:'none',width:0}});
}
function slide(title, source, cover=false) {
  const s = p.slides.add();
  s.background.fill = canvas;
  glow(s,cover?85:660,cover?50:-65,cover?750:520,cover?560:300);
  text(s, 'E C O L L A T E R A L   /   C S C I  4 1 5 0  A 2', 80, 36, 1000, 22, 14, false, gray);
  const titleY=cover?143:91, titleH=cover?180:110;
  s.shapes.add({geometry:'rect',position:{left:66,top:titleY+2,width:1.5,height:titleH-7},
    fill:navy,line:{fill:'none',width:0}});
  text(s, title.toUpperCase(), 85, titleY, cover?1060:1105, titleH, cover?58:43, false, navy, headingFamily);
  text(s, source, 80, 664, 1070, 35, 13, false, gray);
  text(s, String(p.slides.items.length).padStart(2,'0'), 1180, 664, 36, 24, 14, false, gray);
  return s;
}
function note(s, content) {s.speakerNotes.textFrame.setText(content);}
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

let s = slide('Estimate the water a data center uses for cooling',
  'October 7, 2026 snapshot | Made-up test data; real-facility accuracy still unverified',true);
text(s, 'Shaun, Troy, Scott', 85, 100, 650, 28, 20, false, gray);
text(s, 'For researchers and planners comparing proposed data centers', 85, 340, 1100, 43, 25);
text(s, 'I N P U T', 85, 426, 410, 30, 16, false, gray);
rule(s,85,465,435);
text(s, 'IT size (megawatts)\nCooling type\nWatershed + month', 85, 483, 435, 115, 27);
text(s, 'O U T P U T', 660, 426, 485, 30, 16, false, gray);
rule(s,660,465,535);
text(s, 'Water use + physical limits\nPrediction range + warnings\nPermit quotes for the location', 660, 483, 535, 115, 27);
text(s, 'Working local prototype', 85, 616, 800, 27, 19, false, gray);
note(s, 'Shaun, 30 seconds. Source: docs/a2/dossier.md section 1; docs/a2/evidence/forecast.json. '
  + 'Synthetic labels and fictional permits. Public ingestion is a parser smoke test. '
  + 'The current collateral stress field is an on-site consumption proxy. Assigned day is pending.');

s = slide('Two paths: predict water use and find permit quotes',
  'E3/E4: constraint-failure-cases.json; retrieval-cases.json | Diagram shows current prototype');
text(s, 'Enter IT size, cooling type, watershed code (HUC8), and month; coordinates optional', 80, 231, 1135, 55, 22);
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
  ['Public data','USGS / NOAA\nunits + dates'], ['6 inputs','size, dry/wet C\nflow, PDSI, season'],
  ['AI model','RF / XGBoost\npredict a number'], ['Heat rules','size + weather\nlimits + warnings'],
  ['Response','MGD + range\nlimits + warnings']
];
const lower = [
  ['Permit text','source + section\noriginal words'], ['Doc info','HUC or radius\nsection IDs'],
  ['Word search','TF-IDF / FAISS\nrank word matches'], ['Location','HUC or radius\nkeep eligible k'],
  ['Quotes','source + section\nexact quotations']
];
const row1=top.map((v,i)=>box(xPositions[i],315,...v));
const row2=lower.map((v,i)=>box(xPositions[i],465,...v));
for (const row of [row1,row2]) for (let i=0;i<4;i++) {
  s.shapes.connect(row[i],row[i+1],{kind:'straight',fromSide:'right',toSide:'left',
    line:{fill:'#9CA3AF',width:1},tail:{type:'arrow',width:'sm',length:'sm'}});
}
s.shapes.connect(row2[4],row1[4],{kind:'straight',fromSide:'top',toSide:'bottom',
  line:{fill:'#9CA3AF',width:1},tail:{type:'arrow',width:'sm',length:'sm'}});
text(s, 'Before use: train on made-up water use; choose, set ranges, and test by date.',
  80, 592, 1140, 28, 20);
text(s, 'Forced wrong numbers trigger warnings. Four permit-location tests pass.',
  80, 625, 1140, 26, 20);
note(s, 'Shaun, 30 seconds. Sources: src/models/regression.py, src/rules/thermodynamic.py, '
  + 'src/grounding/store.py, src/grounding/generator.py; docs/a2/evidence E3/E4 JSON. '
  + 'Rules also use capacity and ambient features. Fault injection -1/1e6 MGD clips to '
  + '0/0.446484 MGD for 40 MW, 30 C dry, 20 C wet. Four fictional retrieval cases pass. '
  + 'No LLM arithmetic or legal compliance decision.');

s = slide('XGBoost made smaller errors on our test data',
  'E1: regression-comparison.csv | 333 test rows per evaporative type | MGD = million US gallons/day');
chart(s, ['Cooling tower', 'Direct evaporative'], [
  {name:'RandomForest', values:[0.004889693030131237,0.0038419326899621887],fill:'#D1D5DB'},
  {name:'XGBoost',values:[0.003668214892310914,0.0031913200828182888],fill:lavender}
], 'Average error (MAE, MGD)', 0.006, '0.000');
text(s, 'KEEP XGBOOST', 850, 253, 350, 34, 24);
rule(s,850,303,345);
text(s, 'Choose with RMSE on\nthe middle date group.\nKeep RF for comparison.', 850, 327, 350, 129, 27);
text(s, 'Next: measured water\nuse at real facilities.', 850, 486, 350, 82, 25);
text(s, 'Dates: train 60% / choose + set ranges 20% / test 20%\nDry air cooling: zero water target; R2 is undefined.',
  80, 593, 1140, 57, 21);
note(s, 'Shaun, 45 seconds. Source: docs/a2/evidence/regression-comparison.csv and benchmark.json. '
  + '1,600 synthetic rows per type, six years, seed 42. Selected tower R2 .99808, direct .99728. '
  + 'No field generalization claim. Model selection and interval sizing reuse calibration partition.');

s = slide('Similar nearby stations made gaps easier to fill',
  'E2: missingness-summary.csv; biased-donor-diagnostic.csv | Main test uses trained AI and made-up river data');
chart(s, ['10% gaps','25% gaps','40% gaps'], [
  {name:'Nearby station',values:[0.3294740911224772,0.6313760632259535,0.9053629337832835],fill:lavender},
  {name:'Straight line',values:[0.6001259730487575,2.2120857291241645,4.092290509419216],fill:'#D1D5DB'}
], 'Prediction spread (10^-8 MGD2)', 5, '0.0');
text(s, '100%', 850, 233, 350, 96, 84);
rule(s,850,335,345);
text(s, 'All main cases passed', 850, 351, 350, 33, 25);
text(s, 'Change within +/-0.05 MGD\n50 repeats; 121 drought dates', 850, 398, 350, 95, 22, false, gray);
rule(s,850,500,345);
text(s, 'Biased-neighbor test:\nonly 60.3% within limits', 850, 514, 350, 67, 24);
text(s, 'Improve: check neighbors and shared outages. The biased test uses a separate simple formula.',
  80, 607, 1140, 43, 21);
note(s, 'Troy, 40 seconds. Main data source: missingness-summary.csv. Bar values are exact variance '
  + 'multiplied by 1e8. Random gaps, fixed trained model, seed 42. Biased diagnostic: +100 MGD '
  + 'donors, 40% gaps, 20 repeats, predictor=.01*flow, spatial coverage .603305785, linear .985950413. '
  + 'Not a fitted-model failure rate. Interpolation is retrospective; sensitivity bands are not forecast intervals.');

s = slide('The prediction ranges missed our 90% goal',
  'E5: interval-coverage.csv; benchmark.json | Made-up test values; 333 per model');
chart(s, ['Tower XGB','Direct XGB','Goal'],[
  {name:'Coverage',values:[0.8828828828828829,0.8798798798798799,0.9],fill:lavender,
    points:[{idx:2,fill:'#D1D5DB'}]}
], 'Test values inside range', 1, '0%',{left:660,top:270,width:545,height:295});
text(s, '88.3% / 88.0%', 80, 266, 560, 102, 73);
rule(s,80,375,530);
text(s, 'Tower / direct evaporative coverage', 80, 393, 550, 32, 23, false, gray);
text(s, 'Tower R2 = 0.998\nGood fit does not prove the range is reliable.', 80, 443, 525, 101, 26);
rule(s,80,555,1120);
text(s, 'Improve: use separate data to choose models and set ranges.', 80, 575, 1120, 37, 24);
text(s, 'Limited samples; no statistical significance test or independently verified coverage guarantee.',
  80, 620, 1140, 34, 19, false, gray);
note(s, 'Troy, 35 seconds. Sources: interval-coverage.csv; src/models/regression.py. '
  + 'Tower 294/333, direct 293/333, nominal .9. Selection and radius share calibration set. '
  + 'Chronological dependence complicates exchangeability. These finite samples do not establish '
  + 'statistical significance. R2 is not confidence; air zero target excluded.');

s = slide('Next: test real water use at a new facility',
  'Decisions: E1-E5 | Proposed responsibilities: Shaun / Troy / Scott | Presentation day pending');
text(s, 'KEEP (ADOPT)', 80, 238, 605, 28, 19, false, gray);
rule(s,80,272,610);
text(s, 'Tree models, physical limits, permit-location checks', 80, 286, 620, 55, 26);
text(s, 'IMPROVE (MODIFY)', 80, 355, 605, 28, 19, false, gray);
rule(s,80,389,610);
text(s, 'Check neighbors, shared outages, and prediction ranges', 80, 403, 620, 55, 26);
text(s, 'REJECT / DEFER', 80, 472, 605, 28, 19, false, gray);
rule(s,80,506,610);
text(s, 'R2 is not confidence; wait on neural and generative LLM models', 80, 520, 620, 69, 24);
// Native, editable abstract composition: softly shaded sphere and thin orbit.
// Decorative only; it represents no experimental evidence or measured geometry.
glow(s,755,215,450,350);
s.shapes.add({geometry:'ellipse',position:{left:835,top:247,width:270,height:270},
  fill:'radial(#FFFFFF 0%, #EEEBFF 40%, #C8BFFF 75%, #9382FF/45 100%)',
  line:{fill:ruleColor,width:1}});
s.shapes.add({geometry:'ellipse',position:{left:803,top:350,width:335,height:75},
  fill:'none',line:{fill:'#9CA3AF/60',width:1}});
text(s, 'Will it work during drought at an unseen facility, with reliable prediction ranges?',
  80, 620, 1130, 33, 24);
text(s, 'Shaun: code + ranges\nTroy: data + drought\nScott: permits + evidence',
  835, 538, 365, 65, 17, false, gray);
note(s, 'Scott, 60 seconds. Source: docs/a2/dossier.md sections 7-8, evidence-summary.csv, '
  + 'team-contributions.md. No neural/LLM comparison run. Shaun majority coding is confirmed; '
  + 'Troy/Scott supporting responsibilities are assigned, not certified completed. Next measured-label '
  + 'study needs facility holdouts, verified station maps, real permit relevance, MAE/RMSE/R2/coverage/width. '
  + 'Course date, deadline, office hours and instructor access remain pending.');

// Keep the exact source details above and attach the simplified spoken script too.
const talk = await fs.readFile(path.join(out, 'presentation-script.md'), 'utf8');
const scriptSections = talk.matchAll(/## Slide ([1-6]):[^\n]*\n([\s\S]*?)(?=\n## |$)/g);
for (const match of scriptSections) {
  p.slides.items[Number(match[1])-1].speakerNotes.append('\nPlain-English talk:\n'+match[2].trim());
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
