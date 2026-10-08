// Execute a copy in data/processed/a2-build/slides, linked to bundled node_modules.
// Required environment: SKILL_DIR, WORKSPACE_DIR, RUNTIME_PYTHON, TMP_DIR.
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
const family = resolvePresentationFont();
const p = Presentation.create({slideSize: {width: 1280, height: 720}});
const navy = '#142D42', teal = '#167D8D', gray = '#536777', orange = '#BD622B';
const out = path.join(WORKSPACE_DIR, 'docs/a2');
await fs.mkdir(TMP_DIR, {recursive: true});

function text(s, value, x, y, w, h, size = 27, bold = false, color = navy) {
  const shape = s.shapes.add({geometry: 'textbox',
    position: {left: x, top: y, width: w, height: h},
    fill: 'none', line: {fill: 'none', width: 0}});
  shape.text = value;
  shape.text.style = {typeface: family, fontSize: size, bold, color, autoFit: 'none'};
  return shape;
}
function slide(title, source) {
  const s = p.slides.add();
  s.background.fill = '#FFFFFF';
  text(s, 'ECOllateral / CSCI 4150 A2', 60, 25, 900, 32, 19, true, teal);
  text(s, title, 60, 73, 1150, 100, 43, true);
  text(s, source, 60, 656, 1110, 42, 16, false, gray);
  text(s, String(p.slides.items.length), 1190, 663, 35, 30, 17, false, gray);
  return s;
}
function note(s, content) {s.speakerNotes.textFrame.setText(content);}
function chart(s, categories, series, yTitle, yMax, format, height=330) {
  // Ten significant digits preserve display accuracy and fit Excel's numeric limit.
  // The evidence CSVs retain full precision; chart workbooks are intentional snapshots.
  series = series.map(item => ({...item, values:item.values.map(v=>Number(v.toPrecision(10)))}));
  const c = s.charts.add('bar', {
    position: {left: 62, top: 205, width: 760, height}, categories, series,
    barOptions: {direction: 'column', grouping: 'clustered', gapWidth: 100},
    hasLegend: series.length > 1,
    legend: {position: 'bottom', textStyle: {fontSize: 23, fill: navy}},
    xAxis: {textStyle: {fontSize: 23, fill: navy}},
    yAxis: {min: 0, max: yMax, numberFormatCode: format,
      title: {text: yTitle, textStyle: {fontSize: 21, fill: navy}},
      textStyle: {fontSize: 20, fill: gray},
      majorGridlines: {fill: '#DEE7EB', width: 1}},
    chartFill: '#FFFFFF', plotAreaFill: '#FFFFFF',
    dataLabels: {showValue: false, textStyle: {fontSize: 23}},
  });
  applyPresentationChartFont(c, {fontFamily: family});
  return c;
}

let s = slide('How much water does a cooling scenario consume?',
  'Snapshot: October 7, 2026 | Synthetic labels; field validation pending');
text(s, 'For researchers and planners comparing proposed data centers', 64, 194, 1120, 64, 30);
text(s, 'INPUT', 65, 288, 410, 40, 23, true, teal);
text(s, 'Capacity (MW)\nCooling type\nWatershed + month', 65, 334, 430, 180, 34);
text(s, 'OUTPUT', 665, 288, 480, 40, 23, true, teal);
text(s, 'Consumption (MGD) + bounds\nInterval + quality warnings\nGeographic permit quotations', 665, 334, 540, 180, 32);
text(s, 'Working local prototype | Shaun, Troy, Scott', 65, 566, 1110, 48, 28, true);
note(s, 'Shaun, 30 seconds. Source: docs/a2/dossier.md section 1; docs/a2/evidence/forecast.json. '
  + 'Synthetic labels and fictional permits. Public ingestion is a parser smoke test. '
  + 'The current collateral stress field is an on-site consumption proxy. Assigned day is pending.');

s = slide('Meaning lives in features, rules, vectors, and scope',
  'E3/E4: constraint-failure-cases.json; retrieval-cases.json | Diagram shows current prototype');
text(s, 'Request: MW, cooling type, HUC8, month; optional facility coordinates', 64, 173, 1140, 42, 24);
const xPositions = [65, 300, 535, 770, 1005];
function box(x, y, heading, body) {
  const b = s.shapes.add({geometry: 'rect', position:{left:x, top:y, width:195, height:116},
    fill:'#EFF5F7', line:{fill:teal,width:1.5}});
  text(s, heading, x+10, y+13, 177, 35, 24, true);
  text(s, body, x+10, y+51, 177, 65, 21);
  return b;
}
const top = [
  ['Public data','USGS / NOAA\nvalues + units'], ['Six features','MW, C, MGD\nPDSI + season'],
  ['Regressor','RF / XGBoost\nlearned trees'], ['Thermal rules','clip + flag\ncapacity/ambient'],
  ['Forecast','MGD + interval\nbounds + flags']
];
const lower = [
  ['Permit text','source + section\nexact excerpt'], ['Metadata','HUC or radius\nidentifiers'],
  ['TF-IDF','FAISS ranking\nlexical vectors'], ['Geo filter','scope match\nbefore top-k'],
  ['Quotations','source + section\nextractive text']
];
const row1=top.map((v,i)=>box(xPositions[i],237,...v));
const row2=lower.map((v,i)=>box(xPositions[i],403,...v));
for (const row of [row1,row2]) for (let i=0;i<4;i++) {
  s.shapes.connect(row[i],row[i+1],{kind:'straight',fromSide:'right',toSide:'left',
    line:{fill:teal,width:2},tail:{type:'arrow',width:'med',length:'med'}});
}
s.shapes.connect(row2[4],row1[4],{kind:'straight',fromSide:'top',toSide:'bottom',
  line:{fill:teal,width:2},tail:{type:'arrow',width:'med',length:'med'}});
text(s, 'Offline: synthetic consumption labels -> chronological train / calibration / test',
  65, 547, 1140, 40, 23);
text(s, 'Bounds flag injected errors; four geographic retrieval cases pass.',
  65, 597, 1140, 35, 24, true, teal);
note(s, 'Shaun, 30 seconds. Sources: src/models/regression.py, src/rules/thermodynamic.py, '
  + 'src/grounding/store.py, src/grounding/generator.py; docs/a2/evidence E3/E4 JSON. '
  + 'Rules also use capacity and ambient features. Fault injection -1/1e6 MGD clips to '
  + '0/0.446484 MGD for 40 MW, 30 C dry, 20 C wet. Four fictional retrieval cases pass. '
  + 'No LLM arithmetic or legal compliance decision.');

s = slide('XGBoost reduced error on the synthetic benchmark',
  'E1: regression-comparison.csv | 333 test rows per evaporative type | MAE in MGD');
chart(s, ['Cooling tower', 'Direct evaporative'], [
  {name:'RandomForest', values:[0.004889693030131237,0.0038419326899621887],fill:'#9BAEB9'},
  {name:'XGBoost',values:[0.003668214892310914,0.0031913200828182888],fill:teal}
], 'Mean absolute error (MGD)', 0.006, '0.000');
text(s, 'Adopt', 862, 221, 340, 45, 32, true, teal);
text(s, 'Select by calibration RMSE.\nKeep RF as the baseline.', 862, 284, 338, 152, 29);
text(s, 'Measured facility labels\nremain the main gap.', 862, 469, 338, 105, 29, true);
text(s, 'Chronological 60/20/20 dates | Dry air cooling: zero target, undefined R2',
  65, 594, 1140, 48, 24);
note(s, 'Shaun, 45 seconds. Source: docs/a2/evidence/regression-comparison.csv and benchmark.json. '
  + '1,600 synthetic rows per type, six years, seed 42. Selected tower R2 .99808, direct .99728. '
  + 'No field generalization claim. Model selection and interval sizing reuse calibration partition.');

s = slide('Correlated donors made drought gaps easy to fill',
  'E2: missingness-summary.csv; biased-donor-diagnostic.csv | Main test: fitted model, synthetic hydrology');
chart(s, ['10% gaps','25% gaps','40% gaps'], [
  {name:'Spatial nearest',values:[0.3294740911224772,0.6313760632259535,0.9053629337832835],fill:teal},
  {name:'Linear time',values:[0.6001259730487575,2.2120857291241645,4.092290509419216],fill:'#9BAEB9'}
], 'Variance (10^-8 MGD2)', 5, '0.0');
text(s, '100% within tolerance', 862, 218, 345, 84, 31, true, teal);
text(s, '+/-0.05 MGD\n50 repeats; 121 drought dates', 862, 315, 345, 116, 27);
text(s, 'Biased-donor diagnostic:\nspatial coverage 60.3%', 862, 463, 345, 100, 29, true, orange);
text(s, 'Modify: validate donors and shared outages; diagnostic uses a separate simple predictor.',
  65, 594, 1145, 54, 24);
note(s, 'Troy, 40 seconds. Main data source: missingness-summary.csv. Bar values are exact variance '
  + 'multiplied by 1e8. Random gaps, fixed trained model, seed 42. Biased diagnostic: +100 MGD '
  + 'donors, 40% gaps, 20 repeats, predictor=.01*flow, spatial coverage .603305785, linear .985950413. '
  + 'Not a fitted-model failure rate. Interpolation is retrospective; sensitivity bands are not forecast intervals.');

s = slide('High R2 did not establish 90% interval coverage',
  'E5: interval-coverage.csv; benchmark.json | Synthetic held-out samples, 333 per model');
chart(s, ['Tower XGB','Direct XGB','Nominal'],[
  {name:'Coverage',values:[0.8828828828828829,0.8798798798798799,0.9],fill:teal,
    points:[{idx:2,fill:'#9BAEB9'}]}
], 'Labels inside interval', 1, '0%');
text(s, '88.3% / 88.0%', 862, 220, 345, 58, 38, true, orange);
text(s, 'Tower R2 = 0.998\nCoverage misses the\nobserved 90% gate.', 862, 295, 345, 148, 28);
text(s, 'Modify: separate tuning\nand interval calibration.', 862, 479, 345, 98, 28, true);
text(s, 'Finite samples; no significance test or independently validated coverage guarantee.',
  65, 594, 1145, 48, 24);
note(s, 'Troy, 35 seconds. Sources: interval-coverage.csv; src/models/regression.py. '
  + 'Tower 294/333, direct 293/333, nominal .9. Selection and radius share calibration set. '
  + 'Chronological dependence complicates exchangeability. These finite samples do not establish '
  + 'statistical significance. R2 is not confidence; air zero target excluded.');

s = slide('Next: test measured consumption at an unseen facility',
  'Decisions: E1-E5 | Proposed responsibilities: Shaun / Troy / Scott | Presentation day pending');
text(s, 'Adopt', 65, 190, 210, 46, 31, true, teal);
text(s, 'Tree baselines, independent rules, geography-aware quotations', 285, 190, 900, 64, 29);
text(s, 'Modify', 65, 283, 210, 46, 31, true, orange);
text(s, 'Donor validation, shared outages, independent interval calibration', 285, 283, 900, 64, 29);
text(s, 'Reject / Defer', 65, 376, 215, 65, 29, true);
text(s, 'Reject R2-as-confidence; defer neural and generative LLM models', 285, 376, 900, 70, 29);
text(s, 'Can the constrained model generalize during drought with adequate coverage?',
  65, 479, 1140, 83, 34, true);
text(s, 'Shaun: code + calibration    Troy: data + drought    Scott: permits + evidence',
  65, 583, 1145, 52, 24);
note(s, 'Scott, 60 seconds. Source: docs/a2/dossier.md sections 7-8, evidence-summary.csv, '
  + 'team-contributions.md. No neural/LLM comparison run. Shaun majority coding is confirmed; '
  + 'Troy/Scott supporting responsibilities are assigned, not certified completed. Next measured-label '
  + 'study needs facility holdouts, verified station maps, real permit relevance, MAE/RMSE/R2/coverage/width. '
  + 'Course date, deadline, office hours and instructor access remain pending.');

const candidatePath = path.join(TMP_DIR, 'candidate.pptx');
await (await PresentationFile.exportPptx(p)).save(candidatePath);
const finalPath = path.join(out, process.env.FINAL_NAME ?? 'review-slides.pptx');
const result = await finalizePresentation({workspaceDir:WORKSPACE_DIR, candidatePath, finalPath,
  pythonExecutable:RUNTIME_PYTHON,
  integrityValidatorPath:path.join(SKILL_DIR,'container_tools/inspect_presentation_package_integrity.py'),
  layoutValidatorPath:path.join(SKILL_DIR,'container_tools/inspect_presentation_layout_geometry.py'),
  layoutArgs:['--expected-slide-size-emu','12192000,6858000','--validate-bullet-geometry','--validate-heading-fit'],
  explicitTotalSlideCount:6, requiredNativeTableOwnerSlides:[], requiredNativeChartOwnerSlides:[3,4,5],
  materializeLiteralChartWorkbooks:true, fontPolicy:{basis:'design',families:[family]},
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
